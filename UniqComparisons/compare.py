import pandas as pd
import numpy as np
from datetime import datetime
import os
import sys

def timeStr(string: str):
    """Function that takes in a string and returns it as a datetime.
    Args: 
        string (str): String value containing a UTC timestamp that follows ISO standards.
    Raises:
        Exception: An exception is thrown when a non string value is passed as an argument.
    Returns:
        A datetime value created from the timestamp string."""
    time = datetime.fromisoformat(string)
    time.replace(tzinfo=None)
    return time

def compare(myrow: pd.Series, edwindata: pd.DataFrame, output: pd.DataFrame, compOut: pd.DataFrame, index):
    for idx, row, in edwindata.iterrows():
        if myrow.at['Uniqueness_'+row.at['CurveName']] != row.at['Result']:
            print(myrow.at['Uniqueness_'+row.at['CurveName']])
            print(row.at['Result'])
            compOut.at[index, 'Differ'] = True

def main():
    mine = pd.read_csv(os.path.join(sys.path[0], 'dimData.csv'), index_col=0)
    edwins = pd.read_csv(os.path.join(sys.path[0], 'Edwins.csv'), index_col=0)
    output = pd.read_csv(os.path.join(sys.path[0], 'RI_CONS.csv'), index_col=0)
    comparison = output.copy(deep=True)
    comparison.insert(len(comparison.columns), 'Differ', '')

    for idx, row in mine.iterrows():
        temp = pd.DataFrame()
        for ind, erow, in edwins.iterrows():
            if datetime.strptime(ind, ' %m/%d/%Y %I:%M:%S') != timeStr(idx):
                #print(datetime.strptime(ind, ' %m/%d/%Y %I:%M:%S'))
                #print(timeStr(idx))
                edwins = edwins.drop(edwins.index[0:10])
                break
            temp = pd.concat([temp, erow.to_frame().T])
        print(temp)
        compare(row, temp, output, comparison, idx)

    comparison.to_csv('comparison.csv')

if __name__ == "__main__":
    main()