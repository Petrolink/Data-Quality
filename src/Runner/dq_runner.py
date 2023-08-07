import os
import pandas as pd
import yaml
import copy
from datetime import datetime, timedelta
# Temporary fix that allows dimensions lib to be imported from other dir while the lib is not registered with pip
# According to https://www.geeksforgeeks.org/python-import-module-outside-directory/
import sys
sys.path.append(os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'Library')))
import dq_dimensions as dq


def yaml_loader(filepath):
    """Function that Loads a yaml file"""
    with open(os.path.join(sys.path[0], filepath), 'r') as file_descriptor:
        data = yaml.load(file_descriptor, Loader=yaml.Loader)
    return data

def timeStr(string):
    """Function that takes in a string and returns it as a datetime.
    Args: 
        string (str): String value containing a UTC timestamp that follows ISO standards.
    Raises:
        Exception: An exception is thrown when a non string value is passed as an argument.
    Returns:
        A datetime value created from the timestamp string."""
    if type(string) is not str: 
        raise Exception('Please only pass string values to timeStr.')
    return datetime.fromisoformat(string)

def get_Configs(configType):
    """Function that retrieves the type of configuration and returns them as a iterable dictionary.
    Args:
        configType (str): String key value used to request types of user configurations from config.yaml
    Raises:
        Exception: An exception is raised when the argument passed is not a str value.
    Returns:
        
    """
    if type(configType) is not str:
        raise Exception('Please only provide a key string value (ie. "curve") when using get_Configs to retrieve a type of yaml configuration.')
    configs = yaml_loader('config.yaml')
    match(str.lower(configType)):
        case 'curve':
            if len(configs['Curve_configs']) == 0:
                raise Exception('Expecting input for Curve_configs in config.yaml')
            return configs['Curve_configs']
        case 'general':
            if len(configs['General_configs']) == 0:
                raise Exception('Excpecting input for General_configs in config.yaml')
            return configs['General_configs']
        case 'accuracy':
            if len(configs['Accuracy_configs']) == 0:
                raise Exception('Expecting input for Accuracy_conifgs in config.yaml')
            return configs['Accuracy_configs']
        case 'dimensions':
            if len(configs['Dimension_weights']) == 0:
                raise Exception('Expecting input for Dimension_weights in config.yaml')
            return configs['Dimension_weights']
        case 'rules':
            if len(configs['Rule_thresholds']) == 0:
                raise Exception('Expecting input for Rule_thresholds in config.yaml')
            return configs['Rule_thresholds']
        case default:
            raise Exception('The value passed was an invalid config type key. Please pass a valid key: "curve"')

def fill_dataframe(itype:str):
    """Reads in a .csv file and returns a mutable dataframe filled with .csv data.
    Args: 
        itype (str): An input type key word (input or check)
    Raises:
        Exception: An Exception occurs when the file path parameter is an empty string.
        Exception: An Exception occurs when the input file is not of type .csv.
        Exception: An Exception occurs when there is no data in the input file.
    Returns:
        df (pd): Pandas dataframe with input .csv data.
    """
    #TODO finish updating file structure/loading and update unittests on Monday, need to make a test config file to use
    configs = get_Configs('general')
    if len(itype) == 0:
        raise Exception('Please provide a valid input type key-word ("input" or "check"), empty strings will not be accepted.')
    match(str.lower(itype)):
        case 'input':
            if not configs.get('DataFile').endswith('csv'):
                raise Exception('Expecting a .csv file name for the DataFile config in General_configs.')
            csvfile = os.path.realpath(os.path.join(os.path.dirname(__file__), '../..', 'input', configs.get('DataFile')))
        case 'check':
            if not configs.get('CheckFile').endswith('csv'):
                raise Exception('Expecting a .csv file name for the CheckFile config in General_configs.')
            csvfile = os.path.realpath(os.path.join(os.path.dirname(__file__), '../..', 'input', configs.get('CheckFile')))
        case default:
            raise Exception('The value passed is an invalid input type key. Please Specify "input" or "check".')
    df = pd.DataFrame()
    df = pd.read_csv(csvfile)
    if df.empty:
        raise Exception("Expecting file with data")
    return df

