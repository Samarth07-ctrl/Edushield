"""
SQLite Database Handler for Client-Side Data Storage
Each client maintains their own local database
"""

import sqlite3
import os
import logging
import pandas as pd
import numpy as np
from typing import List, Tuple, Dict, Any
import config

logger = logging.getLogger(__name__)


class ClientDatabase:
    """
    Manages local SQLite database for each client
    """
    
    def __init__(self, client_id: int):
        """
        Initialize database for a specific client
        
        Args:
            client_id: Unique client identifier
        """
        self.client_id = client_id
        self.db_path = os.path.join(config.DB_PATH, f'client_{client_id}.db')
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        self.conn = None
        self.cursor = None
        
        logger.info(f"Database initialized for client {client_id}: {self.db_path}")
    
    def connect(self):
        """Establish database connection"""
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        logger.debug(f"Connected to database: {self.db_path}")
    
    def disconnect(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.debug(f"Disconnected from database: {self.db_path}")
    
    def create_tables(self, use_case: str):
        """
        Create tables for specific use case
        
        Args:
            use_case: 'attendance' or 'learning'
        """
        self.connect()
        
        if use_case == 'attendance':
            self._create_attendance_table()
        elif use_case == 'learning':
            self._create_learning_table()
        else:
            raise ValueError(f"Unknown use case: {use_case}")
        
        self.conn.commit()
        self.disconnect()
        
        logger.info(f"Tables created for use case: {use_case}")
    
    def _create_attendance_table(self):
        """Create table for attendance risk prediction"""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS attendance_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                attendance_rate REAL NOT NULL,
                absences INTEGER NOT NULL,
                study_hours REAL NOT NULL,
                participation REAL NOT NULL,
                at_risk INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create index for faster queries
        self.cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_student_id 
            ON attendance_data(student_id)
        ''')
    
    def _create_learning_table(self):
        """Create table for learning recommendation"""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS learning_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                math_score REAL NOT NULL,
                science_score REAL NOT NULL,
                english_score REAL NOT NULL,
                time_math REAL NOT NULL,
                time_science REAL NOT NULL,
                time_english REAL NOT NULL,
                assignment_rate REAL NOT NULL,
                quiz_avg REAL NOT NULL,
                weak_subject TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_student_id_learning 
            ON learning_data(student_id)
        ''')
    
    def insert_attendance_data(self, data: List[Dict[str, Any]]):
        """
        Insert attendance data
        
        Args:
            data: List of attendance records
        """
        self.connect()
        
        for record in data:
            self.cursor.execute('''
                INSERT INTO attendance_data 
                (student_id, attendance_rate, absences, study_hours, participation, at_risk)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                record['student_id'],
                record['attendance_rate'],
                record['absences'],
                record['study_hours'],
                record['participation'],
                record['at_risk']
            ))
        
        self.conn.commit()
        self.disconnect()
        
        logger.info(f"Inserted {len(data)} attendance records")
    
    def insert_learning_data(self, data: List[Dict[str, Any]]):
        """
        Insert learning data
        
        Args:
            data: List of learning records
        """
        self.connect()
        
        for record in data:
            self.cursor.execute('''
                INSERT INTO learning_data 
                (student_id, math_score, science_score, english_score, 
                 time_math, time_science, time_english, assignment_rate, 
                 quiz_avg, weak_subject)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                record['student_id'],
                record['math_score'],
                record['science_score'],
                record['english_score'],
                record['time_math'],
                record['time_science'],
                record['time_english'],
                record['assignment_rate'],
                record['quiz_avg'],
                record['weak_subject']
            ))
        
        self.conn.commit()
        self.disconnect()
        
        logger.info(f"Inserted {len(data)} learning records")
    
    def get_attendance_data(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Retrieve attendance data as features and labels
        
        Returns:
            Tuple of (features, labels)
        """
        self.connect()
        
        self.cursor.execute('''
            SELECT attendance_rate, absences, study_hours, participation, at_risk
            FROM attendance_data
        ''')
        
        rows = self.cursor.fetchall()
        self.disconnect()
        
        if not rows:
            return np.array([]), np.array([])
        
        data = np.array(rows)
        X = data[:, :-1]  # Features
        y = data[:, -1]   # Labels
        
        logger.info(f"Retrieved {len(X)} attendance samples")
        
        return X, y
    
    def get_learning_data(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Retrieve learning data as features and labels
        
        Returns:
            Tuple of (features, labels)
        """
        self.connect()
        
        self.cursor.execute('''
            SELECT math_score, science_score, english_score, 
                   time_math, time_science, time_english, 
                   assignment_rate, quiz_avg, weak_subject
            FROM learning_data
        ''')
        
        rows = self.cursor.fetchall()
        self.disconnect()
        
        if not rows:
            return np.array([]), np.array([])
        
        # Convert to numpy array
        features = []
        labels = []
        
        for row in rows:
            features.append(row[:-1])
            labels.append(row[-1])
        
        X = np.array(features, dtype=np.float32)
        
        # Convert string labels to integers
        label_map = {'math': 0, 'science': 1, 'english': 2, 'none': 3}
        y = np.array([label_map[label] for label in labels])
        
        logger.info(f"Retrieved {len(X)} learning samples")
        
        return X, y
    
    def get_data_count(self, use_case: str) -> int:
        """
        Get number of records in database
        
        Args:
            use_case: 'attendance' or 'learning'
        
        Returns:
            Number of records
        """
        self.connect()
        
        table_name = f'{use_case}_data'
        self.cursor.execute(f'SELECT COUNT(*) FROM {table_name}')
        count = self.cursor.fetchone()[0]
        
        self.disconnect()
        
        return count
    
    def clear_data(self, use_case: str):
        """
        Clear all data from table
        
        Args:
            use_case: 'attendance' or 'learning'
        """
        self.connect()
        
        table_name = f'{use_case}_data'
        self.cursor.execute(f'DELETE FROM {table_name}')
        
        self.conn.commit()
        self.disconnect()
        
        logger.info(f"Cleared all data from {table_name}")
    
    def get_statistics(self, use_case: str) -> Dict[str, Any]:
        """
        Get statistical summary of data
        
        Args:
            use_case: 'attendance' or 'learning'
        
        Returns:
            Dictionary of statistics
        """
        if use_case == 'attendance':
            X, y = self.get_attendance_data()
            feature_names = ['attendance_rate', 'absences', 'study_hours', 'participation']
        else:
            X, y = self.get_learning_data()
            feature_names = ['math_score', 'science_score', 'english_score', 
                           'time_math', 'time_science', 'time_english', 
                           'assignment_rate', 'quiz_avg']
        
        if len(X) == 0:
            return {}
        
        stats = {
            'num_samples': len(X),
            'num_features': X.shape[1],
            'feature_means': {name: float(X[:, i].mean()) 
                            for i, name in enumerate(feature_names)},
            'feature_stds': {name: float(X[:, i].std()) 
                           for i, name in enumerate(feature_names)},
            'label_distribution': {
                int(label): int(np.sum(y == label)) 
                for label in np.unique(y)
            }
        }
        
        return stats


def create_all_client_databases(num_clients: int, use_case: str):
    """
    Create databases for all clients
    
    Args:
        num_clients: Number of clients
        use_case: 'attendance' or 'learning'
    """
    for client_id in range(1, num_clients + 1):
        db = ClientDatabase(client_id)
        db.create_tables(use_case)
    
    logger.info(f"Created databases for {num_clients} clients")


if __name__ == "__main__":
    # Test database operations
    print("Testing Database Module...")
    
    # Create test database
    db = ClientDatabase(client_id=999)
    db.create_tables('attendance')
    
    # Insert test data
    test_data = [
        {
            'student_id': 1,
            'attendance_rate': 0.85,
            'absences': 5,
            'study_hours': 20.0,
            'participation': 0.75,
            'at_risk': 0
        },
        {
            'student_id': 2,
            'attendance_rate': 0.60,
            'absences': 15,
            'study_hours': 10.0,
            'participation': 0.50,
            'at_risk': 1
        }
    ]
    
    db.insert_attendance_data(test_data)
    
    # Retrieve data
    X, y = db.get_attendance_data()
    print(f"Retrieved {len(X)} samples")
    print(f"Features shape: {X.shape}")
    print(f"Labels shape: {y.shape}")
    
    # Get statistics
    stats = db.get_statistics('attendance')
    print(f"Statistics: {stats}")
    
    # Clean up
    db.clear_data('attendance')
    
    print("\nDatabase module test completed!")
