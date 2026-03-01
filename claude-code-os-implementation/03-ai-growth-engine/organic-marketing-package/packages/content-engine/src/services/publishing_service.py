"""
Publishing Service for TikTok Content

This service handles the actual publishing of scheduled content to TikTok Shop,
including retry logic, error handling, and publish attempt logging.
"""
import json
import os
import time
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from config.config import (
    TIKTOK_SHOP_APP_KEY,
    TIKTOK_SHOP_APP_SECRET,
    TIKTOK_SHOP_ACCESS_TOKEN
)
from database.connection import get_db_session
from database.models import ScheduledContent, PublishLog
from integrations.tiktok_shop.client import TikTokShopClient
from integrations.tiktok_shop.exceptions import (
    TikTokShopAPIError,
    TikTokShopAuthError,
    TikTokShopRateLimitError,
    TikTokShopValidationError,
    TikTokShopServerError,
    TikTokShopNetworkError
)
from logging_config import get_logger
from exceptions import DatabaseError, ConfigurationError


class PublishingService:
    """
    Service for publishing scheduled content to TikTok Shop

    This service manages the entire publishing lifecycle including:
    - Publishing content to TikTok Shop via API
    - Retry logic with exponential backoff
    - Detailed logging of all publish attempts
    - Status updates for scheduled content

    Attributes:
        logger: Logger instance for service operations
        tiktok_client: TikTok Shop API client
        max_retries: Maximum number of retry attempts (default: 3)
        initial_backoff_seconds: Initial backoff time for retries (default: 1.0)
        max_backoff_seconds: Maximum backoff time for retries (default: 32.0)

    Example:
        >>> service = PublishingService()
        >>> service.publish_content(scheduled_content_id=123)
        >>> # Check if publish succeeded
        >>> service.retry_failed_content(scheduled_content_id=123)
    """

    # Retry configuration
    DEFAULT_MAX_RETRIES = 3
    INITIAL_BACKOFF_SECONDS = 1.0
    MAX_BACKOFF_SECONDS = 32.0

    def __init__(
        self,
        tiktok_client: Optional[TikTokShopClient] = None,
        max_retries: int = DEFAULT_MAX_RETRIES
    ):
        """
        Initialize the Publishing Service

        Args:
            tiktok_client: Optional TikTok Shop client (creates default if not provided)
            max_retries: Maximum number of retry attempts

        Raises:
            ConfigurationError: If TikTok Shop credentials are missing
        """
        self.logger = get_logger("publishing_service")
        self.max_retries = max_retries

        try:
            # Initialize TikTok Shop client
            if tiktok_client:
                self.tiktok_client = tiktok_client
            else:
                # Check if we should use mock client for testing
                use_mock = os.getenv('USE_MOCK_TIKTOK_CLIENT', '').lower() == 'true'

                if use_mock:
                    # Import mock client for testing
                    try:
                        from tests.mocks.mock_tiktok_client import MockTikTokShopClient
                        self.tiktok_client = MockTikTokShopClient()
                        self.logger.info("Using mock TikTok client for testing")
                    except ImportError:
                        self.logger.warning("Mock client requested but not available, using real client")
                        use_mock = False

                if not use_mock:
                    # Use real TikTok Shop client
                    if not TIKTOK_SHOP_APP_KEY or not TIKTOK_SHOP_APP_SECRET:
                        raise ConfigurationError(
                            "Missing TikTok Shop credentials",
                            "TIKTOK_SHOP_APP_KEY and TIKTOK_SHOP_APP_SECRET are required"
                        )

                    self.tiktok_client = TikTokShopClient(
                        app_key=TIKTOK_SHOP_APP_KEY,
                        app_secret=TIKTOK_SHOP_APP_SECRET,
                        access_token=TIKTOK_SHOP_ACCESS_TOKEN
                    )

            self.logger.info("Publishing service initialized successfully")

        except Exception as e:
            self.logger.error(f"Failed to initialize publishing service: {e}", exc_info=True)
            raise

    def publish_content(self, scheduled_content_id: int) -> bool:
        """
        Publish scheduled content to TikTok Shop

        This method:
        1. Loads the scheduled content from database
        2. Validates content status (must be 'pending')
        3. Calls appropriate publish method based on content type
        4. Logs the publish attempt
        5. Updates content status based on result

        Args:
            scheduled_content_id: ID of the scheduled content to publish

        Returns:
            True if publish succeeded, False otherwise

        Raises:
            DatabaseError: If database operations fail

        Example:
            >>> service = PublishingService()
            >>> success = service.publish_content(123)
            >>> if success:
            ...     print("Content published successfully")
        """
        db = get_db_session()
        try:
            # Load scheduled content
            scheduled_content = db.query(ScheduledContent).filter(
                ScheduledContent.id == scheduled_content_id
            ).first()

            if not scheduled_content:
                self.logger.error(f"Scheduled content not found: {scheduled_content_id}")
                raise DatabaseError(
                    "query",
                    f"Scheduled content with ID {scheduled_content_id} not found",
                    "scheduled_content"
                )

            # Check if content is in pending status
            if scheduled_content.status != "pending":
                self.logger.warning(
                    f"Scheduled content {scheduled_content_id} is not in pending status "
                    f"(current: {scheduled_content.status})"
                )
                return False

            self.logger.info(
                f"Starting publish for scheduled content {scheduled_content_id} "
                f"(type: {scheduled_content.content_type})"
            )

            # Attempt to publish
            attempt_number = scheduled_content.retry_count + 1
            success, result = self._attempt_publish(scheduled_content, attempt_number, db)

            # Update retry count
            scheduled_content.retry_count = attempt_number
            scheduled_content.updated_at = datetime.utcnow()

            if success:
                # Update status to published
                scheduled_content.status = "published"
                scheduled_content.published_at = datetime.utcnow()
                scheduled_content.tiktok_video_id = result.get("video_id") or result.get("post_id")
                scheduled_content.error_message = None

                self.logger.info(
                    f"Successfully published content {scheduled_content_id} "
                    f"(TikTok ID: {scheduled_content.tiktok_video_id})"
                )
            else:
                # Check if max retries exceeded
                if scheduled_content.retry_count >= scheduled_content.max_retries:
                    scheduled_content.status = "failed"
                    self.logger.error(
                        f"Content {scheduled_content_id} failed after "
                        f"{scheduled_content.retry_count} attempts"
                    )
                else:
                    self.logger.warning(
                        f"Content {scheduled_content_id} publish failed, "
                        f"will retry (attempt {attempt_number}/{scheduled_content.max_retries})"
                    )

            db.commit()
            return success

        except Exception as e:
            db.rollback()
            self.logger.error(
                f"Error publishing content {scheduled_content_id}: {e}",
                exc_info=True
            )
            raise DatabaseError("update", str(e), "scheduled_content")

        finally:
            db.close()

    def retry_failed_content(self, scheduled_content_id: int) -> bool:
        """
        Retry publishing failed or pending content

        This method resets the retry count and attempts to publish content
        that previously failed or is still pending. Useful for manual retry
        operations or retry logic in scheduler.

        Args:
            scheduled_content_id: ID of the scheduled content to retry

        Returns:
            True if retry succeeded, False otherwise

        Raises:
            DatabaseError: If database operations fail

        Example:
            >>> service = PublishingService()
            >>> success = service.retry_failed_content(123)
        """
        db = get_db_session()
        try:
            scheduled_content = db.query(ScheduledContent).filter(
                ScheduledContent.id == scheduled_content_id
            ).first()

            if not scheduled_content:
                self.logger.error(f"Scheduled content not found: {scheduled_content_id}")
                raise DatabaseError(
                    "query",
                    f"Scheduled content with ID {scheduled_content_id} not found",
                    "scheduled_content"
                )

            # Only retry if status is pending or failed
            if scheduled_content.status not in ["pending", "failed"]:
                self.logger.warning(
                    f"Cannot retry content {scheduled_content_id} with status "
                    f"{scheduled_content.status}"
                )
                return False

            # Check if retry limit exceeded
            if scheduled_content.retry_count >= scheduled_content.max_retries:
                self.logger.warning(
                    f"Content {scheduled_content_id} has exceeded max retries "
                    f"({scheduled_content.retry_count}/{scheduled_content.max_retries})"
                )
                return False

            self.logger.info(f"Retrying content {scheduled_content_id}")

            # Reset to pending if failed
            if scheduled_content.status == "failed":
                scheduled_content.status = "pending"
                db.commit()

            # Attempt publish
            return self.publish_content(scheduled_content_id)

        except Exception as e:
            db.rollback()
            self.logger.error(
                f"Error retrying content {scheduled_content_id}: {e}",
                exc_info=True
            )
            raise DatabaseError("update", str(e), "scheduled_content")

        finally:
            db.close()

    def _attempt_publish(
        self,
        scheduled_content: ScheduledContent,
        attempt_number: int,
        db: Session
    ) -> tuple[bool, Optional[Dict[str, Any]]]:
        """
        Attempt to publish content and log the attempt

        This is an internal method that handles the actual API call and logging.

        Args:
            scheduled_content: ScheduledContent database object
            attempt_number: Current attempt number (1-indexed)
            db: Database session

        Returns:
            Tuple of (success: bool, result: Optional[Dict])

        Raises:
            No exceptions raised - all errors are caught and logged
        """
        # Create publish log entry
        publish_log = PublishLog(
            scheduled_content_id=scheduled_content.id,
            attempt_number=attempt_number,
            status="pending",
            platform="tiktok",
            attempted_at=datetime.utcnow()
        )
        db.add(publish_log)
        db.commit()

        try:
            # Parse content data
            content_data = json.loads(scheduled_content.content_data)

            # Call appropriate publish method based on content type
            if scheduled_content.content_type == "video":
                result = self._publish_video(content_data)
            elif scheduled_content.content_type == "post":
                result = self._publish_post(content_data)
            else:
                raise ValueError(f"Unknown content type: {scheduled_content.content_type}")

            # Update publish log with success
            publish_log.status = "success"
            publish_log.completed_at = datetime.utcnow()
            publish_log.tiktok_video_id = result.get("video_id") or result.get("post_id")
            publish_log.api_response = json.dumps(result)

            db.commit()

            return True, result

        except TikTokShopAuthError as e:
            self.logger.error(f"Authentication error: {e}")
            publish_log.status = "failed"
            publish_log.error_type = "auth_error"
            publish_log.error_message = str(e)
            publish_log.completed_at = datetime.utcnow()
            scheduled_content.error_message = f"Authentication error: {str(e)}"
            db.commit()
            return False, None

        except TikTokShopValidationError as e:
            self.logger.error(f"Validation error: {e}")
            publish_log.status = "failed"
            publish_log.error_type = "validation_error"
            publish_log.error_message = str(e)
            publish_log.completed_at = datetime.utcnow()
            scheduled_content.error_message = f"Validation error: {str(e)}"
            db.commit()
            return False, None

        except TikTokShopRateLimitError as e:
            self.logger.warning(f"Rate limit error: {e}")
            publish_log.status = "failed"
            publish_log.error_type = "rate_limit_error"
            publish_log.error_message = str(e)
            publish_log.completed_at = datetime.utcnow()
            scheduled_content.error_message = f"Rate limit exceeded: {str(e)}"

            # Apply exponential backoff for rate limit errors
            if e.retry_after:
                backoff_time = e.retry_after
            else:
                backoff_time = self.INITIAL_BACKOFF_SECONDS * (2 ** (attempt_number - 1))
                backoff_time = min(backoff_time, self.MAX_BACKOFF_SECONDS)

            self.logger.info(f"Applying backoff: {backoff_time} seconds")
            db.commit()

            # Wait before next retry (if not max retries)
            if attempt_number < scheduled_content.max_retries:
                time.sleep(backoff_time)

            return False, None

        except (TikTokShopServerError, TikTokShopNetworkError) as e:
            self.logger.error(f"Server/Network error: {e}")
            publish_log.status = "failed"
            publish_log.error_type = "server_error" if isinstance(e, TikTokShopServerError) else "network_error"
            publish_log.error_message = str(e)
            publish_log.completed_at = datetime.utcnow()
            scheduled_content.error_message = f"Server/Network error: {str(e)}"

            # Apply exponential backoff for transient errors
            backoff_time = self.INITIAL_BACKOFF_SECONDS * (2 ** (attempt_number - 1))
            backoff_time = min(backoff_time, self.MAX_BACKOFF_SECONDS)

            self.logger.info(f"Applying backoff: {backoff_time} seconds")
            db.commit()

            # Wait before next retry (if not max retries)
            if attempt_number < scheduled_content.max_retries:
                time.sleep(backoff_time)

            return False, None

        except Exception as e:
            self.logger.error(f"Unexpected error: {e}", exc_info=True)
            publish_log.status = "failed"
            publish_log.error_type = "unexpected_error"
            publish_log.error_message = str(e)
            publish_log.completed_at = datetime.utcnow()
            scheduled_content.error_message = f"Unexpected error: {str(e)}"
            db.commit()
            return False, None

    def _publish_video(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Publish video content to TikTok Shop

        Args:
            content_data: Dictionary containing video data:
                - video_url: URL of the video to upload (required)
                - title: Video title (required)
                - description: Video description (optional)
                - product_ids: List of product IDs to tag (optional)
                - tags: List of hashtags (optional)

        Returns:
            Dictionary containing TikTok API response with video_id

        Raises:
            TikTokShopValidationError: If required fields are missing
            TikTokShopAPIError: If API request fails

        Example:
            >>> content_data = {
            ...     "video_url": "https://example.com/video.mp4",
            ...     "title": "New Product Showcase",
            ...     "description": "Check out our latest products!",
            ...     "product_ids": ["1234567890"]
            ... }
            >>> result = service._publish_video(content_data)
        """
        self.logger.debug(f"Publishing video with data: {content_data}")

        # Validate required fields
        if "video_url" not in content_data or "title" not in content_data:
            raise TikTokShopValidationError(
                "Video content must include 'video_url' and 'title' fields"
            )

        # Call TikTok Shop API
        response = self.tiktok_client.upload_video(
            video_url=content_data["video_url"],
            title=content_data["title"],
            description=content_data.get("description"),
            product_ids=content_data.get("product_ids"),
            tags=content_data.get("tags")
        )

        # Extract video_id from response
        if response.get("data") and response["data"].get("video_id"):
            return {
                "video_id": response["data"]["video_id"],
                "status": response["data"].get("status"),
                "full_response": response
            }
        else:
            raise TikTokShopAPIError(
                "Invalid response from TikTok API: missing video_id",
                response=response
            )

    def _publish_post(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Publish post content to TikTok Shop

        Args:
            content_data: Dictionary containing post data:
                - content: Post content/text (required)
                - media_urls: List of media URLs (optional)
                - product_ids: List of product IDs to tag (optional)
                - tags: List of hashtags (optional)

        Returns:
            Dictionary containing TikTok API response with post_id

        Raises:
            TikTokShopValidationError: If required fields are missing
            TikTokShopAPIError: If API request fails

        Example:
            >>> content_data = {
            ...     "content": "Check out our new products!",
            ...     "product_ids": ["1234567890"],
            ...     "tags": ["newarrivals", "shopping"]
            ... }
            >>> result = service._publish_post(content_data)
        """
        self.logger.debug(f"Publishing post with data: {content_data}")

        # Validate required fields
        if "content" not in content_data:
            raise TikTokShopValidationError(
                "Post content must include 'content' field"
            )

        # Call TikTok Shop API
        response = self.tiktok_client.create_post(
            content=content_data["content"],
            media_urls=content_data.get("media_urls"),
            product_ids=content_data.get("product_ids"),
            tags=content_data.get("tags")
        )

        # Extract post_id from response
        if response.get("data") and response["data"].get("post_id"):
            return {
                "post_id": response["data"]["post_id"],
                "status": response["data"].get("status"),
                "url": response["data"].get("url"),
                "full_response": response
            }
        else:
            raise TikTokShopAPIError(
                "Invalid response from TikTok API: missing post_id",
                response=response
            )
