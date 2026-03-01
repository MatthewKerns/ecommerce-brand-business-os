#!/usr/bin/env bash
# migrate-all.sh
#
# Master migration script that runs all individual migration scripts
# in the correct order. Run from the organic-marketing-package root.
#
# Usage:
#   bash infrastructure/scripts/migrate-all.sh              # Execute all migrations
#   bash infrastructure/scripts/migrate-all.sh --dry-run    # Preview only
#
# Order of operations:
#   1. content-agents -> packages/content-engine
#   2. dashboard -> packages/dashboard
#   3. mcf-connector -> packages/mcf-connector
#   4. blog -> packages/blog
#   5. scripts/ and root files -> infrastructure/
#   6. Update Python imports
#   7. Update TypeScript imports
#   8. Run validation

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

DRY_RUN_FLAG=""
if [[ "${1:-}" == "--dry-run" ]]; then
    DRY_RUN_FLAG="--dry-run"
    echo "============================================"
    echo "  DRY RUN - No changes will be made"
    echo "============================================"
fi

cd "$ROOT_DIR"

echo ""
echo "============================================"
echo "  Organic Marketing Package Migration"
echo "============================================"
echo ""
echo "This will reorganize the package into a monorepo structure:"
echo ""
echo "  content-agents/  -> packages/content-engine/"
echo "  dashboard/       -> packages/dashboard/"
echo "  mcf-connector/   -> packages/mcf-connector/"
echo "  blog/            -> packages/blog/"
echo "  scripts/         -> infrastructure/scripts/"
echo "  *.md (root)      -> docs/"
echo ""

if [[ -z "$DRY_RUN_FLAG" ]]; then
    echo "Press Enter to continue or Ctrl+C to abort..."
    read -r
fi

echo ""
echo ">>> Step 1/8: Migrating content-agents..."
bash "$SCRIPT_DIR/migrate-content-agents.sh" $DRY_RUN_FLAG

echo ""
echo ">>> Step 2/8: Migrating dashboard..."
bash "$SCRIPT_DIR/migrate-dashboard.sh" $DRY_RUN_FLAG

echo ""
echo ">>> Step 3/8: Migrating mcf-connector..."
bash "$SCRIPT_DIR/migrate-mcf-connector.sh" $DRY_RUN_FLAG

echo ""
echo ">>> Step 4/8: Migrating blog..."
bash "$SCRIPT_DIR/migrate-blog.sh" $DRY_RUN_FLAG

echo ""
echo ">>> Step 5/8: Migrating infrastructure files..."
bash "$SCRIPT_DIR/migrate-infrastructure.sh" $DRY_RUN_FLAG

echo ""
echo ">>> Step 6/8: Updating Python imports..."
bash "$SCRIPT_DIR/update-python-imports.sh" $DRY_RUN_FLAG

echo ""
echo ">>> Step 7/8: Updating TypeScript imports..."
bash "$SCRIPT_DIR/update-ts-imports.sh" $DRY_RUN_FLAG

echo ""
echo ">>> Step 8/8: Running validation..."
bash "$SCRIPT_DIR/validate-migration.sh" || true

echo ""
echo "============================================"
echo "  Migration Complete"
echo "============================================"
echo ""
echo "Next steps:"
echo "  1. Review changes: git diff --stat"
echo "  2. Run tests in each package"
echo "  3. Commit: git add -A && git commit -m 'refactor: reorganize into monorepo structure'"
echo ""
