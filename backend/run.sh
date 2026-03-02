#!/bin/bash
# Backend startup script

echo "Starting Multi-Agent Game Master Backend..."
cd "$(dirname "$0")"

# Install dependencies if needed
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
source venv/bin/activate 2>/dev/null || . venv/Scripts/activate

# Install requirements
pip install -r requirements.txt

# Start the server
echo "Starting FastAPI server on http://localhost:8000"
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
