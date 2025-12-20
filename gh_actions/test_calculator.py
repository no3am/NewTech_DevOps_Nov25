"""
Unit tests for the Calculator class.
"""

import unittest
from calculator import Calculator


class TestCalculator(unittest.TestCase):
    """Test cases for the Calculator class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.calc = Calculator()
    
    def test_add(self):
        """Test addition operation."""
        self.assertEqual(self.calc.add(5, 3), 8)
        self.assertEqual(self.calc.add(-1, 1), 0)
        self.assertEqual(self.calc.add(-5, -3), -8)
        self.assertEqual(self.calc.add(0, 0), 0)
    
    def test_subtract(self):
        """Test subtraction operation."""
        self.assertEqual(self.calc.subtract(10, 4), 6)
        self.assertEqual(self.calc.subtract(0, 5), -5)
        self.assertEqual(self.calc.subtract(-3, -3), 0)
        self.assertEqual(self.calc.subtract(100, 50), 50)
    
    def test_multiply(self):
        """Test multiplication operation."""
        self.assertEqual(self.calc.multiply(6, 7), 42)
        self.assertEqual(self.calc.multiply(-2, 3), -6)
        self.assertEqual(self.calc.multiply(0, 100), 0)
        self.assertEqual(self.calc.multiply(-4, -5), 20)
    
    def test_divide(self):
        """Test division operation."""
        self.assertEqual(self.calc.divide(20, 4), 5)
        self.assertEqual(self.calc.divide(10, 2), 5)
        self.assertEqual(self.calc.divide(-10, 2), -5)
        self.assertAlmostEqual(self.calc.divide(7, 3), 2.333333, places=5)
    
    def test_divide_by_zero(self):
        """Test that dividing by zero raises ValueError."""
        with self.assertRaises(ValueError) as context:
            self.calc.divide(10, 0)
        self.assertEqual(str(context.exception), "Cannot divide by zero")
    
    def test_power(self):
        """Test power operation."""
        self.assertEqual(self.calc.power(2, 3), 8)
        self.assertEqual(self.calc.power(5, 2), 25)
        self.assertEqual(self.calc.power(10, 0), 1)
        self.assertEqual(self.calc.power(2, -1), 0.5)
    
    def test_square_root(self):
        """Test square root operation."""
        self.assertEqual(self.calc.square_root(16), 4)
        self.assertEqual(self.calc.square_root(25), 5)
        self.assertEqual(self.calc.square_root(0), 0)
        self.assertAlmostEqual(self.calc.square_root(2), 1.414213, places=5)
    
    def test_square_root_negative(self):
        """Test that square root of negative number raises ValueError."""
        with self.assertRaises(ValueError) as context:
            self.calc.square_root(-4)
        self.assertEqual(str(context.exception), "Cannot calculate square root of negative number")


if __name__ == "__main__":
    unittest.main()
