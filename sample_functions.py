"""Sample functions for testing the test generator."""
from typing import List, Dict, Optional, Union

def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b

def divide(a: float, b: float) -> float:
    """Divide two numbers."""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

def process_list(items: List[int]) -> List[int]:
    """Process a list of integers."""
    if not items:
        raise ValueError("List cannot be empty")
    return [x * 2 for x in items]

def merge_dicts(d1: Dict[str, str], d2: Dict[str, str]) -> Dict[str, str]:
    """Merge two dictionaries."""
    if not d1 or not d2:
        raise ValueError("Dictionaries cannot be empty")
    return {**d1, **d2}

def find_max(numbers: List[float], default: Optional[float] = None) -> Optional[float]:
    """Find the maximum number in a list."""
    if not numbers:
        return default
    return max(numbers)

class Calculator:
    """Simple calculator class."""
    
    def __init__(self):
        """Initialize calculator."""
        self.history: List[float] = []
    
    def add(self, a: float, b: float) -> float:
        """Add two numbers and store in history."""
        result = a + b
        self.history.append(result)
        return result
    
    def multiply(self, a: float, b: float) -> float:
        """Multiply two numbers."""
        return a * b
    
    def get_history(self) -> List[float]:
        """Get calculation history."""
        return self.history.copy()
