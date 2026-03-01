#!/bin/bash

# Phase 3 Setup Script
# This script sets up the complete system after Phase 3 merge

set -e  # Exit on error

echo "🚀 Starting Phase 3 Setup..."
echo "================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Check prerequisites
echo "Checking prerequisites..."

if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed"
    exit 1
else
    print_status "Python 3 found: $(python3 --version)"
fi

if ! command -v node &> /dev/null; then
    print_error "Node.js is not installed"
    exit 1
else
    print_status "Node.js found: $(node --version)"
fi

if ! command -v npm &> /dev/null; then
    print_error "npm is not installed"
    exit 1
else
    print_status "npm found: $(npm --version)"
fi

# Navigate to content-agents directory
CONTENT_AGENTS_DIR="claude-code-os-implementation/03-ai-growth-engine/organic-marketing-package/content-agents"
cd "$CONTENT_AGENTS_DIR" || exit 1

echo ""
echo "Step 1: Setting up Python environment..."
echo "----------------------------------------"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    print_status "Creating virtual environment..."
    python3 -m venv venv
else
    print_warning "Virtual environment already exists"
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip --quiet

# Install Python dependencies
print_status "Installing Python dependencies..."
pip install -r requirements.txt --quiet

# Install additional Phase 3 dependencies
print_status "Installing Phase 3 dependencies..."
pip install klaviyo-api sendgrid celery redis --quiet 2>/dev/null || true

echo ""
echo "Step 2: Setting up environment variables..."
echo "-------------------------------------------"

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        print_status ".env file created from .env.example"
        print_warning "Please edit .env file with your API keys and credentials"
    else
        print_error ".env.example not found"
    fi
else
    print_warning ".env file already exists"
fi

echo ""
echo "Step 3: Setting up database..."
echo "------------------------------"

# Initialize database
print_status "Initializing database..."
python database/init_db.py 2>/dev/null || print_warning "Database may already be initialized"

# Run migrations if they exist
if [ -f "database/migrations/add_seo_fields.py" ]; then
    print_status "Running SEO fields migration..."
    python database/migrations/add_seo_fields.py 2>/dev/null || print_warning "SEO migration may already be applied"
fi

if [ -f "database/migrations/add_klaviyo_models.py" ]; then
    print_status "Running Klaviyo models migration..."
    python database/migrations/add_klaviyo_models.py 2>/dev/null || print_warning "Klaviyo migration may already be applied"
fi

echo ""
echo "Step 4: Setting up Dashboard..."
echo "-------------------------------"

# Navigate to dashboard directory
cd ../dashboard || exit 1

# Install Node dependencies
if [ ! -d "node_modules" ]; then
    print_status "Installing dashboard dependencies..."
    npm install --silent
else
    print_warning "Node modules already installed"
fi

# Create .env.local if it doesn't exist
if [ ! -f ".env.local" ]; then
    if [ -f ".env.local.example" ]; then
        cp .env.local.example .env.local
        print_status ".env.local created from example"
    fi
else
    print_warning ".env.local already exists"
fi

echo ""
echo "Step 5: Setting up Email Marketing Automation..."
echo "------------------------------------------------"

# Navigate to email marketing directory
cd ../04-email-marketing-automation/implementation 2>/dev/null || {
    print_warning "Email marketing automation directory not found"
}

if [ -d "." ]; then
    if [ ! -d "node_modules" ]; then
        print_status "Installing email automation dependencies..."
        npm install --silent
    else
        print_warning "Email automation dependencies already installed"
    fi
fi

echo ""
echo "================================"
echo -e "${GREEN}✅ Phase 3 Setup Complete!${NC}"
echo "================================"
echo ""
echo "Next steps:"
echo "1. Edit the .env files with your API keys:"
echo "   - $CONTENT_AGENTS_DIR/.env"
echo "   - Dashboard: .env.local"
echo ""
echo "2. Start the services:"
echo "   Backend API:"
echo "   cd $CONTENT_AGENTS_DIR"
echo "   source venv/bin/activate"
echo "   uvicorn api.main:app --reload --port 8000"
echo ""
echo "   Dashboard:"
echo "   cd dashboard"
echo "   npm run dev"
echo ""
echo "3. Access the applications:"
echo "   - API: http://localhost:8000"
echo "   - API Docs: http://localhost:8000/api/docs"
echo "   - Dashboard: http://localhost:3000"
echo ""
echo "For more details, see SETUP_GUIDE.md"