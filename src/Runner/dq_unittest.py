import unittest
import math
import pandas as pd
import numpy as np
from datetime import datetime
# Temporary fix that allows dimensions lib to be imported from other dir while the lib is not registered with pip
# According to https://www.geeksforgeeks.org/python-import-module-outside-directory/
import sys
import os
sys.path.append(os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'Library')))
import dq_dimensions
import dq_runner

class Testdq_dimensions_runner(unittest.TestCase):
    def setUp(self): 
        self.current = datetime.fromisoformat('2020-03-08T19:00:32.9150000Z')
        self.previous = datetime.fromisoformat('2020-03-08T19:00:31.9050000Z')
        self.badprev = datetime.fromisoformat('2020-03-08T19:00:30.8920000Z')
        self.testinput = pd.read_csv(os.path.join(sys.path[0], 'unittest_inputs/testinput.csv'))
        self.dimdata = pd.read_csv(os.path.join(sys.path[0], 'unittest_inputs/testdimdata.csv'), low_memory=False)
        self.dimdata = self.dimdata.replace(np.nan, None, regex=True)
        self.hrscores = pd.read_csv(os.path.join(sys.path[0], 'unittest_inputs/hrtestscores.csv'), index_col=0)
        self.overall = pd.read_csv(os.path.join(sys.path[0], 'unittest_inputs/testoverallDQ.csv'), index_col=0)
        self.test = [2.4, 3.4]
        self.baddict = {
            'BitDepth':{
                'wrong': float
            }
        }
        # sDomain dictionary used to trigger stationary rig status
        self.stationary = {
            'BitDepth': {
                'curr': 2611.11,
                'prev': 2611.11, 
                'surfaceThresh': 328.0,
                'bitmoveThresh': 0.2
            }, 
            'BlockPosition': {
                'curr': 30.11,
                'prev': 30.11,
                'deltaThresh': 0.1
            },
            'RPM': {
                'value': 0.0, 
                'thresh': 5.0
            },
            'SPP': {
                'value': 0.0,
                'thresh': 500.0
            }, 
            'Hookload': {
                'value': 104.29,
                'thresh': 100.0
            }
        }
        # sDomain dictionary used to trigger surface rig status
        self.surface = {
            'BitDepth': {
                'curr': 66.12,
                'prev': 66.12, 
                'surfaceThresh': 328.0,
                'bitmoveThresh': 0.2
            }, 
            'BlockPosition': {
                'curr': 1.54,
                'prev': 0.98,
                'deltaThresh': 0.1
            },
            'RPM': {
                'value': 0, 
                'thresh': 5.0
            },
            'SPP': {
                'value': 0,
                'thresh': 500.0
            }, 
            'Hookload': {
                'value': 25.755,
                'thresh': 100.0
            }
        }
        self.empty = {
            'BitDepth': {
                'curr': float,
                'prev': 66.12, 
                'surfaceThresh': 328.0,
                'bitmoveThresh': 0.2
            }, 
            'BlockPosition': {
                'curr': 1.54,
                'prev': 0.98,
                'deltaThresh': 0.1
            },
            'RPM': {
                'value': 0, 
                'thresh': 5.0
            },
            'SPP': {
                'value': 0,
                'thresh': 500.0
            }, 
            'Hookload': {
                'value': 25.755,
                'thresh': 100.0
            }
        }


    # Testing Dimension Functions in dq_dimensions.py

    def test_Validity(self):
        """Testing Valididty() function in dq_dimensions.py that takes in a curve value argument(float) and determines if it is within the upper and lower limit arguments passed by user."""
        # Ensuring Validity() throws an Exception when the arguments passed are not all float values.
        self.assertRaises(Exception, dq_dimensions.Validity, '1.0', 1.0, 1.0)
        self.assertRaises(Exception, dq_dimensions.Validity, 1.0, 1, 1.0)
        self.assertRaises(Exception, dq_dimensions.Validity, 1.0, 1.0, True)
        # Ensuring Validity() throws an Exception when upper limit <= lower limit.
        self.assertRaises(Exception, dq_dimensions.Validity, 100, 1, 150)
        self.assertRaises(Exception, dq_dimensions.Validity, 100, 150, 150)
        # Ensuring Validity() returns true when lowLimit <= cValue <= upperLimit.
        self.assertTrue(dq_dimensions.Validity(10.0, 50.0, 1.0))
        # Ensuring Validity() returns false when cValue < Lower Limit or cValue > UpperLimit
        self.assertFalse(dq_dimensions.Validity(10.0, 100.0, 20.0))
        self.assertFalse(dq_dimensions.Validity(50.0, 20.0, 10.0))

    def test_Frequency(self):
        """Testing Frequency() funciton in dq_dimensions.py that takes in current and previous arguments(datetime) and determines if the time delta between them is within the expected frequency
        passed as the third argument(float)."""
        # Ensuring Frequency() throws an Exception when an argument passed is not of type datetime.
        self.assertRaises(Exception, dq_dimensions.Frequency, 'date', self.previous, 1.1)
        self.assertRaises(Exception, dq_dimensions.Frequency, self.current, 'date', 1.1)
        self.assertRaises(Exception, dq_dimensions.Frequency, 'date', 'time', 1.1)
        # Ensuring Frequency() throws an Exception when the datetime passed as currentTime(cT) is earlier than the datetime passed as previousTime(pT)
        self.assertRaises(Exception, dq_dimensions.Frequency, self.previous, self.current)
        # Ensuring Frequency() throws an Exception when the "tol" argument is not a float value.
        self.assertRaises(Exception, dq_dimensions.Frequency, self.current, self.previous, '1')
        self.assertRaises(Exception, dq_dimensions.Frequency, self.current, self.previous, 1)
        self.assertRaises(Exception, dq_dimensions.Frequency, self.current, self.previous, True)
        # Ensuring Frequency() returns true when the timedelta between current and previous is within the expected frequency.
        self.assertTrue(dq_dimensions.Frequency(self.current, self.previous, 1.1))
        # Ensuring Frequency() returns false when the timedelta between current and previous is greater than of the expected frequency.
        self.assertFalse(dq_dimensions.Frequency(self.current, self.badprev, 1.1))
        # Ensuring Frequency() returns false in a 1st sample/row case.
        self.assertFalse(dq_dimensions.Frequency(self.current, None, 1.1))

    def test_Completeness(self):
        """Testing Completeness() funciton in dq_dimensions.py that takes in an array of all curves' frequency values for the current log."""
        # Ensuring Completeness() throws an Exception when the argument passed is not an array.
        self.assertRaises(Exception, dq_dimensions.Completeness, True)
        self.assertRaises(Exception, dq_dimensions.Completeness, 21.5)
        # Ensuring Completeness() thorws an Exception when any of the values in the array passed in are not boolean values.
        self.assertRaises(Exception, dq_dimensions.Completeness, )
        # Ensuring Completeness() returns true when all of the values in the array passed in are true.
        good = [True,True, True]
        self.assertTrue(dq_dimensions.Completeness(good))
        # Ensuring Completeness() returns false when any of the values in the array passed in are false.
        bad = [True, True, True, False]
        self.assertFalse(dq_dimensions.Completeness(bad))

    def test_Uniqueness(self):
        """Testing Uniqueness() function in dq_dimensions.py that takes in current and previous(None in 1st sample case) arguments(float) and determines if
        the arguments are unique values."""
        # Ensuring Uniqueness() throws an Exception when the arguments passed are not both floats.
        self.assertRaises(Exception, dq_dimensions.Uniqueness, '12.5', '13.2')
        self.assertRaises(Exception, dq_dimensions.Uniqueness, 12, 13)
        self.assertRaises(Exception, dq_dimensions.Uniqueness, True, False)
        self.assertRaises(Exception, dq_dimensions.Uniqueness, 12.5, 13)
        self.assertRaises(Exception, dq_dimensions.Uniqueness, 12, None)
        # Ensuring Uniqueness() returns true in a 1st sample/row case, "curr" should be float and "prev" should be None
        self.assertTrue(dq_dimensions.Uniqueness(12.5))
        # Ensuring Uniqueness() returns true when curr != prev
        self.assertTrue(dq_dimensions.Uniqueness(12.5, 13.0))
        # Ensuring Uniqueness() returns false if the arguments passed are equal
        self.assertFalse(dq_dimensions.Uniqueness(12.5, 12.5))

    def test_Consistency(self):
        """Tetsing Consistency() function in dq_dimensions.py that takes in curve values from differnet logs at the same index and compares them."""
        # Ensuring Consistency() throws an Exception when the arguments passed are not both numerical values.
        self.assertRaises(Exception, dq_dimensions.Consistency, True, "invalid")
        # Ensuring Consistency() returns true/good when the values passed as arugments are equal 
        self.assertTrue(dq_dimensions.Consistency(12.5, 12.5))
        self.assertTrue(dq_dimensions.Consistency(9555.0, 9555.0))
        # Ensuring Consistency() returns false/bad when the values passed as arguments are not equal.
        self.assertFalse(dq_dimensions.Consistency(12.5, 13.0))

    def test_Accuracy(self):
        """Testing Accuracy() funciton in dq_dimensions that takes in two curve values for a row/sample and ensures their difference is within a specified tolerance."""
        # Ensuring Accuracy() throws an Exception when any of the arguments passed are not numerical values.
        self.assertRaises(Exception, dq_dimensions.Accuracy, self.test, 2.4, 3.2)
        self.assertRaises(Exception, dq_dimensions.Accuracy, 'not a number', '5.6')
        # Ensuring Accuracy() throws an Exception when the tolerance argument passed is not a numerical value
        self.assertRaises(Exception, dq_dimensions.Accuracy, 2.5, 2.5, 'invalid')
        # Ensuring Accuracy() returns true when the difference between the two curve values are 0 and no tolerance is passed.
        self.assertTrue(dq_dimensions.Accuracy(2, 2))
        # Ensuring Accuracy() returns true when the difference between the two curve values is within the specified tolerance.
        self.assertTrue(dq_dimensions.Accuracy(3, 2, 1.2))
        # Ensuring Accuracy() returns false when the difference between the two curve values is not equal and no tolerance is passed.
        self.assertFalse(dq_dimensions.Accuracy(2, 3))
        # Ensuring Accuracy() returns false when the difference between the two curve values is not within the specified tolerance.
        self.assertFalse(dq_dimensions.Accuracy(4, 2, 1.5))
        
    # Testing Rig Status Check Functions

    def testcheckStationary(self):
        """Testing checkStationary Function in dq_dimensions that takes in a sDomain dict (can be copied from dq.dimensions) and performs a stationary check by checking the values and thresholds of BitDepth, RPM, SPP, Hookload, and BlockPosition for the current row."""
        # Ensuring checkStationary() throws an Exception when the argument passed is not a dictionary.
        self.assertRaises(Exception, dq_dimensions.checkStationary, 2.5)
        self.assertRaises(Exception, dq_dimensions.checkStationary, self.test)
        self.assertRaises(Exception, dq_dimensions.checkStationary, True)
        self.assertRaises(Exception, dq_dimensions.checkStationary, 'dict')
        # Ensuring checkStationary() throws an Excception when the dictionary passed is not an instance/copy of the sampleDomain dictionary from dq_dimensions.
        self.assertRaises(Exception, dq_dimensions.checkStationary, self.baddict)
        # Ensuring checkStationary() returns True when passed an sDomain that satisfies the stationary rule.
        self.assertTrue(dq_dimensions.checkStationary(self.stationary))
        # Ensuring checkStationary() returns False if any of the required values are included in the dictionary but empty.
        self.assertFalse(dq_dimensions.checkStationary(self.empty))
        # Ensuring checkStationary() returns False if any curve value breaks its threshold rule.
        self.empty['BitDepth']['curr'] = 400
        self.assertFalse(dq_dimensions.checkStationary(self.empty))

    def testcheckSurface(self):
        """Testing checkSurface Function in dq_dimensions that takes in a sDomain dict (can be copied from dqdimensions) and performs a surface check by checking the value and threshold of the bitdepth curve for the row."""
        # Ensuring checkSurface() throws an Exception when the argument passed is not a dictionary.
        self.assertRaises(Exception, dq_dimensions.checkSurface, 2.5)
        self.assertRaises(Exception, dq_dimensions.checkSurface, self.test)
        self.assertRaises(Exception, dq_dimensions.checkSurface, True)
        self.assertRaises(Exception, dq_dimensions.checkSurface, 'dict')
        # Ensuring checkSurface() throws an Exception when the dictionary passed is not an instance/copy of the sampleDomains dictionary from dq_dimensions.
        self.assertRaises(Exception, dq_dimensions.checkSurface, self.baddict)
        # Ensuring checkSurface() returns True when passed an sDomain that satisfies the surface rule.
        self.assertTrue(dq_dimensions.checkSurface(self.surface))
        # Ensuring checkSurface() returns False if BitDepth value or threshold fields are empty.
        self.assertFalse(dq_dimensions.checkSurface(self.empty))
        # Ensruing checkSurface() returns False if the sDomain does not pass the surface rule.
        self.empty['BitDepth']['curr'] = 400
        self.assertFalse(dq_dimensions.checkSurface(self.empty))
    # Testing Score Calculation Functions

    def testdimScore(self):
        """Testing dimScore() Function in dq_dimensions that takes in a dimension column as an array and produces a raw score using the following formula: goodrows/totalrows * 100."""
        # Ensuring dimScore() throws an Exception when passed anything that is not a list/array.
        self.assertRaises(Exception, dq_dimensions.dimScore, True)
        self.assertRaises(Exception, dq_dimensions.dimScore, 12.3)
        self.assertRaises(Exception, dq_dimensions.dimScore, 'arr')
        # Ensuring dimScore() throws an Exception when any of the values in the list/array passed are not booleans or None(Null).
        badtest = [True, False, False, True, 'None']
        self.assertRaises(Exception, dq_dimensions.dimScore, badtest)
        # Ensuring dimScore() returns expected values following the formula: goodrows/totalrows * 100 
        goodtest = [True, True, False, False, False, True, None, True, True, True]
        self.assertEqual(dq_dimensions.dimScore(goodtest), 60)

    def testOverallDim(self):
        """Testing OverallDim() Funciton in dq_dimensions that takes in a list containing all curve scores for one dimension and returns the Overall Dimension Score."""
        # Ensuring OverallDim() throws an Exception when passed anything that is not a list.
        self.assertRaises(Exception, dq_dimensions.OverallDim, 'list')
        self.assertRaises(Exception, dq_dimensions.OverallDim, 98.5)
        # Ensuring OverallDim() thorws an Exception when passed a list with any non-numerical contents.
        bad = [99.6, None, 99, False, 'not a num']
        self.assertRaises(Exception, dq_dimensions.OverallDim, bad)

    def testcalcWeight(self):
        """Testing calcWeight() Function in dq_dimensions that takes in a dimension score and a weight value and returns the weighted score."""
        # Ensuring calcWeight() throws an Exception when passed anything that is non-numerical.
        bad = [12, False, 12.3]
        self.assertRaises(Exception, dq_dimensions.calcWeight, 'False', 12)
        self.assertRaises(Exception, dq_dimensions.calcWeight, bad, 12.5)
        # Ensuring calcWeight() throws an Exception when weight > 100
        self.assertRaises(Exception, dq_dimensions.calcWeight, 12.5, 101)
        # Ensuring calcWeight() returns expected output
        self.assertEqual(dq_dimensions.calcWeight(93, 15), 13.95)
        self.assertEqual(dq_dimensions.calcWeight(26, 5), 1.3)

    def testOverallDQ(self):
        """Testing OverallDQ() Function in dq_dimensions that takes in a list containing weighted dimension scores of a dataset and returns the Overall DQ Score of said dataset"""
        # Ensuring OverallDQ() throws an Exception when passed an argument that is not a list.
        self.assertRaises(Exception, dq_dimensions.OverallDQ, 12.5)
        self.assertRaises(Exception, dq_dimensions.OverallDQ, False)
        self.assertRaises(Exception, dq_dimensions.OverallDQ, 'Not a list')
        # Ensuring OverallDQ() throws an Exception when any of the contents within the list passed are non-numerical.
        bad = [99.6, None, 99, False, 'not a num']
        self.assertRaises(Exception, dq_dimensions.OverallDQ, bad)
        # Ensuring OverallDQ() throws an Exception when the sum of the data in the list passed is > 100.
        greater = [20, 25, 25, 25, 20]
        self.assertRaises(Exception, dq_dimensions.OverallDQ, greater)
        # Ensuring OverallDQ returns Expected output.
        testset = [15, 25.6, 12.45]
        self.assertEqual(dq_dimensions.OverallDQ(testset), 53.05)

    # Testing Runner Functions

    def test_fill_dataframe(self):
        """Testing fill_dataframe() funciton in dq_runner.py that fills a dataframe with data from a .csv file."""
        # Ensuring fill_dataframe() throws an exception when passed a non-valid key-value.
        self.assertRaises(Exception, dq_runner.fill_dataframe, 'notvalid')
        # Testing passing in an empty and null string ensuring an exception is thrown.
        self.assertRaises(Exception, dq_runner.fill_dataframe)
        self.assertRaises(Exception, dq_runner.fill_dataframe, '')
        # Ensruing fill_dataframe() throws an exception when passed an empty csv file.
        self.assertRaises(Exception, dq_runner.fill_dataframe, 'input', True)
        # Ensuring fill_dataframe() throws an exception when the configured file names do not end in .csv
        self.assertRaises(Exception, dq_runner.fill_dataframe, 'check', True)
        # Ensuring fill_dataframe() returns a pandas dataframe instance when valid key-values are passed ("input" and "check")
        self.assertIsInstance(dq_runner.fill_dataframe('input'), pd.DataFrame)
        self.assertIsInstance(dq_runner.fill_dataframe('check'), pd.DataFrame)

    def test_get_Configs(self):
        """Testing get_Configs() function in dq_runner.py that retrieves type of configuration requested by user with a string key value (ie. "curve")."""
        # Ensuring get_Configs() throws an exception when the argument passed is not a string.
        self.assertRaises(Exception, dq_runner.get_Configs, 12)
        self.assertRaises(Exception, dq_runner.get_Configs, True)
        # Ensruing get_Configs() throws an exception when passed an invalid request.
        self.assertRaises(Exception, dq_runner.get_Configs, 'blah')
        # Ensuring get_Configs() throws an exception when a requested configuration is missing config data
        self.assertRaises(Exception, dq_runner.get_Configs, 'accuracy', True)
        # Ensuring get_Configs() returns a configuration field as a dictionary.
        self.assertIsInstance(dq_runner.get_Configs('curve', True), dict)

    def testtimeStr(self):
        """Testing timeStr() funciton in dq_runner.py that takes in a string time value and returns it as a datetime."""
        # Ensuring timeStr() throws an Exception when passed an argument that is not a string.
        self.assertRaises(Exception, dq_runner.timeStr, False)
        self.assertRaises(Exception, dq_runner.timeStr, self.test)
        self.assertRaises(Exception, dq_runner, self.current)
        # Ensuring timeStr() returns a datetime value when passed a string
        self.assertIsInstance(dq_runner.timeStr('2020-03-08T19:00:31.9050000Z'), datetime)

    def testcreateDimensions(self):
        """"""

    def testcreateSDomains(self):
        """Testing createSDomains() funciton in dq_runner.py that takes in a pandas dataframe loaded with input .csv data and fills a premade sampleDomain dictionary for each row in the dataframe by using the sampleDomains() function."""
        # Ensuring createSDomains() throws an Exception when passed an argument that is not a pandas dataframe()
        self.assertRaises(Exception, dq_runner.createSDomains, self.test)
        # Ensruing createSDomains() returns a dicitonary.
        self.assertIsInstance(dq_runner.createSDomains(self.testinput, True), dict)

    def testfill_sampleDomain(self):
        """Testing fill_sampleDomain() function in dq_runner.py that takes in 1(first row scenario) or 2 pandas series of row data (current and previous) and fills in a sampleDomain dictionary template from dq_dimensions for the current row passed in."""
        # Ensuring sampleDomain() throws an Exception when passed arguments that are not pandas series.
        self.assertRaises(Exception, dq_runner.fill_sampleDomain, self.testinput, self.surface)
        self.assertRaises(Exception, dq_runner.fill_sampleDomain, self.testinput)
        # Ensuring sampleDomain() returns a sDomain dictionary
        self.assertEqual(dq_runner.fill_sampleDomain(self.testinput.loc[5]).keys(), dq_dimensions.sampleDomain.keys())
    
    def testinsertDims(self):
        """Testing insertDims() function in dq_runner.py that inserts/formats the calculated dimension columns into the input data."""
        val = [True for i in range(98)]
        dim = {'Curve': 'BPOS', 'Validity_': val}
        check = self.testinput
        # Ensuring insertDims() throws an Exception when passed unexpected argument types.
        self.assertRaises(Exception, dq_runner.insertDims, self.testinput, 'not an int', dim)
        self.assertRaises(Exception, dq_runner.insertDims, self.surface, 2, dim)
        self.assertRaises(Exception, dq_runner.insertDims, self.testinput, 2, 'not a dict')
        # Ensuring insertDims() inserted/formatted the dimension column (passed in as a dictionary) correctly.
        dq_runner.insertDims(check, 2, dim)
        self.assertIn('Validity_BPOS', check.columns)
    
    def testaggScores(self):
        """Testing aggScores() funciton in dq_runner.py that calculates and records the Dimension scores for each Type of aggregation (specified by user when called)."""
        # Ensuring aggScores() throws an Exception when passed unexpected argument types.
        self.assertRaises(Exception, dq_runner.aggScores, self.dimdata, 2.5) 
        self.assertRaises(Exception, dq_runner.aggScores, self.surface, 'hourly')
        # Ensruing aggScores() throws an Exception when the requested aggType is not recognized.
        self.assertRaises(Exception, dq_runner.aggScores, self.dimdata, 'notagg')
        # Ensuring aggScores() adds a column of scores for each hour of data. (24 Columns Expected.)
        hourly = dq_runner.aggScores(self.dimdata, 'hourly')
        self.assertEqual(len(hourly.columns), 24)
        # Ensuring aggScores() adds a column of scores for each day of data.
        daily = dq_runner.aggScores(self.dimdata, 'daily')
        self.assertEqual(len(daily.columns), 1)

    def testcalcScores(self):
        """Testing calcScores() function in dq_runner.py that calculates and returns a pandas series containing the dimension scores for each curve in the dataframe passed in as an argument."""
        # Ensuring calcScores() throws an Exception when passed an argument that is not a pandas dataframe.
        self.assertRaises(Exception, dq_runner.calcScores, self.surface)
        self.assertRaises(Exception, dq_runner.calcScores, self.test)
        # Ensuring calcScores() returns a pandas series
        self.assertIsInstance(dq_runner.calcScores(self.dimdata), pd.Series)

    def testaggOverall(self):
        """Testing aggOverall() function in dq_runner.py that calculates/formats the aggregation overall scores by ustilizing the createOverall() function for each hour/day of data in the input dataframe."""
        # Ensuring aggOverall() throws an Exception when passed an argument that is not a pandas dataframe.
        self.assertRaises(Exception, dq_runner.aggOverall, self.surface)
        # Ensuring aggOverall() correctly formats its output.
        headers = ['Validity', 'Frequency', 'Consistency', 'Completeness', 'Uniqueness', 'Accuracy', 'Overall Score']
        check = dq_runner.aggOverall(self.hrscores)
        for i in headers:
            self.assertIn(i, check.columns)
        self.assertIn('Weightage (%)', check.index)
        # Ensruing the overall scores for every hour is set, expecting 25 rows(24 hr rows, 1 weightage row).
        self.assertEqual(len(check.index), 25)
        # Ensruing aggOverall returns a pandas dataframe
        self.assertIsInstance(check, pd.DataFrame)

    def testcreateOverall(self):
        """Testing the createOverall() function in dq_runner.py that calculates/formats the overall scores of the pandas series passed."""
        # Ensuring createOverall() throws an Exception when passed an argument that is not a pandas series.
        self.assertRaises(Exception, dq_runner.createOverall, self.dimdata)
        self.assertRaises(Exception, dq_runner.createOverall, self.surface)
        # Ensuring createOverall() correctly formats its output.
        headers = ['Validity', 'Frequency', 'Consistency', 'Completeness', 'Uniqueness', 'Accuracy', 'Overall Score']
        check = dq_runner.createOverall(dq_runner.calcScores(self.dimdata))
        for i in headers:
            self.assertIn(i, check.columns)
        self.assertIn('Score (%)', check.index)
        self.assertIn('Weightage (%)', check.index)
        # Ensuring createOverall() returns a pandas dataframe
        self.assertIsInstance(check, pd.DataFrame)

    def testoverallFormat(self):
        """Testing the overallFormat() void function in dq_runner.py that aids createOverall() in formatting its output."""
        test = pd.DataFrame()
        arr = [95.2, 93.5, 94.2]
        # Ensuring overallFormat() throws an Exception when any of the arguments passed are not of their expected type.
        self.assertRaises(Exception, dq_runner.overallFormat, test, arr, False)
        self.assertRaises(Exception, dq_runner.overallFormat, self.surface, arr, 'Validity')
        self.assertRaises(Exception, dq_runner.overallFormat, test, 'not a list', 'Validity')
        # Ensuring overallFormat() correctly formats the dataframe passed.
        dq_runner.overallFormat(test, arr, 'Validity')
        self.assertIn('Validity', test.columns)
        self.assertIn('Score (%)', test.index)
        self.assertIn('Weightage (%)', test.index)

    def testcalcOverallDQ(self):
        """Testing the calcOverallDQ() void function in dq_runner.py that calculates the Overall DQ score for a dataset by using the calcWeight and OverallDQ function in the dq_dimensions lib."""
        # Ensuring calcOverallDQ() throws an Exception if the arguments passed are not of their expected types.
        self.assertRaises(Exception, dq_runner.calcOverallDQ, self.surface)
        self.assertRaises(Exception, dq_runner.calcOverallDQ, self.overall, 'not a bool', 'correct')
        self.assertRaises(Exception, dq_runner.calcOverallDQ, self.overall, True, False)
        # Ensuring calcOverallDQ() correctly calculates the overall DQ Score.
        dq_runner.calcOverallDQ(self.overall, testing=True)
        self.assertEqual(self.overall.loc['Score (%)']['Overall Score'], 97.76)

if __name__ == "__main__":
    unittest.main()