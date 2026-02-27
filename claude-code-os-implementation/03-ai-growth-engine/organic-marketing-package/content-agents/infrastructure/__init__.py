"""
Infrastructure Layer

Infrastructure implementations and integrations.
"""

from .video_providers import BaseVideoProvider, MockVideoProvider
from .strategies import (
    ChannelStrategyFactory,
    AirChannelStrategy,
    WaterChannelStrategy,
    EarthChannelStrategy,
    FireChannelStrategy,
)
from .parsers import TikTokScriptParser
from .config import VideoConfigManager
from .di import setup_di_container, create_video_generation_service

__all__ = [
    # Video Providers
    'BaseVideoProvider',
    'MockVideoProvider',

    # Strategies
    'ChannelStrategyFactory',
    'AirChannelStrategy',
    'WaterChannelStrategy',
    'EarthChannelStrategy',
    'FireChannelStrategy',

    # Parsers
    'TikTokScriptParser',

    # Configuration
    'VideoConfigManager',

    # DI
    'setup_di_container',
    'create_video_generation_service',
]