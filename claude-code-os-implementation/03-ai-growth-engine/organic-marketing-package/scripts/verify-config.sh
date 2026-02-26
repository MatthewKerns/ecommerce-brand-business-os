#!/bin/bash

# End-to-End Configuration Verification Script
# Tests all configuration and secrets management functionality

set -e

echo "=========================================="
echo "Configuration & Secrets Management E2E Verification"
echo "=========================================="
echo ""

# Track verification status
FAILED_CHECKS=0
PASSED_CHECKS=0

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

check_pass() {
    echo -e "${GREEN}✓ PASS:${NC} $1"
    ((PASSED_CHECKS++))
}

check_fail() {
    echo -e "${RED}✗ FAIL:${NC} $1"
    ((FAILED_CHECKS++))
}

check_info() {
    echo -e "${YELLOW}ℹ INFO:${NC} $1"
}

echo "=========================================="
echo "1. Verify Python service loads config from environment-specific file"
echo "=========================================="
echo ""

# Test development environment
check_info "Testing development environment loading..."
export ENVIRONMENT=development
RESULT=$(python3 -c "
import sys
import os
sys.path.insert(0, 'ai-content-agents')
os.chdir('ai-content-agents')
from config.environments import load_environment_config, get_current_environment
load_environment_config()
env = get_current_environment()
print(f'Environment: {env}')
" 2>&1)

if echo "$RESULT" | grep -q "development"; then
    check_pass "Python loads development config"
else
    check_fail "Python failed to load development config: $RESULT"
fi

# Test staging environment
check_info "Testing staging environment loading..."
export ENVIRONMENT=staging
RESULT=$(python3 -c "
import sys
import os
sys.path.insert(0, 'ai-content-agents')
os.chdir('ai-content-agents')
from config.environments import load_environment_config, get_current_environment
load_environment_config()
env = get_current_environment()
print(f'Environment: {env}')
" 2>&1)

if echo "$RESULT" | grep -q "staging"; then
    check_pass "Python loads staging config"
else
    check_fail "Python failed to load staging config: $RESULT"
fi

# Test production environment
check_info "Testing production environment loading..."
export ENVIRONMENT=production
RESULT=$(python3 -c "
import sys
import os
sys.path.insert(0, 'ai-content-agents')
os.chdir('ai-content-agents')
from config.environments import load_environment_config, get_current_environment
load_environment_config()
env = get_current_environment()
print(f'Environment: {env}')
" 2>&1)

if echo "$RESULT" | grep -q "production"; then
    check_pass "Python loads production config"
else
    check_fail "Python failed to load production config: $RESULT"
fi

echo ""
echo "=========================================="
echo "2. Verify Python secrets encryption/decryption works"
echo "=========================================="
echo ""

# Test encryption and decryption
check_info "Testing encryption/decryption functionality..."
RESULT=$(python3 -c "
import sys
sys.path.insert(0, 'ai-content-agents')
from config.secrets import SecretsManager

# Create a secrets manager
sm = SecretsManager.from_password('test-password-123')

# Test string encryption/decryption
test_string = 'my-secret-api-key-12345'
encrypted = sm.encrypt_string(test_string)
decrypted = sm.decrypt_string(encrypted)

if decrypted == test_string:
    print('SUCCESS: Encryption/decryption works correctly')
else:
    print(f'FAILED: Expected {test_string}, got {decrypted}')
" 2>&1)

if echo "$RESULT" | grep -q "SUCCESS"; then
    check_pass "Python secrets encryption/decryption works"
else
    check_fail "Python secrets encryption/decryption failed: $RESULT"
fi

echo ""
echo "=========================================="
echo "3. Verify TypeScript service loads and validates config"
echo "=========================================="
echo ""

# Test TypeScript config module compilation
check_info "Testing TypeScript config module compilation..."
cd claude-code-os-implementation/03-ai-growth-engine/organic-marketing-package/04-email-marketing-automation/implementation

# Check if config files exist
if [ -f "src/config/index.ts" ] && [ -f "src/config/secrets.ts" ]; then
    check_pass "TypeScript config modules exist"
else
    check_fail "TypeScript config modules missing"
fi

# Test TypeScript compilation
check_info "Running TypeScript type checking..."
if npx tsc --noEmit 2>&1 | grep -q "error"; then
    check_fail "TypeScript compilation has errors"
else
    check_pass "TypeScript config modules compile without errors"
fi

cd - > /dev/null

echo ""
echo "=========================================="
echo "4. Verify OAuth token refresh still works for Gmail"
echo "=========================================="
echo ""

# Check that Gmail OAuth client still has refresh functionality
check_info "Checking Gmail OAuth refresh implementation..."
cd claude-code-os-implementation/03-ai-growth-engine/organic-marketing-package/04-email-marketing-automation/implementation

if grep -q "refreshAccessToken\|refresh_token\|oauth2Client.setCredentials" src/core/email/gmail-client.ts; then
    check_pass "Gmail OAuth refresh functionality present in code"
else
    check_fail "Gmail OAuth refresh functionality not found"
fi

cd - > /dev/null

echo ""
echo "=========================================="
echo "5. Verify all example .env files are up to date"
echo "=========================================="
echo ""

# Check Python .env files
check_info "Checking Python .env files..."

if [ -f "ai-content-agents/.env.example" ]; then
    if grep -q "ENVIRONMENT" ai-content-agents/.env.example && \
       grep -q "ENCRYPTION_KEY" ai-content-agents/.env.example; then
        check_pass "Python .env.example includes new config options"
    else
        check_fail "Python .env.example missing ENVIRONMENT or ENCRYPTION_KEY"
    fi
else
    check_fail "Python .env.example not found"
fi

if [ -f "ai-content-agents/.env.development" ] && \
   [ -f "ai-content-agents/.env.staging" ] && \
   [ -f "ai-content-agents/.env.production" ]; then
    check_pass "All Python environment-specific .env files exist"
else
    check_fail "Missing Python environment-specific .env files"
fi

# Check TypeScript .env files
check_info "Checking TypeScript .env files..."

if [ -f "claude-code-os-implementation/03-ai-growth-engine/organic-marketing-package/04-email-marketing-automation/implementation/.env.example" ]; then
    TS_ENV_FILE="claude-code-os-implementation/03-ai-growth-engine/organic-marketing-package/04-email-marketing-automation/implementation/.env.example"
    if grep -q "GMAIL_" "$TS_ENV_FILE" && \
       grep -q "ANTHROPIC_API_KEY\|GEMINI_API_KEY" "$TS_ENV_FILE"; then
        check_pass "TypeScript .env.example includes required config options"
    else
        check_fail "TypeScript .env.example missing key configuration options"
    fi
else
    check_fail "TypeScript .env.example not found"
fi

echo ""
echo "=========================================="
echo "6. Verify no secrets are committed to git"
echo "=========================================="
echo ""

# Check for .env files in git
check_info "Checking for .env files in git..."
if git ls-files | grep -E '^\.env$|/\.env$'; then
    check_fail ".env files found in git tracking"
else
    check_pass "No .env files committed to git"
fi

# Check for secrets in staged files
check_info "Checking for secrets in code..."
if git diff --cached | grep -iE '(api[_-]?key|secret|password|token).*=.*[a-zA-Z0-9]{20}'; then
    check_fail "Potential secrets detected in staged changes"
else
    check_pass "No secrets detected in staged changes"
fi

# Check .gitignore for .env files
check_info "Checking .gitignore configuration..."
if [ -f ".gitignore" ]; then
    if grep -q "^\.env$" .gitignore || grep -q "^\.env\.local$" .gitignore; then
        check_pass ".gitignore configured to ignore .env files"
    else
        check_fail ".gitignore not configured to ignore .env files"
    fi
else
    check_fail ".gitignore file not found"
fi

echo ""
echo "=========================================="
echo "VERIFICATION SUMMARY"
echo "=========================================="
echo ""
echo -e "Passed checks: ${GREEN}${PASSED_CHECKS}${NC}"
echo -e "Failed checks: ${RED}${FAILED_CHECKS}${NC}"
echo ""

if [ $FAILED_CHECKS -eq 0 ]; then
    echo -e "${GREEN}✓ ALL VERIFICATIONS PASSED${NC}"
    echo ""
    echo "Configuration and secrets management system is working correctly!"
    exit 0
else
    echo -e "${RED}✗ SOME VERIFICATIONS FAILED${NC}"
    echo ""
    echo "Please review and fix the failed checks above."
    exit 1
fi
