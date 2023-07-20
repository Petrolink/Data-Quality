import unittest
import OpenS
import math
from datetime import datetime, timedelta

class TestOpenS(unittest.TestCase):
    def setUp(self):
        """Set Up function for Unittesting."""
        self.goodrow = OpenS.sample()
        self.goodrow.cT = datetime.fromisoformat('2020-03-08T19:00:32.9150000Z')
        self.goodrow.pT = datetime.fromisoformat('2020-03-08T19:00:31.9050000Z')
        self.badrow = OpenS.sample()
        self.badrow.pT = datetime.fromisoformat('2020-03-08T19:00:30.8920000Z')

    def test_Valididty(self):
        """Testing Validity() function in OpenS.py that takes in a sample instance and determines the validity of requested curves for that sample by ensuring the curve values are not null and are within the set sensor limits."""

    def test_Frequency(self):
        """Testing Frequency() funciton in OpenS.py that takes in current and previous datetime values and determines if the time delta between them is within the expected frequency
        configured by user."""
        # Ensuring Frequency() throws an Exception when an argument passed is not of type datetime.
        self.assertRaises(Exception, OpenS.Frequency, 'date', self.goodrow.pT)
        self.assertRaises(Exception, OpenS.Frequency, self.goodrow.cT, 'date')
        self.assertRaises(Exception, OpenS.Frequency, 'date', 'time')
        # Ensuring Frequency() throws an Exception when the datetime passed as currentTime(cT) is earlier than the datetime passed as previousTime(pT)
        self.assertRaises(Exception, OpenS.Frequency, self.goodrow.pT, self.goodrow.cT)
        # Ensuring Frequency() returns true when the timedelta between current and previous is within the expected frequency.
        self.assertTrue(OpenS.Frequency(self.goodrow.cT, self.goodrow.pT))
        # Ensuring Frequency() returns false when the timedelta between current and previous is greater than of the expected frequency.
        self.assertFalse(OpenS.Frequency(self.goodrow.cT, self.badrow.pT))

    def test_Completeness(self):
        """Testing Completeness function in OpenS.py that takes in a sample instance and determines the samples completeness by making use of the samples frequency."""
        # Setting up a sample with a good frequency for testing.
        self.goodrow.frequency = OpenS.Frequency(self.goodrow.cT, self.goodrow.pT)
        # Ensuring Completeness() throws an Exception when the samples frequency has not been set.
        self.assertRaises(Exception, OpenS.Completeness, self.badrow)
        # Ensuring Completeness() throws an Exception when the argument passed is not an instance of the "sample" class.
        self.assertRaises(Exception, OpenS.Completeness, 'Not a sample')
        # Setting up a sample with a bad frequency for testing
        self.badrow.frequency = OpenS.Frequency(self.goodrow.cT, self.badrow.pT)
        # Ensuring Completeness() returns False if the frequency of the sample passed is false/bad.
        self.assertFalse(OpenS.Completeness(self.badrow))
        # Ensuring Completeness() returns True if the frequency of the sample passed is true/good.
        self.assertTrue(OpenS.Completeness(self.goodrow))

if __name__ == "__main__":
    unittest.main()