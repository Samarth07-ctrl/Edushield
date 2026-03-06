"""
Configuration settings for Federated Learning Framework
"""

# Server Configuration
SERVER_HOST = '0.0.0.0'
SERVER_PORT = 5000

# Federated Learning Parameters
NUM_ROUNDS = 10
CLIENTS_PER_ROUND = 3
MIN_CLIENTS = 2
LOCAL_EPOCHS = 5
BATCH_SIZE = 32
LEARNING_RATE = 0.01

# Model Architecture
HIDDEN_UNITS = [64, 32, 16]
DROPOUT_RATE = 0.3
ACTIVATION = 'relu'

# Privacy Parameters
DP_ENABLED = True
DP_EPSILON = 1.0
DP_DELTA = 1e-5
CLIP_NORM = 1.0
NOISE_MULTIPLIER = 1.1

# Encryption
ENCRYPTION_ENABLED = True
ENCRYPTION_KEY_SIZE = 32  # 256 bits

# Database
DB_PATH = '../data/clients/'

# Model Storage
MODEL_SAVE_PATH = '../models/'

# Use Cases
USE_CASES = {
    'attendance': {
        'name': 'Attendance Risk Prediction',
        'features': ['attendance_rate', 'absences', 'study_hours', 'participation'],
        'target': 'at_risk',
        'type': 'binary_classification'
    },
    'learning': {
        'name': 'Personalized Learning Recommendation',
        'features': ['math_score', 'science_score', 'english_score', 'time_math', 
                     'time_science', 'time_english', 'assignment_rate', 'quiz_avg'],
        'target': 'weak_subject',
        'type': 'multiclass_classification',
        'classes': ['math', 'science', 'english', 'none']
    }
}

# Data Generation
NUM_STUDENTS_PER_CLIENT = 100
NUM_CLIENTS_DATA = 5

# Training
VALIDATION_SPLIT = 0.2
RANDOM_SEED = 42

# API
API_PREFIX = '/api'
CORS_ORIGINS = ['http://localhost:3000', 'http://localhost:5173', 'http://localhost:5174']

# Logging
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
