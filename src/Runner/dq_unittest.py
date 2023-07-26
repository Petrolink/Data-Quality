import unittest
import math
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

    def test_timeStr(self):
        """Testing timeStr() function in dq_runner that takes in a timestamp string returns the timestamp as a datetime value."""
        # Ensuring timeStr() throws an Exception when the argument passed is not a string value
        self.assertRaises(Exception, dq_runner.timeStr, self.current)
        # Ensuring timeStr() returns a datetime value when passed a string with a standard ISO timestamp.
        self.assertIsInstance(dq_runner.timeStr('2020-03-08T19:00:32.9150000Z'), datetime)
        
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
        #Ensuring Consistency() throws an Exception when the arguments passed are not both numerical values.
        self.assertRaises(Exception, dq_dimensions.Consistency, True, "invalid")
        #Ensuring Consistency() returns true/good when the values passed as arugments are equal 
        self.assertTrue(dq_dimensions.Consistency(12.5, 12.5))
        self.assertTrue(dq_dimensions.Consistency(9555.0, 9555.0))
        #Ensuring Consistency() returns false/bad when the values passed as arguments are not equal.
        self.assertFalse(dq_dimensions.Consistency(12.5, 13.0))

    def test_Accuracy(self):
        """Testing Accuracy() funciton in dq_dimensions that takes in Bitdepth and Block Position values for a row/sample and ensures their difference is within a specified tolerance."""
        #Ensuring Accuracy() throws an Exception when the arguments passed are not numerical values.
        self.assertRaises(Exception, dq_dimensions.Accuracy, 3, True, "3", 12.5)
        #Ensuring Accuracy() throws an Exception when the tolerance argument passed is not a numerical value
        self.assertRaises(Exception, dq_dimensions.Accuracy, 3, 2, 5, 4, 'invalid')
        # Ensuring Accuracy() returns None when any of the paired curr/prev arguments are None or 0.0. (Handling NULL cases)
        self.assertIsNone(dq_dimensions.Accuracy(0.0, 1.2, 0.0, 1.2))
        self.assertIsNone(dq_dimensions.Accuracy(1.2, 0.0, 1.2, 0.0))
        self.assertIsNone(dq_dimensions.Accuracy(None, 1.2, None , 1.2))
        self.assertIsNone(dq_dimensions.Accuracy(1.2, None, 1.2, None))
        #Ensuring Accuracy() returns true when the differences between the two curves' values are equal and no tolerance is passed.
        self.assertTrue(dq_dimensions.Accuracy(3, 2, 5, 4))
        #Ensuring Accuracy() returns true when the differences between the two curves' values are within the specified tolerance.
        self.assertTrue(dq_dimensions.Accuracy(11, 11.06, 11.06, 11.13, 0.01))
        #Ensuring Accuracy() returns false when the differences between the two curves' values are not equal and no tolerance is passed.
        self.assertFalse(dq_dimensions.Accuracy(13, 12, 14, 12))
        #Ensuring Accuracy() returns false when the differences between the two curves'values are not within the specified tolerance.
        self.assertFalse(dq_dimensions.Accuracy(11, 11.06, 11.06, 11.15, 0.01))

    def testdimScore(self):
        """Testing dimScore() Function in dq_dimensions that takes in a dimension column as an array and produces a raw score using the following formula: goodrows/totalrows * 100."""
        #Ensuring dimScore() throws an Exception when passed anything that is not a list/array.
        self.assertRaises(Exception, dq_dimensions.dimScore, True)
        self.assertRaises(Exception, dq_dimensions.dimScore, 12.3)
        self.assertRaises(Exception, dq_dimensions.dimScore, 'arr')
        #Ensuring dimScore() throws an Exception when any of the values in the list/array passed are not booleans or None(Null).
        badtest = [True, False, False, True, 'None']
        self.assertRaises(Exception, dq_dimensions.dimScore, badtest)
        #Ensuring dimScore() returns expected values following the formula: goodrows/totalrows * 100 
        goodtest = [True, True, False, False, False, True, None, True, True, True]
        self.assertEqual(dq_dimensions.dimScore(goodtest), 60)

    def testOverallDim(self):
        """Testing OverallDim() Funciton in dq_dimensions that takes in a list containing all curve scores for one dimension and returns the Overall Dimension Score."""
        #Ensuring OverallDim() throws an Exception when passed anything that is not a list.
        self.assertRaises(Exception, dq_dimensions.OverallDim, 'list')
        self.assertRaises(Exception, dq_dimensions.OverallDim, 98.5)
        #Ensuring OverallDim() thorws an Exception when passed a list with any non-numerical contents.
        bad = [99.6, None, 99, False, 'not a num']
        self.assertRaises(Exception, dq_dimensions.OverallDim, bad)

    def testcalcWeight(self):
        """Testing calcWeight() Function in dq_dimensions that takes in a dimension score and a weight value and returns the weighted score."""
        #Ensuring calcWeight() throws an Exception when passed anything that is non-numerical.
        bad = [12, False, 12.3]
        self.assertRaises(Exception, dq_dimensions.calcWeight, 'False', 12)
        self.assertRaises(Exception, dq_dimensions.calcWeight, bad, 12.5)
        #Ensuring calcWeight() throws an Exception when weight > 100
        self.assertRaises(Exception, dq_dimensions.calcWeight, 12.5, 101)
        #Ensuring calcWeight() returns expected output
        self.assertEqual(dq_dimensions.calcWeight(93, 15), 13.95)
        self.assertEqual(dq_dimensions.calcWeight(26, 5), 1.3)

    def testOverallDQ(self):
        """Testing OverallDQ() Function in dq_dimensions that takes in a list containing weighted dimension scores of a dataset and returns the Overall DQ Score of said dataset"""
        #Ensuring OverallDQ() throws an Exception when passed an argument that is not a list.
        self.assertRaises(Exception, dq_dimensions.OverallDQ, 12.5)
        self.assertRaises(Exception, dq_dimensions.OverallDQ, False)
        self.assertRaises(Exception, dq_dimensions.OverallDQ, 'Not a list')
        #Ensuring OverallDQ() throws an Exception when any of the contents within the list passed are non-numerical.
        bad = [99.6, None, 99, False, 'not a num']
        self.assertRaises(Exception, dq_dimensions.OverallDQ, bad)
        #Ensuring OverallDQ() throws an Exception when the sum of the data in the list passed is > 100.
        greater = [20, 25, 25, 25, 20]
        self.assertRaises(Exception, dq_dimensions.OverallDQ, greater)
        #Ensuring OverallDQ returns Expected output.
        testset = [15, 25.6, 12.45]
        self.assertEqual(dq_dimensions.OverallDQ(testset), 53.05)

    def test_fill_dataframe(self):
        """Testing fill_dataframe() funciton in dq_runner.py that fills a dataframe with data from a .csv file."""
        # Testing passing in a non .csv file ensuring an exception is thrown.
        self.assertRaises(Exception, dq_runner.fill_dataframe, 'Test_Inputs\Testtype.xlsx')
        # Testing passing in a csv file with no data ensuring an exception is thrown.
        self.assertRaises(Exception, dq_runner.fill_dataframe, 'Test_Inputs\Testempty.csv')
        # Testing passing in an empty and null string ensuring an exception is thrown.
        self.assertRaises(Exception, dq_runner.fill_dataframe)
        self.assertRaises(Exception, dq_runner.fill_dataframe, '')

    def test_get_Configs(self):
        """Testing get_Configs() function in dq_runner.py that retrieves type of configuration requested by user with a string key value (ie. "curve")."""
        #Ensuring get_Configs throws an exception when the argument passed is not a string.
        self.assertRaises(Exception, dq_runner.get_Configs, 12)
        self.assertRaises(Exception, dq_runner.get_Configs, True)
        #Ensruing get_Configs throws an exception when passed an invalid request.
        self.assertRaises(Exception, dq_runner.get_Configs, 'blah')
        #TODO add expected output test
    
    #TODO add createDimensions test
    
if __name__ == "__main__":
    unittest.main()