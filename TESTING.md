# 🧪 Testing & Validation Guide

This guide helps you test and validate the federated learning system.

---

## Quick Test Checklist

Use this checklist to verify everything works:

- [ ] Backend dependencies installed
- [ ] Frontend dependencies installed
- [ ] Sample data generated
- [ ] Server starts successfully
- [ ] Clients connect to server
- [ ] Frontend loads without errors
- [ ] Login works
- [ ] Training starts successfully
- [ ] Charts update in real-time
- [ ] Clients show in dashboard
- [ ] Centralized training works
- [ ] Comparison displays correctly

---

## 1. Backend Testing

### Test 1: Installation Verification

```bash
cd backend
python -c "import flask, tensorflow, numpy, pandas; print('✓ All imports successful')"
```

**Expected:** `✓ All imports successful`

### Test 2: Data Generation

```bash
python generate_data.py
```

**Expected Output:**
```
=== Generating Attendance Risk Data ===
Generated 500 attendance records
Client 1: 87 samples
Client 2: 103 samples
Client 3: 95 samples
Client 4: 112 samples
Client 5: 103 samples
=== Generating Learning Recommendation Data ===
Generated 500 learning records
...
=== Data Generation Complete ===
```

**Validation:**
```bash
# Check data files exist
dir ..\data\*.csv
dir ..\data\clients\*.db
```

### Test 3: Model Creation

```bash
python -c "from model import AttendanceRiskModel, LearningRecommendationModel; m1=AttendanceRiskModel(); m2=LearningRecommendationModel(); print('✓ Models created')"
```

**Expected:** `✓ Models created`

### Test 4: Privacy Module

```bash
python -c "from privacy import DifferentialPrivacy; dp=DifferentialPrivacy(); print(f'✓ DP initialized: ε={dp.epsilon}, δ={dp.delta}')"
```

**Expected:** `✓ DP initialized: ε=1.0, δ=1e-05`

### Test 5: Database Operations

```bash
python -c "from database import ClientDatabase; db=ClientDatabase(1); db.create_tables('attendance'); print('✓ Database operations work')"
```

**Expected:** `✓ Database operations work`

### Test 6: Server Startup

```bash
python server.py
```

**Expected Output:**
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

**Validation:**
- Open browser to `http://localhost:5000/api/health`
- Should see: `{"status":"healthy","server":"federated-learning"}`

### Test 7: Client Startup

```bash
python client.py --client-id 1
```

**Expected Output:**
```
============================================================
FEDERATED LEARNING CLIENT 1
============================================================
Client 1 ready
Server: http://localhost:5000
Waiting for training to start from dashboard...
```

---

## 2. Frontend Testing

### Test 1: Installation Verification

```bash
cd frontend
npm list react react-dom axios recharts
```

**Expected:** All packages listed without errors

### Test 2: Build Test

```bash
npm run build
```

**Expected:** Build completes without errors

### Test 3: Development Server

```bash
npm run dev
```

**Expected Output:**
```
  VITE v5.0.8  ready in 500 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

**Validation:**
- Open `http://localhost:5173`
- Should see login page
- No console errors (F12)

### Test 4: Login Functionality

1. Open `http://localhost:5173`
2. Enter username: `admin`
3. Enter password: `admin123`
4. Click "Sign In"

**Expected:** Redirected to dashboard

### Test 5: API Connection

Open browser console (F12) and run:

```javascript
fetch('http://localhost:5000/api/health')
  .then(r => r.json())
  .then(d => console.log('✓ API connected:', d))
```

**Expected:** `✓ API connected: {status: "healthy", ...}`

---

## 3. Integration Testing

### Test 1: Complete Training Flow

**Steps:**
1. Start server: `python server.py`
2. Start 3 clients in separate terminals
3. Start frontend: `npm run dev`
4. Login to dashboard
5. Select "Attendance Risk Prediction"
6. Set 5 rounds
7. Click "Start Training"

**Expected Results:**
- Training status shows "Training"
- Current round increments (1, 2, 3, 4, 5)
- Accuracy increases over rounds
- Loss decreases over rounds
- Charts update in real-time
- Client terminals show training progress

**Client Terminal Output:**
```
=== Round 1 ===
Starting local training: 5 epochs, 87 samples
Local training completed: accuracy=0.7234, loss=0.5432
Uploaded weights: 1.2 MB, 87 samples
=== Round 2 ===
Downloaded global model (round 1)
Starting local training: 5 epochs, 87 samples
...
```

