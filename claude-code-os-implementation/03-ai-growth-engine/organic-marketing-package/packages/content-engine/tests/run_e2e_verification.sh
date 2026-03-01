#!/bin/bash
#
# End-to-end verification runner for customer profile sync flow
#
# This script:
# 1. Ensures database is set up
# 2. Starts FastAPI server in background
# 3. Runs verification tests
# 4. Stops server
#

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}E2E Verification: Customer Profile Sync${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Change to project directory
cd "$PROJECT_DIR"

# Step 1: Check if database migration is needed
echo -e "${YELLOW}Step 1: Checking database setup...${NC}"
if [ -f "database/migrations/add_klaviyo_models.py" ]; then
    echo "Running database migration..."
    python database/migrations/add_klaviyo_models.py || {
        echo -e "${YELLOW}Warning: Migration may have already been applied${NC}"
    }
else
    echo -e "${YELLOW}Warning: Migration script not found${NC}"
fi

# Step 2: Check if server is already running
echo -e "\n${YELLOW}Step 2: Checking if FastAPI server is running...${NC}"
SERVER_PID=""
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Server is already running${NC}"
    SERVER_RUNNING=true
else
    echo "Server not running. Starting server..."
    SERVER_RUNNING=false

    # Start server in background
    nohup uvicorn api.main:app --host 0.0.0.0 --port 8000 > /tmp/fastapi_server.log 2>&1 &
    SERVER_PID=$!

    echo "Server started with PID: $SERVER_PID"
    echo "Waiting for server to be ready..."

    # Wait for server to start (max 30 seconds)
    for i in {1..30}; do
        if curl -s http://localhost:8000/health > /dev/null 2>&1; then
            echo -e "${GREEN}✓ Server is ready${NC}"
            break
        fi

        if [ $i -eq 30 ]; then
            echo -e "${RED}✗ Server failed to start${NC}"
            echo "Server log:"
            cat /tmp/fastapi_server.log
            exit 1
        fi

        echo -n "."
        sleep 1
    done
fi

# Step 3: Run verification script
echo -e "\n${YELLOW}Step 3: Running verification tests...${NC}\n"
python tests/verify_e2e_profile_sync.py
VERIFY_EXIT_CODE=$?

# Step 4: Cleanup
if [ "$SERVER_RUNNING" = false ] && [ -n "$SERVER_PID" ]; then
    echo -e "\n${YELLOW}Step 4: Stopping server...${NC}"
    kill $SERVER_PID 2>/dev/null || true
    echo -e "${GREEN}✓ Server stopped${NC}"
fi

# Final summary
echo -e "\n${BLUE}========================================${NC}"
if [ $VERIFY_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✓ ALL VERIFICATIONS PASSED${NC}"
    echo -e "${BLUE}========================================${NC}\n"
    exit 0
else
    echo -e "${RED}✗ VERIFICATION FAILED${NC}"
    echo -e "${BLUE}========================================${NC}\n"
    exit 1
fi
