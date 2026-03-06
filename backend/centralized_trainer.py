"""
Centralized Model Trainer for Comparison
Trains model on centralized data (all client data combined)
"""

import numpy as np
import logging
from typing import Tuple, Dict, Any
import config
from database import ClientDatabase
from model import create_model
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CentralizedTrainer:
    """
    Trains model in centralized manner for comparison with federated approach
    """
    
    def __init__(self, use_case: str):
        """
        Initialize centralized trainer
        
        Args:
            use_case: 'attendance' or 'learning'
        """
        self.use_case = use_case
        self.model = create_model(use_case)
        self.metrics = {
            'accuracy': [],
            'loss': [],
            'training_time': 0,
            'communication_cost': 0,  # Zero for centralized
            'privacy_score': 0  # Zero privacy (all data centralized)
        }
        logger.info(f"Centralized trainer initialized for {use_case}")
    
    def collect_all_data(self, num_clients: int) -> Tuple[np.ndarray, np.ndarray]:
        """
        Collect data from all clients (simulates centralized data collection)
        
        Args:
            num_clients: Number of clients to collect from
        
        Returns:
            Tuple of (features, labels)
        """
        all_X = []
        all_y = []
        
        for client_id in range(1, num_clients + 1):
            db = ClientDatabase(client_id)
            
            if self.use_case == 'attendance':
                X, y = db.get_attendance_data()
            else:
                X, y = db.get_learning_data()
            
            if len(X) > 0:
                all_X.append(X)
                all_y.append(y)
        
        # Combine all data
        X_combined = np.vstack(all_X)
        y_combined = np.concatenate(all_y)
        
        logger.info(f"Collected {len(X_combined)} samples from {num_clients} clients")
        
        return X_combined, y_combined
    
    def train(self, num_clients: int, epochs: int = None) -> Dict[str, Any]:
        """
        Train centralized model
        
        Args:
            num_clients: Number of clients to collect data from
            epochs: Number of training epochs
        
        Returns:
            Training metrics
        """
        epochs = epochs or (config.LOCAL_EPOCHS * config.NUM_ROUNDS)
        
        logger.info(f"Starting centralized training for {epochs} epochs...")
        
        # Collect all data
        X, y = self.collect_all_data(num_clients)
        
        # Split into train and validation
        split_idx = int(len(X) * (1 - config.VALIDATION_SPLIT))
        X_train, X_val = X[:split_idx], X[split_idx:]
        y_train, y_val = y[:split_idx], y[split_idx:]
        
        # Train model
        start_time = time.time()
        
        history = self.model.train(
            X_train, y_train,
            epochs=epochs,
            batch_size=config.BATCH_SIZE,
            validation_split=0.0,  # We already split manually
            verbose=1
        )
        
        training_time = time.time() - start_time
        
        # Evaluate on validation set
        val_loss, val_accuracy = self.model.evaluate(X_val, y_val)
        
        # Update metrics
        self.metrics['accuracy'] = history.get('accuracy', [])
        self.metrics['loss'] = history.get('loss', [])
        self.metrics['val_accuracy'] = val_accuracy
        self.metrics['val_loss'] = val_loss
        self.metrics['training_time'] = training_time
        self.metrics['total_samples'] = len(X)
        
        logger.info(f"Centralized training completed in {training_time:.2f}s")
        logger.info(f"Final accuracy: {val_accuracy:.4f}")
        
        return self.metrics
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get training metrics
        
        Returns:
            Metrics dictionary
        """
        return self.metrics
    
    def save_model(self, filepath: str):
        """
        Save trained model
        
        Args:
            filepath: Path to save model
        """
        self.model.save(filepath)
        logger.info(f"Model saved to {filepath}")


def compare_with_federated(centralized_metrics: Dict[str, Any],
                          federated_metrics: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compare centralized and federated approaches
    
    Args:
        centralized_metrics: Metrics from centralized training
        federated_metrics: Metrics from federated training
    
    Returns:
        Comparison results
    """
    comparison = {
        'centralized': {
            'accuracy': centralized_metrics.get('val_accuracy', 0),
            'training_time': centralized_metrics.get('training_time', 0),
            'communication_cost': 0,
            'privacy_score': 0
        },
        'federated': {
            'accuracy': federated_metrics.get('final_accuracy', 0),
            'training_time': federated_metrics.get('total_time', 0),
            'communication_cost': federated_metrics.get('total_communication', 0),
            'privacy_score': 100  # Full privacy preserved
        },
        'differences': {
            'accuracy_diff': 0,
            'time_diff': 0,
            'privacy_gain': 100
        }
    }
    
    # Calculate differences
    comparison['differences']['accuracy_diff'] = (
        comparison['federated']['accuracy'] - comparison['centralized']['accuracy']
    )
    
    comparison['differences']['time_diff'] = (
        comparison['federated']['training_time'] - comparison['centralized']['training_time']
    )
    
    # Determine winner
    comparison['winner'] = {
        'accuracy': 'centralized' if comparison['centralized']['accuracy'] > comparison['federated']['accuracy'] else 'federated',
        'speed': 'centralized' if comparison['centralized']['training_time'] < comparison['federated']['training_time'] else 'federated',
        'privacy': 'federated',
        'overall': 'federated'  # Federated wins on privacy
    }
    
    return comparison


if __name__ == "__main__":
    print("="*60)
    print("CENTRALIZED MODEL TRAINER")
    print("="*60)
    
    # Test with attendance use case
    use_case = 'attendance'
    num_clients = 5
    
    print(f"\nTraining centralized model for {use_case}...")
    
    trainer = CentralizedTrainer(use_case)
    metrics = trainer.train(num_clients=num_clients, epochs=20)
    
    print("\n" + "="*60)
    print("TRAINING RESULTS")
    print("="*60)
    print(f"Final Accuracy: {metrics['val_accuracy']:.4f}")
    print(f"Final Loss: {metrics['val_loss']:.4f}")
    print(f"Training Time: {metrics['training_time']:.2f}s")
    print(f"Total Samples: {metrics['total_samples']}")
    print(f"Communication Cost: {metrics['communication_cost']} bytes (0 for centralized)")
    print(f"Privacy Score: {metrics['privacy_score']}% (0% for centralized)")
    print("="*60)
