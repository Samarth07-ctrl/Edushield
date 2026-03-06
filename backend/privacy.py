"""
Differential Privacy Module for Federated Learning
Implements DP-SGD and secure aggregation mechanisms
"""

import numpy as np
import logging
from typing import List, Tuple
import config

logger = logging.getLogger(__name__)


class DifferentialPrivacy:
    """
    Implements Differential Privacy mechanisms for federated learning
    """
    
    def __init__(self, epsilon: float = None, delta: float = None, 
                 clip_norm: float = None, noise_multiplier: float = None):
        """
        Initialize DP parameters
        
        Args:
            epsilon: Privacy budget (lower = more private)
            delta: Privacy guarantee parameter
            clip_norm: Gradient clipping threshold
            noise_multiplier: Scale of Gaussian noise
        """
        self.epsilon = epsilon or config.DP_EPSILON
        self.delta = delta or config.DP_DELTA
        self.clip_norm = clip_norm or config.CLIP_NORM
        self.noise_multiplier = noise_multiplier or config.NOISE_MULTIPLIER
        
        # Calculate noise scale from epsilon and delta
        self.noise_scale = self._calculate_noise_scale()
        
        logger.info(f"DP initialized: ε={self.epsilon}, δ={self.delta}, "
                   f"clip_norm={self.clip_norm}, noise_scale={self.noise_scale:.4f}")
    
    def _calculate_noise_scale(self) -> float:
        """
        Calculate Gaussian noise scale from privacy parameters
        
        Returns:
            Noise scale (sigma)
        """
        # Using the Gaussian mechanism
        # sigma = (sensitivity * sqrt(2 * ln(1.25/delta))) / epsilon
        sensitivity = self.clip_norm
        sigma = (sensitivity * np.sqrt(2 * np.log(1.25 / self.delta))) / self.epsilon
        return sigma * self.noise_multiplier
    
    def clip_gradients(self, gradients: List[np.ndarray]) -> Tuple[List[np.ndarray], float]:
        """
        Clip gradients to bound sensitivity
        
        Args:
            gradients: List of gradient arrays
        
        Returns:
            Tuple of (clipped gradients, clipping factor)
        """
        # Calculate L2 norm of all gradients
        total_norm = np.sqrt(sum(np.sum(g ** 2) for g in gradients))
        
        # Calculate clipping factor
        clip_factor = min(1.0, self.clip_norm / (total_norm + 1e-6))
        
        # Clip gradients
        clipped_gradients = [g * clip_factor for g in gradients]
        
        if clip_factor < 1.0:
            logger.debug(f"Gradients clipped: norm={total_norm:.4f}, factor={clip_factor:.4f}")
        
        return clipped_gradients, clip_factor
    
    def add_noise(self, weights: List[np.ndarray]) -> List[np.ndarray]:
        """
        Add Gaussian noise to weights for differential privacy
        
        Args:
            weights: List of weight arrays
        
        Returns:
            Noisy weights
        """
        noisy_weights = []
        total_noise = 0
        
        for w in weights:
            # Generate Gaussian noise with same shape as weights
            noise = np.random.normal(0, self.noise_scale, w.shape)
            noisy_w = w + noise
            noisy_weights.append(noisy_w)
            total_noise += np.sum(noise ** 2)
        
        logger.debug(f"Added DP noise: scale={self.noise_scale:.4f}, "
                    f"total_noise_power={total_noise:.4f}")
        
        return noisy_weights
    
    def privatize_weights(self, weights: List[np.ndarray]) -> List[np.ndarray]:
        """
        Apply full DP mechanism: clip and add noise
        
        Args:
            weights: Original weights
        
        Returns:
            Privatized weights
        """
        # Clip weights (treating them as gradients)
        clipped_weights, _ = self.clip_gradients(weights)
        
        # Add noise
        private_weights = self.add_noise(clipped_weights)
        
        return private_weights
    
    def get_privacy_spent(self, num_rounds: int) -> Tuple[float, float]:
        """
        Calculate privacy budget spent over multiple rounds
        
        Args:
            num_rounds: Number of training rounds
        
        Returns:
            Tuple of (total epsilon, total delta)
        """
        # Using strong composition theorem (simplified)
        # For Gaussian mechanism with subsampling
        total_epsilon = self.epsilon * np.sqrt(2 * num_rounds * np.log(1 / self.delta))
        total_delta = num_rounds * self.delta
        
        return total_epsilon, total_delta
    
    def get_privacy_metrics(self, num_rounds: int = 1) -> dict:
        """
        Get comprehensive privacy metrics
        
        Args:
            num_rounds: Number of rounds completed
        
        Returns:
            Dictionary of privacy metrics
        """
        total_epsilon, total_delta = self.get_privacy_spent(num_rounds)
        
        return {
            'epsilon_per_round': self.epsilon,
            'delta_per_round': self.delta,
            'total_epsilon': total_epsilon,
            'total_delta': total_delta,
            'clip_norm': self.clip_norm,
            'noise_scale': self.noise_scale,
            'privacy_level': self._get_privacy_level(total_epsilon)
        }
    
    def _get_privacy_level(self, epsilon: float) -> str:
        """
        Categorize privacy level based on epsilon
        
        Args:
            epsilon: Privacy budget
        
        Returns:
            Privacy level string
        """
        if epsilon < 0.1:
            return "Very High"
        elif epsilon < 1.0:
            return "High"
        elif epsilon < 5.0:
            return "Medium"
        elif epsilon < 10.0:
            return "Low"
        else:
            return "Very Low"