### Test 2: Multiple Clients

**Steps:**
1. Start server
2. Start 5 clients (IDs 1-5)
3. Check dashboard "Client Nodes" tab

**Expected:**
- All 5 clients listed
- Status: "Connected"
- Privacy status: "Protected"

### Test 3: Centralized Comparison

**Steps:**
1. Complete federated training (Test 1)
2. Go to "Comparison" tab
3. Select "Attendance Risk Prediction"
4. Click "Train Centralized Model"
5. Wait for completion

**Expected:**
- Training completes in ~30 seconds
- Comparison table shows both approaches
- Metrics displayed correctly
- Winner determined

### Test 4: Data Persistence

**Steps:**
1. Complete training
2. Stop server
3. Restart server
4. Check if metrics are still available

**Expected:**
- Previous training data persists
- Charts show historical data

---

## 4. Performance Testing

### Test 1: Training Speed

**Measure:**
```python
import time
start = time.time()
# Run 10 rounds of training
end = time.time()
print(f"Total time: {end - start:.2f}s")
print(f"Time per round: {(end - start) / 10:.2f}s")
```

**Expected:**
- Total time: 20-40 seconds
- Time per round: 2-4 seconds

### Test 2: Memory Usage

**Windows:**
```powershell
# While server is running
tasklist | findstr python
```

**Expected:** <500 MB per process

### Test 3: Network Traffic

**Measure:**
- Check browser Network tab (F12)
- Monitor API calls during training

**Expected:**
- API calls every 3-5 seconds
- Response times <100ms
- Payload sizes <2MB

---

## 5. Privacy Testing

### Test 1: Differential Privacy

```python
from privacy import DifferentialPrivacy
import numpy as np

dp = DifferentialPrivacy(epsilon=1.0)
weights = [np.random.randn(10, 5)]

# Test noise addition
noisy = dp.add_noise(weights)
noise_magnitude = np.linalg.norm(noisy[0] - weights[0])

print(f"Noise magnitude: {noise_magnitude:.4f}")
print(f"Expected scale: {dp.noise_scale:.4f}")
```

**Expected:** Noise magnitude ≈ noise scale

### Test 2: Privacy Budget

```python
from privacy import DifferentialPrivacy

dp = DifferentialPrivacy()
epsilon, delta = dp.get_privacy_spent(num_rounds=10)

print(f"Total ε after 10 rounds: {epsilon:.4f}")
print(f"Total δ: {delta:.2e}")
```

**Expected:**
- ε ≈ 3.16
- δ = 1e-5

### Test 3: Data Isolation

**Verify:**
1. Check client databases are separate
2. Confirm no raw data in server
3. Verify only weights transmitted

```bash
# Check client databases
dir ..\data\clients\

# Should see: client_1.db, client_2.db, etc.
# Each file should be separate
```

---

## 6. Error Handling Testing

### Test 1: Server Not Running

**Steps:**
1. Stop server
2. Try to start training from frontend

**Expected:**
- Error message displayed
- "Server Offline" status shown
- No crash

### Test 2: No Clients Connected

**Steps:**
1. Start server only (no clients)
2. Try to start training

**Expected:**
- Training starts but waits for clients
- Graceful handling

### Test 3: Invalid Input

**Steps:**
1. Try to start training with 0 rounds
2. Try negative values

**Expected:**
- Validation errors
- User-friendly messages

---

## 7. Browser Compatibility

Test on multiple browsers:

- [ ] Chrome/Edge (Chromium)
- [ ] Firefox
- [ ] Safari (if on Mac)

**For each browser:**
1. Login works
2. Charts render correctly
3. Real-time updates work
4. No console errors

---

## 8. Stress Testing

### Test 1: Many Rounds

**Steps:**
1. Set rounds to 50
2. Start training
3. Monitor completion

**Expected:**
- Completes without errors
- Memory stable
- Performance consistent

### Test 2: Many Clients

**Steps:**
1. Start 10 clients
2. Run training

**Expected:**
- All clients participate
- Aggregation works correctly
- No timeouts

---

## 9. Validation Metrics

### Model Performance

**Attendance Risk:**
- Accuracy: 85-90%
- Loss: 0.3-0.4
- AUC: >0.85

