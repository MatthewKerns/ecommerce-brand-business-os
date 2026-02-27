"""
Dependency Injection Setup

Sets up and configures the DI container for the video generation system.
"""

import logging
from typing import Optional

from .container import DIContainer, DIModule
from application import VideoGenerationService, ProviderRegistry
from infrastructure.video_providers import MockVideoProvider
from infrastructure.strategies import ChannelStrategyFactory
from infrastructure.parsers import TikTokScriptParser
from infrastructure.config import VideoConfigManager

logger = logging.getLogger(__name__)


class VideoGenerationModule(DIModule):
    """DI module for video generation services."""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize module.

        Args:
            config_path: Optional path to configuration file
        """
        self.config_path = config_path

    def configure(self, container: DIContainer) -> None:
        """
        Configure video generation services.

        Args:
            container: DI container to configure
        """
        # Register configuration manager
        container.register(
            "config_manager",
            factory=lambda: VideoConfigManager(self.config_path),
            singleton=True
        )

        # Register script parser
        container.register(
            "script_parser",
            service=TikTokScriptParser(),
            singleton=True
        )

        # Register channel strategy factory
        container.register(
            "channel_strategy_factory",
            service=ChannelStrategyFactory(),
            singleton=True
        )

        # Register provider registry
        container.register(
            "provider_registry",
            service=ProviderRegistry(),
            singleton=True
        )

        # Register mock provider
        container.register(
            "mock_provider",
            factory=lambda: self._create_mock_provider(container),
            singleton=True
        )

        # Register main video generation service
        container.register(
            "video_generation_service",
            factory=lambda: self._create_video_service(container),
            singleton=True
        )

        logger.info("Configured VideoGenerationModule")

    def _create_mock_provider(self, container: DIContainer) -> MockVideoProvider:
        """Create and configure mock provider."""
        config_manager = container.resolve("config_manager")
        provider_config = config_manager.get_provider_config("mock_provider")

        return MockVideoProvider(config=provider_config)

    def _create_video_service(self, container: DIContainer) -> VideoGenerationService:
        """Create and configure video generation service."""
        provider_registry = container.resolve("provider_registry")
        script_parser = container.resolve("script_parser")
        channel_strategy_factory = container.resolve("channel_strategy_factory")
        config_manager = container.resolve("config_manager")

        # Register providers with the registry
        self._register_providers(container, provider_registry)

        # Create service
        return VideoGenerationService(
            provider_registry=provider_registry,
            script_parser=script_parser,
            channel_strategy_factory=channel_strategy_factory,
            config_manager=config_manager
        )

    def _register_providers(self, container: DIContainer, registry: ProviderRegistry) -> None:
        """Register all available providers with the registry."""
        # Get all providers from container
        for provider_id, provider in container.get_all_providers():
            registry.register_provider(provider)
            logger.info(f"Registered provider with registry: {provider_id}")


def setup_di_container(
    config_path: Optional[str] = None,
    additional_modules: Optional[list[DIModule]] = None
) -> DIContainer:
    """
    Set up and configure the DI container.

    Args:
        config_path: Optional configuration file path
        additional_modules: Optional additional modules to register

    Returns:
        Configured DI container
    """
    container = DIContainer()

    # Register core module
    video_module = VideoGenerationModule(config_path)
    container.register_module(video_module)

    # Register additional modules
    if additional_modules:
        for module in additional_modules:
            container.register_module(module)

    logger.info("DI container setup complete")
    return container


def create_video_generation_service(
    config_path: Optional[str] = None
) -> VideoGenerationService:
    """
    Create a configured video generation service.

    This is a convenience function for quickly getting a working service.

    Args:
        config_path: Optional configuration file path

    Returns:
        Configured VideoGenerationService
    """
    container = setup_di_container(config_path)
    return container.resolve("video_generation_service")