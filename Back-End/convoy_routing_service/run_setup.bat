@echo off
REM ============================================================
REM FastAPI Project Runner for convoy_routing_service
REM ============================================================

REM Change directory to project root
cd /d "C:\Users\nagal\OneDrive\Pictures\TVS HACKATHON\convoy_routing_service"

REM Activate virtual environment
call venv\Scripts\activate

REM OPTIONAL: Ensure all dependencies are installed (uncomment if needed)
REM pip install -r "C:\Users\nagal\OneDrive\Pictures\TVS HACKATHON\requirements.txt"

REM Run FastAPI server with auto-reload
uvicorn app.main:app --reload

REM Keep terminal open after server stops
pause
