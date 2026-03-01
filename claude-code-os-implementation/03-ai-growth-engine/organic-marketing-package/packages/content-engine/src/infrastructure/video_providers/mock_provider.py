"""
Mock Video Provider

Mock implementation for testing and development.
Generates JSON representation of video instead of actual video files.
"""

import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import random

from domain.video_generation import (
    VideoGenerationRequest,
    VideoResult,
    VideoStatus,
    ProviderCapability,
    VideoQuality,
    VideoScene,
    VideoTimeline,
    VideoAsset,
)
from .base_provider import BaseVideoProvider

logger = logging.getLogger(__name__)


class MockVideoProvider(BaseVideoProvider):
    """
    Mock video provider for testing and development.

    Generates JSON representation of video structure
    instead of actual video files.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize mock video provider.

        Args:
            config: Provider configuration
        """
        super().__init__(
            provider_id="mock_provider",
            name="Mock Video Provider",
            capabilities=[
                ProviderCapability.TEXT_TO_VIDEO,
                ProviderCapability.ANIMATION,
                ProviderCapability.TRANSITIONS,
                ProviderCapability.AUDIO_MIXING,
            ],
            supported_qualities=list(VideoQuality),  # Support all qualities
            config=config or {}
        )

        # Override default settings for mock provider
        self._info.average_generation_time = 2  # Fast generation
        self._info.cost_per_second = 0.01  # Cheap

        # Storage for generated videos (in memory for mock)
        self._generated_videos: Dict[str, Dict[str, Any]] = {}

    async def _generate_video_impl(self, request: VideoGenerationRequest, result: VideoResult) -> None:
        """
        Generate mock video JSON representation.

        Args:
            request: Video generation request
            result: Result object to update
        """
        logger.info(f"Mock provider generating video for channel: {request.channel}")

        # Simulate processing delay (short for mock)
        await self._simulate_processing_delay(random.uniform(1, 3))

        # Generate timeline from script
        timeline = self._generate_timeline_from_script(request)

        # Create mock video structure
        mock_video = {
            "id": result.id,
            "provider": self.info.id,
            "channel": request.channel,
            "quality": request.quality.value,
            "timeline": self._timeline_to_dict(timeline),
            "script": {
                "topic": request.script.topic,
                "hook": request.script.hook,
                "main_points": request.script.main_points,
                "call_to_action": request.script.call_to_action,
                "duration_seconds": request.script.duration_seconds,
            },
            "render_settings": {
                "width": self._get_width_for_quality(request.quality),
                "height": self._get_height_for_quality(request.quality),
                "fps": 30,
                "format": "mp4",
            },
            "channel_styling": self._get_channel_styling(request.channel),
            "generated_at": datetime.utcnow().isoformat(),
        }

        # Store generated video
        self._generated_videos[result.id] = mock_video

        # Update result
        result.url = self._generate_video_url(result.id, "json")
        result.thumbnail_url = self._generate_thumbnail_url(result.id)
        result.duration_seconds = timeline.total_duration_seconds
        result.file_size_bytes = len(json.dumps(mock_video).encode())
        result.metadata = {
            "type": "mock",
            "format": "json",
            "scenes": len(timeline.scenes),
            "has_audio": bool(timeline.background_music),
            "channel_style": mock_video["channel_styling"],
        }

        logger.info(
            f"Mock video generated: {result.id} "
            f"({len(timeline.scenes)} scenes, {timeline.total_duration_seconds}s)"
        )

    async def _get_status_impl(self, video_id: str) -> Optional[VideoResult]:
        """
        Get status from memory storage.

        Args:
            video_id: Video job ID

        Returns:
            VideoResult or None
        """
        if video_id in self._generated_videos:
            video = self._generated_videos[video_id]
            return VideoResult(
                id=video_id,
                status=VideoStatus.COMPLETED,
                provider_id=self.info.id,
                url=self._generate_video_url(video_id, "json"),
                thumbnail_url=self._generate_thumbnail_url(video_id),
                duration_seconds=video["timeline"]["total_duration_seconds"],
                file_size_bytes=len(json.dumps(video).encode()),
                metadata={"type": "mock", "format": "json"},
            )
        return None

    def _validate_request_impl(self, request: VideoGenerationRequest) -> tuple[bool, Optional[str]]:
        """
        Validate request for mock provider.

        Args:
            request: Video generation request

        Returns:
            Validation result
        """
        # Mock provider accepts everything within base validation
        return True, None

    async def _cancel_generation_impl(self, video_id: str) -> bool:
        """
        Cancel generation (always succeeds for mock).

        Args:
            video_id: Video job ID

        Returns:
            Always True for mock
        """
        if video_id in self._generated_videos:
            del self._generated_videos[video_id]
        return True

    def _generate_timeline_from_script(self, request: VideoGenerationRequest) -> VideoTimeline:
        """
        Generate a timeline from the script.

        Args:
            request: Video generation request

        Returns:
            Generated timeline
        """
        timeline = VideoTimeline()
        script = request.script

        # Generate intro scene
        intro_scene = VideoScene(
            order=0,
            duration_seconds=3.0,
            text=f"@{request.channel.lower()}vibes",
            visual_description="Channel intro animation",
            transitions={"in": "fade", "out": "slide"},
            effects={"glow": True, "particles": self._get_channel_particles(request.channel)},
        )
        timeline.add_scene(intro_scene)

        # Generate hook scene
        hook_scene = VideoScene(
            order=1,
            duration_seconds=5.0,
            text=script.hook,
            voiceover=script.hook,
            visual_description="Attention-grabbing visual",
            transitions={"in": "slide", "out": "dissolve"},
        )
        timeline.add_scene(hook_scene)

        # Generate main content scenes
        for i, point in enumerate(script.main_points):
            main_scene = VideoScene(
                order=i + 2,
                duration_seconds=max(3.0, len(point) / 20),  # Estimate based on text length
                text=point,
                voiceover=point,
                visual_description=f"Visual for point {i+1}",
                transitions={"in": "wipe", "out": "fade"},
            )
            timeline.add_scene(main_scene)

        # Generate CTA scene
        cta_scene = VideoScene(
            order=len(script.main_points) + 2,
            duration_seconds=4.0,
            text=script.call_to_action,
            voiceover=script.call_to_action,
            visual_description="Call to action with button animation",
            transitions={"in": "zoom", "out": "fade"},
            effects={"pulse": True, "button_animation": True},
        )
        timeline.add_scene(cta_scene)

        # Add background music
        timeline.background_music = VideoAsset(
            type="audio",
            url="/audio/background_music.mp3",
            duration_seconds=timeline.total_duration_seconds,
            metadata={"style": script.music_style or "ambient"},
        )

        return timeline

    def _timeline_to_dict(self, timeline: VideoTimeline) -> Dict[str, Any]:
        """
        Convert timeline to dictionary.

        Args:
            timeline: Video timeline

        Returns:
            Dictionary representation
        """
        return {
            "id": timeline.id,
            "total_duration_seconds": timeline.total_duration_seconds,
            "scenes": [
                {
                    "id": scene.id,
                    "order": scene.order,
                    "duration_seconds": scene.duration_seconds,
                    "text": scene.text,
                    "voiceover": scene.voiceover,
                    "visual_description": scene.visual_description,
                    "transitions": scene.transitions,
                    "effects": scene.effects,
                }
                for scene in timeline.scenes
            ],
            "background_music": {
                "url": timeline.background_music.url,
                "style": timeline.background_music.metadata.get("style"),
            } if timeline.background_music else None,
        }

    def _get_width_for_quality(self, quality: VideoQuality) -> int:
        """Get video width for quality level."""
        quality_map = {
            VideoQuality.LOW: 540,
            VideoQuality.STANDARD: 720,
            VideoQuality.HIGH: 1080,
            VideoQuality.ULTRA: 2160,
        }
        return quality_map.get(quality, 1080)

    def _get_height_for_quality(self, quality: VideoQuality) -> int:
        """Get video height for quality level (9:16 aspect ratio for TikTok)."""
        width = self._get_width_for_quality(quality)
        return int(width * 16 / 9)

    def _get_channel_styling(self, channel: str) -> Dict[str, Any]:
        """
        Get channel-specific styling.

        Args:
            channel: Channel name

        Returns:
            Styling configuration
        """
        channel_styles = {
            "air": {
                "primary_color": "#87CEEB",
                "secondary_color": "#FFFFFF",
                "theme": "minimalist",
                "effects": ["float", "breeze", "clouds"],
                "font": "Helvetica Neue",
            },
            "water": {
                "primary_color": "#4682B4",
                "secondary_color": "#E0FFFF",
                "theme": "fluid",
                "effects": ["ripple", "waves", "flow"],
                "font": "Open Sans",
            },
            "earth": {
                "primary_color": "#8B7355",
                "secondary_color": "#228B22",
                "theme": "organic",
                "effects": ["growth", "texture", "natural"],
                "font": "Roboto",
            },
            "fire": {
                "primary_color": "#FF4500",
                "secondary_color": "#FFD700",
                "theme": "energetic",
                "effects": ["spark", "glow", "pulse"],
                "font": "Montserrat",
            },
        }
        return channel_styles.get(channel.lower(), channel_styles["air"])

    def _get_channel_particles(self, channel: str) -> str:
        """Get channel-specific particle effect."""
        particles = {
            "air": "bubbles",
            "water": "droplets",
            "earth": "leaves",
            "fire": "sparks",
        }
        return particles.get(channel.lower(), "stars")

    def get_generated_video(self, video_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the generated video JSON (for testing).

        Args:
            video_id: Video ID

        Returns:
            Generated video dictionary or None
        """
        return self._generated_videos.get(video_id)