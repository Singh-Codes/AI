"""
Test Case Generator Module for Windsurf AI.
Generates test cases based on code analysis.
"""
import ast
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Set, Tuple, Type
import hypothesis.strategies as st
from hypothesis import given, settings, assume
import inspect
import random
import math
import pytest
from dataclasses import dataclass
from unittest.mock import Mock, patch

# Set up logging
logger = logging.getLogger(__name__)

@dataclass
class TestCase:
    """Represents a test case with inputs and expected output."""
    name: str
    inputs: Dict[str, Any]
    expected_output: Any
    test_type: str  # 'unit', 'property', 'edge_case', 'error'
    description: str
    assertions: List[str]
    setup_code: List[str]

class TestGenerator:
    """Generates test cases for Python code."""
    
    def __init__(self):
        """Initialize the test generator."""
        self.type_strategies = {
            'int': st.integers(min_value=-1000, max_value=1000),
            'float': st.floats(allow_nan=False, allow_infinity=False, min_value=-1000, max_value=1000),
            'str': st.text(min_size=1, max_size=100),
            'bool': st.booleans(),
            'List[int]': st.lists(st.integers(), min_size=1, max_size=100),
            'List[float]': st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=100),
            'List[str]': st.lists(st.text(), min_size=1, max_size=100),
            'Dict[str, Any]': st.dictionaries(
                keys=st.text(min_size=1),
                values=st.one_of(
                    st.integers(),
                    st.floats(allow_nan=False, allow_infinity=False),
                    st.text()
                ),
                min_size=1
            ),
            'Optional[List[int]]': st.one_of(st.none(), st.lists(st.integers())),
            'Optional[List[float]]': st.one_of(st.none(), st.lists(st.floats(allow_nan=False, allow_infinity=False))),
            'Optional[List[str]]': st.one_of(st.none(), st.lists(st.text())),
            'Optional[Dict[str, Any]]': st.one_of(st.none(), st.dictionaries(
                keys=st.text(min_size=1),
                values=st.one_of(st.integers(), st.floats(allow_nan=False, allow_infinity=False), st.text())
            )),
            'Set[int]': st.sets(st.integers(), min_size=1, max_size=100),
            'Set[str]': st.sets(st.text(), min_size=1, max_size=100),
            'Tuple[int, ...]': st.lists(st.integers()).map(tuple),
            'Tuple[str, ...]': st.lists(st.text()).map(tuple)
        }
        
        self.edge_cases = {
            'int': [0, 1, -1, math.inf, -math.inf],
            'float': [0.0, 1.0, -1.0, math.inf, -math.inf, math.nan],
            'str': ['', ' ', 'a', 'A', '0', '\n', '\t', '\\', "'", '"', '[]', '{}', None],
            'List[Any]': [[], [None], [1, None], [1, 2, 3] * 100],  # Large list
            'Dict[str, Any]': [{}, {'': None}, {'key': None}, {str(i): i for i in range(100)}],  # Large dict
            'Set[Any]': [set(), {None}, {1, None}, set(range(100))],  # Large set
            'Tuple[Any, ...]': [(), (None,), (1, None), tuple(range(100))]  # Large tuple
        }
        
        self.property_tests = {
            'numeric': [
                ('commutative', lambda x, y: x + y == y + x),
                ('associative', lambda x, y, z: (x + y) + z == x + (y + z)),
                ('distributive', lambda x, y, z: x * (y + z) == x * y + x * z),
                ('identity', lambda x: x + 0 == x and x * 1 == x),
                ('inverse', lambda x: x + (-x) == 0),
            ],
            'collection': [
                ('length', lambda x: len(x + x) == len(x) * 2),
                ('membership', lambda x, item: item in x + [item]),
                ('slice', lambda x: x[:] == x),
                ('concatenation', lambda x, y: len(x + y) == len(x) + len(y)),
                ('sort_stability', lambda x: sorted(sorted(x)) == sorted(x)),
            ],
            'string': [
                ('concatenation', lambda s1, s2: len(s1 + s2) == len(s1) + len(s2)),
                ('strip', lambda s: s.strip().strip() == s.strip()),
                ('case', lambda s: s.lower().lower() == s.lower()),
                ('split_join', lambda s, sep=' ': sep.join(s.split(sep)) == s),
            ]
        }
        
        self.error_cases = {
            'division': [
                ('zero_division', lambda x: 1/x, ZeroDivisionError),
                ('modulo_zero', lambda x: 1 % x, ZeroDivisionError),
            ],
            'indexing': [
                ('list_index', lambda lst, idx: lst[idx], IndexError),
                ('dict_key', lambda d, key: d[key], KeyError),
            ],
            'type_conversion': [
                ('int_conversion', lambda x: int(x), ValueError),
                ('float_conversion', lambda x: float(x), ValueError),
            ],
            'file_operations': [
                ('file_not_found', lambda path: open(path), FileNotFoundError),
                ('permission_error', lambda path: open(path, 'w'), PermissionError),
            ]
        }
        
    def _get_type_annotation(self, node: ast.AST) -> str:
        """Extract type annotation from AST node."""
        try:
            if isinstance(node, ast.Name):
                return node.id
            elif isinstance(node, ast.Constant):
                return str(node.value)
            elif isinstance(node, ast.Subscript):
                if isinstance(node.value, ast.Name):
                    container = node.value.id
                    if hasattr(node.slice, 'value'):  # Python 3.9+
                        slice_value = node.slice.value
                    else:
                        slice_value = node.slice
                    
                    if isinstance(slice_value, ast.Name):
                        elem_type = slice_value.id
                        return f"{container}[{elem_type}]"
                    elif isinstance(slice_value, ast.Constant):
                        return f"{container}[{slice_value.value}]"
                    elif isinstance(slice_value, ast.Tuple):
                        elts = []
                        for elt in slice_value.elts:
                            if isinstance(elt, ast.Name):
                                elts.append(elt.id)
                            elif isinstance(elt, ast.Constant):
                                elts.append(str(elt.value))
                            else:
                                elts.append('Any')
                        return f"{container}[{', '.join(elts)}]"
                    elif isinstance(slice_value, ast.Subscript):
                        # Handle nested types like List[Dict[str, int]]
                        inner_type = self._get_type_annotation(slice_value)
                        return f"{container}[{inner_type}]"
                    else:
                        return f"{container}[Any]"
                elif isinstance(node.value, ast.Attribute):
                    # Handle module.type annotations like typing.List
                    if isinstance(node.value.value, ast.Name):
                        container = f"{node.value.value.id}.{node.value.attr}"
                        if hasattr(node.slice, 'value'):  # Python 3.9+
                            slice_value = node.slice.value
                        else:
                            slice_value = node.slice
                        
                        if isinstance(slice_value, ast.Name):
                            elem_type = slice_value.id
                            return f"{container}[{elem_type}]"
                        else:
                            return f"{container}[Any]"
            elif isinstance(node, ast.Attribute):
                # Handle module.type annotations without parameters
                if isinstance(node.value, ast.Name):
                    return f"{node.value.id}.{node.attr}"
            return 'Any'
        except Exception as e:
            logger.warning(f"Error parsing type annotation: {e}")
            return 'Any'
    
    def _get_strategy_for_type(self, type_hint: Any) -> str:
        """Get a Hypothesis strategy for a given type."""
        if type_hint == int:
            return "integers(min_value=-1000, max_value=1000)"
        elif type_hint == float:
            return "floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False)"
        elif type_hint == str:
            return "text(min_size=1, max_size=50)"
        elif type_hint == bool:
            return "booleans()"
        elif getattr(type_hint, "__origin__", None) == list:
            element_type = type_hint.__args__[0]
            element_strategy = self._get_strategy_for_type(element_type)
            return f"lists({element_strategy}, min_size=1, max_size=10)"
        elif getattr(type_hint, "__origin__", None) == dict:
            key_type, value_type = type_hint.__args__
            key_strategy = self._get_strategy_for_type(key_type)
            value_strategy = self._get_strategy_for_type(value_type)
            return f"dictionaries(keys={key_strategy}, values={value_strategy}, min_size=1, max_size=10)"
        elif getattr(type_hint, "__origin__", None) == Union:
            strategies = [self._get_strategy_for_type(t) for t in type_hint.__args__]
            if type(None) in type_hint.__args__:
                return f"one_of(none(), {', '.join(s for s in strategies if s)})"
            return f"one_of({', '.join(strategies)})"
        return "none()"
    
    def _generate_basic_test(self, func_name: str, params: Dict[str, Any], return_type: Any, is_class_method: bool = False) -> List[TestCase]:
        """Generate basic test cases."""
        try:
            test_cases = []
            test_name = f"test_{func_name}_basic"
            
            # Generate basic test case with valid inputs
            inputs = {}
            setup_code = []
            
            if is_class_method:
                setup_code.append("calculator = Calculator()")
                func_name = f"calculator.{func_name}"
            
            for param_name, param_type in params.items():
                if param_name == 'self':
                    continue
                if param_type == int:
                    inputs[param_name] = 42
                elif param_type == float:
                    inputs[param_name] = 3.14
                elif param_type == str:
                    inputs[param_name] = "test"
                elif param_type == bool:
                    inputs[param_name] = True
                elif getattr(param_type, "__origin__", None) == list:
                    element_type = param_type.__args__[0]
                    if element_type == int:
                        inputs[param_name] = [1, 2, 3]
                    elif element_type == str:
                        inputs[param_name] = ["a", "b", "c"]
                    elif element_type == float:
                        inputs[param_name] = [1.0, 2.0, 3.0]
                elif getattr(param_type, "__origin__", None) == dict:
                    key_type, value_type = param_type.__args__
                    if key_type == str and value_type == str:
                        inputs[param_name] = {"key": "value"}
            
            # Create test case with basic assertions
            assertions = [
                "assert result is not None",
                f"assert isinstance(result, {self._get_assertion_type(return_type)})"
            ]
            
            test_case = TestCase(
                name=test_name,
                test_type="basic",
                description=f"Basic test for {func_name}",
                inputs=inputs,
                assertions=assertions,
                expected_output=None,
                setup_code=setup_code
            )
            test_cases.append(test_case)
            
            return test_cases
        except Exception as e:
            print(f"Error generating basic tests: {str(e)}")
            return []

    def _generate_property_test(self, func_name: str, params: Dict[str, Any], return_type: Any, is_class_method: bool = False) -> List[TestCase]:
        """Generate property-based test cases."""
        try:
            test_cases = []
            test_name = f"test_{func_name}_property"
            
            # Generate property test case
            inputs = {}
            setup_code = []
            
            if is_class_method:
                setup_code.append("calculator = Calculator()")
                func_name = f"calculator.{func_name}"
            
            for param_name, param_type in params.items():
                if param_name == 'self':
                    continue
                if param_type == int:
                    inputs[param_name] = "integers(min_value=-1000, max_value=1000)"
                elif param_type == float:
                    inputs[param_name] = "floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False)"
                elif param_type == str:
                    inputs[param_name] = "text(min_size=1, max_size=50)"
                elif param_type == bool:
                    inputs[param_name] = "booleans()"
                elif getattr(param_type, "__origin__", None) == list:
                    element_type = param_type.__args__[0]
                    if element_type == int:
                        inputs[param_name] = "lists(integers(min_value=-1000, max_value=1000), min_size=1, max_size=10)"
                    elif element_type == str:
                        inputs[param_name] = "lists(text(min_size=1, max_size=50), min_size=1, max_size=10)"
                    elif element_type == float:
                        inputs[param_name] = "lists(floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False), min_size=1, max_size=10)"
                elif getattr(param_type, "__origin__", None) == dict:
                    key_type, value_type = param_type.__args__
                    if key_type == str and value_type == str:
                        inputs[param_name] = "dictionaries(keys=text(min_size=1, max_size=10), values=text(min_size=1, max_size=50), min_size=1, max_size=10)"
            
            # Create test case with property test assertions
            assertions = [
                "assert result is not None",
                f"assert isinstance(result, {self._get_assertion_type(return_type)})"
            ]
            
            test_case = TestCase(
                name=test_name,
                test_type="property",
                description=f"Property test for {func_name}",
                inputs=inputs,
                assertions=assertions,
                expected_output=None,
                setup_code=setup_code
            )
            test_cases.append(test_case)
            
            return test_cases
        except Exception as e:
            print(f"Error generating property tests: {str(e)}")
            return []

    def _generate_error_test(self, func_name: str, params: Dict[str, Any], is_class_method: bool = False) -> List[TestCase]:
        """Generate error test cases."""
        try:
            test_cases = []
            test_name = f"test_{func_name}_error"
            
            # Generate error test case
            inputs = {}
            assertions = []
            setup_code = []
            
            if is_class_method:
                setup_code.append("calculator = Calculator()")
                func_name = f"calculator.{func_name}"
            
            if 'divide' in func_name:
                inputs = {'a': 1.0, 'b': 0.0}
                assertions = [
                    "with pytest.raises(ValueError) as exc_info:",
                    f"    {func_name}(1.0, 0.0)",
                    'assert str(exc_info.value) == "Cannot divide by zero"'
                ]
            elif 'process_list' in func_name:
                inputs = {'items': []}
                assertions = [
                    "with pytest.raises(ValueError) as exc_info:",
                    f"    {func_name}([])",
                    'assert str(exc_info.value) == "List cannot be empty"'
                ]
            elif 'merge_dicts' in func_name:
                inputs = {'d1': {}, 'd2': {}}
                assertions = [
                    "with pytest.raises(ValueError) as exc_info:",
                    f"    {func_name}({{}}, {{}})",
                    'assert str(exc_info.value) == "Dictionaries cannot be empty"'
                ]
            elif 'find_max' in func_name:
                inputs = {'numbers': [], 'default': None}
                assertions = [
                    f"result = {func_name}([], None)",
                    "assert result is None"
                ]
            elif '__init__' in func_name:
                # __init__ doesn't need error tests
                return []
            elif 'get_history' in func_name:
                # get_history doesn't need error tests
                return []
            else:
                inputs = {k: None for k in params if k != 'self'}
                assertions = [
                    "with pytest.raises(TypeError):",
                    f"    {func_name}(**{inputs})"
                ]
            
            test_case = TestCase(
                name=test_name,
                test_type="error",
                description=f"Error test for {func_name}",
                inputs=inputs,
                assertions=assertions,
                expected_output=None,
                setup_code=setup_code
            )
            test_cases.append(test_case)
            
            return test_cases
        except Exception as e:
            print(f"Error generating error tests: {str(e)}")
            return []
    
    def _get_assertion_type(self, type_hint: Any) -> str:
        """Get the assertion type for a given type hint."""
        if type_hint == int:
            return "int"
        elif type_hint == float:
            return "float"
        elif type_hint == str:
            return "str"
        elif type_hint == bool:
            return "bool"
        elif getattr(type_hint, "__origin__", None) == list:
            return "list"
        elif getattr(type_hint, "__origin__", None) == dict:
            return "dict"
        elif getattr(type_hint, "__origin__", None) == Union:
            types = [self._get_assertion_type(t) for t in type_hint.__args__]
            return f"({', '.join(types)})"
        return "object"

    def _generate_property_tests(self, node: ast.FunctionDef) -> List[TestCase]:
        """Generate property-based test cases."""
        try:
            # Get function parameters and their types
            params = {}
            for arg in node.args.args:
                if arg.arg != 'self':
                    if arg.annotation:
                        arg_type = self._get_type_annotation(arg.annotation)
                    else:
                        arg_type = 'Any'
                    params[arg.arg] = arg_type
            
            # Get return type
            return_type = 'Any'
            if node.returns:
                return_type = self._get_type_annotation(node.returns)
            
            # Generate property tests based on parameter types and function name
            test_cases = self._generate_property_test(node.name, params, return_type)
            
            return test_cases
        except Exception as e:
            logger.error(f"Error generating property tests: {e}")
            return []
    
    def _format_property_test(self, case: TestCase) -> str:
        """Format a property-based test case."""
        if not case.inputs:
            return ""
            
        inputs_str = []
        for k, v in case.inputs.items():
            if isinstance(v, str) and v.startswith("st."):
                inputs_str.append(f"{k}={v}")
        
        if not inputs_str:
            return ""
            
        test_body = [
            f"def {case.name}():",
            f'    """{case.description}"""',
            "    # Property-based test using hypothesis",
            f"    @given({', '.join(inputs_str)})",
            "    @settings(max_examples=100)",
            f"    def property_test({', '.join(case.inputs.keys())}):",
            "        # Skip invalid inputs",
            "        assume(all(x is not None for x in [" + ', '.join(case.inputs.keys()) + "]))",
            "",
            "        # Run test",
            f"        result = {case.name.replace('test_', '').replace('_property', '')}({', '.join(case.inputs.keys())})",
            "",
            "        # Verify properties",
            *[f"        {assertion}" for assertion in case.assertions],
            "",
            "    property_test()  # Run the property test"
        ]
        return "\n".join(test_body)

    def _format_error_test(self, case: TestCase) -> str:
        """Format an error test case."""
        if not case.assertions:
            return ""
            
        test_body = [
            f"def {case.name}():",
            f'    """{case.description}"""',
            "    # Error test",
            *[f"    {assertion}" for assertion in case.assertions]
        ]
        return "\n".join(test_body)

    def _format_standard_test(self, case: TestCase) -> str:
        """Format a standard test case."""
        if not case.inputs:
            return ""
            
        test_body = [
            f"def {case.name}():",
            f'    """{case.description}"""',
            "    # Test setup",
            *[f"    {param} = {repr(value)}" for param, value in case.inputs.items()],
            "",
            "    # Run test",
            f"    result = {case.name.replace('test_', '').replace('_basic', '')}({', '.join(case.inputs.keys())})",
            "",
            "    # Verify results",
            *[f"    {assertion}" for assertion in case.assertions]
        ]
        return "\n".join(test_body)

    def _format_test_cases(self, test_cases: List[TestCase]) -> List[str]:
        """Format test cases into pytest test functions."""
        formatted_tests = []
        
        if test_cases:
            # Add imports and setup
            imports = [
                "import pytest",
                "from hypothesis import given, settings, strategies as st, assume",
                "import math",
                "from typing import Any, Dict, List, Optional, Set, Tuple",
                "from unittest.mock import Mock, patch",
                "",
                "# Import functions under test",
                "from sample_functions import *",
                "",
                "@pytest.fixture",
                "def setup_function():",
                "    # Add any setup code here",
                "    pass",
                ""
            ]
            formatted_tests.extend(imports)
            
            # Format each test case
            for case in test_cases:
                formatted_test = ""
                if case.test_type == 'property':
                    formatted_test = self._format_property_test(case)
                elif case.test_type == 'error':
                    formatted_test = self._format_error_test(case)
                else:
                    formatted_test = self._format_standard_test(case)
                
                if formatted_test:
                    if case.setup_code:
                        formatted_tests.extend(case.setup_code)
                    formatted_tests.append(formatted_test)
                    formatted_tests.append("")  # Add blank line between tests
        
        return formatted_tests
    
    def generate_tests(self, file_path: Path) -> List[str]:
        """
        Generate test cases for all functions in the file.
        """
        try:
            with open(file_path, 'r') as f:
                code = f.read()
            
            tree = ast.parse(code)
            test_cases = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Generate tests for class methods
                    for method in node.body:
                        if isinstance(method, ast.FunctionDef):
                            test_cases.extend(self._generate_function_tests(method))
                elif isinstance(node, ast.FunctionDef):
                    # Generate tests for standalone functions
                    test_cases.extend(self._generate_function_tests(node))
            
            return self._format_test_cases(test_cases)
            
        except Exception as e:
            logger.error(f"Error generating tests: {str(e)}")
            return []
    
    def _generate_function_tests(self, node: ast.FunctionDef) -> List[TestCase]:
        """Generate test cases for a single function."""
        test_cases = []
        
        try:
            # Get function parameters and their types
            params = {}
            for arg in node.args.args:
                if arg.arg != 'self':
                    if arg.annotation:
                        arg_type = self._get_type_annotation(arg.annotation)
                    else:
                        arg_type = 'Any'
                    params[arg.arg] = arg_type
            
            # Get return type
            return_type = 'Any'
            if node.returns:
                return_type = self._get_type_annotation(node.returns)
            
            # Check if this is a class method
            is_class_method = 'self' in [arg.arg for arg in node.args.args]
            
            # Basic functionality tests
            test_cases.extend(self._generate_basic_test(node.name, params, return_type, is_class_method))
            
            # Property-based tests
            test_cases.extend(self._generate_property_test(node.name, params, return_type, is_class_method))
            
            # Error tests
            test_cases.extend(self._generate_error_test(node.name, params, is_class_method))
            
            return test_cases
        except Exception as e:
            logger.error(f"Error generating tests for {node.name}: {e}")
            return []
    
def main():
    """Example usage of TestGenerator."""
    try:
        # Create test generator
        generator = TestGenerator()
        
        # Generate tests for sample functions
        test_file = Path("sample_functions.py")
        tests = generator.generate_tests(test_file)
        
        # Write tests to file
        output_file = Path("tests/generated_tests.py")
        with open(output_file, "w") as f:
            f.write("\n".join(tests))
        
        print(f"Generated {len(tests)} test cases in {output_file}")
    except Exception as e:
        logger.error(f"Error in main: {e}")

if __name__ == '__main__':
    main()
