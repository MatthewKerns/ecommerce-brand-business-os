#!/bin/bash

# Start all Phase 3 services
# This script starts the API server and dashboard

echo "🚀 Starting all Phase 3 services..."
echo "===================================="

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Base directory
BASE_DIR="$(cd "$(dirname "$0")" && pwd)"

# Function to cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}Shutting down services...${NC}"
    # Kill all child processes
    pkill -P $$
    exit 0
}

# Trap Ctrl+C
trap cleanup INT

# Start Backend API
echo -e "${BLUE}Starting Backend API...${NC}"
cd "$BASE_DIR/content-agents" || exit 1

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Please run setup_phase3.sh first."
    exit 1
fi

# Activate virtual environment and start API
(
    source venv/bin/activate
    echo -e "${GREEN}✓ Backend API starting on http://localhost:8000${NC}"
    uvicorn api.main:app --reload --host 0.0.0.0 --port 8000 2>&1 | sed 's/^/[API] /'
) &

# Give the API a moment to start
sleep 2

# Start Dashboard
echo -e "${BLUE}Starting Dashboard...${NC}"
cd "$BASE_DIR/dashboard" || exit 1

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Dashboard dependencies not installed. Please run setup_phase3.sh first."
    exit 1
fi

(
    echo -e "${GREEN}✓ Dashboard starting on http://localhost:3000${NC}"
    npm run dev 2>&1 | sed 's/^/[Dashboard] /'
) &

# Optional: Start Redis if available
if command -v redis-server &> /dev/null; then
    echo -e "${BLUE}Starting Redis...${NC}"
    (
        redis-server 2>&1 | sed 's/^/[Redis] /'
    ) &
    echo -e "${GREEN}✓ Redis started${NC}"
fi

echo ""
echo "===================================="
echo -e "${GREEN}All services are starting!${NC}"
echo "===================================="
echo ""
echo "Services available at:"
echo "  • API:       http://localhost:8000"
echo "  • API Docs:  http://localhost:8000/api/docs"
echo "  • Dashboard: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Wait for all background processes
wait