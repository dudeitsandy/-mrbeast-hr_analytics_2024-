#!/bin/bash
#
# MrBeast HR Analytics - API Runner (Linux)
#
# Development script for starting the FastAPI server.
# This is the Linux equivalent of run_api.ps1
#
# Usage:
#   ./run_api.sh
#   ./run_api.sh --host 0.0.0.0 --port 8001
#   ./run_api.sh --help

set -euo pipefail

# Configuration
HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8000}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

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

test_port() {
    local port="$1"
    if nc -z localhost "$port" 2>/dev/null; then
        return 0
    else
        return 1
    fi
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --host)
            HOST="$2"
            shift 2
            ;;
        --port)
            PORT="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --host HOST    Host to bind to (default: 0.0.0.0)"
            echo "  --port PORT    Port to bind to (default: 8000)"
            echo "  -h, --help     Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                    # Start with default settings"
            echo "  $0 --host 127.0.0.1  # Start on localhost only"
            echo "  $0 --port 8001       # Start on port 8001"
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
    log_header "MrBeast HR Analytics API"
    log_header "========================="
    
    # Check prerequisites
    log_info "Checking prerequisites..."
    
    # Check if virtual environment exists
    if [[ ! -f "../venv/bin/activate" ]]; then
        log_error "Virtual environment not found. Please run setup first."
        log_info "Run: python3 -m venv venv"
        log_info "Then: source venv/bin/activate"
        log_info "Then: pip install -r requirements.txt"
        exit 1
    fi
    
    # Check if main.py exists
    if [[ ! -f "main.py" ]]; then
        log_error "API file not found: main.py"
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
    
    # Check if port is available
    if test_port "$PORT"; then
        log_warning "Port $PORT is already in use"
        log_info "You may need to stop the existing service or use a different port"
    fi
    
    log_success "Prerequisites check passed"
    
    # Set environment variables
    export DATABASE_URL="postgresql://hr_user:hr_password@localhost:5432/mrbeast_hr"
    
    # Activate virtual environment
    log_info "Activating virtual environment..."
    source ../venv/bin/activate
    
    # Start the API server
    log_info "Starting FastAPI server..."
    log_info "Host: $HOST"
    log_info "Port: $PORT"
    log_info "API Documentation: http://$HOST:$PORT/docs"
    log_info "Health Check: http://$HOST:$PORT/health"
    
    # Run the API server
    if python3 main.py --host "$HOST" --port "$PORT"; then
        log_success "API server stopped gracefully"
    else
        log_error "API server failed to start or crashed"
        exit 1
    fi
}

# Run main function
main "$@" 