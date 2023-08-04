import math
from datetime import datetime, timedelta
#TODO add this library to pip.

# Samplewise Domain Dictionary (Use in runner as dictionary template to pass to checker functions).
sampleDomains = {
    'BitDepth': {
        'curr': float,
        'prev': float, 
        'surfaceThresh': float,
        'bitmoveThresh': float
    }, 
    'BlockPosition': {
        'curr': float,
        'prev': float,
        'deltaThresh': float
    },
    'RPM': {
        'value': float, 
        'thresh': float
    },
    'SPP': {
        'value': float,
        'thresh': float
    }, 
    'Hookload': {
        'value': float,
        'thresh': float
    }
}

# Curve Level Functions

def Validity(cValue:float, upLim:float, lowLim:float):
    """Function that determines the valididty of the current sample/row by checking if the curve value passed is within an upper and lower limit

    Args: 
        cValue (float): Curve value of the current sample/row
        upLim (float): Upper Limit for curve value
        lowLim (float): Lower Limit for curve value
    Raises:
        Exception: An Exception is raised when all of the arguments passed are not float values.
        Exception: An Exception is raised when the upLim <= lowLim.
    Returns:
        Boolean: True/Good if curve value is within set limits.
    """
    if upLim <= lowLim:
        raise Exception('Please ensure the upper limit argument is passed before the lower limit argument. ie. (cValue, upLim, lowLim)')
    if cValue > upLim or cValue < lowLim:
        return False
    return True

def Frequency(cT:datetime, pT, tol:float):
    """Function that determines the frequency of the current sample/row by checking if the timedelta between the current timestamp and the previous timestamp is within the expected frequency.
   
    Args: 
        cT (datetime): Current time of row/sample passed.
        pT (datetime or None): Current time of row/sample passed, if None assuming that it is the first row/sample (ie. "dq.Frequency(datetime val, None, 1.1)). 
        tol (float): Expected frequency tolerance.
    Raises: 
        Exception: An exception is raised if one or both of the time arguments passed are not of type datetime.
        Exception: An exception is raised if the cT is an earlier time than pT.
        Exception: An excception is raised if the tol argument is not a float value.
    Returns: 
        Boolean: True/Good if timedelta between cT and pT is within our expected frequency.
        Boolean: False/Bad if timedelta between cT and pT is out of our expected frequency or if it is the first row/sample.
    """
    if type(cT) is datetime and type(pT) is datetime:
        if type(tol) is not float:
            raise Exception('Please ensure the argument passed for "tol" is a float value, Frequency() will not function otherwise.')
        if pT > cT:
            raise Exception('Please ensure that you enter your arguments in the order of (currentTime, previousTime), Frequency() will not function correctly otherwise.')
        expectedF = timedelta(seconds=tol)
        delta = cT - pT
        if delta > expectedF:
            return False
    elif type(cT) is datetime and pT is None:
        # First sample in log case
        return False
    else:
        raise Exception('Please ensure that the args passed as "cT" and "pT" are of type datetime and follow the standard ISO format.')
    return True

def Completeness(cFreqs:list):
    """Function that detemrines the completeness of a sample/row of a log by ensuring all curve frequency values within the log are good.
    
    Args:
        cFreqs (list): Array of curve frequency values for one row/sample in the current log.
    Raises:
        Exception: An exception is raised if the argument passed is not an array.
        Exception: An exception is raised if any values in the array are not boolean values.
    Returns: 
        Boolean: True/Good if all values in the array passed in are "TRUE"
        Boolean: False/Bad if any of the values in the array passed in are "FALSE"
        """
    for i in cFreqs:
        if type(i) is bool or type(i) is None:
            if i is False: 
                return False
        else:
            raise Exception('Please only pass arrays with boolean or Null Values.')
    return True

def Uniqueness(curr:float, prev=0.0, stationary=False, onsurface=False):
    """Function that determines the uniqueness of a sample/row by comparing the current and previous curve values and ensuring they are not the same.
    #TODO Update tests to include rig statuses.
    Args:
        stationary (bool - OPTIONAL): Stationary rig status, defaulted to False.
        onsurface (bool - OPTIONAL): On surface rig status, defaulted to False.
        curr (float): Current curve value to be checked against "prev".
        prev (float or None): Previous curve value to be checked against "curr" or None in 1st sample case (ie. "dq.uniqueness(12.4)").
    Raises: 
        Exception: An exception is raised if the arguments passed are not of their set type (prev is an optional argument).
    Returns:
        Boolean: True/Good if either of the rig statuses are true.
        Boolean: True/Good if curr != prev or if curr is a float value and prev is a None value.
        Boolean: False/Bad if curr == prev."""
    if type(curr) is float and type(prev) is float:
        if curr == prev:
            return False
    elif type(curr) is float and type(prev) is None or type(curr) is float and prev == 0.0:
        return True
    else:
        raise Exception('Please ensure to only pass float values as arguments for Uniqueness() or a float as "curr" and a None as "prev" in a 1st sample/row case.')
    return True

def Consistency(xCurve:float, yCurve:float):
    """Function that determines the consistency of a sample/row by comparing the curve values from different logs at the same index/row.
    
    Args: 
        xCurve (float): curve value from a log reffered to as x.
        yCurve (float): curve value from a log reffered to as y that is used to check the consistency of log x.
    Raises:
        Exception: An Exception is raised if both arguments are not of type float.
    Returns:
        True if xCurve and yCurve are equal."""
    if type(xCurve) is None and type(yCurve) is None:
        return None
    elif type(xCurve) is not float and type(yCurve) is not float:
        raise Exception('Please only pass numerical values to Consistency().')
    if xCurve != yCurve:
        return False
    return True