class SecureAggregation:
    """
    Implements secure aggregation for federated learning
    """
    
    def __init__(self):
        """Initialize secure aggregation"""
        logger.info("Secure aggregation initialized")
    
    def encrypt_weights(self, weights: List[np.ndarray], key: bytes = None) -> bytes:
        """
        Encrypt model weights (simplified encryption for demo)
        
        Args:
            weights: Model weights to encrypt
            key: Encryption key (optional)
        
        Returns:
            Encrypted weights as bytes
        """
        from cryptography.fernet import Fernet
        
        # Generate key if not provided
        if key is None:
            key = Fernet.generate_key()
        
        cipher = Fernet(key)
        
        # Serialize weights to bytes
        weights_bytes = self._serialize_weights(weights)
        
        # Encrypt
        encrypted = cipher.encrypt(weights_bytes)
        
        logger.debug(f"Encrypted weights: {len(encrypted)} bytes")
        
        return encrypted, key
    
    def decrypt_weights(self, encrypted_weights: bytes, key: bytes) -> List[np.ndarray]:
        """
        Decrypt model weights
        
        Args:
            encrypted_weights: Encrypted weights
            key: Decryption key
        
        Returns:
            Decrypted weights
        """
        from cryptography.fernet import Fernet
        
        cipher = Fernet(key)
        
        # Decrypt
        decrypted_bytes = cipher.decrypt(encrypted_weights)
        
        # Deserialize
        weights = self._deserialize_weights(decrypted_bytes)
        
        logger.debug(f"Decrypted weights: {len(weights)} arrays")
        
        return weights
    
    def _serialize_weights(self, weights: List[np.ndarray]) -> bytes:
        """Serialize numpy arrays to bytes"""
        import pickle
        return pickle.dumps(weights)
    
    def _deserialize_weights(self, weights_bytes: bytes) -> List[np.ndarray]:
        """Deserialize bytes to numpy arrays"""
        import pickle
        return pickle.loads(weights_bytes)
    
    def add_masking(self, weights: List[np.ndarray], mask_seed: int = None) -> List[np.ndarray]:
        """
        Add random masking to weights (for secure aggregation)
        
        Args:
            weights: Original weights
            mask_seed: Random seed for mask generation
        
        Returns:
            Masked weights
        """
        if mask_seed is not None:
            np.random.seed(mask_seed)
        
        masked_weights = []
        for w in weights:
            mask = np.random.randn(*w.shape) * 0.01  # Small random mask
            masked_weights.append(w + mask)
        
        return masked_weights
    
    def remove_masking(self, masked_weights: List[np.ndarray], 
                       mask_seed: int) -> List[np.ndarray]:
        """
        Remove masking from weights
        
        Args:
            masked_weights: Masked weights
            mask_seed: Random seed used for masking
        
        Returns:
            Unmasked weights
        """
        np.random.seed(mask_seed)
        
        unmasked_weights = []
        for w in masked_weights:
            mask = np.random.randn(*w.shape) * 0.01
            unmasked_weights.append(w - mask)
        
        return unmasked_weights


def apply_privacy_preserving_aggregation(client_weights: List[List[np.ndarray]], 
                                        num_samples: List[int],
                                        dp_enabled: bool = True) -> List[np.ndarray]:
    """
    Apply privacy-preserving aggregation to client weights
    
    Args:
        client_weights: List of weights from each client
        num_samples: Number of samples per client
        dp_enabled: Whether to apply differential privacy
    
    Returns:
        Aggregated weights with privacy guarantees
    """
    from utils import calculate_weighted_average
    
    # Apply differential privacy to each client's weights
    if dp_enabled:
        dp = DifferentialPrivacy()
        private_weights = [dp.privatize_weights(w) for w in client_weights]
        logger.info(f"Applied DP to {len(client_weights)} clients")
    else:
        private_weights = client_weights
    
    # Aggregate using weighted average (FedAvg)
    aggregated_weights = calculate_weighted_average(private_weights, num_samples)
    
    return aggregated_weights


if __name__ == "__main__":
    # Test differential privacy
    print("Testing Differential Privacy Module...")
    
    dp = DifferentialPrivacy(epsilon=1.0, delta=1e-5)
    
    # Test with dummy weights
    dummy_weights = [np.random.randn(10, 5), np.random.randn(5, 1)]
    
    # Test clipping
    clipped, factor = dp.clip_gradients(dummy_weights)
    print(f"Clipping factor: {factor:.4f}")
    
    # Test noise addition
    noisy = dp.add_noise(dummy_weights)
    print(f"Noise added to {len(noisy)} weight arrays")
    
    # Test privacy metrics
    metrics = dp.get_privacy_metrics(num_rounds=10)
    print(f"Privacy metrics: {metrics}")
    
    # Test secure aggregation
    sa = SecureAggregation()
    encrypted, key = sa.encrypt_weights(dummy_weights)
    print(f"Encrypted size: {len(encrypted)} bytes")
    
    decrypted = sa.decrypt_weights(encrypted, key)
    print(f"Decrypted {len(decrypted)} arrays")
    
    print("\nDifferential Privacy module test completed!")
