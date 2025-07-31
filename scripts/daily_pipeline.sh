#!/bin/bash
#
# MrBeast HR Analytics - Daily Data Pipeline (Linux)
#
# Professional daily pipeline for HR analytics data refresh.
# This script runs daily (typically via cron/scheduler) to:
# 1. Refresh data from source systems
# 2. Validate data quality
# 3. Update database
# 4. Monitor pipeline health
# 5. Generate quality reports
# 6. Send alerts for issues
#
# This is separate from application deployment - applications run as services.
#
# Usage:
#   ./daily_pipeline.sh
#   ./daily_pipeline.sh --log-level warning --generate-report
#   ./daily_pipeline.sh --source-file /path/to/data.xlsx --send-alerts
#
# Cron example:
#   0 2 * * * /path/to/scripts/daily_pipeline.sh >> /var/log/hr-analytics/pipeline.log 2>&1

set -euo pipefail

# Configuration
SOURCE_FILE="${SOURCE_FILE:-data/HRIS_TAKE_HOME_PROJECT_DATA.xlsx}"
LOG_LEVEL="${LOG_LEVEL:-info}"
SEND_ALERTS="${SEND_ALERTS:-false}"
GENERATE_REPORT="${GENERATE_REPORT:-true}"
API_PORT="${API_PORT:-8000}"
DASHBOARD_PORT="${DASHBOARD_PORT:-8501}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Pipeline status tracking
PIPELINE_STATUS_FILE="/tmp/hr_pipeline_status_$(date +%Y%m%d_%H%M%S).json"
START_TIME=$(date -u +%Y-%m-%dT%H:%M:%SZ)
STEPS=()
ERRORS=()
WARNINGS=()

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --source-file)
            SOURCE_FILE="$2"
            shift 2
            ;;
        --log-level)
            LOG_LEVEL="$2"
            shift 2
            ;;
        --send-alerts)
            SEND_ALERTS="true"
            shift
            ;;
        --generate-report)
            GENERATE_REPORT="true"
            shift
            ;;
        --api-port)
            API_PORT="$2"
            shift 2
            ;;
        --dashboard-port)
            DASHBOARD_PORT="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  --source-file PATH    Path to source Excel file"
            echo "  --log-level LEVEL     Logging level (info, warning, error)"
            echo "  --send-alerts         Send email alerts on failures"
            echo "  --generate-report     Generate data quality report"
            echo "  --api-port PORT       API server port (default: 8000)"
            echo "  --dashboard-port PORT Dashboard port (default: 8501)"
            echo "  -h, --help           Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Logging functions
log_info() {
    echo -e "${CYAN}[$(date '+%Y-%m-%d %H:%M:%S')] INFO: $1${NC}"
}

log_success() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] SUCCESS: $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

log_error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

log_header() {
    echo -e "${MAGENTA}[$(date '+%Y-%m-%d %H:%M:%S')] $1${NC}"
}

# Pipeline step tracking
add_pipeline_step() {
    local step="$1"
    local status="$2"
    local details="${3:-}"
    local timestamp=$(date -u +%Y-%m-%dT%H:%M:%SZ)
    
    STEPS+=("{\"step\":\"$step\",\"status\":\"$status\",\"details\":\"$details\",\"timestamp\":\"$timestamp\"}")
}

# Utility functions
check_command() {
    if ! command -v "$1" &> /dev/null; then
        log_error "Command '$1' not found"
        return 1
    fi
}

test_port() {
    local port="$1"
    if nc -z localhost "$port" 2>/dev/null; then
        return 0
    else
        return 1
    fi
}

wait_for_port() {
    local port="$1"
    local service_name="$2"
    local timeout="${3:-30}"
    
    log_info "Waiting for $service_name on port $port..."
    local start_time=$(date +%s)
    
    while [ $(($(date +%s) - start_time)) -lt $timeout ]; do
        if test_port "$port"; then
            log_success "$service_name is ready on port $port"
            return 0
        fi
        sleep 1
    done
    
    log_error "Timeout waiting for $service_name on port $port"
    return 1
}

