"""
Comprehensive test suite for the test generator system.
Tests are organized from basic to advanced functionality.
"""
import pytest
from pathlib import Path
import tempfile
import os
from scripts.test_generator import TestGenerator
from scripts.generate_code import CodeGenerator
import ast
import math
from hypothesis import given, settings, strategies as st, assume
from typing import Any, Dict, List, Optional

class TestBasicFunctionality:
    """Basic functionality tests for the test generator."""
    
    def setup_method(self):
        """Set up test environment."""
        self.test_generator = TestGenerator()
        self.code_generator = CodeGenerator()
    
    def test_simple_function(self):
        """Test generation for a simple function."""
        code = '''
        def add(a: int, b: int) -> int:
            """Add two numbers."""
            return a + b
        '''
        with tempfile.NamedTemporaryFile(suffix='.py', delete=False, mode='w') as f:
            f.write(code)
            temp_path = Path(f.name)
        
        try:
            test_cases = self.test_generator.generate_tests(temp_path)
            assert test_cases, "No test cases generated"
            assert any('test_add_basic' in test for test in test_cases)
            assert any('assert result is not None' in test for test in test_cases)
        finally:
            os.unlink(temp_path)
    
    def test_edge_case_function(self):
        """Test generation for edge cases."""
        code = '''
        def divide(a: float, b: float) -> float:
            """Divide two numbers."""
            if b == 0:
                raise ValueError("Cannot divide by zero")
            return a / b
        '''
        with tempfile.NamedTemporaryFile(suffix='.py', delete=False, mode='w') as f:
            f.write(code)
            temp_path = Path(f.name)
        
        try:
            test_cases = self.test_generator.generate_tests(temp_path)
            assert any('test_divide_edge' in test for test in test_cases)
            assert any('b=0' in test for test in test_cases)
        finally:
            os.unlink(temp_path)

class TestPropertyBasedTests:
    """Property-based test generation."""
    
    def setup_method(self):
        """Set up test environment."""
        self.test_generator = TestGenerator()
    
    def test_numeric_properties(self):
        """Test generation for numeric properties."""
        code = '''
        def multiply(a: float, b: float) -> float:
            """Multiply two numbers."""
            return a * b
        '''
        with tempfile.NamedTemporaryFile(suffix='.py', delete=False, mode='w') as f:
            f.write(code)
            temp_path = Path(f.name)
        
        try:
            test_cases = self.test_generator.generate_tests(temp_path)
            assert any('commutative' in test for test in test_cases)
            assert any('associative' in test for test in test_cases)
            assert any('@given' in test for test in test_cases)
        finally:
            os.unlink(temp_path)
    
    def test_collection_properties(self):
        """Test generation for collection properties."""
        code = '''
        def sort_list(items: List[int]) -> List[int]:
            """Sort a list of integers."""
            return sorted(items)
        '''
        with tempfile.NamedTemporaryFile(suffix='.py', delete=False, mode='w') as f:
            f.write(code)
            temp_path = Path(f.name)
        
        try:
            test_cases = self.test_generator.generate_tests(temp_path)
            assert any('length' in test for test in test_cases)
            assert any('sort_stability' in test for test in test_cases)
        finally:
            os.unlink(temp_path)

class TestErrorCases:
    """Error case test generation."""
    
    def setup_method(self):
        """Set up test environment."""
        self.test_generator = TestGenerator()
    
    def test_division_errors(self):
        """Test generation for division errors."""
        code = '''
        def safe_divide(a: float, b: float) -> float:
            """Safely divide two numbers."""
            if b == 0:
                raise ValueError("Cannot divide by zero")
            return a / b
        '''
        with tempfile.NamedTemporaryFile(suffix='.py', delete=False, mode='w') as f:
            f.write(code)
            temp_path = Path(f.name)
        
        try:
            test_cases = self.test_generator.generate_tests(temp_path)
            assert any('pytest.raises' in test for test in test_cases)
            assert any('ValueError' in test for test in test_cases)
        finally:
            os.unlink(temp_path)
    
    def test_type_errors(self):
        """Test generation for type errors."""
        code = '''
        def process_list(items: List[int]) -> int:
            """Process a list of integers."""
            return sum(items)
        '''
        with tempfile.NamedTemporaryFile(suffix='.py', delete=False, mode='w') as f:
            f.write(code)
            temp_path = Path(f.name)
        
        try:
            test_cases = self.test_generator.generate_tests(temp_path)
            assert any('TypeError' in test for test in test_cases)
            assert any('None' in test for test in test_cases)
        finally:
            os.unlink(temp_path)

class TestAdvancedFeatures:
    """Advanced test generation features."""
    
    def setup_method(self):
        """Set up test environment."""
        self.test_generator = TestGenerator()
    
    def test_async_function(self):
        """Test generation for async functions."""
        code = '''
        async def fetch_data(url: str) -> Dict[str, Any]:
            """Fetch data from URL."""
            return {'status': 'success'}
        '''
        with tempfile.NamedTemporaryFile(suffix='.py', delete=False, mode='w') as f:
            f.write(code)
            temp_path = Path(f.name)
        
        try:
            test_cases = self.test_generator.generate_tests(temp_path)
            assert any('async' in test for test in test_cases)
            assert any('await' in test for test in test_cases)
        finally:
            os.unlink(temp_path)
    
    def test_class_method(self):
        """Test generation for class methods."""
        code = '''
        class Calculator:
            def add(self, a: int, b: int) -> int:
                """Add two numbers."""
                return a + b
        '''
        with tempfile.NamedTemporaryFile(suffix='.py', delete=False, mode='w') as f:
            f.write(code)
            temp_path = Path(f.name)
        
        try:
            test_cases = self.test_generator.generate_tests(temp_path)
            assert any('Calculator' in test for test in test_cases)
            assert any('self' in test for test in test_cases)
        finally:
            os.unlink(temp_path)

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
