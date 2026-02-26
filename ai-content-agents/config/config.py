"""
Configuration for AI Content Agents
"""
import os
from pathlib import Path

# Load environment-specific configuration
try:
    from .environments import load_environment_config
    # Load configuration from environment-specific .env file
    # This ensures the correct .env file is loaded based on ENVIRONMENT variable
    load_environment_config()
except FileNotFoundError:
    # If no environment-specific .env file exists, continue with system environment
    pass
except ImportError:
    # If environments module doesn't exist yet, fall back to default behavior
    pass

# Base paths
BASE_DIR = Path(__file__).parent.parent.parent
AGENTS_DIR = Path(__file__).parent.parent / "agents"
OUTPUT_DIR = Path(__file__).parent.parent / "output"
BRAND_DIR = BASE_DIR / "claude-code-os-implementation"

# Brand knowledge paths
BRAND_VOICE_PATH = BRAND_DIR / "04-content-team" / "brand-voice-guide.md"
BRAND_STRATEGY_PATH = BRAND_DIR / "03-ai-growth-engine" / "positioning" / "brand-strategy.md"
CONTENT_STRATEGY_PATH = BRAND_DIR / "04-content-team" / "content-strategy.md"
VALUE_PROP_PATH = BRAND_DIR / "03-ai-growth-engine" / "business-definition" / "value-proposition.md"
TARGET_MARKET_PATH = BRAND_DIR / "03-ai-growth-engine" / "business-definition" / "target-market.md"

# API Configuration
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
DEFAULT_MODEL = "claude-sonnet-4-5-20250929"
DEFAULT_MAX_TOKENS = 4096

# Output configuration
BLOG_OUTPUT_DIR = OUTPUT_DIR / "blog"
SOCIAL_OUTPUT_DIR = OUTPUT_DIR / "social"
AMAZON_OUTPUT_DIR = OUTPUT_DIR / "amazon"
COMPETITOR_OUTPUT_DIR = OUTPUT_DIR / "competitor-analysis"

# Ensure output directories exist
for dir_path in [BLOG_OUTPUT_DIR, SOCIAL_OUTPUT_DIR, AMAZON_OUTPUT_DIR, COMPETITOR_OUTPUT_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# Brand identity constants
BRAND_NAME = "Infinity Vault"
BRAND_TAGLINE = "Show Up Battle Ready"
BRAND_PROMISE = "Show up to every game feeling confident, prepared, and respected"
BRAND_POSITIONING = "Battle-Ready Equipment (NOT commodity storage)"

# Content pillars
CONTENT_PILLARS = [
    "Battle-Ready Lifestyle",
    "Gear & Equipment",
    "Community Champion",
    "Collector's Journey"
]

# Target channels
CHANNELS = {
    "amazon": "Primary revenue channel",
    "instagram": "Visual showcase",
    "reddit": "Community engagement",
    "discord": "Direct community",
    "youtube": "Brand awareness",
    "blog": "SEO and thought leadership"
}
