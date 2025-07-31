@echo off
echo Testing MrBeast HR Analytics System...
echo.

REM Test Python
echo Testing Python...
python --version
if errorlevel 1 (
    echo ERROR: Python not found
    pause
    exit /b 1
)

REM Test virtual environment
echo Testing virtual environment...
if not exist "venv\Scripts\python.exe" (
    echo ERROR: Virtual environment not found
    pause
    exit /b 1
)
echo Virtual environment exists

REM Test database connection
echo Testing database connection...
psql -h localhost -U hr_user -d mrbeast_hr -c "SELECT 1;" >nul 2>&1
if errorlevel 1 (
    echo ERROR: Database connection failed
    pause
    exit /b 1
)
echo Database connection OK

REM Test API
echo Testing API...
curl -s http://localhost:8000/health >nul 2>&1
if errorlevel 1 (
    echo WARNING: API not running (this is OK if not started yet)
) else (
    echo API is running and healthy
)

echo.
echo System test completed!
pause 