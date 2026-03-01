"""
Video Generation Service

Main orchestration service for video generation following
clean architecture principles.
"""

import asyncio
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

from domain.video_generation import (
    VideoGenerationRequest,
    VideoResult,
    VideoStatus,
    VideoQuality,
    ProviderCapability,
    VideoScript,
    IVideoProvider,
    IScriptParser,
    IChannelStrategy,
    IProviderRegistry,
    IChannelStrategyFactory,
    IConfigManager,
)

logger = logging.getLogger(__name__)


class VideoGenerationService:
    """
    Main service for orchestrating video generation.

    This service coordinates between different components:
    - Script parsing
    - Provider selection
    - Channel strategies
    - Video generation
    """

    def __init__(
        self,
        provider_registry: IProviderRegistry,
        script_parser: IScriptParser,
        channel_strategy_factory: IChannelStrategyFactory,
        config_manager: IConfigManager,
    ):
        """
        Initialize the video generation service.

        Args:
            provider_registry: Registry for managing video providers
            script_parser: Parser for converting raw scripts to structured format
            channel_strategy_factory: Factory for channel-specific strategies
            config_manager: Configuration management
        """
        self.provider_registry = provider_registry
        self.script_parser = script_parser
        self.channel_strategy_factory = channel_strategy_factory
        self.config_manager = config_manager
        self._active_generations: Dict[str, VideoResult] = {}

    async def generate_video(
        self,
        raw_script: Dict[str, Any],
        channel: str,
        quality: VideoQuality = VideoQuality.STANDARD,
        provider_hint: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> VideoResult:
        """
        Generate a video from a raw script.

        Args:
            raw_script: Raw script data from content generation
            channel: Target channel (air, water, earth, fire)
            quality: Video quality level
            provider_hint: Optional preferred provider ID
            options: Additional generation options

        Returns:
            VideoResult with generation status and details
        """
        try:
            # Step 1: Parse and validate script
            logger.info(f"Parsing script for channel: {channel}")
            parsed_script = self.script_parser.parse(raw_script)

            is_valid, error_msg = self.script_parser.validate_script(parsed_script)
            if not is_valid:
                logger.error(f"Script validation failed: {error_msg}")
                return VideoResult(
                    id="error",
                    status=VideoStatus.FAILED,
                    provider_id="none",
                    error_message=f"Script validation failed: {error_msg}"
                )

            # Step 2: Get channel strategy
            logger.info(f"Getting channel strategy for: {channel}")
            strategy = self.channel_strategy_factory.get_strategy(channel)

            # Validate content against channel guidelines
            is_valid, error_msg = strategy.validate_content(parsed_script)
            if not is_valid:
                logger.error(f"Channel validation failed: {error_msg}")
                return VideoResult(
                    id="error",
                    status=VideoStatus.FAILED,
                    provider_id="none",
                    error_message=f"Channel validation failed: {error_msg}"
                )

            # Step 3: Extract required features
            required_features = self.script_parser.extract_required_features(parsed_script)
            logger.info(f"Required features: {[f.value for f in required_features]}")

            # Step 4: Select provider based on requirements
            logger.info("Selecting optimal provider")
            provider = self.provider_registry.select_provider(
                quality=quality,
                required_features=required_features,
                channel=channel,
                prefer_provider=provider_hint
            )

            if not provider:
                logger.error("No suitable provider found")
                return VideoResult(
                    id="error",
                    status=VideoStatus.FAILED,
                    provider_id="none",
                    error_message="No suitable provider found for requirements"
                )

            logger.info(f"Selected provider: {provider.info.id}")

            # Step 5: Create generation request
            request = VideoGenerationRequest(
                script=parsed_script,
                channel=channel,
                quality=quality,
                provider_hint=provider.info.id,
                options=options or {}
            )

            # Step 6: Apply channel-specific enhancements
            enhanced_request = strategy.enhance_request(request)

            # Step 7: Validate request with provider
            is_valid, error_msg = provider.validate_request(enhanced_request)
            if not is_valid:
                logger.error(f"Provider validation failed: {error_msg}")
                return VideoResult(
                    id="error",
                    status=VideoStatus.FAILED,
                    provider_id=provider.info.id,
                    error_message=f"Provider validation failed: {error_msg}"
                )

            # Step 8: Generate video
            logger.info(f"Generating video with provider: {provider.info.id}")
            result = await provider.generate_video(enhanced_request)

            # Store active generation for status tracking
            self._active_generations[result.id] = result

            return result

        except Exception as e:
            logger.exception(f"Video generation failed: {e}")
            return VideoResult(
                id="error",
                status=VideoStatus.FAILED,
                provider_id="none",
                error_message=f"Generation failed: {str(e)}"
            )

    async def get_video_status(self, video_id: str, provider_id: Optional[str] = None) -> VideoResult:
        """
        Get the status of a video generation job.

        Args:
            video_id: ID of the video generation job
            provider_id: Optional provider ID if known

        Returns:
            Current status and information about the video
        """
        # Check active generations first
        if video_id in self._active_generations:
            result = self._active_generations[video_id]

            # If still processing, check with provider for updates
            if result.status == VideoStatus.PROCESSING:
                provider = self.provider_registry.get_provider(result.provider_id)
                if provider:
                    updated_result = await provider.get_status(video_id)
                    self._active_generations[video_id] = updated_result

                    # Clean up completed generations
                    if updated_result.status in [VideoStatus.COMPLETED, VideoStatus.FAILED]:
                        del self._active_generations[video_id]

                    return updated_result

            return result

        # If not in active generations, try to get from provider
        if provider_id:
            provider = self.provider_registry.get_provider(provider_id)
            if provider:
                return await provider.get_status(video_id)

        # Not found
        return VideoResult(
            id=video_id,
            status=VideoStatus.FAILED,
            provider_id=provider_id or "unknown",
            error_message="Video generation job not found"
        )

    async def cancel_video_generation(self, video_id: str) -> bool:
        """
        Cancel an in-progress video generation.

        Args:
            video_id: ID of the video to cancel

        Returns:
            True if cancelled successfully
        """
        if video_id not in self._active_generations:
            logger.warning(f"Video {video_id} not found in active generations")
            return False

        result = self._active_generations[video_id]
        provider = self.provider_registry.get_provider(result.provider_id)

        if not provider:
            logger.error(f"Provider {result.provider_id} not found")
            return False

        try:
            success = await provider.cancel_generation(video_id)

            if success:
                result.status = VideoStatus.CANCELLED
                result.error_message = "Generation cancelled by user"
                del self._active_generations[video_id]

            return success

        except Exception as e:
            logger.exception(f"Failed to cancel video {video_id}: {e}")
            return False

    async def batch_generate_videos(
        self,
        requests: List[tuple[Dict[str, Any], str, VideoQuality]],
        max_concurrent: int = 3
    ) -> List[VideoResult]:
        """
        Generate multiple videos in batch with concurrency control.

        Args:
            requests: List of (raw_script, channel, quality) tuples
            max_concurrent: Maximum concurrent generations

        Returns:
            List of VideoResult objects
        """
        semaphore = asyncio.Semaphore(max_concurrent)

        async def generate_with_limit(raw_script, channel, quality):
            async with semaphore:
                return await self.generate_video(raw_script, channel, quality)

        tasks = [
            generate_with_limit(raw_script, channel, quality)
            for raw_script, channel, quality in requests
        ]

        return await asyncio.gather(*tasks)

    def get_available_providers(self) -> List[Dict[str, Any]]:
        """
        Get information about all available providers.

        Returns:
            List of provider information dictionaries
        """
        providers = self.provider_registry.list_providers()
        return [
            {
                "id": p.id,
                "name": p.name,
                "capabilities": [cap.value for cap in p.capabilities],
                "supported_qualities": [q.value for q in p.supported_qualities],
                "max_duration_seconds": p.max_duration_seconds,
                "is_available": p.is_available,
                "metadata": p.metadata
            }
            for p in providers
        ]

    def get_provider_for_requirements(
        self,
        quality: VideoQuality,
        required_features: List[ProviderCapability],
        channel: Optional[str] = None
    ) -> Optional[str]:
        """
        Get the best provider ID for given requirements.

        Args:
            quality: Required video quality
            required_features: List of required capabilities
            channel: Optional channel for channel-specific selection

        Returns:
            Provider ID or None if no match
        """
        provider = self.provider_registry.select_provider(
            quality=quality,
            required_features=required_features,
            channel=channel
        )

        return provider.info.id if provider else None