"""
Code Generation Module for Windsurf AI.
Handles code analysis and enhancement.
"""
import ast
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Set, Tuple
import inspect

# Set up paths
ROOT_DIR = Path(__file__).parent.parent
LOG_DIR = ROOT_DIR / 'logs'
CONFIG_DIR = ROOT_DIR / 'config'
LOG_DIR.mkdir(exist_ok=True)

# Configure logging
logging.basicConfig(
    filename=str(LOG_DIR / 'code_generation.log'),
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TypeInferer:
    """Infers types from code analysis."""
    
    def __init__(self):
        """Initialize type inference rules."""
        self.type_map = {
            ast.List: 'List',
            ast.Dict: 'Dict',
            ast.Tuple: 'Tuple',
            ast.Set: 'Set',
            ast.Str: 'str',
            ast.Num: 'float',  # We'll refine this between int and float
            ast.NameConstant: 'bool',  # For True/False/None
        }
        
    def infer_type(self, node: ast.AST) -> str:
        """Infer type from AST node."""
        try:
            if isinstance(node, ast.Name):
                if node.id in ['True', 'False']:
                    return 'bool'
                elif node.id == 'None':
                    return 'None'
                elif node.id == 'dict':
                    return 'Dict'
                elif node.id == 'list':
                    return 'List'
                
            elif isinstance(node, ast.Num):
                if isinstance(node.n, int):
                    return 'int'
                return 'float'
                
            elif isinstance(node, ast.List):
                if node.elts:
                    element_types = {self.infer_type(elt) for elt in node.elts}
                    if len(element_types) == 1:
                        return f'List[{element_types.pop()}]'
                return 'List[Any]'
                
            elif isinstance(node, ast.Dict):
                if node.keys and node.values:
                    key_types = {self.infer_type(key) for key in node.keys}
                    value_types = {self.infer_type(value) for value in node.values}
                    if len(key_types) == 1 and len(value_types) == 1:
                        return f'Dict[{key_types.pop()}, {value_types.pop()}]'
                return 'Dict[str, Any]'  # Common case for dictionaries
                
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id == 'sum':
                        return 'float'
                    elif node.func.id == 'len':
                        return 'int'
                    elif node.func.id == 'max':
                        return 'float'
                    elif node.func.id in ['int', 'str', 'float', 'bool', 'list', 'dict', 'set']:
                        return node.func.id
                        
            for ast_type, type_name in self.type_map.items():
                if isinstance(node, ast_type):
                    return type_name
                    
        except Exception as e:
            logger.error(f"Error inferring type: {str(e)}")
            
        return 'Any'

class CodeGenerator:
    """Generates and enhances Python code."""
    
    def __init__(self):
        """Initialize the code generator."""
        self.enhancement_rules = {
            'add_imports': self._add_imports,
            'add_type_hints': self._add_type_hints,
            'add_docstrings': self._add_docstrings,
            'add_error_handling': self._add_error_handling,
            'add_logging': self._add_logging,
            'add_test_markers': self._add_test_markers,
            'add_test_helpers': self._add_test_helpers
        }
        self.type_inferer = TypeInferer()
        self.required_imports = set()
        self.test_patterns = {
            'edge_cases': {
                'empty_input': ['empty', 'none', 'null'],
                'boundary': ['min', 'max', 'limit', 'bound'],
                'error': ['error', 'exception', 'raise'],
                'special': ['zero', 'infinity', 'nan']
            },
            'property_tests': {
                'numeric': ['sum', 'average', 'mean', 'min', 'max'],
                'collection': ['sort', 'filter', 'map', 'reduce'],
                'validation': ['check', 'validate', 'verify']
            }
        }
        
    def enhance_code(self, file_path: Path) -> str:
        """
        Enhance the given Python code with improvements.
        
        Args:
            file_path: Path to the Python file
            
        Returns:
            Enhanced code as string
        """
        try:
            with open(file_path, 'r') as f:
                code = f.read()
            
            tree = ast.parse(code)
            enhanced_tree = self._apply_enhancements(tree)
            
            return ast.unparse(enhanced_tree)
            
        except Exception as e:
            logger.error(f"Error enhancing code: {str(e)}")
            return code
    
    def _add_imports(self, tree: ast.AST) -> ast.AST:
        """Add necessary imports."""
        imports = [
            'from typing import List, Dict, Optional, Union, Any, Tuple',
            'import logging',
            'import pytest',
            'from hypothesis import given, strategies as st',
            'logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")',
            'logger = logging.getLogger(__name__)'
        ]
        
        # Add imports at the beginning of the file
        for import_stmt in reversed(imports):
            tree.body.insert(0, ast.parse(import_stmt))
        
        return tree
    
    def _add_type_hints(self, tree: ast.AST) -> ast.AST:
        """Add type hints to functions and methods."""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Analyze function body to infer return type
                return_type = self._infer_return_type(node)
                if node.returns is None:
                    node.returns = ast.Name(id=return_type, ctx=ast.Load())
                
                # Analyze parameters
                for arg in node.args.args:
                    if arg.annotation is None:
                        if arg.arg == 'self':
                            continue
                        arg_type = self._infer_parameter_type(node, arg.arg)
                        arg.annotation = ast.Name(id=arg_type, ctx=ast.Load())
        return tree
    
    def _infer_return_type(self, node: ast.FunctionDef) -> str:
        """Infer function return type from return statements."""
        return_types = set()
        
        for child in ast.walk(node):
            if isinstance(child, ast.Return) and child.value:
                return_types.add(self.type_inferer.infer_type(child.value))
                
        if not return_types:
            return 'None'
        elif len(return_types) == 1:
            return return_types.pop()
        else:
            return f'Union[{", ".join(sorted(return_types))}]'
    
    def _infer_parameter_type(self, node: ast.FunctionDef, param_name: str) -> str:
        """Infer parameter type from usage."""
        param_types = set()
        
        for child in ast.walk(node):
            if isinstance(child, ast.Name) and child.id == param_name:
                # Look for operations that indicate type
                parent = self._get_parent_node(node, child)
                if parent:
                    param_types.add(self._infer_type_from_operation(parent))
                    
        if not param_types:
            return 'Any'
        elif len(param_types) == 1:
            return param_types.pop()
        else:
            return f'Union[{", ".join(sorted(param_types))}]'
    
    def _get_parent_node(self, tree: ast.AST, target: ast.AST) -> Optional[ast.AST]:
        """Find parent node of a given node."""
        for node in ast.walk(tree):
            for child in ast.iter_child_nodes(node):
                if child == target:
                    return node
        return None
    
    def _infer_type_from_operation(self, node: ast.AST) -> str:
        """Infer type from operation context."""
        if isinstance(node, ast.BinOp):
            if isinstance(node.op, (ast.Add, ast.Sub, ast.Mult, ast.Div)):
                return 'float'
            elif isinstance(node.op, ast.Mod):
                return 'str'
        elif isinstance(node, ast.Compare):
            return 'bool'
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                if node.func.id in ['len', 'sum', 'min', 'max']:
                    return 'int'
        return 'Any'
    
    def _add_docstrings(self, tree: ast.AST) -> ast.AST:
        """Add detailed docstrings to functions and classes."""
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and not ast.get_docstring(node):
                docstring = self._generate_docstring(node)
                node.body.insert(0, ast.Expr(value=ast.Str(s=docstring)))
        return tree
    
    def _generate_docstring(self, node: ast.AST) -> str:
        """Generate detailed docstring for node."""
        if isinstance(node, ast.FunctionDef):
            params = []
            for arg in node.args.args:
                if arg.arg != 'self':
                    arg_type = arg.annotation.id if arg.annotation else 'Any'
                    params.append(f'{arg.arg}: {arg_type}')
            
            return_type = node.returns.id if node.returns else 'None'
            
            docstring = f'''
            {node.name}
            
            Args:
                {chr(10).join(f"    {param}" for param in params)}
            
            Returns:
                {return_type}
            
            Raises:
                Exception: On error
            '''
        else:
            docstring = f'''
            {node.name}
            
            A class for handling {node.name.lower()} operations.
            '''
        
        return inspect.cleandoc(docstring)
    
    def _add_error_handling(self, tree: ast.AST) -> ast.AST:
        """Add try-except blocks to function bodies."""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Skip if already has error handling
                if any(isinstance(n, ast.Try) for n in node.body):
                    continue
                
                # Wrap function body in try-except
                original_body = node.body
                node.body = [
                    ast.Try(
                        body=original_body,
                        handlers=[
                            ast.ExceptHandler(
                                type=ast.Name(id='Exception', ctx=ast.Load()),
                                name=None,
                                body=[
                                    ast.Expr(
                                        value=ast.Call(
                                            func=ast.Attribute(
                                                value=ast.Name(id='logger', ctx=ast.Load()),
                                                attr='error',
                                                ctx=ast.Load()
                                            ),
                                            args=[
                                                ast.JoinedStr(
                                                    values=[
                                                        ast.Str(s=f"Error in {node.name}: "),
                                                        ast.FormattedValue(
                                                            value=ast.Name(id='e', ctx=ast.Load()),
                                                            conversion=-1
                                                        )
                                                    ]
                                                )
                                            ],
                                            keywords=[]
                                        )
                                    ),
                                    ast.Raise()
                                ]
                            )
                        ],
                        orelse=[],
                        finalbody=[]
                    )
                ]
        return tree
    
    def _add_logging(self, tree: ast.AST) -> ast.AST:
        """Add logging statements to functions."""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Add entry log
                entry_log = ast.Expr(
                    value=ast.Call(
                        func=ast.Attribute(
                            value=ast.Name(id='logger', ctx=ast.Load()),
                            attr='info',
                            ctx=ast.Load()
                        ),
                        args=[ast.Str(s=f"Entering {node.name}")],
                        keywords=[]
                    )
                )
                node.body.insert(0, entry_log)
                
                # Add exit log
                exit_log = ast.Expr(
                    value=ast.Call(
                        func=ast.Attribute(
                            value=ast.Name(id='logger', ctx=ast.Load()),
                            attr='info',
                            ctx=ast.Load()
                        ),
                        args=[ast.Str(s=f"Exiting {node.name}")],
                        keywords=[]
                    )
                )
                node.body.append(exit_log)
        return tree
    
    def _add_test_markers(self, tree: ast.AST) -> ast.AST:
        """Add test markers and decorators for pytest and hypothesis."""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Skip if already has test markers
                if any(isinstance(d, ast.Name) and d.id == 'pytest' for d in node.decorator_list):
                    continue
                
                needs_property_test = False
                needs_edge_case = False
                
                # Check function name and body for test patterns
                for pattern_type, patterns in self.test_patterns.items():
                    for category, keywords in patterns.items():
                        if any(kw in node.name.lower() for kw in keywords):
                            if pattern_type == 'property_tests':
                                needs_property_test = True
                            elif pattern_type == 'edge_cases':
                                needs_edge_case = True
                
                # Add appropriate decorators
                if needs_property_test:
                    node.decorator_list.append(
                        ast.Call(
                            func=ast.Name(id='given', ctx=ast.Load()),
                            args=[],
                            keywords=[
                                ast.keyword(
                                    arg='x',
                                    value=ast.Attribute(
                                        value=ast.Name(id='st', ctx=ast.Load()),
                                        attr='integers',
                                        ctx=ast.Load()
                                    )
                                )
                            ]
                        )
                    )
                
                if needs_edge_case:
                    node.decorator_list.append(
                        ast.Name(id='pytest.mark.edge_case', ctx=ast.Load())
                    )
        
        return tree
    
    def _add_test_helpers(self, tree: ast.AST) -> ast.AST:
        """Add helper functions for testing."""
        helpers = [
            '''
            def assert_raises(exc_type, func, *args, **kwargs):
                """Assert that function raises expected exception."""
                with pytest.raises(exc_type):
                    func(*args, **kwargs)
            ''',
            '''
            def assert_type(obj, expected_type):
                """Assert that object is of expected type."""
                assert isinstance(obj, expected_type), f"Expected type {expected_type}, got {type(obj)}"
            ''',
            '''
            def assert_valid_range(value, min_val, max_val):
                """Assert that value is within expected range."""
                assert min_val <= value <= max_val, f"Value {value} not in range [{min_val}, {max_val}]"
            '''
        ]
        
        for helper in helpers:
            tree.body.append(ast.parse(helper))
        
        return tree
    
    def _apply_enhancements(self, tree: ast.AST) -> ast.AST:
        """Apply all enhancement rules to the AST."""
        for rule in self.enhancement_rules.values():
            tree = rule(tree)
        return tree

def main():
    """Example usage of CodeGenerator."""
    generator = CodeGenerator()
    file_path = Path(__file__)
    enhanced_code = generator.enhance_code(file_path)
    print(enhanced_code)

if __name__ == '__main__':
    main()
