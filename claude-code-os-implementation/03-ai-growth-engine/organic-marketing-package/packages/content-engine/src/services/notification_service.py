"""
Notification Service for TikTok Content Publishing

This service handles sending notifications for publishing events including
success confirmations and failure alerts. Initially implements logging-based
notifications with architecture support for future email/SMS/webhook integrations.
"""
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from database.connection import get_db_session
from database.models import ScheduledContent, PublishLog
from logging_config import get_logger
from exceptions import DatabaseError


class NotificationService:
    """
    Service for sending notifications about content publishing events

    This service provides immediate notification when posts succeed or fail,
    addressing the critical pain point where scheduled posts fail without user
    awareness. Currently implements logging-based notifications with a clean
    interface for future expansion to email, SMS, or webhook integrations.

    Attributes:
        logger: Logger instance for service operations

    Example:
        >>> service = NotificationService()
        >>> service.send_failure_notification(
        ...     scheduled_content_id=123,
        ...     error_details={"error_type": "auth_error", "message": "Invalid token"}
        ... )
        >>> service.send_success_notification(
        ...     scheduled_content_id=123,
        ...     tiktok_video_id="7123456789"
        ... )
    """

    def __init__(self):
        """
        Initialize the Notification Service

        Sets up logging and prepares service for sending notifications.
        """
        self.logger = get_logger("notification_service")
        self.logger.info("Notification service initialized successfully")

    def send_failure_notification(
        self,
        scheduled_content_id: int,
        error_details: Dict[str, Any]
    ) -> bool:
        """
        Send notification when content publishing fails

        This method logs detailed failure information and prepares the notification
        payload for future integration with email/SMS/webhook systems. Critical for
        ensuring brand owners are immediately aware of publishing failures.

        Args:
            scheduled_content_id: ID of the scheduled content that failed
            error_details: Dictionary containing error information:
                - error_type: Type of error (auth_error, validation_error, etc.)
                - error_message: Human-readable error message
                - attempt_number: Which attempt failed (optional)
                - retry_available: Whether retry is possible (optional)

        Returns:
            True if notification was sent successfully, False otherwise

        Raises:
            DatabaseError: If database operations fail

        Example:
            >>> service = NotificationService()
            >>> service.send_failure_notification(
            ...     scheduled_content_id=123,
            ...     error_details={
            ...         "error_type": "rate_limit_error",
            ...         "error_message": "Rate limit exceeded, will retry",
            ...         "attempt_number": 2,
            ...         "retry_available": True
            ...     }
            ... )
        """
        try:
            # Load content details from database
            db = get_db_session()
            scheduled_content = db.query(ScheduledContent).filter(
                ScheduledContent.id == scheduled_content_id
            ).first()

            if not scheduled_content:
                self.logger.error(
                    f"Cannot send failure notification: scheduled content {scheduled_content_id} not found"
                )
                db.close()
                return False

            # Get latest publish log for additional context
            latest_log = db.query(PublishLog).filter(
                PublishLog.scheduled_content_id == scheduled_content_id
            ).order_by(PublishLog.attempted_at.desc()).first()

            # Build notification context
            notification_context = {
                "scheduled_content_id": scheduled_content_id,
                "content_type": scheduled_content.content_type,
                "scheduled_time": scheduled_content.scheduled_time.isoformat(),
                "retry_count": scheduled_content.retry_count,
                "max_retries": scheduled_content.max_retries,
                "error_type": error_details.get("error_type", "unknown_error"),
                "error_message": error_details.get("error_message", "No error message provided"),
                "attempt_number": error_details.get("attempt_number", scheduled_content.retry_count),
                "retry_available": error_details.get(
                    "retry_available",
                    scheduled_content.retry_count < scheduled_content.max_retries
                ),
                "timestamp": datetime.utcnow().isoformat()
            }

            if latest_log:
                notification_context["last_attempt_time"] = latest_log.attempted_at.isoformat()

            # Log failure notification (structured for future notification channels)
            self.logger.error(
                f"PUBLISH FAILURE NOTIFICATION | "
                f"Content ID: {scheduled_content_id} | "
                f"Type: {notification_context['error_type']} | "
                f"Message: {notification_context['error_message']} | "
                f"Retry: {notification_context['retry_count']}/{notification_context['max_retries']} | "
                f"Retry Available: {notification_context['retry_available']}"
            )

            # Future extension point: Send to email/SMS/webhook
            # self._send_email_notification(notification_context)
            # self._send_sms_notification(notification_context)
            # self._send_webhook_notification(notification_context)

            db.close()
            return True

        except Exception as e:
            self.logger.error(
                f"Error sending failure notification for content {scheduled_content_id}: {e}",
                exc_info=True
            )
            return False

    def send_success_notification(
        self,
        scheduled_content_id: int,
        tiktok_video_id: str
    ) -> bool:
        """
        Send notification when content is successfully published

        This method logs success information and provides confirmation that
        scheduled content was published as expected. Helps brand owners track
        their content strategy execution.

        Args:
            scheduled_content_id: ID of the scheduled content that was published
            tiktok_video_id: TikTok video/post ID from successful publish

        Returns:
            True if notification was sent successfully, False otherwise

        Raises:
            DatabaseError: If database operations fail

        Example:
            >>> service = NotificationService()
            >>> service.send_success_notification(
            ...     scheduled_content_id=123,
            ...     tiktok_video_id="7123456789012345678"
            ... )
        """
        try:
            # Load content details from database
            db = get_db_session()
            scheduled_content = db.query(ScheduledContent).filter(
                ScheduledContent.id == scheduled_content_id
            ).first()

            if not scheduled_content:
                self.logger.error(
                    f"Cannot send success notification: scheduled content {scheduled_content_id} not found"
                )
                db.close()
                return False

            # Build notification context
            notification_context = {
                "scheduled_content_id": scheduled_content_id,
                "content_type": scheduled_content.content_type,
                "scheduled_time": scheduled_content.scheduled_time.isoformat(),
                "published_at": scheduled_content.published_at.isoformat() if scheduled_content.published_at else None,
                "tiktok_video_id": tiktok_video_id,
                "retry_count": scheduled_content.retry_count,
                "timestamp": datetime.utcnow().isoformat()
            }

            # Log success notification (structured for future notification channels)
            self.logger.info(
                f"PUBLISH SUCCESS NOTIFICATION | "
                f"Content ID: {scheduled_content_id} | "
                f"Type: {notification_context['content_type']} | "
                f"TikTok ID: {tiktok_video_id} | "
                f"Scheduled: {notification_context['scheduled_time']} | "
                f"Published: {notification_context['published_at']} | "
                f"Attempts: {notification_context['retry_count'] + 1}"
            )

            # Future extension point: Send to email/SMS/webhook
            # self._send_email_notification(notification_context, success=True)
            # self._send_sms_notification(notification_context, success=True)
            # self._send_webhook_notification(notification_context, success=True)

            db.close()
            return True

        except Exception as e:
            self.logger.error(
                f"Error sending success notification for content {scheduled_content_id}: {e}",
                exc_info=True
            )
            return False

    # Future notification channel methods (commented out for initial implementation)
    # These can be implemented when email/SMS/webhook integrations are added

    # def _send_email_notification(
    #     self,
    #     notification_context: Dict[str, Any],
    #     success: bool = False
    # ) -> bool:
    #     """
    #     Send email notification
    #
    #     Args:
    #         notification_context: Notification details
    #         success: Whether this is a success or failure notification
    #
    #     Returns:
    #         True if email sent successfully
    #     """
    #     # TODO: Implement email sending via SMTP or email service API
    #     pass
    #
    # def _send_sms_notification(
    #     self,
    #     notification_context: Dict[str, Any],
    #     success: bool = False
    # ) -> bool:
    #     """
    #     Send SMS notification
    #
    #     Args:
    #         notification_context: Notification details
    #         success: Whether this is a success or failure notification
    #
    #     Returns:
    #         True if SMS sent successfully
    #     """
    #     # TODO: Implement SMS sending via Twilio or similar service
    #     pass
    #
    # def _send_webhook_notification(
    #     self,
    #     notification_context: Dict[str, Any],
    #     success: bool = False
    # ) -> bool:
    #     """
    #     Send webhook notification
    #
    #     Args:
    #         notification_context: Notification details
    #         success: Whether this is a success or failure notification
    #
    #     Returns:
    #         True if webhook sent successfully
    #     """
    #     # TODO: Implement webhook POST to configured endpoints
    #     pass
