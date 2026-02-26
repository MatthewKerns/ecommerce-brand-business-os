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
