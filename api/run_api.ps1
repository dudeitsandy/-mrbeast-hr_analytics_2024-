# HR Analytics API - PowerShell Runner
# Runs the FastAPI application for HR analytics

param(
    [string]$DatabaseUrl = $env:DATABASE_URL,
    [int]$Port = 8000,
    [string]$ApiHost = "0.0.0.0",
    [switch]$Help
)

# Show help if requested
if ($Help) {
    Write-Host @"
HR Analytics API Runner

Usage: .\run_api.ps1 [-DatabaseUrl <url>] [-Port <port>] [-ApiHost <host>] [-Help]

Parameters:
    -DatabaseUrl    PostgreSQL connection string (default: DATABASE_URL env var)
    -Port          API port (default: 8000)
    -ApiHost       API host (default: 0.0.0.0)
    -Help          Show this help message

Examples:
    .\run_api.ps1                                    # Run with default settings
    .\run_api.ps1 -Port 8080                        # Run on port 8080
    .\run_api.ps1 -DatabaseUrl "postgresql://..."   # Use custom database URL

"@
    exit 0
}

# Colors for output
$Green = "Green"
$Yellow = "Yellow"
$Red = "Red"
$Cyan = "Cyan"

function Write-ColorOutput {
    param([string]$Message, [string]$Color = "White")
    Write-Host $Message -ForegroundColor $Color
}

# Get the project root directory (parent of api directory)
$ProjectRoot = Split-Path -Parent $PSScriptRoot
Write-ColorOutput "Project root: $ProjectRoot" $Cyan

# Change to project root directory
Set-Location $ProjectRoot
Write-ColorOutput "Changed to project root directory" $Green

# Check if virtual environment exists
if (-not (Test-Path "venv\Scripts\python.exe")) {
    Write-ColorOutput "❌ Virtual environment not found. Please run setup first." $Red
    Write-ColorOutput "Run: .\run_master.ps1 setup" $Yellow
    exit 1
}

# Use virtual environment Python
$pythonExe = "venv\Scripts\python.exe"
Write-ColorOutput "Using Python: $pythonExe" $Green

# Set environment variable if provided
if ($DatabaseUrl) {
    $env:DATABASE_URL = $DatabaseUrl
    Write-ColorOutput "Using custom DATABASE_URL" $Green
} else {
    # Set default DATABASE_URL if not provided
    if (-not $env:DATABASE_URL) {
        $env:DATABASE_URL = "postgresql://hr_user:hr_password@localhost:5432/mrbeast_hr"
        Write-ColorOutput "Using default DATABASE_URL" $Yellow
    }
}

# Check if API file exists
if (-not (Test-Path "api\main.py")) {
    Write-ColorOutput "❌ API file not found: api\main.py" $Red
    exit 1
}

# Run the API
Write-ColorOutput "`n🚀 Starting HR Analytics API..." $Cyan
Write-ColorOutput "Host: $ApiHost" $Yellow
Write-ColorOutput "Port: $Port" $Yellow
Write-ColorOutput "API Documentation: http://$ApiHost`:$Port/docs" $Cyan
Write-ColorOutput "Health Check: http://$ApiHost`:$Port/health" $Cyan
Write-ColorOutput "Working Directory: $ProjectRoot" $Yellow

try {
    # Run the API using the virtual environment Python
    & $pythonExe "api\main.py" --host $ApiHost --port $Port
    
    if ($LASTEXITCODE -eq 0) {
        Write-ColorOutput "API stopped successfully!" $Green
    } else {
        Write-ColorOutput "API stopped with errors (exit code: $LASTEXITCODE)" $Red
    }
} catch {
    Write-ColorOutput "Error running API: $_" $Red
    exit 1
} 