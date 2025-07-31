#!/bin/bash
#
# MrBeast HR Analytics - Service Management (Linux)
#
# Manages the continuous running of HR analytics applications as services.
# This handles the "always-on" applications that run continuously:
# - FastAPI server (API)
# - Streamlit dashboard
# - PostgreSQL database (Docker)
#
# This is separate from the daily pipeline - these services run continuously.
#
# Usage:
#   ./manage_services.sh start all
#   ./manage_services.sh status
#   ./manage_services.sh logs api
#   ./manage_services.sh restart dashboard
#
# Systemd service example:
#   sudo systemctl enable hr-analytics-api
#   sudo systemctl start hr-analytics-api

set -euo pipefail

# Configuration
API_PORT="${API_PORT:-8000}"
DASHBOARD_PORT="${DASHBOARD_PORT:-8501}"
API_HOST="${API_HOST:-0.0.0.0}"
DASHBOARD_HOST="${DASHBOARD_HOST:-localhost}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Service definitions
declare -A SERVICES=(
    ["api"]="HR Analytics API"
    ["dashboard"]="HR Analytics Dashboard"
)

declare -A SERVICE_SCRIPTS=(
    ["api"]="api/main.py"
    ["dashboard"]="dashboard.py"
)

declare -A SERVICE_PORTS=(
    ["api"]="$API_PORT"
    ["dashboard"]="$DASHBOARD_PORT"
)

declare -A SERVICE_WORKDIRS=(
    ["api"]="api"
    ["dashboard"]="visualizations"
)

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

get_service_pid() {
    local service_name="$1"
    local port="${SERVICE_PORTS[$service_name]}"
    
    # Find process using the port
    local pid
    pid=$(lsof -ti:"$port" 2>/dev/null | head -1)
    
    if [[ -n "$pid" ]]; then
        echo "$pid"
    else
        echo ""
    fi
}

get_service_status() {
    local service_name="$1"
    local port="${SERVICE_PORTS[$service_name]}"
    local service_display="${SERVICES[$service_name]}"
    
    local pid
    pid=$(get_service_pid "$service_name")
    local port_in_use
    port_in_use=$(test_port "$port" && echo "true" || echo "false")
    
    if [[ -n "$pid" && "$port_in_use" == "true" ]]; then
        local uptime
        uptime=$(ps -o etime= -p "$pid" 2>/dev/null || echo "unknown")
        echo "Running|$pid|$port|$uptime"
    elif [[ -n "$pid" && "$port_in_use" == "false" ]]; then
        local uptime
        uptime=$(ps -o etime= -p "$pid" 2>/dev/null || echo "unknown")
        echo "Process Running (Port Unavailable)|$pid|$port|$uptime"
    elif [[ -z "$pid" && "$port_in_use" == "true" ]]; then
        echo "Port in Use (Process Unknown)||$port|unknown"
    else
        echo "Stopped||$port|unknown"
    fi
}

start_service() {
    local service_name="$1"
    local port="${SERVICE_PORTS[$service_name]}"
    local service_display="${SERVICES[$service_name]}"
    local script="${SERVICE_SCRIPTS[$service_name]}"
    local workdir="${SERVICE_WORKDIRS[$service_name]}"
    
    log_info "Starting $service_display..."
    
    # Check if already running
    local status
    status=$(get_service_status "$service_name")
    local current_status
    current_status=$(echo "$status" | cut -d'|' -f1)
    
    if [[ "$current_status" == "Running" ]]; then
        log_warning "$service_display is already running"
        return 0
    fi
    
    # Kill any existing processes on the port
    if test_port "$port"; then
        log_warning "Port $port is in use. Attempting to free it..."
        local existing_pid
        existing_pid=$(lsof -ti:"$port" 2>/dev/null | head -1)
        if [[ -n "$existing_pid" ]]; then
            kill -9 "$existing_pid" 2>/dev/null || true
            log_info "Killed process $existing_pid"
        fi
    fi
    
    # Activate virtual environment if it exists
    if [[ -f "venv/bin/activate" ]]; then
        source venv/bin/activate
    fi
    
    # Set working directory
    pushd "$workdir" >/dev/null
    
    # Start service in background
    if [[ "$service_name" == "api" ]]; then
        export DATABASE_URL="postgresql://hr_user:hr_password@localhost:5432/mrbeast_hr"
        nohup python3 "../$script" --host "$API_HOST" --port "$port" > "../logs/api.log" 2>&1 &
        local pid=$!
    else
        nohup streamlit run "$script" --server.port "$port" --server.address "$DASHBOARD_HOST" > "../logs/dashboard.log" 2>&1 &
        local pid=$!
    fi
    
    # Wait for service to start
    log_info "Waiting for $service_display to start..."
    local start_time=$(date +%s)
    local timeout=30
    
    while [[ $(($(date +%s) - start_time)) -lt $timeout ]]; do
        if test_port "$port"; then
            log_success "$service_display started successfully (PID: $pid)"
            popd >/dev/null
            return 0
        fi
        sleep 1
    done
    
    log_error "Timeout waiting for $service_display to start"
    kill -9 "$pid" 2>/dev/null || true
    popd >/dev/null
    return 1
}

stop_service() {
    local service_name="$1"
    local port="${SERVICE_PORTS[$service_name]}"
    local service_display="${SERVICES[$service_name]}"
    
    log_info "Stopping $service_display..."
    
    # Find and stop processes
    local pid
    pid=$(get_service_pid "$service_name")
    
    if [[ -n "$pid" ]]; then
        kill -TERM "$pid" 2>/dev/null || true
        sleep 2
        if kill -0 "$pid" 2>/dev/null; then
            kill -9 "$pid" 2>/dev/null || true
            log_info "Force killed process $pid"
        else
            log_success "Stopped process $pid"
        fi
    else
        log_warning "No running processes found for $service_display"
    fi
    
    # Kill any remaining processes on the port
    local remaining_pid
    remaining_pid=$(lsof -ti:"$port" 2>/dev/null | head -1)
    if [[ -n "$remaining_pid" ]]; then
        kill -9 "$remaining_pid" 2>/dev/null || true
        log_info "Killed remaining process on port $port"
    fi
}

