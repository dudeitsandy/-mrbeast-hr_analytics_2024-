#!/bin/bash
# MrBeast HR Analytics - Master Controller
# Complete setup and deployment script for MrBeast HR Analytics.
# Handles database setup, API startup, and dashboard launch.

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Default values
API_PORT=8000
DASHBOARD_PORT=8501
SKIP_DATA_LOAD=false
CLEAR_DATABASE=false

# Function to print colored output
print_status() {
    local message="$1"
    local color="$2"
    echo -e "${color}${message}${NC}"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check prerequisites
check_prerequisites() {
    print_status "\n🔍 Checking Prerequisites..." "$CYAN"
    
    # Check Python
    if command_exists python3; then
        PYTHON_VERSION=$(python3 --version 2>&1)
        if [[ $PYTHON_VERSION =~ Python\ 3\.[8-9] ]] || [[ $PYTHON_VERSION =~ Python\ [4-9] ]]; then
            print_status "✅ Python: $PYTHON_VERSION" "$GREEN"
        else
            print_status "❌ Python 3.8+ required. Found: $PYTHON_VERSION" "$RED"
            return 1
        fi
    else
        print_status "❌ Python not found. Please install Python 3.8+" "$RED"
        return 1
    fi
    
    # Check PostgreSQL
    if command_exists psql; then
        PSQL_VERSION=$(psql --version 2>&1)
        if [[ $PSQL_VERSION =~ psql.*[0-9]+\.[0-9]+ ]]; then
            print_status "✅ PostgreSQL: $PSQL_VERSION" "$GREEN"
        else
            print_status "❌ PostgreSQL not found. Please install PostgreSQL 12+" "$RED"
            return 1
        fi
    else
        print_status "❌ PostgreSQL not found. Please install PostgreSQL 12+" "$RED"
        return 1
    fi
    
    # Check if virtual environment exists
    if [ -d "venv" ]; then
        print_status "✅ Virtual environment exists" "$GREEN"
    else
        print_status "⚠️ Virtual environment not found. Will create during setup." "$YELLOW"
    fi
    
    return 0
}

# Function to setup environment
setup_environment() {
    print_status "\n🔧 Setting up environment..." "$CYAN"
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        print_status "Creating virtual environment..." "$YELLOW"
        python3 -m venv venv
        if [ $? -ne 0 ]; then
            print_status "❌ Failed to create virtual environment" "$RED"
            return 1
        fi
    fi
    
    # Activate virtual environment
    print_status "Activating virtual environment..." "$YELLOW"
    source venv/bin/activate
    
    # Install dependencies
    print_status "Installing dependencies..." "$YELLOW"
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        print_status "❌ Failed to install dependencies" "$RED"
        return 1
    fi
    
    print_status "✅ Environment setup complete" "$GREEN"
    return 0
}

# Function to setup database
setup_database() {
    print_status "\n🗄️ Setting up database..." "$CYAN"
    
    # Clear database if requested
    if [ "$CLEAR_DATABASE" = true ]; then
        print_status "Clearing existing database..." "$YELLOW"
        ./scripts/clear_database.sh
        if [ $? -ne 0 ]; then
            print_status "❌ Failed to clear database" "$RED"
            return 1
        fi
    fi
    
    # Run data pipeline
    print_status "Running data pipeline..." "$YELLOW"
    ./scripts/run_pipeline.sh
    if [ $? -ne 0 ]; then
        print_status "❌ Failed to run data pipeline" "$RED"
        return 1
    fi
    
    print_status "✅ Database setup complete" "$GREEN"
    return 0
}

# Function to start services
start_services() {
    print_status "\n🚀 Starting services..." "$CYAN"
    
    # Check if services are already running
    API_PID=$(pgrep -f "python.*main.py" || echo "")
    DASHBOARD_PID=$(pgrep -f "streamlit.*dashboard.py" || echo "")
    
    if [ -n "$API_PID" ]; then
        print_status "⚠️ API is already running (PID: $API_PID)" "$YELLOW"
    else
        print_status "Starting API server..." "$YELLOW"
        python api/main.py &
        sleep 3
    fi
    
    if [ -n "$DASHBOARD_PID" ]; then
        print_status "⚠️ Dashboard is already running (PID: $DASHBOARD_PID)" "$YELLOW"
    else
        print_status "Starting dashboard..." "$YELLOW"
        streamlit run visualizations/dashboard.py --server.port $DASHBOARD_PORT &
        sleep 5
    fi
    
    # Test services
    print_status "Testing services..." "$YELLOW"
    
    # Test API
    if curl -s "http://localhost:$API_PORT/health" >/dev/null 2>&1; then
        print_status "✅ API is running and healthy" "$GREEN"
    else
        print_status "❌ API is not responding" "$RED"
        return 1
    fi
    
    # Test Dashboard
    if curl -s "http://localhost:$DASHBOARD_PORT" >/dev/null 2>&1; then
        print_status "✅ Dashboard is running" "$GREEN"
    else
        print_status "❌ Dashboard is not responding" "$RED"
        return 1
    fi
    
    print_status "\n🎉 All services are running!" "$GREEN"
    print_status "📊 Dashboard: http://localhost:$DASHBOARD_PORT" "$CYAN"
    print_status "🔌 API: http://localhost:$API_PORT" "$CYAN"
    print_status "📚 API Docs: http://localhost:$API_PORT/docs" "$CYAN"
    
    return 0
}

# Function to stop services
stop_services() {
    print_status "\n🛑 Stopping services..." "$CYAN"
    
    # Stop API
    API_PID=$(pgrep -f "python.*main.py" || echo "")
    if [ -n "$API_PID" ]; then
        print_status "Stopping API (PID: $API_PID)..." "$YELLOW"
        kill $API_PID 2>/dev/null || true
    fi
    
    # Stop Dashboard
    DASHBOARD_PID=$(pgrep -f "streamlit.*dashboard.py" || echo "")
    if [ -n "$DASHBOARD_PID" ]; then
        print_status "Stopping Dashboard (PID: $DASHBOARD_PID)..." "$YELLOW"
        kill $DASHBOARD_PID 2>/dev/null || true
    fi
    
    print_status "✅ All services stopped" "$GREEN"
}

# Function to get service status
get_service_status() {
    print_status "\n📊 Service Status:" "$CYAN"
    
    # Check API
    API_PID=$(pgrep -f "python.*main.py" || echo "")
    if [ -n "$API_PID" ]; then
        print_status "✅ API: Running (PID: $API_PID)" "$GREEN"
        if curl -s "http://localhost:8000/health" >/dev/null 2>&1; then
            print_status "   Health: OK" "$GREEN"
        else
            print_status "   Health: Not responding" "$RED"
        fi
    else
        print_status "❌ API: Not running" "$RED"
    fi
    
    # Check Dashboard
    DASHBOARD_PID=$(pgrep -f "streamlit.*dashboard.py" || echo "")
    if [ -n "$DASHBOARD_PID" ]; then
        print_status "✅ Dashboard: Running (PID: $DASHBOARD_PID)" "$GREEN"
        if curl -s "http://localhost:8501" >/dev/null 2>&1; then
            print_status "   Status: Responding" "$GREEN"
        else
            print_status "   Status: Not responding" "$RED"
        fi
    else
        print_status "❌ Dashboard: Not running" "$RED"
    fi
    
    # Check Database
    if psql -h localhost -U hr_user -d mrbeast_hr -c "SELECT 1;" >/dev/null 2>&1; then
        print_status "✅ Database: Connected" "$GREEN"
    else
        print_status "❌ Database: Not accessible" "$RED"
    fi
}

# Function to test system
test_system() {
    print_status "\n🧪 Testing system..." "$CYAN"
    
    # Test prerequisites
    if ! check_prerequisites; then
        print_status "❌ Prerequisites check failed" "$RED"
        return 1
    fi
    
    # Test database connection
    if psql -h localhost -U hr_user -d mrbeast_hr -c "SELECT 1;" >/dev/null 2>&1; then
        print_status "✅ Database connection: OK" "$GREEN"
    else
        print_status "❌ Database connection: Failed" "$RED"
        return 1
    fi
    
    # Test API endpoints
    if curl -s "http://localhost:8000/health" >/dev/null 2>&1; then
        print_status "✅ API health: OK" "$GREEN"
    else
        print_status "❌ API health: Failed" "$RED"
        return 1
    fi
    
    print_status "✅ All tests passed!" "$GREEN"
    return 0
}

# Function to show usage
show_usage() {
    echo "Usage: $0 <action> [options]"
    echo ""
    echo "Actions:"
    echo "  setup     - Setup environment and database"
    echo "  start     - Start services only"
    echo "  stop      - Stop all services"
    echo "  restart   - Restart all services"
    echo "  status    - Show service status"
    echo "  test      - Test system components"
    echo "  full      - Complete setup and start"
    echo ""
    echo "Options:"
    echo "  --skip-data-load    - Skip data loading"
    echo "  --clear-database    - Clear database before setup"
    echo "  --api-port <port>   - Custom API port (default: 8000)"
    echo "  --dashboard-port <port> - Custom dashboard port (default: 8501)"
    echo ""
    echo "Examples:"
    echo "  $0 full                    # Complete setup and start"
    echo "  $0 start                   # Start services only"
    echo "  $0 setup --clear-database  # Setup with fresh database"
    echo "  $0 status                  # Check service status"
}

# Parse command line arguments
ACTION=""
while [[ $# -gt 0 ]]; do
    case $1 in
        setup|start|stop|restart|status|test|full)
            ACTION="$1"
            shift
            ;;
        --skip-data-load)
            SKIP_DATA_LOAD=true
            shift
            ;;
        --clear-database)
            CLEAR_DATABASE=true
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
            show_usage
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Check if action is provided
if [ -z "$ACTION" ]; then
    echo "Error: Action is required"
    show_usage
    exit 1
