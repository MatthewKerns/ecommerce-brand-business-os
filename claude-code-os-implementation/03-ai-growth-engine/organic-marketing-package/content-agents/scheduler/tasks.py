"""
Scheduler Task Functions for TikTok Content Publishing

This module contains the core task functions that are executed by the scheduler
service to automatically publish scheduled content, retry failed content, and
clean up old records.
"""
from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy import and_

from database.connection import get_db_session
from database.models import ScheduledContent, PublishLog
from services.publishing_service import PublishingService
from services.notification_service import NotificationService
from logging_config import get_logger
from exceptions import DatabaseError

# Initialize logger
logger = get_logger("scheduler_tasks")


def check_and_publish_due_content() -> int:
    """
    Check for content scheduled for publishing and publish it

    This function is the core scheduler task that:
    1. Queries database for content with scheduled_time <= current time
    2. Filters for content with status='pending'
    3. Calls PublishingService to publish each content item
    4. Sends notifications for success/failure

    This function should be called by the scheduler every minute to ensure
    timely publishing of scheduled content.

    Returns:
        Number of content items processed

    Raises:
        DatabaseError: If database operations fail

    Example:
        >>> # Called by scheduler service every minute
        >>> processed_count = check_and_publish_due_content()
        >>> logger.info(f"Processed {processed_count} content items")
    """
    db = get_db_session()
    processed_count = 0

    try:
        # Query for content that is due to be published
        current_time = datetime.utcnow()
        due_content = db.query(ScheduledContent).filter(
            and_(
                ScheduledContent.scheduled_time <= current_time,
                ScheduledContent.status == "pending"
            )
        ).all()

        if not due_content:
            logger.debug("No content due for publishing")
            return 0

        logger.info(f"Found {len(due_content)} content items due for publishing")

        # Initialize services
        publishing_service = PublishingService()
        notification_service = NotificationService()

        # Process each content item
        for content in due_content:
            try:
                logger.info(
                    f"Publishing content {content.id} "
                    f"(type: {content.content_type}, "
                    f"scheduled: {content.scheduled_time})"
                )

                # Attempt to publish content
                success = publishing_service.publish_content(content.id)

                if success:
                    # Send success notification
                    notification_service.send_success_notification(
                        scheduled_content_id=content.id,
                        tiktok_video_id=content.tiktok_video_id
                    )
                    logger.info(f"Successfully published content {content.id}")
                else:
                    # Send failure notification
                    notification_service.send_failure_notification(
                        scheduled_content_id=content.id,
                        error_details={
                            "error_type": "publish_failed",
                            "error_message": content.error_message or "Unknown error",
                            "attempt_number": content.retry_count,
                            "retry_available": content.retry_count < content.max_retries
                        }
                    )
                    logger.warning(
                        f"Failed to publish content {content.id} "
                        f"(attempt {content.retry_count}/{content.max_retries})"
                    )

                processed_count += 1

            except Exception as e:
                logger.error(
                    f"Error processing content {content.id}: {e}",
                    exc_info=True
                )
                # Continue processing other content items
                continue

        logger.info(f"Processed {processed_count} content items")
        return processed_count

    except Exception as e:
        logger.error(f"Error in check_and_publish_due_content: {e}", exc_info=True)
        raise DatabaseError("query", str(e), "scheduled_content")

    finally:
        db.close()


