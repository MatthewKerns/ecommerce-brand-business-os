"""
Video Generation Domain Interfaces

This module defines the core interfaces for the video generation system
following clean architecture principles and the Plugin Architecture pattern.
"""

from typing import Protocol, Dict, Any, Optional, List, runtime_checkable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


# Enums
class VideoQuality(Enum):
    """Video quality levels supported by the system"""
    LOW = "low"          # 480p, quick generation
    STANDARD = "standard"  # 720p, balanced quality/speed
    HIGH = "high"        # 1080p, high quality
    ULTRA = "ultra"      # 4K, maximum quality


class VideoStatus(Enum):
    """Video generation status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ProviderCapability(Enum):
    """Capabilities that video providers may support"""
    TEXT_TO_VIDEO = "text_to_video"
    IMAGE_SEQUENCE = "image_sequence"
    ANIMATION = "animation"
    TRANSITIONS = "transitions"
    AUDIO_MIXING = "audio_mixing"
    AI_GENERATION = "ai_generation"
    AVATAR_GENERATION = "avatar_generation"
    STYLE_TRANSFER = "style_transfer"
    REAL_TIME = "real_time"
    BATCH_PROCESSING = "batch_processing"


# Data Classes
@dataclass
class VideoScript:
    """Parsed video script with structured content"""
    channel: str
    topic: str
    hook: str
    main_points: List[str]
    call_to_action: str
    duration_seconds: int
    visual_style: str
    music_style: Optional[str] = None
    transitions: Optional[List[str]] = None
    required_features: List[ProviderCapability] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.required_features is None:
            self.required_features = []
        if self.metadata is None:
            self.metadata = {}


@dataclass
class VideoGenerationRequest:
    """Request for video generation"""
    script: VideoScript
    channel: str
    quality: VideoQuality
    provider_hint: Optional[str] = None  # Suggested provider
    options: Dict[str, Any] = None
    priority: int = 5  # 1-10, higher is more urgent
    callback_url: Optional[str] = None

    def __post_init__(self):
        if self.options is None:
            self.options = {}


@dataclass
class VideoResult:
    """Result from video generation"""
    id: str
    status: VideoStatus
    provider_id: str
    url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    duration_seconds: Optional[int] = None
    file_size_bytes: Optional[int] = None
    metadata: Dict[str, Any] = None
    error_message: Optional[str] = None
    created_at: datetime = None
    completed_at: Optional[datetime] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.created_at is None:
            self.created_at = datetime.utcnow()


@dataclass
class ProviderInfo:
    """Information about a video provider"""
    id: str
    name: str
    capabilities: List[ProviderCapability]
    supported_qualities: List[VideoQuality]
    max_duration_seconds: int
    cost_per_second: float  # Relative cost indicator
    average_generation_time: int  # Seconds
    is_available: bool
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


# Protocol Interfaces
@runtime_checkable
class IVideoProvider(Protocol):
    """
    Video provider interface following Plugin Architecture pattern.

    All video generation providers must implement this interface
    to be compatible with the video generation system.
    """

    @property
    def info(self) -> ProviderInfo:
        """Get provider information and capabilities"""
        ...

    async def generate_video(self, request: VideoGenerationRequest) -> VideoResult:
        """
        Generate a video based on the request.

        Args:
            request: Video generation request with script and options

        Returns:
            VideoResult with status and generated video information
        """
        ...

    async def get_status(self, video_id: str) -> VideoResult:
        """
        Get the status of a video generation job.

        Args:
            video_id: ID of the video generation job

        Returns:
            Current status and information about the video
        """
        ...

    def validate_request(self, request: VideoGenerationRequest) -> tuple[bool, Optional[str]]:
        """
        Validate if this provider can handle the request.

        Args:
            request: Video generation request to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        ...

    async def cancel_generation(self, video_id: str) -> bool:
        """
        Cancel an in-progress video generation.

        Args:
            video_id: ID of the video to cancel

        Returns:
            True if cancelled successfully
        """
        ...


