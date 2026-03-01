#!/usr/bin/env bash
# migrate-infrastructure.sh
#
# Migrates scripts/ and root-level shell scripts to infrastructure/
# using git mv to preserve file history.
#
# Usage: bash infrastructure/scripts/migrate-infrastructure.sh [--dry-run]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

DRY_RUN=false
if [[ "${1:-}" == "--dry-run" ]]; then
    DRY_RUN=true
    echo "[DRY RUN] No files will be moved."
fi

cd "$ROOT_DIR"

run_cmd() {
    if $DRY_RUN; then
        echo "  [would run] $*"
    else
        "$@"
    fi
}

echo "=== Migrating infrastructure files ==="
echo ""

# Move scripts/ directory contents
echo "--- Moving scripts/ directory ---"
if [[ -d "scripts" ]]; then
    for file in scripts/*; do
        if [[ -f "$file" ]]; then
            fname=$(basename "$file")
            echo "  git mv $file infrastructure/scripts/$fname"
            run_cmd git mv "$file" "infrastructure/scripts/$fname"
        fi
    done
fi

echo ""
echo "--- Moving root-level shell scripts ---"
ROOT_SCRIPTS=(
    setup_phase3.sh
    start_all.sh
    test_setup.sh
)

for file in "${ROOT_SCRIPTS[@]}"; do
    if [[ -f "$file" ]]; then
        echo "  git mv $file infrastructure/scripts/$file"
        run_cmd git mv "$file" "infrastructure/scripts/$file"
    fi
done

echo ""
echo "--- Moving root-level documentation to docs/ ---"
ROOT_DOCS=(
    SETUP_GUIDE.md
    TROUBLESHOOTING_VIDEO_GENERATOR.md
    VIDEO_GENERATION_UI_GUIDE.md
    AEO_ANALYTICS_ARCHITECTURE.md
)

for file in "${ROOT_DOCS[@]}"; do
    if [[ -f "$file" ]]; then
        echo "  git mv $file docs/$file"
        run_cmd git mv "$file" "docs/$file"
    fi
done

echo ""
echo "=== Migration complete ==="