def retry_failed_content() -> int:
    """
    Retry publishing content that failed but is within retry limits

    This function:
    1. Queries database for content with status='pending' and retry_count < max_retries
    2. Filters for content that was last attempted at least 5 minutes ago
    3. Calls PublishingService to retry each content item
    4. Sends notifications for success/failure

    This function should be called by the scheduler every 5 minutes to retry
    failed content with exponential backoff.

    Returns:
        Number of content items retried

    Raises:
        DatabaseError: If database operations fail

    Example:
        >>> # Called by scheduler service every 5 minutes
        >>> retry_count = retry_failed_content()
        >>> logger.info(f"Retried {retry_count} failed content items")
    """
    db = get_db_session()
    retry_count = 0

    try:
        # Query for pending content that needs retry
        # Only retry if:
        # 1. Status is 'pending' (failed attempts keep status as pending until max retries exceeded)
        # 2. retry_count > 0 (has been attempted at least once)
        # 3. retry_count < max_retries (within retry limits)
        # 4. Last attempt was at least 5 minutes ago (to respect backoff)
        five_minutes_ago = datetime.utcnow() - timedelta(minutes=5)

        # Get content that needs retry by checking publish logs
        retry_candidates = db.query(ScheduledContent).filter(
            and_(
                ScheduledContent.status == "pending",
                ScheduledContent.retry_count > 0,
                ScheduledContent.retry_count < ScheduledContent.max_retries,
                ScheduledContent.updated_at <= five_minutes_ago
            )
        ).all()

        if not retry_candidates:
            logger.debug("No content needs retry")
            return 0

        logger.info(f"Found {len(retry_candidates)} content items to retry")

        # Initialize services
        publishing_service = PublishingService()
        notification_service = NotificationService()

        # Process each content item
        for content in retry_candidates:
            try:
                logger.info(
                    f"Retrying content {content.id} "
                    f"(attempt {content.retry_count + 1}/{content.max_retries})"
                )

                # Attempt to publish content
                success = publishing_service.publish_content(content.id)

                if success:
                    # Send success notification
                    notification_service.send_success_notification(
                        scheduled_content_id=content.id,
                        tiktok_video_id=content.tiktok_video_id
                    )
                    logger.info(f"Successfully published content {content.id} on retry")
                else:
                    # Send failure notification
                    notification_service.send_failure_notification(
                        scheduled_content_id=content.id,
                        error_details={
                            "error_type": "retry_failed",
                            "error_message": content.error_message or "Unknown error",
                            "attempt_number": content.retry_count,
                            "retry_available": content.retry_count < content.max_retries
                        }
                    )
                    logger.warning(
                        f"Retry failed for content {content.id} "
                        f"(attempt {content.retry_count}/{content.max_retries})"
                    )

                retry_count += 1

            except Exception as e:
                logger.error(
                    f"Error retrying content {content.id}: {e}",
                    exc_info=True
                )
                # Continue processing other content items
                continue

        logger.info(f"Retried {retry_count} content items")
        return retry_count

    except Exception as e:
        logger.error(f"Error in retry_failed_content: {e}", exc_info=True)
        raise DatabaseError("query", str(e), "scheduled_content")

    finally:
        db.close()


def cleanup_old_records(days_to_keep: int = 30) -> int:
    """
    Clean up old published content records from the database

    This function removes published content records that are older than the
    specified number of days to prevent database bloat. Only removes content
    with status='published' to preserve failed/pending content for analysis.

    The cleanup also removes associated PublishLog records via CASCADE delete.

    Args:
        days_to_keep: Number of days of published content to retain (default: 30)

    Returns:
        Number of records deleted

    Raises:
        DatabaseError: If database operations fail

    Example:
        >>> # Called by scheduler service once daily
        >>> deleted_count = cleanup_old_records(days_to_keep=30)
        >>> logger.info(f"Cleaned up {deleted_count} old records")
    """
    db = get_db_session()
    deleted_count = 0

    try:
        # Calculate cutoff date
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)

        logger.info(
            f"Cleaning up published content older than {cutoff_date.isoformat()} "
            f"({days_to_keep} days)"
        )

        # Query for old published content
        old_content = db.query(ScheduledContent).filter(
            and_(
                ScheduledContent.status == "published",
                ScheduledContent.published_at <= cutoff_date
            )
        ).all()

        if not old_content:
            logger.debug("No old published content to clean up")
            return 0

        logger.info(f"Found {len(old_content)} old published content records to delete")

        # Delete old content records
        for content in old_content:
            try:
                logger.debug(
                    f"Deleting content {content.id} "
                    f"(published: {content.published_at})"
                )
                db.delete(content)
                deleted_count += 1

            except Exception as e:
                logger.error(
                    f"Error deleting content {content.id}: {e}",
                    exc_info=True
                )
                # Continue processing other content items
                continue

        # Commit all deletes
        db.commit()
        logger.info(f"Successfully cleaned up {deleted_count} old records")

        return deleted_count

    except Exception as e:
        db.rollback()
        logger.error(f"Error in cleanup_old_records: {e}", exc_info=True)
        raise DatabaseError("delete", str(e), "scheduled_content")

    finally:
        db.close()
