#!/usr/bin/env python3
"""Verify TikTok channel configuration"""

from config.config import TIKTOK_CHANNELS, CHANNEL_THEMES

# Verify TIKTOK_CHANNELS
print(f"Number of TikTok channels: {len(TIKTOK_CHANNELS)}")
assert len(TIKTOK_CHANNELS) == 4, f"Expected 4 channels, got {len(TIKTOK_CHANNELS)}"

# Verify all 4 elements are present
elements = ["air", "water", "fire", "earth"]
for element in elements:
    assert element in TIKTOK_CHANNELS, f"Missing element: {element}"
    print(f"✓ Channel '{element}' found: {TIKTOK_CHANNELS[element]['channel_name']}")

# Verify CHANNEL_THEMES
print(f"\nNumber of channel themes: {len(CHANNEL_THEMES)}")
assert len(CHANNEL_THEMES) == 4, f"Expected 4 themes, got {len(CHANNEL_THEMES)}"

for element in elements:
    assert element in CHANNEL_THEMES, f"Missing theme for element: {element}"
    print(f"✓ Theme '{element}': {CHANNEL_THEMES[element]['theme_name']}")

print("\n✓ All configuration checks passed!")
print("4")  # Expected output for verification
