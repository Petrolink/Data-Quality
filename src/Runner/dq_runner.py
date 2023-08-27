import os
import pandas as pd
import numpy as np
import yaml
import copy
from datetime import datetime, timedelta
import sys
import dq_dimensions as dq


def yaml_loader(filepath: str):
    """Function that Loads a yaml file
    Args: 
        filepath (str): path to yaml configuration file.
    Returns:
        The Loaded yaml config file as a dictionary.
    """
    with open(os.path.join(sys.path[0], filepath), 'r') as file_descriptor:
        data = yaml.load(file_descriptor, Loader=yaml.Loader)
    return data

def timeStr(string: str):
    """Function that takes in a string and returns it as a datetime.
    Args: 
        string (str): String value containing a UTC timestamp that follows ISO standards.
    Raises:
        Exception: An exception is thrown when a non string value is passed as an argument.
    Returns:
        A datetime value created from the timestamp string."""
    return datetime.fromisoformat(string)

def get_Configs(configType:str, testing=False):
    """Function that retrieves the type of configuration and returns them as a iterable dictionary.
    Args:
        configType (str): String key value used to request types of user configurations from config.yaml
        testing (bool): A testing toggle used only by unittesting suite.
    Raises:
        Exception: An exception is raised when the argument passed is not a str value.
    Returns:
        configs['REQUESTED_CONFIG_FIELD'] (dict) : The requested configuration field.
    """
    if testing:
        configs = yaml_loader('unittest_inputs/testconfigs.yaml')
    else:
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
                print('triggered')
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

def fill_dataframe(itype:str, testing=False):
    """Function that reads in a .csv file and returns a mutable dataframe filled with the .csv data.
    Args: 
        itype (str): An input type key word (input or check)
        testing (bool): A testing toggle used only in unittesting suite.
    Raises:
        Exception: An Exception occurs when the file path parameter is an empty string.
        Exception: An Exception occurs when the input file is not of type .csv.
        Exception: An Exception occurs when there is no data in the input file.
    Returns:
        df (pd.Dataframe): Pandas dataframe with input .csv data.
    """
    if testing:
        configs = get_Configs('general', True)
        filename = 'src/Runner/unittest_inputs'
    else:
        configs = get_Configs('general')
        filename = 'input'

    if len(itype) == 0:
        raise Exception('Please provide a valid input type key-word ("input" or "check"), empty strings will not be accepted.')
    match(str.lower(itype)):
        case 'input':
            if not configs.get('DataFile').endswith('csv'):
                raise Exception('Expecting a .csv file name for the DataFile config in General_configs.')
            csvfile = os.path.realpath(os.path.join(os.path.dirname(__file__), '../..', filename, configs.get('DataFile')))
        case 'check':
            if not configs.get('CheckFile').endswith('csv'):
                raise Exception('Expecting a .csv file name for the CheckFile config in General_configs.')
            csvfile = os.path.realpath(os.path.join(os.path.dirname(__file__), '../..', filename, configs.get('CheckFile')))
        case default:
            raise Exception('The value passed is an invalid input type key. Please Specify "input" or "check".')
    try:
        df = pd.read_csv(csvfile)
    except Exception as e:
        raise Exception(e)
    return df

