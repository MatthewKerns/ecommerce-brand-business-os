#!/bin/bash

# Test script to verify Phase 3 setup
# This checks that all components are properly configured

echo "🔍 Testing Phase 3 Setup..."
echo "==========================="

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

ERRORS=0
WARNINGS=0

# Function to check status
check_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓${NC} $2"
    else
        echo -e "${RED}✗${NC} $2"
        ERRORS=$((ERRORS + 1))
    fi
}

warn_status() {
    echo -e "${YELLOW}⚠${NC} $1"
    WARNINGS=$((WARNINGS + 1))
}

# Test Python environment
echo ""
echo "Testing Python Environment:"
echo "---------------------------"

cd claude-code-os-implementation/03-ai-growth-engine/organic-marketing-package/content-agents || exit 1

# Check virtual environment
if [ -d "venv" ]; then
    check_status 0 "Virtual environment exists"
else
    check_status 1 "Virtual environment not found"
fi

# Check Python packages
source venv/bin/activate 2>/dev/null || true
python -c "import anthropic" 2>/dev/null
check_status $? "Anthropic package installed"

python -c "import fastapi" 2>/dev/null
check_status $? "FastAPI package installed"

python -c "import sqlalchemy" 2>/dev/null
check_status $? "SQLAlchemy package installed"

# Test database connection
echo ""
echo "Testing Database:"
echo "-----------------"

python -c "
from database.connection import engine
import sqlalchemy
try:
    with engine.connect() as conn:
        result = conn.execute(sqlalchemy.text('SELECT 1'))
        print('Database connection successful')
    exit(0)
except Exception as e:
    print(f'Database connection failed: {e}')
    exit(1)
" 2>/dev/null

check_status $? "Database connection"

# Check for tables
python -c "
from sqlalchemy import inspect
from database.connection import engine

inspector = inspect(engine)
tables = inspector.get_table_names()
expected = ['content_history', 'api_usage', 'performance_metrics']
missing = [t for t in expected if t not in tables]
if missing:
    print(f'Missing tables: {missing}')
    exit(1)
else:
    print(f'Found {len(tables)} tables')
    exit(0)
" 2>/dev/null

check_status $? "Database tables exist"

# Test API imports
echo ""
echo "Testing API Configuration:"
echo "--------------------------"

python -c "
try:
    from api.main import app
    print('API imports successful')
    exit(0)
except Exception as e:
    print(f'API import failed: {e}')
    exit(1)
" 2>/dev/null

check_status $? "API imports"

# Check environment variables
echo ""
echo "Testing Environment Variables:"
echo "------------------------------"

if [ -f ".env" ]; then
    check_status 0 ".env file exists"

    # Check for critical variables
    if grep -q "ANTHROPIC_API_KEY=" .env; then
        if grep -q "ANTHROPIC_API_KEY=your_key_here" .env; then
            warn_status "ANTHROPIC_API_KEY needs to be configured"
        else
            check_status 0 "ANTHROPIC_API_KEY configured"
        fi
    else
        check_status 1 "ANTHROPIC_API_KEY not found in .env"
    fi

    if grep -q "DATABASE_URL=" .env; then
        check_status 0 "DATABASE_URL configured"
    else
        warn_status "DATABASE_URL not found (using default SQLite)"
    fi
else
    check_status 1 ".env file not found"
fi

# Test Dashboard
echo ""
echo "Testing Dashboard:"
echo "------------------"

cd ../dashboard 2>/dev/null || {
    check_status 1 "Dashboard directory not found"
    cd ..
}

if [ -d "node_modules" ]; then
    check_status 0 "Dashboard dependencies installed"
else
    check_status 1 "Dashboard dependencies not installed"
fi

if [ -f ".env.local" ]; then
    check_status 0 "Dashboard .env.local exists"
else
    warn_status "Dashboard .env.local not found"
fi

# Summary
echo ""
echo "==========================="
echo "Test Results:"
echo "==========================="

if [ $ERRORS -eq 0 ]; then
    if [ $WARNINGS -eq 0 ]; then
        echo -e "${GREEN}✅ All tests passed!${NC}"
        echo ""
        echo "Your Phase 3 setup is ready to use!"
        echo "Run ./start_all.sh to start all services"
    else
        echo -e "${GREEN}✅ Setup is functional with $WARNINGS warnings${NC}"
        echo ""
        echo "Please review the warnings above"
        echo "You can still run ./start_all.sh to start services"
    fi
else
    echo -e "${RED}❌ $ERRORS errors found${NC}"
    echo ""
    echo "Please fix the errors above and run setup_phase3.sh"
fi

if [ $WARNINGS -gt 0 ]; then
    echo -e "${YELLOW}⚠ $WARNINGS warnings found${NC}"
fi

exit $ERRORS