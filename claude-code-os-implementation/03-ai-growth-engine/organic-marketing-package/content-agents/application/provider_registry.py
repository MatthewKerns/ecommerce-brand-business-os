"""
Provider Registry

Manages video provider registration and intelligent selection
based on requirements and capabilities.
"""

import logging
from typing import Dict, List, Optional
from dataclasses import dataclass

from domain.video_generation import (
    IVideoProvider,
    IProviderRegistry,
    ProviderInfo,
    VideoQuality,
    ProviderCapability,
)

logger = logging.getLogger(__name__)


@dataclass
class ProviderScore:
    """Score for provider selection"""
    provider_id: str
    capability_score: float
    quality_score: float
    performance_score: float
    cost_score: float
    total_score: float


class ProviderRegistry(IProviderRegistry):
    """
    Registry for managing and selecting video providers.

    Implements intelligent provider selection based on:
    - Required capabilities
    - Quality requirements
    - Performance metrics
    - Cost optimization
    """

    def __init__(self):
        """Initialize the provider registry."""
        self._providers: Dict[str, IVideoProvider] = {}
        self._provider_metrics: Dict[str, Dict] = {}

    def register_provider(self, provider: IVideoProvider) -> None:
        """
        Register a video provider.

        Args:
            provider: Video provider to register
        """
        provider_id = provider.info.id

        if provider_id in self._providers:
            logger.warning(f"Provider {provider_id} already registered, replacing")

        self._providers[provider_id] = provider
        self._provider_metrics[provider_id] = {
            "successful_generations": 0,
            "failed_generations": 0,
            "average_generation_time": provider.info.average_generation_time,
            "last_error": None,
            "last_success": None,
        }

        logger.info(
            f"Registered provider: {provider_id} with capabilities: "
            f"{[c.value for c in provider.info.capabilities]}"
        )

    def unregister_provider(self, provider_id: str) -> None:
        """
        Unregister a video provider.

        Args:
            provider_id: ID of provider to unregister
        """
        if provider_id in self._providers:
            del self._providers[provider_id]
            del self._provider_metrics[provider_id]
            logger.info(f"Unregistered provider: {provider_id}")
        else:
            logger.warning(f"Provider {provider_id} not found for unregistration")

    def get_provider(self, provider_id: str) -> Optional[IVideoProvider]:
        """
        Get a specific provider by ID.

        Args:
            provider_id: ID of provider to get

        Returns:
            Provider instance or None if not found
        """
        return self._providers.get(provider_id)

    def list_providers(self) -> List[ProviderInfo]:
        """
        List all available providers.

        Returns:
            List of provider information
        """
        return [provider.info for provider in self._providers.values()]

    def select_provider(
        self,
        quality: VideoQuality,
        required_features: List[ProviderCapability],
        channel: Optional[str] = None,
        prefer_provider: Optional[str] = None
    ) -> Optional[IVideoProvider]:
        """
        Select the best provider based on requirements.

        Selection algorithm:
        1. Filter providers by required capabilities
        2. Filter by quality support
        3. Score remaining providers
        4. Return highest scoring provider

        Args:
            quality: Required video quality
            required_features: List of required capabilities
            channel: Optional channel for channel-specific selection
            prefer_provider: Optional preferred provider ID

        Returns:
            Best matching provider or None if no match
        """
        # If preferred provider is specified and available, check if it meets requirements
        if prefer_provider and prefer_provider in self._providers:
            provider = self._providers[prefer_provider]
            if self._provider_meets_requirements(provider, quality, required_features):
                logger.info(f"Using preferred provider: {prefer_provider}")
                return provider

        # Filter eligible providers
        eligible_providers = []
        for provider_id, provider in self._providers.items():
            if not provider.info.is_available:
                continue

            if self._provider_meets_requirements(provider, quality, required_features):
                eligible_providers.append(provider)

        if not eligible_providers:
            logger.warning(
                f"No providers found for quality={quality.value}, "
                f"features={[f.value for f in required_features]}"
            )
            return None

        # Score providers
        scores = []
        for provider in eligible_providers:
            score = self._score_provider(provider, quality, required_features, channel)
            scores.append((score, provider))

        # Sort by score (highest first)
        scores.sort(key=lambda x: x[0].total_score, reverse=True)

        selected_provider = scores[0][1]
        logger.info(
            f"Selected provider: {selected_provider.info.id} "
            f"(score: {scores[0][0].total_score:.2f})"
        )

        return selected_provider

    def _provider_meets_requirements(
        self,
        provider: IVideoProvider,
        quality: VideoQuality,
        required_features: List[ProviderCapability]
    ) -> bool:
        """
        Check if provider meets requirements.

        Args:
            provider: Provider to check
            quality: Required quality
            required_features: Required capabilities

        Returns:
            True if provider meets all requirements
        """
        # Check quality support
        if quality not in provider.info.supported_qualities:
            return False

        # Check capability support
        provider_capabilities = set(provider.info.capabilities)
        required_capabilities = set(required_features)

        if not required_capabilities.issubset(provider_capabilities):
            missing = required_capabilities - provider_capabilities
            logger.debug(
                f"Provider {provider.info.id} missing capabilities: "
                f"{[c.value for c in missing]}"
            )
            return False

        return True

    def _score_provider(
        self,
        provider: IVideoProvider,
        quality: VideoQuality,
        required_features: List[ProviderCapability],
        channel: Optional[str] = None
    ) -> ProviderScore:
        """
        Score a provider for selection.

        Scoring factors:
        - Capability coverage (how many extra capabilities)
        - Quality support (supports higher qualities)
        - Performance (generation time, success rate)
        - Cost efficiency

        Args:
            provider: Provider to score
            quality: Required quality
            required_features: Required capabilities
            channel: Optional channel for scoring

        Returns:
            Provider score
        """
        provider_id = provider.info.id
        metrics = self._provider_metrics[provider_id]

        # Capability score (0-1): Extra capabilities beyond required
        total_capabilities = len(provider.info.capabilities)
        required_count = len(required_features)
        extra_capabilities = total_capabilities - required_count
        capability_score = min(1.0, 0.5 + (extra_capabilities * 0.1))

        # Quality score (0-1): Support for higher qualities
        quality_index = list(VideoQuality).index(quality)
        max_quality_index = max(
            list(VideoQuality).index(q) for q in provider.info.supported_qualities
        )
        quality_score = 0.5 + (0.5 * (max_quality_index - quality_index) / len(VideoQuality))

        # Performance score (0-1): Based on success rate and speed
        total_generations = (
            metrics["successful_generations"] + metrics["failed_generations"]
        )

        if total_generations > 0:
            success_rate = metrics["successful_generations"] / total_generations
        else:
            success_rate = 0.8  # Default for new providers

        # Speed component (faster is better)
        avg_time = metrics["average_generation_time"]
        if avg_time < 30:
            speed_score = 1.0
        elif avg_time < 60:
            speed_score = 0.8
        elif avg_time < 120:
            speed_score = 0.6
        else:
            speed_score = 0.4

        performance_score = (success_rate * 0.7) + (speed_score * 0.3)

        # Cost score (0-1): Lower cost is better
        cost = provider.info.cost_per_second
        if cost <= 0.1:
            cost_score = 1.0
        elif cost <= 0.5:
            cost_score = 0.8
        elif cost <= 1.0:
            cost_score = 0.6
        else:
            cost_score = 0.4

        # Channel-specific adjustments
        channel_bonus = 0.0
        if channel and provider.info.metadata:
            if f"optimized_for_{channel}" in provider.info.metadata:
                channel_bonus = 0.2

        # Calculate total score with weights
        total_score = (
            capability_score * 0.25 +
            quality_score * 0.20 +
            performance_score * 0.35 +
            cost_score * 0.20 +
            channel_bonus
        )

        return ProviderScore(
            provider_id=provider_id,
            capability_score=capability_score,
            quality_score=quality_score,
            performance_score=performance_score,
            cost_score=cost_score,
            total_score=total_score
        )

    def update_provider_metrics(
        self,
        provider_id: str,
        success: bool,
        generation_time: Optional[float] = None,
        error: Optional[str] = None
    ) -> None:
        """
        Update provider performance metrics.

        Args:
            provider_id: ID of provider
            success: Whether generation was successful
            generation_time: Time taken for generation
            error: Error message if failed
        """
        if provider_id not in self._provider_metrics:
            logger.warning(f"Provider {provider_id} not found for metrics update")
            return

        metrics = self._provider_metrics[provider_id]

        if success:
            metrics["successful_generations"] += 1
            metrics["last_success"] = generation_time

            # Update average generation time
            if generation_time:
                current_avg = metrics["average_generation_time"]
                total = metrics["successful_generations"]
                metrics["average_generation_time"] = (
                    (current_avg * (total - 1) + generation_time) / total
                )
        else:
            metrics["failed_generations"] += 1
            metrics["last_error"] = error

        logger.debug(
            f"Updated metrics for {provider_id}: "
            f"success={metrics['successful_generations']}, "
            f"fail={metrics['failed_generations']}"
        )