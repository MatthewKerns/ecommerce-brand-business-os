"""
Video Configuration Manager

Manages configuration for video generation system.
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path
from dataclasses import dataclass, asdict

from domain.video_generation import IConfigManager

logger = logging.getLogger(__name__)


@dataclass
class ProviderConfig:
    """Configuration for a video provider"""
    enabled: bool = False
    api_key: Optional[str] = None
    api_url: Optional[str] = None
    max_concurrent: int = 3
    timeout_seconds: int = 300
    retry_attempts: int = 3
    custom_settings: Dict[str, Any] = None

    def __post_init__(self):
        if self.custom_settings is None:
            self.custom_settings = {}


@dataclass
class ChannelConfig:
    """Configuration for a channel"""
    enabled: bool = True
    max_duration_seconds: int = 60
    default_quality: str = "standard"
    custom_settings: Dict[str, Any] = None

    def __post_init__(self):
        if self.custom_settings is None:
            self.custom_settings = {}


@dataclass
class GlobalConfig:
    """Global video generation configuration"""
    default_provider: str = "mock_provider"
    default_quality: str = "standard"
    max_concurrent_generations: int = 5
    enable_caching: bool = True
    cache_ttl_seconds: int = 3600
    storage_path: str = "/tmp/videos"
    thumbnail_path: str = "/tmp/thumbnails"


@dataclass
class VideoGenerationConfig:
    """Complete video generation configuration"""
    providers: Dict[str, ProviderConfig] = None
    channels: Dict[str, ChannelConfig] = None
    global_settings: GlobalConfig = None

    def __post_init__(self):
        if self.providers is None:
            self.providers = {}
        if self.channels is None:
            self.channels = {}
        if self.global_settings is None:
            self.global_settings = GlobalConfig()


class VideoConfigManager(IConfigManager):
    """
    Configuration manager for video generation system.

    Handles loading, saving, and managing configuration
    from multiple sources (files, environment, defaults).
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration manager.

        Args:
            config_path: Path to configuration file
        """
        self._config_path = config_path or self._get_default_config_path()
        self._config = VideoGenerationConfig()
        self._env_overrides: Dict[str, Any] = {}

        # Load configuration
        self._load_configuration()

    def get_provider_config(self, provider_id: str) -> Dict[str, Any]:
        """
        Get configuration for a specific provider.

        Args:
            provider_id: Provider identifier

        Returns:
            Provider configuration dictionary
        """
        if provider_id in self._config.providers:
            config = self._config.providers[provider_id]
            return asdict(config)

        # Return default config if not found
        return asdict(ProviderConfig())

    def update_provider_config(self, provider_id: str, config: Dict[str, Any]) -> None:
        """
        Update provider configuration.

        Args:
            provider_id: Provider identifier
            config: New configuration values
        """
        if provider_id not in self._config.providers:
            self._config.providers[provider_id] = ProviderConfig()

        provider_config = self._config.providers[provider_id]

        # Update fields
        for key, value in config.items():
            if hasattr(provider_config, key):
                setattr(provider_config, key, value)
            else:
                provider_config.custom_settings[key] = value

        # Save configuration
        self._save_configuration()
        logger.info(f"Updated configuration for provider: {provider_id}")

    def get_channel_config(self, channel: str) -> Dict[str, Any]:
        """
        Get configuration for a specific channel.

        Args:
            channel: Channel name

        Returns:
            Channel configuration dictionary
        """
        if channel in self._config.channels:
            config = self._config.channels[channel]
            return asdict(config)

        # Return default config if not found
        return asdict(ChannelConfig())

    def get_global_config(self) -> Dict[str, Any]:
        """
        Get global video generation configuration.

        Returns:
            Global configuration dictionary
        """
        return asdict(self._config.global_settings)

    def reload_config(self) -> None:
        """Reload configuration from source."""
        self._load_configuration()
        logger.info("Configuration reloaded")

    def _load_configuration(self) -> None:
        """Load configuration from file and environment."""
        # Load from file
        self._load_from_file()

        # Load from environment
        self._load_from_environment()

        # Apply defaults
        self._apply_defaults()

        logger.info(f"Loaded configuration with {len(self._config.providers)} providers")

    def _load_from_file(self) -> None:
        """Load configuration from file."""
        config_path = Path(self._config_path)

        if not config_path.exists():
            logger.warning(f"Configuration file not found: {config_path}")
            return

        try:
            with open(config_path, 'r') as f:
                data = json.load(f)

            # Load providers
            if "providers" in data:
                for provider_id, provider_data in data["providers"].items():
                    self._config.providers[provider_id] = ProviderConfig(**provider_data)

            # Load channels
            if "channels" in data:
                for channel, channel_data in data["channels"].items():
                    self._config.channels[channel] = ChannelConfig(**channel_data)

            # Load global settings
            if "global" in data:
                self._config.global_settings = GlobalConfig(**data["global"])

            logger.info(f"Loaded configuration from: {config_path}")

        except Exception as e:
            logger.exception(f"Failed to load configuration file: {e}")

    def _load_from_environment(self) -> None:
        """Load configuration overrides from environment variables."""
        # Provider API keys
        for provider_id in ["remotion", "runway", "synthesia", "ffmpeg"]:
            env_key = f"VIDEO_PROVIDER_{provider_id.upper()}_API_KEY"
            if env_key in os.environ:
                if provider_id not in self._config.providers:
                    self._config.providers[provider_id] = ProviderConfig()
                self._config.providers[provider_id].api_key = os.environ[env_key]
                logger.info(f"Loaded API key for {provider_id} from environment")

        # Global settings
        if "VIDEO_DEFAULT_PROVIDER" in os.environ:
            self._config.global_settings.default_provider = os.environ["VIDEO_DEFAULT_PROVIDER"]

        if "VIDEO_STORAGE_PATH" in os.environ:
            self._config.global_settings.storage_path = os.environ["VIDEO_STORAGE_PATH"]

        if "VIDEO_MAX_CONCURRENT" in os.environ:
            self._config.global_settings.max_concurrent_generations = int(
                os.environ["VIDEO_MAX_CONCURRENT"]
            )

    def _apply_defaults(self) -> None:
        """Apply default configuration values."""
        # Ensure mock provider is always available
        if "mock_provider" not in self._config.providers:
            self._config.providers["mock_provider"] = ProviderConfig(
                enabled=True,
                max_concurrent=10,
                timeout_seconds=60,
            )

        # Ensure all channels have config
        for channel in ["air", "water", "earth", "fire"]:
            if channel not in self._config.channels:
                self._config.channels[channel] = ChannelConfig()

        # Create storage directories if they don't exist
        for path in [
            self._config.global_settings.storage_path,
            self._config.global_settings.thumbnail_path
        ]:
            Path(path).mkdir(parents=True, exist_ok=True)

    def _save_configuration(self) -> None:
        """Save configuration to file."""
        config_path = Path(self._config_path)
        config_path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "providers": {
                pid: asdict(pconf) for pid, pconf in self._config.providers.items()
            },
            "channels": {
                cid: asdict(cconf) for cid, cconf in self._config.channels.items()
            },
            "global": asdict(self._config.global_settings),
        }

        try:
            with open(config_path, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info(f"Saved configuration to: {config_path}")
        except Exception as e:
            logger.exception(f"Failed to save configuration: {e}")

    def _get_default_config_path(self) -> str:
        """Get default configuration file path."""
        # Try multiple locations
        paths = [
            os.environ.get("VIDEO_CONFIG_PATH"),
            "./config/video_generation.json",
            "../config/video_generation.json",
            "~/.config/video_generation/config.json",
        ]

        for path in paths:
            if path:
                expanded = os.path.expanduser(path)
                if os.path.exists(expanded):
                    return expanded

        # Return default path
        return os.path.expanduser("~/.config/video_generation/config.json")

    def get_full_config(self) -> VideoGenerationConfig:
        """
        Get the complete configuration object.

        Returns:
            VideoGenerationConfig object
        """
        return self._config

    def export_config(self, path: str) -> None:
        """
        Export configuration to a file.

        Args:
            path: Path to export configuration to
        """
        data = {
            "providers": {
                pid: asdict(pconf) for pid, pconf in self._config.providers.items()
            },
            "channels": {
                cid: asdict(cconf) for cid, cconf in self._config.channels.items()
            },
            "global": asdict(self._config.global_settings),
        }

        with open(path, 'w') as f:
            json.dump(data, f, indent=2)

        logger.info(f"Exported configuration to: {path}")

    def import_config(self, path: str) -> None:
        """
        Import configuration from a file.

        Args:
            path: Path to import configuration from
        """
        with open(path, 'r') as f:
            data = json.load(f)

        # Clear existing config
        self._config = VideoGenerationConfig()

        # Load imported data
        if "providers" in data:
            for provider_id, provider_data in data["providers"].items():
                self._config.providers[provider_id] = ProviderConfig(**provider_data)

        if "channels" in data:
            for channel, channel_data in data["channels"].items():
                self._config.channels[channel] = ChannelConfig(**channel_data)

        if "global" in data:
            self._config.global_settings = GlobalConfig(**data["global"])

        # Save to default location
        self._save_configuration()

        logger.info(f"Imported configuration from: {path}")