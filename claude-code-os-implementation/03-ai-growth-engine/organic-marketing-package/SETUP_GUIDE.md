# Phase 3 Setup Guide

This guide will help you set up and run the complete system after the Phase 3 merge, including database migrations, dependencies, and servers.

## Prerequisites

- Python 3.8+ installed
- Node.js 18+ installed
- PostgreSQL or SQLite installed
- Redis (optional, for caching)

## Step 1: Environment Variables

First, set up your environment variables:

```bash
cd claude-code-os-implementation/03-ai-growth-engine/organic-marketing-package/content-agents

# Copy the example file
cp .env.example .env

# Edit the .env file with your credentials
nano .env
```

Required environment variables:
```env
# Database
DATABASE_URL=sqlite:///content_agents.db  # Or PostgreSQL URL

# API Keys
ANTHROPIC_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
PERPLEXITY_API_KEY=your_key_here

# Clerk (for authentication)
CLERK_WEBHOOK_SECRET=whsec_xxxxx

# Klaviyo (for email marketing)
KLAVIYO_API_KEY=pk_xxxxx
KLAVIYO_ACCOUNT_ID=xxxxx

# TikTok (for social commerce)
TIKTOK_SHOP_APP_KEY=xxxxx
TIKTOK_SHOP_APP_SECRET=xxxxx
TIKTOK_SHOP_ACCESS_TOKEN=xxxxx

# Amazon SP-API (optional)
AMAZON_SELLER_ID=xxxxx
AMAZON_SP_API_CLIENT_ID=xxxxx
AMAZON_SP_API_CLIENT_SECRET=xxxxx
AMAZON_SP_API_REFRESH_TOKEN=xxxxx

# SEO Tools (optional)
SEMRUSH_API_KEY=xxxxx
AHREFS_API_KEY=xxxxx
```

## Step 2: Python Backend Setup

### 2.1 Create Virtual Environment

```bash
cd claude-code-os-implementation/03-ai-growth-engine/organic-marketing-package/content-agents

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate  # On Windows
```

### 2.2 Install Python Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install all dependencies
pip install -r requirements.txt

# Install additional dependencies from Phase 3
pip install klaviyo-api sendgrid celery redis
```

### 2.3 Run Database Migrations

```bash
# Initialize the database
python database/init_db.py

# Run SQL migrations
python database/init_db.py --migrations

# Run Python migration scripts
python database/migrations/add_seo_fields.py
python database/migrations/add_klaviyo_models.py

# Verify database setup
python -c "from database.connection import test_connection; test_connection()"
```

### 2.4 Start the FastAPI Server

```bash
# Development mode with auto-reload
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Or production mode
uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

The API will be available at:
- API: http://localhost:8000
- Docs: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

## Step 3: Dashboard Setup (Next.js)

### 3.1 Install Node Dependencies

```bash
cd claude-code-os-implementation/03-ai-growth-engine/organic-marketing-package/dashboard

# Install dependencies
npm install

# If you encounter issues, try:
npm install --legacy-peer-deps
```

### 3.2 Configure Dashboard Environment

```bash
# Copy example env file
cp .env.local.example .env.local

# Edit with your settings
nano .env.local
```

Add these variables:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_xxxxx
CLERK_SECRET_KEY=sk_xxxxx
```

### 3.3 Run the Dashboard

```bash
# Development mode
npm run dev

# Or build and run production
npm run build
npm run start
```

Dashboard will be available at: http://localhost:3000

## Step 4: Email Marketing Automation Setup

```bash
cd claude-code-os-implementation/03-ai-growth-engine/organic-marketing-package/04-email-marketing-automation/implementation

# Install dependencies
npm install

# Run tests to verify setup
npm test
```

## Step 5: MCF Connector Setup (Optional)

```bash
cd claude-code-os-implementation/03-ai-growth-engine/organic-marketing-package/mcf-connector

# Install dependencies
npm install

# Build TypeScript
npm run build
```

## Step 6: Start Background Workers (Optional)

If using Celery for background tasks:

```bash
# Start Redis (if not running)
redis-server

# Start Celery worker
cd content-agents
celery -A tasks worker --loglevel=info

# Start Celery beat (for scheduled tasks)
celery -A tasks beat --loglevel=info
```

## Step 7: Verify Everything is Working

### Test API Endpoints
```bash
# Health check
curl http://localhost:8000/api/health

# SEO endpoint
curl http://localhost:8000/api/seo/health

# Klaviyo status
curl http://localhost:8000/api/klaviyo/status

# Clerk webhook status
curl http://localhost:8000/api/webhooks/clerk/status
```

### Test Content Generation
```bash
cd content-agents
python quick_start.py
```

### Test Analytics
```bash
# Run analytics ETL test
python analytics/etl/tiktok_ingestion.py --test
```

## Step 8: Common Issues and Solutions

### Issue: Database connection error
**Solution:** Check DATABASE_URL in .env file and ensure database server is running

### Issue: Import errors for new modules
**Solution:** Ensure you're in the activated virtual environment and all dependencies are installed

### Issue: API key errors
**Solution:** Verify all required API keys are set in the .env file

### Issue: Port already in use
**Solution:** Change the port in the uvicorn command or stop the process using the port

### Issue: Dashboard build errors
**Solution:** Clear node_modules and reinstall:
```bash
rm -rf node_modules package-lock.json
npm install
```

## Step 9: Development Workflow

### Running Tests
```bash
# Backend tests
cd content-agents
pytest tests/

# Dashboard tests
cd dashboard
npm test

# E2E tests
npm run test:e2e
```

### Code Quality
```bash
# Python linting
cd content-agents
flake8 .

# TypeScript/JavaScript linting
cd dashboard
npm run lint
```

## Step 10: Production Deployment

For production deployment:

1. Use environment-specific .env files (.env.production)
2. Set up proper database (PostgreSQL recommended)
3. Use a process manager (systemd, supervisor, PM2)
4. Set up reverse proxy (nginx, Apache)
5. Enable SSL/TLS certificates
6. Configure proper logging and monitoring

## Quick Start Script

For convenience, here's a quick start script:

```bash
#!/bin/bash
# save as start_all.sh

# Start Backend
cd content-agents
source venv/bin/activate
uvicorn api.main:app --reload --port 8000 &

# Start Dashboard
cd ../dashboard
npm run dev &

# Start Redis
redis-server &

echo "All services started!"
echo "API: http://localhost:8000"
echo "Dashboard: http://localhost:3000"
echo "API Docs: http://localhost:8000/api/docs"
```

## Need Help?

- Check logs in `content-agents/logs/`
- Review documentation in each component's README
- Verify all environment variables are set correctly
- Ensure all services (database, Redis) are running