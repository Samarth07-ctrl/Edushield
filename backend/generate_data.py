"""
Sample Dataset Generator for Smart Campus Applications
Generates realistic simulated data for both use cases
"""

import numpy as np
import pandas as pd
import os
import logging
from typing import List, Dict, Any
import config
from database import ClientDatabase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataGenerator:
    """
    Generates synthetic campus data for federated learning
    """
    
    def __init__(self, seed: int = None):
        """
        Initialize data generator
        
        Args:
            seed: Random seed for reproducibility
        """
        self.seed = seed or config.RANDOM_SEED
        np.random.seed(self.seed)
        logger.info(f"Data generator initialized with seed={self.seed}")
    
    def generate_attendance_data(self, num_students: int) -> List[Dict[str, Any]]:
        """
        Generate attendance risk prediction data
        
        Features:
        - attendance_rate: 0-1 (percentage of classes attended)
        - absences: 0-30 (number of absences)
        - study_hours: 0-40 (hours per week)
        - participation: 0-1 (participation score)
        
        Target:
        - at_risk: 0 or 1 (whether student is at risk)
        
        Args:
            num_students: Number of student records to generate
        
        Returns:
            List of student records
        """
        data = []
        
        for student_id in range(1, num_students + 1):
            # Generate correlated features
            # Good students: high attendance, low absences, high study hours
            # At-risk students: opposite pattern
            
            is_at_risk = np.random.rand() < 0.3  # 30% at risk
            
            if is_at_risk:
                # At-risk student pattern
                attendance_rate = np.random.uniform(0.4, 0.7)
                absences = int(np.random.uniform(10, 25))
                study_hours = np.random.uniform(5, 15)
                participation = np.random.uniform(0.3, 0.6)
            else:
                # Good student pattern
                attendance_rate = np.random.uniform(0.75, 0.98)
                absences = int(np.random.uniform(0, 8))
                study_hours = np.random.uniform(15, 35)
                participation = np.random.uniform(0.65, 0.95)
            
            # Add some noise
            attendance_rate += np.random.normal(0, 0.05)
            study_hours += np.random.normal(0, 2)
            participation += np.random.normal(0, 0.05)
            
            # Clip values to valid ranges
            attendance_rate = np.clip(attendance_rate, 0, 1)
            study_hours = np.clip(study_hours, 0, 40)
            participation = np.clip(participation, 0, 1)
            
            record = {
                'student_id': student_id,
                'attendance_rate': float(attendance_rate),
                'absences': int(absences),
                'study_hours': float(study_hours),
                'participation': float(participation),
                'at_risk': int(is_at_risk)
            }
            
            data.append(record)
        
        logger.info(f"Generated {num_students} attendance records")
        return data
    
    def generate_learning_data(self, num_students: int) -> List[Dict[str, Any]]:
        """
        Generate personalized learning recommendation data
        
        Features:
        - math_score, science_score, english_score: 0-100
        - time_math, time_science, time_english: hours per week
        - assignment_rate: 0-1 (completion rate)
        - quiz_avg: 0-100 (average quiz score)
        
        Target:
        - weak_subject: 'math', 'science', 'english', or 'none'
        
        Args:
            num_students: Number of student records to generate
        
        Returns:
            List of student records
        """
        data = []
        subjects = ['math', 'science', 'english']
        
        for student_id in range(1, num_students + 1):
            # Generate base ability
            base_ability = np.random.uniform(50, 90)
            
            # Generate scores with one potentially weak subject
            weak_subject_idx = np.random.choice([0, 1, 2, 3])  # 3 = none
            
            scores = []
            times = []
            
            for i, subject in enumerate(subjects):
                if i == weak_subject_idx:
                    # Weak subject: lower score, less time
                    score = base_ability - np.random.uniform(15, 30)
                    time = np.random.uniform(2, 6)
                else:
                    # Strong subject: higher score, more time
                    score = base_ability + np.random.uniform(-10, 15)
                    time = np.random.uniform(5, 12)
                
                scores.append(np.clip(score, 0, 100))
                times.append(time)
            
            # Assignment completion rate
            assignment_rate = np.random.uniform(0.6, 0.98)
            
            # Quiz average (correlated with overall performance)
            quiz_avg = np.mean(scores) + np.random.normal(0, 5)
            quiz_avg = np.clip(quiz_avg, 0, 100)
            
            # Determine weak subject
            if weak_subject_idx < 3:
                weak_subject = subjects[weak_subject_idx]
            else:
                weak_subject = 'none'
            
            record = {
                'student_id': student_id,
                'math_score': float(scores[0]),
                'science_score': float(scores[1]),
                'english_score': float(scores[2]),
                'time_math': float(times[0]),
                'time_science': float(times[1]),
                'time_english': float(times[2]),
                'assignment_rate': float(assignment_rate),
                'quiz_avg': float(quiz_avg),
                'weak_subject': weak_subject
            }
            
            data.append(record)
        
        logger.info(f"Generated {num_students} learning records")
        return data
    
    def save_to_csv(self, data: List[Dict[str, Any]], filename: str):
        """
        Save data to CSV file
        
        Args:
            data: List of records
            filename: Output filename
        """
        df = pd.DataFrame(data)
        filepath = os.path.join('../data', filename)
        df.to_csv(filepath, index=False)
        logger.info(f"Data saved to {filepath}")
    
    def distribute_to_clients(self, data: List[Dict[str, Any]], 
                             num_clients: int, use_case: str):
        """
        Distribute data across multiple clients (non-IID distribution)
        
        Args:
            data: Complete dataset
            num_clients: Number of clients
            use_case: 'attendance' or 'learning'
        """
        # Shuffle data
        np.random.shuffle(data)
        
        # Split data with varying sizes (non-IID)
        split_sizes = np.random.dirichlet(np.ones(num_clients)) * len(data)
        split_sizes = split_sizes.astype(int)
        
        # Ensure all data is distributed
        split_sizes[-1] = len(data) - sum(split_sizes[:-1])
        
        start_idx = 0
        for client_id in range(1, num_clients + 1):
            end_idx = start_idx + split_sizes[client_id - 1]
            client_data = data[start_idx:end_idx]
            
            # Save to client database
            db = ClientDatabase(client_id)
            db.create_tables(use_case)
            
            if use_case == 'attendance':
                db.insert_attendance_data(client_data)
            else:
                db.insert_learning_data(client_data)
            
            logger.info(f"Client {client_id}: {len(client_data)} samples")
            
            start_idx = end_idx


