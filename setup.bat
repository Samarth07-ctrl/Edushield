@echo off
echo ============================================================
echo FEDERATED LEARNING CAMPUS - SETUP SCRIPT
echo ============================================================
echo.

echo [1/4] Setting up backend...
cd backend

echo Creating virtual environment...
python -m venv venv
call venv\Scripts\activate

echo Installing Python dependencies...
pip install -r requirements.txt

echo.
echo [2/4] Generating sample data...
python generate_data.py

echo.
echo [3/4] Setting up frontend...
cd ..\frontend

echo Installing Node.js dependencies...
call npm install

echo.
echo [4/4] Setup complete!
echo.
echo ============================================================
echo NEXT STEPS:
echo ============================================================
echo.
echo 1. Start the backend server:
echo    cd backend
echo    python server.py
echo.
echo 2. Start clients (in separate terminals):
echo    cd backend
echo    python client.py --client-id 1
echo    python client.py --client-id 2
echo    python client.py --client-id 3
echo.
echo 3. Start the frontend:
echo    cd frontend
echo    npm run dev
echo.
echo 4. Open browser to: http://localhost:5173
echo    Login: admin / admin123
echo.
echo ============================================================
echo.
pause
