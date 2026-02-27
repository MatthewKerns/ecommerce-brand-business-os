"""
Video Generation Domain Entities

This module defines core domain entities and value objects
for the video generation system.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid


@dataclass
class VideoAsset:
    """Represents an asset used in video generation"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: str = ""  # image, audio, video, text
    url: Optional[str] = None
    content: Optional[str] = None  # For text assets
    duration_seconds: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class VideoScene:
    """Represents a scene in a video"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    order: int = 0
    duration_seconds: float = 3.0
    text: Optional[str] = None
    voiceover: Optional[str] = None
    visual_description: Optional[str] = None
    assets: List[VideoAsset] = field(default_factory=list)
    transitions: Dict[str, Any] = field(default_factory=dict)
    effects: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class VideoTimeline:
    """Represents the complete timeline of a video"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    scenes: List[VideoScene] = field(default_factory=list)
    total_duration_seconds: float = 0.0
    background_music: Optional[VideoAsset] = None
    watermark: Optional[VideoAsset] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def calculate_duration(self) -> float:
        """Calculate total duration from scenes"""
        return sum(scene.duration_seconds for scene in self.scenes)

    def add_scene(self, scene: VideoScene) -> None:
        """Add a scene and update duration"""
        self.scenes.append(scene)
        self.total_duration_seconds = self.calculate_duration()


@dataclass
class VideoProject:
    """Represents a complete video generation project"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    channel: str = ""
    status: str = "draft"  # draft, processing, completed, failed
    timeline: Optional[VideoTimeline] = None
    output_settings: Dict[str, Any] = field(default_factory=dict)
    provider_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def update_status(self, status: str) -> None:
        """Update project status and timestamp"""
        self.status = status
        self.updated_at = datetime.utcnow()
        if status == "completed":
            self.completed_at = datetime.utcnow()


@dataclass
class RenderSettings:
    """Video rendering settings"""
    width: int = 1080
    height: int = 1920  # 9:16 for TikTok
    fps: int = 30
    bitrate: str = "10M"
    codec: str = "h264"
    format: str = "mp4"
    quality_preset: str = "medium"  # ultrafast, fast, medium, slow, veryslow


@dataclass
class ChannelBranding:
    """Channel-specific branding elements"""
    channel: str = ""
    primary_color: str = "#000000"
    secondary_color: str = "#FFFFFF"
    font_family: str = "Arial"
    logo_url: Optional[str] = None
    intro_animation: Optional[str] = None
    outro_animation: Optional[str] = None
    watermark_position: str = "bottom-right"
    visual_theme: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GenerationMetrics:
    """Metrics for video generation performance"""
    generation_time_seconds: float = 0.0
    provider_id: str = ""
    quality_score: Optional[float] = None  # 0-1 quality metric
    cost_estimate: Optional[float] = None
    resource_usage: Dict[str, Any] = field(default_factory=dict)
    error_count: int = 0
    retry_count: int = 0


@dataclass
class ContentElement:
    """Represents a content element in video generation"""
    type: str = ""  # text, image, shape, effect
    content: Any = None
    position: Dict[str, float] = field(default_factory=dict)  # x, y, z
    size: Dict[str, float] = field(default_factory=dict)  # width, height
    animation: Dict[str, Any] = field(default_factory=dict)
    style: Dict[str, Any] = field(default_factory=dict)
    duration: float = 0.0
    start_time: float = 0.0
    end_time: float = 0.0


@dataclass
class AudioTrack:
    """Represents an audio track in the video"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: str = ""  # music, voiceover, effect
    asset: Optional[VideoAsset] = None
    volume: float = 1.0
    fade_in: float = 0.0
    fade_out: float = 0.0
    start_time: float = 0.0
    duration: float = 0.0
    effects: List[Dict[str, Any]] = field(default_factory=list)