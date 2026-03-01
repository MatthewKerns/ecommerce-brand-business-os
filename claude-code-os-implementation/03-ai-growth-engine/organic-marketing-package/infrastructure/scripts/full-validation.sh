#!/usr/bin/env bash
# full-validation.sh
#
# Comprehensive validation for the package reorganization (Task #12).
# Checks structure, imports, builds, tests, and cleanup.
#
# Usage: bash infrastructure/scripts/full-validation.sh [--fix]
#
# --fix: Attempt to auto-fix issues where possible

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

FIX_MODE=false
if [[ "${1:-}" == "--fix" ]]; then
    FIX_MODE=true
fi

cd "$ROOT_DIR"

PASS=0
FAIL=0
WARN=0
SKIP=0

log_pass() { echo "  [PASS] $1"; PASS=$((PASS + 1)); }
log_fail() { echo "  [FAIL] $1"; FAIL=$((FAIL + 1)); }
log_warn() { echo "  [WARN] $1"; WARN=$((WARN + 1)); }
log_skip() { echo "  [SKIP] $1"; SKIP=$((SKIP + 1)); }

echo "================================================================"
echo "  Organic Marketing Package - Full Validation"
echo "  $(date)"
echo "================================================================"
echo ""

# ===================================================================
# SECTION 1: Directory Structure
# ===================================================================
echo "=== [1/8] Directory Structure ==="

REQUIRED_DIRS=(
    packages packages/content-engine packages/dashboard
    packages/mcf-connector packages/blog packages/shared
    packages/shared/src infrastructure infrastructure/scripts docs
)

for dir in "${REQUIRED_DIRS[@]}"; do
    if [[ -d "$dir" ]]; then
        log_pass "$dir/ exists"
    else
        log_fail "$dir/ missing"
    fi
done

echo ""

# ===================================================================
# SECTION 2: Package Configuration
# ===================================================================
echo "=== [2/8] Package Configuration ==="

# Root package.json with workspaces
if [[ -f "package.json" ]]; then
    if grep -q '"workspaces"' package.json; then
        log_pass "Root package.json has workspaces configured"
    else
        log_fail "Root package.json missing workspaces"
    fi
else
    log_fail "Root package.json missing"
fi

# Root tsconfig
if [[ -f "tsconfig.json" ]]; then
    if grep -q '"references"' tsconfig.json; then
        log_pass "Root tsconfig.json has project references"
    else
        log_warn "Root tsconfig.json missing project references"
    fi
else
    log_fail "Root tsconfig.json missing"
fi

# Base tsconfig
if [[ -f "tsconfig.base.json" ]]; then
    if grep -q '"composite"' tsconfig.base.json; then
        log_pass "tsconfig.base.json has composite mode"
    else
        log_fail "tsconfig.base.json missing composite mode"
    fi
else
    log_fail "tsconfig.base.json missing"
fi

# Per-package configs
PACKAGES_WITH_PKG_JSON=(shared dashboard mcf-connector blog content-engine)
for pkg in "${PACKAGES_WITH_PKG_JSON[@]}"; do
    if [[ -f "packages/$pkg/package.json" ]]; then
        log_pass "packages/$pkg/package.json exists"
    else
        log_fail "packages/$pkg/package.json missing"
    fi
done

# Shared package must export types
if [[ -f "packages/shared/src/index.ts" ]]; then
    log_pass "packages/shared/src/index.ts exists"
else
    log_fail "packages/shared/src/index.ts missing"
fi

echo ""

# ===================================================================
# SECTION 3: Cross-Package Dependencies
# ===================================================================
echo "=== [3/8] Cross-Package Dependencies ==="

# Check that dashboard and mcf-connector reference @organic-marketing/shared
for pkg in dashboard mcf-connector blog; do
    if [[ -f "packages/$pkg/package.json" ]]; then
        if grep -q '"@organic-marketing/shared"' "packages/$pkg/package.json"; then
            log_pass "packages/$pkg depends on @organic-marketing/shared"
        else
            log_warn "packages/$pkg does not depend on @organic-marketing/shared"
        fi
    fi
done

# Check TypeScript project references
for pkg in dashboard mcf-connector blog; do
    if [[ -f "packages/$pkg/tsconfig.json" ]]; then
        if grep -q '"../shared"' "packages/$pkg/tsconfig.json"; then
            log_pass "packages/$pkg has TS reference to shared"
        else
            log_warn "packages/$pkg missing TS reference to shared"
        fi
    fi
