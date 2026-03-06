# ⚠️ SERVER ERROR - QUICK FIX

## 🔍 Problem Detected

The server is showing 500 Internal Server Errors. This is likely because:
- The server wasn't started with the virtual environment activated
- Some dependencies are missing in the running server

## ✅ QUICK FIX

### Step 1: Stop the Current Server

In the terminal running `python server.py`, press **Ctrl+C** to stop it.

### Step 2: Restart Server with Virtual Environment

**Option A: Use the Batch Script (EASIEST)**
```cmd
cd d:\Projects\Personal_projects\edi_practise\federated-learning-campus\backend
start_server.bat
```

**Option B: Manual Activation**
```cmd
cd d:\Projects\Personal_projects\edi_practise\federated-learning-campus\backend
venv\Scripts\activate.bat
python server.py
```

### Step 3: Verify Server Started

You should see:
```
============================================================
FEDERATED LEARNING SERVER
============================================================
Server starting on 0.0.0.0:5000
Privacy: ENABLED
Encryption: ENABLED
============================================================
 * Serving Flask app 'server'
 * Running on http://0.0.0.0:5000
```

### Step 4: Restart Clients (if needed)

If clients show errors, restart them:
```cmd
cd d:\Projects\Personal_projects\edi_practise\federated-learning-campus\backend
venv\Scripts\activate.bat
python client.py --client-id 1
```

### Step 5: Refresh Browser

- Go to http://localhost:5173
- Press **Ctrl+Shift+R** (hard refresh)
- Login again if needed

---

## 🎯 CORRECT STARTUP SEQUENCE

Always start in this order:

### 1. Server (with venv)
```cmd
cd backend
venv\Scripts\activate.bat
python server.py
```
**Wait for:** "Running on http://0.0.0.0:5000"

### 2. Clients (with venv)
```cmd
cd backend
venv\Scripts\activate.bat
python client.py --client-id 1
```
**Wait for:** "Waiting for training to start..."

### 3. Frontend (already running - OK)
```cmd
cd frontend
npm run dev
```

---

## 🔍 How to Check if venv is Active

Before running `python server.py`, check:

**In Command Prompt:**
```cmd
where python
```
Should show: `...\backend\venv\Scripts\python.exe`

**In PowerShell:**
```powershell
(Get-Command python).Source
```
Should show: `...\backend\venv\Scripts\python.exe`

**Or look for `(venv)` in your prompt:**
```
(venv) PS D:\...\backend>
```

---

## 💡 Pro Tip: Always Use Batch Scripts

To avoid this issue, always use the batch scripts I created:

- `start_server.bat` - Auto-activates venv and starts server
- `start_client.bat 1` - Auto-activates venv and starts client

These scripts ensure the virtual environment is always activated!

---

## ✅ After Restarting

Once server is restarted correctly:
1. Refresh browser (Ctrl+Shift+R)
2. Login (admin/admin123)
3. Start training
4. Everything should work!

---

**The issue is just the venv not being activated. Quick restart will fix it!** 🚀
