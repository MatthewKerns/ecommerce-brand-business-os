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
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY", "")
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

# Klaviyo API Configuration
KLAVIYO_API_KEY = os.getenv("KLAVIYO_API_KEY", "")
KLAVIYO_API_BASE_URL = os.getenv("KLAVIYO_API_BASE_URL", "https://a.klaviyo.com/api")

# Output configuration
BLOG_OUTPUT_DIR = OUTPUT_DIR / "blog"
SOCIAL_OUTPUT_DIR = OUTPUT_DIR / "social"
AMAZON_OUTPUT_DIR = OUTPUT_DIR / "amazon"
COMPETITOR_OUTPUT_DIR = OUTPUT_DIR / "competitor-analysis"
TIKTOK_OUTPUT_DIR = OUTPUT_DIR / "tiktok"
TIKTOK_CHANNELS_OUTPUT_DIR = OUTPUT_DIR / "tiktok-channels"
AEO_OUTPUT_DIR = OUTPUT_DIR / "aeo"
REDDIT_OUTPUT_DIR = OUTPUT_DIR / "reddit"

# Ensure output directories exist
for dir_path in [BLOG_OUTPUT_DIR, SOCIAL_OUTPUT_DIR, AMAZON_OUTPUT_DIR, COMPETITOR_OUTPUT_DIR, TIKTOK_OUTPUT_DIR, TIKTOK_CHANNELS_OUTPUT_DIR, AEO_OUTPUT_DIR, REDDIT_OUTPUT_DIR]:
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


# TikTok Channel Themes
CHANNEL_THEMES = {
    "air": {
        "visual_style": "Fast cuts, dynamic angles, motion graphics",
        "hook_style": "Question or shocking statement",
        "video_length": "15-30 seconds",
        "key_messages": ["Speed wins", "Be ready", "Quick tips"],
        "hashtags": ["#TCGSpeed", "#QuickTips", "#TournamentReady", "#InfinityVault"]
    },
    "water": {
        "visual_style": "Smooth transitions, emotional close-ups",
        "hook_style": "Personal story or relatable moment",
        "video_length": "30-60 seconds",
        "key_messages": ["Community first", "Share your journey", "We understand"],
        "hashtags": ["#TCGCommunity", "#CollectorStory", "#CardFamily", "#InfinityVault"]
    },
    "earth": {
        "visual_style": "Clear demonstrations, product close-ups",
        "hook_style": "Problem statement or how-to",
        "video_length": "30-45 seconds",
        "key_messages": ["Quality matters", "Built to last", "Protect your investment"],
        "hashtags": ["#CardProtection", "#TCGStorage", "#QualityFirst", "#InfinityVault"]
    },
    "fire": {
        "visual_style": "Bold graphics, high contrast, intense music",
        "hook_style": "Controversial opinion or challenge",
        "video_length": "15-30 seconds",
        "key_messages": ["Challenge accepted", "Prove them wrong", "Be legendary"],
        "hashtags": ["#HotTake", "#TCGDebate", "#Controversial", "#InfinityVault"]
    }
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
            "times": ["8am", "3pm", "7pm"],
            "timezone": "America/New_York"
        }
    },
    "water": {
        "channel_name": "Infinity Vault - Water",
        "element_theme": "water",
        "description": "Community stories, collector journeys, and nostalgic content",
        "target_audience": "Collectors, community members, nostalgia seekers",
        "content_focus": "Community stories, collection showcases, emotional connections, memories",
        "posting_schedule": {
            "frequency": "daily",
            "times": ["10am", "5pm", "9pm"],
            "timezone": "America/New_York"
        }
    },
    "earth": {
        "channel_name": "Infinity Vault - Earth",
        "element_theme": "earth",
        "description": "Product deep dives, durability tests, and educational content",
        "target_audience": "Parents, careful buyers, quality-focused consumers",
        "content_focus": "Product features, protection tests, educational content, value propositions",
        "posting_schedule": {
            "frequency": "3x_week",
            "days": ["Tuesday", "Thursday", "Saturday"],
            "times": ["2pm"],
            "timezone": "America/New_York"
        }
    },
    "fire": {
        "channel_name": "Infinity Vault - Fire",
        "element_theme": "fire",
        "description": "Bold claims, controversial takes, and competitive spirit",
        "target_audience": "Competitive players, debate lovers, engagement seekers",
        "content_focus": "Hot takes, controversial opinions, competitive spirit, bold statements",
        "posting_schedule": {
            "frequency": "daily",
            "times": ["12pm", "6pm"],
            "timezone": "America/New_York"
        }
    }
}

