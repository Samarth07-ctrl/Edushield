"""
Client Prediction API for EduShield AI
Reads from existing client SQLite databases to provide student-level predictions.
Does NOT modify any data or interfere with federated training.
Runs on port 5002.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import numpy as np
import os
import logging
import config

# ─────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────
CLIENT_API_PORT = 5002

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('client_api')

app = Flask(__name__)
CORS(app, origins=['http://localhost:5173', 'http://localhost:5174', 'http://localhost:3000'])


# ─────────────────────────────────────────────
# Database Helpers (read-only from existing DBs)
# ─────────────────────────────────────────────
def get_client_db_path(client_id: int) -> str:
    """Get path to existing client database"""
    return os.path.join(config.DB_PATH, f'client_{client_id}.db')


def query_student_attendance(client_id: int, student_id: int) -> dict:
    """Read attendance data for a specific student from their client's DB"""
    db_path = get_client_db_path(client_id)
    
    if not os.path.exists(db_path):
        return None
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT student_id, attendance_rate, absences, study_hours, participation, at_risk
        FROM attendance_data
        WHERE student_id = ?
    ''', (student_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return dict(row)
    return None


def query_student_learning(client_id: int, student_id: int) -> dict:
    """Read learning data for a specific student from their client's DB"""
    db_path = get_client_db_path(client_id)
    
    if not os.path.exists(db_path):
        return None
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT student_id, math_score, science_score, english_score,
               time_math, time_science, time_english, 
               assignment_rate, quiz_avg, weak_subject
        FROM learning_data
        WHERE student_id = ?
    ''', (student_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return dict(row)
    return None


def get_all_student_ids(client_id: int) -> list:
    """Get all student IDs available in a client's database"""
    db_path = get_client_db_path(client_id)
    
    if not os.path.exists(db_path):
        return []
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    ids = set()
    
    try:
        cursor.execute('SELECT DISTINCT student_id FROM attendance_data')
        ids.update([r[0] for r in cursor.fetchall()])
    except sqlite3.OperationalError:
        pass
    
    try:
        cursor.execute('SELECT DISTINCT student_id FROM learning_data')
        ids.update([r[0] for r in cursor.fetchall()])
    except sqlite3.OperationalError:
        pass
    
    conn.close()
    return sorted(list(ids))


# ─────────────────────────────────────────────
# Risk Prediction (local computation)
# ─────────────────────────────────────────────
def compute_attendance_risk(attendance_data: dict) -> dict:
    """
    Compute attendance risk prediction locally.
    Uses rule-based scoring that mirrors the ML model output.
    Data never leaves this process.
    """
    attendance_rate = attendance_data.get('attendance_rate', 0)
    absences = attendance_data.get('absences', 0)
    study_hours = attendance_data.get('study_hours', 0)
    participation = attendance_data.get('participation', 0)
    
    # Risk score computation (0-100, higher = more at risk)
    risk_score = 0
    
    # Attendance rate factor (most important)
    if attendance_rate < 0.6:
        risk_score += 40
    elif attendance_rate < 0.75:
        risk_score += 25
    elif attendance_rate < 0.85:
        risk_score += 10
    
    # Absences factor
    if absences > 15:
        risk_score += 25
    elif absences > 10:
        risk_score += 15
    elif absences > 5:
        risk_score += 8
    
    # Study hours factor
    if study_hours < 2:
        risk_score += 20
    elif study_hours < 4:
        risk_score += 10
    elif study_hours < 6:
        risk_score += 5
    
    # Participation factor
    if participation < 0.3:
        risk_score += 15
    elif participation < 0.5:
        risk_score += 8
    elif participation < 0.7:
        risk_score += 3
    
    risk_score = min(risk_score, 100)
    
    # Risk level
    if risk_score >= 60:
        risk_level = 'high'
    elif risk_score >= 35:
        risk_level = 'medium'
    else:
        risk_level = 'low'
    
    return {
        'risk_score': risk_score,
        'risk_level': risk_level,
        'at_risk': attendance_data.get('at_risk', 0) == 1,
        'factors': {
            'attendance_rate': round(attendance_rate * 100, 1),
            'absences': absences,
            'study_hours': round(study_hours, 1),
            'participation': round(participation * 100, 1)
        },
        'recommendations': _get_risk_recommendations(risk_level, attendance_rate, study_hours, participation)
    }


def _get_risk_recommendations(risk_level, attendance_rate, study_hours, participation):
    """Generate personalized recommendations based on risk factors"""
    recs = []
    
    if attendance_rate < 0.75:
        recs.append({
            'area': 'Attendance',
            'priority': 'high',
            'suggestion': f'Your attendance is {attendance_rate*100:.0f}%. Aim for at least 85% to stay on track.'
        })
    
    if study_hours < 4:
        recs.append({
            'area': 'Study Hours',
            'priority': 'high' if study_hours < 2 else 'medium',
            'suggestion': f'Increase daily study time from {study_hours:.1f}h to at least 4-5 hours.'
        })
    
    if participation < 0.5:
        recs.append({
            'area': 'Participation',
            'priority': 'medium',
            'suggestion': 'Engage more in class discussions and group activities.'
        })
    
    if risk_level == 'low':
        recs.append({
            'area': 'Keep Going',
            'priority': 'info',
            'suggestion': 'You\'re doing great! Maintain your current habits.'
        })
    
    return recs


# ─────────────────────────────────────────────
# Placement Readiness
# ─────────────────────────────────────────────
def compute_placement_readiness(learning_data: dict, attendance_data: dict = None) -> dict:
    """
    Compute placement readiness score from local data.
    Data stays local — never transmitted.
    """
    math = learning_data.get('math_score', 0)
    science = learning_data.get('science_score', 0)
    english = learning_data.get('english_score', 0)
    assignment_rate = learning_data.get('assignment_rate', 0)
    quiz_avg = learning_data.get('quiz_avg', 0)
    
    # Academic score (40% of total)
    avg_score = (math + science + english) / 3
    academic_pct = min(avg_score / 100, 1.0) * 100
    
    # Assignment completion (20%)
    assignment_pct = min(assignment_rate, 1.0) * 100
    
    # Quiz performance (20%)
    quiz_pct = min(quiz_avg / 100, 1.0) * 100
    
    # Attendance factor (20%)
    attendance_pct = 75  # default
    if attendance_data:
        attendance_pct = min(attendance_data.get('attendance_rate', 0.75), 1.0) * 100
    
    # Weighted total
    readiness_score = (
        academic_pct * 0.40 +
        assignment_pct * 0.20 +
        quiz_pct * 0.20 +
        attendance_pct * 0.20
    )
    
    # Readiness level
    if readiness_score >= 80:
        level = 'excellent'
    elif readiness_score >= 65:
        level = 'good'
    elif readiness_score >= 50:
        level = 'moderate'
    else:
        level = 'needs_improvement'
    
    # Skill breakdown
    skills = {
        'mathematics': {'score': round(math, 1), 'grade': _score_to_grade(math)},
        'science': {'score': round(science, 1), 'grade': _score_to_grade(science)},
        'english': {'score': round(english, 1), 'grade': _score_to_grade(english)},
        'assignments': {'score': round(assignment_rate * 100, 1), 'grade': _score_to_grade(assignment_rate * 100)},
        'quizzes': {'score': round(quiz_avg, 1), 'grade': _score_to_grade(quiz_avg)},
    }
    
    return {
        'readiness_score': round(readiness_score, 1),
        'level': level,
        'breakdown': {
            'academic': round(academic_pct, 1),
            'assignments': round(assignment_pct, 1),
            'quizzes': round(quiz_pct, 1),
            'attendance': round(attendance_pct, 1)
        },
        'skills': skills,
        'weak_subject': learning_data.get('weak_subject', 'none')
    }


def _score_to_grade(score):
    if score >= 90: return 'A+'
    if score >= 80: return 'A'
    if score >= 70: return 'B'
    if score >= 60: return 'C'
    if score >= 50: return 'D'
    return 'F'


# ─────────────────────────────────────────────
# Study Planner
# ─────────────────────────────────────────────
def generate_study_plan(learning_data: dict, attendance_data: dict = None) -> dict:
    """Generate a personalized study plan from local data"""
    math = learning_data.get('math_score', 50)
    science = learning_data.get('science_score', 50)
    english = learning_data.get('english_score', 50)
    time_math = learning_data.get('time_math', 2)
    time_science = learning_data.get('time_science', 2)
    time_english = learning_data.get('time_english', 2)
    weak = learning_data.get('weak_subject', 'none')
    
    total_study_time = time_math + time_science + time_english
    
    # Build schedule recommendations
    subjects = [
        {'name': 'Mathematics', 'score': math, 'current_hours': time_math},
        {'name': 'Science', 'score': science, 'current_hours': time_science},
        {'name': 'English', 'score': english, 'current_hours': time_english},
    ]
    
    # Sort by weakest first
    subjects.sort(key=lambda s: s['score'])
    
    plan = []
    for subj in subjects:
        if subj['score'] < 50:
            recommended_hours = max(subj['current_hours'] + 2, 4)
            priority = 'critical'
        elif subj['score'] < 70:
            recommended_hours = max(subj['current_hours'] + 1, 3)
            priority = 'high'
        elif subj['score'] < 85:
            recommended_hours = max(subj['current_hours'], 2)
            priority = 'medium'
        else:
            recommended_hours = max(subj['current_hours'] - 0.5, 1)
            priority = 'maintain'
        
        plan.append({
            'subject': subj['name'],
            'current_score': round(subj['score'], 1),
            'current_hours': round(subj['current_hours'], 1),
            'recommended_hours': round(recommended_hours, 1),
            'priority': priority,
            'tips': _get_study_tips(subj['name'], subj['score'])
        })
    
    return {
        'weekly_plan': plan,
        'total_current_hours': round(total_study_time, 1),
        'total_recommended_hours': round(sum(p['recommended_hours'] for p in plan), 1),
        'focus_area': weak if weak != 'none' else subjects[0]['name'].lower()
    }


def _get_study_tips(subject, score):
    tips = {
        'Mathematics': [
            'Practice problem-solving daily',
            'Focus on understanding concepts, not memorization',
            'Use online resources like Khan Academy'
        ],
        'Science': [
            'Review lab experiments and observations',
            'Create concept maps linking topics',
            'Practice with past exam questions'
        ],
        'English': [
            'Read diverse texts daily for 30 minutes',
            'Practice writing essays regularly',
            'Build vocabulary with flashcards'
        ]
    }
    
    if score < 50:
        return tips.get(subject, ['Focus on fundamentals'])[:3]
    elif score < 70:
        return tips.get(subject, ['Practice regularly'])[:2]
    return [tips.get(subject, ['Keep it up'])[0]]


# ─────────────────────────────────────────────
# API Endpoints
# ─────────────────────────────────────────────

@app.route('/api/student/attendance', methods=['GET'])
def get_student_attendance():
    """Get attendance data for a student"""
    client_id = request.args.get('client_id', type=int)
    student_id = request.args.get('student_id', type=int)
    
    if not client_id or not student_id:
        return jsonify({'error': 'client_id and student_id are required'}), 400
    
    data = query_student_attendance(client_id, student_id)
    if not data:
        return jsonify({'error': 'No attendance data found', 'data': None}), 404
    
    return jsonify({'data': data}), 200


@app.route('/api/student/marks', methods=['GET'])
def get_student_marks():
    """Get marks/learning data for a student"""
    client_id = request.args.get('client_id', type=int)
    student_id = request.args.get('student_id', type=int)
    
    if not client_id or not student_id:
        return jsonify({'error': 'client_id and student_id are required'}), 400
    
    data = query_student_learning(client_id, student_id)
    if not data:
        return jsonify({'error': 'No learning data found', 'data': None}), 404
    
    return jsonify({'data': data}), 200


@app.route('/predict-risk', methods=['GET'])
def predict_risk():
    """
    GET /predict-risk?client_id=1&student_id=5
    Predicts attendance risk from local data. No raw data sent to server.
    """
    client_id = request.args.get('client_id', type=int)
    student_id = request.args.get('student_id', type=int)
    
    if not client_id or not student_id:
        return jsonify({'error': 'client_id and student_id required'}), 400
    
    attendance = query_student_attendance(client_id, student_id)
    if not attendance:
        return jsonify({'error': 'Student data not found'}), 404
    
    prediction = compute_attendance_risk(attendance)
    prediction['student_id'] = student_id
    prediction['client_id'] = client_id
    
    logger.info(f"Risk prediction for student {student_id}: {prediction['risk_level']}")
    
    return jsonify(prediction), 200


@app.route('/placement-readiness', methods=['GET'])
def placement_readiness():
    """
    GET /placement-readiness?client_id=1&student_id=5
    Computes placement readiness from local data only.
    """
    client_id = request.args.get('client_id', type=int)
    student_id = request.args.get('student_id', type=int)
    
    if not client_id or not student_id:
        return jsonify({'error': 'client_id and student_id required'}), 400
    
    learning = query_student_learning(client_id, student_id)
    attendance = query_student_attendance(client_id, student_id)
    
    if not learning:
        return jsonify({'error': 'Student learning data not found'}), 404
    
    readiness = compute_placement_readiness(learning, attendance)
    readiness['student_id'] = student_id
    
    return jsonify(readiness), 200


@app.route('/api/student/study-plan', methods=['GET'])
def study_plan():
    """Generate personalized study plan from local data"""
    client_id = request.args.get('client_id', type=int)
    student_id = request.args.get('student_id', type=int)
    
    if not client_id or not student_id:
        return jsonify({'error': 'client_id and student_id required'}), 400
    
    learning = query_student_learning(client_id, student_id)
    attendance = query_student_attendance(client_id, student_id)
    
    if not learning:
        return jsonify({'error': 'Student data not found'}), 404
    
    plan = generate_study_plan(learning, attendance)
    plan['student_id'] = student_id
    
    return jsonify(plan), 200


@app.route('/api/student/ids', methods=['GET'])
def get_student_ids():
    """Get available student IDs for a client"""
    client_id = request.args.get('client_id', type=int, default=1)
    ids = get_all_student_ids(client_id)
    return jsonify({'client_id': client_id, 'student_ids': ids, 'count': len(ids)}), 200


@app.route('/train-local', methods=['POST'])
def train_local():
    """
    POST /train-local
    Triggers local model training. This is read-only from the student perspective.
    Actual training is handled by the federated client process.
    """
    return jsonify({
        'message': 'Local training is managed by the federated client process',
        'info': 'Use the admin dashboard to start federated training'
    }), 200


@app.route('/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({'status': 'ok', 'service': 'client_api'}), 200


# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────
if __name__ == '__main__':
    print("=" * 60)
    print("  EDUSHIELD AI — CLIENT PREDICTION API")
    print("=" * 60)
    print(f"  Port: {CLIENT_API_PORT}")
    print(f"  Client DBs: {os.path.abspath(config.DB_PATH)}")
    print("  Endpoints:")
    print("    GET  /predict-risk?client_id=X&student_id=Y")
    print("    GET  /placement-readiness?client_id=X&student_id=Y")
    print("    GET  /api/student/attendance?client_id=X&student_id=Y")
    print("    GET  /api/student/marks?client_id=X&student_id=Y")
    print("    GET  /api/student/study-plan?client_id=X&student_id=Y")
    print("    GET  /api/student/ids?client_id=X")
    print("    POST /train-local")
    print("=" * 60 + "\n")
    
    app.run(host='0.0.0.0', port=CLIENT_API_PORT, debug=False)
