from scripts.test_generator import TestGenerator
from pathlib import Path

# Create a test generator instance
generator = TestGenerator()

# Create a sample file to test
sample_file = Path('sample_code.py')
with open(sample_file, 'w') as f:
    f.write('''
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b

def divide(a: float, b: float) -> float:
    """Divide two numbers."""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b
''')

# Generate test cases
test_cases = generator.generate_tests(sample_file)

# Print generated test cases
print("\nGenerated Test Cases:")
for test in test_cases:
    print("\n" + "="*50)
    print(test)
    print("="*50)

# Cleanup
sample_file.unlink()
