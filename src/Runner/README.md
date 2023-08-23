# Petrolink Data Quality Algorithm Script/Runner
This Data Quality Algorithm "Runner" is called a runner as it is the executable that "runs" the recieved user input through the Data Quality Algorithm and produces output. The runner performs a data quality analysis by manipulating the input data recieved with the configurations set by users in the config.yaml file as well as functions imported from Petrolink's [dq_dimensions python module](../Library/README.md). A module that includes the dimension and calculation logic necessary to produce Data Quality statistics/scores.

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
1. Runner will first parse through the downloaded repo's "Input" directory searching for the file whose name matches the one provideed within the "DataFile" configuration and load the input data into a mutable dataframe.
2. Runner then calculates and records each curves dimension values for every sample in the loaded dataframe, these newly calculated/created dimension columns are inserted into the original loaded dataframe. (This is the curve_dimData.csv output in the Output directory)
3. Runner takes the dataframe that now contains dimensions and calculates the curve dimension scores for each aggregation (overall/hourly/daily) storing the calculated scores each into their own "aggregationscore" dataframes. (These are your "scores".csv outputs in the Output directory)
4. Using the calculated scores dataframes the runner then calculates the overall dimension scores as well as the DQ Score for each aggregation (overall/hourly/daily) storing the calculated overall scores into their own "aggregationoverall" dataframes. (These are your overall.csv outputs in the Output directory).
5. Script then outputs created dataframes to .csv files within the Output repo directory.

## Data Manipulation Processes
### Calculating and Recording Dimensions

## Assumptions

## Configurations

## Objects

## Functions

## Running Unit Tests
