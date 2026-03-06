"""
API Client Wrapper
Provides convenient functions for interacting with the federated learning server
"""

import requests
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class FederatedLearningAPI:
    """
    API client for federated learning server
    """
    
    def __init__(self, base_url: str = 'http://localhost:5000'):
        """
        Initialize API client
        
        Args:
            base_url: Base URL of the server
        """
        self.base_url = base_url
        self.session = requests.Session()
    
    def health_check(self) -> bool:
        """
        Check if server is healthy
        
        Returns:
            True if server is healthy
        """
        try:
            response = self.session.get(f'{self.base_url}/api/health', timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def register_client(self, client_id: int) -> Dict[str, Any]:
        """
        Register a client with the server
        
        Args:
            client_id: Unique client identifier
        
        Returns:
            Response data
        """
        response = self.session.post(
            f'{self.base_url}/api/register-client',
            json={'client_id': client_id}
        )
        response.raise_for_status()
        return response.json()
    
    def start_training(self, use_case: str, num_rounds: int) -> Dict[str, Any]:
        """
        Start federated training
        
        Args:
            use_case: 'attendance' or 'learning'
            num_rounds: Number of training rounds
        
        Returns:
            Response data
        """
        response = self.session.post(
            f'{self.base_url}/api/federated/start',
            json={
                'use_case': use_case,
                'num_rounds': num_rounds
            }
        )
        response.raise_for_status()
        return response.json()
    
    def get_training_status(self) -> Dict[str, Any]:
        """
        Get current training status
        
        Returns:
            Status data
        """
        response = self.session.get(f'{self.base_url}/api/federated/status')
        response.raise_for_status()
        return response.json()
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get training metrics
        
        Returns:
            Metrics data
        """
        response = self.session.get(f'{self.base_url}/api/metrics')
        response.raise_for_status()
        return response.json()
    
    def train_centralized(self, use_case: str, num_clients: int = 5) -> Dict[str, Any]:
        """
        Train centralized model
        
        Args:
            use_case: 'attendance' or 'learning'
            num_clients: Number of clients to collect data from
        
        Returns:
            Training results
        """
        response = self.session.post(
            f'{self.base_url}/api/centralized/train',
            json={
                'use_case': use_case,
                'num_clients': num_clients
            }
        )
        response.raise_for_status()
        return response.json()
    
    def get_comparison(self) -> Dict[str, Any]:
        """
        Get comparison between centralized and federated
        
        Returns:
            Comparison data
        """
        response = self.session.get(f'{self.base_url}/api/comparison')
        response.raise_for_status()
        return response.json()
    
    def get_clients(self) -> Dict[str, Any]:
        """
        Get list of registered clients
        
        Returns:
            Client data
        """
        response = self.session.get(f'{self.base_url}/api/clients')
        response.raise_for_status()
        return response.json()


if __name__ == "__main__":
    # Test API
    api = FederatedLearningAPI()
    
    print("Testing API...")
    
    # Health check
    if api.health_check():
        print("✓ Server is healthy")
    else:
        print("✗ Server is not responding")