@runtime_checkable
class IScriptParser(Protocol):
    """Interface for parsing raw scripts into structured format"""

    def parse(self, raw_script: Dict[str, Any]) -> VideoScript:
        """
        Parse a raw script into structured VideoScript format.

        Args:
            raw_script: Raw script data from content generation

        Returns:
            Structured VideoScript object
        """
        ...

    def validate_script(self, script: VideoScript) -> tuple[bool, Optional[str]]:
        """
        Validate a parsed script.

        Args:
            script: VideoScript to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        ...

    def extract_required_features(self, script: VideoScript) -> List[ProviderCapability]:
        """
        Extract required provider capabilities from script.

        Args:
            script: VideoScript to analyze

        Returns:
            List of required provider capabilities
        """
        ...


@runtime_checkable
class IChannelStrategy(Protocol):
    """Interface for channel-specific video generation strategies"""

    @property
    def channel_name(self) -> str:
        """Get the channel name this strategy handles"""
        ...

    def enhance_request(self, request: VideoGenerationRequest) -> VideoGenerationRequest:
        """
        Apply channel-specific enhancements to the request.

        Args:
            request: Original video generation request

        Returns:
            Enhanced request with channel-specific modifications
        """
        ...

    def get_visual_style(self) -> Dict[str, Any]:
        """
        Get channel-specific visual style configuration.

        Returns:
            Visual style configuration for the channel
        """
        ...

    def get_audio_style(self) -> Dict[str, Any]:
        """
        Get channel-specific audio style configuration.

        Returns:
            Audio style configuration for the channel
        """
        ...

    def validate_content(self, script: VideoScript) -> tuple[bool, Optional[str]]:
        """
        Validate if content aligns with channel guidelines.

        Args:
            script: VideoScript to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        ...


@runtime_checkable
class IProviderRegistry(Protocol):
    """Interface for managing and selecting video providers"""

    def register_provider(self, provider: IVideoProvider) -> None:
        """Register a video provider"""
        ...

    def unregister_provider(self, provider_id: str) -> None:
        """Unregister a video provider"""
        ...

    def get_provider(self, provider_id: str) -> Optional[IVideoProvider]:
        """Get a specific provider by ID"""
        ...

    def list_providers(self) -> List[ProviderInfo]:
        """List all available providers"""
        ...

    def select_provider(
        self,
        quality: VideoQuality,
        required_features: List[ProviderCapability],
        channel: Optional[str] = None,
        prefer_provider: Optional[str] = None
    ) -> Optional[IVideoProvider]:
        """
        Select the best provider based on requirements.

        Args:
            quality: Required video quality
            required_features: List of required capabilities
            channel: Optional channel for channel-specific selection
            prefer_provider: Optional preferred provider ID

        Returns:
            Best matching provider or None if no match
        """
        ...


@runtime_checkable
class IChannelStrategyFactory(Protocol):
    """Factory for creating channel-specific strategies"""

    def get_strategy(self, channel: str) -> IChannelStrategy:
        """
        Get strategy for a specific channel.

        Args:
            channel: Channel name (air, water, earth, fire)

        Returns:
            Channel-specific strategy
        """
        ...

    def register_strategy(self, channel: str, strategy: IChannelStrategy) -> None:
        """Register a channel strategy"""
        ...


@runtime_checkable
class IConfigManager(Protocol):
    """Interface for managing video generation configuration"""

    def get_provider_config(self, provider_id: str) -> Dict[str, Any]:
        """Get configuration for a specific provider"""
        ...

    def update_provider_config(self, provider_id: str, config: Dict[str, Any]) -> None:
        """Update provider configuration"""
        ...

    def get_channel_config(self, channel: str) -> Dict[str, Any]:
        """Get configuration for a specific channel"""
        ...

    def get_global_config(self) -> Dict[str, Any]:
        """Get global video generation configuration"""
        ...

    def reload_config(self) -> None:
        """Reload configuration from source"""
        ...