def createDimensions(dataframe:pd.DataFrame):
    """Void function that adds and calculates dimension columns in the dataframe passed in using the configurations set by user.
    Args:
        dataframe (pd): Pandas dataframe with input .csv data
    Raises:
        TODO: Add exceptions and Test
    """
    # TODO Break this function up into multiple, too much going on in here.
    CurveConfigs = get_Configs('curve')
    GenConfigs = get_Configs('general')
    cCheck = GenConfigs.get('CalcConsistency')
    if cCheck:
        consCheck = fill_dataframe('check')
    AccConfigs = get_Configs('accuracy')
    AccCurves = AccConfigs.get('Curves')
    CurveNames = get_Configs('curve').keys()
    AllFreq = pd.DataFrame()
    comp = []
    sDomains = {}
    if GenConfigs['CheckRigStatuses']:
        print('Creating sDomains')
        sDomains = createSDomains(dataframe)
        #print(sDomains)
        print('Complete!')

    # Looping through input columns.
    for column in dataframe:
        colNum = 0
        accuracy = False
        # Calculating Dimensions lists/arrays.

        # Checking to see if the column(curve) name is a configured curve in config.yaml
        if column in CurveNames:
            #Grabbing the current curves configuration.
            cConfig = CurveConfigs[column]
            #Checking if the column(curve) is listed in Accuracy_configs in config.yaml
            if column in AccConfigs['Curves'].keys():
                accuracy = True
            val = []
            freq = []
            uniq = [] 
            cons = []
            acc = []
            colNum = dataframe.columns.get_loc(column)
            index = 0
            for i in dataframe[column]:
                val.append(dq.Validity(i, cConfig.get('upLim'), cConfig.get('lowLim')))
                if cCheck:
                    cons.append(dq.Consistency(i, consCheck.iloc[index][column]))
                if index == 0:
                    if accuracy:
                        paired = AccCurves[column]
                        acc.append(dq.Accuracy(i, None, dataframe.iloc[index][paired], None))
                    #First sample/row scenarios.
                    freq.append(dq.Frequency(timeStr(dataframe.iloc[index]['Time']), None, GenConfigs.get('freqTol')))
                    if GenConfigs['CheckRigStatuses']:
                        uniq.append(dq.Uniqueness(i, 0.0, dq.checkStationary(sDomains[index]), dq.checkSurface(sDomains[index])))
                    else:
                        uniq.append(dq.Uniqueness(i))
                else:
                    if accuracy:
                        paired = AccCurves[column]
                        acc.append(dq.Accuracy(i, prev, dataframe.iloc[index][paired], dataframe.iloc[index-1][paired]))
                    freq.append(dq.Frequency(timeStr(dataframe.iloc[index]['Time']), timeStr(dataframe.iloc[index-1]['Time']), GenConfigs.get('freqTol')))
                    if GenConfigs['CheckRigStatuses']:
                        uniq.append(dq.Uniqueness(i, prev, dq.checkStationary(sDomains[index]), dq.checkSurface(sDomains[index])))
                    else:
                        uniq.append(dq.Uniqueness(i, prev))
                prev = i
                index += 1
            # Inserts
            count = 0
            AllFreq.insert(count, "Frequency", freq, True)
            count += 1
            if cCheck:
                dimensions = {'Curve': column, 'Validity_': val, 'Frequency_': freq, 'Consistency_': cons, 'Uniqueness_': uniq}
            else:
                dimensions = {'Curve': column, 'Validity_': val, 'Frequency_': freq, 'Uniqueness_': uniq}
            if accuracy:
                dimensions['Accuracy_']= acc
            insertDims(dataframe, colNum, dimensions)
    for idx, row, in AllFreq.iterrows():
        comp.append(dq.Completeness(row.tolist()))
    dataframe['Completeness'] = comp

def createSDomains(dataframe: pd.DataFrame):
    """Function that returns a dictionary filled with sampleDomains for each row in the dataframe passed by using the sampleDomains() function.
    Args:
        dataframe (pd.Dataframe): Pandas dataframe with input .csv data
    Raises:
        Exception: An Exception is raised if the argument passed is not a pandas dataframe.
    Returns:
        sDomains (dict)
    """
    sDomains = {}
    for idx, row in dataframe.iterrows():
        if idx == len(dataframe)/2:
            print('50%' + ' complete')
        if idx == 0: 
            sDomains[idx] = sampleDomain(row)
        else:
            sDomains[idx] = sampleDomain(row, prev)
        prev = row
    return sDomains

