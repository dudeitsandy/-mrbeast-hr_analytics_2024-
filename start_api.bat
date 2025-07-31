@echo off
echo Starting MrBeast HR Analytics API...
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\python.exe" (
    echo ERROR: Virtual environment not found!
    echo Please run: python -m venv venv
    echo Then run: venv\Scripts\pip install -r requirements.txt
    pause
    exit /b 1
)

REM Set environment variable
set DATABASE_URL=postgresql://hr_user:hr_password@localhost:5432/mrbeast_hr

REM Start the API
echo Starting API on http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo.
venv\Scripts\python.exe api\main.py

pause 