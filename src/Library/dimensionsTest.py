import unittest
from datetime import datetime
import dq_dimensions

class Testdq_dimensions(unittest.TestCase):
    def setUp(self):
        self.current = datetime.fromisoformat('2020-03-08T19:00:32.9150000Z')
        self.previous = datetime.fromisoformat('2020-03-08T19:00:31.9050000Z')
        self.badprev = datetime.fromisoformat('2020-03-08T19:00:30.8920000Z')
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
        
    # Testing Dimension Functions 

    def test_validity(self):
        """Testing validity() function in dq_dimensions.py that takes in a curve value argument(float) and determines if it is within the upper and lower limit arguments passed by user."""
        # Ensuring validity() throws an Exception when the arguments passed are not all float values.
        self.assertRaises(Exception, dq_dimensions.validity, '1.0', 1.0, 1.0)
        self.assertRaises(Exception, dq_dimensions.validity, 1.0, 1, 1.0)
        self.assertRaises(Exception, dq_dimensions.validity, 1.0, 1.0, True)
        # Ensuring validity() throws an Exception when upper limit <= lower limit.
        self.assertRaises(Exception, dq_dimensions.validity, 100, 1, 150)
        self.assertRaises(Exception, dq_dimensions.validity, 100, 150, 150)
        # Ensuring validity() returns true when lowLimit <= cValue <= upperLimit.
        self.assertTrue(dq_dimensions.validity(10.0, 50.0, 1.0))
        # Ensuring validity() returns false when cValue < Lower Limit or cValue > UpperLimit
        self.assertFalse(dq_dimensions.validity(10.0, 100.0, 20.0))
        self.assertFalse(dq_dimensions.validity(50.0, 20.0, 10.0))

    def test_frequency(self):
        """Testing frequency() funciton in dq_dimensions.py that takes in current and previous arguments(datetime) and determines if the time delta between them is within the expected frequency
        passed as the third argument(float)."""
        # Ensuring frequency() throws an Exception when an argument passed is not of type datetime.
        self.assertRaises(Exception, dq_dimensions.frequency, 'date', self.previous, 1.1)
        self.assertRaises(Exception, dq_dimensions.frequency, self.current, 'date', 1.1)
        self.assertRaises(Exception, dq_dimensions.frequency, 'date', 'time', 1.1)
        # Ensuring frequency() throws an Exception when the datetime passed as currentTime(cT) is earlier than the datetime passed as previousTime(pT)
        self.assertRaises(Exception, dq_dimensions.frequency, self.previous, self.current)
        # Ensuring frequency() throws an Exception when the "tol" argument is not a float value.
        self.assertRaises(Exception, dq_dimensions.frequency, self.current, self.previous, '1')
        self.assertRaises(Exception, dq_dimensions.frequency, self.current, self.previous, 1)
        self.assertRaises(Exception, dq_dimensions.frequency, self.current, self.previous, True)
        # Ensuring frequency() returns true when the timedelta between current and previous is within the expected frequency.
        self.assertTrue(dq_dimensions.frequency(self.current, self.previous, 1.1))
        # Ensuring frequency() returns false when the timedelta between current and previous is greater than of the expected frequency.
        self.assertFalse(dq_dimensions.frequency(self.current, self.badprev, 1.1))
        # Ensuring frequency() returns false in a 1st sample/row case.
        self.assertFalse(dq_dimensions.frequency(self.current, None, 1.1))

    def test_completeness(self):
        """Testing completeness() funciton in dq_dimensions.py that takes in an array of all curves' frequency values for the current log."""
        # Ensuring completeness() throws an Exception when the argument passed is not an array.
        self.assertRaises(Exception, dq_dimensions.completeness, True)
        self.assertRaises(Exception, dq_dimensions.completeness, 21.5)
        # Ensuring completeness() thorws an Exception when any of the values in the array passed in are not boolean values.
        self.assertRaises(Exception, dq_dimensions.completeness, )
        # Ensuring completeness() returns true when all of the values in the array passed in are true.
        good = [True,True, True]
        self.assertTrue(dq_dimensions.completeness(good))
        # Ensuring completeness() returns false when any of the values in the array passed in are false.
        bad = [True, True, True, False]
        self.assertFalse(dq_dimensions.completeness(bad))

    def test_uniqueness(self):
        """Testing uniqueness() function in dq_dimensions.py that takes in current and previous(None in 1st sample case) arguments(float) and determines if
        the arguments are unique values."""
        # Testing FUNCTIONALITY WITH RIG STATUSES
        # Ensuring uniqueness() throws an Exception when any of the arguments passed are not of their expected type.
        self.assertRaises(Exception, dq_dimensions.uniqueness, 12.5, 12.5, 'NOT A BOOL', 'NOT A BOOL')
        self.assertRaises(Exception, dq_dimensions.uniqueness, 12.5, 12.5, 'NOT A BOOL')
        self.assertRaises(Exception, dq_dimensions.uniqueness, 12.5, 0.0, 12.5, False)
        self.assertRaises(Exception, dq_dimensions.uniqueness, 12.5, 0.0, False, 124)
        self.assertRaises(Exception, dq_dimensions.uniqueness, 12.5, None, 'NOT A BOOL')
        self.assertRaises(Exception, dq_dimensions.uniqueness, 12.5, None, 12.5)
        self.assertRaises(Exception, dq_dimensions.uniqueness, 'Not a num', 12.5, False)
        # Ensuring uniqueness() returns true if the stationary or surface rig status checks are true.
        self.assertTrue(dq_dimensions.uniqueness(12.5, None, dq_dimensions.check_stationary(self.stationary)))
        self.assertTrue(dq_dimensions.uniqueness(12.5, 12.5, False, dq_dimensions.check_surface(self.surface)))
        # Ensuring uniqueness() returns true when vals are unique and rig statuses are false.
        self.assertTrue(dq_dimensions.uniqueness(12.5, 13.0, False, False))
        #Ensuring uniqueness() returns fasle when vals are equal and rig statuses are false.
        self.assertFalse(dq_dimensions.uniqueness(0.0, 0.0, False, False))


        # TESTING FUNCTIONALITY WITHOUT RIG STATUSES 
        # # Ensuring uniqueness() throws an Exception when the arguments passed are not both floats.
        self.assertRaises(Exception, dq_dimensions.uniqueness, '12.5', '13.2')
        self.assertRaises(Exception, dq_dimensions.uniqueness, 12, 13)
        self.assertRaises(Exception, dq_dimensions.uniqueness, True, False)
        self.assertRaises(Exception, dq_dimensions.uniqueness, 12.5, 13)
        self.assertRaises(Exception, dq_dimensions.uniqueness, 12, None)       
        # Ensuring uniqueness() returns true in a 1st sample/row case, "curr" should be float and "prev" should be None
        self.assertTrue(dq_dimensions.uniqueness(12.5))
        # Ensuring uniqueness() returns true when curr != prev
        self.assertTrue(dq_dimensions.uniqueness(12.5, 13.0))
        # Ensuring uniqueness() returns false if the arguments passed are equal
        self.assertFalse(dq_dimensions.uniqueness(12.5, 12.5))

    def test_consistency(self):
        """Tetsing consistency() function in dq_dimensions.py that takes in curve values from differnet logs at the same index and compares them."""
        # Ensuring consistency() throws an Exception when the arguments passed are not both numerical values.
        self.assertRaises(Exception, dq_dimensions.consistency, True, "invalid")
        # Ensuring consistency() returns true/good when the values passed as arugments are equal 
        self.assertTrue(dq_dimensions.consistency(12.5, 12.5))
        self.assertTrue(dq_dimensions.consistency(9555.0, 9555.0))
        # Ensuring consistency() returns false/bad when the values passed as arguments are not equal.
        self.assertFalse(dq_dimensions.consistency(12.5, 13.0))

    def test_accuracy(self):
        """Testing accuracy() funciton in dq_dimensions that takes in two curve values for a row/sample and ensures their difference is within a specified tolerance."""
        # Ensuring accuracy() throws an Exception when any of the arguments passed are not numerical values.
        self.assertRaises(Exception, dq_dimensions.accuracy, self.test, 2.4, 3.2)
        self.assertRaises(Exception, dq_dimensions.accuracy, 'not a number', '5.6')
        # Ensuring accuracy() throws an Exception when the tolerance argument passed is not a numerical value
        self.assertRaises(Exception, dq_dimensions.accuracy, 2.5, 2.5, 'invalid')
        # Ensuring accuracy() returns true when the difference between the two curve values are 0 and no tolerance is passed.
        self.assertTrue(dq_dimensions.accuracy(2, 2))
        # Ensuring accuracy() returns true when the difference between the two curve values is within the specified tolerance.
        self.assertTrue(dq_dimensions.accuracy(3, 2, 1.2))
        # Ensuring accuracy() returns false when the difference between the two curve values is not equal and no tolerance is passed.
        self.assertFalse(dq_dimensions.accuracy(2, 3))
        # Ensuring accuracy() returns false when the difference between the two curve values is not within the specified tolerance.
        self.assertFalse(dq_dimensions.accuracy(4, 2, 1.5))
        
    # Testing Rig Status Check Functions

    def test_check_stationary(self):
        """Testing check_stationary Function in dq_dimensions that takes in a sDomain dict (can be copied from dq.dimensions) and performs a stationary check by checking the values and thresholds of BitDepth, RPM, SPP, Hookload, and BlockPosition for the current row."""
        # Ensuring check_stationary() throws an Exception when the argument passed is not a dictionary.
        self.assertRaises(Exception, dq_dimensions.check_stationary, 2.5)
        self.assertRaises(Exception, dq_dimensions.check_stationary, self.test)
        self.assertRaises(Exception, dq_dimensions.check_stationary, True)
        self.assertRaises(Exception, dq_dimensions.check_stationary, 'dict')
        # Ensuring check_stationary() throws an Excception when the dictionary passed is not an instance/copy of the sampleDomain dictionary from dq_dimensions.
        self.assertRaises(Exception, dq_dimensions.check_stationary, self.baddict)
        # Ensuring check_stationary() returns True when passed an sDomain that satisfies the stationary rule.
        self.assertTrue(dq_dimensions.check_stationary(self.stationary))
        # Ensuring check_stationary() returns False if any of the required values are included in the dictionary but empty.
        self.assertFalse(dq_dimensions.check_stationary(self.empty))
        # Ensuring check_stationary() returns False if any curve value breaks its threshold rule.
        self.empty['BitDepth']['curr'] = 400
        self.assertFalse(dq_dimensions.check_stationary(self.empty))

    def test_check_surface(self):
        """Testing check_surface Function in dq_dimensions that takes in a sDomain dict (can be copied from dqdimensions) and performs a surface check by checking the value and threshold of the bitdepth curve for the row."""
        # Ensuring check_surface() throws an Exception when the argument passed is not a dictionary.
        self.assertRaises(Exception, dq_dimensions.check_surface, 2.5)
        self.assertRaises(Exception, dq_dimensions.check_surface, self.test)
        self.assertRaises(Exception, dq_dimensions.check_surface, True)
        self.assertRaises(Exception, dq_dimensions.check_surface, 'dict')
        # Ensuring check_surface() throws an Exception when the dictionary passed is not an instance/copy of the sampleDomains dictionary from dq_dimensions.
        self.assertRaises(Exception, dq_dimensions.check_surface, self.baddict)
        # Ensuring check_surface() returns True when passed an sDomain that satisfies the surface rule.
        self.assertTrue(dq_dimensions.check_surface(self.surface))
        # Ensuring check_surface() returns False if BitDepth value or threshold fields are empty.
        self.assertFalse(dq_dimensions.check_surface(self.empty))
        # Ensruing check_surface() returns False if the sDomain does not pass the surface rule.
        self.empty['BitDepth']['curr'] = 400
        self.assertFalse(dq_dimensions.check_surface(self.empty))

    # Testing Score Calculation Functions

    def test_dim_score(self):
        """Testing dim_score() Function in dq_dimensions that takes in a dimension column as an array and produces a raw score using the following formula: goodrows/totalrows * 100."""
        # Ensuring dim_score() throws an Exception when passed anything that is not a list/array.
        self.assertRaises(Exception, dq_dimensions.dim_score, True)
        self.assertRaises(Exception, dq_dimensions.dim_score, 12.3)
        self.assertRaises(Exception, dq_dimensions.dim_score, 'arr')
        # Ensuring dim_score() throws an Exception when any of the values in the list/array passed are not booleans or None(Null).
        badtest = [True, False, False, True, 'None']
        self.assertRaises(Exception, dq_dimensions.dim_score, badtest)
        # Ensuring dim_score() returns expected values following the formula: goodrows/totalrows * 100 
        goodtest = [True, True, False, False, False, True, None, True, True, True]
        self.assertEqual(dq_dimensions.dim_score(goodtest), 60)

    def test_overall_dim(self):
        """Testing overall_dim() Funciton in dq_dimensions that takes in a list containing all curve scores for one dimension and returns the Overall Dimension Score."""
        # Ensuring overall_dim() throws an Exception when passed anything that is not a list.
        self.assertRaises(Exception, dq_dimensions.overall_dim, 'list')
        self.assertRaises(Exception, dq_dimensions.overall_dim, 98.5)
        # Ensuring overall_dim() thorws an Exception when passed a list with any non-numerical contents.
        bad = [99.6, None, 99, False, 'not a num']
        self.assertRaises(Exception, dq_dimensions.overall_dim, bad)

    def test_calc_weight(self):
        """Testing calc_weight() Function in dq_dimensions that takes in a dimension score and a weight value and returns the weighted score."""
        # Ensuring calc_weight() throws an Exception when passed anything that is non-numerical.
        bad = [12, False, 12.3]
        self.assertRaises(Exception, dq_dimensions.calc_weight, 'False', 12)
        self.assertRaises(Exception, dq_dimensions.calc_weight, bad, 12.5)
        # Ensuring calc_weight() throws an Exception when weight > 100
        self.assertRaises(Exception, dq_dimensions.calc_weight, 12.5, 101)
        # Ensuring calc_weight() returns expected output
        self.assertEqual(dq_dimensions.calc_weight(93, 15), 13.95)
        self.assertEqual(dq_dimensions.calc_weight(26, 5), 1.3)

    def test_overall_dq(self):
        """Testing overall_dq() Function in dq_dimensions that takes in a list containing weighted dimension scores of a dataset and returns the Overall DQ Score of said dataset"""
        # Ensuring overall_dq() throws an Exception when passed an argument that is not a list.
        self.assertRaises(Exception, dq_dimensions.overall_dq, 12.5)
        self.assertRaises(Exception, dq_dimensions.overall_dq, False)
        self.assertRaises(Exception, dq_dimensions.overall_dq, 'Not a list')
        # Ensuring overall_dq() throws an Exception when any of the contents within the list passed are non-numerical.
        bad = [99.6, None, 99, False, 'not a num']
        self.assertRaises(Exception, dq_dimensions.overall_dq, bad)
        # Ensuring overall_dq() throws an Exception when the sum of the data in the list passed is > 100.
        greater = [20, 25, 25, 25, 20]
        self.assertRaises(Exception, dq_dimensions.overall_dq, greater)
        # Ensuring overall_dq returns Expected output.
        testset = [15, 25.6, 12.45]
        self.assertEqual(dq_dimensions.overall_dq(testset), 53.05)

if __name__ == "__main__":
    unittest.main()