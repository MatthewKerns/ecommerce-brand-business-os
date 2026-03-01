"""
Base Video Provider

Abstract base class for all video generation providers.
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime
import asyncio
import uuid

from domain.video_generation import (
    IVideoProvider,
    VideoGenerationRequest,
    VideoResult,
    VideoStatus,
    ProviderInfo,
    ProviderCapability,
    VideoQuality,
)

logger = logging.getLogger(__name__)


class BaseVideoProvider(ABC, IVideoProvider):
    """
    Base class for video generation providers.

    Provides common functionality and enforces interface implementation.
    """

    def __init__(
        self,
        provider_id: str,
        name: str,
        capabilities: List[ProviderCapability],
        supported_qualities: List[VideoQuality],
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize base provider.

        Args:
            provider_id: Unique provider identifier
            name: Human-readable provider name
            capabilities: List of supported capabilities
            supported_qualities: List of supported quality levels
            config: Provider-specific configuration
        """
        self._config = config or {}
        self._info = ProviderInfo(
            id=provider_id,
            name=name,
            capabilities=capabilities,
            supported_qualities=supported_qualities,
            max_duration_seconds=self._config.get("max_duration_seconds", 60),
            cost_per_second=self._config.get("cost_per_second", 0.1),
            average_generation_time=self._config.get("average_generation_time", 30),
            is_available=True,
            metadata=self._config.get("metadata", {})
        )
        self._active_jobs: Dict[str, VideoResult] = {}

    @property
    def info(self) -> ProviderInfo:
        """Get provider information and capabilities."""
        return self._info

    async def generate_video(self, request: VideoGenerationRequest) -> VideoResult:
        """
        Generate a video based on the request.

        Args:
            request: Video generation request

        Returns:
            VideoResult with generation status
        """
        # Generate unique ID for this job
        job_id = str(uuid.uuid4())

        # Create initial result
        result = VideoResult(
            id=job_id,
            status=VideoStatus.PENDING,
            provider_id=self.info.id,
            metadata={"request": request.__dict__}
        )

        # Store in active jobs
        self._active_jobs[job_id] = result

        try:
            # Pre-generation hook
            await self._pre_generation(request, result)

            # Update status to processing
            result.status = VideoStatus.PROCESSING
            logger.info(f"Starting video generation: {job_id}")

            # Perform actual generation (implemented by subclass)
            await self._generate_video_impl(request, result)

            # Post-generation hook
            await self._post_generation(request, result)

            # Mark as completed if not already set
            if result.status == VideoStatus.PROCESSING:
                result.status = VideoStatus.COMPLETED

            result.completed_at = datetime.utcnow()
            logger.info(f"Video generation completed: {job_id}")

        except Exception as e:
            logger.exception(f"Video generation failed: {job_id}")
            result.status = VideoStatus.FAILED
            result.error_message = str(e)
            result.completed_at = datetime.utcnow()

        return result

    async def get_status(self, video_id: str) -> VideoResult:
        """
        Get the status of a video generation job.

        Args:
            video_id: ID of the video job

        Returns:
            Current status and information
        """
        if video_id in self._active_jobs:
            return self._active_jobs[video_id]

        # Try to get from persistent storage (implemented by subclass)
        result = await self._get_status_impl(video_id)

        if result:
            return result

        # Not found
        return VideoResult(
            id=video_id,
            status=VideoStatus.FAILED,
            provider_id=self.info.id,
            error_message="Video job not found"
        )

    def validate_request(self, request: VideoGenerationRequest) -> tuple[bool, Optional[str]]:
        """
        Validate if this provider can handle the request.

        Args:
            request: Video generation request

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check quality support
        if request.quality not in self.info.supported_qualities:
            return False, f"Quality {request.quality.value} not supported"

        # Check duration
        duration = request.script.duration_seconds
        if duration > self.info.max_duration_seconds:
            return False, f"Duration {duration}s exceeds maximum {self.info.max_duration_seconds}s"

        # Check required features
        if request.script.required_features:
            missing = set(request.script.required_features) - set(self.info.capabilities)
            if missing:
                return False, f"Missing capabilities: {[c.value for c in missing]}"

        # Provider-specific validation
        return self._validate_request_impl(request)

    async def cancel_generation(self, video_id: str) -> bool:
        """
        Cancel an in-progress video generation.

        Args:
            video_id: ID of the video to cancel

        Returns:
            True if cancelled successfully
        """
        if video_id not in self._active_jobs:
            logger.warning(f"Video {video_id} not found for cancellation")
            return False

        result = self._active_jobs[video_id]

        if result.status not in [VideoStatus.PENDING, VideoStatus.PROCESSING]:
            logger.warning(f"Video {video_id} cannot be cancelled (status: {result.status})")
            return False

        # Perform cancellation (implemented by subclass)
        success = await self._cancel_generation_impl(video_id)

        if success:
            result.status = VideoStatus.CANCELLED
            result.error_message = "Cancelled by user"
            result.completed_at = datetime.utcnow()

        return success

    # Abstract methods to be implemented by subclasses
    @abstractmethod
    async def _generate_video_impl(self, request: VideoGenerationRequest, result: VideoResult) -> None:
        """
        Actual video generation implementation.

        Args:
            request: Video generation request
            result: Result object to update with generated video info
        """
        pass

    @abstractmethod
    async def _get_status_impl(self, video_id: str) -> Optional[VideoResult]:
        """
        Get status from persistent storage.

        Args:
            video_id: Video job ID

        Returns:
            VideoResult or None if not found
        """
        pass

    @abstractmethod
    def _validate_request_impl(self, request: VideoGenerationRequest) -> tuple[bool, Optional[str]]:
        """
        Provider-specific request validation.

        Args:
            request: Video generation request

        Returns:
            Tuple of (is_valid, error_message)
        """
        pass

    @abstractmethod
    async def _cancel_generation_impl(self, video_id: str) -> bool:
        """
        Provider-specific cancellation logic.

        Args:
            video_id: Video job ID

        Returns:
            True if cancelled successfully
        """
        pass

    # Hook methods for subclasses to override
    async def _pre_generation(self, request: VideoGenerationRequest, result: VideoResult) -> None:
        """
        Hook called before video generation starts.

        Args:
            request: Video generation request
            result: Result object
        """
        pass

    async def _post_generation(self, request: VideoGenerationRequest, result: VideoResult) -> None:
        """
        Hook called after video generation completes.

        Args:
            request: Video generation request
            result: Result object
        """
        pass

    # Utility methods for subclasses
    def _generate_video_url(self, job_id: str, extension: str = "mp4") -> str:
        """
        Generate a URL for the video file.

        Args:
            job_id: Video job ID
            extension: File extension

        Returns:
            Generated video URL
        """
        # In production, this would generate a CDN or storage URL
        return f"/videos/{self.info.id}/{job_id}.{extension}"

    def _generate_thumbnail_url(self, job_id: str, extension: str = "jpg") -> str:
        """
        Generate a URL for the thumbnail.

        Args:
            job_id: Video job ID
            extension: File extension

        Returns:
            Generated thumbnail URL
        """
        return f"/thumbnails/{self.info.id}/{job_id}.{extension}"

    async def _simulate_processing_delay(self, seconds: float) -> None:
        """
        Simulate processing delay for testing.

        Args:
            seconds: Number of seconds to delay
        """
        await asyncio.sleep(seconds)