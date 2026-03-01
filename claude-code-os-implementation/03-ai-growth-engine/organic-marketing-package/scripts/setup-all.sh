#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "Setting up Organic Marketing Package..."

# Python setup (content-engine)
echo "--- Setting up Python environment (content-engine) ---"
cd "$ROOT_DIR/packages/content-engine"
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install -r requirements.txt
deactivate

# Node.js setup (all TypeScript packages via npm workspaces)
echo "--- Setting up Node.js packages (via npm workspaces) ---"
cd "$ROOT_DIR"
npm install

# Build shared types first (other packages depend on it)
echo "--- Building shared types ---"
npm run build:shared

echo ""
echo "Setup complete!"
echo "  Content Engine: packages/content-engine/"
echo "  Dashboard:      packages/dashboard/"
echo "  MCF Connector:  packages/mcf-connector/"
echo "  Blog:           packages/blog/"
echo "  Shared:         packages/shared/"
