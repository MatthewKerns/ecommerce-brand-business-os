#!/usr/bin/env bash
# reorganize-content-agents-root.sh
#
# Moves test/demo .py files from content-agents/ root into organized subdirectories.
# Uses git mv to preserve file history.
#
# Run from the organic-marketing-package root.
#
# Usage: bash infrastructure/scripts/reorganize-content-agents-root.sh [--dry-run]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
CA="content-agents"

DRY_RUN=false
if [[ "${1:-}" == "--dry-run" ]]; then
    DRY_RUN=true
    echo "[DRY RUN] No files will be moved."
fi

cd "$ROOT_DIR"

if [[ ! -d "$CA" ]]; then
    echo "ERROR: $CA/ not found."
    exit 1
fi

run_cmd() {
    if $DRY_RUN; then
        echo "  [would run] $*"
    else
        "$@"
    fi
}

echo "=== Reorganizing content-agents root files ==="
echo ""

# ---------------------------------------------------------------
# Tests: integration tests (TikTok Shop API testing)
# ---------------------------------------------------------------
echo "--- Moving integration test files -> tests/integration/ ---"
run_cmd mkdir -p "$CA/tests/integration"

INTEGRATION_TESTS=(
    test_oauth_flow.py
    test_order_analytics.py
    test_product_sync.py
    test_rate_limiting_errors.py
)

for file in "${INTEGRATION_TESTS[@]}"; do
    if [[ -f "$CA/$file" ]]; then
        echo "  git mv $CA/$file -> $CA/tests/integration/$file"
        run_cmd git mv "$CA/$file" "$CA/tests/integration/$file"
    fi
done

# ---------------------------------------------------------------
# Tests: e2e tests
# ---------------------------------------------------------------
echo ""
echo "--- Moving e2e test files -> tests/e2e/ ---"
run_cmd mkdir -p "$CA/tests/e2e"

E2E_TESTS=(
    test_seo_e2e_workflow.py
    e2e_aeo_verification.py
    aeo_testing_workflow.py
)

for file in "${E2E_TESTS[@]}"; do
    if [[ -f "$CA/$file" ]]; then
        echo "  git mv $CA/$file -> $CA/tests/e2e/$file"
        run_cmd git mv "$CA/$file" "$CA/tests/e2e/$file"
    fi
done

# ---------------------------------------------------------------
# Tests: verification/validation
# ---------------------------------------------------------------
echo ""
echo "--- Moving verification files -> tests/verification/ ---"
run_cmd mkdir -p "$CA/tests/verification"

VERIFICATION_TESTS=(
    aeo_checklist.py
    verify_meta_description.py
    verify_tiktok_config.py
    test_setup.py
    test_video_architecture.py
)

for file in "${VERIFICATION_TESTS[@]}"; do
    if [[ -f "$CA/$file" ]]; then
        echo "  git mv $CA/$file -> $CA/tests/verification/$file"
        run_cmd git mv "$CA/$file" "$CA/tests/verification/$file"
    fi
done

# ---------------------------------------------------------------
# Demo/CLI scripts
# ---------------------------------------------------------------
echo ""
echo "--- Moving demo/script files -> examples/ ---"
run_cmd mkdir -p "$CA/examples"

DEMO_SCRIPTS=(
    tiktok_api_demo.py
    tiktok_demo.py
    generate_content.py
    quick_start.py
    api_video_endpoint.py
)

for file in "${DEMO_SCRIPTS[@]}"; do
    if [[ -f "$CA/$file" ]]; then
        echo "  git mv $CA/$file -> $CA/examples/$file"
        run_cmd git mv "$CA/$file" "$CA/examples/$file"
    fi
done

echo ""
echo "=== Root file reorganization complete ==="
echo ""

# Report what remains at root
echo "--- Files remaining at $CA/ root ---"
remaining=$(find "$CA" -maxdepth 1 -name "*.py" -type f 2>/dev/null | sort)
if [[ -n "$remaining" ]]; then
    echo "$remaining"
    echo ""
    echo "These are core modules (exceptions.py, logging_config.py, celery_app.py)"
    echo "that should stay at the package root."
else
    echo "  (none - all .py files moved)"
fi
