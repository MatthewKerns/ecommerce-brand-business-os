#!/bin/bash
echo "Running all tests..."

# Python tests
echo "Running Python tests..."
cd content-agents
source venv/bin/activate
pytest

# TypeScript tests
echo "Running TypeScript tests..."
cd ../mcf-connector
npm test

echo "✅ All tests complete!"
