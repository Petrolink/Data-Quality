import math
import yaml
import os
import sys
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict, make_dataclass, field

def yaml_loader(filepath):
    """Function that Loads a yaml file"""
    with open(os.path.join(sys.path[0], filepath), 'r') as file_descriptor:
        data = yaml.load(file_descriptor, Loader=yaml.Loader)
    return data

@dataclass
class curvedef:
    name: str = None
    fTolerance: float = None
    upLimit: float = None
    lowLimit: float = None
    
@dataclass
class curve:
    validity: bool = None
    frequency: bool = None
    completeness: bool = None
    uniqueness: bool = None
    concistency: bool = None
    accuracy: bool = None


@dataclass
class sample:
    # Loading yaml config file into configs variable
    configs = yaml_loader('config.yaml')
    curves = {}
    # Creating a curve instance for each curve configured by user in yaml config file.
    for key, value in configs['Curve_configs'].items():
        curves[key] = curve()
    rowNum: int = 0
    cT: datetime = None
    pT: datetime = None

def add_configuratedfields(sNode):
    """Function that creates new attributes/fields requested/configured by user for sample in yaml config file.
    Args: 
        sNode (sample): Sample intance containing all mutable sample information"""

def Validity(sNode):
    """Function that determines the validity of curve value(s) for a sample/row by checking if the curve value(s) is null and by comparing the curve value(s) with the sensor upper and lower limits.
    Args: 
        sNode (sample): Sample instance containing all mutable sample information 
    Returns: 
        Boolean: True/Good if curve data is not null and is within upper and lower sensor limits.
    """
    for curve in sNode.curves:
        print(curve)
    return True

def Frequency(sNode):
    """Function that determines the frequency of the current sample/row by checking if the timedelta between the current timestamp and the previous timestamp is within the expected frequency.
   
    Args: 
        sNode (sample): Sample instance containing all mutable sample information 
    Raises: 
        Exception: An exception is raised if one or both of the arguments passed are not of type datetime.
        Exception: An exception is raised if the cT is an earlier time than pT.
    Returns: 
        Boolean: True/Good if timedelta between cT and pT is within our expected frequency.
    """
    # Would like to be builiding a column of Bad and Good rows through a pandas database to avoid having to use global variables when keeping track of good and bad rows.
    if type(sNode.cT) is datetime and type(sNode.pT) is datetime:
        if sNode.pT > sNode.cT:
            raise Exception('Please ensure that you enter your arguments in the order of (currentTime, previousTime), Frequency() will not function correctly otherwise.')
        expectedF = timedelta(seconds=1.1)
        delta = sNode.cT - sNode.pT
        if delta > expectedF:
            return False
    else:
        raise Exception('Please ensure that the args passed to Frequency() are of type datetime and follow the standard ISO format.')
    return True

def Completeness(sNode):
    """Function that determines the completeness of a sample by making use of the samples frequency.

    Args: 
        sNode (sample): Sample instance containing all mutable sample information
    Raises: 
        Exception: An exception is raised if the argument passed is not an instance of the "sample" class.
        Exception: An exception is raised if the frequency of the sample passed as an argument has not been set to true/good or false/bad.
    Returns: 
        Boolean: True/Good if the samples frequency is true/good.
    """
    if isinstance(sNode, sample):
       if sNode.frequency is None:
           raise Exception('Completeness for a sample cannot be determined prior to a samples frequency.')
       elif sNode.frequency is False:
           return False
    else:
        raise Exception('Please ensure the argument passed to Completeness() is an instance of the "sample" class.')
    return True

def Uniqueness(sNode):
    """Function that determines the uniqueness of curve values for a sample/row by checking if the current samples curve value is equal to the previous samples curve value.
    
    Args: 
        sNode (sample): Sample instance containing all mutable sample information
    Return:
        Boolean: True/Good if the curve value of the sample passed is not equal to the previous samples curve value.
    """
    return 0

def Consistency(sNode):
    """blah blah blah"""
    return 0

def DomainChecks(sNode):
    """blah blah blah"""
    return 0

def main():
    rowOne = sample()
    rowOne.cT = datetime.fromisoformat('2020-03-08T19:00:32.9150000Z')
    rowOne.pT = datetime.fromisoformat('2020-03-08T19:00:31.9050000Z')
    print(rowOne.curves['BitDepth'])
    rowOne.frequency = Frequency(rowOne.cT, rowOne.pT)
    rowTwo = sample()
    badprev = datetime.fromisoformat('2020-03-08T19:00:30.8920000Z')
    # print(Frequency(rowOne.cT, badprev)) use to show a bad frequency 
    # rowOne.completeness = Completeness(rowOne)
    tstr = 'BitDepth'
    rowOne.__class__ = make_dataclass('Y', fields=[(tstr, float, field(init=False))], bases=(sample,))
    rowOne.__class__ = make_dataclass('Y', fields=[('bdvalidity', bool, field(init=False))], bases=(sample,))
    setattr(rowOne, tstr, 900.12)
    setattr(rowOne, 'bdvalidity', Validity(rowOne))
    # print(asdict(rowOne))

if __name__ == "__main__":
    main()