# TikTok scheduling configuration
TIKTOK_SCHEDULER_CONFIG = {
    "max_scheduled_days": 30,
    "min_scheduled_days": 7,
    "buffer_hours": 2,
    "retry_failed_posts": True,
    "retry_max_attempts": 3,
    "auto_reschedule": True
}

# Citation monitoring targets
CITATION_MONITORING_TARGETS = [
    "infinity vault",
    "infinity vault tcg",
    "infinity vault binder",
    "infinity vault deck box",
    "@infinityvault"
]

# AEO (Agentic Engine Optimization) configurations
AEO_PERPLEXITY_QUERIES = [
    "Best TCG storage solutions",
    "Top rated card binders for collectors",
    "Premium deck boxes for competitive players",
    "How to protect valuable trading cards",
    "Best trading card organization systems"
]

AEO_OPENAI_QUERIES = [
    "Trading card storage recommendations",
    "Card collection organization tips",
    "Best binders for Pokemon cards",
    "MTG deck box recommendations",
    "Trading card protection guide"
]

AEO_GEMINI_QUERIES = [
    "Trading card binder reviews",
    "Best card sleeves and protectors",
    "TCG storage solutions comparison",
    "Card collection display options",
    "Tournament deck box features"
]

# AEO (Agentic Engine Optimization) Configuration
AEO_CONFIG = {
    # Tracking frequency
    "monitoring_interval_hours": int(os.getenv("AEO_MONITORING_INTERVAL_HOURS", "6")),
    "batch_size": int(os.getenv("AEO_BATCH_SIZE", "10")),

    # Scoring thresholds
    "opportunity_score_high": 70,
    "opportunity_score_medium": 40,
    "opportunity_score_low": 20,

    # Scoring weights
    "weights": {
        "brand_not_mentioned": 30,
        "competitor_mentioned": 25,
        "high_intent_query": 20,
        "no_citation_url": 15,
        "query_category_relevance": 10,
    },

    # Alert thresholds
    "alert_citation_drop_percent": 20,
    "alert_competitor_gain_percent": 15,
    "alert_min_data_points": 5,

    # Content optimization
    "max_recommendations_per_run": 10,
    "recommendation_cooldown_hours": 48,
}

# AI Platform API Configurations for Citation Tracking
AEO_PLATFORM_CONFIG = {
    "chatgpt": {
        "api_key_env": "OPENAI_API_KEY",
        "model": os.getenv("AEO_CHATGPT_MODEL", "gpt-4o"),
        "max_tokens": 2048,
        "enabled": os.getenv("AEO_CHATGPT_ENABLED", "true").lower() == "true",
    },
    "perplexity": {
        "api_key_env": "PERPLEXITY_API_KEY",
        "model": os.getenv("AEO_PERPLEXITY_MODEL", "llama-3.1-sonar-large-128k-online"),
        "max_tokens": 2048,
        "enabled": os.getenv("AEO_PERPLEXITY_ENABLED", "true").lower() == "true",
    },
    "claude": {
        "api_key_env": "ANTHROPIC_API_KEY",
        "model": os.getenv("AEO_CLAUDE_MODEL", "claude-sonnet-4-5-20250929"),
        "max_tokens": 2048,
        "enabled": os.getenv("AEO_CLAUDE_ENABLED", "true").lower() == "true",
    },
    "google_ai": {
        "api_key_env": "GOOGLE_AI_API_KEY",
        "model": os.getenv("AEO_GOOGLE_MODEL", "gemini-2.0-flash"),
        "max_tokens": 2048,
        "enabled": os.getenv("AEO_GOOGLE_ENABLED", "true").lower() == "true",
    },
}

# Google AI API Key
GOOGLE_AI_API_KEY = os.getenv("GOOGLE_AI_API_KEY", "")

# Reddit Integration Settings (Phase 3)
REDDIT_CONFIG = {
    "client_id": os.getenv("REDDIT_CLIENT_ID", ""),
    "client_secret": os.getenv("REDDIT_CLIENT_SECRET", ""),
    "username": os.getenv("REDDIT_USERNAME", ""),
    "password": os.getenv("REDDIT_PASSWORD", ""),
    "user_agent": os.getenv("REDDIT_USER_AGENT", "InfinityVault AEO Bot v1.0"),
    "target_subreddits": [
        "mtg", "magicTCG", "pkmntcg", "PokemonTCG",
        "yugioh", "lorcana", "FleshandBloodTCG",
        "tradingcardcommunity", "cardgames"
    ],
    "monitoring_keywords": [
        "card storage", "deck box", "binder", "card protection",
        "card organizer", "trading card accessories"
    ],
    "enabled": os.getenv("REDDIT_ENABLED", "false").lower() == "true",
}

