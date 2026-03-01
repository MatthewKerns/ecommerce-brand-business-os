"""
Review workflow routes.

This module defines API endpoints for content review workflow, allowing
human review and approval of AI-generated content before publication.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
import logging

from api.dependencies import get_request_id
from api.models import (
    ReviewSubmitRequest,
    ReviewActionRequest,
    ReviewStatusResponse,
    ErrorResponse
)
from database.connection import get_db
from database.models import ContentReview, ContentHistory, ApprovalStatus

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/review",
    tags=["review"],
    responses={
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)


# ============================================================================
# Endpoints
# ============================================================================

@router.post(
    "/submit",
    response_model=ReviewStatusResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit content for review",
    description="Submit AI-generated content for human review"
)
async def submit_for_review(
    request: ReviewSubmitRequest,
    request_id: str = Depends(get_request_id),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Submit content for human review.

    Args:
        request: Review submission request
        request_id: Unique request identifier
        db: Database session

    Returns:
        Review status response with review details

    Raises:
        HTTPException: If content not found or submission fails
    """
    logger.info(f"[{request_id}] Submitting content for review: content_id={request.content_id}, reviewer={request.reviewer_id}")

    try:
        # Verify content exists
        content = db.query(ContentHistory).filter(
            ContentHistory.id == request.content_id
        ).first()

        if not content:
            logger.warning(f"[{request_id}] Content not found: content_id={request.content_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "ContentNotFound",
                    "message": f"Content with ID {request.content_id} not found",
                    "request_id": request_id,
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                }
            )

        # Check if content already has a review record
        existing_review = db.query(ContentReview).filter(
            ContentReview.content_id == request.content_id
        ).first()

        if existing_review:
            # Update existing review to in_review status
            existing_review.approval_status = ApprovalStatus.IN_REVIEW.value
            existing_review.reviewer_id = request.reviewer_id
            existing_review.submitted_at = datetime.utcnow()
            existing_review.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(existing_review)

            logger.info(f"[{request_id}] Updated existing review: review_id={existing_review.id}")
            review = existing_review
        else:
            # Create new review record
            review = ContentReview(
                content_id=request.content_id,
                approval_status=ApprovalStatus.IN_REVIEW.value,
                reviewer_id=request.reviewer_id,
                submitted_at=datetime.utcnow()
            )
            db.add(review)
            db.commit()
            db.refresh(review)

            logger.info(f"[{request_id}] Created new review record: review_id={review.id}")

        # Build response
        response = {
            "review_id": review.id,
            "content_id": review.content_id,
            "status": review.approval_status,
            "reviewer_id": review.reviewer_id,
            "submitted_at": review.submitted_at,
            "reviewed_at": review.reviewed_at,
            "notes": review.review_notes
        }

        logger.info(f"[{request_id}] Successfully submitted content for review")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[{request_id}] Error submitting content for review: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "ReviewSubmissionError",
                "message": f"Failed to submit content for review: {str(e)}",
                "request_id": request_id,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        )


