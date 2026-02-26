#!/bin/bash
cd ./ai-content-agents
python3 -c "from agents.tiktok_shop_agent import TikTokShopAgent; agent = TikTokShopAgent(); print('OK')" 2>&1
