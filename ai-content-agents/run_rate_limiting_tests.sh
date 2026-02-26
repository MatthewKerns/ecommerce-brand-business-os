#!/bin/bash
#
# Run TikTok Shop rate limiting and error handling tests
#
# This script executes comprehensive tests for:
# - Rate limiter basic functionality
# - Rate limiter under load
# - API client rate limiting integration
# - Authentication error handling
# - Validation error handling
# - Not found error handling
# - Retry logic for transient errors
#
# Usage:
#   ./run_rate_limiting_tests.sh

set -e

echo "========================================================================"
echo "  TikTok Shop Rate Limiting & Error Handling Test Suite"
echo "========================================================================"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found"
    echo "   Copy .env.example to .env and add your credentials for full testing"
    echo ""
fi

# Run the test script
echo "Running test suite..."
echo ""

python3 test_rate_limiting_errors.py

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo "========================================================================"
    echo "  ✓ All tests PASSED"
    echo "========================================================================"
    exit 0
else
    echo ""
    echo "========================================================================"
    echo "  ✗ Some tests FAILED - see output above"
    echo "========================================================================"
    exit 1
fi
