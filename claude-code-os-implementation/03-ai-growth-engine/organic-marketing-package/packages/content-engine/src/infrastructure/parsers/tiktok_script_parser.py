"""
TikTok Script Parser

Parser for converting raw TikTok scripts into structured VideoScript format.
"""

import re
import logging
from typing import Dict, Any, List, Optional

from domain.video_generation import (
    IScriptParser,
    VideoScript,
    ProviderCapability,
)

logger = logging.getLogger(__name__)


class TikTokScriptParser(IScriptParser):
    """
    Parser for TikTok video scripts.

    Converts raw script data from content generation
    into structured VideoScript format.
    """

    def __init__(self):
        """Initialize the TikTok script parser."""
        self._default_duration = 30  # Default 30 seconds for TikTok

    def parse(self, raw_script: Dict[str, Any]) -> VideoScript:
        """
        Parse a raw script into structured VideoScript format.

        Args:
            raw_script: Raw script data from content generation

        Returns:
            Structured VideoScript object
        """
        try:
            # Extract basic information
            channel = raw_script.get("channel", "air")
            topic = raw_script.get("topic", "")

            # Parse hook
            hook = self._extract_hook(raw_script)

            # Parse main points
            main_points = self._extract_main_points(raw_script)

            # Parse call to action
            call_to_action = self._extract_cta(raw_script)

            # Calculate duration
            duration = self._calculate_duration(raw_script, main_points)

            # Extract visual and audio styles
            visual_style = raw_script.get("visual_style", "modern")
            music_style = raw_script.get("music_style", "upbeat")

            # Extract transitions
            transitions = self._extract_transitions(raw_script)

            # Determine required features
            required_features = self._determine_required_features(raw_script)

            # Extract metadata
            metadata = self._extract_metadata(raw_script)

            # Create VideoScript
            script = VideoScript(
                channel=channel,
                topic=topic,
                hook=hook,
                main_points=main_points,
                call_to_action=call_to_action,
                duration_seconds=duration,
                visual_style=visual_style,
                music_style=music_style,
                transitions=transitions,
                required_features=required_features,
                metadata=metadata
            )

            logger.info(
                f"Parsed script for channel={channel}, topic={topic}, "
                f"duration={duration}s, {len(main_points)} main points"
            )

            return script

        except Exception as e:
            logger.exception(f"Failed to parse script: {e}")
            raise ValueError(f"Script parsing failed: {str(e)}")

    def validate_script(self, script: VideoScript) -> tuple[bool, Optional[str]]:
        """
        Validate a parsed script.

        Args:
            script: VideoScript to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check required fields
        if not script.topic:
            return False, "Script missing topic"

        if not script.hook:
            return False, "Script missing hook"

        if not script.main_points:
            return False, "Script has no main points"

        if not script.call_to_action:
            return False, "Script missing call to action"

        # Check duration
        if script.duration_seconds <= 0:
            return False, "Invalid duration"

        if script.duration_seconds > 180:  # TikTok max 3 minutes
            return False, "Duration exceeds TikTok maximum (180 seconds)"

        # Check content length
        if len(script.hook) > 500:
            return False, "Hook too long (max 500 characters)"

        if len(script.call_to_action) > 300:
            return False, "Call to action too long (max 300 characters)"

        # Validate main points
        for i, point in enumerate(script.main_points):
            if len(point) > 1000:
                return False, f"Main point {i+1} too long (max 1000 characters)"

        return True, None

    def extract_required_features(self, script: VideoScript) -> List[ProviderCapability]:
        """
        Extract required provider capabilities from script.

        Args:
            script: VideoScript to analyze

        Returns:
            List of required provider capabilities
        """
        required = []

        # Text to video is always required
        required.append(ProviderCapability.TEXT_TO_VIDEO)

        # Check for animation requirements
        if script.visual_style in ["animated", "cartoon", "motion"]:
            required.append(ProviderCapability.ANIMATION)

        # Check for transition requirements
        if script.transitions:
            required.append(ProviderCapability.TRANSITIONS)

        # Check for audio requirements
        if script.music_style:
            required.append(ProviderCapability.AUDIO_MIXING)

        # Check metadata for special requirements
        metadata = script.metadata or {}

        if metadata.get("requires_ai_generation"):
            required.append(ProviderCapability.AI_GENERATION)

        if metadata.get("requires_avatar"):
            required.append(ProviderCapability.AVATAR_GENERATION)

        if metadata.get("requires_style_transfer"):
            required.append(ProviderCapability.STYLE_TRANSFER)

        if metadata.get("requires_real_time"):
            required.append(ProviderCapability.REAL_TIME)

        return required

    def _extract_hook(self, raw_script: Dict[str, Any]) -> str:
        """Extract hook from raw script."""
        # Check multiple possible locations
        hook = raw_script.get("hook", "")

        if not hook and "content" in raw_script:
            content = raw_script["content"]
            if isinstance(content, dict):
                hook = content.get("hook", "")
            elif isinstance(content, str):
                # Extract first sentence as hook
                sentences = re.split(r'[.!?]', content)
                if sentences:
                    hook = sentences[0].strip()

        if not hook and "intro" in raw_script:
            hook = raw_script["intro"]

        return hook or "Check this out!"

    def _extract_main_points(self, raw_script: Dict[str, Any]) -> List[str]:
        """Extract main points from raw script."""
        main_points = []

        # Check for explicit main points
        if "main_points" in raw_script:
            points = raw_script["main_points"]
            if isinstance(points, list):
                main_points = [str(p) for p in points]
            elif isinstance(points, str):
                # Split by newlines or numbering
                main_points = self._split_into_points(points)

        # Check content field
        elif "content" in raw_script:
            content = raw_script["content"]
            if isinstance(content, dict) and "points" in content:
                main_points = content["points"]
            elif isinstance(content, dict) and "main_points" in content:
                main_points = content["main_points"]
            elif isinstance(content, str):
                main_points = self._split_into_points(content)

        # Check body field
        elif "body" in raw_script:
            body = raw_script["body"]
            if isinstance(body, list):
                main_points = [str(p) for p in body]
            elif isinstance(body, str):
                main_points = self._split_into_points(body)

        # Ensure at least one main point
        if not main_points:
            main_points = ["Key information to share"]

        # Limit to reasonable number of points
        if len(main_points) > 5:
            logger.warning(f"Too many main points ({len(main_points)}), limiting to 5")
            main_points = main_points[:5]

        return main_points

    def _extract_cta(self, raw_script: Dict[str, Any]) -> str:
        """Extract call to action from raw script."""
        # Check multiple possible locations
        cta = raw_script.get("call_to_action", "")

        if not cta:
            cta = raw_script.get("cta", "")

        if not cta and "content" in raw_script:
            content = raw_script["content"]
            if isinstance(content, dict):
                cta = content.get("call_to_action", "") or content.get("cta", "")

        if not cta:
            cta = raw_script.get("conclusion", "")

        if not cta:
            cta = raw_script.get("outro", "")

        return cta or "Follow for more!"

    def _calculate_duration(self, raw_script: Dict[str, Any], main_points: List[str]) -> int:
        """Calculate video duration based on content."""
        # Check for explicit duration
        if "duration" in raw_script:
            duration = raw_script["duration"]
            if isinstance(duration, (int, float)):
                return int(duration)
            elif isinstance(duration, str):
                # Parse duration string (e.g., "30s", "1m30s")
                return self._parse_duration_string(duration)

        # Estimate based on content
        # Hook: 3-5 seconds
        # Each main point: 5-10 seconds
        # CTA: 3-5 seconds
        estimated = 4 + (len(main_points) * 7) + 4

        # Cap at TikTok limits
        if estimated > 60:
            return 60  # Default to 1 minute for long content
        elif estimated < 15:
            return 15  # Minimum 15 seconds

        return estimated

    def _extract_transitions(self, raw_script: Dict[str, Any]) -> List[str]:
        """Extract transition styles from raw script."""
        transitions = raw_script.get("transitions", [])

        if not transitions and "visual_effects" in raw_script:
            effects = raw_script["visual_effects"]
            if isinstance(effects, dict) and "transitions" in effects:
                transitions = effects["transitions"]

        if isinstance(transitions, str):
            transitions = [transitions]

        return transitions or ["fade", "slide"]

    def _determine_required_features(self, raw_script: Dict[str, Any]) -> List[ProviderCapability]:
        """Determine required features from raw script."""
        required = [ProviderCapability.TEXT_TO_VIDEO]

        # Check for specific requirements in script
        if raw_script.get("requires_animation"):
            required.append(ProviderCapability.ANIMATION)

        if raw_script.get("requires_avatar"):
            required.append(ProviderCapability.AVATAR_GENERATION)

        if raw_script.get("requires_ai"):
            required.append(ProviderCapability.AI_GENERATION)

        if raw_script.get("has_music", True):
            required.append(ProviderCapability.AUDIO_MIXING)

        if raw_script.get("has_transitions", True):
            required.append(ProviderCapability.TRANSITIONS)

        return required

    def _extract_metadata(self, raw_script: Dict[str, Any]) -> Dict[str, Any]:
        """Extract metadata from raw script."""
        metadata = raw_script.get("metadata", {})

        # Add additional metadata
        metadata["source"] = "tiktok_script_parser"
        metadata["parser_version"] = "1.0.0"

        # Copy relevant fields
        for field in ["hashtags", "target_audience", "mood", "style", "language"]:
            if field in raw_script:
                metadata[field] = raw_script[field]

        return metadata

    def _split_into_points(self, text: str) -> List[str]:
        """Split text into numbered or bulleted points."""
        points = []

        # Try numbered points (1. 2. 3. or 1) 2) 3))
        numbered = re.findall(r'\d+[.)]\s*([^\n]+)', text)
        if numbered:
            return numbered

        # Try bullet points
        bulleted = re.findall(r'[•·-]\s*([^\n]+)', text)
        if bulleted:
            return bulleted

        # Try newline separation
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if line and len(line) > 10:  # Skip very short lines
                points.append(line)

        # If still no points, split by sentences
        if not points:
            sentences = re.split(r'[.!?]', text)
            points = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]

        return points[:5]  # Limit to 5 points

    def _parse_duration_string(self, duration_str: str) -> int:
        """Parse duration string like '30s' or '1m30s' into seconds."""
        try:
            # Remove spaces
            duration_str = duration_str.replace(" ", "")

            # Match patterns like 1m30s, 30s, 2m
            match = re.match(r'(?:(\d+)m)?(?:(\d+)s)?', duration_str)
            if match:
                minutes = int(match.group(1) or 0)
                seconds = int(match.group(2) or 0)
                return minutes * 60 + seconds

            # Try to parse as plain number (assume seconds)
            return int(duration_str)

        except:
            return self._default_duration