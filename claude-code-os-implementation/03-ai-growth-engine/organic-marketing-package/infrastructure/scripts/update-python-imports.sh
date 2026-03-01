#!/usr/bin/env bash
# update-python-imports.sh
#
# Updates Python imports after migrating content-agents/ to packages/content-engine/.
# Rewrites import paths for the new src/ directory structure.
#
# Usage: bash infrastructure/scripts/update-python-imports.sh [--dry-run]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
CONTENT_ENGINE="$ROOT_DIR/packages/content-engine"

DRY_RUN=false
if [[ "${1:-}" == "--dry-run" ]]; then
    DRY_RUN=true
    echo "[DRY RUN] No files will be modified."
fi

cd "$ROOT_DIR"

if [[ ! -d "$CONTENT_ENGINE/src" ]]; then
    echo "ERROR: packages/content-engine/src/ not found."
    echo "Run migrate-content-agents.sh first."
    exit 1
fi

echo "=== Updating Python Imports ==="
echo ""

# Map of old import prefixes to new ones
# After migration, modules that were at content-agents/agents/ are now at
# packages/content-engine/src/agents/. Internal Python imports reference
# the module name directly (e.g., 'from agents.blog_agent import ...').
# These don't need path changes since they're relative to the Python path.
#
# What DOES need updating:
# 1. Any absolute path references in config files
# 2. Import paths that referenced the old directory structure

# Find all Python files in the content-engine package
PY_FILES=$(find "$CONTENT_ENGINE" -name "*.py" -not -path "*/venv/*" -not -path "*/__pycache__/*" 2>/dev/null)

CHANGES=0

for file in $PY_FILES; do
    # Check for imports that reference old paths
    if grep -qE "content.agents\." "$file" 2>/dev/null; then
        echo "  Updating imports in: $(basename "$file")"
        if ! $DRY_RUN; then
            # Replace content_agents.X with src.X or just X depending on context
            sed -i '' 's/content_agents\.\(agents\)/\1/g' "$file"
            sed -i '' 's/content_agents\.\(services\)/\1/g' "$file"
            sed -i '' 's/content_agents\.\(infrastructure\)/\1/g' "$file"
            sed -i '' 's/content_agents\.\(integrations\)/\1/g' "$file"
            sed -i '' 's/content_agents\.\(database\)/\1/g' "$file"
            sed -i '' 's/content_agents\.\(domain\)/\1/g' "$file"
            sed -i '' 's/content_agents\.\(api\)/\1/g' "$file"
            sed -i '' 's/content_agents\.\(analytics\)/\1/g' "$file"
            sed -i '' 's/content_agents\.\(config\)/\1/g' "$file"
            sed -i '' 's/content_agents\.\(utils\)/\1/g' "$file"
        fi
        CHANGES=$((CHANGES + 1))
    fi
done

echo ""
echo "--- Updating configuration references ---"

# Update any YAML, JSON, or TOML config files that reference old paths
CONFIG_PATTERNS=(
    "content-agents/"
    "content_agents/"
)

for pattern in "${CONFIG_PATTERNS[@]}"; do
    MATCHES=$(grep -rl "$pattern" "$CONTENT_ENGINE" --include="*.json" --include="*.toml" --include="*.yaml" --include="*.yml" --include="*.cfg" --include="*.ini" 2>/dev/null || true)
    for file in $MATCHES; do
        echo "  Updating config: $(basename "$file")"
        if ! $DRY_RUN; then
            sed -i '' "s|content-agents/|packages/content-engine/src/|g" "$file"
            sed -i '' "s|content_agents/|packages/content-engine/src/|g" "$file"
        fi
        CHANGES=$((CHANGES + 1))
    done
done

echo ""
echo "=== Import update complete: $CHANGES files updated ==="
echo ""
echo "Next steps:"
echo "  1. Run 'bash infrastructure/scripts/validate-migration.sh' to check for broken imports"
echo "  2. Test with: cd packages/content-engine && python -c 'from src.agents import blog_agent'"
