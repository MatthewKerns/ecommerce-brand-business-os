"""
TikTok content scheduling routes.

This module defines API endpoints for TikTok content scheduling and publishing management.
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from datetime import datetime
import logging
import json

from api.dependencies import get_request_id
from api.models import (
    ScheduleContentRequest,
    ScheduleContentResponse,
    ScheduledContentDetail,
    BulkScheduleRequest,
    BulkScheduleResponse,
    ErrorResponse
)
from database.connection import get_session
from database.models import ScheduledContent
from sqlalchemy.orm import Session

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/tiktok",
    tags=["tiktok-scheduling"],
    responses={
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)


# ============================================================================
# Helper Functions
# ============================================================================

def _scheduled_content_to_response(scheduled_content: ScheduledContent) -> ScheduleContentResponse:
    """
    Convert ScheduledContent database model to API response model.

    Args:
        scheduled_content: ScheduledContent database object

    Returns:
        ScheduleContentResponse object
    """
    return ScheduleContentResponse(
        id=scheduled_content.id,
        content_type=scheduled_content.content_type,
        status=scheduled_content.status,
        scheduled_time=scheduled_content.scheduled_time,
        created_at=scheduled_content.created_at,
        max_retries=scheduled_content.max_retries
    )


def _scheduled_content_to_detail(scheduled_content: ScheduledContent) -> ScheduledContentDetail:
    """
    Convert ScheduledContent database model to detailed API response model.

    Args:
        scheduled_content: ScheduledContent database object

    Returns:
        ScheduledContentDetail object
    """
    # Parse JSON content_data
    try:
        content_data = json.loads(scheduled_content.content_data)
    except json.JSONDecodeError:
        content_data = {}

    return ScheduledContentDetail(
        id=scheduled_content.id,
        content_type=scheduled_content.content_type,
        content_data=content_data,
        scheduled_time=scheduled_content.scheduled_time,
        status=scheduled_content.status,
        retry_count=scheduled_content.retry_count,
        max_retries=scheduled_content.max_retries,
        tiktok_video_id=scheduled_content.tiktok_video_id,
        error_message=scheduled_content.error_message,
        created_at=scheduled_content.created_at,
        updated_at=scheduled_content.updated_at,
        published_at=scheduled_content.published_at
    )


# ============================================================================
# API Endpoints
# ============================================================================

@router.post(
    "/schedule",
    response_model=ScheduleContentResponse,
    status_code=201,
    summary="Schedule TikTok content",
    description="Schedule a single piece of content for automatic publishing to TikTok"
)
async def schedule_content(
    request: ScheduleContentRequest,
    request_id: str = Depends(get_request_id)
) -> ScheduleContentResponse:
    """
    Schedule content for automatic TikTok publishing.

    This endpoint creates a new scheduled content item that will be automatically
    published by the scheduler service at the specified time.

    Args:
        request: Content scheduling request with type, data, and schedule time
        request_id: Unique request identifier

    Returns:
        ScheduleContentResponse with scheduling confirmation

    Raises:
        HTTPException: 400 if validation fails, 500 for server errors
    """
    try:
        logger.info(
            f"Scheduling TikTok {request.content_type} content | "
            f"Request ID: {request_id} | "
            f"Scheduled Time: {request.scheduled_time}"
        )

        # Validate scheduled time is in the future
        if request.scheduled_time <= datetime.utcnow():
            raise HTTPException(
                status_code=400,
                detail="scheduled_time must be in the future"
            )

        # Create database record
        db = next(get_session())
        try:
            scheduled_content = ScheduledContent(
                content_type=request.content_type,
                content_data=json.dumps(request.content_data),
                scheduled_time=request.scheduled_time,
                status="pending",
                retry_count=0,
                max_retries=request.max_retries
            )

            db.add(scheduled_content)
            db.commit()
            db.refresh(scheduled_content)

            logger.info(
                f"Content scheduled successfully | "
                f"Request ID: {request_id} | "
                f"Scheduled Content ID: {scheduled_content.id}"
            )

            return _scheduled_content_to_response(scheduled_content)

        finally:
            db.close()

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error scheduling content | "
            f"Request ID: {request_id} | "
            f"Error: {str(e)}",
            exc_info=True
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to schedule content: {str(e)}"
        )


@router.post(
    "/schedule/bulk",
    response_model=BulkScheduleResponse,
    status_code=201,
    summary="Bulk schedule TikTok content",
    description="Schedule multiple content items in a single request (up to 100 items)"
)
async def schedule_bulk_content(
    request: BulkScheduleRequest,
    request_id: str = Depends(get_request_id)
) -> BulkScheduleResponse:
    """
    Schedule multiple content items for automatic TikTok publishing.

    This endpoint creates multiple scheduled content items in a single request.
    Items that fail validation are returned in the failed list while valid items
    are scheduled successfully.

    Args:
        request: Bulk scheduling request with list of content items
        request_id: Unique request identifier

    Returns:
        BulkScheduleResponse with success/failure breakdown

    Raises:
        HTTPException: 500 for server errors
    """
    try:
        logger.info(
            f"Bulk scheduling TikTok content | "
            f"Request ID: {request_id} | "
            f"Total Items: {len(request.items)}"
        )

        scheduled = []
        failed = []

        db = next(get_session())
        try:
            for idx, item in enumerate(request.items):
                try:
                    # Validate scheduled time is in the future
                    if item.scheduled_time <= datetime.utcnow():
                        failed.append({
                            "index": idx,
                            "item": item.dict(),
                            "error": "scheduled_time must be in the future"
                        })
                        continue

                    # Create database record
                    scheduled_content = ScheduledContent(
                        content_type=item.content_type,
                        content_data=json.dumps(item.content_data),
                        scheduled_time=item.scheduled_time,
                        status="pending",
                        retry_count=0,
                        max_retries=item.max_retries
                    )

                    db.add(scheduled_content)
                    db.flush()  # Get ID without committing

                    scheduled.append(_scheduled_content_to_response(scheduled_content))

                except Exception as e:
                    failed.append({
                        "index": idx,
                        "item": item.dict(),
                        "error": str(e)
                    })

            # Commit all successful items
            db.commit()

            logger.info(
                f"Bulk scheduling complete | "
                f"Request ID: {request_id} | "
                f"Scheduled: {len(scheduled)} | "
                f"Failed: {len(failed)}"
            )

            return BulkScheduleResponse(
                scheduled=scheduled,
                failed=failed,
                total_requested=len(request.items),
                total_scheduled=len(scheduled),
                total_failed=len(failed)
            )

        finally:
            db.close()

    except Exception as e:
        logger.error(
            f"Error in bulk scheduling | "
            f"Request ID: {request_id} | "
            f"Error: {str(e)}",
            exc_info=True
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to bulk schedule content: {str(e)}"
        )


@router.get(
    "/schedule",
    response_model=List[ScheduledContentDetail],
    summary="List scheduled content",
    description="Retrieve all scheduled content items with optional status filtering"
)
async def list_scheduled_content(
    status: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    request_id: str = Depends(get_request_id)
) -> List[ScheduledContentDetail]:
    """
    List all scheduled content items.

    This endpoint retrieves scheduled content with optional filtering by status.
    Results are ordered by scheduled_time ascending (next to publish first).

    Args:
        status: Optional status filter (pending, published, failed)
        limit: Maximum number of items to return (default: 100, max: 1000)
        offset: Number of items to skip (for pagination)
        request_id: Unique request identifier

    Returns:
        List of ScheduledContentDetail objects

    Raises:
        HTTPException: 400 for invalid parameters, 500 for server errors
    """
    try:
        # Validate status if provided
        if status and status not in ["pending", "published", "failed"]:
            raise HTTPException(
                status_code=400,
                detail="status must be one of: pending, published, failed"
            )

        # Validate limit
        if limit < 1 or limit > 1000:
            raise HTTPException(
                status_code=400,
                detail="limit must be between 1 and 1000"
            )

        logger.info(
            f"Listing scheduled content | "
            f"Request ID: {request_id} | "
            f"Status: {status} | "
            f"Limit: {limit} | "
            f"Offset: {offset}"
        )

        db = next(get_session())
        try:
            query = db.query(ScheduledContent)

            # Apply status filter if provided
            if status:
                query = query.filter(ScheduledContent.status == status)

            # Order by scheduled_time (next to publish first)
            query = query.order_by(ScheduledContent.scheduled_time.asc())

            # Apply pagination
            query = query.limit(limit).offset(offset)

            scheduled_items = query.all()

            logger.info(
                f"Retrieved {len(scheduled_items)} scheduled content items | "
                f"Request ID: {request_id}"
            )

            return [_scheduled_content_to_detail(item) for item in scheduled_items]

        finally:
            db.close()

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error listing scheduled content | "
            f"Request ID: {request_id} | "
            f"Error: {str(e)}",
            exc_info=True
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list scheduled content: {str(e)}"
        )


@router.get(
    "/schedule/{schedule_id}",
    response_model=ScheduledContentDetail,
    summary="Get scheduled content details",
    description="Retrieve detailed information about a specific scheduled content item"
)
async def get_scheduled_content(
    schedule_id: int,
    request_id: str = Depends(get_request_id)
) -> ScheduledContentDetail:
    """
    Get details for a specific scheduled content item.

    This endpoint retrieves full details including publish status, error messages,
    and TikTok video ID for a scheduled content item.

    Args:
        schedule_id: ID of the scheduled content item
        request_id: Unique request identifier

    Returns:
        ScheduledContentDetail object

    Raises:
        HTTPException: 404 if not found, 500 for server errors
    """
    try:
        logger.info(
            f"Retrieving scheduled content | "
            f"Request ID: {request_id} | "
            f"Schedule ID: {schedule_id}"
        )

        db = next(get_session())
        try:
            scheduled_content = db.query(ScheduledContent).filter(
                ScheduledContent.id == schedule_id
            ).first()

            if not scheduled_content:
                raise HTTPException(
                    status_code=404,
                    detail=f"Scheduled content with ID {schedule_id} not found"
                )

            return _scheduled_content_to_detail(scheduled_content)

        finally:
            db.close()

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error retrieving scheduled content | "
            f"Request ID: {request_id} | "
            f"Schedule ID: {schedule_id} | "
            f"Error: {str(e)}",
            exc_info=True
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve scheduled content: {str(e)}"
        )


@router.put(
    "/schedule/{schedule_id}",
    response_model=ScheduleContentResponse,
    summary="Update scheduled content",
    description="Update the scheduled time or max_retries for pending content"
)
async def update_scheduled_content(
    schedule_id: int,
    request: ScheduleContentRequest,
    request_id: str = Depends(get_request_id)
) -> ScheduleContentResponse:
    """
    Update a scheduled content item.

    This endpoint allows updating the content data, scheduled time, or max_retries
    for content that hasn't been published yet. Only pending content can be updated.

    Args:
        schedule_id: ID of the scheduled content item
        request: Updated content scheduling request
        request_id: Unique request identifier

    Returns:
        ScheduleContentResponse with updated information

    Raises:
        HTTPException: 400 for validation errors, 404 if not found, 500 for server errors
    """
    try:
        logger.info(
            f"Updating scheduled content | "
            f"Request ID: {request_id} | "
            f"Schedule ID: {schedule_id}"
        )

        # Validate scheduled time is in the future
        if request.scheduled_time <= datetime.utcnow():
            raise HTTPException(
                status_code=400,
                detail="scheduled_time must be in the future"
            )

        db = next(get_session())
        try:
            scheduled_content = db.query(ScheduledContent).filter(
                ScheduledContent.id == schedule_id
            ).first()

            if not scheduled_content:
                raise HTTPException(
                    status_code=404,
                    detail=f"Scheduled content with ID {schedule_id} not found"
                )

            # Only allow updating pending content
            if scheduled_content.status != "pending":
                raise HTTPException(
                    status_code=400,
                    detail=f"Cannot update content with status '{scheduled_content.status}'. Only pending content can be updated."
                )

            # Update fields
            scheduled_content.content_type = request.content_type
            scheduled_content.content_data = json.dumps(request.content_data)
            scheduled_content.scheduled_time = request.scheduled_time
            scheduled_content.max_retries = request.max_retries
            scheduled_content.updated_at = datetime.utcnow()

            db.commit()
            db.refresh(scheduled_content)

            logger.info(
                f"Scheduled content updated successfully | "
                f"Request ID: {request_id} | "
                f"Schedule ID: {schedule_id}"
            )

            return _scheduled_content_to_response(scheduled_content)

        finally:
            db.close()

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error updating scheduled content | "
            f"Request ID: {request_id} | "
            f"Schedule ID: {schedule_id} | "
            f"Error: {str(e)}",
            exc_info=True
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update scheduled content: {str(e)}"
        )


@router.delete(
    "/schedule/{schedule_id}",
    status_code=204,
    summary="Cancel scheduled content",
    description="Delete/cancel a scheduled content item (only pending content can be deleted)"
)
async def delete_scheduled_content(
    schedule_id: int,
    request_id: str = Depends(get_request_id)
) -> None:
    """
    Delete/cancel a scheduled content item.

    This endpoint removes a scheduled content item from the queue. Only pending
    content can be deleted. Published or failed content cannot be deleted to
    maintain audit history.

    Args:
        schedule_id: ID of the scheduled content item
        request_id: Unique request identifier

    Returns:
        None (204 No Content)

    Raises:
        HTTPException: 400 if not pending, 404 if not found, 500 for server errors
    """
    try:
        logger.info(
            f"Deleting scheduled content | "
            f"Request ID: {request_id} | "
            f"Schedule ID: {schedule_id}"
        )

        db = next(get_session())
        try:
            scheduled_content = db.query(ScheduledContent).filter(
                ScheduledContent.id == schedule_id
            ).first()

            if not scheduled_content:
                raise HTTPException(
                    status_code=404,
                    detail=f"Scheduled content with ID {schedule_id} not found"
                )

            # Only allow deleting pending content
            if scheduled_content.status != "pending":
                raise HTTPException(
                    status_code=400,
                    detail=f"Cannot delete content with status '{scheduled_content.status}'. Only pending content can be deleted."
                )

            db.delete(scheduled_content)
            db.commit()

            logger.info(
                f"Scheduled content deleted successfully | "
                f"Request ID: {request_id} | "
                f"Schedule ID: {schedule_id}"
            )

        finally:
            db.close()

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error deleting scheduled content | "
            f"Request ID: {request_id} | "
            f"Schedule ID: {schedule_id} | "
            f"Error: {str(e)}",
            exc_info=True
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete scheduled content: {str(e)}"
        )


@router.post(
    "/schedule/{schedule_id}/retry",
    response_model=ScheduleContentResponse,
    summary="Manually retry failed content",
    description="Manually retry publishing failed content (resets retry count and status)"
)
async def retry_scheduled_content(
    schedule_id: int,
    request_id: str = Depends(get_request_id)
) -> ScheduleContentResponse:
    """
    Manually retry publishing failed content.

    This endpoint resets the status to pending and retry count to 0, allowing
    the scheduler to attempt publishing again. Only failed content can be retried.

    Args:
        schedule_id: ID of the scheduled content item
        request_id: Unique request identifier

    Returns:
        ScheduleContentResponse with updated status

    Raises:
        HTTPException: 400 if not failed, 404 if not found, 500 for server errors
    """
    try:
        logger.info(
            f"Manually retrying scheduled content | "
            f"Request ID: {request_id} | "
            f"Schedule ID: {schedule_id}"
        )

        db = next(get_session())
        try:
            scheduled_content = db.query(ScheduledContent).filter(
                ScheduledContent.id == schedule_id
            ).first()

            if not scheduled_content:
                raise HTTPException(
                    status_code=404,
                    detail=f"Scheduled content with ID {schedule_id} not found"
                )

            # Only allow retrying failed content
            if scheduled_content.status != "failed":
                raise HTTPException(
                    status_code=400,
                    detail=f"Cannot retry content with status '{scheduled_content.status}'. Only failed content can be retried."
                )

            # Reset status and retry count
            scheduled_content.status = "pending"
            scheduled_content.retry_count = 0
            scheduled_content.error_message = None
            scheduled_content.updated_at = datetime.utcnow()

            db.commit()
            db.refresh(scheduled_content)

            logger.info(
                f"Scheduled content reset for retry | "
                f"Request ID: {request_id} | "
                f"Schedule ID: {schedule_id}"
            )

            return _scheduled_content_to_response(scheduled_content)

        finally:
            db.close()

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error retrying scheduled content | "
            f"Request ID: {request_id} | "
            f"Schedule ID: {schedule_id} | "
            f"Error: {str(e)}",
            exc_info=True
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retry scheduled content: {str(e)}"
        )
