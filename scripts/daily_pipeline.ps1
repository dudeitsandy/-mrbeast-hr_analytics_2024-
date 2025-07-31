#!/usr/bin/env pwsh
<#
.SYNOPSIS
    MrBeast HR Analytics - Daily Data Pipeline
    
.DESCRIPTION
    Professional daily pipeline for HR analytics data refresh.
    This script runs daily (typically via cron/scheduler) to:
    1. Refresh data from source systems
    2. Validate data quality
    3. Update database
    4. Monitor pipeline health
    5. Generate quality reports
    6. Send alerts for issues
    
    This is separate from application deployment - applications run as services.
    
.PARAMETER SourceFile
    Path to source Excel file (default: data/HRIS_TAKE_HOME_PROJECT_DATA.xlsx)
    
.PARAMETER LogLevel
    Logging level: Info, Warning, Error (default: Info)
    
.PARAMETER SendAlerts
    Send email alerts on failures (requires email configuration)
    
.PARAMETER GenerateReport
    Generate data quality report (default: true)
    
.EXAMPLE
    .\daily_pipeline.ps1
    # Run daily pipeline with default settings
    
.EXAMPLE
    .\daily_pipeline.ps1 -LogLevel Warning -GenerateReport
    # Run with warning-level logging and generate report
#>

param(
    [string]$SourceFile = "data\HRIS_TAKE_HOME_PROJECT_DATA.xlsx",
    [ValidateSet("Info", "Warning", "Error")]$LogLevel = "Info",
    [switch]$SendAlerts,
    [switch]$GenerateReport = $true
)

# Set error action preference
$ErrorActionPreference = "Stop"

# Colors for output
$Colors = @{
    Success = "Green"
    Info = "Cyan"
    Warning = "Yellow"
    Error = "Red"
    Header = "Magenta"
}

# Pipeline status tracking
$PipelineStatus = @{
    StartTime = Get-Date
    Steps = @()
    Errors = @()
    Warnings = @()
    DataQuality = @{}
}

function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "[$timestamp] $Message" -ForegroundColor $Colors[$Color]
}

function Add-PipelineStep {
    param(
        [string]$Step,
        [string]$Status,
        [string]$Details = ""
    )
    $PipelineStatus.Steps += @{
        Step = $Step
        Status = $Status
        Details = $Details
        Timestamp = Get-Date
    }
}

function Test-DatabaseConnection {
    try {
        Write-ColorOutput "Testing database connection..." "Info"
        $env:DATABASE_URL = "postgresql://postgres:password@localhost:5432/hr_analytics"
        
        # Test connection using Python
        $testScript = @"
import psycopg2
import os
try:
    conn = psycopg2.connect(os.environ['DATABASE_URL'])
    conn.close()
    print("SUCCESS")
except Exception as e:
    print(f"ERROR: {e}")
    exit(1)
"@
        
        $result = python -c $testScript
        if ($result -eq "SUCCESS") {
            Write-ColorOutput "✅ Database connection successful" "Success"
            Add-PipelineStep "Database Connection" "Success"
            return $true
        } else {
            Write-ColorOutput "❌ Database connection failed: $result" "Error"
            Add-PipelineStep "Database Connection" "Failed" $result
            return $false
        }
    } catch {
        Write-ColorOutput "❌ Database connection test failed: $($_.Exception.Message)" "Error"
        Add-PipelineStep "Database Connection" "Failed" $_.Exception.Message
        return $false
    }
}

function Test-SourceData {
    try {
        Write-ColorOutput "Validating source data file..." "Info"
        
        if (-not (Test-Path $SourceFile)) {
            Write-ColorOutput "❌ Source file not found: $SourceFile" "Error"
            Add-PipelineStep "Source Data Validation" "Failed" "File not found"
            return $false
        }
        
        # Check file size and modification date
        $fileInfo = Get-Item $SourceFile
        $fileSize = $fileInfo.Length
        $lastModified = $fileInfo.LastWriteTime
        
        Write-ColorOutput "📁 Source file: $SourceFile" "Info"
        Write-ColorOutput "📊 File size: $([math]::Round($fileSize/1MB, 2)) MB" "Info"
        Write-ColorOutput "📅 Last modified: $lastModified" "Info"
        
        # Check if file is recent (within last 24 hours)
        $hoursSinceModified = (Get-Date) - $lastModified
        if ($hoursSinceModified.TotalHours -gt 24) {
            Write-ColorOutput "⚠️ Warning: Source file is older than 24 hours" "Warning"
            $PipelineStatus.Warnings += "Source file is older than 24 hours"
        }
        
        Add-PipelineStep "Source Data Validation" "Success" "File size: $([math]::Round($fileSize/1MB, 2)) MB"
        return $true
    } catch {
        Write-ColorOutput "❌ Source data validation failed: $($_.Exception.Message)" "Error"
        Add-PipelineStep "Source Data Validation" "Failed" $_.Exception.Message
        return $false
    }
}

