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
1. Runner parses through the downloaded repo's "Input" directory searching for the file whose name matches the one provided within the "DataFile" configuration in config.yaml and load the input data into a mutable dataframe.
2. Runner then calculates and records each curves dimension values for every sample in the loaded dataframe, these newly calculated/created dimension columns are inserted into the original loaded dataframe. (This is the [curve_dimData.csv output](../../README.md#outputs-explained) in the Output directory)
3. Runner takes the dataframe that now contains dimensions and calculates the curve dimension scores for each aggregation (overall/hourly/daily) storing the calculated scores each into their own "aggregationscore" dataframes. (These are your [scores.csv outputs](../../README.md#outputs-explained) in the Output directory)
4. Using the calculated scores dataframes the runner then calculates the overall dimension scores as well as the DQ Score for each aggregation (overall/hourly/daily) storing the calculated overall scores into their own "aggregationoverall" dataframes. (These are your [overall.csv outputs](../../README.md#outputs-explained) in the Output directory).
5. Runner then outputs all created dataframes to .csv files within the Output repo directory.

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
 - Steps:
    1. Check if consistency should be calculated
    2. Create sDomains for the dataset (sub-process)
    3. Begin looping through input dataframe columns, ensure the current column is a configured curve if not skip the current column
    4. Determine if the current configured curve is BitDepth so accuracy dimension is set to be calculated
    5. Create empty lists for each dimension. (Done for every configured curve)
    7. Begin Looping through every value of the current configured curve 
    8. Call dimensions functions imported from dq_dimensions module and append their return values to their corresponding lists.
    9. Once done looping through every value of the current configured curve, the runner then inserts the newly created dimensions lists with the following format (Dimension_Curve, ie. Frequency_BPOS) to the right of the current curve within the input dataframe. 
    10. Once all curves dimensions have been calculated and inserted into the input dataframe, the runner calculates the overall completeness dimension.
        - Completeness is not being calculated and recorded for every curve as completeness is good if all curve frequencies for the current sample are good.

 - **Creating sDomains (SUBPROCESS)**
    - This Subprocess is the process of looping through every row in the input data set to create and fill a SampleDomain dictionary object with the required sample curve data used by the rig status check functions imported from dq_dimensions. 
    - This process is dependent upon the following configurations in 'config.yaml':
        - Curve_configs
            - Runner uses to reference the rule's for specific curves. 
        - Rule_configs
            - Runner uses to grab and store the threshold/rule values for the rules corresponding curve.

### 2. Calculating and Recording Scores 
The second data maniuplation process the runner puts the input data through is the process of calculating and recording the dimension scores for each curve, using the newly inserted dimension columns within the input dataframe. All aggregate data will go through the same process for each (hour/day) of data.
 - This process is dependent upon the following configurations in 'config.yaml':
    - Curve_configs
        - Uses the names/headers/keys of this configuration
    - Dimension_weights
        - Uses the names/headers/keys of this configuration
- Steps:
    1. Create an empty score dataframe to fill with data and return
    2. Begin looping through the curve dimension data column headers
    3. If the current column is a dimension column call the dim_score() function imported from the dq_dimensions module, runner passes the column data as a list as the argument
    4. Store the calculated score into the score dataframe created in step 1
    5. Once loop is complete return the filled in score dataframe

### 3. Creating Aggregate datasets/scores
The third data manipulation process the runner puts the input data through is the process of creating aggregate datasets. This process is actually done in parallel to the score calculation process for each aggregation. As the Runner grabs a (hour/day)s worth of data and passes it to the function that performs the calculation process and concatenates the scores produced by the calculation function to a dataframe for the current aggregation's scores (this is repeated for each (hour/day) of data).
 - This process is not dependent upon any configurations
 - Steps:
    1. Create an empty aggregate score dataframe to fill with aggregate data and return
    2. Create an empty temporary dataframe to store the current working (hour/day) of data
    3. Begin to loop through each sample of data, checking each samples timestamp
    4. Add each sample to the temporary dataframe created in step 2 until an (hour/day) of data has elapsed
    5. Once an (hour/day) of data has been temporarily stored, pass the temporary dataframe to the function that performs the calculation process.
    6. Store the current working (hour/day)s score to the aggregate score dataframe created in step 1
    7. Once done looping and every (hour/day) of data has scores return the aggregrate score dataframe.

### 4. Calculating and Recording Overall Scores 
The fourth and final data maniuplation processs the runner "runs" the input data through the the process of calculating and recording the overall dimension scores as well as the overall data quality score for the score dataset (entire or aggregate). 
 - This process is dependent upon the following configurations in 'config.yaml':
    - Dimension_weights
        - Runner uses config key/headers/names to create the overall dimension columns
        - Runner uses config values to determine the weights for each dimension when calculating the overall DQ score.
 - Steps
    1. Create an empty overall output dataframe to be filled with overall score data for the dataset
    2. Create empty lists for each dimension
    3. Begin to loop through score dataset
    4. If the current index is a dimension score append it to is corresponding dimension list created in step 2
    5. Once done looping through dataset, call the overall_dim() function imported from the dq_dimensions module for each dimension, passing the corresponding dimension list an argument.
    6. Store the overall dimension score returned from overall_dim() in the overall output dataframe created in step 1
    7. Once all overall dimension scores have all been calculated and stored calculate and store overall data quality score by taking a weightage average of the overall dimension scores using their corresponding configured weights.
    
    The Runner repeats steps 1-7 for every (hour/day) of dimension scores when calculating the overall scores for aggregate datasets.
    
    8. Return the overall output dataframe for the dataset.

## Assumptions
1. Assuming the curves configured under the Curve_configs within config.yaml are identical to the corresponding curve headers within the input DataFile.csv.
2. Assuming input data is formatted with a "Time" column and unitless curve columns. [see example](#accpted-input)
3. 

## Configurations
The Data Quality Runner is dependent upon its user configurations failure to follow the following instructions could lead to errors. There are 4 configuration fields in the runners 'config.yaml' file.

### 1. General_configs

### 2. Curve_configs

### 3. Rule_thresholds

### 4. Dimension_weights


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