def createDimensions(dataframe:pd.DataFrame):
    """Void function that adds and calculates curve dimension columns in the dataframe passed in using the configurations set by user.
    Args:
        dataframe (pd): Pandas dataframe with input .csv data
    Raises:
        TODO: Add exceptions and Test
    """
    # TODO (if time) Break this function up into multiple, too much going on in here.
    CurveConfigs = get_Configs('curve')
    CurveNames = get_Configs('curve').keys()
    GenConfigs = get_Configs('general')
    AccConfigs = get_Configs('accuracy')
    cCheck = GenConfigs.get('CalcConsistency')
    if cCheck:
        consCheck = fill_dataframe('check')
    
    print('Creating sDomains')
    sDomains = createSDomains(dataframe)
    print('Complete!')

    # Variables used to calulate and record completion.
    AllFreq = pd.DataFrame()
    comp = []
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
            if column in AccConfigs['Curve']:
                accuracy = True
            # Lists used to record dimension values for each curve
            val = []
            freq = []
            uniq = [] 
            cons = []
            acc = []
            sta = []
            sur = []
            colNum = dataframe.columns.get_loc(column)
            lastgoodVal = 0.0
            index = 0
            # Looping through each curve value (curr) of the current curve
            for curr in dataframe[column]:
                if type(curr) is float or type(curr) is int:
                    sDomain = sDomains[index]
                    val.append(dq.validity(curr, cConfig.get('upLim'), cConfig.get('lowLim')))
                    if cCheck:
                        if consCheck.iloc[index][column].item() is None:
                            cons.append(None)
                        else:
                            cons.append(dq.consistency(float(curr), float(consCheck.iloc[index][column].item())))
                    if index == 0:
                        #First sample/row scenarios.
                        if accuracy:
                            acc.append(None)
                        freq.append(dq.frequency(timeStr(dataframe.iloc[index]['Time']), None, GenConfigs.get('freqTol')))
                        if GenConfigs['CheckRigStatuses']:
                            match(cConfig.get('rigStatuses').lower()):
                                case 'all':
                                    uniq.append(dq.uniqueness(float(curr), 0.0, dq.check_stationary(sDomain), dq.check_surface(sDomain)))
                                case 'stationary': 
                                    uniq.append(dq.uniqueness(float(curr), 0.0, dq.check_stationary(sDomain)))
                                case 'surface': 
                                    uniq.append(dq.uniqueness(float(curr), 0.0, dq.check_surface(sDomain)))
                                case default:
                                    raise Exception('Please ensure to specify which rigStatuses should be checked for ' + column + '. (all, stationary, or surface)')
                            sta.append(dq.check_stationary(sDomain))
                            sur.append(dq.check_surface(sDomain))
                        else:
                            uniq.append(dq.uniquness(curr))
                    else:
                        if accuracy:
                            if sDomain['Hookload']['value'] < sDomain['Hookload']['thresh']:
                                acc.append(True)
                            else:
                                acc.append(dq.accuracy(abs(sDomain['BitDepth']['curr'] - sDomain['BitDepth']['prev']),  abs(sDomain['BlockPosition']['curr']- sDomain['BlockPosition']['prev']), sDomain['BlockPosition']['deltaThresh']))
                        freq.append(dq.frequency(timeStr(dataframe.iloc[index]['Time']), timeStr(dataframe.iloc[index-1]['Time']), GenConfigs.get('freqTol')))
                        if GenConfigs['CheckRigStatuses']:
                            match(cConfig.get('rigStatuses').lower()):
                                case 'all':
                                    uniq.append(dq.uniqueness(float(curr), float(lastgoodVal), dq.check_stationary(sDomain), dq.check_surface(sDomain)))
                                case 'stationary': 
                                    uniq.append(dq.uniqueness(float(curr), float(lastgoodVal), dq.check_stationary(sDomain)))
                                case 'surface': 
                                    uniq.append(dq.uniqueness(float(curr), float(lastgoodVal), dq.check_surface(sDomain)))
                                case default:
                                    raise Exception('Please ensure to specify which rigStatuses should be checked for ' + column + '. (all, stationary, or surface)')
                            sta.append(dq.check_stationary(sDomain))
                            sur.append(dq.check_surface(sDomain))
                        else:
                            uniq.append(dq.uniqueness(float(curr), float(lastgoodVal)))
                    lastgoodVal = curr
                else:
                    val.append(False)
                    cons.append(False)
                    uniq.append(False)
                    freq.append(dq.frequency(timeStr(dataframe.iloc[index]['Time']), timeStr(dataframe.iloc[index-1]['Time']), GenConfigs.get('freqTol')))
                    if accuracy: 
                        acc.append(False)
            
                index += 1

            # Inserts
            count = 0
            AllFreq.insert(count, "Frequency", freq, True)
            count += 1
            if cCheck:
                dimensions = {'Curve': column, 'Validity_': val, 'Frequency_': freq, 'Consistency_': cons, 'Uniqueness_': uniq, 'Stationary_': sta, 'Surface_': sur}
            else:
                dimensions = {'Curve': column, 'Validity_': val, 'Frequency_': freq, 'Uniqueness_': uniq}
            if accuracy:
                dimensions['Accuracy_']= acc
            insertDims(dataframe, colNum, dimensions)
    for idx, row, in AllFreq.iterrows():
        comp.append(dq.completeness(row.tolist()))
    dataframe['Completeness'] = comp