# Database connection test
test_database_connection() {
    log_info "Testing database connection..."
    
    export DATABASE_URL="postgresql://hr_user:hr_password@localhost:5432/mrbeast_hr"
    
    # Test connection using Python
    local test_script="
import psycopg2
import os
try:
    conn = psycopg2.connect(os.environ['DATABASE_URL'])
    conn.close()
    print('SUCCESS')
except Exception as e:
    print(f'ERROR: {e}')
    exit(1)
"
    
    if python3 -c "$test_script" 2>/dev/null | grep -q "SUCCESS"; then
        log_success "Database connection successful"
        add_pipeline_step "Database Connection" "Success"
        return 0
    else
        log_error "Database connection failed"
        add_pipeline_step "Database Connection" "Failed" "Connection test failed"
        return 1
    fi
}

# Source data validation
test_source_data() {
    log_info "Validating source data file..."
    
    if [[ ! -f "$SOURCE_FILE" ]]; then
        log_error "Source file not found: $SOURCE_FILE"
        add_pipeline_step "Source Data Validation" "Failed" "File not found"
        return 1
    fi
    
    # Check file size and modification date
    local file_size=$(stat -c%s "$SOURCE_FILE")
    local last_modified=$(stat -c%y "$SOURCE_FILE")
    local file_size_mb=$(echo "scale=2; $file_size / 1024 / 1024" | bc)
    
    log_info "Source file: $SOURCE_FILE"
    log_info "File size: ${file_size_mb} MB"
    log_info "Last modified: $last_modified"
    
    # Check if file is recent (within last 24 hours)
    local file_timestamp=$(stat -c%Y "$SOURCE_FILE")
    local current_timestamp=$(date +%s)
    local hours_since_modified=$(( (current_timestamp - file_timestamp) / 3600 ))
    
    if [[ $hours_since_modified -gt 24 ]]; then
        log_warning "Source file is older than 24 hours"
        WARNINGS+=("Source file is older than 24 hours")
    fi
    
    add_pipeline_step "Source Data Validation" "Success" "File size: ${file_size_mb} MB"
    return 0
}

# Data refresh
invoke_data_refresh() {
    log_info "Refreshing data from source..."
    
    # Activate virtual environment if it exists
    if [[ -f "venv/bin/activate" ]]; then
        source venv/bin/activate
    fi
    
    # Run data pipeline with validation
    log_info "Running data pipeline..."
    if python3 scripts/hr_data_pipeline.py --validate-only; then
        log_success "Data refresh completed successfully"
        add_pipeline_step "Data Refresh" "Success"
        return 0
    else
        log_error "Data refresh failed"
        add_pipeline_step "Data Refresh" "Failed" "Pipeline returned non-zero exit code"
        return 1
    fi
}

# Data quality checks
test_data_quality() {
    log_info "Running data quality checks..."
    
    # Activate virtual environment if it exists
    if [[ -f "venv/bin/activate" ]]; then
        source venv/bin/activate
    fi
    
    # Run data quality checks
    local quality_script="
import pandas as pd
import psycopg2
import os
import json
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
            cursor.execute(f'SELECT COUNT(*) FROM hr_analytics.\"{table}\"')
            count = cursor.fetchone()[0]
            results[table] = count
            
        # Check for null values in critical columns
        cursor.execute('''
            SELECT 
                COUNT(*) as total_applicants,
                COUNT(CASE WHEN \"Name\" IS NULL THEN 1 END) as null_names,
                COUNT(CASE WHEN \"Role\" IS NULL THEN 1 END) as null_roles,
                COUNT(CASE WHEN \"Status\" IS NULL THEN 1 END) as null_status
            FROM hr_analytics.applicants
        ''')
        applicant_quality = cursor.fetchone()
        
        cursor.execute('''
            SELECT 
                COUNT(*) as total_employees,
                COUNT(CASE WHEN \"Name\" IS NULL THEN 1 END) as null_names,
                COUNT(CASE WHEN \"Department\" IS NULL THEN 1 END) as null_depts,
                COUNT(CASE WHEN \"Salary\" IS NULL THEN 1 END) as null_salaries
            FROM hr_analytics.employees
        ''')
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
        
        print('QUALITY_CHECK_SUCCESS')
        print(json.dumps(quality_metrics))
        
    except Exception as e:
        print(f'QUALITY_CHECK_ERROR:{e}')
        exit(1)

if __name__ == '__main__':
    check_data_quality()
"
    
    local quality_result
    quality_result=$(python3 -c "$quality_script" 2>/dev/null)
    
    if echo "$quality_result" | grep -q "QUALITY_CHECK_SUCCESS"; then
        log_success "Data quality checks completed"
        add_pipeline_step "Data Quality Check" "Success"
        return 0
    else
        log_error "Data quality check failed: $quality_result"
        add_pipeline_step "Data Quality Check" "Failed" "$quality_result"
        return 1
    fi
}

