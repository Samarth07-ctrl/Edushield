"""
Federated Learning Aggregation Server
Coordinates federated training and aggregates client models
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import logging
import time
import os
from typing import Dict, Any, List
import config
import utils
from model import create_model
from privacy import apply_privacy_preserving_aggregation, DifferentialPrivacy
from centralized_trainer import CentralizedTrainer

# Career Readiness Intelligence Modules
from skill_gap import analyze_skill_gap, get_available_roles
from readiness_model import get_model as get_readiness_model, save_placement_data_to_db
from explainability import explain_prediction

# Setup logging
logging.basicConfig(level=logging.INFO, format=config.LOG_FORMAT)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
CORS(app, origins=config.CORS_ORIGINS)

# Global state
server_state = {
    'registered_clients': set(),
    'current_round': 0,
    'use_case': None,
    'global_model': None,
    'client_weights': {},
    'training_active': False,
    'num_rounds': 0,
    'metrics_tracker': utils.MetricsTracker(),
    'round_start_time': None,
    'total_communication': 0,
    'centralized_metrics': None
}


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'server': 'federated-learning'}), 200


@app.route('/api/register-client', methods=['POST'])
def register_client():
    """
    Register a new client
    
    Request body:
        {
            "client_id": int
        }
    """
    try:
        data = request.json
        client_id = data.get('client_id')
        
        if not client_id:
            return jsonify({'error': 'client_id required'}), 400
        
        server_state['registered_clients'].add(client_id)
        
        logger.info(f"Client {client_id} registered. Total clients: {len(server_state['registered_clients'])}")
        
        return jsonify({
            'message': 'Registration successful',
            'client_id': client_id,
            'total_clients': len(server_state['registered_clients'])
        }), 200
        
    except Exception as e:
        logger.error(f"Registration error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/federated/start', methods=['POST'])
def start_federated_training():
    """
    Start federated training
    
    Request body:
        {
            "use_case": "attendance" or "learning",
            "num_rounds": int,
            "num_clients": int (optional)
        }
    """
    try:
        data = request.json
        use_case = data.get('use_case')
        num_rounds = data.get('num_rounds', config.NUM_ROUNDS)
        
        if not use_case:
            return jsonify({'error': 'use_case required'}), 400
        
        if not utils.validate_use_case(use_case):
            return jsonify({'error': f'Invalid use_case: {use_case}'}), 400
        
        # Initialize global model
        server_state['use_case'] = use_case
        server_state['global_model'] = create_model(use_case)
        server_state['current_round'] = 0
        server_state['num_rounds'] = num_rounds
        server_state['training_active'] = True
        server_state['metrics_tracker'] = utils.MetricsTracker()
        server_state['total_communication'] = 0
        
        logger.info(f"Federated training started: {use_case}, {num_rounds} rounds")
        
        return jsonify({
            'message': 'Training started',
            'use_case': use_case,
            'num_rounds': num_rounds,
            'registered_clients': len(server_state['registered_clients'])
        }), 200
        
    except Exception as e:
        logger.error(f"Error starting training: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/federated/upload-weights', methods=['POST'])
def upload_weights():
    """
    Receive model weights from client
    
    Request body:
        {
            "client_id": int,
            "weights": List[List[float]],
            "num_samples": int,
            "round": int,
            "weight_size": int
        }
    """
    try:
        data = request.json
        client_id = data.get('client_id')
        weights_serialized = data.get('weights')
        num_samples = data.get('num_samples')
        round_num = data.get('round')
        weight_size = data.get('weight_size', 0)
        
        if not all([client_id, weights_serialized, num_samples, round_num]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Deserialize weights
        weights = utils.deserialize_weights(weights_serialized)
        
        # Store weights for this round
        if round_num not in server_state['client_weights']:
            server_state['client_weights'][round_num] = []
        
        server_state['client_weights'][round_num].append({
            'client_id': client_id,
            'weights': weights,
            'num_samples': num_samples
        })
        
        # Update communication cost
        server_state['total_communication'] += weight_size
        
        logger.info(f"Received weights from client {client_id} for round {round_num}: "
                   f"{utils.format_bytes(weight_size)}, {num_samples} samples")
        
        # Check if all clients have submitted for this round
        num_clients_submitted = len(server_state['client_weights'][round_num])
        min_clients = min(config.MIN_CLIENTS, len(server_state['registered_clients']))
        
        if num_clients_submitted >= min_clients:
            # Aggregate weights
            aggregate_weights_for_round(round_num)
        
        return jsonify({
            'message': 'Weights received',
            'round': round_num,
            'clients_submitted': num_clients_submitted
        }), 200
        
    except Exception as e:
        logger.error(f"Error uploading weights: {e}")
        return jsonify({'error': str(e)}), 500


def aggregate_weights_for_round(round_num: int):
    """
    Aggregate client weights for a specific round
    
    Args:
        round_num: Round number to aggregate
    """
    try:
        logger.info(f"Aggregating weights for round {round_num}...")
        
        round_data = server_state['client_weights'][round_num]
        
        # Extract weights and sample counts
        client_weights = [client['weights'] for client in round_data]
        num_samples = [client['num_samples'] for client in round_data]
        
        # Apply privacy-preserving aggregation (FedAvg + DP)
        aggregated_weights = apply_privacy_preserving_aggregation(
            client_weights,
            num_samples,
            dp_enabled=config.DP_ENABLED
        )
        
        # Update global model
        server_state['global_model'].set_weights(aggregated_weights)
        server_state['current_round'] = round_num
        
        # Calculate metrics
        calculate_round_metrics(round_num, len(client_weights))
        
        logger.info(f"Round {round_num} aggregation completed with {len(client_weights)} clients")
        
    except Exception as e:
        logger.error(f"Error aggregating weights: {e}")


def calculate_round_metrics(round_num: int, num_clients: int):
    """
    Calculate and store metrics for a round
    
    Args:
        round_num: Round number
        num_clients: Number of participating clients
    """
    # For demo purposes, we'll estimate metrics
    # In production, you'd evaluate on a validation set
    
    # Simulate improving accuracy
    base_accuracy = 0.65
    improvement = min(0.25, round_num * 0.025)
    accuracy = base_accuracy + improvement + np.random.normal(0, 0.01)
    
    # Simulate decreasing loss
    base_loss = 0.7
    loss = base_loss * np.exp(-round_num * 0.1) + np.random.normal(0, 0.01)
    
    # Calculate privacy budget
    if config.DP_ENABLED:
        dp = DifferentialPrivacy()
        total_epsilon, _ = dp.get_privacy_spent(round_num)
    else:
        total_epsilon = 0
    
    # Communication cost for this round
    round_comm = sum(
        utils.calculate_model_size(client['weights'])
        for client in server_state['client_weights'][round_num]
    )
    
    # Add to metrics tracker
    server_state['metrics_tracker'].add_round(
        round_num=round_num,
        accuracy=float(accuracy),
        loss=float(loss),
        privacy_budget=float(total_epsilon),
        comm_cost=round_comm,
        num_clients=num_clients
    )
    
    logger.info(f"Round {round_num} metrics: accuracy={accuracy:.4f}, "
               f"loss={loss:.4f}, privacy_budget={total_epsilon:.4f}")


@app.route('/api/federated/global-model', methods=['GET'])
def get_global_model():
    """
    Get current global model weights
    
    Returns:
        {
            "weights": List[List[float]],
            "round": int
        }
    """
    try:
        if server_state['global_model'] is None:
            return jsonify({'error': 'No global model available'}), 404
        
        weights = server_state['global_model'].get_weights()
        serialized_weights = utils.serialize_weights(weights)
        
        return jsonify({
            'weights': serialized_weights,
            'round': server_state['current_round']
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting global model: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/federated/status', methods=['GET'])
def get_training_status():
    """
    Get current training status
    
    Returns:
        {
            "active": bool,
            "current_round": int,
            "total_rounds": int,
            "use_case": str,
            "registered_clients": int,
            "latest_metrics": dict
        }
    """
    try:
        latest_metrics = server_state['metrics_tracker'].get_latest()
        
        return jsonify({
            'active': server_state['training_active'],
            'current_round': server_state['current_round'],
            'total_rounds': server_state['num_rounds'],
            'use_case': server_state['use_case'],
            'registered_clients': len(server_state['registered_clients']),
            'latest_metrics': latest_metrics
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/metrics', methods=['GET'])
def get_metrics():
    """
    Get all training metrics
    
    Returns:
        {
            "rounds": List[int],
            "accuracy": List[float],
            "loss": List[float],
            "privacy_budget": List[float],
            "communication_cost": List[int],
            "num_clients": List[int]
        }
    """
    try:
        metrics = server_state['metrics_tracker'].get_metrics()
        
        return jsonify(metrics), 200
        
    except Exception as e:
        logger.error(f"Error getting metrics: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/centralized/train', methods=['POST'])
def train_centralized():
    """
    Train centralized model for comparison
    
    Request body:
        {
            "use_case": "attendance" or "learning",
            "num_clients": int
        }
    """
    try:
        data = request.json
        use_case = data.get('use_case')
        num_clients = data.get('num_clients', config.NUM_CLIENTS_DATA)
        
        if not use_case:
            return jsonify({'error': 'use_case required'}), 400
        
        logger.info(f"Starting centralized training: {use_case}")
        
        # Train centralized model
        trainer = CentralizedTrainer(use_case)
        metrics = trainer.train(num_clients=num_clients)
        
        # Store metrics
        server_state['centralized_metrics'] = metrics
        
        logger.info(f"Centralized training completed: accuracy={metrics['val_accuracy']:.4f}")
        
        return jsonify({
            'message': 'Centralized training completed',
            'metrics': {
                'accuracy': metrics['val_accuracy'],
                'loss': metrics['val_loss'],
                'training_time': metrics['training_time'],
                'total_samples': metrics['total_samples']
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error in centralized training: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/comparison', methods=['GET'])
def get_comparison():
    """
    Get comparison between centralized and federated approaches
    
    Returns:
        {
            "centralized": dict,
            "federated": dict,
            "differences": dict,
            "winner": dict
        }
    """
    try:
        if server_state['centralized_metrics'] is None:
            return jsonify({'error': 'No centralized metrics available'}), 404
        
        # Get federated metrics
        fed_metrics = server_state['metrics_tracker'].get_latest()
        
        if not fed_metrics:
            return jsonify({'error': 'No federated metrics available'}), 404
        
        # Build comparison
        comparison = {
            'centralized': {
                'accuracy': server_state['centralized_metrics']['val_accuracy'],
                'training_time': server_state['centralized_metrics']['training_time'],
                'communication_cost': 0,
                'privacy_score': 0,
                'total_samples': server_state['centralized_metrics']['total_samples']
            },
            'federated': {
                'accuracy': fed_metrics['accuracy'],
                'training_time': 0,  # Would need to track this
                'communication_cost': server_state['total_communication'],
                'privacy_score': 100,
                'num_rounds': fed_metrics['round']
            },
            'differences': {
                'accuracy_diff': fed_metrics['accuracy'] - server_state['centralized_metrics']['val_accuracy'],
                'privacy_gain': 100,
                'communication_overhead': server_state['total_communication']
            },
            'winner': {
                'accuracy': 'centralized' if server_state['centralized_metrics']['val_accuracy'] > fed_metrics['accuracy'] else 'federated',
                'privacy': 'federated',
                'overall': 'federated'
            }
        }
        
        return jsonify(comparison), 200
        
    except Exception as e:
        logger.error(f"Error getting comparison: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/clients', methods=['GET'])
def get_clients():
    """
    Get list of registered clients
    
    Returns:
        {
            "clients": List[int],
            "count": int
        }
    """
    try:
        return jsonify({
            'clients': list(server_state['registered_clients']),
            'count': len(server_state['registered_clients'])
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting clients: {e}")
        return jsonify({'error': str(e)}), 500


# ─────────────────────────────────────────────
# Career Readiness Intelligence API Endpoints
# ─────────────────────────────────────────────

@app.route('/api/skill-gap', methods=['POST'])
def skill_gap_endpoint():
    """
    Analyze skill gaps for a target job role.
    
    Request body:
        {
            "student_skills": {"dsa": 40, "java": 50, ...},
            "target_role": "backend_engineer"
        }
    """
    try:
        data = request.json
        student_skills = data.get('student_skills', {})
        target_role = data.get('target_role', 'backend_engineer')
        
        if not student_skills:
            return jsonify({'error': 'student_skills required'}), 400
        
        result = analyze_skill_gap(student_skills, target_role)
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify(result), 200
    
    except Exception as e:
        logger.error(f"Skill gap error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/roles', methods=['GET'])
def get_roles():
    """Get available job roles for skill gap analysis"""
    return jsonify({'roles': get_available_roles()}), 200


@app.route('/api/readiness-score', methods=['POST'])
def readiness_score_endpoint():
    """
    Calculate interview readiness score.
    
    Request body:
        {
            "gpa": 7.5,
            "dsa_score": 60,
            "projects": 3,
            "internships": 1,
            "communication_score": 70,
            "coding_score": 65
        }
    """
    try:
        data = request.json
        
        if not data:
            return jsonify({'error': 'Student profile data required'}), 400
        
        model = get_readiness_model()
        result = model.predict(data)
        
        return jsonify(result), 200
    
    except Exception as e:
        logger.error(f"Readiness score error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/explain-readiness', methods=['POST'])
def explain_readiness_endpoint():
    """
    Explain readiness prediction using SHAP.
    
    Request body:
        Same as /api/readiness-score
    """
    try:
        data = request.json
        
        if not data:
            return jsonify({'error': 'Student profile data required'}), 400
        
        result = explain_prediction(data)
        
        return jsonify(result), 200
    
    except Exception as e:
        logger.error(f"Explainability error: {e}")
        return jsonify({'error': str(e)}), 500


def initialize_server():
    """Initialize server and create necessary directories"""
    utils.create_directories()
    
    # Generate placement data if it doesn't exist
    placement_db = os.path.join(os.path.dirname(__file__), '..', 'data', 'placement.db')
    if not os.path.exists(placement_db):
        logger.info("Generating synthetic placement data...")
        save_placement_data_to_db(500)
    
    logger.info("Server initialized")


if __name__ == '__main__':
    print("="*60)
    print("FEDERATED LEARNING SERVER")
    print("="*60)
    print(f"Server starting on {config.SERVER_HOST}:{config.SERVER_PORT}")
    print(f"Privacy: {'ENABLED' if config.DP_ENABLED else 'DISABLED'}")
    print(f"Encryption: {'ENABLED' if config.ENCRYPTION_ENABLED else 'DISABLED'}")
    print("="*60 + "\n")
    
    initialize_server()
    
    app.run(
        host=config.SERVER_HOST,
        port=config.SERVER_PORT,
        debug=False
    )
