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

# Amazon SP-API Configuration
AMAZON_SELLER_ID = os.getenv("AMAZON_SELLER_ID", "")
AMAZON_SP_API_CLIENT_ID = os.getenv("AMAZON_SP_API_CLIENT_ID", "")
AMAZON_SP_API_CLIENT_SECRET = os.getenv("AMAZON_SP_API_CLIENT_SECRET", "")
AMAZON_SP_API_REFRESH_TOKEN = os.getenv("AMAZON_SP_API_REFRESH_TOKEN", "")
AMAZON_SP_API_REGION = os.getenv("AMAZON_SP_API_REGION", "us-east-1")
AMAZON_MARKETPLACE_ID = os.getenv("AMAZON_MARKETPLACE_ID", "ATVPDKIKX0DER")

# TikTok Shop API Configuration
TIKTOK_SHOP_APP_KEY = os.getenv("TIKTOK_SHOP_APP_KEY", "")
TIKTOK_SHOP_APP_SECRET = os.getenv("TIKTOK_SHOP_APP_SECRET", "")
TIKTOK_SHOP_ACCESS_TOKEN = os.getenv("TIKTOK_SHOP_ACCESS_TOKEN", "")
TIKTOK_SHOP_API_BASE_URL = os.getenv("TIKTOK_SHOP_API_BASE_URL", "https://open-api.tiktokglobalshop.com")

# Output configuration
BLOG_OUTPUT_DIR = OUTPUT_DIR / "blog"
SOCIAL_OUTPUT_DIR = OUTPUT_DIR / "social"
AMAZON_OUTPUT_DIR = OUTPUT_DIR / "amazon"
COMPETITOR_OUTPUT_DIR = OUTPUT_DIR / "competitor-analysis"
TIKTOK_OUTPUT_DIR = OUTPUT_DIR / "tiktok"
AEO_OUTPUT_DIR = OUTPUT_DIR / "aeo"

# Ensure output directories exist
for dir_path in [BLOG_OUTPUT_DIR, SOCIAL_OUTPUT_DIR, AMAZON_OUTPUT_DIR, COMPETITOR_OUTPUT_DIR, TIKTOK_OUTPUT_DIR, AEO_OUTPUT_DIR]:
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

# TikTok 4-Channel Strategy Configuration
TIKTOK_CHANNELS = {
    "air": {
        "channel_name": "Infinity Vault - Air",
        "element_theme": "air",
        "description": "Quick tips, fast moves, and tournament prep for competitive players",
        "target_audience": "Competitive players, tournament grinders, speed strategists",
        "content_focus": "Fast-paced, quick wins, tournament prep hacks, speed strategies",
        "posting_schedule": {
            "frequency": "daily",
            "best_times": ["7:00 AM", "12:00 PM", "6:00 PM"],
            "days": ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        },
        "branding_guidelines": {
            "tone": "Energetic, fast-paced, action-oriented",
            "hashtags": ["#QuickWin", "#TournamentPrep", "#BattleReady", "#SpeedStrategy"],
            "visual_style": "Dynamic, quick cuts, high energy"
        }
    },
    "water": {
        "channel_name": "Infinity Vault - Water",
        "element_theme": "water",
        "description": "Strategy, flow, and adaptability for the thinking player",
        "target_audience": "Strategic thinkers, competitive players seeking edge, meta analysts",
        "content_focus": "Meta analysis, deck tech, strategy guides, adaptation tactics",
        "posting_schedule": {
            "frequency": "5x per week",
            "best_times": ["8:00 AM", "1:00 PM", "7:00 PM"],
            "days": ["monday", "tuesday", "wednesday", "thursday", "friday"]
        },
        "branding_guidelines": {
            "tone": "Analytical, thoughtful, strategic",
            "hashtags": ["#MetaAnalysis", "#DeckTech", "#Strategy", "#AdaptAndWin"],
            "visual_style": "Smooth transitions, calming but focused, analytical overlays"
        }
    },
    "fire": {
        "channel_name": "Infinity Vault - Fire",
        "element_theme": "fire",
        "description": "Hype, energy, and passion for the dedicated collector",
        "target_audience": "Collectors, passionate gamers, community members, hype seekers",
        "content_focus": "Unboxings, collection showcases, epic plays, community stories, tournament hype",
        "posting_schedule": {
            "frequency": "4x per week",
            "best_times": ["9:00 AM", "3:00 PM", "8:00 PM"],
            "days": ["monday", "wednesday", "friday", "saturday"]
        },
        "branding_guidelines": {
            "tone": "Hyped, passionate, celebratory",
            "hashtags": ["#Unboxing", "#EpicPlay", "#CollectorLife", "#GamersUnite"],
            "visual_style": "High energy, dramatic lighting, emotional moments"
        }
    },
    "earth": {
        "channel_name": "Infinity Vault - Earth",
        "element_theme": "earth",
        "description": "Building, collecting, and organizing for the serious hobbyist",
        "target_audience": "Collectors, organizers, long-term players, gear enthusiasts",
        "content_focus": "Collection building, gear reviews, organization tips, long-term strategies",
        "posting_schedule": {
            "frequency": "3x per week",
            "best_times": ["10:00 AM", "2:00 PM", "7:00 PM"],
            "days": ["tuesday", "thursday", "saturday"]
        },
        "branding_guidelines": {
            "tone": "Grounded, methodical, knowledgeable",
            "hashtags": ["#CollectionGoals", "#GearReview", "#OrganizeTCG", "#BuildYourArsenal"],
            "visual_style": "Stable shots, detailed close-ups, satisfying organization"
        }
    }
}

