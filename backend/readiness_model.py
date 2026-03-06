"""
Interview Readiness Model — EduShield AI
Logistic Regression model trained on historical placement data.
Predicts placement probability and readiness score (0–100).
"""

import numpy as np
import logging
import os
import pickle
import sqlite3
from typing import Dict, Any, List, Optional

from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

import config

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# Feature list (order matters)
# ─────────────────────────────────────────────
FEATURES = [
    'gpa',
    'dsa_score',
    'projects',
    'internships',
    'communication_score',
    'coding_score'
]

FEATURE_LABELS = {
    'gpa': 'GPA',
    'dsa_score': 'DSA Score',
    'projects': 'Projects',
    'internships': 'Internships',
    'communication_score': 'Communication',
    'coding_score': 'Coding Score'
}

MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'models', 'readiness_model.pkl')
SCALER_PATH = os.path.join(os.path.dirname(__file__), '..', 'models', 'readiness_scaler.pkl')


class ReadinessModel:
    """
    Logistic Regression model for interview/placement readiness prediction.
    
    Learns from historical placement outcomes:
        P(placement) = sigmoid(w1*gpa + w2*dsa_score + ... + b)
        readiness_score = P(placement) * 100
    """
    
    def __init__(self):
        self.model = LogisticRegression(
            max_iter=1000,
            solver='lbfgs',
            random_state=42,
            C=1.0
        )
        self.scaler = StandardScaler()
        self.is_trained = False
        self._load_model()
    
    def _load_model(self):
        """Try to load a previously trained model from disk"""
        try:
            if os.path.exists(MODEL_PATH) and os.path.exists(SCALER_PATH):
                with open(MODEL_PATH, 'rb') as f:
                    self.model = pickle.load(f)
                with open(SCALER_PATH, 'rb') as f:
                    self.scaler = pickle.load(f)
                self.is_trained = True
                logger.info("Readiness model loaded from disk")
        except Exception as e:
            logger.warning(f"Could not load model: {e}")
            self.is_trained = False
    
    def _save_model(self):
        """Save trained model to disk"""
        os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
        with open(MODEL_PATH, 'wb') as f:
            pickle.dump(self.model, f)
        with open(SCALER_PATH, 'wb') as f:
            pickle.dump(self.scaler, f)
        logger.info("Readiness model saved to disk")
    
    def train(self, X: np.ndarray, y: np.ndarray) -> Dict[str, Any]:
        """
        Train the logistic regression model.
        
        Args:
            X: Feature matrix (n_samples, 6)
            y: Labels (0 = not placed, 1 = placed)
        
        Returns:
            Training metrics
        """
        # Split data
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_val_scaled = self.scaler.transform(X_val)
        
        # Train
        self.model.fit(X_train_scaled, y_train)
        self.is_trained = True
        
        # Evaluate
        train_acc = accuracy_score(y_train, self.model.predict(X_train_scaled))
        val_acc = accuracy_score(y_val, self.model.predict(X_val_scaled))
        val_proba = self.model.predict_proba(X_val_scaled)[:, 1]
        
        # Feature weights (interpretability)
        weights = dict(zip(FEATURES, self.model.coef_[0].tolist()))
        
        # Save model
        self._save_model()
        
        metrics = {
            'train_accuracy': round(train_acc, 4),
            'val_accuracy': round(val_acc, 4),
            'num_samples': len(X),
            'feature_weights': weights,
            'intercept': float(self.model.intercept_[0])
        }
        
        logger.info(f"Readiness model trained: train_acc={train_acc:.4f}, val_acc={val_acc:.4f}")
        
        return metrics
    
    def predict(self, student_profile: Dict[str, float]) -> Dict[str, Any]:
        """
        Predict placement readiness for a single student.
        
        Args:
            student_profile: {
                "gpa": 7.5,
                "dsa_score": 60,
                "projects": 3,
                "internships": 1,
                "communication_score": 70,
                "coding_score": 65
            }
        
        Returns:
            Readiness prediction with score and category
        """
        if not self.is_trained:
            # Auto-train on synthetic data if no model exists
            self._train_on_synthetic()
        
        # Build feature vector
        feature_vector = np.array([[
            student_profile.get(f, 0) for f in FEATURES
        ]])
        
        # Scale and predict
        feature_scaled = self.scaler.transform(feature_vector)
        probability = float(self.model.predict_proba(feature_scaled)[0][1])
        readiness_score = round(probability * 100, 1)
        
        # Categorize
        if readiness_score >= 70:
            category = "Placement Ready"
            color = "#2ed573"
        elif readiness_score >= 40:
            category = "Needs Preparation"
            color = "#ffa502"
        else:
            category = "Not Ready"
            color = "#ff4757"
        
        # Feature contributions (simple weight-based)
        contributions = {}
        if hasattr(self.model, 'coef_'):
            scaled = feature_scaled[0]
            for i, feat in enumerate(FEATURES):
                contrib = float(self.model.coef_[0][i] * scaled[i])
                contributions[feat] = {
                    "value": student_profile.get(feat, 0),
                    "contribution": round(contrib, 4),
                    "label": FEATURE_LABELS.get(feat, feat)
                }
        
        return {
            "placement_probability": round(probability, 4),
            "readiness_score": readiness_score,
            "category": category,
            "category_color": color,
            "contributions": contributions,
            "profile": student_profile
        }
    
    def _train_on_synthetic(self):
        """Auto-train on synthetic placement data if no model exists"""
        logger.info("No trained model found. Training on synthetic data...")
        X, y = generate_synthetic_placement_data(500)
        self.train(X, y)
    
    def get_feature_weights(self) -> Dict[str, float]:
        """Get learned feature weights for interpretability"""
        if not self.is_trained:
            return {}
        return dict(zip(FEATURES, self.model.coef_[0].tolist()))


