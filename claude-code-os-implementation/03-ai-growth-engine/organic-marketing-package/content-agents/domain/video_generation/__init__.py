"""
Video Generation Domain Layer

This package contains the core business logic and interfaces
for the video generation system.
"""

from .interfaces import (
    # Enums
    VideoQuality,
    VideoStatus,
    ProviderCapability,

    # Data Classes
    VideoScript,
    VideoGenerationRequest,
    VideoResult,
    ProviderInfo,

    # Interfaces
    IVideoProvider,
    IScriptParser,
    IChannelStrategy,
    IProviderRegistry,
    IChannelStrategyFactory,
    IConfigManager,
)

from .entities import (
    VideoAsset,
    VideoScene,
    VideoTimeline,
    VideoProject,
    RenderSettings,
    ChannelBranding,
    GenerationMetrics,
    ContentElement,
    AudioTrack,
)

__all__ = [
    # Enums
    'VideoQuality',
    'VideoStatus',
    'ProviderCapability',

    # Data Classes
    'VideoScript',
    'VideoGenerationRequest',
    'VideoResult',
    'ProviderInfo',

    # Interfaces
    'IVideoProvider',
    'IScriptParser',
    'IChannelStrategy',
    'IProviderRegistry',
    'IChannelStrategyFactory',
    'IConfigManager',

    # Entities
    'VideoAsset',
    'VideoScene',
    'VideoTimeline',
    'VideoProject',
    'RenderSettings',
    'ChannelBranding',
    'GenerationMetrics',
    'ContentElement',
    'AudioTrack',
]