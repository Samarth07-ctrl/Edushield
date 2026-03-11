# Privacy-Preserving Federated Learning Framework for Smart Campus Applications

## 🎯 Project Overview

A complete full-stack demonstration of Federated Learning for smart campus use cases that preserves student privacy by training machine learning models locally on student devices and only sharing encrypted model updates with a central server.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     React Frontend                          │
│  (Dashboard, Client Simulator, Analytics, Comparison)       │
└─────────────────────┬───────────────────────────────────────┘
                      │ REST API
┌─────────────────────▼───────────────────────────────────────┐
│              Flask Backend Server                           │
│  (Federated Aggregation, Privacy Layer, API Endpoints)      │
└─────────────────────┬───────────────────────────────────────┘
                      │ Model Updates (Encrypted)
┌─────────────────────▼───────────────────────────────────────┐
│           Multiple Client Nodes (Simulated)                 │
│  (Local Training, SQLite Storage, Privacy Protection)       │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Features

### Core Modules

1. **Federated Learning Server**
   - Central aggregation using FedAvg algorithm
   - Handles encrypted model weights
   - No raw student data storage
   - Multi-round training coordination

2. **Client Nodes (Simulated)**
   - Local SQLite database per client
   - Local model training
   - Privacy-preserving weight transmission
   - Differential privacy implementation

3. **Privacy Preservation**
   - Differential Privacy (DP) noise addition
   - Secure aggregation
   - Encrypted weight transmission
   - Zero personal data transfer

4. **Smart Campus Use Cases**
   - **Use Case A**: Attendance Risk Prediction
   - **Use Case B**: Personalized Learning Recommendation

5. **Comparison Module**
   - Centralized vs Federated training
   - Accuracy comparison
   - Privacy metrics
   - Communication cost analysis

6. **React Dashboard**
   - Real-time training visualization
   - Client management
   - Performance metrics
   - Privacy status monitoring

## 📁 Project Structure

```
federated-learning-campus/
├── backend/
│   ├── server.py                 # Federated aggregation server
│   ├── client.py                 # Client node implementation
│   ├── model.py                  # ML models for both use cases
│   ├── privacy.py                # Differential privacy module
│   ├── api.py                    # REST API endpoints
│   ├── database.py               # SQLite database handling
│   ├── generate_data.py          # Sample dataset generator
│   ├── centralized_trainer.py    # Centralized model for comparison
│   ├── config.py                 # Configuration settings
│   ├── utils.py                  # Utility functions
│   └── requirements.txt          # Python dependencies
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Dashboard.jsx
│   │   │   ├── ClientSimulator.jsx
│   │   │   ├── TrainingControl.jsx
│   │   │   ├── Visualization.jsx
│   │   │   ├── Comparison.jsx
│   │   │   └── Login.jsx
│   │   ├── services/
│   │   │   └── api.js
│   │   ├── App.jsx
│   │   ├── App.css
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
├── data/                         # Generated datasets (auto-created)
├── models/                       # Saved models (auto-created)
└── README.md
```

## 🛠️ Technology Stack

### Backend
- **Python 3.8+**
- **Flask** - Web framework
- **TensorFlow 2.x** - Deep learning
- **NumPy** - Numerical computing
- **SQLite** - Local storage
- **Flask-CORS** - Cross-origin support
- **Cryptography** - Encryption

### Frontend
- **React 18**
- **Vite** - Build tool
- **Axios** - HTTP client
- **Recharts** - Data visualization
- **React Router** - Navigation
- **Tailwind CSS** - Styling

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- Node.js 16 or higher
- npm or yarn

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
```

3. Activate virtual environment:
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Generate sample data:
```bash
python generate_data.py
```

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

## 🎮 Running the Application

### Step 1: Start the Backend Server

```bash
cd backend
python server.py
```

Server will start at `http://localhost:5000`

### Step 2: Start Client Nodes (Multiple Terminals)

Open separate terminals for each client:

```bash
# Terminal 1 - Client 1
cd backend
python client.py --client-id 1 --port 5001

# Terminal 2 - Client 2
cd backend
python client.py --client-id 2 --port 5002

# Terminal 3 - Client 3
cd backend
python client.py --client-id 3 --port 5003
```

### Step 3: Start Frontend

```bash
cd frontend
npm run dev
```

Frontend will start at `http://localhost:5173`

### Step 4: Access Dashboard

Open browser and navigate to `http://localhost:5173`

Default credentials:
- Username: `admin`
- Password: `admin123`

## 🎯 Usage Guide

### 1. Dashboard Overview
- View connected clients
- Monitor training status
- Check privacy metrics

### 2. Start Federated Training

1. Go to "Training Control" panel
2. Select use case (Attendance Risk or Learning Recommendation)
3. Set number of rounds (e.g., 10)
4. Click "Start Federated Training"
5. Watch real-time updates

### 3. View Results

