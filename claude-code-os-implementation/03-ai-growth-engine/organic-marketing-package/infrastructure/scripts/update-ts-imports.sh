#!/usr/bin/env bash
# update-ts-imports.sh
#
# Updates TypeScript/JavaScript imports after migrating packages.
# Fixes relative import paths and workspace references.
#
# Usage: bash infrastructure/scripts/update-ts-imports.sh [--dry-run]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

DRY_RUN=false
if [[ "${1:-}" == "--dry-run" ]]; then
    DRY_RUN=true
    echo "[DRY RUN] No files will be modified."
fi

cd "$ROOT_DIR"

echo "=== Updating TypeScript/JavaScript Imports ==="
echo ""

CHANGES=0

# Update cross-package references in the root scripts and configs
echo "--- Updating root-level references ---"

ROOT_FILES=$(find "$ROOT_DIR" -maxdepth 1 -name "*.sh" -o -name "*.json" -o -name "*.js" -o -name "*.ts" 2>/dev/null || true)
for file in $ROOT_FILES; do
    if grep -q "dashboard/" "$file" 2>/dev/null || grep -q "mcf-connector/" "$file" 2>/dev/null || grep -q "content-agents/" "$file" 2>/dev/null; then
        echo "  Updating: $(basename "$file")"
        if ! $DRY_RUN; then
            sed -i '' 's|"dashboard/|"packages/dashboard/|g' "$file"
            sed -i '' 's|"mcf-connector/|"packages/mcf-connector/|g' "$file"
            sed -i '' 's|"content-agents/|"packages/content-engine/|g' "$file"
            sed -i '' "s|'dashboard/|'packages/dashboard/|g" "$file"
            sed -i '' "s|'mcf-connector/|'packages/mcf-connector/|g" "$file"
            sed -i '' "s|'content-agents/|'packages/content-engine/|g" "$file"
        fi
        CHANGES=$((CHANGES + 1))
    fi
done

echo ""
echo "--- Updating infrastructure script references ---"

INFRA_FILES=$(find "$ROOT_DIR/infrastructure" -name "*.sh" 2>/dev/null || true)
for file in $INFRA_FILES; do
    # Skip the migration scripts themselves
    if [[ "$file" == *"migrate-"* ]] || [[ "$file" == *"update-"* ]]; then
        continue
    fi
    if grep -q "content-agents/" "$file" 2>/dev/null; then
        echo "  Updating: $(basename "$file")"
        if ! $DRY_RUN; then
            sed -i '' 's|content-agents/|packages/content-engine/|g' "$file"
            sed -i '' 's|dashboard/|packages/dashboard/|g' "$file"
            sed -i '' 's|mcf-connector/|packages/mcf-connector/|g' "$file"
        fi
        CHANGES=$((CHANGES + 1))
    fi
done

echo ""
echo "--- Updating dashboard API references ---"
# The dashboard may reference the content-agents API URL in env or config
DASH_CONFIG=$(find "$ROOT_DIR/packages/dashboard" -name "*.env*" -o -name "*.config.*" 2>/dev/null || true)
for file in $DASH_CONFIG; do
    if grep -q "content-agents" "$file" 2>/dev/null; then
        echo "  Updating: $file"
        if ! $DRY_RUN; then
            sed -i '' 's|content-agents|content-engine|g' "$file"
        fi
        CHANGES=$((CHANGES + 1))
    fi
done

echo ""
echo "=== Import update complete: $CHANGES files updated ==="
echo ""
echo "Note: TypeScript packages use workspace references (@organic-marketing/*)"
echo "which are resolved by npm workspaces, so internal package imports"
echo "should not need path updates."