# Channel theme mappings for content generation
CHANNEL_THEMES = {
    "air": {
        "theme_name": "Quick Tips & Fast Moves",
        "content_types": ["quick_tips", "tournament_prep", "speed_strategies", "fast_plays"],
        "tone": "Fast-paced, energetic, action-oriented",
        "key_messages": [
            "Win faster with smart prep",
            "Tournament-ready in minutes",
            "Quick wins for competitive play"
        ],
        "content_pillars": ["Battle-Ready Lifestyle", "Gear & Equipment"],
        "video_length": "15-30 seconds",
        "hook_style": "Start with action or bold statement"
    },
    "water": {
        "theme_name": "Strategy & Flow",
        "content_types": ["meta_analysis", "deck_tech", "strategy_guides", "adaptation_tactics"],
        "tone": "Analytical, thoughtful, strategic",
        "key_messages": [
            "Adapt to win",
            "Master the meta",
            "Strategic advantage through preparation"
        ],
        "content_pillars": ["Battle-Ready Lifestyle", "Collector's Journey"],
        "video_length": "45-60 seconds",
        "hook_style": "Start with question or insight"
    },
    "fire": {
        "theme_name": "Hype & Energy",
        "content_types": ["unboxings", "collection_showcases", "epic_plays", "community_stories"],
        "tone": "Hyped, passionate, celebratory",
        "key_messages": [
            "Celebrate the passion",
            "Epic moments deserve epic gear",
            "Join the collector community"
        ],
        "content_pillars": ["Community Champion", "Collector's Journey"],
        "video_length": "30-60 seconds",
        "hook_style": "Start with excitement or reveal"
    },
    "earth": {
        "theme_name": "Building & Collecting",
        "content_types": ["collection_building", "gear_reviews", "organization_tips", "long_term_strategies"],
        "tone": "Grounded, methodical, knowledgeable",
        "key_messages": [
            "Build your arsenal methodically",
            "Quality gear for serious collectors",
            "Organization is battle preparation"
        ],
        "content_pillars": ["Gear & Equipment", "Collector's Journey"],
        "video_length": "60-90 seconds",
        "hook_style": "Start with problem or showcase result"
    }
}

# TikTok channel output directories
TIKTOK_CHANNELS_OUTPUT_DIR = OUTPUT_DIR / "tiktok" / "channels"
for element in ["air", "water", "fire", "earth"]:
    channel_dir = TIKTOK_CHANNELS_OUTPUT_DIR / element
    channel_dir.mkdir(parents=True, exist_ok=True)
