#!/usr/bin/env bash
# migrate-content-agents.sh
#
# Migrates content-agents/ to packages/content-engine/ using git mv
# to preserve file history. Run from the organic-marketing-package root.
#
# Usage: bash infrastructure/scripts/migrate-content-agents.sh [--dry-run]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
SOURCE="content-agents"
DEST="packages/content-engine"

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

# Core source directories
CORE_DIRS=(
    agents
    analytics
    api
    application
    config
    database
    domain
    infrastructure
    integrations
    scheduler
    services
    tasks
    templates
    utils
)

echo "--- Moving core source directories ---"
for dir in "${CORE_DIRS[@]}"; do
    if [[ -d "$SOURCE/$dir" ]]; then
        echo "  git mv $SOURCE/$dir $DEST/src/$dir"
        run_cmd mkdir -p "$DEST/src"
        run_cmd git mv "$SOURCE/$dir" "$DEST/src/$dir"
    else
        echo "  [skip] $SOURCE/$dir (not found)"
    fi
done

echo ""
echo "--- Moving test directories ---"
if [[ -d "$SOURCE/tests" ]]; then
    echo "  git mv $SOURCE/tests $DEST/tests"
    run_cmd git mv "$SOURCE/tests" "$DEST/tests"
fi

echo ""
echo "--- Moving configuration files ---"
CONFIG_FILES=(
    pyproject.toml
    pytest.ini
    requirements.txt
    exceptions.py
    logging_config.py
    celery_app.py
)

for file in "${CONFIG_FILES[@]}"; do
    if [[ -f "$SOURCE/$file" ]]; then
        echo "  git mv $SOURCE/$file $DEST/$file"
        run_cmd git mv "$SOURCE/$file" "$DEST/$file"
    fi
done

echo ""
echo "--- Moving test/demo files (to be relocated by task #3) ---"
# These are test/demo files at content-agents root that should go to tests/
TEST_DEMO_FILES=(
    aeo_checklist.py
    aeo_testing_workflow.py
    api_video_endpoint.py
    e2e_aeo_verification.py
    generate_content.py
    quick_start.py
    test_oauth_flow.py
    test_order_analytics.py
    test_product_sync.py
    test_rate_limiting_errors.py
    test_seo_e2e_workflow.py
    test_setup.py
    test_video_architecture.py
    tiktok_api_demo.py
    tiktok_demo.py
    verify_meta_description.py
    verify_tiktok_config.py
)

run_cmd mkdir -p "$DEST/tests/root-level"
for file in "${TEST_DEMO_FILES[@]}"; do
    if [[ -f "$SOURCE/$file" ]]; then
        echo "  git mv $SOURCE/$file $DEST/tests/root-level/$file"
        run_cmd git mv "$SOURCE/$file" "$DEST/tests/root-level/$file"
    fi
done

echo ""
echo "--- Moving documentation files ---"
DOC_FILES=(
    README.md
    AEO_E2E_VERIFICATION_GUIDE.md
    AEO_VERIFICATION_SUMMARY.md
    API_TEST_RESULTS.md
    MANUAL_TESTING.md
    RATE_LIMITING_ERROR_HANDLING_TESTING.md
    TESTING_INSTRUCTIONS.md
    VALIDATION.md
    VERIFICATION_CHECKLIST.md
)

run_cmd mkdir -p "$DEST/docs"
for file in "${DOC_FILES[@]}"; do
    if [[ -f "$SOURCE/$file" ]]; then
        echo "  git mv $SOURCE/$file $DEST/docs/$file"
        run_cmd git mv "$SOURCE/$file" "$DEST/docs/$file"
    fi
done

echo ""
echo "--- Moving shell scripts ---"
SHELL_SCRIPTS=(
    install_deps.sh
    run_rate_limiting_tests.sh
    run_verify_config.sh
    setup_venv.sh
    test_api_manual.sh
    verify_blog_routes.sh
    verify_tiktok_channel_agent.sh
)

for file in "${SHELL_SCRIPTS[@]}"; do
    if [[ -f "$SOURCE/$file" ]]; then
        echo "  git mv $SOURCE/$file $DEST/$file"
        run_cmd git mv "$SOURCE/$file" "$DEST/$file"
    fi
done

echo ""
echo "--- Moving output and data directories ---"
for dir in examples logs output; do
    if [[ -d "$SOURCE/$dir" ]]; then
        echo "  git mv $SOURCE/$dir $DEST/$dir"
        run_cmd git mv "$SOURCE/$dir" "$DEST/$dir"
    fi
done

echo ""
echo "--- Moving JSON data files ---"
for file in "$SOURCE"/*.json; do
    if [[ -f "$file" ]]; then
        fname=$(basename "$file")
        echo "  git mv $file $DEST/$fname"
        run_cmd git mv "$file" "$DEST/$fname"
    fi
done

echo ""
echo "=== Migration complete ==="
echo ""
echo "Next steps:"
echo "  1. Run 'bash infrastructure/scripts/update-python-imports.sh' to fix imports"
echo "  2. Run 'bash infrastructure/scripts/validate-migration.sh' to verify"
echo "  3. Review and commit the changes"
