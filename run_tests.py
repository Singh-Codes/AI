#!/usr/bin/env python3

import os
import sys
import pytest
from pathlib import Path
from scripts.test_generator import TestGenerator

def main():
    """Run the test generator test suite."""
    print("Running Test Generator Test Suite")
    print("================================\n")
    
    # Create test generator
    generator = TestGenerator()
    
    # Generate tests for sample functions
    sample_file = Path("sample_functions.py")
    print(f"Generating tests for {os.path.abspath(sample_file)}")
    
    # Create tests directory if it doesn't exist
    tests_dir = Path("tests")
    tests_dir.mkdir(exist_ok=True)
    
    # Generate and write tests
    tests = generator.generate_tests(sample_file)
    test_file = tests_dir / "generated_tests.py"
    with open(test_file, "w") as f:
        f.write("\n".join(tests))
    
    # Run the generated tests
    pytest.main(["-v", str(test_file)])

if __name__ == "__main__":
    main()
