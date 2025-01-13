import pytest
from hypothesis import given, settings, strategies as st, assume
import math
from typing import Any, Dict, List, Optional, Set, Tuple
from unittest.mock import Mock, patch

# Import functions under test
from sample_functions import *

@pytest.fixture
def setup_function():
    # Add any setup code here
    pass

def test_add_error():
    """Error test for add"""
    # Error test
    with pytest.raises(TypeError):
        add(**{'a': None, 'b': None})

def test_divide_error():
    """Error test for divide"""
    # Error test
    with pytest.raises(ValueError) as exc_info:
        divide(1.0, 0.0)
    assert str(exc_info.value) == "Cannot divide by zero"

def test_process_list_error():
    """Error test for process_list"""
    # Error test
    with pytest.raises(ValueError) as exc_info:
        process_list([])
    assert str(exc_info.value) == "List cannot be empty"

def test_merge_dicts_error():
    """Error test for merge_dicts"""
    # Error test
    with pytest.raises(ValueError) as exc_info:
        merge_dicts({}, {})
    assert str(exc_info.value) == "Dictionaries cannot be empty"

def test_find_max_error():
    """Error test for find_max"""
    # Error test
    result = find_max([], None)
    assert result is None

calculator = Calculator()
def test_add_error():
    """Error test for calculator.add"""
    # Error test
    with pytest.raises(TypeError):
        calculator.add(**{'a': None, 'b': None})

calculator = Calculator()
def test_multiply_error():
    """Error test for calculator.multiply"""
    # Error test
    with pytest.raises(TypeError):
        calculator.multiply(**{'a': None, 'b': None})

calculator = Calculator()
def test_add_error():
    """Error test for calculator.add"""
    # Error test
    with pytest.raises(TypeError):
        calculator.add(**{'a': None, 'b': None})

calculator = Calculator()
def test_multiply_error():
    """Error test for calculator.multiply"""
    # Error test
    with pytest.raises(TypeError):
        calculator.multiply(**{'a': None, 'b': None})
