"""
Integration tests for code generator and test generator.
"""
import pytest
from pathlib import Path
from scripts.generate_code import CodeGenerator
from scripts.test_generator import TestGenerator
import ast
import tempfile
import os

def test_code_generation_and_testing():
    """Test the full pipeline of code generation and test generation."""
    # Create a sample function to test
    sample_code = '''
def calculate_statistics(numbers: List[float]) -> Dict[str, float]:
    """Calculate basic statistics for a list of numbers."""
    if not numbers:
        return {'mean': 0.0, 'sum': 0.0, 'min': 0.0, 'max': 0.0}
    
    stats = {
        'mean': sum(numbers) / len(numbers),
        'sum': sum(numbers),
        'min': min(numbers),
        'max': max(numbers)
    }
    return stats
'''
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(suffix='.py', delete=False, mode='w') as f:
        f.write(sample_code)
        temp_path = Path(f.name)
    
    try:
        # Step 1: Enhance the code
        code_generator = CodeGenerator()
        enhanced_code = code_generator.enhance_code(temp_path)
        
        # Write enhanced code to new file
        enhanced_path = temp_path.parent / 'enhanced_code.py'
        with open(enhanced_path, 'w') as f:
            f.write(enhanced_code)
        
        # Step 2: Generate tests
        test_generator = TestGenerator()
        test_cases = test_generator.generate_tests(enhanced_path)
        
        # Verify test generation
        assert test_cases, "No test cases were generated"
        
        # Check for different types of tests
        test_types = set()
        for test in test_cases:
            if 'property' in test:
                test_types.add('property')
            elif 'edge' in test:
                test_types.add('edge')
            elif 'error' in test:
                test_types.add('error')
            else:
                test_types.add('basic')
        
        # Verify we have all types of tests
        assert 'basic' in test_types, "No basic tests generated"
        assert 'property' in test_types, "No property tests generated"
        assert 'edge' in test_types, "No edge case tests generated"
        
        # Write tests to file
        test_path = temp_path.parent / 'test_generated.py'
        with open(test_path, 'w') as f:
            f.write('\n'.join(test_cases))
        
        # Print summary
        print(f"\nGenerated {len(test_cases)} test cases:")
        print(f"- Basic tests: {sum(1 for t in test_cases if 'basic' in t)}")
        print(f"- Property tests: {sum(1 for t in test_cases if 'property' in t)}")
        print(f"- Edge case tests: {sum(1 for t in test_cases if 'edge' in t)}")
        print(f"- Error tests: {sum(1 for t in test_cases if 'error' in t)}")
        
    finally:
        # Cleanup
        os.unlink(temp_path)
        if enhanced_path.exists():
            os.unlink(enhanced_path)
        if test_path.exists():
            os.unlink(test_path)

def test_code_enhancement_features():
    """Test specific code enhancement features."""
    code_generator = CodeGenerator()
    
    # Test type inference
    sample_code = '''
def process_data(x: int, y: float) -> float:
    return x + y
'''
    with tempfile.NamedTemporaryFile(suffix='.py', delete=False, mode='w') as f:
        f.write(sample_code)
        temp_path = Path(f.name)
    
    try:
        enhanced_code = code_generator.enhance_code(temp_path)
        
        # Check for enhancements
        assert 'logging' in enhanced_code, "Logging not added"
        assert 'try:' in enhanced_code, "Error handling not added"
        assert 'pytest' in enhanced_code, "Test imports not added"
        assert 'hypothesis' in enhanced_code, "Property testing imports not added"
        
    finally:
        os.unlink(temp_path)

def test_test_generation_features():
    """Test specific test generation features."""
    test_generator = TestGenerator()
    
    # Test edge case detection
    sample_code = '''
def validate_input(value: int) -> bool:
    if value <= 0:
        raise ValueError("Value must be positive")
    return True
'''
    with tempfile.NamedTemporaryFile(suffix='.py', delete=False, mode='w') as f:
        f.write(sample_code)
        temp_path = Path(f.name)
    
    try:
        test_cases = test_generator.generate_tests(temp_path)
        
        # Check for different test types
        has_error_test = any('error' in test for test in test_cases)
        has_edge_test = any('edge' in test for test in test_cases)
        
        assert has_error_test, "No error tests generated for ValueError"
        assert has_edge_test, "No edge case tests generated for boundary value"
        
    finally:
        os.unlink(temp_path)

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