show_service_status() {
    local service_name="${1:-all}"
    
    log_header "Service Status"
    log_header "=============="
    
    if [[ "$service_name" == "all" ]]; then
        for service_key in "${!SERVICES[@]}"; do
            show_service_status "$service_key"
        done
    else
        local service_display="${SERVICES[$service_name]}"
        local status
        status=$(get_service_status "$service_name")
        
        local status_text
        status_text=$(echo "$status" | cut -d'|' -f1)
        local pid
        pid=$(echo "$status" | cut -d'|' -f2)
        local port
        port=$(echo "$status" | cut -d'|' -f3)
        local uptime
        uptime=$(echo "$status" | cut -d'|' -f4)
        
        log_info "$service_display:"
        case "$status_text" in
            "Running")
                log_success "  Status: $status_text"
                ;;
            "Stopped")
                log_error "  Status: $status_text"
                ;;
            *)
                log_warning "  Status: $status_text"
                ;;
        esac
        log_info "  Port: $port"
        
        if [[ -n "$pid" ]]; then
            log_info "  Process ID: $pid"
        fi
        
        if [[ "$uptime" != "unknown" ]]; then
            log_info "  Uptime: $uptime"
        fi
        
        echo ""
    fi
}

show_service_logs() {
    local service_name="$1"
    local service_display="${SERVICES[$service_name]}"
    
    log_header "Logs for $service_display"
    log_header "========================"
    
    local log_file="logs/${service_name}.log"
    
    if [[ -f "$log_file" ]]; then
        log_info "Recent logs from $log_file:"
        echo "----------------------------------------"
        tail -n 20 "$log_file" 2>/dev/null || echo "No recent logs found"
        echo "----------------------------------------"
        log_info "Full log file: $log_file"
    else
        log_warning "Log file not found: $log_file"
    fi
    
    # Check if service is running and show process info
    local status
    status=$(get_service_status "$service_name")
    local pid
    pid=$(echo "$status" | cut -d'|' -f2)
    
    if [[ -n "$pid" ]]; then
        log_info "Process $pid is running"
        log_info "Use 'ps -p $pid' for more details"
    fi
}

# Main execution
main() {
    local action="${1:-status}"
    local service="${2:-all}"
    
    log_header "MrBeast HR Analytics Service Management"
    log_header "======================================="
    
    # Check prerequisites
    if [[ ! -f "venv/bin/activate" ]]; then
        log_error "Virtual environment not found. Please run setup first."
        exit 1
    fi
    
    # Check required commands
    local required_commands=("python3" "nc" "lsof" "ps" "kill" "nohup")
    for cmd in "${required_commands[@]}"; do
        if ! check_command "$cmd"; then
            log_error "Required command '$cmd' not found"
            exit 1
        fi
    done
    
    # Ensure logs directory exists
    mkdir -p logs
    
    # Execute action
    case "$action" in
        "start")
            if [[ "$service" == "all" ]]; then
                for service_name in "${!SERVICES[@]}"; do
                    start_service "$service_name"
                done
            else
                if [[ -n "${SERVICES[$service]:-}" ]]; then
                    start_service "$service"
                else
                    log_error "Unknown service: $service"
                    exit 1
                fi
            fi
            ;;
        "stop")
            if [[ "$service" == "all" ]]; then
                for service_name in "${!SERVICES[@]}"; do
                    stop_service "$service_name"
                done
            else
                if [[ -n "${SERVICES[$service]:-}" ]]; then
                    stop_service "$service"
                else
                    log_error "Unknown service: $service"
                    exit 1
                fi
            fi
            ;;
        "restart")
            if [[ "$service" == "all" ]]; then
                for service_name in "${!SERVICES[@]}"; do
                    log_info "Restarting ${SERVICES[$service_name]}..."
                    stop_service "$service_name"
                    sleep 2
                    start_service "$service_name"
                done
            else
                if [[ -n "${SERVICES[$service]:-}" ]]; then
                    log_info "Restarting ${SERVICES[$service]}..."
                    stop_service "$service"
                    sleep 2
                    start_service "$service"
                else
                    log_error "Unknown service: $service"
                    exit 1
                fi
            fi
            ;;
        "status")
            show_service_status "$service"
            ;;
        "logs")
            if [[ "$service" == "all" ]]; then
                log_warning "Please specify a service for logs: api or dashboard"
            else
                if [[ -n "${SERVICES[$service]:-}" ]]; then
                    show_service_logs "$service"
                else
                    log_error "Unknown service: $service"
                    exit 1
                fi
            fi
            ;;
        *)
            echo "Usage: $0 {start|stop|restart|status|logs} [service]"
            echo ""
            echo "Actions:"
            echo "  start    Start service(s)"
            echo "  stop     Stop service(s)"
            echo "  restart  Restart service(s)"
            echo "  status   Show service status"
            echo "  logs     Show service logs"
            echo ""
            echo "Services:"
            echo "  api       HR Analytics API"
            echo "  dashboard HR Analytics Dashboard"
            echo "  all       All services (default)"
            echo ""
            echo "Examples:"
            echo "  $0 start all"
            echo "  $0 status"
            echo "  $0 logs api"
            echo "  $0 restart dashboard"
            exit 1
            ;;
    esac
    
    log_header "Service management completed"
}

# Run main function
main "$@" 