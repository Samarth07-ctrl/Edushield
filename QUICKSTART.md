# 🚀 Quick Start Guide - Federated Learning Smart Campus

This guide will help you get the complete federated learning system up and running in minutes.

## 📋 Prerequisites

Before starting, ensure you have:

- ✅ Python 3.8 or higher
- ✅ Node.js 16 or higher
- ✅ npm or yarn
- ✅ At least 4GB RAM
- ✅ Windows/Linux/Mac OS

## 🎯 Step-by-Step Setup

### Step 1: Backend Setup (5 minutes)

1. **Navigate to backend directory:**
```bash
cd backend
```

2. **Create virtual environment:**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

3. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

This will install:
- Flask (web framework)
- TensorFlow (machine learning)
- NumPy, Pandas (data processing)
- Cryptography (encryption)
- Flask-CORS (API support)

4. **Generate sample data:**
```bash
python generate_data.py
```

This creates:
- 500 attendance records
- 500 learning records
- 5 client databases with distributed data
- CSV files in `../data/` directory

**Expected output:**
```
=== Generating Attendance Risk Data ===
Generated 500 attendance records
Client 1: 87 samples
Client 2: 103 samples
...
=== Data Generation Complete ===
```

### Step 2: Frontend Setup (3 minutes)

1. **Open a NEW terminal and navigate to frontend:**
```bash
cd frontend
```

2. **Install Node.js dependencies:**
```bash
npm install
```

This installs:
- React 18
- Vite (build tool)
- Axios (HTTP client)
- Recharts (data visualization)
- React Router (navigation)

### Step 3: Start the System (2 minutes)

Now you'll start multiple components. Keep each terminal open!

#### Terminal 1: Start Backend Server

```bash
cd backend
# Activate venv if not already active
python server.py
```

**Expected output:**
```
============================================================
FEDERATED LEARNING SERVER
============================================================
Server starting on 0.0.0.0:5000
Privacy: ENABLED
Encryption: ENABLED
============================================================
 * Running on http://0.0.0.0:5000
```

✅ Server is ready when you see "Running on..."

#### Terminal 2: Start Client 1

```bash
cd backend
python client.py --client-id 1
```

**Expected output:**
```
============================================================
FEDERATED LEARNING CLIENT 1
============================================================
Client 1 ready
Server: http://localhost:5000
Waiting for training to start from dashboard...
```

#### Terminal 3: Start Client 2

```bash
cd backend
python client.py --client-id 2
```

#### Terminal 4: Start Client 3

```bash
cd backend
python client.py --client-id 3
```

**💡 Tip:** You can start as many clients as you want (1-5 recommended for demo)

#### Terminal 5: Start Frontend

```bash
cd frontend
npm run dev
```

**Expected output:**
```
  VITE v5.0.8  ready in 500 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

✅ Frontend is ready! Open http://localhost:5173 in your browser

## 🎮 Using the Application

### 1. Login

- Open browser to `http://localhost:5173`
- Username: `admin`
- Password: `admin123`
- Click "Sign In"

### 2. Start Federated Training

1. You'll see the Dashboard with Training Control Panel
2. Select **Use Case**: 
   - "Attendance Risk Prediction" OR
   - "Learning Recommendation"
3. Set **Number of Rounds**: 10 (recommended)
4. Click **"▶️ Start Training"**

### 3. Watch Real-Time Training

You'll see:
- ✅ Current round progress
- ✅ Connected clients count
- ✅ Live accuracy updates
- ✅ Real-time charts updating

**In client terminals, you'll see:**
```
=== Round 1 ===
Starting local training: 5 epochs, 87 samples
Local training completed: accuracy=0.7234, loss=0.5432, time=2.34s
Uploaded weights: 1.2 MB, 87 samples
```

### 4. View Visualizations

Scroll down to see:
- 📈 **Accuracy Over Rounds** - Model improving
- 📉 **Loss Over Rounds** - Error decreasing
- 👥 **Client Participation** - Active clients per round
- 🔒 **Privacy Budget** - Privacy consumption tracking

### 5. Check Client Nodes

Click **"💻 Client Nodes"** in sidebar to see:
- Connected clients
- Privacy features explanation
- Data location (local only)
- Encryption status

### 6. Compare Approaches

Click **"⚖️ Comparison"** in sidebar:

1. Select use case
2. Click **"🚀 Train Centralized Model"**
3. Wait ~30 seconds for training
4. View comparison table:
   - Accuracy comparison
   - Privacy scores
   - Communication costs
   - Winner determination

## 📊 Expected Results

### Attendance Risk Prediction
- **Final Accuracy**: 85-90%
- **Training Rounds**: 10
- **Privacy Budget (ε)**: ~3.16
- **Clients**: 3-5

### Learning Recommendation
- **Final Accuracy**: 80-85%
- **Training Rounds**: 10
- **Privacy Budget (ε)**: ~3.16
- **Clients**: 3-5

### Comparison Results
- **Federated Accuracy**: ~85%
- **Centralized Accuracy**: ~87%
- **Privacy Gain**: +100% (Federated)
- **Communication Cost**: ~5-10 MB (Federated)

## 🔍 Troubleshooting

### Issue: "Connection refused" error

**Solution:**
```bash
# Check if server is running
# Terminal should show "Running on http://0.0.0.0:5000"
# If not, restart server.py
```

### Issue: "No module named 'tensorflow'"

**Solution:**
```bash
# Activate virtual environment
cd backend
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: Frontend shows "Server Offline"

**Solution:**
1. Check backend server is running (Terminal 1)
2. Check URL is `http://localhost:5000`
3. Try refreshing browser
4. Check CORS settings in `server.py`

### Issue: "No training data available"

**Solution:**
```bash
# Regenerate data
cd backend
python generate_data.py
```

### Issue: Clients not connecting

**Solution:**
1. Ensure server is running first
2. Check client terminal for errors
3. Verify port 5000 is not blocked
4. Try restarting clients one by one

### Issue: Charts not showing

**Solution:**
1. Start training first
2. Wait for at least 2-3 rounds
3. Refresh browser
4. Check browser console for errors (F12)

## 🎯 Demo Scenarios

### Scenario 1: Quick Demo (5 minutes)

1. Start server + 2 clients + frontend
2. Login to dashboard
3. Start "Attendance" training for 5 rounds
4. Watch real-time updates
5. Show privacy features

### Scenario 2: Full Comparison (10 minutes)

1. Start server + 3 clients + frontend
2. Run federated training (10 rounds)
3. Train centralized model
4. Show comparison results
5. Explain privacy vs accuracy trade-off

### Scenario 3: Privacy Focus (15 minutes)

1. Start system with 5 clients
2. Show client nodes tab
3. Explain differential privacy
4. Show encryption in action
5. Compare with centralized (no privacy)
6. Show privacy budget consumption

## 📁 Project Structure Quick Reference

```
federated-learning-campus/
├── backend/
│   ├── server.py          ← Start this first
│   ├── client.py          ← Start multiple instances
│   ├── generate_data.py   ← Run once to create data
│   └── requirements.txt   ← Install dependencies
├── frontend/
│   ├── src/
│   │   ├── components/    ← React UI components
│   │   └── services/      ← API communication
│   └── package.json       ← Install dependencies
└── data/
    ├── clients/           ← Auto-generated databases
    └── *.csv              ← Auto-generated datasets
```

## 🎓 What You're Demonstrating

This project showcases:

1. **Federated Learning**: Distributed ML training
2. **Privacy Preservation**: Differential privacy + encryption
3. **Real-World Application**: Smart campus use cases
4. **Full-Stack Development**: Python backend + React frontend
5. **Data Visualization**: Real-time charts and metrics
6. **Comparison Analysis**: Centralized vs Federated

## 🚀 Next Steps

After basic demo:

1. **Modify hyperparameters** in `config.py`
2. **Add more clients** (up to 10)
3. **Try different use cases**
4. **Adjust privacy budget** (epsilon values)
5. **Experiment with rounds** (5-50)

## 💡 Tips for Presentation

1. **Start with privacy problem**: Why federated learning?
2. **Show data generation**: Local data stays local
3. **Demonstrate training**: Real-time visualization
4. **Highlight privacy**: Differential privacy + encryption
5. **Compare approaches**: Show trade-offs
6. **Explain results**: Accuracy vs Privacy

## 📞 Need Help?

If you encounter issues:

1. Check all terminals are running
2. Verify Python virtual environment is activated
3. Ensure all dependencies are installed
4. Check firewall/antivirus settings
5. Try restarting in order: server → clients → frontend

---

**🎉 You're all set! Enjoy your federated learning demonstration!**