def generate_all_data():
    """
    Generate data for all use cases and distribute to clients.
    
    IMPORTANT: Each student gets BOTH attendance and learning data
    on the SAME client, so the student dashboard can find all data.
    """
    logger.info("Starting data generation...")
    
    # Create data directory
    os.makedirs('../data', exist_ok=True)
    os.makedirs('../data/clients', exist_ok=True)
    
    generator = DataGenerator()
    
    total_students = config.NUM_STUDENTS_PER_CLIENT * config.NUM_CLIENTS_DATA
    num_clients = config.NUM_CLIENTS_DATA
    
    # ─── Step 1: Generate ALL data (same student_ids) ───
    logger.info("\n=== Generating Attendance Risk Data ===")
    attendance_data = generator.generate_attendance_data(total_students)
    generator.save_to_csv(attendance_data, 'attendance_data.csv')
    
    logger.info("\n=== Generating Learning Recommendation Data ===")
    learning_data = generator.generate_learning_data(total_students)
    generator.save_to_csv(learning_data, 'learning_data.csv')
    
    # ─── Step 2: Assign students to clients (ONCE, deterministic) ───
    # Use a fixed seed so distribution is reproducible
    rng = np.random.RandomState(42)
    
    # Create mapping: student_id → client_id
    student_ids = list(range(1, total_students + 1))
    rng.shuffle(student_ids)
    
    # Split with Dirichlet for non-IID sizes
    split_sizes = rng.dirichlet(np.ones(num_clients)) * total_students
    split_sizes = split_sizes.astype(int)
    split_sizes[-1] = total_students - sum(split_sizes[:-1])
    
    student_to_client = {}
    start_idx = 0
    for client_id in range(1, num_clients + 1):
        end_idx = start_idx + split_sizes[client_id - 1]
        for sid in student_ids[start_idx:end_idx]:
            student_to_client[sid] = client_id
        start_idx = end_idx
    
    # ─── Step 3: Build per-client data buckets ───
    client_attendance = {c: [] for c in range(1, num_clients + 1)}
    client_learning = {c: [] for c in range(1, num_clients + 1)}
    
    # Index data by student_id
    att_by_id = {rec['student_id']: rec for rec in attendance_data}
    learn_by_id = {rec['student_id']: rec for rec in learning_data}
    
    for sid, cid in student_to_client.items():
        if sid in att_by_id:
            client_attendance[cid].append(att_by_id[sid])
        if sid in learn_by_id:
            client_learning[cid].append(learn_by_id[sid])
    
    # ─── Step 4: Write to client databases ───
    for client_id in range(1, num_clients + 1):
        db = ClientDatabase(client_id)
        
        # Attendance
        db.create_tables('attendance')
        db.clear_data('attendance')
        db.insert_attendance_data(client_attendance[client_id])
        
        # Learning
        db.create_tables('learning')
        db.clear_data('learning')
        db.insert_learning_data(client_learning[client_id])
        
        logger.info(f"Client {client_id}: {len(client_attendance[client_id])} attendance + "
                    f"{len(client_learning[client_id])} learning samples")
    
    logger.info("\n=== Data Generation Complete ===")
    logger.info(f"Total students: {total_students}")
    logger.info(f"Number of clients: {num_clients}")
    logger.info(f"Each student has BOTH attendance + learning data on same client")
    logger.info(f"Data saved to: ../data/")
    logger.info(f"Client databases: ../data/clients/")


def print_data_summary():
    """
    Print summary of generated data
    """
    print("\n" + "="*60)
    print("DATA GENERATION SUMMARY")
    print("="*60)
    
    for client_id in range(1, config.NUM_CLIENTS_DATA + 1):
        db = ClientDatabase(client_id)
        
        # Attendance data
        attendance_count = db.get_data_count('attendance')
        attendance_stats = db.get_statistics('attendance')
        
        # Learning data
        learning_count = db.get_data_count('learning')
        learning_stats = db.get_statistics('learning')
        
        print(f"\nClient {client_id}:")
        print(f"  Attendance samples: {attendance_count}")
        if attendance_stats:
            print(f"  At-risk distribution: {attendance_stats['label_distribution']}")
        
        print(f"  Learning samples: {learning_count}")
        if learning_stats:
            print(f"  Weak subject distribution: {learning_stats['label_distribution']}")
    
    print("="*60 + "\n")


if __name__ == "__main__":
    print("="*60)
    print("SMART CAMPUS DATA GENERATOR")
    print("="*60)
    
    # Generate all data
    generate_all_data()
    
    # Print summary
    print_data_summary()
    
    print("\nData generation completed successfully!")
    print("You can now start the federated learning server and clients.")