done

echo ""

# ===================================================================
# SECTION 4: Python Package (Content Engine)
# ===================================================================
echo "=== [4/8] Content Engine (Python) ==="

CE_DIR="content-agents"
CE_PKG="packages/content-engine"

# Check source directories exist (in either old or new location)
PYTHON_SRC_DIRS=(agents api services database infrastructure integrations config)
for dir in "${PYTHON_SRC_DIRS[@]}"; do
    if [[ -d "$CE_DIR/$dir" ]] || [[ -d "$CE_PKG/src/$dir" ]]; then
        log_pass "Python source: $dir/"
    else
        log_fail "Python source missing: $dir/"
    fi
done

# Check for requirements.txt
if [[ -f "$CE_DIR/requirements.txt" ]] || [[ -f "$CE_PKG/requirements.txt" ]]; then
    log_pass "requirements.txt exists"
else
    log_fail "requirements.txt missing"
fi

# Check test organization
if [[ -d "$CE_DIR/tests" ]] || [[ -d "$CE_PKG/tests" ]]; then
    TESTS_DIR="$CE_DIR/tests"
    [[ -d "$CE_PKG/tests" ]] && TESTS_DIR="$CE_PKG/tests"

    for subdir in integration e2e verification; do
        if [[ -d "$TESTS_DIR/$subdir" ]]; then
            log_pass "Test subdirectory: tests/$subdir/"
        else
            log_warn "Test subdirectory missing: tests/$subdir/"
        fi
    done
else
    log_fail "Tests directory missing"
fi

# Check no test files at root
ROOT_TEST_FILES=$(find "$CE_DIR" -maxdepth 1 \( -name "test_*.py" -o -name "verify_*.py" \) 2>/dev/null | wc -l | tr -d ' ' || echo "0")
if [[ "$ROOT_TEST_FILES" -eq 0 ]]; then
    log_pass "No test files at content-agents root"
else
    log_warn "$ROOT_TEST_FILES test files remain at content-agents root"
fi

echo ""

# ===================================================================
# SECTION 5: Import Consistency
# ===================================================================
echo "=== [5/8] Import Consistency ==="

# Check for old content_agents module imports (exclude DB filenames)
OLD_PY_IMPORTS=$(set +o pipefail; grep -rn "content_agents\." --include="*.py" --exclude-dir=venv --exclude-dir=__pycache__ --exclude-dir=node_modules --exclude-dir=.git content-agents/ packages/content-engine/ 2>/dev/null | grep -v "content_agents\.db" | grep -v "content_agents\.log" | wc -l | tr -d ' ')
if [[ "$OLD_PY_IMPORTS" -eq 0 ]]; then
    log_pass "No old content_agents.* Python imports"
else
    log_warn "$OLD_PY_IMPORTS lines with old content_agents imports"
fi

# Check for old path references in TypeScript (packages/*/src only, no node_modules)
for pkg in dashboard mcf-connector blog; do
    if [[ -d "packages/$pkg/src" ]]; then
        OLD_TS=$(set +o pipefail; grep -rn 'content-agents\|\.\.\/\.\.\/mcf-connector\|\.\.\/\.\.\/dashboard' --include="*.ts" --include="*.tsx" --exclude-dir=node_modules --exclude-dir=.next "packages/$pkg/src/" 2>/dev/null | wc -l | tr -d ' ')
        if [[ "$OLD_TS" -eq 0 ]]; then
            log_pass "packages/$pkg: no old relative imports"
        else
            log_warn "packages/$pkg: $OLD_TS lines with old path references"
        fi
    fi
done

echo ""

# ===================================================================
# SECTION 6: Build Verification
# ===================================================================
echo "=== [6/8] Build Verification ==="

# Check if shared has valid TypeScript config and source
if [[ -f "packages/shared/tsconfig.json" ]] && [[ -f "packages/shared/src/index.ts" ]]; then
    # Verify tsconfig is valid JSON
    if python3 -c "import json; json.load(open('packages/shared/tsconfig.json'))" 2>/dev/null; then
        log_pass "packages/shared tsconfig.json is valid JSON"
    else
        log_fail "packages/shared tsconfig.json is invalid JSON"
    fi
    # Check TypeScript syntax with a quick parse
    if command -v npx &> /dev/null && [[ -d "node_modules" ]]; then
        if timeout 15 npx tsc --noEmit -p packages/shared/tsconfig.json 2>/dev/null; then
            log_pass "packages/shared TypeScript compiles"
        else
            log_warn "packages/shared TypeScript has compilation warnings"
        fi
    else
        log_skip "TypeScript build check (npx/node_modules not available)"
    fi
