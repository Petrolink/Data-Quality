# PetroLink DataQuality Dimensions Python Library/Module
This DataQuality Dimension python library/module was created with the intent to open source callable curve-level dimension functions that implement petrolinks data quality dimension logic, allowing for a more direct representation of how Petrolink . This library can be installed and imported by any python developer that wishes to write their own runner/parser/etc. that utilizes our data quality logic.

The functions in this library were written to calculate/determine curve-level dimensions. Doing so allows for modular use in any script/program/algorithm/etx. that wishes to calculate and use dimension data to produce statistics such as data quality.

## Table of Contents
1. [Petrolinks Dimension Logic](#petrolinks-dimension-logic)
2. [Assumptions](#assumptions)
3. [How to Install and Import](#how-to-install-and-import)
4. [Constants](#constants)
5. [Functions](#functions) 
6. [Unit Tests](#unit-tests)

## Petrolinks Dimension Logic

## Assumptions

## How to Install and Import
1. Open command prompt and enter "pip install dq_dimensions"
2. At top of "Your.py" file use the following import statement
3. import dq_dimensions as dq

## Constants


## Functions
The Data Quality Dimensions Library includes three types of functions.

### 1. Curve Level Dimension Functions

**validity(value, upper, lower)**   
 - Function that determines the validity of a current sample/row by checking if the curve value passed is within an upper and lower limit. 
 - Returns True if value is within set limits.

**frequency(current_time, previous_time, tolerance)**

**completeness(curve_frequencies)**

**uniqueness(current, previous(OPTIONAL), stationary(OPTIONAL), on_surface(OPTIONAL))**

**consistency(curve, consistency_curve)**

**accuracy(value, value_check, tolerance(OPTIONAL))**

### 2. Rig_Status Check Functions

**check_stationary(s_domain)**

**check_surface(s_domain)**

### 3. Score Calculation Functions

**dim_score(dimension_col)**

**overall_dim(dimension_scores)**

**calc_weight(score, weight)**

**overall_dq(weighted scores)**

## Unit Tests
This library/module has a Unittest that contains unittesting suites for every function that can be run to debug any issues you may have when using the library. Any issues that are encountered that are not discovered by the unitests should be submitted to developers to be resolved.

### How to Run Test
1. Download the dimensionsTest.py file
2. Open file in preferred IDE
3. Navigate to the directory that contains the test using console/terminal.
4. Enter 'dq_dimensions.py'

### Interpreting Results 
