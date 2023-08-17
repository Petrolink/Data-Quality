# Petrolink DataQuality Algorithm (Open-Sourced Python Implementation)
This "DataQuality_Algorithm" repository is the home of Petrolink's "open sourced" python DataQuality algorithm.

In this repository there are 2 main directories, these are "Input" and "Src". The "Input" directory is self explanitory as that is where users are to put static ".csv" data they would like to run a DataQuality analysis on. The "Src" directory is where users will find the source code that drives the Data Quality algorithm. 

There are two python.py programs/scripts that make up the source code for the python implementaion of the Data Quality Algorithm. These are the runner (dq_runner.py) and the library (dq_dimensions.py). The runner is an executable script where user input is loaded into a dataframe and manipulated using functions from the imported library to produce Data Quality output. The library is where the dimension calculation functions for the algorithm are located. 

## Table of Contents
1. [What is DataQuality](***REMOVED***scm/repo/git/DataQuality_Algorithim/code/sources/3300c23de1571af50d9f39560718aea5996de56a/README.md/#what-is-dataquality)
2. [How Petrolink Assesses Data Quality](***REMOVED***scm/repo/git/DataQuality_Algorithim/code/sources/a8a6c801cdfc381ade72d6a1d21569f92022837f/README.md/#how-petrolink-assesses-data-quality)
3. [Directory Guide](***REMOVED***scm/repo/git/DataQuality_Algorithim/code/sources/a8a6c801cdfc381ade72d6a1d21569f92022837f/README.md/#directory-guide)
4. [How to Run](***REMOVED***scm/repo/git/DataQuality_Algorithim/code/sources/a8a6c801cdfc381ade72d6a1d21569f92022837f/README.md/#how-to-run)
5. [Outputs Explained](***REMOVED***scm/repo/git/DataQuality_Algorithim/code/sources/a8a6c801cdfc381ade72d6a1d21569f92022837f/README.md/#outputs-explained)
4. [Future Steps](***REMOVED***scm/repo/git/DataQuality_Algorithim/code/sources/fc06201ff517060bc4f9ca80ccf1635a1491f932/README.md/#future-steps)

## What is Data Quality


## How Petrolink Assesses Data Quality


## Directory Guide
Input directory: Where users should put their .csv data that they wish to perform a Data Qulity analysis on.

Src directory: Location of the Data Quality Algorithm's source code.
  - Runner directory: Location of the executable runner's source code, configurations, unittesting suite, and documentation.
  - Library directory: Location of the importable dimension library's source code, unittesting suite, and documentation.


## Installation and Setup
1. Download the [DataQuality Algorithm Repo](***REMOVED***scm/repo/git/DataQuality_Algorithim/code/sources/e257c46a9c14e898d9a0a6507558b036ef879a2b/)
2. Install latest Python3
    - make sure to select "add Python to PATH"
3. Open command prompt
    - Enter "pip install pandas" 
    - Enter "pip install pyyaml"
4. Place static .csv data to be analyzed into the "Input" directory 
    - Please ensure to provide a consistency check file if calculating consitency
5. Update the DataFile and CheckFile(for consistency check) "General_configs" fields in config.yaml with the respective input file names


## Outputs Explained


## Future Steps
1. Accept real-time dynamic data as well as static data.