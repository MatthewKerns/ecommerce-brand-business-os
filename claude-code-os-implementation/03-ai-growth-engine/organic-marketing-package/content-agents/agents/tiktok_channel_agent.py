"""
TikTok 4-Channel Content Strategy Agent
Manages content generation for the 4 elemental TikTok channels (Air, Water, Fire, Earth)
Each channel has distinct themes, audiences, and content strategies
"""
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import hashlib

from .base_agent import BaseAgent
from config.config import (
    TIKTOK_CHANNELS_OUTPUT_DIR,
    TIKTOK_CHANNELS,
    CHANNEL_THEMES,
    CONTENT_PILLARS
)
from database.connection import get_db_session
from database.models import ChannelContent, ContentHistory, TikTokChannel


class TikTokChannelAgent(BaseAgent):
    """Agent specialized in multi-channel TikTok content strategy"""

    def __init__(self):
        """
        Initialize the TikTok Channel agent with 4-channel strategy

        The agent manages content for 4 elemental channels:
        - Air: Quick tips, fast moves, tournament prep
        - Water: Strategy, flow, adaptation
        - Fire: Hype, energy, passion
        - Earth: Building, collecting, organizing
        """
        super().__init__(agent_name="tiktok_channel_agent")

        self.logger.debug("Initializing 4-channel TikTok strategy")

        # Load channel configurations from config
        self.channels = TIKTOK_CHANNELS
        self.channel_themes = CHANNEL_THEMES

        # Validate that all 4 channels are configured
        required_elements = ["air", "water", "fire", "earth"]
        for element in required_elements:
            if element not in self.channels:
                self.logger.warning(f"Channel '{element}' not found in configuration")

        self.logger.info(f"Initialized TikTok Channel Agent with {len(self.channels)} channels")

    def get_channel_specs(self, channel_element: str) -> Dict[str, Any]:
        """
        Get specifications for a specific channel

        Args:
            channel_element: Channel element (air, water, fire, earth)

        Returns:
            Dictionary containing channel specifications

        Raises:
            ValueError: If channel_element is not valid

        Example:
            >>> agent = TikTokChannelAgent()
            >>> specs = agent.get_channel_specs('air')
            >>> print(specs['tone'])
            'Fast-paced, energetic, action-oriented'
        """
        if channel_element not in self.channels:
            valid_channels = ", ".join(self.channels.keys())
            raise ValueError(
                f"Invalid channel element: '{channel_element}'. "
                f"Valid channels: {valid_channels}"
            )

        channel_config = self.channels[channel_element]
        theme_config = self.channel_themes[channel_element]

        return {
            "element": channel_element,
            "channel_name": channel_config["channel_name"],
            "description": channel_config["description"],
            "target_audience": channel_config["target_audience"],
            "content_focus": channel_config["content_focus"],
            "posting_schedule": channel_config["posting_schedule"],
            "tone": theme_config["tone"],
            "content_types": theme_config["content_types"],
            "key_messages": theme_config["key_messages"],
            "content_pillars": theme_config["content_pillars"],
            "video_length": theme_config["video_length"],
            "hook_style": theme_config["hook_style"],
            "hashtags": channel_config["branding_guidelines"]["hashtags"],
            "visual_style": channel_config["branding_guidelines"]["visual_style"]
        }

    def validate_content_for_channel(
        self,
        content: str,
        channel_element: str
    ) -> Dict[str, Any]:
        """
        Validate if content aligns with channel theme and specifications

        Args:
            content: Content text to validate
            channel_element: Target channel element

        Returns:
            Dictionary with validation results:
            - is_valid: bool
            - alignment_score: float (0-1)
            - feedback: str
            - suggestions: List[str]

        Example:
            >>> agent = TikTokChannelAgent()
            >>> result = agent.validate_content_for_channel(
            ...     "Quick deck building tip!",
            ...     "air"
            ... )
            >>> print(result['is_valid'])
            True
        """
        self.logger.info(f"Validating content for {channel_element} channel")

        specs = self.get_channel_specs(channel_element)

        prompt = f"""Validate this TikTok content for the {channel_element.upper()} channel:

CONTENT TO VALIDATE:
{content}

CHANNEL SPECIFICATIONS:
- Element Theme: {specs['element']}
- Target Audience: {specs['target_audience']}
- Content Focus: {specs['content_focus']}
- Tone: {specs['tone']}
- Key Messages: {', '.join(specs['key_messages'])}
- Hook Style: {specs['hook_style']}

VALIDATION CRITERIA:
1. Does the tone match the channel's required tone?
2. Is the content relevant to the target audience?
3. Does it align with the content focus areas?
4. Does the hook style match channel expectations?
5. Are key messages reflected in the content?
6. Is the content length appropriate for video length {specs['video_length']}?

Provide validation in this format:
ALIGNMENT_SCORE: [0.0-1.0]
IS_VALID: [YES/NO]
FEEDBACK: [Brief assessment]
SUGGESTIONS:
- [Suggestion 1]
- [Suggestion 2]
- [etc.]

Validate now:"""

        system_context = f"""
You are a TikTok content strategist for the {channel_element.upper()} channel.

Channel Identity:
- {specs['description']}
- Tone: {specs['tone']}
- Visual Style: {specs['visual_style']}

Your role is to ensure content perfectly aligns with this channel's unique identity and audience expectations."""

        validation_response = self.generate_content(
            prompt=prompt,
            system_context=system_context,
            max_tokens=1000,
            temperature=0.3  # Lower temperature for more consistent validation
        )

        # Parse validation response
        lines = validation_response.strip().split('\n')
        alignment_score = 0.0
        is_valid = False
        feedback = ""
        suggestions = []

        for line in lines:
            if line.startswith("ALIGNMENT_SCORE:"):
                try:
                    alignment_score = float(line.split(":")[1].strip())
                except ValueError:
                    alignment_score = 0.5
            elif line.startswith("IS_VALID:"):
                is_valid = "YES" in line.upper()
            elif line.startswith("FEEDBACK:"):
                feedback = line.split(":", 1)[1].strip()
            elif line.startswith("- "):
                suggestions.append(line[2:].strip())

        return {
            "is_valid": is_valid,
            "alignment_score": alignment_score,
            "feedback": feedback,
            "suggestions": suggestions,
            "channel_element": channel_element,
            "full_response": validation_response
        }

    def generate_channel_video_script(
        self,
        channel_element: str,
        topic: str,
        product: Optional[str] = None,
        include_product_link: bool = False
    ) -> tuple[str, Path]:
        """
        Generate TikTok video script tailored to specific channel element

        Args:
            channel_element: Channel element (air, water, fire, earth)
            topic: Video topic/theme
            product: Optional product to feature
            include_product_link: Whether to include product CTA

        Returns:
            Tuple of (script_content, file_path)

        Example:
            >>> agent = TikTokChannelAgent()
            >>> script, path = agent.generate_channel_video_script(
            ...     channel_element='air',
            ...     topic='Quick deck building for tournaments',
            ...     product='Tournament Deck Box'
            ... )
        """
        self.logger.info(
            f"Generating video script: element={channel_element}, "
            f"topic='{topic}', product={product}"
        )

        specs = self.get_channel_specs(channel_element)

        product_section = ""
        if product:
            product_section = f"""
PRODUCT TO FEATURE: {product}
{"INCLUDE PRODUCT LINK: Yes - add Shop Now CTA" if include_product_link else "INCLUDE PRODUCT LINK: No - natural mention only"}
"""

        prompt = f"""Create a TikTok video script for the {specs['channel_name']} channel:

TOPIC: {topic}
CHANNEL ELEMENT: {channel_element.upper()}
TARGET AUDIENCE: {specs['target_audience']}
VIDEO LENGTH: {specs['video_length']}
{product_section}

CHANNEL SPECIFICATIONS:
- Tone: {specs['tone']}
- Hook Style: {specs['hook_style']}
- Content Focus: {specs['content_focus']}
- Key Messages: {', '.join(specs['key_messages'])}
- Visual Style: {specs['visual_style']}

REQUIREMENTS:
1. Hook must match {specs['hook_style']}
2. Stay within {specs['video_length']} video length
3. Match {specs['tone']} tone throughout
4. Align with content focus: {specs['content_focus']}
5. Include visual direction and camera notes
6. Add text overlay suggestions
7. Suggest background music style
8. End with clear call-to-action
9. Connect to "Battle Ready" brand identity
10. Include recommended hashtags from: {', '.join(specs['hashtags'])}

Format:
[HOOK (0-3s)]
Visual: [Camera direction, what viewer sees]
Audio: [Exact script to say]
Text Overlay: [On-screen text]

[MAIN CONTENT]
Visual: [Camera direction, what viewer sees]
Audio: [Exact script to say]
Text Overlay: [On-screen text]

[CALL-TO-ACTION (Last 3-5s)]
Visual: [Camera direction, what viewer sees]
Audio: [Exact script to say]
Text Overlay: [On-screen text]

[PRODUCTION NOTES]
Music Style: [Recommended music type]
Pace: [Video pacing notes]
Transitions: [Transition suggestions]

[CAPTION & HASHTAGS]
[Complete caption with hashtags]

Write the complete video script now:"""

        system_context = f"""
You are creating content for the {specs['channel_name']} TikTok channel.

CHANNEL IDENTITY:
{specs['description']}

This channel is one of 4 elemental channels in Infinity Vault's TikTok strategy:
- AIR: Quick, fast, tournament-focused
- WATER: Strategic, analytical, adaptive
- FIRE: Hyped, passionate, celebratory
- EARTH: Grounded, methodical, building-focused

The {channel_element.upper()} channel specifically serves: {specs['target_audience']}

Content must be distinct from the other 3 channels while maintaining the overall
"Show Up Battle Ready" brand identity.

Best Practices for {channel_element.upper()}:
- Tone: {specs['tone']}
- Visual Style: {specs['visual_style']}
- Hook Style: {specs['hook_style']}
- Key Messages: {', '.join(specs['key_messages'])}

Create content that makes the target audience feel understood and empowered."""

        content, path = self.generate_and_save(
            prompt=prompt,
            output_dir=TIKTOK_CHANNELS_OUTPUT_DIR / channel_element,
            system_context=system_context,
            metadata={
                "platform": "tiktok",
                "channel_element": channel_element,
                "channel_name": specs['channel_name'],
                "topic": topic,
                "product": product,
                "target_audience": specs['target_audience'],
                "video_length": specs['video_length']
            }
        )

        self.logger.info(
            f"Successfully generated {channel_element} channel video script: {path}"
        )
        return content, path

    def generate_channel_content_calendar(
        self,
        channel_element: str,
        num_days: int = 7,
        include_topics: bool = True
    ) -> tuple[str, Path]:
        """
        Generate content calendar for a specific channel

        Args:
            channel_element: Channel element (air, water, fire, earth)
            num_days: Number of days to plan (default 7)
            include_topics: Whether to include specific topic suggestions

        Returns:
            Tuple of (calendar_content, file_path)

        Example:
            >>> agent = TikTokChannelAgent()
            >>> calendar, path = agent.generate_channel_content_calendar(
            ...     channel_element='water',
            ...     num_days=14
            ... )
        """
        self.logger.info(
            f"Generating {num_days}-day content calendar for {channel_element} channel"
        )

        specs = self.get_channel_specs(channel_element)
        posting_schedule = specs['posting_schedule']

        prompt = f"""Create a {num_days}-day TikTok content calendar for the {specs['channel_name']} channel:

CHANNEL SPECIFICATIONS:
- Element: {channel_element.upper()}
- Target Audience: {specs['target_audience']}
- Content Focus: {specs['content_focus']}
- Posting Frequency: {posting_schedule['frequency']}
- Best Posting Times: {', '.join(posting_schedule['best_times'])}
- Posting Days: {', '.join(posting_schedule['days'])}

CONTENT TYPES FOR THIS CHANNEL:
{', '.join(specs['content_types'])}

REQUIREMENTS:
1. Follow the posting schedule (frequency and days)
2. Use best posting times from the schedule
3. Ensure all content aligns with {channel_element} theme
4. Mix different content types throughout the calendar
5. Each day should have a clear content theme
6. {"Include specific topic suggestions with brief descriptions" if include_topics else "Include content type only"}
7. Add recommended hashtag groups for each post
8. Note which content pillars each post serves
9. Ensure variety while maintaining channel identity
10. Include product feature opportunities where natural

Format for each day:
DATE: [Day, Date]
TIME: [Best time from schedule]
CONTENT TYPE: [Type from channel's content types]
{"TOPIC: [Specific topic/title]" if include_topics else ""}
{"DESCRIPTION: [2-3 sentence content description]" if include_topics else ""}
CONTENT PILLAR: [Which pillar(s) this serves]
HASHTAGS: [Recommended hashtag group]
PRODUCT OPPORTUNITY: [Yes/No - if yes, which product]

Create the {num_days}-day calendar now:"""

        system_context = f"""
You are planning content for the {specs['channel_name']} TikTok channel.

CHANNEL MISSION:
{specs['description']}

This channel serves {specs['target_audience']} with content focused on:
{specs['content_focus']}

The calendar must respect the posting schedule while maximizing engagement and
maintaining the unique {channel_element.upper()} identity.

Key Messages to Reinforce:
{chr(10).join(f"- {msg}" for msg in specs['key_messages'])}

Content Pillars Available:
{chr(10).join(f"- {pillar}" for pillar in CONTENT_PILLARS)}

Focus on this channel's pillars: {', '.join(specs['content_pillars'])}"""

        content, path = self.generate_and_save(
            prompt=prompt,
            output_dir=TIKTOK_CHANNELS_OUTPUT_DIR / channel_element / "calendars",
            system_context=system_context,
            metadata={
                "platform": "tiktok",
                "channel_element": channel_element,
                "channel_name": specs['channel_name'],
                "num_days": num_days,
                "posting_frequency": posting_schedule['frequency'],
                "content_types": specs['content_types']
            }
        )

        self.logger.info(
            f"Successfully generated {num_days}-day calendar for {channel_element}: {path}"
        )
        return content, path

    def generate_multi_channel_strategy(
        self,
        time_period: str = "weekly"
    ) -> tuple[str, Path]:
        """
        Generate coordinated content strategy across all 4 channels

        Args:
            time_period: Time period for strategy (weekly, monthly)

        Returns:
            Tuple of (strategy_content, file_path)

        Example:
            >>> agent = TikTokChannelAgent()
            >>> strategy, path = agent.generate_multi_channel_strategy('weekly')
        """
        self.logger.info(f"Generating {time_period} multi-channel strategy")

        # Get specs for all channels
        all_specs = {
            element: self.get_channel_specs(element)
            for element in ["air", "water", "fire", "earth"]
        }

        channels_overview = "\n\n".join([
            f"{element.upper()} - {specs['channel_name']}:\n"
            f"  Audience: {specs['target_audience']}\n"
            f"  Focus: {specs['content_focus']}\n"
            f"  Frequency: {specs['posting_schedule']['frequency']}\n"
            f"  Tone: {specs['tone']}"
            for element, specs in all_specs.items()
        ])

        prompt = f"""Create a coordinated {time_period} content strategy across all 4 TikTok channels:

CHANNEL OVERVIEW:
{channels_overview}

STRATEGIC GOALS:
1. Maximize reach across different audience segments
2. Ensure content diversity while maintaining brand consistency
3. Prevent content duplication across channels
4. Create opportunities for cross-channel engagement
5. Align with "Show Up Battle Ready" brand identity
6. Focus on 'saves' as primary success metric

REQUIREMENTS:
1. Coordinate posting schedules to avoid same-day conflicts
2. Identify unique content angles for each channel
3. Suggest cross-promotion opportunities
4. Plan product features across different channels
5. Ensure each channel maintains distinct identity
6. Include weekly themes that work across all channels
7. Suggest A/B testing opportunities
8. Plan for trending topics adaptation by channel

Format:
OVERVIEW:
[Strategic summary of the {time_period} plan]

CHANNEL BREAKDOWN:

AIR CHANNEL:
[Content themes, posting plan, unique angles]

WATER CHANNEL:
[Content themes, posting plan, unique angles]

FIRE CHANNEL:
[Content themes, posting plan, unique angles]

EARTH CHANNEL:
[Content themes, posting plan, unique angles]

CROSS-CHANNEL OPPORTUNITIES:
[How channels can work together]

CONTENT COLLISION PREVENTION:
[Rules to avoid duplication]

PRODUCT FEATURE SCHEDULE:
[Which products featured on which channels when]

METRICS & TESTING:
[What to track and test this {time_period}]

Create the complete multi-channel strategy now:"""

        system_context = """
You are the master strategist for Infinity Vault's 4-channel TikTok presence.

BRAND IDENTITY: Show Up Battle Ready
MISSION: Help TCG players feel confident, prepared, and respected

The 4-channel strategy is designed to:
1. Reach different audience segments (competitive, strategic, passionate, methodical)
2. Test different content approaches simultaneously
3. Maximize overall reach while maintaining brand consistency
4. Create a comprehensive brand presence on TikTok

Each channel must feel distinct yet cohesive with the overall brand.
The strategy should leverage the strengths of each elemental theme while
creating synergies across the full channel ecosystem.

PRIMARY SUCCESS METRIC: Save rate (saves/views)
- Saves indicate purchase intent and valuable content
- Focus on creating "save-worthy" content for each channel"""

        content, path = self.generate_and_save(
            prompt=prompt,
            output_dir=TIKTOK_CHANNELS_OUTPUT_DIR / "strategy",
            system_context=system_context,
            metadata={
                "platform": "tiktok",
                "strategy_type": "multi_channel",
                "time_period": time_period,
                "num_channels": 4
            }
        )

        self.logger.info(f"Successfully generated multi-channel {time_period} strategy: {path}")
        return content, path

    def list_channels(self) -> List[Dict[str, Any]]:
        """
        List all available TikTok channels with comprehensive information

        Returns:
            List of dictionaries containing channel information including:
            - element: Channel element identifier
            - channel_name: Display name of the channel
            - description: Channel description
            - target_audience: Target audience description
            - content_focus: Main content focus areas
            - posting_frequency: How often to post
            - tone: Channel tone/voice
            - content_types: List of content types for the channel

        Example:
            >>> agent = TikTokChannelAgent()
            >>> channels = agent.list_channels()
            >>> print(f"Found {len(channels)} channels")
            Found 4 channels
            >>> for channel in channels:
            ...     print(f"{channel['element']}: {channel['channel_name']}")
            air: Infinity Vault - Air
            water: Infinity Vault - Water
            fire: Infinity Vault - Fire
            earth: Infinity Vault - Earth
        """
        self.logger.debug("Listing all TikTok channels")

        channels = []
        required_elements = ["air", "water", "fire", "earth"]

        for element in required_elements:
            if element not in self.channels:
                self.logger.warning(f"Channel '{element}' not found in configuration")
                continue

            channel_config = self.channels[element]
            theme_config = self.channel_themes.get(element, {})

            channels.append({
                "element": element,
                "channel_name": channel_config["channel_name"],
                "description": channel_config["description"],
                "target_audience": channel_config["target_audience"],
                "content_focus": channel_config["content_focus"],
                "posting_frequency": channel_config["posting_schedule"]["frequency"],
                "posting_days": channel_config["posting_schedule"]["days"],
                "best_times": channel_config["posting_schedule"]["best_times"],
                "tone": theme_config.get("tone", ""),
                "content_types": theme_config.get("content_types", []),
                "visual_style": channel_config["branding_guidelines"]["visual_style"],
                "hashtags": channel_config["branding_guidelines"]["hashtags"]
            })

        self.logger.info(f"Found {len(channels)} TikTok channels")
        return channels

    def get_channel(self, channel_element: str) -> Dict[str, Any]:
        """
        Get detailed information for a specific channel

        Args:
            channel_element: Channel element identifier (air, water, fire, earth)

        Returns:
            Dictionary containing comprehensive channel information

        Raises:
            ValueError: If channel_element is not valid

        Example:
            >>> agent = TikTokChannelAgent()
            >>> channel = agent.get_channel('air')
            >>> print(channel['channel_name'])
            Infinity Vault - Air
        """
        if channel_element not in self.channels:
            valid_channels = ", ".join(self.channels.keys())
            error_msg = (
                f"Invalid channel element: '{channel_element}'. "
                f"Valid channels: {valid_channels}"
            )
            self.logger.error(error_msg)
            raise ValueError(error_msg)

        self.logger.debug(f"Getting channel information for '{channel_element}'")

        channel_config = self.channels[channel_element]
        theme_config = self.channel_themes.get(channel_element, {})

        return {
            "element": channel_element,
            "channel_name": channel_config["channel_name"],
            "description": channel_config["description"],
            "target_audience": channel_config["target_audience"],
            "content_focus": channel_config["content_focus"],
            "posting_schedule": channel_config["posting_schedule"],
            "tone": theme_config.get("tone", ""),
            "content_types": theme_config.get("content_types", []),
            "key_messages": theme_config.get("key_messages", []),
            "content_pillars": theme_config.get("content_pillars", []),
            "video_length": theme_config.get("video_length", ""),
            "hook_style": theme_config.get("hook_style", ""),
            "branding_guidelines": channel_config["branding_guidelines"],
            "hashtags": channel_config["branding_guidelines"]["hashtags"],
            "visual_style": channel_config["branding_guidelines"]["visual_style"]
        }

    def create_channel(
        self,
        element: str,
        channel_name: str,
        description: str,
        target_audience: str,
        content_focus: str,
        posting_schedule: Dict[str, Any],
        branding_guidelines: Dict[str, Any],
        theme_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a new TikTok channel configuration

        Args:
            element: Channel element identifier (must be unique)
            channel_name: Display name for the channel
            description: Channel description
            target_audience: Target audience description
            content_focus: Main content focus areas
            posting_schedule: Dictionary with frequency, days, and best_times
            branding_guidelines: Dictionary with visual_style and hashtags
            theme_config: Optional theme configuration with tone, content_types, etc.

        Returns:
            Dictionary containing the created channel configuration

        Raises:
            ValueError: If element already exists or required fields are invalid

        Example:
            >>> agent = TikTokChannelAgent()
            >>> channel = agent.create_channel(
            ...     element='metal',
            ...     channel_name='Infinity Vault - Metal',
            ...     description='Premium collecting and rare cards',
            ...     target_audience='High-value collectors',
            ...     content_focus='Rare cards, premium products',
            ...     posting_schedule={
            ...         'frequency': '3x per week',
            ...         'days': ['monday', 'wednesday', 'friday'],
            ...         'best_times': ['6:00 PM']
            ...     },
            ...     branding_guidelines={
            ...         'visual_style': 'Premium, elegant',
            ...         'hashtags': ['#PremiumTCG', '#RareCards']
            ...     }
            ... )
        """
        self.logger.info(f"Creating new channel: '{element}'")

        # Validate element doesn't already exist
        if element in self.channels:
            error_msg = f"Channel '{element}' already exists. Use update_channel() to modify."
            self.logger.error(error_msg)
            raise ValueError(error_msg)

        # Validate required fields
        if not element or not isinstance(element, str):
            raise ValueError("Element must be a non-empty string")

        if not channel_name or not isinstance(channel_name, str):
            raise ValueError("Channel name must be a non-empty string")

        if not isinstance(posting_schedule, dict):
            raise ValueError("Posting schedule must be a dictionary")

        required_schedule_keys = ["frequency", "days", "best_times"]
        for key in required_schedule_keys:
            if key not in posting_schedule:
                raise ValueError(f"Posting schedule must include '{key}'")

        if not isinstance(branding_guidelines, dict):
            raise ValueError("Branding guidelines must be a dictionary")

        required_branding_keys = ["visual_style", "hashtags"]
        for key in required_branding_keys:
            if key not in branding_guidelines:
                raise ValueError(f"Branding guidelines must include '{key}'")

        # Create channel configuration
        channel_config = {
            "channel_name": channel_name,
            "element_theme": element,
            "description": description,
            "target_audience": target_audience,
            "content_focus": content_focus,
            "posting_schedule": posting_schedule,
            "branding_guidelines": branding_guidelines
        }

        # Add to channels dictionary
        self.channels[element] = channel_config

        # Add theme configuration if provided
        if theme_config:
            self.channel_themes[element] = theme_config

        self.logger.info(f"Successfully created channel '{element}'")

        return {
            "element": element,
            "status": "created",
            "channel_config": channel_config,
            "theme_config": theme_config
        }

    def update_channel(
        self,
        element: str,
        **updates: Any
    ) -> Dict[str, Any]:
        """
        Update an existing TikTok channel configuration

        Args:
            element: Channel element identifier to update
            **updates: Keyword arguments for fields to update. Supported fields:
                - channel_name: str
                - description: str
                - target_audience: str
                - content_focus: str
                - posting_schedule: Dict[str, Any]
                - branding_guidelines: Dict[str, Any]
                - tone: str (updates theme_config)
                - content_types: List[str] (updates theme_config)
                - key_messages: List[str] (updates theme_config)
                - video_length: str (updates theme_config)
                - hook_style: str (updates theme_config)

        Returns:
            Dictionary containing updated channel information

        Raises:
            ValueError: If element doesn't exist or update fields are invalid

        Example:
            >>> agent = TikTokChannelAgent()
            >>> result = agent.update_channel(
            ...     'air',
            ...     posting_schedule={
            ...         'frequency': 'daily',
            ...         'days': ['monday', 'wednesday', 'friday'],
            ...         'best_times': ['8:00 AM', '5:00 PM']
            ...     },
            ...     description='Updated: Quick tips and tournament prep'
            ... )
            >>> print(result['status'])
            updated
        """
        self.logger.info(f"Updating channel: '{element}'")

        # Validate element exists
        if element not in self.channels:
            error_msg = f"Channel '{element}' does not exist. Use create_channel() to create it."
            self.logger.error(error_msg)
            raise ValueError(error_msg)

        if not updates:
            self.logger.warning(f"No updates provided for channel '{element}'")
            return {
                "element": element,
                "status": "no_changes",
                "message": "No updates provided"
            }

        # Define which fields belong to channel config vs theme config
        channel_fields = {
            "channel_name", "description", "target_audience",
            "content_focus", "posting_schedule", "branding_guidelines"
        }
        theme_fields = {
            "tone", "content_types", "key_messages", "content_pillars",
            "video_length", "hook_style"
        }

        updated_fields = []

        # Update channel configuration
        for field, value in updates.items():
            if field in channel_fields:
                self.channels[element][field] = value
                updated_fields.append(field)
                self.logger.debug(f"Updated channel field '{field}' for '{element}'")

            elif field in theme_fields:
                if element not in self.channel_themes:
                    self.channel_themes[element] = {}
                self.channel_themes[element][field] = value
                updated_fields.append(field)
                self.logger.debug(f"Updated theme field '{field}' for '{element}'")

            else:
                self.logger.warning(
                    f"Unknown field '{field}' provided for channel update. Ignoring."
                )

        self.logger.info(
            f"Successfully updated channel '{element}'. "
            f"Updated fields: {', '.join(updated_fields)}"
        )

        return {
            "element": element,
            "status": "updated",
            "updated_fields": updated_fields,
            "channel_info": self.get_channel(element)
        }

    def list_available_channels(self) -> List[Dict[str, str]]:
        """
        List all available channels with basic information

        DEPRECATED: Use list_channels() instead for more comprehensive information.

        Returns:
            List of dictionaries containing basic channel information

        Example:
            >>> agent = TikTokChannelAgent()
            >>> channels = agent.list_available_channels()
            >>> for channel in channels:
            ...     print(f"{channel['element']}: {channel['name']}")
        """
        self.logger.warning(
            "list_available_channels() is deprecated. Use list_channels() instead."
        )

        channels = []
        for element in ["air", "water", "fire", "earth"]:
            if element in self.channels:
                config = self.channels[element]
                channels.append({
                    "element": element,
                    "name": config["channel_name"],
                    "description": config["description"],
                    "audience": config["target_audience"],
                    "frequency": config["posting_schedule"]["frequency"]
                })

        return channels

    def check_content_uniqueness(
        self,
        content_text: str,
        channel_element: str,
        similarity_threshold: float = 0.8
    ) -> bool:
        """
        Check if content is unique across all channels (cross-posting prevention)

        This method prevents content duplication penalties by checking if similar
        content has already been posted to other channels. Uses both exact hash
        matching and similarity scoring to detect duplicates.

        Args:
            content_text: Content text to check for uniqueness
            channel_element: Target channel element (air, water, fire, earth)
            similarity_threshold: Similarity threshold for duplicate detection (0-1).
                                 Default 0.8 means 80% similar = duplicate.

        Returns:
            bool: True if content is unique (safe to post), False if duplicate detected

        Raises:
            ValueError: If channel_element is invalid

        Example:
            >>> agent = TikTokChannelAgent()
            >>> is_unique = agent.check_content_uniqueness(
            ...     "Quick deck building tips for tournaments",
            ...     "air"
            ... )
            >>> if is_unique:
            ...     print("Safe to post - content is unique")
            >>> else:
            ...     print("Duplicate detected - revise content")
        """
        self.logger.info(
            f"Checking content uniqueness for {channel_element} channel "
            f"(threshold: {similarity_threshold})"
        )

        # Validate channel element
        if channel_element not in self.channels:
            valid_channels = ", ".join(self.channels.keys())
            raise ValueError(
                f"Invalid channel element: '{channel_element}'. "
                f"Valid channels: {valid_channels}"
            )

        # Normalize content for comparison
        normalized_content = self._normalize_content(content_text)

        # Generate hash for exact duplicate detection
        content_hash = self._generate_content_hash(normalized_content)

        # Get database session
        db = get_db_session()
        try:
            # Query all channel content from OTHER channels
            # First, get the channel_id for the target channel (if it exists in DB)
            target_channel_ids = []
            target_channel = db.query(TikTokChannel).filter(
                TikTokChannel.element_theme == channel_element
            ).first()

            if target_channel:
                target_channel_ids.append(target_channel.id)

            # Get all content from OTHER channels
            other_channel_content = db.query(
                ChannelContent, ContentHistory
            ).join(
                ContentHistory,
                ChannelContent.content_id == ContentHistory.id
            ).filter(
                ChannelContent.channel_id.notin_(target_channel_ids) if target_channel_ids else True
            ).all()

            if not other_channel_content:
                # No content in other channels, so this is unique
                self.logger.info("No existing content in other channels - content is unique")
                return True

            # Check for duplicates
            for channel_content, content_history in other_channel_content:
                existing_content = content_history.content
                if not existing_content:
                    continue

                # Normalize existing content
                normalized_existing = self._normalize_content(existing_content)

                # Check exact hash match
                existing_hash = self._generate_content_hash(normalized_existing)
                if content_hash == existing_hash:
                    self.logger.warning(
                        f"Exact duplicate detected in channel_id={channel_content.channel_id}"
                    )
                    return False

                # Check similarity
                similarity = self._calculate_similarity(
                    normalized_content,
                    normalized_existing
                )

                if similarity >= similarity_threshold:
                    self.logger.warning(
                        f"Similar content detected (similarity: {similarity:.2%}) "
                        f"in channel_id={channel_content.channel_id}"
                    )
                    return False

            # No duplicates found
            self.logger.info("Content is unique across all channels")
            return True

        except Exception as e:
            self.logger.error(f"Error checking content uniqueness: {e}", exc_info=True)
            # On error, default to allowing content (fail open)
            # This prevents blocking content generation if DB has issues
            self.logger.warning("Defaulting to unique=True due to error")
            return True
        finally:
            db.close()

    def _normalize_content(self, content: str) -> str:
        """
        Normalize content for comparison by removing extra whitespace and lowercasing

        Args:
            content: Content to normalize

        Returns:
            Normalized content string
        """
        # Convert to lowercase
        normalized = content.lower()

        # Remove extra whitespace
        normalized = " ".join(normalized.split())

        return normalized.strip()

    def _generate_content_hash(self, content: str) -> str:
        """
        Generate SHA-256 hash of content for exact duplicate detection

        Args:
            content: Content to hash

        Returns:
            SHA-256 hash as hexadecimal string
        """
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    def _calculate_similarity(self, content1: str, content2: str) -> float:
        """
        Calculate similarity score between two content strings using Jaccard similarity

        This uses word-level Jaccard similarity (intersection over union of word sets).
        Simple but effective for detecting similar content.

        Args:
            content1: First content string
            content2: Second content string

        Returns:
            float: Similarity score between 0.0 (completely different) and 1.0 (identical)

        Example:
            >>> agent = TikTokChannelAgent()
            >>> similarity = agent._calculate_similarity(
            ...     "quick deck building tips",
            ...     "quick tips for deck building"
            ... )
            >>> print(f"Similarity: {similarity:.2%}")
            Similarity: 100.00%
        """
        # Split into word sets
        words1 = set(content1.split())
        words2 = set(content2.split())

        # Handle empty sets
        if not words1 and not words2:
            return 1.0  # Both empty = identical
        if not words1 or not words2:
            return 0.0  # One empty = completely different

        # Calculate Jaccard similarity: intersection / union
        intersection = words1.intersection(words2)
        union = words1.union(words2)

        similarity = len(intersection) / len(union)

        return similarity
