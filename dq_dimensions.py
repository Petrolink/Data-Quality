import math
from datetime import datetime, timedelta
#TODO add this library to pip when completed.

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
    if type(cFreqs) is list:
        for i in cFreqs:
            if type(i) is bool or type(i) is None:
                if i is False: 
                    return False
            else:
                raise Exception('Please only pass arrays with boolean or Null Values.')
    else:
        raise Exception('Please only pass boolean arrays as arguments to Completeness().')
    return True

def Uniqueness(curr:float, prev=0.0):
    """Function that determines the uniqueness of a sample/row by comparing the current and previous curve values and ensuring they are not the same.
    
    Args:
        curr (float): Current curve value to be checked against "prev".
        prev (float or None): Previous curve value to be checked against "curr" or None in 1st sample case (ie. "dq.uniqueness(12.4)").
    Raises: 
        Exception: An exception is raised if both arguments are not type(None) and are not of type float.
    Returns:
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
        if abs(BDdelta - BPdelta) > tol:
            return False
    return True

def logwiseagg(dimValues):
    """Function that calculates a logwise dimension using the dimension column passed as a list.
    Args:
        dimValues (list): Dimension column values generated using the dq_dimension curve level functions.
    Raises:
        Exception: 
    Returns:
        Measure: The calculated 
    """