import os
import pandas as pd
import yaml
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
        case default:
            raise Exception('The value passed was an invalid config type key. Please pass a valid key: "curve"')


def fill_dataframe(itype):
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

def createDimensions(dataframe):
    """Void function that adds and calculates dimension columns in the dataframe passed in using the configurations set by user.
    Args:
        dataframe (pd): Pandas dataframe with intput .csv data
    Raises:
        TODO: Add exceptions and Test
    """
    # TODO Break this function up into multiple, too much going on in here.
    # TODO DONT FORGET TO TEST WITH DATA FROM EDWIN!!
    CurveConfigs = get_Configs('curve')
    GenConfigs = get_Configs('general')
    Ccheck = False
    if GenConfigs.get('CalcConsistency') is True: 
        consCheck = fill_dataframe('check')
        Ccheck = True
    AccConfigs = get_Configs('accuracy')
    AccCurves = AccConfigs.get('Curves')
    CurveNames = get_Configs('curve').keys()
    AllFreq = pd.DataFrame()
    comp = []
    numcurv = 0
    for column in dataframe:
        colNum = 0
        if column in CurveNames:
            numcurv += 1
            cConfig = CurveConfigs[column]
            val = []
            freq = []
            uniq = [] 
            cons = []
            acc = []
            colNum = dataframe.columns.get_loc(column)
            index = 0
            for i in dataframe[column]:
                val.append(dq.Validity(i, cConfig.get('upLim'), cConfig.get('lowLim')))
                if Ccheck:
                    cons.append(dq.Consistency(i, consCheck.iloc[index][column]))
                if index == 0:
                    if column in AccCurves.keys():
                        paired = AccCurves[column]
                        acc.append(dq.Accuracy(i, None, dataframe.iloc[index][paired], None))
                    #First sample/row scenarios.
                    freq.append(dq.Frequency(timeStr(dataframe.iloc[index]['Time']), None, GenConfigs.get('freqTol')))
                    uniq.append(dq.Uniqueness(i))
                else:
                    if column in AccCurves.keys():
                        paired = AccCurves[column]
                        acc.append(dq.Accuracy(i, prev, dataframe.iloc[index][paired], dataframe.iloc[index-1][paired]))
                    freq.append(dq.Frequency(timeStr(dataframe.iloc[index]['Time']), timeStr(dataframe.iloc[index-1]['Time']), GenConfigs.get('freqTol')))
                    uniq.append(dq.Uniqueness(i, prev))
                prev = i
                index += 1
            # these inserts will be put into a function here for testing ATM.
            count = 0
            AllFreq.insert(count, "Frequency", freq, True)
            count += 1
            dataframe.insert(colNum+1, "Validity_"+str(numcurv), val, True)
            dataframe.insert(colNum+2, "Frequency_"+str(numcurv), freq, True)
            if Ccheck:
                dataframe.insert(colNum+3, "Consistency_"+str(numcurv), cons, True)
                dataframe.insert(colNum+4, "Uniqueness_"+str(numcurv), uniq, True)
                if column in AccCurves.keys():
                    dataframe.insert(colNum+5, "Accuracy_"+str(numcurv), acc, True)
            else:
                dataframe.insert(colNum+3, "Uniqueness_"+str(numcurv), uniq, True)
                if column in AccCurves.keys():
                    dataframe.insert(colNum+4, "Accuracy_"+str(numcurv), acc, True)
    for idx, row, in AllFreq.iterrows():
        comp.append(dq.Completeness(row.tolist()))
    dataframe['Completeness'] = comp

def hourlyScores(dataframe:pd):
    """Function that calculates and records the Dimension scores for each curve for each hour using the dimScore function in the dq_dimensions lib.
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
        
    

def calcScores(dataframe:pd):
    """Function that calculates the Dimension scores for each curve using the dimScore function in the dq_dimensions lib.

    Args: 
        dataframe (pd): Pandas dataframe filled with all dimension data for each curve passed in as input.
    Raises:
        Exception: An exception is thrown when the argument passed is not a pandas dataframe.
    Returns: 
        scoreDf (pd): Pandas series that includes the dimension scores for each curve.
    """
    #TODO add tests
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

def hourlyOverall(dataframe: pd):
    """Function that creates the hourly aggregation output and calculates the hourly overall scores for the input dataset using the OverallDim() function in the dq_dimensions lib.
    
    Args: 
        dataframe (pd): Pandas dataframe that inclues the hourly dimension scores for each curve.
    Raises: 
        Exception: An Exception is raised if the argument passed is not a pandas dataframe"""
    HrDQout = pd.DataFrame()
    #TODO Break create Overall into several functions so you can pass each column as a series to calculate the overall scores for an hour.
    

def createOverall(dataframe:pd):
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
    vali = []
    freq = []
    cons = []
    uniq = []
    acc = [] 

    for idx, value in dataframe.items():
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
                arr = arr
        if config == 'Completeness':
            DQout.at['Score (%)', config] = int(dataframe.at[config])
        else:
            DQout.at['Score (%)', config] = int(dq.OverallDim(arr))
        DQout.at['Weightage (%)', config] = int(weights.get(config))

    calcOverallDQ(DQout)
    return DQout
    
def calcOverallDQ(dataframe:pd):
    """Void Function that calculates the Overall DQ score for a dataset using the calcWeight and OverallDQ functions in the dq_dimensions lib.

    Args:
        dataframe (pd): Pandas dataframe that includes the overall dimension scores and their corresponding weights set by user
    Raises:
        Exception: An Exception is raised if the argument passed is not a pandas dataframe.
    """
    #TODO Test

    #Creating list for weighted dimensions
    wDims = []
    configs = get_Configs('dimensions')
    for column in dataframe:
        if column in configs.keys():
            wDims.append(dq.calcWeight(dataframe.loc['Score (%)'][column], dataframe.loc['Weightage (%)'][column]))
    arr = [int(dq.OverallDQ(wDims)), dataframe.loc['Weightage (%)'].sum()]
    dataframe.insert(len(dataframe.columns), "Overall DQ Score", arr, False)

def main():

    print('Loading Input...')
    data = fill_dataframe('input')
    print('Done!')

    print('Calculating and Recording Dimensions...')
    createDimensions(data)
    print('Done!')

    print('Calculating Scores...')
    datascores = calcScores(data)
    hrscores = hourlyScores(data)
    overall = createOverall(datascores)
    print('Done!')

    print('Outputting Data...')
    data.to_csv("output.csv")
    datascores.to_csv("scores.csv")
    overall.to_csv("overall.csv")
    hrscores.to_csv('hrscores.csv')
    print('Done!') 

if __name__ == "__main__":
    main()