- **Accuracy Graph**: Model performance over rounds
- **Loss Graph**: Training loss progression
- **Client Participation**: Active clients per round
- **Privacy Metrics**: DP epsilon values

### 4. Compare with Centralized

1. Navigate to "Comparison" tab
2. Click "Train Centralized Model"
3. View side-by-side comparison:
   - Accuracy difference
   - Privacy score
   - Communication cost
   - Training time

## 📊 API Endpoints

### Server Endpoints

```
POST   /api/register-client          # Register new client
POST   /api/federated/start           # Start federated training
GET    /api/federated/status          # Get training status
POST   /api/federated/upload-weights  # Upload model weights
GET    /api/federated/global-model    # Download global model
GET    /api/metrics                   # Get training metrics
POST   /api/centralized/train         # Train centralized model
GET    /api/comparison                # Get comparison results
```

### Example API Request

```bash
# Start federated training
curl -X POST http://localhost:5000/api/federated/start \
  -H "Content-Type: application/json" \
  -d '{
    "use_case": "attendance",
    "num_rounds": 10,
    "num_clients": 3
  }'
```

## 🔒 Privacy Features

### Differential Privacy
- Gaussian noise addition to gradients
- Configurable epsilon (ε = 1.0 default)
- Delta (δ = 1e-5)
- Gradient clipping (C = 1.0)

### Secure Aggregation
- Model weights encrypted before transmission
- AES-256 encryption
- No raw data leaves client devices

### Privacy Metrics
- Privacy budget tracking
- Epsilon consumption per round
- Privacy vs Accuracy trade-off visualization

## 🧪 Use Cases

### Use Case A: Attendance Risk Prediction

**Objective**: Predict students at risk of low attendance

**Features**:
- Past attendance percentage
- Number of absences
- Study hours per week
- Participation score

**Model**: Binary classification (Risk/No Risk)

**Local Training**: Each student's device trains on their own data

### Use Case B: Personalized Learning Recommendation

**Objective**: Identify weak subjects and recommend focus areas

**Features**:
- Subject-wise marks
- Time spent per subject
- Assignment completion rate
- Quiz scores

**Local Training**: Personalized recommendations without sharing grades

## 📈 Performance Metrics

### Training Metrics
- **Accuracy**: Model prediction accuracy
- **Loss**: Cross-entropy loss
- **F1 Score**: Balanced performance metric
- **Convergence**: Rounds to convergence

### Privacy Metrics
- **Epsilon (ε)**: Privacy budget
- **Delta (δ)**: Privacy guarantee
- **Noise Scale**: DP noise magnitude

### Communication Metrics
- **Bytes Transferred**: Total data sent
- **Rounds**: Number of communication rounds
- **Clients per Round**: Participation rate

## 🔧 Configuration

Edit `backend/config.py` to customize:

```python
# Federated Learning
NUM_ROUNDS = 10
CLIENTS_PER_ROUND = 3
LOCAL_EPOCHS = 5
BATCH_SIZE = 32
LEARNING_RATE = 0.01

# Privacy
DP_EPSILON = 1.0
DP_DELTA = 1e-5
CLIP_NORM = 1.0

# Model
HIDDEN_UNITS = [64, 32]
DROPOUT_RATE = 0.3
```

## 🐛 Troubleshooting

### Backend Issues

**Issue**: `ModuleNotFoundError`
```bash
# Solution: Reinstall dependencies
pip install -r requirements.txt
```

**Issue**: Port already in use
```bash
# Solution: Change port in server.py or kill process
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:5000 | xargs kill -9
```

### Frontend Issues

**Issue**: `npm install` fails
```bash
# Solution: Clear cache and reinstall
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

**Issue**: CORS errors
```bash
# Solution: Ensure Flask-CORS is installed and server is running
pip install flask-cors
```

## 📚 Additional Resources

### Research Papers
- [Communication-Efficient Learning of Deep Networks from Decentralized Data](https://arxiv.org/abs/1602.05629)
- [The Algorithmic Foundations of Differential Privacy](https://www.cis.upenn.edu/~aaroth/Papers/privacybook.pdf)

### Documentation
- [TensorFlow Federated](https://www.tensorflow.org/federated)
- [Flower Framework](https://flower.dev/)
- [Differential Privacy](https://www.microsoft.com/en-us/research/publication/differential-privacy/)

## 🎓 Educational Value

This project demonstrates:
- ✅ Federated Learning fundamentals
- ✅ Privacy-preserving machine learning
- ✅ Distributed systems architecture
- ✅ Full-stack development
- ✅ Real-world ML deployment
- ✅ Data privacy compliance

## 👥 Contributors

Samarth Khadse | 
Manan Oswal | 
Shrikant Kole

## 🙏 Acknowledgments

- TensorFlow team for ML framework
- Flask community for web framework
- React team for frontend library
- Research community for federated learning algorithms

---