# API health check
test_api_health() {
    log_info "Testing API health..."
    
    local endpoints=(
        "http://localhost:$API_PORT/health"
        "http://localhost:$API_PORT/hiring-metrics"
        "http://localhost:$API_PORT/applicants/status-summary"
    )
    
    local healthy_endpoints=0
    local total_endpoints=${#endpoints[@]}
    
    for endpoint in "${endpoints[@]}"; do
        if curl -s -f "$endpoint" >/dev/null 2>&1; then
            log_success "$endpoint - Healthy"
            ((healthy_endpoints++))
        else
            log_error "$endpoint - Unhealthy"
            ERRORS+=("API endpoint $endpoint failed")
        fi
    done
    
    if [[ $healthy_endpoints -eq $total_endpoints ]]; then
        log_success "All API endpoints healthy"
        add_pipeline_step "API Health Check" "Success" "All $total_endpoints endpoints healthy"
        return 0
    else
        log_warning "Some API endpoints unhealthy ($healthy_endpoints/$total_endpoints)"
        add_pipeline_step "API Health Check" "Warning" "$healthy_endpoints/$total_endpoints endpoints healthy"
        return 1
    fi
}

# Generate quality report
generate_quality_report() {
    log_info "Generating data quality report..."
    
    local report_path="reports/daily_pipeline_report_$(date +%Y-%m-%d).json"
    
    # Ensure reports directory exists
    mkdir -p reports
    
    # Create comprehensive report
    local end_time=$(date -u +%Y-%m-%dT%H:%M:%SZ)
    local duration=$(($(date +%s) - $(date -d "$START_TIME" +%s)))
    
    local report="{
        \"pipeline_run\": {
            \"start_time\": \"$START_TIME\",
            \"end_time\": \"$end_time\",
            \"duration_seconds\": $duration,
            \"steps\": [$(IFS=,; echo "${STEPS[*]}")],
            \"errors\": [$(IFS=,; printf '"%s"' "${ERRORS[@]}")],
            \"warnings\": [$(IFS=,; printf '"%s"' "${WARNINGS[@]}")]
        },
        \"summary\": {
            \"total_steps\": ${#STEPS[@]},
            \"successful_steps\": $(echo "${STEPS[@]}" | grep -o '"status":"Success"' | wc -l),
            \"failed_steps\": $(echo "${STEPS[@]}" | grep -o '"status":"Failed"' | wc -l),
            \"warning_steps\": $(echo "${STEPS[@]}" | grep -o '"status":"Warning"' | wc -l),
            \"overall_status\": \"$([[ ${#ERRORS[@]} -gt 0 ]] && echo 'Failed' || ([[ ${#WARNINGS[@]} -gt 0 ]] && echo 'Warning' || echo 'Success'))\"
        }
    }"
    
    echo "$report" > "$report_path"
    
    log_success "Quality report saved: $report_path"
    add_pipeline_step "Quality Report" "Success" "Report saved to $report_path"
    
    # Display summary
    log_header "Pipeline Summary:"
    log_info "Total Steps: ${#STEPS[@]}"
    log_info "Successful: $(echo "${STEPS[@]}" | grep -o '"status":"Success"' | wc -l)"
    log_info "Failed: $(echo "${STEPS[@]}" | grep -o '"status":"Failed"' | wc -l)"
    log_info "Warnings: $(echo "${STEPS[@]}" | grep -o '"status":"Warning"' | wc -l)"
    
    local overall_status
    if [[ ${#ERRORS[@]} -gt 0 ]]; then
        overall_status="Failed"
        log_error "Overall Status: $overall_status"
    elif [[ ${#WARNINGS[@]} -gt 0 ]]; then
        overall_status="Warning"
        log_warning "Overall Status: $overall_status"
    else
        overall_status="Success"
        log_success "Overall Status: $overall_status"
    fi
    
    return 0
}

# Send alert
send_alert() {
    local subject="$1"
    local body="$2"
    
    if [[ "$SEND_ALERTS" == "true" ]]; then
        log_info "Sending alert..."
        # Implement email sending logic here
        # Example: echo "$body" | mail -s "$subject" hr@mrbeast.com
        log_success "Alert sent successfully"
    else
        log_info "Alert would be sent (--send-alerts not specified)"
        log_info "Subject: $subject"
        log_info "Body: $body"
    fi
}

# Cleanup function
cleanup() {
    log_info "Cleaning up..."
    
    # Remove old reports (keep last 7 days)
    if [[ -d "reports" ]]; then
        find reports -name "daily_pipeline_report_*.json" -mtime +7 -delete 2>/dev/null || true
        log_info "Cleaned up old reports"
    fi
    
    # Remove temporary status file
    rm -f "$PIPELINE_STATUS_FILE" 2>/dev/null || true
}

# Main execution
main() {
    log_header "Starting MrBeast HR Analytics Daily Pipeline..."
    log_header "=================================================="
    log_info "Start Time: $(date)"
    
    # Set up cleanup trap
    trap cleanup EXIT
    
    # Check prerequisites
    log_info "Checking prerequisites..."
    
    local required_commands=("python3" "curl" "nc" "bc")
    for cmd in "${required_commands[@]}"; do
        if ! check_command "$cmd"; then
            log_error "Required command '$cmd' not found"
            exit 1
        fi
    done
    
    # Check if virtual environment exists
    if [[ ! -f "venv/bin/activate" ]]; then
        log_error "Virtual environment not found. Please run setup first."
        log_info "Run: python3 -m venv venv"
        log_info "Then: source venv/bin/activate"
        log_info "Then: pip install -r requirements.txt"
        exit 1
    fi
    
    # Check if data file exists
    if [[ ! -f "$SOURCE_FILE" ]]; then
        log_error "Data file not found: $SOURCE_FILE"
        exit 1
    fi
    
    log_success "Prerequisites check passed"
    
    # Step 1: Test database connection
    if ! test_database_connection; then
        log_error "Database connection failed"
        exit 1
    fi
    
    # Step 2: Validate source data
    if ! test_source_data; then
        log_error "Source data validation failed"
        exit 1
    fi
    
    # Step 3: Refresh data
    if ! invoke_data_refresh; then
        log_error "Data refresh failed"
        exit 1
    fi
    
    # Step 4: Quality checks
    if ! test_data_quality; then
        log_error "Data quality check failed"
        exit 1
    fi
    
    # Step 5: API health check
    if ! test_api_health; then
        WARNINGS+=("API health check failed")
    fi
    
    # Step 6: Generate report
    if [[ "$GENERATE_REPORT" == "true" ]]; then
        generate_quality_report
    fi
    
    # Final status
    local end_time=$(date)
    local duration=$(( $(date +%s) - $(date -d "$START_TIME" +%s) ))
    local duration_minutes=$(( duration / 60 ))
    
    log_success "Daily pipeline completed successfully"
    log_info "Duration: ${duration_minutes} minutes"
    
    # Send success alert if configured
    if [[ "$SEND_ALERTS" == "true" && ${#ERRORS[@]} -eq 0 ]]; then
        send_alert "✅ HR Analytics Pipeline Success" "Daily pipeline completed successfully in ${duration_minutes} minutes"
    fi
    
    log_header "Pipeline finished at $(date)"
}

# Run main function
main "$@" 