#!/bin/bash
#
# MrBeast HR Analytics - Dashboard Runner (Linux)
#
# Development script for starting the Streamlit dashboard.
# This is the Linux equivalent of run_dashboard.ps1
#
# Usage:
#   ./run_dashboard.sh
#   ./run_dashboard.sh --host localhost --port 8502
#   ./run_dashboard.sh --help

set -euo pipefail

# Configuration
HOST="${HOST:-localhost}"
PORT="${PORT:-8501}"

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

check_api_health() {
    local api_url="http://localhost:8000/health"
    local timeout=5
    
    log_info "Checking API health..."
    
    if curl -s -f --max-time "$timeout" "$api_url" >/dev/null 2>&1; then
        log_success "API is healthy"
        return 0
    else
        log_error "API is not responding"
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
            echo "  --host HOST    Host to bind to (default: localhost)"
            echo "  --port PORT    Port to bind to (default: 8501)"
            echo "  -h, --help     Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                    # Start with default settings"
            echo "  $0 --host 0.0.0.0    # Start on all interfaces"
            echo "  $0 --port 8502       # Start on port 8502"
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
    log_header "MrBeast HR Analytics Dashboard"
    log_header "=============================="
    
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
    
    # Check if dashboard.py exists
    if [[ ! -f "dashboard.py" ]]; then
        log_error "Dashboard file not found: dashboard.py"
        exit 1
    fi
    
    # Check required commands
    local required_commands=("python3" "pip" "streamlit" "curl" "nc")
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
    
    # Check API health before starting dashboard
    if ! check_api_health; then
        log_error "API is not running. Please start the API first:"
        log_info "  cd ../api && ./run_api.sh"
        log_info "  Or run: python3 ../api/main.py"
        exit 1
    fi
    
    log_success "Prerequisites check passed"
    
    # Activate virtual environment
    log_info "Activating virtual environment..."
    source ../venv/bin/activate
    
    # Start the dashboard
    log_info "Starting Streamlit dashboard..."
    log_info "Host: $HOST"
    log_info "Port: $PORT"
    log_info "Dashboard URL: http://$HOST:$PORT"
    
    # Run the dashboard
    if streamlit run dashboard.py --server.port "$PORT" --server.address "$HOST"; then
        log_success "Dashboard stopped gracefully"
    else
        log_error "Dashboard failed to start or crashed"
        exit 1
    fi
}

# Run main function
main "$@" 