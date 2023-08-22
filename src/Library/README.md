# PetroLink DataQuality Dimensions Python Library/Module
This DataQuality Dimension python library/module was created with the intent to open source callable curve-level dimension functions that implement the Petrolink data quality algorithm's dimension logic, allowing for a more direct representation of how Petrolink determines their dimension values. 

This module can be installed and imported by any python developer that wishes to write their own runner/parser/etc. that utilizes our data quality logic to calculate and use dimension data to produce statistics such as data quality.

## Table of Contents
1. [Dimensions of Data Quality](#dimensions-of-data-quality)
2. [Assumptions](#assumptions)
3. [How to Install and Import](#how-to-install-and-import)
4. [Objects](#objects)
5. [Constants](#constants)
6. [Functions](#functions) 
7. [Unit Tests](#unit-tests)

## Dimensions of Data Quality
Data Quality(DQ) dimension is a recognized term used by data management professionals to describe a feature of data that can be measured or assessed against defined standards in order to determine the quality of data. In other words, something (data item, record, data set or database) that can either be measured or assessed based on various standards in order to understand the quality of data. 

We have collected the various aspects with which the quality of the surface and subsurface data can be quantified as: 

1. Frequency 
2. Completeness 
2. Uniqueness 
4. Consistency 
5. Validity 
6. Accuracy 

Multi-dimensional quality analysis concept includes screening every data point through various lenses and coming up with an Overall Score for Data Quality. 

The main intention is to use these dimensions to measure the impact of the poor data quality in terms of cost, regulatory compliance, and to increase the quality of the service provided. 

The client should agree to the adopted quality rules with which the data will be assessed against. In some cases, these rules can be decided by the client as these rules might interfere with their operational procedures. 

## Assumptions
1. completeness() Function is assuming that the (list) argument passed in is a list filled with the frequency values for every curve for a sample/row.
2. consistency() Function is assuming that the (float) arguments passed in are not from the same log (1 from input log, 1 from a consistency check log).
3. Rig Status check functions are assuming the (dict) argument passed is a SampleDomain dict or a dict with equivalent key values.
4. dim_score() Funciton is assuming that the (list) argument passed in is a whole dimension column for a curve (ie. the Frequency values for an arbitrary curve).
5. overall_dim() Function is assuming that the (list) argument passed in is a list containing all the calculated scores for a certain dimension in a dataset (ie. all the Frequency scores from every curve).

## How to Install and Import
1. Open command prompt and enter "pip install dq_dimensions"
2. At top of "Your.py" file use the following import statement
    - "import dq_dimensions as dq"

## Objects
The Data Quality Dimensions Library includes one dictionary object. 

**SampleDomain**
 - Dictionary object that holds the curve value(s) and threshold information required to perfrom rig status checks for each sample within a data set. 
 - Current curves used:
    - Bit Depth
    - Block Position
    - RPM
    - SPP
    - Hookload
  - The Bit Depth and Block Position curve fields require their current value, previous value, and specific domain threshold(s) as compared to the rest of the curve fields that only require a value (current) and their corresponding curve domain threshold.

## Constants
The Data Quality Dimensions Library includes four types of constants. Three of which are used as accessors to fields or values of the SampleDomain dict object.

### 1. SampleDomain Instance Constant

**SAMPLE_DOMAIN**
 - New instance of a SampleDomain dict.
 - Use this constant to create a SampleDomain for each sample of data.

### 2. SampleDomain Curve Field Constants

**CURVE_BIT_DEPTH**
 - Curve field key for Bit Depth.

**CURVE_BLOCK_POSITION**
 - Curve field key for Block Position.

**CURVE_RPM**
 - Curve field key for RPM.

**CURVE_SPP**
 - Curve field key for SPP.

**CURVE_HOOKLOAD**
 - Curve field key for Hookload.

### 3. SampleDomain General Value Constants

**VALUE**
 - Curve value.

**VALUE_THRESH**
 - Curve Domain Threshold.

### 4. SampleDomain BitDepth and BlockPosition Value Constants
**VALUE_CURRENT**
 - Current curve value. 

**VALUE_PREVIOUS**
 - Previous curve value.

**VALUE_ON_SURFACE_THRESH**
 - On Surface Domain Threshold

**VALUE_BPOS_DELTA_THRESH**
 - Block Position Delta Domain Threshold 

**VALUE_BITMOVEMENT_THRESH**
 - Bit Depth Movement Domain Threshold.

## Functions
The Data Quality Dimensions Library includes three types of functions.

### 1. Curve Level Dimension Functions

**validity(value, upper, lower)**   
 - Function that determines the validity of a current sample/row by checking if the curve value passed is within an upper and lower limit. 
 - Returns True if value is within set limits.

**frequency(current_time, previous_time, tolerance)**
 - Function that determines the frequency of the current sample/row by checking if the timedelta between the current timestamp and the previous timestamp is within the expected frequency tolerance.
 - Returns True if the timedelta calculated is within the expected frequency.

**completeness(curve_frequencies)**
 - Function that detemrines the completeness of a sample/row of a log by ensuring all curve      frequency values within the log are good.
 - Returns True if all curve frequency values are good.

**uniqueness(current, previous(OPTIONAL), stationary(OPTIONAL), on_surface(OPTIONAL))**
 - Function that determines the uniqueness of a sample/row by comparing the current and previous curve values and ensuring they are not the same.
 - Returns True if any optional rig status (bool) arguments are passed in as True.
 - Returns True if current is not equal to previous.

**consistency(curve, consistency_curve)**
 - Function that determines the consistency of a sample/row by comparing the curve values from different logs at the same index/row.
 - Returns True if curve and consistency_curve are equal.

**accuracy(value, value_check, tolerance(OPTIONAL))**
 - Function that determines the accuracy of a sample/row by ensuring that the delta of value and value_check is <= tolerance (set by user, or 0.0001 when not specified).

### 2. Rig_Status Check Functions

**check_stationary(s_domain)**
 - Function that performs a stationary check by utilizing a "SampleDomain" dictionary containing the following curves and their thresholds: BitDepth, RPM, SPP, Hookload and BlockPosition.
 - Returns True if all curve values are within their corresponding thresholds.

**check_surface(s_domain)**
 - Function that performs an on surface check by taking a bitdepth value and a on-surface threshold from a "SampleDomain" dictionary.
 - Returns True if the bitdepth value <= on-surface thresh

### 3. Score Calculation Functions

**dim_score(dimension_col)**
 - Function that calculates the score of a curve's dimension.
 - Returns the calculated score percentage (float) of the dimension passed.

**overall_dim(dimension_scores)**
 - Function that calculates the overall score of a Dimension for a dataset.
 - Returns the calculated overall dimension score of the dimension values passed in as a list.

**calc_weight(score, weight)**
 - Function that calculates the weighted score of a dimension.
 - Returns the calculated weighted score.

**overall_dq(weighted scores)**
 - Function that calculates the overall Data Quality score of dataset.
 - Returns the calculated Data Quality Score.

## Unit Tests
This library/module has a Unittest that contains unittesting suites for every function that can be run to debug any issues you may have when using the library. Any issues that are encountered that are not discovered by the unitests should be submitted to developers to be resolved.

### How to Run UnitTest
1. Download the dimensionsTest.py file
2. Open file in preferred IDE
3. Navigate to the directory that contains the test using console/terminal.
4. Enter 'dimensionsTest.py' 

### Interpreting Results 
After running the unittests you will either recieve an "OK" message which is synonymous to passing.

```
............
----------------------------------------------------------------------
Ran 12 tests in 0.002s

OK
```
Or a "FAILED" message similar to the following:
```
.........E..
======================================================================
ERROR: test_overall_dq (__main__.Testdq_dimensions.test_overall_dq)
Testing overall_dq() Function in dq_dimensions that takes in a list containing weighted dimension scores of a dataset and returns the Overall DQ Score of said dataset
----------------------------------------------------------------------
Traceback (most recent call last):
  File "c:\Users\gonzaleza\OneDrive - Petrolink Technical Services\DataQuality_Algorithim\Src\Library\dimensionsTest.py", line 280, in test_overall_dq
    self.assertRaises(TypeError, dq_dimensions.overall_dq, 'Not a list')
  File "C:\Users\gonzaleza\AppData\Local\Programs\Python\Python311\Lib\unittest\case.py", line 766, in assertRaises
    return context.handle('assertRaises', args, kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
FAILED (errors=1)
```