def Accuracy(currBD=0.0, prevBD=0.0, currBH=0.0, prevBH=0.0, tol=0.0):
    """Function that determines the accuracy of a sample/row by taking the differnece of the current and previous BitDepth values and comparing it to the difference of the current and previous BlockHeight values. Ensuring that the BitDepth is simultaneously moving with the BlockHeight.
    
    Args: 
        currBD (float): current BitDepth value
        prevBD (float): previous BitDepth value
        currBH (float): current BlockHeight value
        prevBH (float): previous BlockHeight value 
        tol (Float or None): Accuracy tolerance specified by user, defaulted to 0 when not passed.
    Raises: 
        Exception: An exception is raised if all curr/prev arguments are not float values.
    Returns:
        Boolean: True
        Boolean: False
        None: Returns None if any of the paired curr/prev arguments passed are null.
    """
    if currBD == 0.0 or currBD is None and currBH == 0.0 or currBH is None:
        return None
    elif prevBD == 0.0 or prevBD is None and prevBH == 0.0 or prevBH is None:
        return None
    else:
        BDdelta = abs(currBD - prevBD)
        BPdelta = abs(currBH - prevBH)
    return checkDelta(BDdelta, BPdelta, tol)

# Checker Functions

def checkDelta(valOne: float, valTwo: float, tol: float):
    """Function that determines if the delta between two values lies within a givin tolerance.
    
    Args:
        valOne (float): 1st value to be used in calculating the delta
        valTwo (float): 2nd value to be used in calculating the delta
        tol (float): Delta tolerance
    Raises:
        Exception: An exception is raised if any of the arguments passed are not numerical.
    Returns: 
        Boolean: True if the calculated delta lies within the specified tolerance.
    """
    Delta = abs(valOne - valTwo)
    if Delta > tol:
        return False
    return True

def checkStationary(sDomain: dict):
    """Function that performs a stationary check by utilizing the following curves and their thresholds: 
    BitDepth, RPM, SPP, Hookload and BlockPosition.
    
    Args:
        sDomain (dict): 
    Raises:
        Exception: An Exception is raised if
    Returns:
        Boolean: True if all curve values are within their corresponding thresholds.
        Boolean: False if any of the curves needed for a stationary check are not included/passed as an argument.
        Boolean: False if any curve value breaks its threshold."""

def checkSurface(sDomain: dict):
    """Function that performs an on surface check by taking a bitdepth value and a on surface threshold.
    Args:
        sDomain (dict): 
    Raises:
        Exception: An exception is raised if the arguments passed are not numerical values.
    Returns:
        Boolean: True if depth <= thresh.
        Boolean: False if depth > thresh.
    """
    
    return True

# Score Calculation Functions
def dimScore(dim:list):
    """Function that calculates the score of a curve's dimension.
    Args:
        dim (list): Dimension Column values generated using the dq_dimension curve level functions.
    Raises:
        Exception: An Exception is raised if any value in the dimension column passed is not a boolean or None value.
        Exception: An Exception is raised if the argument passed is not a list.
    Returns: 
        score (float): Calculated score percentage of the dimension passed.
    """
    good = 0
    check =  all(isinstance(x, (bool, type(None))) for x in dim)
    if check is True:
        good = dim.count(True)
        score = (good/len(dim)) * 100
    else:
        raise Exception('Please only provide a list with containing only boolean data to dimScore().')
    return score

def OverallDim(data: list):
    """Function that calculates the overall score of a Dimension for a dataset.
    Args:
        data (list): List containing all curve scores for a certain dimension
    Raises:
        Exception: An Exception is raised if the argument passed is not a list.
        Exception: An Exception is raised if the contents of data are not all numerical.
    Returns:
        """
    Overall = 0
    for score in data: 
        if type(score) is float or type(score) is int:
            Overall += score
        else:
            raise Exception('Please only pass lists with pure numerical data to OverallDim().')
    return Overall/len(data)

def calcWeight(score: float, weight: float):
    """Function that calculates the weighted score of a dimension.
    Args:
        score (float): Dimension score
        weight (float): Dimension weightage
    Raises:
        Exception: An exception is raised if the arguments passed are not numerical.
    Returns:
        wScore (float): The weighted dimension score.
    """
    if weight > 100:
        raise Exception('Dimension Weights can only range from 0-100 as it is a percentage.')
    wScore = score * (weight/100)
    return wScore


def OverallDQ(data: list):
    """Funtion that calculates the overall Data Quality score of a dataset.
    Args: 
        data (list): List of weighted dimension scores
    Raises: 
        Exception: An Exception is raised if the argument passed is not a list.
        Exception: An Exception is raised if the contents of data are not all numerical.
        Exception: An Exception is raised if the sum of the contents of data is greater than 100.
    Returns:
        DQscore (float): Overall Data Quality Score.
    """
    DQscore = 0
    check =  all(isinstance(x, (float, int)) for x in data)
    if check:
        for dim in data:
            DQscore += dim
        if DQscore > 100:
            raise Exception('Please ensure the dimensions passed have been weighted, the sum of all weighted values should be <= 100. Sum Produced: ' + str(DQscore))
    else:
        raise Exception('Please only pass lists with pure numerical data to OverallDQ().')
    return DQscore
    