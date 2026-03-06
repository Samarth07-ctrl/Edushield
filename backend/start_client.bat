@echo off
echo ============================================================
echo ACTIVATING VIRTUAL ENVIRONMENT AND STARTING CLIENT %1
echo ============================================================
echo.

if "%1"=="" (
    echo ERROR: Please provide a client ID
    echo Usage: start_client.bat [client_id]
    echo Example: start_client.bat 1
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Check if activation worked
python -c "import sys; print('Virtual environment:', 'ACTIVE' if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix) else 'NOT ACTIVE')"

echo.
echo Starting Federated Learning Client %1...
echo.

REM Start the client
python client.py --client-id %1

pause
