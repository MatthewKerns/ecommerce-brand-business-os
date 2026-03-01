#!/bin/bash
# Verification script for TikTokChannelAgent

cd "$(dirname "$0")"

echo "Verifying TikTokChannelAgent..."

# Try to import and initialize the agent
/opt/homebrew/bin/python3 -c "
from agents.tiktok_channel_agent import TikTokChannelAgent
agent = TikTokChannelAgent()
print('Agent initialized successfully')
"

if [ $? -eq 0 ]; then
    echo "✓ TikTokChannelAgent verification passed"
    exit 0
else
    echo "✗ TikTokChannelAgent verification failed"
    exit 1
fi