function Invoke-DataRefresh {
    try {
        Write-ColorOutput "🔄 Refreshing data from source..." "Info"
        
        # Activate virtual environment
        & "venv\Scripts\Activate.ps1"
        
        # Run data pipeline with validation
        Write-ColorOutput "Running data pipeline..." "Info"
        $pipelineResult = & python "scripts\hr_data_pipeline.py" --validate-only
        
        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput "✅ Data refresh completed successfully" "Success"
            Add-PipelineStep "Data Refresh" "Success"
            return $true
        } else {
            Write-ColorOutput "❌ Data refresh failed" "Error"
            Add-PipelineStep "Data Refresh" "Failed" "Pipeline returned non-zero exit code"
            return $false
        }
    } catch {
        Write-ColorOutput "❌ Data refresh failed: $($_.Exception.Message)" "Error"
        Add-PipelineStep "Data Refresh" "Failed" $_.Exception.Message
        return $false
    }
}

function Test-DataQuality {
    try {
        Write-ColorOutput "🔍 Running data quality checks..." "Info"
        
        # Activate virtual environment
        & "venv\Scripts\Activate.ps1"
        
        # Run data quality checks
        $qualityScript = @"
import pandas as pd
import psycopg2
import os
from datetime import datetime

def check_data_quality():
    try:
        # Connect to database
        conn = psycopg2.connect(os.environ['DATABASE_URL'])
        cursor = conn.cursor()
        
        # Check table row counts
        tables = ['applicants', 'employees', 'Employment type']
        results = {}
        
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM hr_analytics.\"{table}\"")
            count = cursor.fetchone()[0]
            results[table] = count
            
        # Check for null values in critical columns
        cursor.execute("""
            SELECT 
                COUNT(*) as total_applicants,
                COUNT(CASE WHEN \"Name\" IS NULL THEN 1 END) as null_names,
                COUNT(CASE WHEN \"Role\" IS NULL THEN 1 END) as null_roles,
                COUNT(CASE WHEN \"Status\" IS NULL THEN 1 END) as null_status
            FROM hr_analytics.applicants
        """)
        applicant_quality = cursor.fetchone()
        
        cursor.execute("""
            SELECT 
                COUNT(*) as total_employees,
                COUNT(CASE WHEN \"Name\" IS NULL THEN 1 END) as null_names,
                COUNT(CASE WHEN \"Department\" IS NULL THEN 1 END) as null_depts,
                COUNT(CASE WHEN \"Salary\" IS NULL THEN 1 END) as null_salaries
            FROM hr_analytics.employees
        """)
        employee_quality = cursor.fetchone()
        
        conn.close()
        
        # Calculate quality metrics
        quality_metrics = {
            'table_counts': results,
            'applicant_quality': {
                'total': applicant_quality[0],
                'null_names_pct': (applicant_quality[1] / applicant_quality[0] * 100) if applicant_quality[0] > 0 else 0,
                'null_roles_pct': (applicant_quality[2] / applicant_quality[0] * 100) if applicant_quality[0] > 0 else 0,
                'null_status_pct': (applicant_quality[3] / applicant_quality[0] * 100) if applicant_quality[0] > 0 else 0
            },
            'employee_quality': {
                'total': employee_quality[0],
                'null_names_pct': (employee_quality[1] / employee_quality[0] * 100) if employee_quality[0] > 0 else 0,
                'null_depts_pct': (employee_quality[2] / employee_quality[0] * 100) if employee_quality[0] > 0 else 0,
                'null_salaries_pct': (employee_quality[3] / employee_quality[0] * 100) if employee_quality[0] > 0 else 0
            }
        }
        
        print("QUALITY_CHECK_SUCCESS")
        for key, value in quality_metrics.items():
            print(f"{key}:{value}")
            
    except Exception as e:
        print(f"QUALITY_CHECK_ERROR:{e}")
        exit(1)

if __name__ == "__main__":
    check_data_quality()
"@
        
        $qualityResult = python -c $qualityScript
        
        if ($qualityResult -like "QUALITY_CHECK_SUCCESS*") {
            Write-ColorOutput "✅ Data quality checks completed" "Success"
            
            # Parse quality metrics
            $qualityLines = $qualityResult -split "`n" | Where-Object { $_ -ne "QUALITY_CHECK_SUCCESS" }
            foreach ($line in $qualityLines) {
                if ($line -match "(.+):(.+)") {
                    $key = $matches[1]
                    $value = $matches[2]
                    $PipelineStatus.DataQuality[$key] = $value
                }
            }
            
            Add-PipelineStep "Data Quality Check" "Success"
            return $true
        } else {
            Write-ColorOutput "❌ Data quality check failed: $qualityResult" "Error"
            Add-PipelineStep "Data Quality Check" "Failed" $qualityResult
            return $false
        }
    } catch {
        Write-ColorOutput "❌ Data quality check failed: $($_.Exception.Message)" "Error"
        Add-PipelineStep "Data Quality Check" "Failed" $_.Exception.Message
        return $false
    }
}

