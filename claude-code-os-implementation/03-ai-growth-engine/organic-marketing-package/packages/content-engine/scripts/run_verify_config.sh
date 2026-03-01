#!/bin/bash
# Verify TikTok channel configuration

set -e

cd "$(dirname "$0")"

echo "Verifying TikTok channel configuration..."
python3 verify_tiktok_config.py
