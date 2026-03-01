#!/usr/bin/env bash
# migrate-blog.sh
#
# Migrates blog/ to packages/blog/ using git mv
# to preserve file history. Run from the organic-marketing-package root.
#
# Usage: bash infrastructure/scripts/migrate-blog.sh [--dry-run]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
SOURCE="blog"
DEST="packages/blog"

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

# Move all source directories
SOURCE_DIRS=(
    app
    components
    content
    lib
    public
)

echo "--- Moving source directories ---"
for dir in "${SOURCE_DIRS[@]}"; do
    if [[ -d "$SOURCE/$dir" ]]; then
        echo "  git mv $SOURCE/$dir $DEST/$dir"
        run_cmd git mv "$SOURCE/$dir" "$DEST/$dir"
    fi
done

echo ""
echo "--- Moving configuration files ---"
CONFIG_FILES=(
    package.json
    package-lock.json
    tsconfig.json
    next.config.js
    tailwind.config.js
    postcss.config.js
    vercel.json
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
    CONTENT_WORKFLOW.md
    DEPLOYMENT.md
    DOMAIN_SETUP.md
    QA_CHECKLIST.md
    STRUCTURED_DATA_VERIFICATION.md
)

run_cmd mkdir -p "$DEST/docs"
for file in "${DOC_FILES[@]}"; do
    if [[ -f "$SOURCE/$file" ]]; then
        echo "  git mv $SOURCE/$file $DEST/docs/$file"
        run_cmd git mv "$SOURCE/$file" "$DEST/docs/$file"
    fi
done

echo ""
echo "=== Migration complete ==="
echo ""
echo "Next steps:"
echo "  1. Run 'npm install' in packages/blog/"
echo "  2. Run 'bash infrastructure/scripts/validate-migration.sh' to verify"
