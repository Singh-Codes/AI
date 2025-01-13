"""
Test cases for example.py using unittest
"""
import unittest
import sys
from pathlib import Path

# Add input_files directory to Python path
sys.path.append(str(Path(__file__).parent.parent / 'input_files'))

from example import *


class TestDataProcessing(unittest.TestCase):
    """Test cases for data processing functions."""

    def test_calculate_average_basic(self):
        """Test calculate_average with basic input."""
        numbers = [1, 2, 3, 4, 5]
        result = calculate_average(numbers)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, float)
        self.assertEqual(result, 3.0)

    def test_calculate_average_edge_cases(self):
        """Test calculate_average with edge cases."""
        with self.assertRaises(ZeroDivisionError):
            calculate_average([])
        
        with self.assertRaises(TypeError):
            calculate_average(None)
        
        # Test with single value
        self.assertEqual(calculate_average([5]), 5.0)
        
        # Test with negative numbers
        self.assertEqual(calculate_average([-1, -2, -3]), -2.0)
        
        # Test with floating point numbers
        self.assertAlmostEqual(calculate_average([1.5, 2.5, 3.5]), 2.5)

    def test_find_max_value_basic(self):
        """Test find_max_value with basic input."""
        data_list = [1, 2, 3, 4, 5]
        result = find_max_value(data_list)
        self.assertEqual(result, 5)

    def test_find_max_value_edge_cases(self):
        """Test find_max_value with edge cases."""
        # Test empty list
        self.assertIsNone(find_max_value([]))
        
        # Test None input
        self.assertIsNone(find_max_value(None))
        
        # Test single value
        self.assertEqual(find_max_value([42]), 42)
        
        # Test negative numbers
        self.assertEqual(find_max_value([-1, -2, -3]), -1)
        
        # Test mixed numbers
        self.assertEqual(find_max_value([-10, 0, 10]), 10)

    def test_process_numbers_basic(self):
        """Test process_numbers with basic input."""
        processor = DataProcessor()
        numbers = [1, 2, 3, 4, 5]
        result = processor.process_numbers(numbers)
        
        self.assertIsNotNone(result)
        self.assertIsInstance(result, dict)
        self.assertIn('average', result)
        self.assertIn('maximum', result)
        self.assertEqual(result['average'], 3.0)
        self.assertEqual(result['maximum'], 5)

    def test_process_numbers_edge_cases(self):
        """Test process_numbers with edge cases."""
        processor = DataProcessor()
        
        # Test empty list
        with self.assertRaises(ZeroDivisionError):
            processor.process_numbers([])
        
        # Test None input
        with self.assertRaises(TypeError):
            processor.process_numbers(None)
        
        # Test single value
        result = processor.process_numbers([42])
        self.assertEqual(result['average'], 42.0)
        self.assertEqual(result['maximum'], 42)
        
        # Test negative numbers
        result = processor.process_numbers([-1, -2, -3])
        self.assertEqual(result['average'], -2.0)
        self.assertEqual(result['maximum'], -1)

    def test_main(self):
        """Test main function."""
        try:
            main()
        except Exception as e:
            self.fail(f"main() raised {type(e).__name__} unexpectedly!")


if __name__ == '__main__':
    unittest.main()
