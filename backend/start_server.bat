@echo off
echo ============================================================
echo ACTIVATING VIRTUAL ENVIRONMENT AND STARTING SERVER
echo ============================================================
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Check if activation worked
python -c "import sys; print('Virtual environment:', 'ACTIVE' if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix) else 'NOT ACTIVE')"

echo.
echo Starting Federated Learning Server...
echo.

REM Start the server
python server.py

pause
