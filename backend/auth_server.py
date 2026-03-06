"""
Authentication Server for EduShield AI
Handles student registration, login, and JWT authentication.
Runs separately from the FL server on port 5001.
"""

from flask import Flask, request, jsonify, g
from flask_cors import CORS
import sqlite3
import bcrypt
import jwt
import datetime
import os
import functools
import logging

# ─────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────
AUTH_DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'auth.db')
JWT_SECRET = 'edushield-ai-secret-key-2025'
JWT_ALGORITHM = 'HS256'
JWT_EXPIRY_HOURS = 24
AUTH_PORT = 5001

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('auth_server')

# ─────────────────────────────────────────────
# Flask App
# ─────────────────────────────────────────────
app = Flask(__name__)
CORS(app, origins=['http://localhost:5173', 'http://localhost:5174', 'http://localhost:3000'],
     supports_credentials=True)


# ─────────────────────────────────────────────
# Database Setup
# ─────────────────────────────────────────────
def get_db():
    """Get database connection (per-request)"""
    if 'db' not in g:
        os.makedirs(os.path.dirname(AUTH_DB_PATH), exist_ok=True)
        g.db = sqlite3.connect(AUTH_DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    """Initialize the auth database with students table"""
    os.makedirs(os.path.dirname(AUTH_DB_PATH), exist_ok=True)
    conn = sqlite3.connect(AUTH_DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            department TEXT NOT NULL,
            client_id INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_student_id ON students(student_id)
    ''')
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_email ON students(email)
    ''')
    conn.commit()
    conn.close()
    logger.info(f"Auth database initialized at {AUTH_DB_PATH}")


# ─────────────────────────────────────────────
# JWT Helpers
# ─────────────────────────────────────────────
def create_token(student_id: str, email: str, department: str, client_id: int, name: str) -> str:
    """Create a JWT token for the student"""
    payload = {
        'student_id': student_id,
        'email': email,
        'department': department,
        'client_id': client_id,
        'name': name,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=JWT_EXPIRY_HOURS),
        'iat': datetime.datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    """Decode and verify JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def jwt_required(f):
    """Decorator for JWT-protected routes"""
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        
        if not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Missing or invalid authorization header'}), 401
        
        token = auth_header.split(' ')[1]
        payload = decode_token(token)
        
        if payload is None:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        g.current_user = payload
        return f(*args, **kwargs)
    
    return decorated


# ─────────────────────────────────────────────
# Auth Endpoints
# ─────────────────────────────────────────────

@app.route('/auth/register', methods=['POST'])
def register():
    """
    Register a new student
    
    Request body:
        {
            "student_id": "STU001",
            "name": "John Doe",
            "email": "john@campus.edu",
            "password": "securepass",
            "department": "Computer Science"
        }
    """
    try:
        data = request.json
        
        # Validate required fields
        required = ['student_id', 'name', 'email', 'password', 'department']
        for field in required:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        student_id = data['student_id'].strip()
        name = data['name'].strip()
        email = data['email'].strip().lower()
        password = data['password']
        department = data['department'].strip()
        
        # Map department to client_id (1-5)
        dept_map = {
            'computer science': 1,
            'electronics': 2,
            'mechanical': 3,
            'civil': 4,
            'information technology': 5
        }
        client_id = dept_map.get(department.lower(), 1)
        
        # Hash password
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Insert into DB
        db = get_db()
        try:
            db.execute(
                'INSERT INTO students (student_id, name, email, password_hash, department, client_id) VALUES (?, ?, ?, ?, ?, ?)',
                (student_id, name, email, password_hash, department, client_id)
            )
            db.commit()
        except sqlite3.IntegrityError as e:
            if 'student_id' in str(e):
                return jsonify({'error': 'Student ID already registered'}), 409
            elif 'email' in str(e):
                return jsonify({'error': 'Email already registered'}), 409
            return jsonify({'error': 'Registration failed'}), 409
        
        # Create token
        token = create_token(student_id, email, department, client_id, name)
        
        logger.info(f"Student registered: {student_id} ({department}, client {client_id})")
        
        return jsonify({
            'message': 'Registration successful',
            'token': token,
            'student': {
                'student_id': student_id,
                'name': name,
                'email': email,
                'department': department,
                'client_id': client_id
            }
        }), 201
    
    except Exception as e:
        logger.error(f"Registration error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/auth/login', methods=['POST'])
def login():
    """
    Login with email and password
    
    Request body:
        {
            "email": "john@campus.edu",
            "password": "securepass"
        }
    """
    try:
        data = request.json
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        db = get_db()
        student = db.execute(
            'SELECT * FROM students WHERE email = ?', (email,)
        ).fetchone()
        
        if not student:
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Verify password
        if not bcrypt.checkpw(password.encode('utf-8'), student['password_hash'].encode('utf-8')):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Create token
        token = create_token(
            student['student_id'],
            student['email'],
            student['department'],
            student['client_id'],
            student['name']
        )
        
        logger.info(f"Student logged in: {student['student_id']}")
        
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'student': {
                'student_id': student['student_id'],
                'name': student['name'],
                'email': student['email'],
                'department': student['department'],
                'client_id': student['client_id']
            }
        }), 200
    
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/auth/me', methods=['GET'])
@jwt_required
def get_me():
    """
    Get current authenticated student info
    Requires: Authorization: Bearer <token>
    """
    return jsonify({
        'student_id': g.current_user['student_id'],
        'name': g.current_user['name'],
        'email': g.current_user['email'],
        'department': g.current_user['department'],
        'client_id': g.current_user['client_id']
    }), 200


@app.route('/auth/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({'status': 'ok', 'service': 'auth'}), 200


# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────
if __name__ == '__main__':
    init_db()
    
    print("=" * 60)
    print("  EDUSHIELD AI — AUTHENTICATION SERVER")
    print("=" * 60)
    print(f"  Port: {AUTH_PORT}")
    print(f"  DB:   {os.path.abspath(AUTH_DB_PATH)}")
    print(f"  JWT:  {JWT_EXPIRY_HOURS}h expiry")
    print("=" * 60 + "\n")
    
    app.run(host='0.0.0.0', port=AUTH_PORT, debug=False)
