# MrBeast HR Analytics Dashboard - PowerShell Runner
# Runs the Streamlit dashboard for HR analytics

param(
    [int]$Port = 8501,
    [string]$HostAddress = "localhost",
    [switch]$Help
)

# Show help if requested
if ($Help) {
    Write-Host @"
MrBeast HR Analytics Dashboard Runner

Usage: .\run_dashboard.ps1 [-Port <port>] [-HostAddress <host>] [-Help]

Parameters:
    -Port          Dashboard port (default: 8501)
    -HostAddress   Dashboard host (default: localhost)
    -Help          Show this help message

Examples:
    .\run_dashboard.ps1                           # Run with default settings
    .\run_dashboard.ps1 -Port 8502               # Run on port 8502
    .\run_dashboard.ps1 -HostAddress 0.0.0.0     # Run on all interfaces

"@
    exit 0
}

# Check if virtual environment exists and activate it
if (Test-Path "..\venv\Scripts\Activate.ps1") {
    Write-Host "Activating virtual environment..." -ForegroundColor Green
    & "..\venv\Scripts\Activate.ps1"
} else {
    Write-Host "Warning: Virtual environment not found. Using system Python." -ForegroundColor Yellow
}

# Check if required files exist
if (-not (Test-Path "visualizations\dashboard.py")) {
    Write-Host "Error: Dashboard file not found: visualizations\dashboard.py" -ForegroundColor Red
    exit 1
}

# Check if API is running
Write-Host "Checking API health..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get -TimeoutSec 5
    if ($response.database_connected) {
        Write-Host "✅ API is healthy and connected to database" -ForegroundColor Green
    } else {
        Write-Host "⚠️ API is running but database connection failed" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ API is not running. Please start the API first:" -ForegroundColor Red
    Write-Host "   cd ..\api && .\run_api.ps1" -ForegroundColor Cyan
    Write-Host "   Or run: python ..\api\main.py" -ForegroundColor Cyan
    exit 1
}

# Run the dashboard
Write-Host "Starting MrBeast HR Analytics Dashboard..." -ForegroundColor Green
Write-Host "Host: $HostAddress" -ForegroundColor Gray
Write-Host "Port: $Port" -ForegroundColor Gray
Write-Host "Dashboard URL: http://$HostAddress`:$Port" -ForegroundColor Cyan
Write-Host "API URL: http://localhost:8000" -ForegroundColor Cyan

try {
    & streamlit run visualizations\dashboard.py --server.port $Port --server.address $HostAddress
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Dashboard stopped successfully!" -ForegroundColor Green
    } else {
        Write-Host "Dashboard stopped with errors (exit code: $LASTEXITCODE)" -ForegroundColor Red
    }
} catch {
    Write-Host "Error running dashboard: $_" -ForegroundColor Red
    exit 1
} 