#!/bin/bash

# Script to reorganize the project structure
# Moving all implementation under organic-marketing-package

echo "🚀 Starting reorganization of organic-marketing-package..."

# Set the target directory
PACKAGE_DIR="claude-code-os-implementation/03-ai-growth-engine/organic-marketing-package"

# 1. Move ai-content-agents to content-agents under package
echo "📦 Moving content agents..."
if [ -d "ai-content-agents" ]; then
    mv ai-content-agents "$PACKAGE_DIR/content-agents"
    echo "  ✅ Moved ai-content-agents → $PACKAGE_DIR/content-agents"
fi

# 2. Move dashboard under package
echo "📦 Moving dashboard..."
if [ -d "dashboard" ]; then
    mv dashboard "$PACKAGE_DIR/dashboard"
    echo "  ✅ Moved dashboard → $PACKAGE_DIR/dashboard"
fi

# 3. Move/rename MCF connector (it's already there but deeply nested)
echo "📦 Reorganizing MCF connector..."
if [ -d "$PACKAGE_DIR/05-mcf-connector-integration/implementation" ]; then
    mv "$PACKAGE_DIR/05-mcf-connector-integration/implementation" "$PACKAGE_DIR/mcf-connector"
    rm -rf "$PACKAGE_DIR/05-mcf-connector-integration"
    echo "  ✅ Moved MCF connector to cleaner location"
fi

# 4. Move docs to package
echo "📦 Moving documentation..."
if [ -d "docs" ]; then
    mv docs "$PACKAGE_DIR/docs"
    echo "  ✅ Moved docs → $PACKAGE_DIR/docs"
fi

# 5. Move Python project files
echo "📦 Moving Python project files..."
for file in pyproject.toml pytest.ini setup_venv.sh install_deps.sh; do
    if [ -f "$file" ]; then
        mv "$file" "$PACKAGE_DIR/content-agents/"
        echo "  ✅ Moved $file"
    fi
done

# 6. Move verification and test scripts
echo "📦 Moving verification scripts..."
for file in verify*.sh test*.sh; do
    if [ -f "$file" ]; then
        mkdir -p "$PACKAGE_DIR/scripts"
        mv "$file" "$PACKAGE_DIR/scripts/"
        echo "  ✅ Moved $file"
    fi
done

# 7. Create package-level README
echo "📄 Creating package README..."
cat > "$PACKAGE_DIR/README.md" << 'EOF'
# Organic Marketing Package

This package contains all the implementation code for the organic marketing automation system.

## Components

### 1. Content Agents (`content-agents/`)
Python-based AI content generation system with:
- Blog, Social, Amazon, Competitor, and TikTok Shop agents
- FastAPI REST API
- Database persistence
- Platform integrations (TikTok Shop, Amazon SP-API)

### 2. MCF Connector (`mcf-connector/`)
TypeScript service for Multi-Channel Fulfillment:
- Order routing between TikTok Shop and Amazon MCF
- Inventory synchronization
- Shipment tracking

### 3. Dashboard (`dashboard/`)
Next.js management interface:
- System health monitoring
- Configuration management
- Metrics visualization
- Multi-tenant workspace support

## Quick Start

```bash
# Install all dependencies
./scripts/setup-all.sh

# Start all services
./scripts/start-services.sh

# Run all tests
./scripts/test-all.sh
```

## Environment Setup

1. Copy `.env.example` files in each component
2. Add your API keys
3. Start services

See `docs/SETUP.md` for detailed instructions.
EOF

# 8. Create consolidated setup script
echo "📄 Creating setup scripts..."
mkdir -p "$PACKAGE_DIR/scripts"

cat > "$PACKAGE_DIR/scripts/setup-all.sh" << 'EOF'
#!/bin/bash
echo "Setting up Organic Marketing Package..."

# Python setup
echo "Setting up Python environment..."
cd content-agents
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Node.js setup
echo "Setting up Node.js projects..."
cd ../mcf-connector
npm install

cd ../dashboard
npm install

echo "✅ Setup complete!"
EOF

cat > "$PACKAGE_DIR/scripts/start-services.sh" << 'EOF'
#!/bin/bash
echo "Starting all services..."

# Start API
echo "Starting FastAPI..."
cd content-agents
source venv/bin/activate
uvicorn api.main:app --reload &

# Start Dashboard
echo "Starting Dashboard..."
cd ../dashboard
npm run dev &

echo "✅ Services started!"
echo "API: http://localhost:8000"
echo "Dashboard: http://localhost:3000"
EOF

cat > "$PACKAGE_DIR/scripts/test-all.sh" << 'EOF'
#!/bin/bash
echo "Running all tests..."

# Python tests
echo "Running Python tests..."
cd content-agents
source venv/bin/activate
pytest

# TypeScript tests
echo "Running TypeScript tests..."
cd ../mcf-connector
npm test

echo "✅ All tests complete!"
EOF

chmod +x "$PACKAGE_DIR/scripts/"*.sh

# 9. Update paths in moved files
echo "🔧 Updating import paths..."

# Update virtual environment path in content-agents
if [ -d "venv" ]; then
    mv venv "$PACKAGE_DIR/content-agents/venv"
    echo "  ✅ Moved Python virtual environment"
fi

echo "✨ Reorganization complete!"
echo ""
echo "New structure:"
echo "  📁 $PACKAGE_DIR/"
echo "    ├── content-agents/     (Python content generation)"
echo "    ├── mcf-connector/      (TypeScript MCF service)"
echo "    ├── dashboard/          (Next.js UI)"
echo "    ├── docs/              (Documentation)"
echo "    └── scripts/           (Utility scripts)"
echo ""
echo "Next steps:"
echo "  1. cd $PACKAGE_DIR"
echo "  2. ./scripts/setup-all.sh"
echo "  3. Update .env files with your API keys"
echo "  4. ./scripts/start-services.sh"