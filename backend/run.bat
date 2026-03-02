@echo off
REM Backend startup script for Windows

echo Starting Multi-Agent Game Master Backend...
cd /d "%~dp0"

REM Check if venv exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install requirements
pip install -r requirements.txt

REM Start the server
echo Starting FastAPI server on http://localhost:8000
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
