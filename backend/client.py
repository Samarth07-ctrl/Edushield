"""
Federated Learning Client Node
Handles local training and communication with server
"""

import argparse
import requests
import numpy as np
import logging
import time
import json
from typing import Dict, Any, List
import config
from database import ClientDatabase
from model import create_model
from privacy import DifferentialPrivacy
import utils

logging.basicConfig(level=logging.INFO, format=config.LOG_FORMAT)
logger = logging.getLogger(__name__)


class FederatedClient:
    """
    Federated Learning Client
    Performs local training and communicates with central server
    """
    
    def __init__(self, client_id: int, server_url: str = None):
        """
        Initialize federated client
        
        Args:
            client_id: Unique client identifier
            server_url: URL of federated server
        """
        self.client_id = client_id
        self.server_url = server_url or f'http://localhost:{config.SERVER_PORT}'
        self.database = ClientDatabase(client_id)
        self.model = None
        self.use_case = None
        self.dp = DifferentialPrivacy() if config.DP_ENABLED else None
        
        logger.info(f"Client {client_id} initialized, server: {self.server_url}")
    
    def register(self) -> bool:
        """
        Register with federated server
        
        Returns:
            True if registration successful
        """
        try:
            response = requests.post(
                f'{self.server_url}/api/register-client',
                json={'client_id': self.client_id},
                timeout=5
            )
            
            if response.status_code == 200:
                logger.info(f"Client {self.client_id} registered successfully")
                return True
            else:
                logger.error(f"Registration failed: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Registration error: {e}")
            return False
    
    def initialize_model(self, use_case: str):
        """
        Initialize local model
        
        Args:
            use_case: 'attendance' or 'learning'
        """
        self.use_case = use_case
        self.model = create_model(use_case)
        logger.info(f"Model initialized for {use_case}")
    
    def download_global_model(self) -> bool:
        """
        Download global model weights from server
        
        Returns:
            True if download successful
        """
        try:
            response = requests.get(
                f'{self.server_url}/api/federated/global-model',
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                weights = utils.deserialize_weights(data['weights'])
                self.model.set_weights(weights)
                logger.info(f"Downloaded global model (round {data.get('round', 0)})")
                return True
            else:
                logger.warning("No global model available yet")
                return False
                
        except Exception as e:
            logger.error(f"Error downloading global model: {e}")
            return False
    
    def load_local_data(self) -> tuple:
        """
        Load training data from local database
        
        Returns:
            Tuple of (X_train, y_train)
        """
        if self.use_case == 'attendance':
            X, y = self.database.get_attendance_data()
        elif self.use_case == 'learning':
            X, y = self.database.get_learning_data()
        else:
            raise ValueError(f"Unknown use case: {self.use_case}")
        
        logger.info(f"Loaded {len(X)} local samples")
        return X, y
    
    def train_local_model(self, epochs: int = None) -> Dict[str, Any]:
        """
        Train model on local data
        
        Args:
            epochs: Number of local epochs
        
        Returns:
            Training metrics
        """
        epochs = epochs or config.LOCAL_EPOCHS
        
        # Load local data
        X_train, y_train = self.load_local_data()
        
        if len(X_train) == 0:
            logger.warning("No training data available")
            return {}
        
        # Train model
        logger.info(f"Starting local training: {epochs} epochs, {len(X_train)} samples")
        
        start_time = time.time()
        history = self.model.train(
            X_train, y_train,
            epochs=epochs,
            batch_size=config.BATCH_SIZE,
            validation_split=config.VALIDATION_SPLIT,
            verbose=0
        )
        training_time = time.time() - start_time
        
        # Evaluate
        loss, accuracy = self.model.evaluate(X_train, y_train)
        
        metrics = {
            'loss': float(loss),
            'accuracy': float(accuracy),
            'num_samples': len(X_train),
            'training_time': training_time
        }
        
        logger.info(f"Local training completed: accuracy={accuracy:.4f}, "
                   f"loss={loss:.4f}, time={training_time:.2f}s")
        
        return metrics
    
    def get_model_weights(self) -> List[np.ndarray]:
        """
        Get current model weights
        
        Returns:
            List of weight arrays
        """
        return self.model.get_weights()
    
    def apply_privacy(self, weights: List[np.ndarray]) -> List[np.ndarray]:
        """
        Apply differential privacy to weights
        
        Args:
            weights: Original weights
        
        Returns:
            Privatized weights
        """
        if self.dp and config.DP_ENABLED:
            private_weights = self.dp.privatize_weights(weights)
            logger.info("Applied differential privacy to weights")
            return private_weights
        return weights
    
    def upload_weights(self, weights: List[np.ndarray], 
                      num_samples: int, round_num: int) -> bool:
        """
        Upload model weights to server
        
        Args:
            weights: Model weights to upload
            num_samples: Number of samples trained on
            round_num: Current round number
        
        Returns:
            True if upload successful
        """
        try:
            # Apply privacy
            private_weights = self.apply_privacy(weights)
            
            # Serialize weights
            serialized_weights = utils.serialize_weights(private_weights)
            
            # Calculate size
            weight_size = utils.calculate_model_size(private_weights)
            
            # Upload to server
            payload = {
                'client_id': self.client_id,
                'weights': serialized_weights,
                'num_samples': num_samples,
                'round': round_num,
                'weight_size': weight_size
            }
            
            response = requests.post(
                f'{self.server_url}/api/federated/upload-weights',
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                logger.info(f"Uploaded weights: {utils.format_bytes(weight_size)}, "
                           f"{num_samples} samples")
                return True
            else:
                logger.error(f"Upload failed: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error uploading weights: {e}")
            return False
    
    def participate_in_round(self, round_num: int) -> bool:
        """
        Participate in a federated learning round
        
        Args:
            round_num: Current round number
        
        Returns:
            True if participation successful
        """
        logger.info(f"=== Round {round_num} ===")
        
        # Download global model
        if round_num > 1:
            self.download_global_model()
        
        # Train locally
        metrics = self.train_local_model()
        
        if not metrics:
            return False
        
        # Get weights
        weights = self.get_model_weights()
        
        # Upload weights
        success = self.upload_weights(
            weights, 
            metrics['num_samples'], 
            round_num
        )
        
        return success
    
    def run_federated_training(self, use_case: str, num_rounds: int):
        """
        Run complete federated training process
        
        Args:
            use_case: 'attendance' or 'learning'
            num_rounds: Number of rounds to train
        """
        logger.info(f"Starting federated training: {use_case}, {num_rounds} rounds")
        
        # Initialize model
        self.initialize_model(use_case)
        
        # Register with server
        if not self.register():
            logger.error("Failed to register with server")
            return
        
        # Participate in each round
        for round_num in range(1, num_rounds + 1):
            success = self.participate_in_round(round_num)
            
            if not success:
                logger.warning(f"Failed to participate in round {round_num}")
            
            # Wait between rounds
            time.sleep(2)
        
        logger.info("Federated training completed")
    
    def get_local_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about local data
        
        Returns:
            Statistics dictionary
        """
        if not self.use_case:
            return {}
        
        return self.database.get_statistics(self.use_case)


def main():
    """Main function for running client"""
    parser = argparse.ArgumentParser(description='Federated Learning Client')
    parser.add_argument('--client-id', type=int, required=True, 
                       help='Unique client ID')
    parser.add_argument('--server-url', type=str, 
                       default=f'http://localhost:{config.SERVER_PORT}',
                       help='Server URL')
    parser.add_argument('--use-case', type=str, choices=['attendance', 'learning'],
                       help='Use case to train')
    parser.add_argument('--rounds', type=int, default=config.NUM_ROUNDS,
                       help='Number of training rounds')
    parser.add_argument('--auto-start', action='store_true',
                       help='Automatically start training')
    
    args = parser.parse_args()
    
    # Create client
    client = FederatedClient(args.client_id, args.server_url)
    
    print("="*60)
    print(f"FEDERATED LEARNING CLIENT {args.client_id}")
    print("="*60)
    
    if args.auto_start and args.use_case:
        # Auto-start training
        client.run_federated_training(args.use_case, args.rounds)
    else:
        # Interactive mode - register with server first
        if not client.register():
            print(f"\nWARNING: Could not register with server at {args.server_url}")
            print("Make sure the server is running and try again.")
        
        print(f"\nClient {args.client_id} ready")
        print(f"Server: {args.server_url}")
        print("\nWaiting for training to start from dashboard...")
        print("(Or use --auto-start --use-case <case> to start automatically)")
        
        # Keep client running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nClient stopped")


if __name__ == "__main__":
    main()
