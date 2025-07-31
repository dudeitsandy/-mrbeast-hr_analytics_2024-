@echo off
echo Starting chart export...
echo.

REM Check if API is running
curl -s http://localhost:8000/health >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: API is not running on localhost:8000
    echo Please start the API first with: .\start_api.bat
    pause
    exit /b 1
)

echo API is running. Starting export...
python visualizations/export_dashboard.py

echo.
echo Export complete! Check the 'exports' directory for images.
pause 