**Learning Recommendation:**
- Accuracy: 80-85%
- Loss: 0.4-0.5
- F1 Score: >0.75

### Privacy Metrics

- Epsilon (10 rounds): 2.5-3.5
- Delta: 1e-5
- Privacy level: "High"

### System Metrics

- API latency: <100ms
- Frontend load: <2 seconds
- Training round: 2-4 seconds
- Memory usage: <500MB

---

## 10. Troubleshooting Tests

### Issue: Import Errors

**Test:**
```bash
python -c "import sys; print(sys.executable)"
```

**Fix:** Ensure virtual environment is activated

### Issue: Port Already in Use

**Test:**
```bash
netstat -ano | findstr :5000
```

**Fix:** Kill process or use different port

### Issue: Database Locked

**Test:**
```bash
python -c "from database import ClientDatabase; db=ClientDatabase(1); db.connect(); db.disconnect()"
```

**Fix:** Close all connections, restart

### Issue: CORS Errors

**Test:** Check browser console for CORS messages

**Fix:** Verify `config.CORS_ORIGINS` includes frontend URL

---

## 11. Automated Test Script

Create `test_system.py`:

```python
import requests
import time

def test_system():
    print("Testing Federated Learning System...")
    
    # Test 1: Server health
    try:
        r = requests.get('http://localhost:5000/api/health')
        assert r.status_code == 200
        print("✓ Server health check passed")
    except:
        print("✗ Server health check failed")
        return
    
    # Test 2: Start training
    try:
        r = requests.post('http://localhost:5000/api/federated/start', 
                         json={'use_case': 'attendance', 'num_rounds': 5})
        assert r.status_code == 200
        print("✓ Training start passed")
    except:
        print("✗ Training start failed")
        return
    
    # Test 3: Get status
    time.sleep(2)
    try:
        r = requests.get('http://localhost:5000/api/federated/status')
        data = r.json()
        assert data['active'] == True
        print("✓ Status check passed")
    except:
        print("✗ Status check failed")
        return
    
    print("\n✓ All tests passed!")

if __name__ == "__main__":
    test_system()
```

**Run:**
```bash
python test_system.py
```

---

## 12. Pre-Demo Checklist

Before demonstrating:

- [ ] All dependencies installed
- [ ] Data generated successfully
- [ ] Server starts without errors
- [ ] At least 3 clients running
- [ ] Frontend loads correctly
- [ ] Login credentials work
- [ ] Training completes successfully
- [ ] Charts display properly
- [ ] Comparison works
- [ ] No console errors
- [ ] Network connection stable
- [ ] Backup plan ready

---

## 13. Demo Script

**5-Minute Demo:**

1. **Introduction (30s)**
   - Explain federated learning
   - Show architecture diagram

2. **Login (15s)**
   - Open frontend
   - Login with credentials

3. **Show Clients (30s)**
   - Navigate to Client Nodes
   - Explain privacy features

4. **Start Training (2min)**
   - Select use case
   - Set 5 rounds
   - Start training
   - Watch real-time updates

5. **Show Results (1min)**
   - Point out accuracy improvement
   - Show privacy budget
   - Explain charts

6. **Comparison (1min)**
   - Train centralized model
   - Show comparison table
   - Explain trade-offs

7. **Q&A (30s)**

---

## 14. Common Test Scenarios

### Scenario 1: Fresh Install Test

```bash
# Clean install
rmdir /s /q venv node_modules
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
cd ..\frontend
npm install
```

### Scenario 2: Data Reset Test

```bash
# Clear all data
rmdir /s /q ..\data
python generate_data.py
```

### Scenario 3: Multi-Use Case Test

```bash
# Test both use cases
# 1. Train attendance model
# 2. Train learning model
# 3. Compare results
```

---

## 15. Acceptance Criteria

System is ready for demo when:

✅ All components start without errors
✅ Training completes successfully
✅ Accuracy reaches 85%+
✅ Charts update in real-time
✅ Privacy features work
✅ Comparison shows results
✅ No critical bugs
✅ Performance is acceptable
✅ Documentation is complete
✅ Demo script works smoothly

---

## Need Help?

If tests fail:

1. Check error messages carefully
2. Verify all dependencies installed
3. Ensure virtual environment active
4. Check port availability
5. Review logs for details
6. Restart components in order
7. Clear cache and retry
8. Consult troubleshooting guide

---

**Happy Testing! 🧪**
