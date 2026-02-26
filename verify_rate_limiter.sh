#!/bin/bash
# Verification script for rate limiter integration

cd ./ai-content-agents || exit 1

# Test 1: Check if client can be imported
echo "Test 1: Importing TikTokShopClient..."
python3 -c "from integrations.tiktok_shop.client import TikTokShopClient; print('✓ Import successful')" || exit 1

# Test 2: Check if rate limiter attribute exists
echo "Test 2: Checking _rate_limiter attribute..."
python3 -c "from integrations.tiktok_shop.client import TikTokShopClient; c = TikTokShopClient('k','s','t'); assert hasattr(c, '_rate_limiter'); print('✓ Rate limiter attribute exists')" || exit 1

# Test 3: Check if rate limiter is properly initialized
echo "Test 3: Checking rate limiter initialization..."
python3 -c "from integrations.tiktok_shop.client import TikTokShopClient; from integrations.tiktok_shop.rate_limiter import RateLimiter; c = TikTokShopClient('k','s','t'); assert isinstance(c._rate_limiter, RateLimiter); print('✓ Rate limiter properly initialized')" || exit 1

# Test 4: Check rate limiter configuration
echo "Test 4: Checking rate limiter configuration..."
python3 -c "from integrations.tiktok_shop.client import TikTokShopClient; c = TikTokShopClient('k','s','t'); assert c._rate_limiter.requests_per_second == 10.0; assert c._rate_limiter.bucket_capacity == 20; print('✓ Rate limiter configured correctly')" || exit 1

echo ""
echo "✓ All tests passed! Rate limiter integration successful."
