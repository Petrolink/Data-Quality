import os
import pandas as pd
import yaml
from datetime import datetime
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
    #TODO finish updating file structure/loading and update unittests on Monday
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
    consCheck = fill_dataframe('check')
    CurveConfigs = get_Configs('curve')
    GenConfigs = get_Configs('general')
    AccConfigs = get_Configs('accuracy')
    AccCurves = AccConfigs.get('Curves')
    CurveNames = get_Configs('curve').keys()
    AllFreq = pd.DataFrame()
    comp = []
    for column in dataframe:
        colNum = 0
        if column in CurveNames:
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
            dataframe.insert(colNum+1, "Validity", val, True)
            dataframe.insert(colNum+2, "Frequency", freq, True)
            dataframe.insert(colNum+3, "Consistency", cons, True)
            dataframe.insert(colNum+4, "Uniqueness", uniq, True)
            if column in AccCurves.keys():
                dataframe.insert(colNum+5, "Accuracy", acc, True)
    for idx, row, in AllFreq.iterrows():
        comp.append(dq.Completeness(row.tolist()))
    dataframe['Completeness'] = comp

def main():
    data = fill_dataframe('input')
    # data Original data fed in as input 
    print(data)
    createDimensions(data)
    #output data
    data.to_csv("output.csv")

if __name__ == "__main__":
    main()