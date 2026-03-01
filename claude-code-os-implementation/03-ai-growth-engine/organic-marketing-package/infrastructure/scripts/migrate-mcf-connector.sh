#!/usr/bin/env bash
# migrate-mcf-connector.sh
#
# Migrates mcf-connector/ to packages/mcf-connector/ using git mv
# to preserve file history. Run from the organic-marketing-package root.
#
# Usage: bash infrastructure/scripts/migrate-mcf-connector.sh [--dry-run]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
SOURCE="mcf-connector"
DEST="packages/mcf-connector"

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

echo "--- Moving source code ---"
if [[ -d "$SOURCE/src" ]]; then
    echo "  git mv $SOURCE/src $DEST/src"
    run_cmd git mv "$SOURCE/src" "$DEST/src"
fi

echo ""
echo "--- Moving tests ---"
if [[ -d "$SOURCE/tests" ]]; then
    echo "  git mv $SOURCE/tests $DEST/tests"
    run_cmd git mv "$SOURCE/tests" "$DEST/tests"
fi

echo ""
echo "--- Moving scripts ---"
if [[ -d "$SOURCE/scripts" ]]; then
    echo "  git mv $SOURCE/scripts $DEST/scripts"
    run_cmd git mv "$SOURCE/scripts" "$DEST/scripts"
fi

echo ""
echo "--- Moving configuration files ---"
CONFIG_FILES=(
    package.json
    package-lock.json
    tsconfig.json
    jest.config.ts
    .env.example
    .eslintrc.json
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
echo "--- Skipping node_modules/ (will be reinstalled) ---"

echo ""
echo "=== Migration complete ==="
echo ""
echo "Next steps:"
echo "  1. Run 'npm install' in packages/mcf-connector/ to regenerate node_modules"
echo "  2. Run 'bash infrastructure/scripts/update-ts-imports.sh' to fix imports"
echo "  3. Run 'bash infrastructure/scripts/validate-migration.sh' to verify"