def createSDomains(dataframe: pd.DataFrame, testing=False):
    """Function that returns a dictionary filled with sampleDomains for each row in the dataframe passed by using the sampleDomains() function.
    Args:
        dataframe (pd.Dataframe): Pandas dataframe with input .csv data
        testing (bool): A testing toggle used only in unittesting suite.
    Raises:
        Exception: An Exception is raised if the argument passed is not a pandas dataframe.
    Returns:
        sDomains (dict): Dictionary of sDomain dictionaries for every row in the input data.
    """
    sDomains = {}
    for idx, row in dataframe.iterrows():
        if idx == len(dataframe)/2 and testing == False:
            print('50%' + ' complete')
        if idx == 0: 
            sDomains[idx] = fill_sampleDomain(row)
        else:
            sDomains[idx] = fill_sampleDomain(row, prev)
        prev = row
    return sDomains

def fill_sampleDomain(cSample: pd.Series, pSample=pd.Series):
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
    if type(cSample) is pd.Series:
        CurveConfigs = get_Configs('curve')
        RuleConfigs = get_Configs('rules')
        sDomain = dq.SAMPLE_DOMAIN
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
    else:
        raise Exception('Please only pass pandas series to fill_sampleDomain.')
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

def aggScores(dataframe:pd.DataFrame, aggType:str):
    """Function that calculates and records the Dimension scores for each curve for each [TYPE OF AGGREGATION] by using the calcScores() function for each (hour/day) of data.
    Args:
        dataframe (pd): Pandas dataframe filled with all dimension data for each curve passed in as input.
        aggType (str): Desired type of aggregation, "hourly" or "daily".
    Raises:
        Exception: An Exception is thrown when the argument passed is not a pandas dataframe.
    Returns:
        aggScores (pd): Pandas dataframe that includes the dimension scores for each curve for each [TYPE OF AGGREGATION REQUESTED]."""
    aggScores = pd.DataFrame()
    aggData = pd.DataFrame()
    match(aggType):
        case 'hourly':
            agg = timedelta(hours=1)
        case 'daily':
            agg = timedelta(days=1)
        case default:
            raise Exception(aggType + ' is not a valid aggType. Accepted: "hourly" or "daily".')

    for index, row in dataframe.iterrows():
        currtime = timeStr(row.at['Time'])
        if index == 0:
            aggStart = timeStr(row.at['Time'])

        # Checking if an agg(hour/day) of data has been captured.
        if currtime - aggStart >= agg:
            currscore = calcScores(aggData)
            currscore.name = str(aggStart)
            # Resetting aggstart.
            aggStart = currtime
            # Concatenating aggregate scores to hrScores dataframe and reseting the agg dataframe.
            aggScores = pd.concat([aggScores, currscore.to_frame()], axis=1)
            aggData = pd.DataFrame()
        else:
            aggData = pd.concat([aggData, row.to_frame(1).T])
    return aggScores
        
def calcScores(dataframe:pd.DataFrame):
    """Function that calculates the Dimension scores for each curve using the dimScore function in the dq_dimensions lib.

    Args: 
        dataframe (pd): Pandas dataframe filled with all dimension data for each curve passed in as input.
    Raises:
        Exception: An exception is thrown when the argument passed is not a pandas dataframe.
    Returns: 
        scoreDf (pd): Pandas series that includes the dimension scores for each curve.
    """
    if type(dataframe) is pd.DataFrame:
        CurveNames = get_Configs('curve').keys()
        Dimensions = get_Configs('dimensions').keys()
        scoreDf = pd.Series()
        for column in dataframe:
            if column in CurveNames:
                currCurve = column
            colcheck = column.split("_")
            if colcheck[0] in Dimensions:
                score = dq.dim_score(list(dataframe[column]))
                if colcheck[0] == 'Completeness':
                    scoreDf[colcheck[0]] = score
                else:
                    scoreDf[currCurve + '_' + colcheck[0]] = score
    else:
        raise Exception('Please only pass pandas Dataframes to calcScores().')
    return scoreDf

