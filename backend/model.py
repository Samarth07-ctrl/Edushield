"""
Machine Learning Models for Smart Campus Use Cases
Implements models for both attendance prediction and learning recommendation
"""

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, models
import numpy as np
import logging
from typing import Tuple, List
import config

logger = logging.getLogger(__name__)


class AttendanceRiskModel:
    """
    Binary classification model for attendance risk prediction
    Predicts whether a student is at risk of low attendance
    """
    
    def __init__(self, input_dim: int = 4):
        """
        Initialize model
        
        Args:
            input_dim: Number of input features
        """
        self.input_dim = input_dim
        self.model = self._build_model()
        logger.info(f"Attendance Risk Model initialized with input_dim={input_dim}")
    
    def _build_model(self) -> keras.Model:
        """
        Build neural network architecture
        
        Returns:
            Compiled Keras model
        """
        model = models.Sequential([
            layers.Input(shape=(self.input_dim,)),
            
            # First hidden layer
            layers.Dense(config.HIDDEN_UNITS[0], activation=config.ACTIVATION),
            layers.Dropout(config.DROPOUT_RATE),
            
            # Second hidden layer
            layers.Dense(config.HIDDEN_UNITS[1], activation=config.ACTIVATION),
            layers.Dropout(config.DROPOUT_RATE),
            
            # Third hidden layer
            layers.Dense(config.HIDDEN_UNITS[2], activation=config.ACTIVATION),
            
            # Output layer (binary classification)
            layers.Dense(1, activation='sigmoid')
        ])
        
        # Compile model
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=config.LEARNING_RATE),
            loss='binary_crossentropy',
            metrics=['accuracy', keras.metrics.AUC(name='auc')]
        )
        
        logger.info(f"Model architecture: {[layer.output.shape for layer in model.layers]}")
        
        return model
    
    def train(self, X_train: np.ndarray, y_train: np.ndarray, 
              epochs: int = None, batch_size: int = None, 
              validation_split: float = 0.0, verbose: int = 0) -> dict:
        """
        Train model on local data
        
        Args:
            X_train: Training features
            y_train: Training labels
            epochs: Number of epochs
            batch_size: Batch size
            validation_split: Validation split ratio
            verbose: Verbosity level
        
        Returns:
            Training history
        """
        epochs = epochs or config.LOCAL_EPOCHS
        batch_size = batch_size or config.BATCH_SIZE
        
        history = self.model.fit(
            X_train, y_train,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=validation_split,
            verbose=verbose
        )
        
        logger.info(f"Training completed: {epochs} epochs, {len(X_train)} samples")
        
        return history.history
    
    def evaluate(self, X_test: np.ndarray, y_test: np.ndarray) -> Tuple[float, float]:
        """
        Evaluate model
        
        Args:
            X_test: Test features
            y_test: Test labels
        
        Returns:
            Tuple of (loss, accuracy)
        """
        results = self.model.evaluate(X_test, y_test, verbose=0)
        loss, accuracy = results[0], results[1]
        
        logger.info(f"Evaluation: loss={loss:.4f}, accuracy={accuracy:.4f}")
        
        return loss, accuracy
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Make predictions
        
        Args:
            X: Input features
        
        Returns:
            Predictions (probabilities)
        """
        predictions = self.model.predict(X, verbose=0)
        return predictions
    
    def get_weights(self) -> List[np.ndarray]:
        """
        Get model weights
        
        Returns:
            List of weight arrays
        """
        return self.model.get_weights()
    
    def set_weights(self, weights: List[np.ndarray]):
        """
        Set model weights
        
        Args:
            weights: List of weight arrays
        """
        self.model.set_weights(weights)
        logger.debug("Model weights updated")
    
    def save(self, filepath: str):
        """Save model to file"""
        self.model.save(filepath)
        logger.info(f"Model saved to {filepath}")
    
    def load(self, filepath: str):
        """Load model from file"""
        self.model = keras.models.load_model(filepath)
        logger.info(f"Model loaded from {filepath}")


class LearningRecommendationModel:
    """
    Multi-class classification model for personalized learning recommendations
    Predicts which subject a student should focus on
    """
    
    def __init__(self, input_dim: int = 8, num_classes: int = 4):
        """
        Initialize model
        
        Args:
            input_dim: Number of input features
            num_classes: Number of output classes
        """
        self.input_dim = input_dim
        self.num_classes = num_classes
        self.model = self._build_model()
        logger.info(f"Learning Recommendation Model initialized: "
                   f"input_dim={input_dim}, num_classes={num_classes}")
    
    def _build_model(self) -> keras.Model:
        """
        Build neural network architecture
        
        Returns:
            Compiled Keras model
        """
        model = models.Sequential([
            layers.Input(shape=(self.input_dim,)),
            
            # First hidden layer
            layers.Dense(config.HIDDEN_UNITS[0], activation=config.ACTIVATION),
            layers.BatchNormalization(),
            layers.Dropout(config.DROPOUT_RATE),
            
            # Second hidden layer
            layers.Dense(config.HIDDEN_UNITS[1], activation=config.ACTIVATION),
            layers.BatchNormalization(),
            layers.Dropout(config.DROPOUT_RATE),
            
            # Third hidden layer
            layers.Dense(config.HIDDEN_UNITS[2], activation=config.ACTIVATION),
            
            # Output layer (multi-class classification)
            layers.Dense(self.num_classes, activation='softmax')
        ])
        
        # Compile model
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=config.LEARNING_RATE),
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']
        )
        
        logger.info(f"Model architecture: {[layer.output.shape for layer in model.layers]}")
        
        return model
    
    def train(self, X_train: np.ndarray, y_train: np.ndarray, 
              epochs: int = None, batch_size: int = None, 
              validation_split: float = 0.0, verbose: int = 0) -> dict:
        """
        Train model on local data
        
        Args:
            X_train: Training features
            y_train: Training labels
            epochs: Number of epochs
            batch_size: Batch size
            validation_split: Validation split ratio
            verbose: Verbosity level
        
        Returns:
            Training history
        """
        epochs = epochs or config.LOCAL_EPOCHS
        batch_size = batch_size or config.BATCH_SIZE
        
        history = self.model.fit(
            X_train, y_train,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=validation_split,
            verbose=verbose
        )
        
        logger.info(f"Training completed: {epochs} epochs, {len(X_train)} samples")
        
        return history.history
    
    def evaluate(self, X_test: np.ndarray, y_test: np.ndarray) -> Tuple[float, float]:
        """
        Evaluate model
        
        Args:
            X_test: Test features
            y_test: Test labels
        
        Returns:
            Tuple of (loss, accuracy)
        """
        loss, accuracy = self.model.evaluate(X_test, y_test, verbose=0)
        
        logger.info(f"Evaluation: loss={loss:.4f}, accuracy={accuracy:.4f}")
        
        return loss, accuracy
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Make predictions
        
        Args:
            X: Input features
        
        Returns:
            Predictions (class probabilities)
        """
        predictions = self.model.predict(X, verbose=0)
        return predictions
    
    def get_weights(self) -> List[np.ndarray]:
        """
        Get model weights
        
        Returns:
            List of weight arrays
        """
        return self.model.get_weights()
    
    def set_weights(self, weights: List[np.ndarray]):
        """
        Set model weights
        
        Args:
            weights: List of weight arrays
        """
        self.model.set_weights(weights)
        logger.debug("Model weights updated")
    
    def save(self, filepath: str):
        """Save model to file"""
        self.model.save(filepath)
        logger.info(f"Model saved to {filepath}")
    
    def load(self, filepath: str):
        """Load model from file"""
        self.model = keras.models.load_model(filepath)
        logger.info(f"Model loaded from {filepath}")