@router.post(
    "/approve",
    response_model=ReviewStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="Approve content",
    description="Approve content under review"
)
async def approve_content(
    request: ReviewActionRequest,
    request_id: str = Depends(get_request_id),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Approve content under review.

    Args:
        request: Review action request (with action='approve')
        request_id: Unique request identifier
        db: Database session

    Returns:
        Review status response with updated review details

    Raises:
        HTTPException: If review not found or approval fails
    """
    logger.info(f"[{request_id}] Approving content: review_id={request.review_id}")

    try:
        # Validate action is 'approve'
        if request.action != "approve":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "InvalidAction",
                    "message": "Action must be 'approve' for this endpoint",
                    "request_id": request_id,
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                }
            )

        # Get review record
        review = db.query(ContentReview).filter(
            ContentReview.id == request.review_id
        ).first()

        if not review:
            logger.warning(f"[{request_id}] Review not found: review_id={request.review_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "ReviewNotFound",
                    "message": f"Review with ID {request.review_id} not found",
                    "request_id": request_id,
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                }
            )

        # Update review status
        review.approval_status = ApprovalStatus.APPROVED.value
        review.review_notes = request.notes
        review.reviewed_at = datetime.utcnow()
        review.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(review)

        logger.info(f"[{request_id}] Successfully approved content: review_id={review.id}")

        # Build response
        response = {
            "review_id": review.id,
            "content_id": review.content_id,
            "status": review.approval_status,
            "reviewer_id": review.reviewer_id,
            "submitted_at": review.submitted_at,
            "reviewed_at": review.reviewed_at,
            "notes": review.review_notes
        }

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[{request_id}] Error approving content: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "ReviewApprovalError",
                "message": f"Failed to approve content: {str(e)}",
                "request_id": request_id,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        )


@router.post(
    "/reject",
    response_model=ReviewStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="Reject content",
    description="Reject content under review"
)
async def reject_content(
    request: ReviewActionRequest,
    request_id: str = Depends(get_request_id),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Reject content under review.

    Args:
        request: Review action request (with action='reject')
        request_id: Unique request identifier
        db: Database session

    Returns:
        Review status response with updated review details

    Raises:
        HTTPException: If review not found or rejection fails
    """
    logger.info(f"[{request_id}] Rejecting content: review_id={request.review_id}")

    try:
        # Validate action is 'reject'
        if request.action != "reject":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "InvalidAction",
                    "message": "Action must be 'reject' for this endpoint",
                    "request_id": request_id,
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                }
            )

        # Get review record
        review = db.query(ContentReview).filter(
            ContentReview.id == request.review_id
        ).first()

        if not review:
            logger.warning(f"[{request_id}] Review not found: review_id={request.review_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "ReviewNotFound",
                    "message": f"Review with ID {request.review_id} not found",
                    "request_id": request_id,
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                }
            )

        # Update review status
        review.approval_status = ApprovalStatus.REJECTED.value
        review.review_notes = request.notes
        review.reviewed_at = datetime.utcnow()
        review.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(review)

        logger.info(f"[{request_id}] Successfully rejected content: review_id={review.id}")

        # Build response
        response = {
            "review_id": review.id,
            "content_id": review.content_id,
            "status": review.approval_status,
            "reviewer_id": review.reviewer_id,
            "submitted_at": review.submitted_at,
            "reviewed_at": review.reviewed_at,
            "notes": review.review_notes
        }

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[{request_id}] Error rejecting content: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "ReviewRejectionError",
                "message": f"Failed to reject content: {str(e)}",
                "request_id": request_id,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        )


@router.get(
    "/status/{content_id}",
    response_model=ReviewStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="Get review status",
    description="Get the current review status for a content item"
)
async def get_review_status(
    content_id: int,
    request_id: str = Depends(get_request_id),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get review status for a content item.

    Args:
        content_id: Content ID to check review status for
        request_id: Unique request identifier
        db: Database session

    Returns:
        Review status response with current review details

    Raises:
        HTTPException: If content or review not found
    """
    logger.info(f"[{request_id}] Getting review status: content_id={content_id}")

    try:
        # Verify content exists
        content = db.query(ContentHistory).filter(
            ContentHistory.id == content_id
        ).first()

        if not content:
            logger.warning(f"[{request_id}] Content not found: content_id={content_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "ContentNotFound",
                    "message": f"Content with ID {content_id} not found",
                    "request_id": request_id,
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                }
            )

        # Get review record
        review = db.query(ContentReview).filter(
            ContentReview.content_id == content_id
        ).first()

        if not review:
            logger.warning(f"[{request_id}] No review found for content: content_id={content_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "ReviewNotFound",
                    "message": f"No review found for content ID {content_id}",
                    "request_id": request_id,
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                }
            )

        # Build response
        response = {
            "review_id": review.id,
            "content_id": review.content_id,
            "status": review.approval_status,
            "reviewer_id": review.reviewer_id,
            "submitted_at": review.submitted_at,
            "reviewed_at": review.reviewed_at,
            "notes": review.review_notes
        }

        logger.info(f"[{request_id}] Successfully retrieved review status: review_id={review.id}, status={review.approval_status}")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[{request_id}] Error retrieving review status: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "ReviewStatusError",
                "message": f"Failed to retrieve review status: {str(e)}",
                "request_id": request_id,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        )