def aggOverall(dataframe: pd.DataFrame):
    """Function that creates the aggregation outputs and calculates the aggregation overall scores for the input dataset using the createOverall Function for each agg(hour/day) of scores.
    
    Args: 
        dataframe (pd.Dataframe): Pandas dataframe that inclues (hourly/daily) dimension scores for each curve.
    Raises: 
        Exception: An Exception is raised if the argument passed is not a pandas dataframe
    Returns:
        aggOut (pd.Dataframe): Pandas dataframe
    """
    if len(dataframe) == 0:
        return pd.DataFrame()
    aggOut = pd.DataFrame()
    weights = get_Configs('dimensions')
    for col in dataframe:
        coldata = createOverall(dataframe[col], True)
        aggOut = pd.concat([aggOut, coldata])

    for dim in aggOut:
        if dim in weights.keys():
            aggOut.at['Weightage (%)', dim] = weights.get(dim)
    totalweight = aggOut.loc['Weightage (%)'].sum()
    aggOut.at['Weightage (%)', 'Overall Score'] = totalweight
    return aggOut

def createOverall(series:pd.Series(), hourly=False):
    """Function that creates the overall output and calculates the overall scores for the input dataset using the OverallDim() function in the dq_dimensions lib.
    
    Args:
        dataframe (pd.Series): Pandas series that includes the dimension scores for each curve.
    Raises:
        Exception: An Exception is raised if the argument passed is not a pandas dataframe.
    Returns:
        DQout (pd.Dataframe): Pandas dataframe that includes the overall dimension scores and their corresponding weights set by user in config.yaml
    """
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
        Exception: An Exception is raised if any of the arguments passed are not of their expected type.
    """
    weights = get_Configs('dimensions')
    if hourly:
        outData.at[hour, dim] = round(dq.overall_dim(dArr), 2)
    else:
        outData.at['Score (%)', dim] = round(dq.overall_dim(dArr), 2)
        outData.at['Weightage (%)', dim] = weights.get(dim)
    
def calcOverallDQ(dataframe:pd.DataFrame, hourly=False, hour='', testing=False):
    """Void Function that calculates the Overall DQ score for a dataset using the calcWeight and OverallDQ functions in the dq_dimensions lib.

    Args:
        dataframe (pd.Dataframe): Pandas dataframe that includes the overall dimension scores and their corresponding weights set by user
    Raises:
        Exception: An Exception is raised if the argument passed is not a pandas dataframe.
    """
    #Creating list for weighted dimensions
    wDims = []
    if testing:
        configs = get_Configs('dimensions', True)
    else:
        configs = get_Configs('dimensions')

    for column in dataframe:
        if column in configs.keys():
            if hourly:
                wDims.append(dq.calc_weight(dataframe.loc[hour][column], configs.get(column)))
            else:
                wDims.append(dq.calc_weight(dataframe.loc['Score (%)'][column], dataframe.loc['Weightage (%)'][column]))
    if hourly:
        arr = [round(dq.overall_dq(wDims), 2)]
    else:
        arr = [round(dq.overall_dq(wDims), 2), dataframe.loc['Weightage (%)'].sum()]
    dataframe.insert(len(dataframe.columns), "Overall Score", arr, False)

def main():

    print('Loading Input...')
    data = fill_dataframe('input')
    print('Done!')
    print()

    print('Calculating and Recording Dimensions...')
    createDimensions(data)
    print('Done!')
    print()

    print('Calculating Scores...')
    datascores = calcScores(data)
    print('Overall scores calculated.')
    hrscores = aggScores(data, 'hourly')
    print('Hourly scores calculated.')
    dailyscores = aggScores(data, 'daily')
    print('Daily scores calculated.')
    print('Calculating Overall Scores...')
    overall = createOverall(datascores)
    print('Overall DQ calculated.')
    hroverall = aggOverall(hrscores)
    print('Hourly DQ\'s calulated.')
    dailyoverall = aggOverall(dailyscores)
    print('Daily DQ\'s calculated.')
    print('Done!')
    print()

    print('Outputting Data...')
    output = os.path.realpath(os.path.join(os.path.dirname(__file__), '..\..', 'Output'))
    data.to_csv(output+"\curve_dimData.csv")
    datascores.to_csv(output+"\scores.csv")
    overall.to_csv(output+"\overall.csv")
    hrscores.to_csv(output+"\hrscores.csv")
    hroverall.to_csv(output+"\hroverall.csv")
    dailyscores.to_csv(output+"\dailyscores.csv")
    dailyoverall.to_csv(output+"\dailyoverall.csv")
    print('Done!') 

if __name__ == "__main__":
    main()