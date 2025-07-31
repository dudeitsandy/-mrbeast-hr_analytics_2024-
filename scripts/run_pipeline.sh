#!/bin/bash
#
# MrBeast HR Analytics - Data Pipeline Runner (Linux)
#
# Development script for running the HR analytics data pipeline.
# This is the Linux equivalent of run_pipeline.ps1
#
# Usage:
#   ./run_pipeline.sh
#   ./run_pipeline.sh --validate-only
#   ./run_pipeline.sh --load-only
#   ./run_pipeline.sh --help

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Default arguments
VALIDATE_ONLY=false
LOAD_ONLY=false

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

# Utility functions
check_command() {
    if ! command -v "$1" &> /dev/null; then
        log_error "Command '$1' not found"
        return 1
    fi
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --validate-only)
            VALIDATE_ONLY=true
            shift
            ;;
        --load-only)
            LOAD_ONLY=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --validate-only    Run data validation only"
            echo "  --load-only        Run data loading only"
            echo "  -h, --help         Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                 # Run full pipeline (load + validate)"
            echo "  $0 --validate-only # Run validation only"
            echo "  $0 --load-only     # Run loading only"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Main execution
main() {
    log_header "MrBeast HR Analytics Data Pipeline"
    log_header "==================================="
    
    # Check prerequisites
    log_info "Checking prerequisites..."
    
    # Check if virtual environment exists
    if [[ ! -f "venv/bin/activate" ]]; then
        log_error "Virtual environment not found. Please run setup first."
        log_info "Run: python3 -m venv venv"
        log_info "Then: source venv/bin/activate"
        log_info "Then: pip install -r requirements.txt"
        exit 1
    fi
    
    # Check if data file exists
    if [[ ! -f "data/HRIS_TAKE_HOME_PROJECT_DATA.xlsx" ]]; then
        log_error "Data file not found: data/HRIS_TAKE_HOME_PROJECT_DATA.xlsx"
        exit 1
    fi
    
    # Check required commands
    local required_commands=("python3" "pip")
    for cmd in "${required_commands[@]}"; do
        if ! check_command "$cmd"; then
            log_error "Required command '$cmd' not found"
            exit 1
        fi
    done
    
    log_success "Prerequisites check passed"
    
    # Activate virtual environment
    log_info "Activating virtual environment..."
    source venv/bin/activate
    
    # Build Python arguments
    local python_args=()
    
    if [[ "$VALIDATE_ONLY" == "true" ]]; then
        python_args+=("--validate-only")
        log_info "Running validation only..."
    elif [[ "$LOAD_ONLY" == "true" ]]; then
        python_args+=("--load-only")
        log_info "Running loading only..."
    else
        log_info "Running full pipeline (load + validate)..."
    fi
    
    # Run the pipeline
    log_info "Executing data pipeline..."
    if python3 scripts/hr_data_pipeline.py "${python_args[@]}"; then
        log_success "Data pipeline completed successfully"
    else
        log_error "Data pipeline failed"
        exit 1
    fi
    
    log_header "Pipeline execution completed"
}

# Run main function
main "$@" 