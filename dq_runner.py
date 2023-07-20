import os
import sys
import pandas as pd
import yaml
from datetime import datetime
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
        case 'accuracy':
            if len(configs['Curve_conifgs']) == 0:
                raise Exception('Expecting input for Accuracy_conifgs in config.yaml')
        case default:
            raise Exception('The value passed was an invalid config type key. Please pass a valid key: "curve"')


def fill_dataframe(csvfile):
    """Reads in a .csv file and returns a mutable dataframe filled with .csv data.
    Args: 
        csvfile (str): The file path to log.csv
    Raises:
        Exception: An Exception occurs when the file path parameter is an empty string.
        Exception: An Exception occurs when the input file is not of type .csv.
        Exception: An Exception occurs when there is no data in the input file.
    Returns:
        df (pd): Pandas dataframe with input .csv data.
    """
    df = pd.DataFrame()
    if len(csvfile) == 0:
        raise Exception('Please provide a valid path to fill_dataframe(), empty strings will not be accepted.')
    if not csvfile.endswith('.csv'):
        raise Exception("Expecting .csv file format")
    df = pd.read_csv(os.path.join(sys.path[0], csvfile))
    if df.empty:
        raise Exception("Expeccting file with data")
    return df

def createDimensions(dataframe):
    """Void function that adds and calculates dimension columns in the dataframe passed in using the configurations set by user.
    Args:
        dataframe (pd): Pandas dataframe with intput .csv data
    Raises:
        TODO: Add exceptions and Test
    """
    CurveConfigs = get_Configs('curve')
    CurveNames = get_Configs('curve').keys()
    for column in dataframe:
        colNum = 0
        if column in CurveNames:
            cConfig = CurveConfigs[column]
            val = []
            freq = []
            uniq = []
            cons = []
            colNum = dataframe.columns.get_loc(column)
            index = 0
            for i in dataframe[column]:
                val.append(dq.Validity(i, cConfig.get('upLim'), cConfig.get('lowLim')))
                if index == 0:
                    #First sample/row scenarios.
                    freq.append(dq.Frequency(timeStr(dataframe.iloc[index]['Time']), None, cConfig.get('freqTol')))
                    uniq.append(dq.Uniqueness(i))
                else:
                    freq.append(dq.Frequency(timeStr(dataframe.iloc[index]['Time']), timeStr(dataframe.iloc[index-1]['Time']), cConfig.get('freqTol')))
                    uniq.append(dq.Uniqueness(i, prev))
                prev = i
                index += 1
            # these inserts will be put into a function here for testing ATM.
            dataframe.insert(colNum+1, "Validity", val, True)
            dataframe.insert(colNum+2, "Frequency", freq, True)
            dataframe.insert(colNum+3, "Uniqueness", uniq, True)


def main():
    data = fill_dataframe('example.csv')
    # data Original data fed in as input 
    print(data)
    createDimensions(data)
    #output data
    print(data)

if __name__ == "__main__":
    main()