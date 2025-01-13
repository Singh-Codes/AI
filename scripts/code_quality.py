"""
Code Quality Analysis Module for Windsurf AI.
Handles code quality checks and provides improvement suggestions.
"""
import ast
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Set
import radon.complexity as radon
from pylint.lint import Run
from pycodestyle import StyleGuide
import io
import sys
from contextlib import redirect_stdout, redirect_stderr

# Set up logging
logger = logging.getLogger(__name__)

class CodeQualityAnalyzer:
    """Analyzes code quality and provides improvement suggestions."""
    
    def __init__(self):
        """Initialize the code quality analyzer."""
        self.style_guide = StyleGuide(quiet=True)
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
        
    def analyze_code(self, file_path: Path) -> Dict[str, Any]:
        """
        Analyze code quality and return a report.
        
        Args:
            file_path: Path to the Python file
            
        Returns:
            Dict containing analysis results
        """
        try:
            results = {
                'style_issues': self._check_style(file_path),
                'complexity': self._check_complexity(file_path),
                'maintainability': self._check_maintainability(file_path),
                'suggestions': self._generate_suggestions(file_path),
                'pylint': self._check_pylint(file_path),
                'test_recommendations': self._analyze_test_needs(file_path)
            }
            return results
        except Exception as e:
            logger.error(f"Error analyzing code quality: {str(e)}")
            return {}
    
    def _check_style(self, file_path: Path) -> List[Dict[str, Any]]:
        """Check code style using pycodestyle."""
        try:
            result = self.style_guide.check_files([str(file_path)])
            return [
                {
                    'line': error.line_number,
                    'column': error.column,
                    'message': error.text,
                    'type': error.check
                }
                for error in result.get_statistics()
            ]
        except Exception as e:
            logger.error(f"Error checking style: {str(e)}")
            return []
    
    def _check_complexity(self, file_path: Path) -> Dict[str, Any]:
        """Check code complexity using radon."""
        try:
            with open(file_path, 'r') as f:
                code = f.read()
            
            complexity_results = {}
            blocks = radon.cc_visit(code)
            
            for block in blocks:
                complexity_results[block.name] = {
                    'complexity': block.complexity,
                    'rank': self._get_complexity_rank(block.complexity),
                    'line_number': block.lineno,
                    'endline': block.endline,
                    'test_priority': 'high' if block.complexity > 10 else 'medium' if block.complexity > 5 else 'low'
                }
            
            return complexity_results
        except Exception as e:
            logger.error(f"Error checking complexity: {str(e)}")
            return {}
    
    def _get_complexity_rank(self, complexity: int) -> str:
        """Get complexity rank (A-F) based on cyclomatic complexity."""
        if complexity <= 5:
            return 'A'
        elif complexity <= 10:
            return 'B'
        elif complexity <= 20:
            return 'C'
        elif complexity <= 30:
            return 'D'
        elif complexity <= 40:
            return 'E'
        else:
            return 'F'
    
    def _check_maintainability(self, file_path: Path) -> Dict[str, Any]:
        """Check code maintainability using various metrics."""
        try:
            with open(file_path, 'r') as f:
                code = f.read()
            
            tree = ast.parse(code)
            stats = {
                'num_functions': len([n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]),
                'num_classes': len([n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]),
                'lines_of_code': len(code.splitlines()),
                'docstring_coverage': self._calculate_docstring_coverage(tree),
                'type_hint_coverage': self._calculate_type_hint_coverage(tree),
                'test_coverage_estimate': self._estimate_test_coverage(tree)
            }
            
            return stats
        except Exception as e:
            logger.error(f"Error checking maintainability: {str(e)}")
            return {}
    
    def _calculate_docstring_coverage(self, tree: ast.AST) -> float:
        """Calculate percentage of functions/classes with docstrings."""
        try:
            nodes = [n for n in ast.walk(tree) 
                    if isinstance(n, (ast.FunctionDef, ast.ClassDef))]
            if not nodes:
                return 100.0
                
            nodes_with_docstring = [n for n in nodes if ast.get_docstring(n)]
            return (len(nodes_with_docstring) / len(nodes)) * 100
        except Exception as e:
            logger.error(f"Error calculating docstring coverage: {str(e)}")
            return 0.0
    
    def _calculate_type_hint_coverage(self, tree: ast.AST) -> float:
        """Calculate percentage of function parameters with type hints."""
        try:
            total_params = 0
            typed_params = 0
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    for arg in node.args.args:
                        if arg.arg != 'self':  # Skip self parameter
                            total_params += 1
                            if arg.annotation:
                                typed_params += 1
            
            return (typed_params / total_params * 100) if total_params else 100.0
        except Exception as e:
            logger.error(f"Error calculating type hint coverage: {str(e)}")
            return 0.0
    
    def _estimate_test_coverage(self, tree: ast.AST) -> Dict[str, Any]:
        """Estimate test coverage needs based on code analysis."""
        coverage_stats = {
            'functions_needing_tests': [],
            'edge_cases_needed': [],
            'property_tests_needed': []
        }
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if node.name.startswith('_'):  # Skip private methods
                    continue
                    
                # Check function complexity
                if ast.unparse(node).count('\n') > 10:
                    coverage_stats['functions_needing_tests'].append(node.name)
                
                # Check for edge cases
                for pattern_type, patterns in self.test_patterns['edge_cases'].items():
                    if any(p in node.name.lower() for p in patterns):
                        coverage_stats['edge_cases_needed'].append(
                            f"{node.name} ({pattern_type})"
                        )
                
                # Check for property-based tests
                for pattern_type, patterns in self.test_patterns['property_tests'].items():
                    if any(p in node.name.lower() for p in patterns):
                        coverage_stats['property_tests_needed'].append(
                            f"{node.name} ({pattern_type})"
                        )
        
        return coverage_stats
    
    def _generate_suggestions(self, file_path: Path) -> List[str]:
        """Generate improvement suggestions based on analysis."""
        try:
            suggestions = []
            maintainability = self._check_maintainability(file_path)
            complexity = self._check_complexity(file_path)
            
            # Check docstring coverage
            if maintainability.get('docstring_coverage', 0) < 80:
                suggestions.append("Consider adding docstrings to more functions and classes")
            
            # Check type hint coverage
            if maintainability.get('type_hint_coverage', 0) < 80:
                suggestions.append("Add type hints to more function parameters")
            
            # Check complexity and suggest test improvements
            for func_name, stats in complexity.items():
                if stats['rank'] in ['D', 'E', 'F']:
                    suggestions.append(
                        f"Function '{func_name}' has high complexity ({stats['complexity']}). "
                        "Consider breaking it into smaller functions and adding comprehensive tests"
                    )
                elif stats['test_priority'] == 'high':
                    suggestions.append(
                        f"Add property-based tests for complex function '{func_name}'"
                    )
            
            # Check file size
            if maintainability.get('lines_of_code', 0) > 500:
                suggestions.append(
                    "File is quite large. Consider splitting it into multiple modules"
                )
            
            # Add test-related suggestions
            test_coverage = maintainability.get('test_coverage_estimate', {})
            if test_coverage.get('functions_needing_tests'):
                suggestions.append(
                    "Add tests for functions: " + 
                    ", ".join(test_coverage['functions_needing_tests'])
                )
            if test_coverage.get('edge_cases_needed'):
                suggestions.append(
                    "Add edge case tests for: " + 
                    ", ".join(test_coverage['edge_cases_needed'])
                )
            if test_coverage.get('property_tests_needed'):
                suggestions.append(
                    "Add property-based tests for: " + 
                    ", ".join(test_coverage['property_tests_needed'])
                )
            
            return suggestions
        except Exception as e:
            logger.error(f"Error generating suggestions: {str(e)}")
            return []
    
    def _check_pylint(self, file_path: Path) -> Dict[str, Any]:
        """Check code using pylint."""
        try:
            output = io.StringIO()
            with redirect_stdout(output), redirect_stderr(output):
                Run([str(file_path)], exit_zero=True)
            
            report = output.getvalue()
            return {
                'report': report,
                'score': self._calculate_pylint_score(report)
            }
        except Exception as e:
            logger.error(f"Error checking pylint: {str(e)}")
            return {}
    
    def _calculate_pylint_score(self, report: str) -> float:
        """Calculate pylint score."""
        try:
            lines = report.splitlines()
            for line in lines:
                if 'Your code has been rated at' in line:
                    score = float(line.split('/')[-1].strip())
                    return score
            return 0.0
        except Exception as e:
            logger.error(f"Error calculating pylint score: {str(e)}")
            return 0.0
    
    def _analyze_test_needs(self, file_path: Path) -> Dict[str, Any]:
        """Analyze test requirements for the code."""
        try:
            with open(file_path, 'r') as f:
                code = f.read()
            
            tree = ast.parse(code)
            test_needs = {
                'required_test_types': set(),
                'functions_to_test': [],
                'suggested_frameworks': set(['unittest']),
                'coverage_targets': {
                    'statements': 80,
                    'branches': 70,
                    'functions': 90
                }
            }
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if node.name.startswith('_'):
                        continue
                        
                    func_info = {
                        'name': node.name,
                        'complexity': len(list(ast.walk(node))),
                        'test_types': []
                    }
                    
                    # Check for error handling
                    if any(isinstance(n, ast.Try) for n in ast.walk(node)):
                        func_info['test_types'].append('error_handling')
                        test_needs['suggested_frameworks'].add('pytest')
                    
                    # Check for numeric operations
                    if any(isinstance(n, (ast.Add, ast.Sub, ast.Mult, ast.Div)) 
                          for n in ast.walk(node)):
                        func_info['test_types'].append('numeric')
                        test_needs['suggested_frameworks'].add('hypothesis')
                    
                    # Check for collections
                    if any(isinstance(n, (ast.List, ast.Dict, ast.Set)) 
                          for n in ast.walk(node)):
                        func_info['test_types'].append('collections')
                        test_needs['suggested_frameworks'].add('hypothesis')
                    
                    test_needs['functions_to_test'].append(func_info)
                    test_needs['required_test_types'].update(func_info['test_types'])
            
            return test_needs
            
        except Exception as e:
            logger.error(f"Error analyzing test needs: {str(e)}")
            return {}