def sampleDomain(cSample: pd.Series, pSample=pd.Series):
    """Function that loads an empty sampleDomain dictionary template from dq.dimensions with data to be passed to checker functions in dq.dimensions
    using a sample(row of data) from a dataset.

    Args:
        cSample (pd.Series): Current row of data from input
        pSample (optional): Previous row of data from input (optional argument as 1st row of data has no previous)
    Raises:
        Exception: An Exception is raised if the argument passed is not a pandas series.
    Returns:
        sDomain (dict): sampleDomain dictionary loaded with data
    """
    CurveConfigs = get_Configs('curve')
    RuleConfigs = get_Configs('rules')
    sDomain = copy.deepcopy(dq.sampleDomains)
    for idx, value in cSample.items():
        if idx in CurveConfigs.keys() and CurveConfigs[idx].get('rule') is not None:
            rule = CurveConfigs[idx].get('rule')
            if type(rule) is list:
                sDomain['BitDepth']['curr'] = value
                if type(pSample) is pd.Series:
                    sDomain['BitDepth']['prev'] = pSample.at[idx]
                for i in rule:
                    match(i):
                        case 'OnSurface':
                            sDomain['BitDepth']['surfaceThresh'] = RuleConfigs.get(i)
                        case 'Bit_Move':
                            sDomain['BitDepth']['bitmoveThresh'] = RuleConfigs.get(i)
                        case default:
                            raise Exception(i + ' is not a recognized BitDepth domain rule.')
            else:
                match(rule):
                    case 'Hookload':
                        sDomain['Hookload']['value'] = value
                        sDomain['Hookload']['thresh'] = RuleConfigs.get(rule)
                    case 'RPM':
                        sDomain['RPM']['value'] = value
                        sDomain['RPM']['thresh'] = RuleConfigs.get(rule)
                    case 'SPP':
                        sDomain['SPP']['value'] = value
                        sDomain['SPP']['thresh'] = RuleConfigs.get(rule)
                    case 'Delta_BPOS':
                        sDomain['BlockPosition']['curr'] = value
                        if type(pSample) is pd.Series:
                            sDomain['BlockPosition']['prev'] = pSample.at[idx]
                        sDomain['BlockPosition']['deltaThresh'] = RuleConfigs.get(rule)
    return sDomain

def insertDims(dataframe: pd.DataFrame, curveCol:int, dims:dict):
    """Void Function that aids createDimensions by inserting/formatting the calculated dimensions lists into the curveDimension Dataframe (data in main).
    Args:
        dataframe (pd.Dataframe): Dataframe to add inserts into.
        curveCol (int): Column number of the current curve to add dimensions for.
        dims (dict): Dictionary containing all dimensions for a curve, except for completeness(there is only one overall completeness value).
    Raises:
        Exception: An Exception is raised if any of the arguments are not of their expected types.
    """
    for key, value in dims.items():
        if key == 'Curve':
            name = value
        else:
            curveCol+= 1
            dataframe.insert(curveCol, key+name, value, True)


def hourlyScores(dataframe:pd.DataFrame):
    """Function that calculates and records the Dimension scores for each curve for each hour by using the calcScores() function for each hour of data.
    Args:
        dataframe (pd): Pandas dataframe filled with all dimension data for each curve passed in as input.
    Raises:
        Exception: An Exception is thrown when the argument passed is not a pandas dataframe.
    Returns:
        hrScores (pd): Pandas dataframe that includes the dimension scores for each curve for each hour."""
    hrScores = pd.DataFrame()
    hrData = pd.DataFrame()
    for index, row in dataframe.iterrows():
        currtime = timeStr(row.at['Time'])
        if index == 0:
            hrstart = timeStr(row.at['Time'])

        # Checking if an hour of data has been captured.
        if currtime - hrstart >= timedelta(hours=1):
            currscore = calcScores(hrData)
            currscore.name = str(hrstart)
            # Resetting hrstart.
            hrstart = currtime
            # Concatenating hourly scores to hrScores dataframe and reseting the hourly dataframe.
            hrScores = pd.concat([hrScores, currscore.to_frame()], axis=1)
            hrData = pd.DataFrame()
        else:
            hrData = pd.concat([hrData, row.to_frame(1).T])
    return hrScores
        
def calcScores(dataframe:pd.DataFrame):
    """Function that calculates the Dimension scores for each curve using the dimScore function in the dq_dimensions lib.

    Args: 
        dataframe (pd): Pandas dataframe filled with all dimension data for each curve passed in as input.
    Raises:
        Exception: An exception is thrown when the argument passed is not a pandas dataframe.
    Returns: 
        scoreDf (pd): Pandas series that includes the dimension scores for each curve.
    """
    #TODO add tests
    #TODO continue debugging find out why valididy is not being added into scoreDf
    CurveNames = get_Configs('curve').keys()
    Dimensions = get_Configs('dimensions').keys()
    scoreDf = pd.Series()
    for column in dataframe:
        if column in CurveNames:
            currCurve = column
        colcheck = column.split("_")
        if colcheck[0] in Dimensions:
            score = dq.dimScore(list(dataframe[column]))
            if colcheck[0] == 'Completeness':
                scoreDf[colcheck[0]] = score
            else:
                scoreDf[currCurve + '_' + colcheck[0]] = score
    return scoreDf

