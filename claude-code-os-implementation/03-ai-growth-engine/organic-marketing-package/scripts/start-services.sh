#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "Starting all services..."

# Start Content Engine API
echo "--- Starting Content Engine API ---"
cd "$ROOT_DIR/packages/content-engine"
source venv/bin/activate
uvicorn src.api.main:app --reload --port 8000 &

# Start Dashboard
echo "--- Starting Dashboard ---"
cd "$ROOT_DIR"
npm run dev:dashboard &

# Start Blog (optional)
# npm run dev:blog &

echo ""
echo "Services started!"
echo "  API:       http://localhost:8000"
echo "  Dashboard: http://localhost:3000"
echo "  Blog:      http://localhost:3001 (start with: npm run dev:blog)"
