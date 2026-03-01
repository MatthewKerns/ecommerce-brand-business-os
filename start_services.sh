#!/bin/bash

# Start services for E2E testing
# This script starts the FastAPI server and Celery worker in the background

set -e

echo "Starting services for E2E workflow testing..."
echo "=============================================="

# Get the content-engine directory
CONTENT_ENGINE_DIR="./claude-code-os-implementation/03-ai-growth-engine/organic-marketing-package/packages/content-engine"

# Check if the directory exists
if [ ! -d "$CONTENT_ENGINE_DIR" ]; then
    echo "Error: Content engine directory not found at $CONTENT_ENGINE_DIR"
    exit 1
fi

cd "$CONTENT_ENGINE_DIR"

# Check for .env file
if [ ! -f ".env" ] && [ ! -f ".env.development" ]; then
    echo "Warning: No .env file found. Copying from .env.example"
    cp .env.example .env
    echo "Please configure .env with your API keys before running services"
    exit 1
fi

echo ""
echo "1. Starting FastAPI server..."
echo "   Command: python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000"
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000 > /tmp/fastapi.log 2>&1 &
FASTAPI_PID=$!
echo "   FastAPI started with PID: $FASTAPI_PID"
echo "   Logs: /tmp/fastapi.log"

echo ""
echo "2. Starting Celery worker..."
echo "   Command: celery -A celery_app worker --loglevel=info -Q content_high,content_medium,content_low,default"
celery -A celery_app worker --loglevel=info -Q content_high,content_medium,content_low,default > /tmp/celery.log 2>&1 &
CELERY_PID=$!
echo "   Celery started with PID: $CELERY_PID"
echo "   Logs: /tmp/celery.log"

echo ""
echo "=============================================="
echo "Services started successfully!"
echo "=============================================="
echo ""
echo "Process IDs:"
echo "  FastAPI: $FASTAPI_PID"
echo "  Celery:  $CELERY_PID"
echo ""
echo "To stop services:"
echo "  kill $FASTAPI_PID $CELERY_PID"
echo ""
echo "Or use: pkill -f 'uvicorn api.main' && pkill -f 'celery.*worker'"
echo ""
echo "Waiting 5 seconds for services to start..."
sleep 5

# Check if services are running
if ps -p $FASTAPI_PID > /dev/null; then
    echo "✓ FastAPI is running"
else
    echo "✗ FastAPI failed to start. Check /tmp/fastapi.log"
    exit 1
fi

if ps -p $CELERY_PID > /dev/null; then
    echo "✓ Celery is running"
else
    echo "✗ Celery failed to start. Check /tmp/celery.log"
    exit 1
fi

echo ""
echo "All services are ready!"
echo "You can now run: ./test_e2e_workflow.py"
echo ""
echo "Service health check:"
curl -s http://localhost:8000/health | python -m json.tool || echo "Health check failed"