def hourlyOverall(dataframe: pd.DataFrame):
    """Function that creates the hourly aggregation output and calculates the hourly overall scores for the input dataset using the createOverall Function for each hour of scores.
    
    Args: 
        dataframe (pd): Pandas dataframe that inclues the hourly dimension scores for each curve.
    Raises: 
        Exception: An Exception is raised if the argument passed is not a pandas dataframe"""
    HrDQout = pd.DataFrame()
    weights = get_Configs('dimensions')
    for col in dataframe:
        coldata = createOverall(dataframe[col], True)
        HrDQout = pd.concat([HrDQout, coldata])

    for dim in HrDQout:
        if dim in weights.keys():
            HrDQout.at['Weightage (%)', dim] = weights.get(dim)
    totalweight = HrDQout.loc['Weightage (%)'].sum()
    HrDQout.at['Weightage (%)', 'Overall Score'] = totalweight
    return HrDQout

def createOverall(series:pd.Series(), hourly=False):
    """Function that creates the overall aggregation output and calculates the overall scores for the input dataset using the OverallDim() function in the dq_dimensions lib.
    
    Args:
        dataframe (pd): Pandas series that includes the dimension scores for each curve.
    Raises:
        Exception: An Exception is raised if the argument passed is not a pandas dataframe.
    Returns:
        DQout (pd): Pandas dataframe that includes the overall dimension scores and their corresponding weights set by user in config.yaml
    """
    #TODO break up and test
    DQout = pd.DataFrame()
    weights = get_Configs('dimensions')
    hrname = ''
    if hourly: 
        hrname = series.name
    vali = []
    freq = []
    cons = []
    uniq = []
    acc = [] 

    for idx, value in series.items():
        if 'Validity' in idx:
            vali.append(float(value))
        elif 'Frequency' in idx: 
            freq.append(float(value))
        elif 'Consistency' in idx: 
            cons.append(float(value))
        elif 'Uniqueness' in idx:
            uniq.append(float(value))
        elif 'Accuracy' in idx: 
            acc.append(float(value))
    
    for config in weights:
        arr = []
        match(config):
            case 'Validity':
                arr = vali
            case 'Frequency': 
                arr = freq
            case 'Consistency':
                arr = cons
            case 'Uniqueness': 
                arr = uniq
                print(arr)
            case 'Accuracy':
                arr = acc
            case 'Completeness':
                arr.append(float(series.at[config]))
        overallFormat(DQout, arr, config, hourly, hrname)
    
    calcOverallDQ(DQout, hourly, hrname)
    return DQout
    
def overallFormat(outData: pd.DataFrame, dArr: list, dim:str, hourly=False, hour=''):
    """Void Function that aids in formatting the DQout output dataframe in the createOverall() Function.
    Args:
        dArr (list): Dimension array containing all curve scores for a certain dimension.
        dim (str): Dimension name 
        hourly (boolean): Hourly aggregation toggle, defaulted to false when not passed as an argument.
        hour (str): Hour timestamp, defaulted to an empty string when not passed as an argument.
    Raises:

    """
    weights = get_Configs('dimensions')
    if hourly:
        outData.at[hour, dim] = round(dq.OverallDim(dArr), 2)
    else:
        outData.at['Score (%)', dim] = round(dq.OverallDim(dArr), 2)
        outData.at['Weightage (%)', dim] = weights.get(dim)
    
def calcOverallDQ(dataframe:pd.DataFrame, hourly=False, hour=''):
    """Void Function that calculates the Overall DQ score for a dataset using the calcWeight and OverallDQ functions in the dq_dimensions lib.

    Args:
        dataframe (pd.Dataframe): Pandas dataframe that includes the overall dimension scores and their corresponding weights set by user
    Raises:
        Exception: An Exception is raised if the argument passed is not a pandas dataframe.
    """
    #TODO Test

    #Creating list for weighted dimensions
    wDims = []
    configs = get_Configs('dimensions')
    for column in dataframe:
        if column in configs.keys():
            if hourly:
                wDims.append(dq.calcWeight(dataframe.loc[hour][column], configs.get(column)))
            else:
                wDims.append(dq.calcWeight(dataframe.loc['Score (%)'][column], dataframe.loc['Weightage (%)'][column]))
    if hourly:
        arr = [round(dq.OverallDQ(wDims), 2)]
    else:
        arr = [round(dq.OverallDQ(wDims), 2), dataframe.loc['Weightage (%)'].sum()]
    dataframe.insert(len(dataframe.columns), "Overall Score", arr, False)

def main():

    print('Loading Input...')
    data = fill_dataframe('input')
    print('Done!')

    print('Calculating and Recording Dimensions...')
    createDimensions(data)
    print('Done!')

    print('Calculating Scores...')
    datascores = calcScores(data)
    print('datascores done!')
    hrscores = hourlyScores(data)
    overall = createOverall(datascores)
    hroverall = hourlyOverall(hrscores)
    print('Done!')

    print('Outputting Data...')
    data.to_csv("curve_dimData.csv")
    datascores.to_csv("scores.csv")
    overall.to_csv("overall.csv")
    hrscores.to_csv('hrscores.csv')
    hroverall.to_csv('hroverall.csv')
    print('Done!') 

if __name__ == "__main__":
    main()