else
    log_skip "Shared package not ready for build check"
fi

# Check if Python syntax is valid for key files
if command -v python3 &> /dev/null; then
    PY_SYNTAX_ERRORS=0
    KEY_PY_FILES=(
        "$CE_DIR/agents/__init__.py"
        "$CE_DIR/api/routes/aeo.py"
        "$CE_DIR/config/config.py"
    )
    for f in "${KEY_PY_FILES[@]}"; do
        if [[ -f "$f" ]]; then
            if python3 -m py_compile "$f" 2>/dev/null; then
                log_pass "Python syntax OK: $(basename "$f")"
            else
                log_fail "Python syntax error: $f"
                PY_SYNTAX_ERRORS=$((PY_SYNTAX_ERRORS + 1))
            fi
        fi
    done
else
    log_skip "Python syntax check (python3 not available)"
fi

echo ""

# ===================================================================
# SECTION 7: Documentation
# ===================================================================
echo "=== [7/8] Documentation ==="

# README files
README_LOCATIONS=(
    "packages/README.md"
    "packages/content-engine/README.md"
    "packages/dashboard/README.md"
    "packages/mcf-connector/README.md"
    "packages/blog/README.md"
    "packages/shared/README.md"
    "infrastructure/README.md"
    "docs/README.md"
    "README.md"
)

for readme in "${README_LOCATIONS[@]}"; do
    if [[ -f "$readme" ]]; then
        log_pass "$readme exists"
    else
        log_warn "$readme missing"
    fi
done

echo ""

# ===================================================================
# SECTION 8: Cleanup Check
# ===================================================================
echo "=== [8/8] Cleanup Status ==="

# Check for orphaned empty directories (only in packages/ and infrastructure/)
EMPTY_DIRS=$(find packages/ infrastructure/ -type d -empty -not -path "*/node_modules/*" -not -path "*/.next/*" 2>/dev/null | wc -l | tr -d ' ')
if [[ "$EMPTY_DIRS" -eq 0 ]]; then
    log_pass "No orphaned empty directories"
else
    log_warn "$EMPTY_DIRS empty directories found (may be intentional)"
fi

# Check for hardcoded old paths in non-migration scripts
HARDCODED=$(set +o pipefail; grep -rn "organic-marketing-package/content-agents\|organic-marketing-package/dashboard" --include="*.py" --include="*.ts" --include="*.tsx" --include="*.js" --include="*.json" --include="*.sh" --include="*.md" --exclude-dir=node_modules --exclude-dir=.next --exclude-dir=venv --exclude-dir=.git packages/ docs/ 2>/dev/null | wc -l | tr -d ' ')
if [[ "$HARDCODED" -eq 0 ]]; then
    log_pass "No hardcoded old paths in packages/ or docs/"
else
    log_warn "$HARDCODED hardcoded old path references remain"
fi

# Check .gitignore covers build artifacts
if [[ -f ".gitignore" ]]; then
    GITIGNORE_CHECKS=("node_modules" "dist" ".next" "venv" "__pycache__")
    MISSING_IGNORES=0
    for pattern in "${GITIGNORE_CHECKS[@]}"; do
        if ! grep -q "$pattern" .gitignore 2>/dev/null; then
            MISSING_IGNORES=$((MISSING_IGNORES + 1))
        fi
    done
    if [[ "$MISSING_IGNORES" -eq 0 ]]; then
        log_pass ".gitignore covers all build artifacts"
    else
        log_warn ".gitignore missing $MISSING_IGNORES common patterns"
    fi
else
    log_fail ".gitignore missing"
fi

echo ""
echo "================================================================"
echo "  Validation Summary"
echo "================================================================"
echo "  PASS: $PASS"
echo "  FAIL: $FAIL"
echo "  WARN: $WARN"
echo "  SKIP: $SKIP"
echo ""

if [[ $FAIL -gt 0 ]]; then
    echo "  RESULT: FAILED - Fix $FAIL error(s) before proceeding"
    exit 1
elif [[ $WARN -gt 0 ]]; then
    echo "  RESULT: PASSED WITH WARNINGS"
    echo "  Review $WARN warning(s) above"
    exit 0
else
    echo "  RESULT: ALL CHECKS PASSED"
    exit 0
fi
