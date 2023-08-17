import math
from datetime import datetime, timedelta
#TODO add this library to pip.

# SampleDomain Curve/Value Name Constants
CURVE_BIT_DEPTH = 'BitDepth'
CURVE_BLOCK_POSITION = 'BlockPosition'
CURVE_RPM = 'RPM'
CURVE_SPP = 'SPP'
CURVE_HOOKLOAD = 'Hookload'
VALUE = 'value'
VALUE_THRESH = 'thresh'
# SampleDomain BitDepth and Block Position value Constants
VALUE_CURRENT = 'curr'
VALUE_PREVIOUS = 'prev'
VALUE_ON_SURFACE_THRESH = 'surfaceThresh'
VALUE_BPOS_DELTA_THRESH = 'deltaThresh'
VALUE_BITMOVEMENT_THRESH = 'bitmoveThresh'

# Samplewise Domain Dictionary (Use in runner as dictionary template to pass copies/instances to checker functions).
SampleDomain = {
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

# Curve Level Dimension Functions

def validity(value:float, upper:float, lower:float):
    """Function that determines the valididty of the current sample/row by checking if the curve value passed is within an upper and lower limit

    Args: 
        value (float): Curve value of the current sample/row
        upper (float): Upper Limit for curve value
        lower (float): Lower Limit for curve value
    Raises:
        Exception: An Exception is raised when all of the arguments passed are not float values.
        Exception: An Exception is raised when the upLim <= lowLim.
    Returns:
        Boolean: True/Good if curve value is within set limits.
    """
    if upper <= lower:
        raise Exception('Please ensure the upper limit argument is passed before the lower limit argument. ie. (cValue, upLim, lowLim)')
    if value >= upper or value <= lower:
        return False
    return True

def frequency(current_time:datetime, previous_time, tolerance:float):
    """Function that determines the frequency of the current sample/row by checking if the timedelta between the current timestamp and the previous timestamp is within the expected frequency.
   
    Args: 
        current_time (datetime): Current time of row/sample passed.
        previous_time (datetime or None): Current time of row/sample passed, if None assuming that it is the first row/sample (ie. "dq.Frequency(datetime val, None, 1.1)). 
        tolerance (float): Expected frequency tolerance in seconds.
    Raises: 
        Exception: An exception is raised if one or both of the time arguments passed are not of type datetime.
        Exception: An exception is raised if the cT is an earlier time than pT.
        Exception: An excception is raised if the tol argument is not a float value.
    Returns: 
        Boolean: True/Good if timedelta between cT and pT is within our expected frequency.
        Boolean: False/Bad if timedelta between cT and pT is out of our expected frequency or if it is the first row/sample.
    """
    if type(current_time) is datetime and type(previous_time) is datetime:
        if type(tolerance) is not float:
            raise Exception('Please ensure the argument passed for "tol" is a float value, Frequency() will not function otherwise.')
        if previous_time > current_time:
            raise Exception('Please ensure that you enter your arguments in the order of (currentTime, previousTime), Frequency() will not function correctly otherwise.')
        expectedF = timedelta(seconds=tolerance)
        delta = current_time - previous_time
        if delta > expectedF:
            return False
    elif type(current_time) is datetime and previous_time is None:
        # First sample in log case
        return False
    else:
        raise Exception('Please ensure that the args passed as "cT" and "pT" are of type datetime and follow the standard ISO format.')
    return True

def completeness(curve_frequencies:list):
    """Function that detemrines the completeness of a sample/row of a log by ensuring all curve frequency values within the log are good.
    
    Args:
        curve_frequencies (list): Array of curve frequency values for one row/sample in the current log.
    Raises:
        Exception: An exception is raised if the argument passed is not an array.
        Exception: An exception is raised if any values in the array are not boolean values.
    Returns: 
        Boolean: True/Good if all values in the array passed in are "TRUE"
        Boolean: False/Bad if any of the values in the array passed in are "FALSE"
        """
    for i in curve_frequencies:
        if type(i) is bool or type(i) is None:
            if i is False: 
                return False
        else:
            raise Exception('Please only pass arrays with boolean or Null Values.')
    return True

def uniqueness(current:float, previous=0.0, stationary=False, on_surface=False):
    """Function that determines the uniqueness of a sample/row by comparing the current and previous curve values and ensuring they are not the same.
    Args:
        current (float): Current curve value to be checked against "prev".
        previous (float or None): Previous curve value to be checked against "curr" or None in 1st sample case (ie. "dq.uniqueness(12.4)").
        stationary (bool - OPTIONAL): Stationary rig status, defaulted to False.
        on_surface (bool - OPTIONAL): On surface rig status, defaulted to False.
    Raises: 
        Exception: An exception is raised if the arguments passed are not of their set type (prev is an optional argument).
    Returns:
        Boolean: True/Good if either of the rig statuses are true.
        Boolean: True/Good if curr != prev or if curr is a float value and prev is a None value (1st row of data).
        Boolean: False/Bad if curr == prev."""
    if type(stationary) == bool and type(on_surface) == bool:
        if stationary or on_surface:
            return True
        else:
            if type(current) is float and type(previous) is float:
                if current == previous:
                    return False
            elif type(current) is float and type(previous) is None or type(current) is float and previous == 0.0:
                return True
            else:
                raise Exception('Please ensure to only pass float values as arguments(curr/prev) for Uniqueness() or a float as "curr" and a None as "prev" in a 1st sample/row case.')
    else:
        raise Exception('Please ensure to only pass boolean values as rig status arguments for Uniqueness()')
    return True

def consistency(curve:float, consistency_curve:float):
    """Function that determines the consistency of a sample/row by comparing the curve values from different logs at the same index/row.
    
    Args: 
        curve (float): curve value from data log.
        consistency_curve (float): curve value from a consistency check data log.
    Raises:
        Exception: An Exception is raised if both arguments are not of type float.
    Returns:
        True if xCurve and yCurve are equal."""
    if type(curve) is None and type(consistency_curve) is None:
        return None
    elif type(curve) is not float and type(consistency_curve) is not float:
        raise Exception('Please only pass numerical values to Consistency(). Passed: ' + str(type(curve)) + ' ' + str(type(consistency_curve)))
    if curve != consistency_curve:
        return False
    return True

def accuracy(value: float, value_check:float, tolerance=0.0001):
    """Function that determines the accuracy of a sample/row by ensuring that the delta of value and value_check is <= tolerance (set by user, or 0.0001 when not specified).
    
    Args: 
        value (float): Value whose accuracy is being determined.
        value_check (float): Value being used to determine the accuracy of value.
        tolerance (Float or None): Accuracy tolerance specified by user, (OPTIONAL) defaulted to 0.0001 when not passed.
    Raises: 
        Exception: An exception is raised if any of the values passed are not float values.
    Returns:
        Boolean: True if the delta of val - valcheck <= tol
        Boolean: False if the delta of val - valcheck > tol
    """
    delta = abs(value - value_check)
    if delta > tolerance:
        return False
    return True

# Rig_Status Check Functions
    
def check_stationary(s_domain: dict):
    """Function that performs a stationary check by utilizing the following curves and their thresholds: 
    BitDepth, RPM, SPP, Hookload and BlockPosition.
    
    Args:
        s_domain (dict): Dictionary filled with required data from each row of input for rig status checks (PLEASE USE TEMPLATE "sampleDomain" DICT from dq_dimensions.py)
    Raises:
        Exception: An Exception is raised if the argument passed is not of type "dict"
        Exception: An Exception is raised if the dictionary passed is not an instance of the "sampleDomain" dictionary in dq_dimensions.py.
    Returns:
        Boolean: True if all curve values are within their corresponding thresholds.
        Boolean: False if any of the required values in the s_domain that are needed for a stationary check are empty.
        Boolean: False if any curve value breaks its threshold."""
    # Ensuring the dictionary passed as input contains the same curve fields as the sampleDomain dictionary template.
    if s_domain.keys() != SampleDomain.keys():
        raise Exception('Please ensure you are passing a copy/instance of the sampleDomain dictionary found in dq_dimensions.py.')
    # Ensuring all required fields are filled with data
    required = True
    for key1, val1 in s_domain.items():
        if val1.keys() != SampleDomain[key1].keys():
            raise Exception('Please ensure you are passing a copy/instance of the sampleDomain dictionary found in dq_dimensions.py.')
        for key2, val2 in val1.items():
            # Checking if expected numerical data is empty.
            if type(val2) is type:
                required = False
    
    if required:
        # Stationary rule logic 
        if s_domain[CURVE_BIT_DEPTH][VALUE_CURRENT] > s_domain[CURVE_BIT_DEPTH][VALUE_ON_SURFACE_THRESH] and s_domain[CURVE_RPM][VALUE] < s_domain[CURVE_RPM][VALUE_THRESH] and s_domain[CURVE_SPP][VALUE] < s_domain[CURVE_SPP][VALUE_THRESH] and s_domain[CURVE_HOOKLOAD][VALUE] >= s_domain[CURVE_HOOKLOAD][VALUE_THRESH] and accuracy(s_domain[CURVE_BLOCK_POSITION][VALUE_CURRENT], s_domain[CURVE_BLOCK_POSITION][VALUE_PREVIOUS], s_domain[CURVE_BLOCK_POSITION][VALUE_BPOS_DELTA_THRESH]) and accuracy(s_domain[CURVE_BIT_DEPTH][VALUE_CURRENT], s_domain[CURVE_BIT_DEPTH][VALUE_PREVIOUS], s_domain[CURVE_BIT_DEPTH][VALUE_BITMOVEMENT_THRESH]):
            return True
    return False

def check_surface(s_domain: dict):
    """Function that performs an on surface check by taking a bitdepth value and a on surface threshold.
    Args:
        s_domain (dict): Dictionary filled with required data from each row of input for rig status checks (PLEASE USE TEMPLATE "sampleDomain" DICT from dq_dimensions.py)
    Raises:
        Exception: An exception is raised if the argument passed is not of type "dict".
        Exception: An Exception is raised if passed a dictionary that does not include the required fields.
    Returns:
        Boolean: True if depth <= thresh.
        Boolean: False if depth > thresh.
    """
    # Ensuring the dictionary passed as input contains the same curve fields as the sampleDomain dictionary template.
    if s_domain.keys() != SampleDomain.keys():
        raise Exception('Please ensure you are passing a copy/instance of the sampleDomain dictionary found in dq_dimensions.py.')
    # Ensuring all required fields are filled with data
    for key, val in s_domain.items():
        if val.keys() != SampleDomain[key].keys():
            raise Exception('Please ensure you are passing a copy/instance of the sampleDomain dictionary found in dq_dimensions.py.')
    # Checking if expected numerical data is empty.    
    if type(s_domain[CURVE_BIT_DEPTH][VALUE_CURRENT]) is type or type(s_domain[CURVE_BIT_DEPTH][VALUE_ON_SURFACE_THRESH]) is type:
        return False
    
    # Surface rule logic 
    if s_domain[CURVE_BIT_DEPTH][VALUE_CURRENT] > s_domain[CURVE_BIT_DEPTH][VALUE_ON_SURFACE_THRESH]:
        return False
    return True

# Score Calculation Functions
def dim_score(dimension_col:list):
    """Function that calculates the score of a curve's dimension.
    Args:
        dimension_col (list): Dimension Column values generated using the dq_dimension curve level functions.
    Raises:
        Exception: An Exception is raised if any value in the dimension column passed is not a boolean or None value.
        Exception: An Exception is raised if the argument passed is not a list.
    Returns: 
        score (float): Calculated score percentage of the dimension passed.
    """
    good = 0
    check =  all(isinstance(x, (bool, type(None))) for x in dimension_col)
    if check is True:
        good = dimension_col.count(True)
        score = (good/len(dimension_col)) * 100
    else:
        raise Exception('Please only provide a list with containing only boolean data to dimScore().')
    return score

def overall_dim(dimension_scores: list):
    """Function that calculates the overall score of a Dimension for a dataset.
    Args:
        dimension_scores (list): List containing all curve scores for a certain dimension
    Raises:
        Exception: An Exception is raised if the argument passed is not a list.
        Exception: An Exception is raised if the contents of data are not all numerical.
    Returns:
        """
    overall = 0
    for score in dimension_scores: 
        if type(score) is float or type(score) is int:
            Overall += score
        else:
            raise Exception('Please only pass lists with pure numerical data to OverallDim().')
    return overall/len(dimension_scores)

def calc_weight(score: float, weight: float):
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
    wscore = score * (weight/100)
    return wscore


def overall_dq(weighted_scores: list):
    """Funtion that calculates the overall Data Quality score of a dataset.
    Args: 
        weighted_scores (list): List of weighted dimension scores
    Raises: 
        Exception: An Exception is raised if the argument passed is not a list.
        Exception: An Exception is raised if the contents of data are not all numerical.
        Exception: An Exception is raised if the sum of the contents of data is greater than 100.
    Returns:
        dq_score (float): Overall Data Quality Score.
    """
    dq_score = 0
    check =  all(isinstance(x, (float, int)) for x in weighted_scores)
    if check:
        for dim in weighted_scores:
            DQscore += dim
        if dq_score > 100:
            raise Exception('Please ensure the dimensions passed have been weighted, the sum of all weighted values should be <= 100. Sum Produced: ' + str(DQscore))
    else:
        raise Exception('Please only pass lists with pure numerical data to OverallDQ().')
    return dq_score
    