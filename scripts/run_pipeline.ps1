# HR Analytics Data Pipeline - PowerShell Wrapper
# Simple execution script for the consolidated HR data pipeline

param(
    [string]$DatabaseUrl,
    [string]$ExcelFile = "data/HRIS_TAKE_HOME_PROJECT_DATA.xlsx",
    [switch]$ValidateOnly,
    [switch]$LoadOnly,
    [switch]$Help
)

# Set default database URL from environment if not provided
if (-not $DatabaseUrl) {
    $DatabaseUrl = $env:DATABASE_URL
}

# Show help if requested
if ($Help) {
    Write-Host @"
HR Analytics Data Pipeline

Usage: .\run_pipeline.ps1 [-DatabaseUrl <url>] [-ExcelFile <path>] [-ValidateOnly] [-LoadOnly] [-Help]

Parameters:
    -DatabaseUrl    PostgreSQL connection string (default: DATABASE_URL env var)
    -ExcelFile      Path to Excel file (default: data/HRIS_TAKE_HOME_PROJECT_DATA.xlsx)
    -ValidateOnly   Only validate existing data (skip loading)
    -LoadOnly       Only load data (skip validation)
    -Help          Show this help message

Examples:
    .\run_pipeline.ps1                                    # Run full pipeline (load + validate)
    .\run_pipeline.ps1 -ValidateOnly                      # Only validate existing data
    .\run_pipeline.ps1 -LoadOnly                          # Only load data
    .\run_pipeline.ps1 -DatabaseUrl "postgresql://..."    # Use custom database URL

"@
    exit 0
}

# Check if virtual environment exists and activate it
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "Activating virtual environment..." -ForegroundColor Green
    & "venv\Scripts\Activate.ps1"
} else {
    Write-Host "Warning: Virtual environment not found. Using system Python." -ForegroundColor Yellow
}

# Check if required files exist
if (-not (Test-Path $ExcelFile)) {
    Write-Host "Error: Excel file not found: $ExcelFile" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path "scripts\hr_data_pipeline.py")) {
    Write-Host "Error: Pipeline script not found: scripts\hr_data_pipeline.py" -ForegroundColor Red
    exit 1
}

# Set up arguments for the Python script
$pythonArgs = @("scripts\hr_data_pipeline.py")

# Only add database-url if it's not empty
if ($DatabaseUrl -and $DatabaseUrl.Trim() -ne "") {
    $pythonArgs += @("--database-url", $DatabaseUrl)
}
# Note: If no database URL is provided, the Python script will use the DATABASE_URL environment variable
# The Python script will automatically use the DATABASE_URL environment variable if --database-url is not provided

if ($ExcelFile -ne "data/HRIS_TAKE_HOME_PROJECT_DATA.xlsx") {
    $pythonArgs += @("--excel-file", $ExcelFile)
}

if ($ValidateOnly) {
    $pythonArgs += @("--validate-only")
}

if ($LoadOnly) {
    $pythonArgs += @("--load-only")
}

# Run the pipeline
Write-Host "Starting HR Analytics Data Pipeline..." -ForegroundColor Green
Write-Host "Command: python $($pythonArgs -join ' ')" -ForegroundColor Gray

try {
    & python @pythonArgs
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Pipeline completed successfully!" -ForegroundColor Green
    } else {
        Write-Host "Pipeline completed with errors (exit code: $LASTEXITCODE)" -ForegroundColor Red
    }
} catch {
    Write-Host "Error running pipeline: $_" -ForegroundColor Red
    exit 1
} 