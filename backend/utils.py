"""
Utility functions for the Federated Learning Framework
"""

import numpy as np
import json
import os
import logging
from datetime import datetime
from typing import List, Dict, Any
import config

# Setup logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format=config.LOG_FORMAT
)
logger = logging.getLogger(__name__)


def create_directories():
    """Create necessary directories if they don't exist"""
    directories = [
        '../data',
        '../data/clients',
        '../models',
        '../logs'
    ]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        logger.info(f"Directory ensured: {directory}")


def serialize_weights(weights: List[np.ndarray]) -> List[List[float]]:
    """
    Convert numpy arrays to JSON-serializable lists
    
    Args:
        weights: List of numpy arrays (model weights)
    
    Returns:
        List of lists (serializable weights)
    """
    return [w.tolist() for w in weights]


def deserialize_weights(weights_list: List[List[float]]) -> List[np.ndarray]:
    """
    Convert lists back to numpy arrays
    
    Args:
        weights_list: List of lists (serialized weights)
    
    Returns:
        List of numpy arrays
    """
    return [np.array(w) for w in weights_list]


def calculate_weighted_average(weights_list: List[List[np.ndarray]], 
                               num_samples_list: List[int]) -> List[np.ndarray]:
    """
    Calculate weighted average of model weights (FedAvg algorithm)
    
    Args:
        weights_list: List of model weights from different clients
        num_samples_list: Number of samples each client trained on
    
    Returns:
        Averaged model weights
    """
    total_samples = sum(num_samples_list)
    
    # Initialize averaged weights with zeros
    avg_weights = [np.zeros_like(w) for w in weights_list[0]]
    
    # Weighted sum
    for client_weights, num_samples in zip(weights_list, num_samples_list):
        weight_factor = num_samples / total_samples
        for i, w in enumerate(client_weights):
            avg_weights[i] += w * weight_factor
    
    logger.info(f"Averaged weights from {len(weights_list)} clients with {total_samples} total samples")
    return avg_weights


def calculate_model_size(weights: List[np.ndarray]) -> int:
    """
    Calculate total size of model weights in bytes
    
    Args:
        weights: List of numpy arrays
    
    Returns:
        Size in bytes
    """
    total_bytes = sum(w.nbytes for w in weights)
    return total_bytes


def format_bytes(bytes_size: int) -> str:
    """
    Format bytes to human-readable string
    
    Args:
        bytes_size: Size in bytes
    
    Returns:
        Formatted string (e.g., "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} TB"


def calculate_accuracy(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """
    Calculate classification accuracy
    
    Args:
        y_true: True labels
        y_pred: Predicted labels
    
    Returns:
        Accuracy score (0-1)
    """
    return np.mean(y_true == y_pred)


def calculate_f1_score(y_true: np.ndarray, y_pred: np.ndarray, 
                       average: str = 'binary') -> float:
    """
    Calculate F1 score
    
    Args:
        y_true: True labels
        y_pred: Predicted labels
        average: Averaging method ('binary' or 'macro')
    
    Returns:
        F1 score
    """
    from sklearn.metrics import f1_score
    return f1_score(y_true, y_pred, average=average)


def save_metrics(metrics: Dict[str, Any], filename: str):
    """
    Save metrics to JSON file
    
    Args:
        metrics: Dictionary of metrics
        filename: Output filename
    """
    filepath = os.path.join('../logs', filename)
    with open(filepath, 'w') as f:
        json.dump(metrics, f, indent=2)
    logger.info(f"Metrics saved to {filepath}")


def load_metrics(filename: str) -> Dict[str, Any]:
    """
    Load metrics from JSON file
    
    Args:
        filename: Input filename
    
    Returns:
        Dictionary of metrics
    """
    filepath = os.path.join('../logs', filename)
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            return json.load(f)
    return {}


def get_timestamp() -> str:
    """
    Get current timestamp as string
    
    Returns:
        Formatted timestamp
    """
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def calculate_privacy_budget(epsilon_per_round: float, num_rounds: int) -> float:
    """
    Calculate total privacy budget consumed
    
    Args:
        epsilon_per_round: Epsilon value per round
        num_rounds: Number of training rounds
    
    Returns:
        Total epsilon consumed
    """
    # Using composition theorem (simplified)
    total_epsilon = epsilon_per_round * np.sqrt(num_rounds)
    return total_epsilon


def print_training_summary(metrics: Dict[str, Any]):
    """
    Print formatted training summary
    
    Args:
        metrics: Training metrics dictionary
    """
    print("\n" + "="*60)
    print("TRAINING SUMMARY")
    print("="*60)
    for key, value in metrics.items():
        if isinstance(value, float):
            print(f"{key:.<40} {value:.4f}")
        else:
            print(f"{key:.<40} {value}")
    print("="*60 + "\n")


class MetricsTracker:
    """Track and store training metrics over rounds"""
    
    def __init__(self):
        self.metrics = {
            'rounds': [],
            'accuracy': [],
            'loss': [],
            'privacy_budget': [],
            'communication_cost': [],
            'num_clients': []
        }
    
    def add_round(self, round_num: int, accuracy: float, loss: float, 
                  privacy_budget: float, comm_cost: int, num_clients: int):
        """Add metrics for a training round"""
        self.metrics['rounds'].append(round_num)
        self.metrics['accuracy'].append(accuracy)
        self.metrics['loss'].append(loss)
        self.metrics['privacy_budget'].append(privacy_budget)
        self.metrics['communication_cost'].append(comm_cost)
        self.metrics['num_clients'].append(num_clients)
    
    def get_metrics(self) -> Dict[str, List]:
        """Get all tracked metrics"""
        return self.metrics
    
    def get_latest(self) -> Dict[str, Any]:
        """Get latest metrics"""
        if not self.metrics['rounds']:
            return {}
        return {
            'round': self.metrics['rounds'][-1],
            'accuracy': self.metrics['accuracy'][-1],
            'loss': self.metrics['loss'][-1],
            'privacy_budget': self.metrics['privacy_budget'][-1],
            'communication_cost': self.metrics['communication_cost'][-1],
            'num_clients': self.metrics['num_clients'][-1]
        }
    
    def save(self, filename: str):
        """Save metrics to file"""
        save_metrics(self.metrics, filename)
    
    def load(self, filename: str):
        """Load metrics from file"""
        self.metrics = load_metrics(filename)


def validate_use_case(use_case: str) -> bool:
    """
    Validate if use case is supported
    
    Args:
        use_case: Use case identifier
    
    Returns:
        True if valid, False otherwise
    """
    return use_case in config.USE_CASES


def get_use_case_config(use_case: str) -> Dict[str, Any]:
    """
    Get configuration for a specific use case
    
    Args:
        use_case: Use case identifier
    
    Returns:
        Use case configuration dictionary
    """
    if not validate_use_case(use_case):
        raise ValueError(f"Invalid use case: {use_case}")
    return config.USE_CASES[use_case]


if __name__ == "__main__":
    # Test utilities
    create_directories()
    print("Utilities module loaded successfully!")
