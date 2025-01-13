"""
Workflow Manager for Windsurf AI.
Orchestrates code analysis, enhancement, and testing.
"""
import logging
from pathlib import Path
from typing import Dict, Any

from generate_code import CodeGenerator
from code_quality import CodeQualityAnalyzer
from test_generator import TestGenerator

# Set up paths
ROOT_DIR = Path(__file__).parent.parent
INPUT_DIR = ROOT_DIR / 'input_files'
OUTPUT_DIR = ROOT_DIR / 'output_files'
TEST_DIR = ROOT_DIR / 'tests'
LOG_DIR = ROOT_DIR / 'logs'

# Create directories
for directory in [INPUT_DIR, OUTPUT_DIR, TEST_DIR, LOG_DIR]:
    directory.mkdir(exist_ok=True)

# Configure logging
logging.basicConfig(
    filename=str(LOG_DIR / 'workflow.log'),
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class WorkflowManager:
    """Manages the code enhancement workflow."""
    
    def __init__(self):
        """Initialize workflow components."""
        self.code_generator = CodeGenerator()
        self.quality_analyzer = CodeQualityAnalyzer()
        self.test_generator = TestGenerator()
    
    def process_file(self, input_file: Path) -> Dict[str, Any]:
        """
        Process a single Python file through the enhancement workflow.
        
        Args:
            input_file: Path to input Python file
            
        Returns:
            Dict containing processing results
        """
        try:
            logger.info(f"Processing file: {input_file}")
            
            # Step 1: Analyze code quality
            quality_report = self.quality_analyzer.analyze_code(input_file)
            logger.info("Quality analysis complete")
            
            # Step 2: Generate enhanced code
            enhanced_code = self.code_generator.enhance_code(input_file)
            output_file = OUTPUT_DIR / f"enhanced_{input_file.name}"
            with open(output_file, 'w') as f:
                f.write(enhanced_code)
            logger.info(f"Enhanced code written to {output_file}")
            
            # Step 3: Generate test cases
            test_code = self.test_generator.generate_tests(input_file)
            test_file = TEST_DIR / f"test_{input_file.stem}.py"
            with open(test_file, 'w') as f:
                f.write(test_code)
            logger.info(f"Test cases written to {test_file}")
            
            return {
                'quality_report': quality_report,
                'enhanced_file': str(output_file),
                'test_file': str(test_file)
            }
            
        except Exception as e:
            logger.error(f"Error processing file: {str(e)}")
            return {}

def main():
    """Main entry point."""
    try:
        workflow = WorkflowManager()
        
        # Process all Python files in input directory
        for file_path in INPUT_DIR.glob('*.py'):
            results = workflow.process_file(file_path)
            
            if results:
                print("\nProcessing Summary:\n")
                print(f"Input:  {file_path}")
                print(f"Output: {results['enhanced_file']}")
                print(f"Tests:  {results['test_file']}\n")
                
                if results['quality_report'].get('suggestions'):
                    print("Suggestions for improvement:")
                    for suggestion in results['quality_report']['suggestions']:
                        print(f"- {suggestion}")
                
    except Exception as e:
        logger.error(f"Error in main workflow: {str(e)}")

if __name__ == '__main__':
    main()