# ─────────────────────────────────────────────
# Synthetic Data Generator for Placement
# ─────────────────────────────────────────────
def generate_synthetic_placement_data(num_students: int = 500, seed: int = 42):
    """
    Generate synthetic placement dataset for training.
    
    In production, this would come from historical placement records.
    """
    np.random.seed(seed)
    
    X = np.zeros((num_students, len(FEATURES)))
    y = np.zeros(num_students)
    
    for i in range(num_students):
        is_placed = np.random.rand() < 0.55  # 55% placement rate
        
        if is_placed:
            gpa = np.random.uniform(6.5, 9.8)
            dsa_score = np.random.uniform(55, 95)
            projects = np.random.randint(2, 8)
            internships = np.random.randint(1, 4)
            communication = np.random.uniform(60, 95)
            coding = np.random.uniform(55, 90)
        else:
            gpa = np.random.uniform(4.0, 7.5)
            dsa_score = np.random.uniform(20, 65)
            projects = np.random.randint(0, 3)
            internships = np.random.randint(0, 2)
            communication = np.random.uniform(30, 70)
            coding = np.random.uniform(25, 60)
        
        # Add noise
        gpa = np.clip(gpa + np.random.normal(0, 0.3), 0, 10)
        dsa_score = np.clip(dsa_score + np.random.normal(0, 5), 0, 100)
        communication = np.clip(communication + np.random.normal(0, 5), 0, 100)
        coding = np.clip(coding + np.random.normal(0, 5), 0, 100)
        
        X[i] = [gpa, dsa_score, projects, internships, communication, coding]
        y[i] = 1 if is_placed else 0
    
    return X, y


def save_placement_data_to_db(num_students: int = 500):
    """Save synthetic placement data to the central data directory"""
    X, y = generate_synthetic_placement_data(num_students)
    
    db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'placement.db')
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS placement_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            gpa REAL NOT NULL,
            dsa_score REAL NOT NULL,
            projects INTEGER NOT NULL,
            internships INTEGER NOT NULL,
            communication_score REAL NOT NULL,
            coding_score REAL NOT NULL,
            placed INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('DELETE FROM placement_data')  # reset
    
    for i in range(len(X)):
        cursor.execute(
            'INSERT INTO placement_data (student_id, gpa, dsa_score, projects, internships, communication_score, coding_score, placed) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
            (i + 1, float(X[i][0]), float(X[i][1]), int(X[i][2]), int(X[i][3]), float(X[i][4]), float(X[i][5]), int(y[i]))
        )
    
    conn.commit()
    conn.close()
    logger.info(f"Saved {num_students} placement records to {db_path}")


# Singleton instance for the API
_model_instance = None

def get_model() -> ReadinessModel:
    """Get or create the readiness model singleton"""
    global _model_instance
    if _model_instance is None:
        _model_instance = ReadinessModel()
    return _model_instance
