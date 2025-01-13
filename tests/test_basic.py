"""
Basic tests for code generator and test generator.
"""
import pytest
from pathlib import Path
import tempfile
import os

def test_file_creation():
    """Test basic file operations."""
    # Create a temporary file
    with tempfile.NamedTemporaryFile(suffix='.py', delete=False, mode='w') as f:
        f.write('def add(a: int, b: int) -> int:\n    return a + b\n')
        temp_path = Path(f.name)
    
    try:
        # Verify file exists and content
        assert temp_path.exists()
        with open(temp_path, 'r') as f:
            content = f.read()
            assert 'def add' in content
            assert 'return a + b' in content
    finally:
        # Cleanup
        os.unlink(temp_path)

def test_ast_parsing():
    """Test AST parsing capabilities."""
    import ast
    
    code = '''
def calculate_sum(numbers: list) -> float:
    """Calculate sum of numbers."""
    return sum(numbers)
'''
    
    # Parse the code
    tree = ast.parse(code)
    
    # Verify AST structure
    assert isinstance(tree, ast.Module)
    assert len(tree.body) == 1
    
    func_def = tree.body[0]
    assert isinstance(func_def, ast.FunctionDef)
    assert func_def.name == 'calculate_sum'
    
    # Check docstring
    assert ast.get_docstring(func_def) == 'Calculate sum of numbers.'

def test_type_annotations():
    """Test type annotation handling."""
    import ast
    
    code = '''
def process_data(x: int, y: float = 0.0) -> float:
    return x + y
'''
    
    tree = ast.parse(code)
    func_def = tree.body[0]
    
    # Check argument annotations
    assert isinstance(func_def.args.args[0].annotation, ast.Name)
    assert func_def.args.args[0].annotation.id == 'int'
    
    assert isinstance(func_def.args.args[1].annotation, ast.Name)
    assert func_def.args.args[1].annotation.id == 'float'
    
    # Check return annotation
    assert isinstance(func_def.returns, ast.Name)
    assert func_def.returns.id == 'float'

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
