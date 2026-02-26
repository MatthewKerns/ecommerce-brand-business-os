#!/bin/bash
echo "Starting all services..."

# Start API
echo "Starting FastAPI..."
cd content-agents
source venv/bin/activate
uvicorn api.main:app --reload &

# Start Dashboard
echo "Starting Dashboard..."
cd ../dashboard
npm run dev &

echo "✅ Services started!"
echo "API: http://localhost:8000"
echo "Dashboard: http://localhost:3000"
