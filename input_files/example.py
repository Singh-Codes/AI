"""
Example module demonstrating basic data processing functions.
"""
from typing import List, Dict, Optional, Union, Any


def calculate_average(numbers: Optional[List[float]]) -> float:
    """
    Calculate the average of a list of numbers.
    
    Args:
        numbers: List of numbers to average
        
    Returns:
        float: Average of the numbers
        
    Raises:
        TypeError: If numbers is None
        ZeroDivisionError: If numbers is empty
    """
    if numbers is None:
        raise TypeError("Input cannot be None")
    if not numbers:
        raise ZeroDivisionError("Cannot calculate average of empty list")
    return sum(numbers) / len(numbers)


def find_max_value(data_list: Optional[List[float]]) -> Optional[float]:
    """
    Find the maximum value in a list.
    
    Args:
        data_list: List of numbers to search
        
    Returns:
        Optional[float]: Maximum value, or None if list is empty or None
    """
    if not data_list:
        return None
    return max(data_list)


class DataProcessor:
    """Class to process numerical data."""
    
    def process_numbers(self, numbers: List[float]) -> Dict[str, float]:
        """
        Process a list of numbers and return statistics.
        
        Args:
            numbers: List of numbers to process
            
        Returns:
            Dict containing average and maximum values
            
        Raises:
            TypeError: If numbers is None
            ZeroDivisionError: If numbers is empty
        """
        avg = calculate_average(numbers)
        max_val = find_max_value(numbers)
        return {
            'average': avg,
            'maximum': max_val
        }


def main() -> None:
    """Main function to demonstrate usage."""
    sample_data = [1, 2, 3, 4, 5]
    processor = DataProcessor()
    results = processor.process_numbers(sample_data)
    print(f"Results: {results}")


if __name__ == "__main__":
    main()