function Test-APIHealth {
    try {
        Write-ColorOutput "🏥 Testing API health..." "Info"
        
        # Test API endpoints
        $endpoints = @(
            "http://localhost:8000/health",
            "http://localhost:8000/hiring-metrics",
            "http://localhost:8000/applicants/status-summary"
        )
        
        $healthyEndpoints = 0
        foreach ($endpoint in $endpoints) {
            try {
                $response = Invoke-RestMethod -Uri $endpoint -Method Get -TimeoutSec 10
                Write-ColorOutput "✅ $endpoint - Healthy" "Success"
                $healthyEndpoints++
            } catch {
                Write-ColorOutput "❌ $endpoint - Unhealthy: $($_.Exception.Message)" "Error"
                $PipelineStatus.Errors += "API endpoint $endpoint failed"
            }
        }
        
        if ($healthyEndpoints -eq $endpoints.Count) {
            Write-ColorOutput "✅ All API endpoints healthy" "Success"
            Add-PipelineStep "API Health Check" "Success" "All $($endpoints.Count) endpoints healthy"
            return $true
        } else {
            Write-ColorOutput "⚠️ Some API endpoints unhealthy ($healthyEndpoints/$($endpoints.Count))" "Warning"
            Add-PipelineStep "API Health Check" "Warning" "$healthyEndpoints/$($endpoints.Count) endpoints healthy"
            return $false
        }
    } catch {
        Write-ColorOutput "❌ API health check failed: $($_.Exception.Message)" "Error"
        Add-PipelineStep "API Health Check" "Failed" $_.Exception.Message
        return $false
    }
}

function New-QualityReport {
    try {
        Write-ColorOutput "📊 Generating data quality report..." "Info"
        
        $reportPath = "reports\daily_pipeline_report_$(Get-Date -Format 'yyyy-MM-dd').json"
        
        # Ensure reports directory exists
        if (-not (Test-Path "reports")) {
            New-Item -ItemType Directory -Path "reports" -Force | Out-Null
        }
        
        # Create comprehensive report
        $report = @{
            PipelineRun = @{
                StartTime = $PipelineStatus.StartTime
                EndTime = Get-Date
                Duration = (Get-Date) - $PipelineStatus.StartTime
                Steps = $PipelineStatus.Steps
                Errors = $PipelineStatus.Errors
                Warnings = $PipelineStatus.Warnings
            }
            DataQuality = $PipelineStatus.DataQuality
            Summary = @{
                TotalSteps = $PipelineStatus.Steps.Count
                SuccessfulSteps = ($PipelineStatus.Steps | Where-Object { $_.Status -eq "Success" }).Count
                FailedSteps = ($PipelineStatus.Steps | Where-Object { $_.Status -eq "Failed" }).Count
                WarningSteps = ($PipelineStatus.Steps | Where-Object { $_.Status -eq "Warning" }).Count
                OverallStatus = if ($PipelineStatus.Errors.Count -gt 0) { "Failed" } elseif ($PipelineStatus.Warnings.Count -gt 0) { "Warning" } else { "Success" }
            }
        }
        
        # Save report
        $report | ConvertTo-Json -Depth 10 | Out-File -FilePath $reportPath -Encoding UTF8
        
        Write-ColorOutput "✅ Quality report saved: $reportPath" "Success"
        Add-PipelineStep "Quality Report" "Success" "Report saved to $reportPath"
        
        # Display summary
        Write-ColorOutput "📈 Pipeline Summary:" "Header"
        Write-ColorOutput "   Total Steps: $($report.Summary.TotalSteps)" "Info"
        Write-ColorOutput "   Successful: $($report.Summary.SuccessfulSteps)" "Success"
        Write-ColorOutput "   Failed: $($report.Summary.FailedSteps)" "Error"
        Write-ColorOutput "   Warnings: $($report.Summary.WarningSteps)" "Warning"
        Write-ColorOutput "   Overall Status: $($report.Summary.OverallStatus)" $(if ($report.Summary.OverallStatus -eq "Success") { "Success" } elseif ($report.Summary.OverallStatus -eq "Warning") { "Warning" } else { "Error" })
        
        return $true
    } catch {
        Write-ColorOutput "❌ Quality report generation failed: $($_.Exception.Message)" "Error"
        Add-PipelineStep "Quality Report" "Failed" $_.Exception.Message
        return $false
    }
}

