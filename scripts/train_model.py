"""
Trains the code generation model using preprocessed data.
"""
import os
import json
import logging
from pathlib import Path
import numpy as np
from tensorflow import keras
from tensorflow.keras import layers
import tensorflow as tf
from typing import List, Dict, Tuple

# Configure logging
logging.basicConfig(
    filename='../logs/training.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CodeGenerationModel:
    """Handles model creation, training, and saving."""
    
    def __init__(self, config_path: str = '../config/settings.json'):
        """Initialize the model with configuration."""
        self.config = self._load_config(config_path)
        self.model = None
        self.tokenizer_data = self._load_tokenizer()
        
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration settings."""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading config: {str(e)}")
            return {}
    
    def _load_tokenizer(self) -> Dict:
        """Load tokenizer data."""
        try:
            with open('../tokenizer/tokenizer.json', 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading tokenizer: {str(e)}")
            return {'vocabulary': [], 'max_sequence_length': 512}
    
    def create_model(self) -> None:
        """Create the neural network model."""
        try:
            vocab_size = len(self.tokenizer_data['vocabulary'])
            max_length = self.tokenizer_data['max_sequence_length']
            
            # Create a transformer-based model
            inputs = layers.Input(shape=(max_length,))
            embedding = layers.Embedding(vocab_size, 256)(inputs)
            
            # Transformer blocks
            transformer_block = self._create_transformer_block(embedding)
            
            # Output layer
            outputs = layers.Dense(vocab_size, activation='softmax')(transformer_block)
            
            self.model = keras.Model(inputs=inputs, outputs=outputs)
            self.model.compile(
                optimizer='adam',
                loss='sparse_categorical_crossentropy',
                metrics=['accuracy']
            )
            
            logger.info("Successfully created model")
            
        except Exception as e:
            logger.error(f"Error creating model: {str(e)}")
    
    def _create_transformer_block(self, inputs: tf.Tensor) -> tf.Tensor:
        """Create a transformer block."""
        # Multi-head attention
        attention = layers.MultiHeadAttention(
            num_heads=8, key_dim=256
        )(inputs, inputs)
        attention = layers.Dropout(0.1)(attention)
        
        # Add & normalize
        x = layers.LayerNormalization()(inputs + attention)
        
        # Feed forward
        ffn = layers.Dense(1024, activation='relu')(x)
        ffn = layers.Dense(256)(ffn)
        ffn = layers.Dropout(0.1)(ffn)
        
        # Add & normalize
        return layers.LayerNormalization()(x + ffn)
    
    def train(self, train_data: Tuple[np.ndarray, np.ndarray],
              validation_data: Tuple[np.ndarray, np.ndarray],
              epochs: int = 10) -> None:
        """
        Train the model.
        
        Args:
            train_data: Tuple of (input_data, target_data) for training
            validation_data: Tuple of (input_data, target_data) for validation
            epochs: Number of training epochs
        """
        try:
            if self.model is None:
                self.create_model()
            
            # Training callbacks
            callbacks = [
                keras.callbacks.ModelCheckpoint(
                    '../models/code_generator_model.h5',
                    save_best_only=True
                ),
                keras.callbacks.EarlyStopping(
                    patience=3,
                    restore_best_weights=True
                )
            ]
            
            # Train the model
            history = self.model.fit(
                train_data[0],
                train_data[1],
                epochs=epochs,
                validation_data=validation_data,
                callbacks=callbacks
            )
            
            logger.info("Model training completed successfully")
            
            # Save training history
            self._save_training_history(history.history)
            
        except Exception as e:
            logger.error(f"Error training model: {str(e)}")
    
    def _save_training_history(self, history: Dict) -> None:
        """Save training history to file."""
        try:
            history_path = Path('../models/training_history.json')
            history_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(history_path, 'w') as f:
                json.dump(history, f, indent=2)
            
            logger.info(f"Saved training history to {history_path}")
            
        except Exception as e:
            logger.error(f"Error saving training history: {str(e)}")
    
    def generate_code(self, input_sequence: np.ndarray,
                     max_length: int = 100) -> List[int]:
        """
        Generate code from input sequence.
        
        Args:
            input_sequence: Input token sequence
            max_length: Maximum length of generated sequence
            
        Returns:
            List of token indices for generated code
        """
        try:
            generated = []
            for _ in range(max_length):
                predictions = self.model.predict(input_sequence)
                next_token = np.argmax(predictions[0, -1, :])
                generated.append(next_token)
                
                # Update input sequence
                input_sequence = np.roll(input_sequence, -1)
                input_sequence[0, -1] = next_token
            
            return generated
            
        except Exception as e:
            logger.error(f"Error generating code: {str(e)}")
            return []

def main():
    """Main function to demonstrate usage."""
    model = CodeGenerationModel()
    
    # Example usage (you would need actual training data)
    print("Model will be trained when training data is provided")
    print("Use the preprocess_data.py script first to prepare the training data")

if __name__ == "__main__":
    main()