fi

# Main execution
print_status "🚀 MrBeast HR Analytics - Master Controller" "$CYAN"
print_status "Action: $ACTION" "$YELLOW"

case $ACTION in
    "setup")
        if ! check_prerequisites; then
            print_status "❌ Prerequisites check failed. Please install required software." "$RED"
            exit 1
        fi
        
        if ! setup_environment; then
            print_status "❌ Environment setup failed." "$RED"
            exit 1
        fi
        
        if ! setup_database; then
            print_status "❌ Database setup failed." "$RED"
            exit 1
        fi
        
        print_status "\n✅ Setup complete! Run './run_master.sh start' to start services." "$GREEN"
        ;;
        
    "start")
        if ! start_services; then
            print_status "❌ Failed to start services." "$RED"
            exit 1
        fi
        ;;
        
    "stop")
        stop_services
        ;;
        
    "restart")
        stop_services
        sleep 2
        if ! start_services; then
            print_status "❌ Failed to restart services." "$RED"
            exit 1
        fi
        ;;
        
    "status")
        get_service_status
        ;;
        
    "test")
        if ! test_system; then
            print_status "❌ System test failed." "$RED"
            exit 1
        fi
        ;;
        
    "full")
        print_status "\n🎯 Running complete setup and start..." "$CYAN"
        
        # Setup
        if ! check_prerequisites; then
            print_status "❌ Prerequisites check failed." "$RED"
            exit 1
        fi
        
        if ! setup_environment; then
            print_status "❌ Environment setup failed." "$RED"
            exit 1
        fi
        
        if [ "$SKIP_DATA_LOAD" != true ]; then
            if ! setup_database; then
                print_status "❌ Database setup failed." "$RED"
                exit 1
            fi
        fi
        
        # Start services
        if ! start_services; then
            print_status "❌ Failed to start services." "$RED"
            exit 1
        fi
        
        print_status "\n🎉 MrBeast HR Analytics is ready!" "$GREEN"
        print_status "📊 Open your browser to: http://localhost:$DASHBOARD_PORT" "$CYAN"
        ;;
        
    *)
        print_status "❌ Unknown action: $ACTION" "$RED"
        show_usage
        exit 1
        ;;
esac 

print_status "\n✅ Master controller completed successfully!" "$GREEN" 