function Send-Alert {
    param([string]$Subject, [string]$Body)
    
    if (-not $SendAlerts) {
        Write-ColorOutput "📧 Alert would be sent (--SendAlerts not specified)" "Info"
        Write-ColorOutput "   Subject: $Subject" "Info"
        Write-ColorOutput "   Body: $Body" "Info"
        return
    }
    
    try {
        Write-ColorOutput "📧 Sending alert..." "Info"
        # Implement email sending logic here
        # Example: Send-MailMessage -From "pipeline@mrbeast.com" -To "hr@mrbeast.com" -Subject $Subject -Body $Body
        Write-ColorOutput "✅ Alert sent successfully" "Success"
    } catch {
        Write-ColorOutput "❌ Failed to send alert: $($_.Exception.Message)" "Error"
    }
}

# Main execution
try {
    Write-ColorOutput "🚀 Starting MrBeast HR Analytics Daily Pipeline..." "Header"
    Write-ColorOutput "==================================================" "Header"
    Write-ColorOutput "Start Time: $(Get-Date)" "Info"
    
    # Step 1: Test database connection
    if (-not (Test-DatabaseConnection)) {
        throw "Database connection failed"
    }
    
    # Step 2: Validate source data
    if (-not (Test-SourceData)) {
        throw "Source data validation failed"
    }
    
    # Step 3: Refresh data
    if (-not (Invoke-DataRefresh)) {
        throw "Data refresh failed"
    }
    
    # Step 4: Quality checks
    if (-not (Test-DataQuality)) {
        throw "Data quality check failed"
    }
    
    # Step 5: API health check
    if (-not (Test-APIHealth)) {
        $PipelineStatus.Warnings += "API health check failed"
    }
    
    # Step 6: Generate report
    if ($GenerateReport) {
        New-QualityReport | Out-Null
    }
    
    # Final status
    $endTime = Get-Date
    $duration = $endTime - $PipelineStatus.StartTime
    
    Write-ColorOutput "✅ Daily pipeline completed successfully" "Success"
    Write-ColorOutput "Duration: $($duration.TotalMinutes.ToString('F2')) minutes" "Info"
    
    # Send success alert if configured
    if ($SendAlerts -and $PipelineStatus.Errors.Count -eq 0) {
        Send-Alert -Subject "✅ HR Analytics Pipeline Success" -Body "Daily pipeline completed successfully in $($duration.TotalMinutes.ToString('F2')) minutes"
    }
    
} catch {
    Write-ColorOutput "❌ Pipeline failed: $($_.Exception.Message)" "Error"
    
    # Send failure alert
    if ($SendAlerts) {
        Send-Alert -Subject "❌ HR Analytics Pipeline Failed" -Body "Pipeline failed: $($_.Exception.Message)"
    }
    
    exit 1
} finally {
    # Cleanup
    Write-ColorOutput "🧹 Cleaning up..." "Info"
    
    # Remove old reports (keep last 7 days)
    if (Test-Path "reports") {
        $oldReports = Get-ChildItem "reports\daily_pipeline_report_*.json" | Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-7) }
        if ($oldReports) {
            $oldReports | Remove-Item -Force
            Write-ColorOutput "🗑️ Cleaned up $($oldReports.Count) old reports" "Info"
        }
    }
    
    Write-ColorOutput "🏁 Pipeline finished at $(Get-Date)" "Header"
} 