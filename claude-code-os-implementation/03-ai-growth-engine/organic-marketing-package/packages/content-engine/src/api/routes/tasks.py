"""
Task status management routes.

This module defines API endpoints for checking the status of async tasks.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, Optional
from datetime import datetime
import logging

from api.dependencies import get_request_id
from api.models import ErrorResponse
from pydantic import BaseModel, Field
from celery.result import AsyncResult
from celery_app import app

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
    responses={
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)


# ============================================================================
# Response Models
# ============================================================================

class TaskStatusResponse(BaseModel):
    """Response model for task status check."""
    task_id: str = Field(
        ...,
        description="Unique identifier for the task"
    )
    status: str = Field(
        ...,
        description="Current status: pending, running, completed, failed"
    )
    result: Optional[Dict[str, Any]] = Field(
        None,
        description="Task result if completed"
    )
    error: Optional[str] = Field(
        None,
        description="Error message if failed"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp of status check"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "task_id": "abc123def456",
                "status": "completed",
                "result": {
                    "success": True,
                    "content_id": 42,
                    "topic": "How to Organize Your Trading Cards"
                },
                "error": None,
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }


# ============================================================================
# Endpoints
# ============================================================================

@router.get(
    "/status/{task_id}",
    response_model=TaskStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="Check task status",
    description="Check the status of an async content generation task"
)
async def get_task_status(
    task_id: str,
    request_id: str = Depends(get_request_id)
) -> Dict[str, Any]:
    """
    Check the status of an async task.

    This endpoint retrieves the current status of a background task using its task ID.
    Returns the task state and result if completed.

    Args:
        task_id: Unique identifier for the task
        request_id: Unique request identifier

    Returns:
        Task status response with current state and result

    Raises:
        HTTPException: If task status check fails
    """
    logger.info(f"[{request_id}] Checking status for task: {task_id}")

    try:
        # Get task result using Celery AsyncResult
        task_result = AsyncResult(task_id, app=app)

        # Map Celery states to our status values
        celery_state = task_result.state

        # Convert Celery state to our standard status
        if celery_state == "PENDING":
            task_status = "pending"
            result_data = None
            error_message = None
        elif celery_state == "STARTED":
            task_status = "running"
            result_data = None
            error_message = None
        elif celery_state == "SUCCESS":
            task_status = "completed"
            result_data = task_result.result
            error_message = None
        elif celery_state == "FAILURE":
            task_status = "failed"
            result_data = None
            error_message = str(task_result.info) if task_result.info else "Task failed"
        elif celery_state == "RETRY":
            task_status = "running"
            result_data = None
            error_message = None
        else:
            # Handle other states (REVOKED, REJECTED, etc.)
            task_status = celery_state.lower()
            result_data = None
            error_message = f"Unexpected task state: {celery_state}"

        response = {
            "task_id": task_id,
            "status": task_status,
            "result": result_data,
            "error": error_message,
            "timestamp": datetime.utcnow()
        }

        logger.info(
            f"[{request_id}] Task status retrieved: "
            f"task_id={task_id}, status={task_status}"
        )

        return response

    except Exception as e:
        logger.error(
            f"[{request_id}] Error checking task status: task_id={task_id}, error={e}",
            exc_info=True
        )
        raise HTTPException(
            status_code=500,
            detail={
                "error": "TaskStatusError",
                "message": f"Failed to check task status: {str(e)}",
                "request_id": request_id,
                "task_id": task_id,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        )
