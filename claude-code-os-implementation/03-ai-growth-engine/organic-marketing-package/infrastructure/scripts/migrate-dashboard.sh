#!/usr/bin/env bash
# migrate-dashboard.sh
#
# Migrates dashboard/ to packages/dashboard/ using git mv
# to preserve file history. Run from the organic-marketing-package root.
#
# Usage: bash infrastructure/scripts/migrate-dashboard.sh [--dry-run]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
SOURCE="dashboard"
DEST="packages/dashboard"

DRY_RUN=false
if [[ "${1:-}" == "--dry-run" ]]; then
    DRY_RUN=true
    echo "[DRY RUN] No files will be moved."
fi

cd "$ROOT_DIR"

if [[ ! -d "$SOURCE" ]]; then
    echo "ERROR: Source directory '$SOURCE' not found. Already migrated?"
    exit 1
fi

run_cmd() {
    if $DRY_RUN; then
        echo "  [would run] $*"
    else
        "$@"
    fi
}

echo "=== Migrating $SOURCE -> $DEST ==="
echo ""

# Move the entire src directory
echo "--- Moving source code ---"
if [[ -d "$SOURCE/src" ]]; then
    echo "  git mv $SOURCE/src $DEST/src"
    run_cmd git mv "$SOURCE/src" "$DEST/src"
fi

if [[ -d "$SOURCE/public" ]]; then
    echo "  git mv $SOURCE/public $DEST/public"
    run_cmd git mv "$SOURCE/public" "$DEST/public"
fi

echo ""
echo "--- Moving tests ---"
if [[ -d "$SOURCE/tests" ]]; then
    echo "  git mv $SOURCE/tests $DEST/tests"
    run_cmd git mv "$SOURCE/tests" "$DEST/tests"
fi

echo ""
echo "--- Moving configuration files ---"
CONFIG_FILES=(
    package.json
    package-lock.json
    tsconfig.json
    next.config.js
    tailwind.config.js
    postcss.config.js
    .env.example
    .env.local
    .eslintrc.json
    jest.config.js
    jest.config.ts
)

for file in "${CONFIG_FILES[@]}"; do
    if [[ -f "$SOURCE/$file" ]]; then
        echo "  git mv $SOURCE/$file $DEST/$file"
        run_cmd git mv "$SOURCE/$file" "$DEST/$file"
    fi
done

echo ""
echo "--- Moving documentation ---"
DOC_FILES=(
    README.md
)

for file in "${DOC_FILES[@]}"; do
    if [[ -f "$SOURCE/$file" ]]; then
        echo "  git mv $SOURCE/$file $DEST/docs/$file"
        run_cmd mkdir -p "$DEST/docs"
        run_cmd git mv "$SOURCE/$file" "$DEST/docs/$file"
    fi
done

echo ""
echo "--- Skipping build artifacts (.next/, .swc/) ---"
echo "  These will be regenerated on next build."

echo ""
echo "=== Migration complete ==="
echo ""
echo "Next steps:"
echo "  1. Run 'npm install' in packages/dashboard/ to regenerate node_modules"
echo "  2. Run 'bash infrastructure/scripts/update-ts-imports.sh' to fix imports"
echo "  3. Run 'bash infrastructure/scripts/validate-migration.sh' to verify"
