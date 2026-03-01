"""
Channel Strategy Factory

Factory for creating and managing channel-specific strategies.
"""

import logging
from typing import Dict, Optional

from domain.video_generation import (
    IChannelStrategy,
    IChannelStrategyFactory,
)
from .channel_strategies import (
    AirChannelStrategy,
    WaterChannelStrategy,
    EarthChannelStrategy,
    FireChannelStrategy,
)

logger = logging.getLogger(__name__)


class ChannelStrategyFactory(IChannelStrategyFactory):
    """
    Factory for creating channel-specific strategies.

    Manages the creation and caching of channel strategies.
    """

    def __init__(self):
        """Initialize the channel strategy factory."""
        self._strategies: Dict[str, IChannelStrategy] = {}
        self._custom_strategies: Dict[str, IChannelStrategy] = {}

        # Initialize default strategies
        self._initialize_default_strategies()

    def get_strategy(self, channel: str) -> IChannelStrategy:
        """
        Get strategy for a specific channel.

        Args:
            channel: Channel name (air, water, earth, fire, or custom)

        Returns:
            Channel-specific strategy

        Raises:
            ValueError: If channel is not recognized
        """
        channel_lower = channel.lower()

        # Check custom strategies first
        if channel_lower in self._custom_strategies:
            return self._custom_strategies[channel_lower]

        # Check default strategies
        if channel_lower in self._strategies:
            return self._strategies[channel_lower]

        # Channel not found
        available = list(self._strategies.keys()) + list(self._custom_strategies.keys())
        raise ValueError(
            f"Unknown channel: {channel}. Available channels: {available}"
        )

    def register_strategy(self, channel: str, strategy: IChannelStrategy) -> None:
        """
        Register a custom channel strategy.

        Args:
            channel: Channel name
            strategy: Strategy implementation
        """
        channel_lower = channel.lower()

        if channel_lower in self._strategies:
            logger.warning(
                f"Overriding default strategy for channel: {channel}. "
                "Use custom channel names to avoid conflicts."
            )

        self._custom_strategies[channel_lower] = strategy
        logger.info(f"Registered custom strategy for channel: {channel}")

    def _initialize_default_strategies(self) -> None:
        """Initialize default channel strategies."""
        self._strategies = {
            "air": AirChannelStrategy(),
            "water": WaterChannelStrategy(),
            "earth": EarthChannelStrategy(),
            "fire": FireChannelStrategy(),
        }

        logger.info(
            f"Initialized {len(self._strategies)} default channel strategies: "
            f"{list(self._strategies.keys())}"
        )

    def list_channels(self) -> list[str]:
        """
        List all available channels.

        Returns:
            List of channel names
        """
        default_channels = list(self._strategies.keys())
        custom_channels = list(self._custom_strategies.keys())
        return default_channels + custom_channels

    def get_channel_info(self, channel: str) -> Dict:
        """
        Get information about a channel.

        Args:
            channel: Channel name

        Returns:
            Channel information dictionary
        """
        strategy = self.get_strategy(channel)

        return {
            "name": strategy.channel_name,
            "visual_style": strategy.get_visual_style(),
            "audio_style": strategy.get_audio_style(),
            "is_custom": channel.lower() in self._custom_strategies,
        }

    def reset_custom_strategies(self) -> None:
        """Clear all custom strategies."""
        self._custom_strategies.clear()
        logger.info("Cleared all custom channel strategies")