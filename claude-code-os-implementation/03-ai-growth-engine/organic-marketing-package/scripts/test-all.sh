#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "Running all tests..."

# Python tests (content-engine)
echo "--- Running Content Engine tests (Python) ---"
cd "$ROOT_DIR/packages/content-engine"
source venv/bin/activate
pytest tests/
deactivate

# TypeScript tests (all packages via npm workspaces)
echo "--- Running TypeScript tests (all packages) ---"
cd "$ROOT_DIR"
npm run test

echo ""
echo "All tests complete!"