# AEO Query Categories
AEO_QUERY_CATEGORIES = {
    "product_discovery": "Queries where users are looking for products",
    "problem_solving": "Queries about solving card storage/protection problems",
    "comparison": "Queries comparing different brands or products",
    "purchase_intent": "Queries with clear buying signals",
    "educational": "Queries seeking knowledge about card care/collecting",
}

# Blog platform configuration
BLOG_PLATFORM_CONFIG = {
    "base_url": os.getenv("BLOG_BASE_URL", "https://infinityvault.com"),
    "api_endpoint": os.getenv("BLOG_API_ENDPOINT", "/api/blog"),
    "auth_token": os.getenv("BLOG_AUTH_TOKEN", ""),
    "auto_publish": os.getenv("BLOG_AUTO_PUBLISH", "false").lower() == "true",
    "draft_review_required": os.getenv("BLOG_DRAFT_REVIEW", "true").lower() == "true"
}

# Product-focused keywords for content
PRODUCT_KEYWORDS = [
    "Trading card binder",
    "9-pocket pages",
    "TCG deck box",
    "Card storage solution",
    "Card collection organizer",
    "Tournament deck case",
    "Premium card protection",
    "Trading card portfolio"
]

# Competitor brands to monitor
COMPETITOR_BRANDS = [
    "Ultra Pro",
    "BCW Supplies",
    "Dragon Shield",
    "Ultimate Guard",
    "Dex Protection",
    "Monster Protectors",
    "Legion Supplies",
    "GameGenic"
]

# High-value search terms for optimization
HIGH_VALUE_SEARCH_TERMS = [
    "Best card binder for Pokemon",
    "MTG deck box with dice tray",
    "Premium trading card storage",
    "9 pocket binder pages bulk",
    "Tournament legal deck box",
    "Waterproof card binder",
    "Side loading card pages",
    "Zipper binder for cards",
    "Top trading card binders",
    "Best card sleeves for protection",
    "How to organize trading card collection",
    "Best deck boxes for TCG players"
]

# Analytics refresh configuration
ANALYTICS_REFRESH_HOURS = int(os.getenv("ANALYTICS_REFRESH_HOURS", "24"))
ANALYTICS_INCREMENTAL_HOURS = int(os.getenv("ANALYTICS_INCREMENTAL_HOURS", "1"))
ANALYTICS_BACKFILL_BATCH_DAYS = int(os.getenv("ANALYTICS_BACKFILL_BATCH_DAYS", "7"))
ANALYTICS_MAX_RETRIES = int(os.getenv("ANALYTICS_MAX_RETRIES", "3"))
ANALYTICS_RETRY_DELAY_SECONDS = int(os.getenv("ANALYTICS_RETRY_DELAY_SECONDS", "60"))

# Refresh schedule configuration
TIKTOK_REFRESH_ENABLED = os.getenv("TIKTOK_REFRESH_ENABLED", "true").lower() == "true"
WEBSITE_REFRESH_ENABLED = os.getenv("WEBSITE_REFRESH_ENABLED", "true").lower() == "true"
EMAIL_REFRESH_ENABLED = os.getenv("EMAIL_REFRESH_ENABLED", "true").lower() == "true"
SALES_REFRESH_ENABLED = os.getenv("SALES_REFRESH_ENABLED", "true").lower() == "true"


# Settings object for convenient access
class Settings:
    """Configuration settings container"""

    # Analytics refresh settings
    analytics_refresh_hours = ANALYTICS_REFRESH_HOURS
    analytics_incremental_hours = ANALYTICS_INCREMENTAL_HOURS
    analytics_backfill_batch_days = ANALYTICS_BACKFILL_BATCH_DAYS
    analytics_max_retries = ANALYTICS_MAX_RETRIES
    analytics_retry_delay_seconds = ANALYTICS_RETRY_DELAY_SECONDS

    # Channel refresh toggles
    tiktok_refresh_enabled = TIKTOK_REFRESH_ENABLED
    website_refresh_enabled = WEBSITE_REFRESH_ENABLED
    email_refresh_enabled = EMAIL_REFRESH_ENABLED
    sales_refresh_enabled = SALES_REFRESH_ENABLED

    # AEO settings
    aeo_config = AEO_CONFIG
    aeo_platform_config = AEO_PLATFORM_CONFIG
    reddit_config = REDDIT_CONFIG
    aeo_query_categories = AEO_QUERY_CATEGORIES


settings = Settings()
