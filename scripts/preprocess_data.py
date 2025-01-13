"""
Preprocesses Python code for model training.
Handles tokenization, cleaning, and formatting of code snippets.
"""
import os
import ast
import json
from typing import List, Dict, Tuple
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    filename='../logs/preprocessing.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CodePreprocessor:
    """Preprocesses Python code for model training."""
    
    def __init__(self, config_path: str = '../config/settings.json'):
        """Initialize preprocessor with configuration."""
        self.config = self._load_config(config_path)
        self.tokenizer_path = Path('../tokenizer/tokenizer.json')
        self.vocab = set()
        
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration settings."""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading config: {str(e)}")
            return {}
    
    def clean_code(self, code: str) -> str:
        """
        Clean and normalize code.
        
        Args:
            code: Raw Python code string
            
        Returns:
            Cleaned code string
        """
        try:
            # Parse and unparse to normalize code structure
            tree = ast.parse(code)
            cleaned_code = ast.unparse(tree)
            return cleaned_code
        except Exception as e:
            logger.error(f"Error cleaning code: {str(e)}")
            return code
    
    def tokenize_code(self, code: str) -> List[str]:
        """
        Tokenize code into meaningful segments.
        
        Args:
            code: Python code string
            
        Returns:
            List of tokens
        """
        tokens = []
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                # Extract different types of tokens
                if isinstance(node, ast.Name):
                    tokens.append(node.id)
                elif isinstance(node, ast.Str):
                    tokens.append('STRING_LITERAL')
                elif isinstance(node, ast.Num):
                    tokens.append('NUMBER_LITERAL')
                elif isinstance(node, ast.FunctionDef):
                    tokens.append(f'FUNCTION_{node.name}')
                elif isinstance(node, ast.ClassDef):
                    tokens.append(f'CLASS_{node.name}')
            
            # Update vocabulary
            self.vocab.update(tokens)
            return tokens
            
        except Exception as e:
            logger.error(f"Error tokenizing code: {str(e)}")
            return []
    
    def save_tokenizer(self) -> None:
        """Save tokenizer vocabulary to file."""
        try:
            tokenizer_data = {
                'vocabulary': list(self.vocab),
                'max_sequence_length': self.config.get('model_settings', {}).get('max_sequence_length', 512)
            }
            
            self.tokenizer_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.tokenizer_path, 'w') as f:
                json.dump(tokenizer_data, f, indent=2)
                
            logger.info(f"Saved tokenizer to {self.tokenizer_path}")
            
        except Exception as e:
            logger.error(f"Error saving tokenizer: {str(e)}")
    
    def process_file(self, file_path: str) -> Tuple[List[str], str]:
        """
        Process a single Python file.
        
        Args:
            file_path: Path to Python file
            
        Returns:
            Tuple of (tokens, cleaned_code)
        """
        try:
            with open(file_path, 'r') as f:
                code = f.read()
            
            cleaned_code = self.clean_code(code)
            tokens = self.tokenize_code(cleaned_code)
            
            logger.info(f"Successfully processed {file_path}")
            return tokens, cleaned_code
            
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {str(e)}")
            return [], ""

def main():
    """Main function to demonstrate usage."""
    preprocessor = CodePreprocessor()
    
    # Process input files
    input_dir = Path('../input_files')
    for file_path in input_dir.glob('*.py'):
        tokens, cleaned_code = preprocessor.process_file(str(file_path))
        
        if tokens:
            print(f"\nProcessed {file_path.name}:")
            print(f"Number of tokens: {len(tokens)}")
            print(f"Sample tokens: {tokens[:10]}")
    
    # Save tokenizer
    preprocessor.save_tokenizer()

if __name__ == "__main__":
    main()