def create_model(use_case: str) -> keras.Model:
    """
    Factory function to create model based on use case
    
    Args:
        use_case: 'attendance' or 'learning'
    
    Returns:
        Model instance
    """
    if use_case == 'attendance':
        return AttendanceRiskModel()
    elif use_case == 'learning':
        return LearningRecommendationModel()
    else:
        raise ValueError(f"Unknown use case: {use_case}")


def calculate_gradients(model: keras.Model, X: np.ndarray, y: np.ndarray) -> List[np.ndarray]:
    """
    Calculate gradients for given data
    
    Args:
        model: Keras model
        X: Input features
        y: Labels
    
    Returns:
        List of gradient arrays
    """
    with tf.GradientTape() as tape:
        predictions = model(X, training=True)
        loss = model.compiled_loss(y, predictions)
    
    gradients = tape.gradient(loss, model.trainable_variables)
    
    return [g.numpy() for g in gradients]


if __name__ == "__main__":
    # Test models
    print("Testing Model Module...")
    
    # Test Attendance Risk Model
    print("\n1. Testing Attendance Risk Model...")
    attendance_model = AttendanceRiskModel(input_dim=4)
    
    # Generate dummy data
    X_train = np.random.rand(100, 4).astype(np.float32)
    y_train = np.random.randint(0, 2, 100).astype(np.float32)
    
    # Train
    history = attendance_model.train(X_train, y_train, epochs=2, verbose=1)
    print(f"Training history keys: {history.keys()}")
    
    # Evaluate
    loss, acc = attendance_model.evaluate(X_train, y_train)
    print(f"Loss: {loss:.4f}, Accuracy: {acc:.4f}")
    
    # Get weights
    weights = attendance_model.get_weights()
    print(f"Number of weight arrays: {len(weights)}")
    
    # Test Learning Recommendation Model
    print("\n2. Testing Learning Recommendation Model...")
    learning_model = LearningRecommendationModel(input_dim=8, num_classes=4)
    
    # Generate dummy data
    X_train = np.random.rand(100, 8).astype(np.float32)
    y_train = np.random.randint(0, 4, 100)
    
    # Train
    history = learning_model.train(X_train, y_train, epochs=2, verbose=1)
    print(f"Training history keys: {history.keys()}")
    
    # Evaluate
    loss, acc = learning_model.evaluate(X_train, y_train)
    print(f"Loss: {loss:.4f}, Accuracy: {acc:.4f}")
    
    print("\nModel module test completed!")
