"""
Channel-Specific Strategies

Implementation of channel-specific video generation strategies
based on the four elements concept.
"""

import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass

from domain.video_generation import (
    IChannelStrategy,
    VideoGenerationRequest,
    VideoScript,
    ProviderCapability,
)

logger = logging.getLogger(__name__)


@dataclass
class ChannelStyle:
    """Channel-specific style configuration"""
    primary_color: str
    secondary_color: str
    accent_color: str
    font_family: str
    font_weight: str
    animation_style: str
    transition_speed: str
    particle_effect: str
    background_style: str
    music_genre: str
    voice_tone: str


class BaseChannelStrategy(IChannelStrategy):
    """Base implementation for channel strategies"""

    def __init__(self, channel_name: str, style: ChannelStyle):
        """
        Initialize base channel strategy.

        Args:
            channel_name: Name of the channel
            style: Channel style configuration
        """
        self._channel_name = channel_name
        self._style = style

    @property
    def channel_name(self) -> str:
        """Get the channel name this strategy handles."""
        return self._channel_name

    def enhance_request(self, request: VideoGenerationRequest) -> VideoGenerationRequest:
        """
        Apply channel-specific enhancements to the request.

        Args:
            request: Original video generation request

        Returns:
            Enhanced request with channel-specific modifications
        """
        # Add channel-specific visual style
        if "visual_style" not in request.options:
            request.options["visual_style"] = self.get_visual_style()

        # Add channel-specific audio style
        if "audio_style" not in request.options:
            request.options["audio_style"] = self.get_audio_style()

        # Add channel-specific effects
        request.options["channel_effects"] = self._get_channel_effects()

        # Enhance script with channel-specific elements
        self._enhance_script(request.script)

        return request

    def get_visual_style(self) -> Dict[str, Any]:
        """
        Get channel-specific visual style configuration.

        Returns:
            Visual style configuration
        """
        return {
            "primary_color": self._style.primary_color,
            "secondary_color": self._style.secondary_color,
            "accent_color": self._style.accent_color,
            "font": {
                "family": self._style.font_family,
                "weight": self._style.font_weight,
            },
            "animations": {
                "style": self._style.animation_style,
                "speed": self._style.transition_speed,
            },
            "background": {
                "style": self._style.background_style,
                "particles": self._style.particle_effect,
            },
        }

    def get_audio_style(self) -> Dict[str, Any]:
        """
        Get channel-specific audio style configuration.

        Returns:
            Audio style configuration
        """
        return {
            "music": {
                "genre": self._style.music_genre,
                "energy": self._get_audio_energy(),
                "tempo": self._get_audio_tempo(),
            },
            "voice": {
                "tone": self._style.voice_tone,
                "speed": self._get_voice_speed(),
                "pitch": self._get_voice_pitch(),
            },
            "effects": self._get_audio_effects(),
        }

    def validate_content(self, script: VideoScript) -> tuple[bool, Optional[str]]:
        """
        Validate if content aligns with channel guidelines.

        Args:
            script: VideoScript to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check duration
        if script.duration_seconds > self._get_max_duration():
            return False, f"Duration exceeds {self._channel_name} channel maximum"

        # Check content alignment
        if not self._validate_content_theme(script):
            return False, f"Content doesn't align with {self._channel_name} channel theme"

        return True, None

    def _enhance_script(self, script: VideoScript) -> None:
        """Enhance script with channel-specific elements"""
        # Add channel-specific visual style if not set
        if not script.visual_style:
            script.visual_style = self._style.animation_style

        # Add channel-specific music style if not set
        if not script.music_style:
            script.music_style = self._style.music_genre

    def _get_channel_effects(self) -> Dict[str, Any]:
        """Get channel-specific effects"""
        return {
            "particles": self._style.particle_effect,
            "transitions": self._get_transition_effects(),
            "overlays": self._get_overlay_effects(),
        }

    def _get_audio_energy(self) -> str:
        """Get audio energy level for channel"""
        return "medium"  # Default, overridden in subclasses

    def _get_audio_tempo(self) -> int:
        """Get audio tempo for channel"""
        return 120  # Default BPM, overridden in subclasses

    def _get_voice_speed(self) -> float:
        """Get voice speed for channel"""
        return 1.0  # Default, overridden in subclasses

    def _get_voice_pitch(self) -> float:
        """Get voice pitch for channel"""
        return 1.0  # Default, overridden in subclasses

    def _get_audio_effects(self) -> list:
        """Get audio effects for channel"""
        return []  # Default, overridden in subclasses

    def _get_max_duration(self) -> int:
        """Get maximum duration for channel"""
        return 60  # Default 60 seconds

    def _validate_content_theme(self, script: VideoScript) -> bool:
        """Validate if content theme matches channel"""
        return True  # Default, overridden in subclasses

    def _get_transition_effects(self) -> list:
        """Get transition effects for channel"""
        return ["fade"]  # Default

    def _get_overlay_effects(self) -> list:
        """Get overlay effects for channel"""
        return []  # Default


class AirChannelStrategy(BaseChannelStrategy):
    """
    Air Channel Strategy - Mental clarity and flow states

    Focuses on minimalist design, clean transitions,
    and content promoting mental clarity.
    """

    def __init__(self):
        style = ChannelStyle(
            primary_color="#87CEEB",  # Sky blue
            secondary_color="#FFFFFF",  # White
            accent_color="#E0FFFF",  # Light cyan
            font_family="Helvetica Neue",
            font_weight="300",  # Light
            animation_style="smooth_float",
            transition_speed="slow",
            particle_effect="clouds",
            background_style="gradient_sky",
            music_genre="ambient",
            voice_tone="calm"
        )
        super().__init__("air", style)

    def _get_audio_energy(self) -> str:
        return "low"

    def _get_audio_tempo(self) -> int:
        return 80  # Slow, meditative

    def _get_voice_speed(self) -> float:
        return 0.9  # Slightly slower

    def _get_voice_pitch(self) -> float:
        return 0.95  # Slightly lower

    def _get_audio_effects(self) -> list:
        return ["reverb", "echo_subtle"]

    def _validate_content_theme(self, script: VideoScript) -> bool:
        """Ensure content promotes mental clarity"""
        clarity_keywords = ["focus", "clarity", "mindful", "peace", "flow", "breath"]
        topic_lower = script.topic.lower()
        return any(keyword in topic_lower for keyword in clarity_keywords)

    def _get_transition_effects(self) -> list:
        return ["fade", "dissolve", "float"]

    def _get_overlay_effects(self) -> list:
        return ["soft_glow", "light_particles"]


class WaterChannelStrategy(BaseChannelStrategy):
    """
    Water Channel Strategy - Emotional intelligence and wellness

    Focuses on fluid design, flowing transitions,
    and content promoting emotional wellness.
    """

    def __init__(self):
        style = ChannelStyle(
            primary_color="#4682B4",  # Steel blue
            secondary_color="#E0FFFF",  # Light cyan
            accent_color="#00CED1",  # Dark turquoise
            font_family="Open Sans",
            font_weight="400",  # Regular
            animation_style="fluid_wave",
            transition_speed="medium",
            particle_effect="water_drops",
            background_style="gradient_ocean",
            music_genre="new_age",
            voice_tone="soothing"
        )
        super().__init__("water", style)

    def _get_audio_energy(self) -> str:
        return "medium-low"

    def _get_audio_tempo(self) -> int:
        return 100  # Moderate, flowing

    def _get_voice_speed(self) -> float:
        return 0.95  # Slightly slower

    def _get_voice_pitch(self) -> float:
        return 1.0  # Normal

    def _get_audio_effects(self) -> list:
        return ["chorus", "gentle_reverb"]

    def _validate_content_theme(self, script: VideoScript) -> bool:
        """Ensure content promotes emotional wellness"""
        wellness_keywords = ["emotion", "feeling", "wellness", "heal", "self-care", "balance"]
        topic_lower = script.topic.lower()
        return any(keyword in topic_lower for keyword in wellness_keywords)

    def _get_transition_effects(self) -> list:
        return ["ripple", "wave", "flow"]

    def _get_overlay_effects(self) -> list:
        return ["water_reflection", "soft_ripples"]


class EarthChannelStrategy(BaseChannelStrategy):
    """
    Earth Channel Strategy - Practical grounding and implementation

    Focuses on structured design, solid transitions,
    and practical, actionable content.
    """

    def __init__(self):
        style = ChannelStyle(
            primary_color="#8B7355",  # Tan
            secondary_color="#228B22",  # Forest green
            accent_color="#D2691E",  # Chocolate
            font_family="Roboto",
            font_weight="500",  # Medium
            animation_style="grounded_slide",
            transition_speed="medium",
            particle_effect="leaves",
            background_style="texture_natural",
            music_genre="acoustic",
            voice_tone="confident"
        )
        super().__init__("earth", style)

    def _get_audio_energy(self) -> str:
        return "medium"

    def _get_audio_tempo(self) -> int:
        return 110  # Moderate, steady

    def _get_voice_speed(self) -> float:
        return 1.0  # Normal

    def _get_voice_pitch(self) -> float:
        return 0.98  # Slightly lower, authoritative

    def _get_audio_effects(self) -> list:
        return ["warm_compression", "subtle_bass_boost"]

    def _validate_content_theme(self, script: VideoScript) -> bool:
        """Ensure content is practical and actionable"""
        practical_keywords = ["how", "step", "guide", "practical", "implement", "action"]
        topic_lower = script.topic.lower()
        return any(keyword in topic_lower for keyword in practical_keywords)

    def _get_transition_effects(self) -> list:
        return ["slide", "push", "cube"]

    def _get_overlay_effects(self) -> list:
        return ["texture_overlay", "natural_elements"]


class FireChannelStrategy(BaseChannelStrategy):
    """
    Fire Channel Strategy - Motivation and transformation

    Focuses on energetic design, dynamic transitions,
    and content promoting action and transformation.
    """

    def __init__(self):
        style = ChannelStyle(
            primary_color="#FF4500",  # Orange red
            secondary_color="#FFD700",  # Gold
            accent_color="#DC143C",  # Crimson
            font_family="Montserrat",
            font_weight="700",  # Bold
            animation_style="dynamic_burst",
            transition_speed="fast",
            particle_effect="sparks",
            background_style="gradient_fire",
            music_genre="electronic",
            voice_tone="energetic"
        )
        super().__init__("fire", style)

    def _get_audio_energy(self) -> str:
        return "high"

    def _get_audio_tempo(self) -> int:
        return 140  # Fast, energetic

    def _get_voice_speed(self) -> float:
        return 1.1  # Slightly faster

    def _get_voice_pitch(self) -> float:
        return 1.05  # Slightly higher, enthusiastic

    def _get_audio_effects(self) -> list:
        return ["punch", "excitement_boost", "dynamic_compression"]

    def _validate_content_theme(self, script: VideoScript) -> bool:
        """Ensure content promotes action and transformation"""
        action_keywords = ["transform", "change", "action", "power", "achieve", "success"]
        topic_lower = script.topic.lower()
        return any(keyword in topic_lower for keyword in action_keywords)

    def _get_transition_effects(self) -> list:
        return ["burst", "zoom", "spin", "flash"]

    def _get_overlay_effects(self) -> list:
        return ["glow_intense", "energy_particles", "fire_border"]