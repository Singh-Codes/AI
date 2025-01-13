"""
Test module for data_analyzer.py
"""
import pytest
from data_analyzer import DataAnalyzer, DataValidator

def test_data_validator():
    """Test data validation functionality."""
    # Test numeric validation
    assert DataValidator.is_numeric(42) == True
    assert DataValidator.is_numeric("3.14") == True
    assert DataValidator.is_numeric("abc") == False
    
    # Test list validation
    valid_data = [1, "2", 3.14]
    assert len(DataValidator.validate_data_list(valid_data)) == 3
    
    # Test empty list
    with pytest.raises(ValueError):
        DataValidator.validate_data_list([])
    
    # Test invalid data
    with pytest.raises(ValueError):
        DataValidator.validate_data_list(["abc", "def"])

def test_data_analyzer():
    """Test DataAnalyzer functionality."""
    analyzer = DataAnalyzer()
    test_data = [1, 2, 3, 4, 5]
    
    # Test data addition
    analyzer.add_data(test_data)
    assert len(analyzer.data) == 5
    
    # Test analysis
    results = analyzer.analyze()
    assert results['count'] == 5
    assert results['mean'] == 3.0
    assert results['median'] == 3.0
    assert results['min'] == 1
    assert results['max'] == 5
    
    # Test history
    history = analyzer.get_analysis_history()
    assert len(history) == 1
    assert 'timestamp' in history[0]
    assert 'results' in history[0]

def test_error_handling():
    """Test error handling scenarios."""
    analyzer = DataAnalyzer()
    
    # Test empty data analysis
    with pytest.raises(ValueError):
        analyzer.analyze()
    
    # Test invalid data addition
    with pytest.raises(ValueError):
        analyzer.add_data(["invalid"])
