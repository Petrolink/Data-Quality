# Petrolink Data Quality Algorithm Script/Runner
This Data Quality Algorithm "Runner" is called a runner as it is the script that "runs" the recieved user input through the Data Quality Algorithm and produces output. The runner performs a data quality analysis by manipulating the input data recieved with the configurations set by users in the config.yaml file as well as functions imported from Petrolink's [dq_dimensions python module](../Library). A module that includes the dimension and calculation logic necessary to produce Data Quality statistics/scores.

## Table of Contents

1. [Running](#running)
2. [Input](#input)
3. [Functionality](#functionality)
4. [Data Manipulation Processes](#data-manipulation-processes)
5. [Assumptions](#assumptions)
6. [Configurations](#configurations)
7. [Objects](#objects)
8. [Functions](#functions)
8. [Running Unit Tests](#running-unit-tests)

## Running
1. Update the runner configurations in config.yaml file (located in Runner directory) using the input data file accordingly.
2. Navigate to the Runner directory within a terminal/cmd
3. Within terminal enter the following 
    - Python .\dq_runner.py
4. Save desired Outputs to a directory outside the downloaded repository's "Output" directory as the runner will overwrite all output wihtin the "Output" repo directory each time it executes.

## Accpted Input
The Runner is expecting numerical .csv input, other file formats are not accepted at this time.
 - Input should be formatted similarly to the following example

![Input Example](../../doc_images/image-8.png)

 - Time Column should be named "Time" and follow the same time format. 
 - Curve Columns names should be unitless

## Functionality
1. Runner will first parse through the downloaded repo's "Input" directory searching for the file whose name matches the one provided within the "DataFile" configuration in config.yaml and load the input data into a mutable dataframe.
2. Runner then calculates and records each curves dimension values for every sample in the loaded dataframe, these newly calculated/created dimension columns are inserted into the original loaded dataframe. (This is the curve_dimData.csv output in the Output directory)
3. Runner takes the dataframe that now contains dimensions and calculates the curve dimension scores for each aggregation (overall/hourly/daily) storing the calculated scores each into their own "aggregationscore" dataframes. (These are your "scores".csv outputs in the Output directory)
4. Using the calculated scores dataframes the runner then calculates the overall dimension scores as well as the DQ Score for each aggregation (overall/hourly/daily) storing the calculated overall scores into their own "aggregationoverall" dataframes. (These are your overall.csv outputs in the Output directory).
5. Script then outputs created dataframes to .csv files within the Output repo directory.

## Data Manipulation Processes
The Data Quality Algorithm Runner calculates and produces its data quality statistics by running data recieved as input data through various data manipulation processes.

### 1. Calculating and Recording Dimensions
The first data manipulation process input data will undergo wihtin the runner is the proccess of calculating and recording the dimension values/states for every curve and sample (row of data). 
 - This process is very dependent upon the following user configurations in 'config.yaml':
    - Curve_configs
        - Runner uses all Curve_config names/headers/keys when looping through input dataframe columns headers to determine which columns are configured curves that need to have their dimensions calculated and recorded.
        - Runner Utilizes all Cuve_config values (ie. upLim, lowLim...) when calculating the dimensions values for each sample's curves.
    - General_configs
        - CalcConsistency
            - Runner checks to determine if consistency dimensions should be calculated. 
        - Check_RigStatuses:
            - Runner checks to determine if rig_statuses should be checked when calculating the uniqueness value for each sample.
    - Accuracy_configs
        - Runner checks the configured accuracy curve to ensure the accuracy dimension is only evaluated for the Bit Depth cuve.
 - Steps
    1. Check if consistency should be calculated
    2. Create sDomains for the dataset (sub-process)
    3. Begin looping through input dataframe columns, ensure the current column is a configured curve if not skip the current column
    4. Determine if the current configured curve is BitDepth so accuracy dimension is set to be calculated
    5. Creates an empty list for each dimension. (Done for every configured curve)
    7. Begin Looping through every value of the current configured curve 
    8. Call dimensions functions imported from dq_dimensions module and append their return values to their corresponding lists.
    9. Once done looping through every value of the current configurd curve and creating the dimension lists, the runner then inserts the dimensions lists to the right of the current curve within the input dataframe. 
    10. Once all curves dimensions have been calculated and inserted into the input dataframe, the runner calculates the overall completeness dimension.
        - Completeness is not being calculated and recorded for every curve as completeness is good if all curve frequencies for the current sample are good.

 - **Create sDomains Subprocess**
    - This Subprocess is the process of looping through every row in the input data set to create and fill a SampleDomain dictionary object with the required sample curve data used by the rig status check functions imported from dq_dimensions. 
    - This process is dependent upon the following configurations in 'config.yaml':
        - Curve_configs
            - Runner uses to reference the rule's for specific curves. 
        - Rule_configs
            - Runner uses to grab and store the threshold/rule values for the rules corresponding curve.

### 2. Creating Aggregate datasets
The second data manipulation process the runner 

### 3. Calculating and Recording Scores 
The third data maniuplation process the runner puts the input data through is the process of calculating and recording the dimension scores for each curve, using the newly inserted dimension columns within the input dataframe. All aggregate data will go through the same process for each (hour/day) of data.
 - This process is dependent upon the following configurations in 'config.yaml':
    - Curve_configs
        - Uses the names/headers/keys of this configuration
    - Dimension_weights
        - Uses the names/headers/keys of this configuration
- Steps
    1. 

### 4. Calculating and Recording Overall Scores 
The third data maniuplation processs the runner "runs" the input data through the the process of calculating and recording the overall


## Assumptions
1. Runner is assuming the curves configured under the Curve_configs within config.yaml are identical to the corresponding curve headers within the input DataFile.csv.

## Configurations

## Objects
The Data Quality Runner only utilizes 1 object.

**SampleDomain**
 - Imported dictionary object from dq_dimensions module.
 - Dictionary object that holds the curve value(s) and threshold information required to call the dq_dimension rig status checks functions on each sample within a data set. 

## Functions

**yaml_loader(filepath)**

**timeStr(string)**

**get_Configs(cconfigType, testing)**

**fill_dataframe(itype, testing)**

**createDimensions(dataframe)**

**createSDomains(dataframe, testing)**

**fill_sampleDomain(cSample, pSample)**

**insertDims(dataframe, curveCol, dims)**

**aggScores(dataframe, aggType)**

**calcSccores(dataframe)**

**createOverall(series, hourly)**

**overallFormat(outData, dArr, dim, hourly, hour)**

**calcOverallDQ(dataframe, hourly, hour, testing)**

## Running Unit Tests
This runner has a Unittest that contains unittesting suites for every function in the runner and the imported dq_dimensions module. These unittests can be run to debug any issues you may have when using the runner within an avg of 2 minutes. Any issues that are encountered that are not discaovered by the unitests should be submitted to developers to be resolved. 

### How to Run UnitTest
1. Download the dq_unittest.py file
2. Navigate to the directory that contains the test using console/terminal/IDE.
3. Enter 'Python dq_unittest.py' 

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