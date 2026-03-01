#!/usr/bin/env bash
# validate-migration.sh
#
# Validates the monorepo migration by checking for:
# - Broken imports and references
# - Missing files
# - Orphaned directories
# - Import consistency
#
# Usage: bash infrastructure/scripts/validate-migration.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

cd "$ROOT_DIR"

ERRORS=0
WARNINGS=0

echo "============================================"
echo "  Organic Marketing - Migration Validator"
echo "============================================"
echo ""

# --- Check 1: New directory structure exists ---
echo "--- [1/7] Checking new directory structure ---"

REQUIRED_DIRS=(
    "packages"
    "packages/content-engine"
    "packages/dashboard"
    "packages/mcf-connector"
    "packages/blog"
    "packages/shared"
    "packages/shared/src"
    "infrastructure"
    "infrastructure/scripts"
    "docs"
)

for dir in "${REQUIRED_DIRS[@]}"; do
    if [[ -d "$dir" ]]; then
        echo "  [OK] $dir/"
    else
        echo "  [MISSING] $dir/"
        ERRORS=$((ERRORS + 1))
    fi
done

echo ""

# --- Check 2: Old directories should be empty or gone ---
echo "--- [2/7] Checking old directories are cleaned up ---"

OLD_DIRS=(
    "content-agents"
    "dashboard"
    "mcf-connector"
    "blog"
    "scripts"
)

for dir in "${OLD_DIRS[@]}"; do
    if [[ -d "$dir" ]]; then
        file_count=$(find "$dir" -type f -not -path "*/node_modules/*" -not -path "*/.next/*" -not -path "*/venv/*" -not -path "*/__pycache__/*" 2>/dev/null | wc -l | tr -d ' ')
        if [[ "$file_count" -gt 0 ]]; then
            echo "  [WARN] $dir/ still has $file_count tracked files - migration may be incomplete"
            WARNINGS=$((WARNINGS + 1))
        else
            echo "  [WARN] $dir/ exists but is empty - can be removed"
            WARNINGS=$((WARNINGS + 1))
        fi
    else
        echo "  [OK] $dir/ removed"
    fi
done

echo ""

# --- Check 3: Python import consistency ---
echo "--- [3/7] Checking Python imports ---"

if [[ -d "packages/content-engine" ]]; then
    # Look for imports that still reference old paths
    OLD_IMPORTS=$(grep -rn "content_agents\." packages/content-engine/ --include="*.py" 2>/dev/null | grep -v "__pycache__" | grep -v "venv/" || true)
    if [[ -n "$OLD_IMPORTS" ]]; then
        echo "  [WARN] Found references to old 'content_agents' module:"
        echo "$OLD_IMPORTS" | head -10
        WARNINGS=$((WARNINGS + 1))
    else
        echo "  [OK] No old content_agents imports found"
    fi

    # Check for broken relative imports
    BROKEN=$(grep -rn "from \.\.\." packages/content-engine/src/ --include="*.py" 2>/dev/null | grep -v "__pycache__" || true)
    if [[ -n "$BROKEN" ]]; then
        echo "  [WARN] Found suspicious deep relative imports:"
        echo "$BROKEN" | head -5
        WARNINGS=$((WARNINGS + 1))
    else
        echo "  [OK] No suspicious relative imports"
    fi
else
    echo "  [SKIP] packages/content-engine/ not yet populated"
fi

echo ""

# --- Check 4: TypeScript import consistency ---
echo "--- [4/7] Checking TypeScript imports ---"

TS_PACKAGES=("packages/dashboard" "packages/mcf-connector" "packages/blog")
for pkg in "${TS_PACKAGES[@]}"; do
    if [[ -d "$pkg/src" ]]; then
        # Check for old path references
        OLD_REFS=$(grep -rn "content-agents\|mcf-connector/" "$pkg/src/" --include="*.ts" --include="*.tsx" 2>/dev/null || true)
        if [[ -n "$OLD_REFS" ]]; then
            echo "  [WARN] $pkg has old path references:"
            echo "$OLD_REFS" | head -5
            WARNINGS=$((WARNINGS + 1))
        else
            echo "  [OK] $pkg - no old path references"
        fi
    else
        echo "  [SKIP] $pkg/src/ not yet populated"
    fi
done

echo ""

# --- Check 5: Configuration files exist ---
echo "--- [5/7] Checking package configuration ---"

EXPECTED_CONFIGS=(
    "packages/content-engine/pyproject.toml:Python project config"
    "packages/content-engine/requirements.txt:Python dependencies"
    "packages/dashboard/package.json:Dashboard npm config"
    "packages/mcf-connector/package.json:MCF Connector npm config"
    "packages/shared/package.json:Shared npm config"
)

for entry in "${EXPECTED_CONFIGS[@]}"; do
    file="${entry%%:*}"
    desc="${entry##*:}"
    if [[ -f "$file" ]]; then
        echo "  [OK] $file ($desc)"
    else
        echo "  [MISSING] $file ($desc)"
        WARNINGS=$((WARNINGS + 1))
    fi
done

echo ""

# --- Check 6: README files exist ---
echo "--- [6/7] Checking README files ---"

README_DIRS=(
    "packages"
    "packages/content-engine"
    "packages/dashboard"
    "packages/mcf-connector"
    "packages/blog"
    "packages/shared"
    "infrastructure"
    "docs"
)

for dir in "${README_DIRS[@]}"; do
    if [[ -f "$dir/README.md" ]]; then
        echo "  [OK] $dir/README.md"
    else
        echo "  [MISSING] $dir/README.md"
        WARNINGS=$((WARNINGS + 1))
    fi
done

echo ""

# --- Check 7: No hardcoded absolute paths ---
echo "--- [7/7] Checking for hardcoded paths ---"

HARDCODED=$(grep -rn "organic-marketing-package/content-agents\|organic-marketing-package/dashboard\|organic-marketing-package/mcf-connector" \
    packages/ infrastructure/ docs/ \
    --include="*.py" --include="*.ts" --include="*.tsx" --include="*.js" \
    --include="*.json" --include="*.yaml" --include="*.yml" --include="*.sh" \
    --include="*.toml" --include="*.md" \
    2>/dev/null || true)

if [[ -n "$HARDCODED" ]]; then
    echo "  [WARN] Found hardcoded old paths:"
    echo "$HARDCODED" | head -10
    WARNINGS=$((WARNINGS + 1))
else
    echo "  [OK] No hardcoded old paths found"
fi

echo ""
echo "============================================"
echo "  Validation Results"
echo "============================================"
echo "  Errors:   $ERRORS"
echo "  Warnings: $WARNINGS"
echo ""

if [[ $ERRORS -gt 0 ]]; then
    echo "  STATUS: FAILED - Fix errors before proceeding"
    exit 1
elif [[ $WARNINGS -gt 0 ]]; then
    echo "  STATUS: PASSED WITH WARNINGS"
    echo "  Review warnings above. Some may be expected during incremental migration."
    exit 0
else
    echo "  STATUS: PASSED"
    exit 0
fi
