"""
Version management routes.

This module defines API endpoints for content version management, allowing
users to track, compare, and revert content versions.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc
import logging
from pydantic import BaseModel, Field

from api.dependencies import get_request_id
from api.models import ErrorResponse
from database.connection import get_db
from database.models import ContentHistory

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/versions",
    tags=["versions"],
    responses={
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)


# ============================================================================
# Request Models
# ============================================================================

class CreateRevisionRequest(BaseModel):
    """Request model for creating a new content revision."""
    content_id: int = Field(
        ...,
        ge=1,
        description="ID of the content to create a revision from"
    )
    content: str = Field(
        ...,
        min_length=1,
        description="Updated content text"
    )
    notes: Optional[str] = Field(
        None,
        max_length=500,
        description="Notes about this revision"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "content_id": 123,
                "content": "# Updated Blog Post\n\nThis is the revised content...",
                "notes": "Fixed grammar and added more details"
            }
        }


class RevertVersionRequest(BaseModel):
    """Request model for reverting to a previous version."""
    notes: Optional[str] = Field(
        None,
        max_length=500,
        description="Notes about why reverting"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "notes": "Reverting to version 2 due to formatting issues in latest"
            }
        }


# ============================================================================
# Response Models
# ============================================================================

class VersionInfo(BaseModel):
    """Version information model."""
    id: int = Field(..., description="Content history ID")
    version_number: int = Field(..., description="Version number")
    content: str = Field(..., description="Content text")
    is_draft: bool = Field(..., description="Whether this is a draft")
    created_at: datetime = Field(..., description="When this version was created")
    updated_at: datetime = Field(..., description="When this version was last updated")
    parent_content_id: Optional[int] = Field(None, description="Parent content ID if this is a revision")

    class Config:
        json_schema_extra = {
            "example": {
                "id": 123,
                "version_number": 2,
                "content": "# Blog Post Title\n\nContent here...",
                "is_draft": False,
                "created_at": "2024-02-26T10:30:45Z",
                "updated_at": "2024-02-26T11:15:30Z",
                "parent_content_id": 122
            }
        }


class VersionHistoryResponse(BaseModel):
    """Response model for version history."""
    content_id: int = Field(..., description="Content ID")
    versions: List[VersionInfo] = Field(..., description="List of all versions")
    total_versions: int = Field(..., description="Total number of versions")

    class Config:
        json_schema_extra = {
            "example": {
                "content_id": 123,
                "versions": [
                    {
                        "id": 123,
                        "version_number": 2,
                        "content": "Updated content",
                        "is_draft": False,
                        "created_at": "2024-02-26T11:00:00Z",
                        "updated_at": "2024-02-26T11:00:00Z",
                        "parent_content_id": 122
                    },
                    {
                        "id": 122,
                        "version_number": 1,
                        "content": "Original content",
                        "is_draft": False,
                        "created_at": "2024-02-26T10:00:00Z",
                        "updated_at": "2024-02-26T10:00:00Z",
                        "parent_content_id": None
                    }
                ],
                "total_versions": 2
            }
        }


class VersionComparisonResponse(BaseModel):
    """Response model for version comparison."""
    version1: VersionInfo = Field(..., description="First version details")
    version2: VersionInfo = Field(..., description="Second version details")
    content_length_diff: int = Field(..., description="Difference in content length (chars)")
    version_diff: int = Field(..., description="Difference in version numbers")

    class Config:
        json_schema_extra = {
            "example": {
                "version1": {
                    "id": 122,
                    "version_number": 1,
                    "content": "Original content",
                    "is_draft": False,
                    "created_at": "2024-02-26T10:00:00Z",
                    "updated_at": "2024-02-26T10:00:00Z",
                    "parent_content_id": None
                },
                "version2": {
                    "id": 123,
                    "version_number": 2,
                    "content": "Updated content with more details",
                    "is_draft": False,
                    "created_at": "2024-02-26T11:00:00Z",
                    "updated_at": "2024-02-26T11:00:00Z",
                    "parent_content_id": 122
                },
                "content_length_diff": 150,
                "version_diff": 1
            }
        }


class CreateRevisionResponse(BaseModel):
    """Response model for creating a revision."""
    id: int = Field(..., description="New content history ID")
    content_id: int = Field(..., description="Original content ID")
    version_number: int = Field(..., description="New version number")
    parent_content_id: int = Field(..., description="Parent content ID")
    created_at: datetime = Field(..., description="When this revision was created")
    message: str = Field(..., description="Success message")

    class Config:
        json_schema_extra = {
            "example": {
                "id": 124,
                "content_id": 123,
                "version_number": 3,
                "parent_content_id": 123,
                "created_at": "2024-02-26T12:00:00Z",
                "message": "Revision created successfully"
            }
        }


# ============================================================================
# Endpoints
# ============================================================================

@router.get(
    "/history/{content_id}",
    response_model=VersionHistoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Get version history",
    description="Get all versions of a content item"
)
async def get_version_history(
    content_id: int,
    request_id: str = Depends(get_request_id),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get version history for a content item.

    Args:
        content_id: Content ID to get version history for
        request_id: Unique request identifier
        db: Database session

    Returns:
        Version history response with all versions

    Raises:
        HTTPException: If content not found or retrieval fails
    """
    logger.info(f"[{request_id}] Getting version history: content_id={content_id}")

    try:
        # Get the original content
        original_content = db.query(ContentHistory).filter(
            ContentHistory.id == content_id
        ).first()

        if not original_content:
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

        # Get all versions (content that references this as parent, plus this content itself)
        versions = db.query(ContentHistory).filter(
            (ContentHistory.id == content_id) |
            (ContentHistory.parent_content_id == content_id)
        ).order_by(desc(ContentHistory.version_number)).all()

        # Build version info list
        version_list = []
        for version in versions:
            version_list.append({
                "id": version.id,
                "version_number": version.version_number,
                "content": version.content,
                "is_draft": version.is_draft,
                "created_at": version.created_at,
                "updated_at": version.updated_at,
                "parent_content_id": version.parent_content_id
            })

        response = {
            "content_id": content_id,
            "versions": version_list,
            "total_versions": len(version_list)
        }

        logger.info(f"[{request_id}] Successfully retrieved version history: {len(version_list)} versions")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[{request_id}] Error retrieving version history: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "VersionHistoryError",
                "message": f"Failed to retrieve version history: {str(e)}",
                "request_id": request_id,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        )


@router.post(
    "/create-revision",
    response_model=CreateRevisionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create content revision",
    description="Create a new revision of existing content"
)
async def create_revision(
    request: CreateRevisionRequest,
    request_id: str = Depends(get_request_id),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Create a new revision of existing content.

    Args:
        request: Create revision request
        request_id: Unique request identifier
        db: Database session

    Returns:
        Create revision response with new version details

    Raises:
        HTTPException: If content not found or creation fails
    """
    logger.info(f"[{request_id}] Creating content revision: content_id={request.content_id}")

    try:
        # Get the original content
        original_content = db.query(ContentHistory).filter(
            ContentHistory.id == request.content_id
        ).first()

        if not original_content:
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

        # Calculate new version number
        max_version = db.query(ContentHistory).filter(
            (ContentHistory.id == request.content_id) |
            (ContentHistory.parent_content_id == request.content_id)
        ).order_by(desc(ContentHistory.version_number)).first()

        new_version_number = (max_version.version_number if max_version else original_content.version_number) + 1

        # Create new content history record as a revision
        new_revision = ContentHistory(
            request_id=f"{original_content.request_id}_v{new_version_number}",
            content_type=original_content.content_type,
            agent_name=original_content.agent_name,
            prompt=original_content.prompt if request.notes is None else f"{original_content.prompt}\n\nRevision notes: {request.notes}",
            parameters=original_content.parameters,
            content_metadata=original_content.content_metadata,
            content=request.content,
            content_format=original_content.content_format,
            model=original_content.model,
            tokens_used=0,  # No new tokens used for manual revision
            generation_time_ms=0,
            status="success",
            version_number=new_version_number,
            parent_content_id=request.content_id,
            is_draft=False,
            user_id=original_content.user_id,
            campaign_id=original_content.campaign_id
        )

        db.add(new_revision)
        db.commit()
        db.refresh(new_revision)

        logger.info(f"[{request_id}] Successfully created revision: id={new_revision.id}, version={new_version_number}")

        response = {
            "id": new_revision.id,
            "content_id": request.content_id,
            "version_number": new_version_number,
            "parent_content_id": request.content_id,
            "created_at": new_revision.created_at,
            "message": f"Revision created successfully as version {new_version_number}"
        }

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[{request_id}] Error creating revision: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "RevisionCreationError",
                "message": f"Failed to create revision: {str(e)}",
                "request_id": request_id,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        )


@router.get(
    "/compare/{version1_id}/{version2_id}",
    response_model=VersionComparisonResponse,
    status_code=status.HTTP_200_OK,
    summary="Compare versions",
    description="Compare two content versions"
)
async def compare_versions(
    version1_id: int,
    version2_id: int,
    request_id: str = Depends(get_request_id),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Compare two content versions.

    Args:
        version1_id: First version ID
        version2_id: Second version ID
        request_id: Unique request identifier
        db: Database session

    Returns:
        Version comparison response with details and differences

    Raises:
        HTTPException: If versions not found or comparison fails
    """
    logger.info(f"[{request_id}] Comparing versions: version1_id={version1_id}, version2_id={version2_id}")

    try:
        # Get both versions
        version1 = db.query(ContentHistory).filter(
            ContentHistory.id == version1_id
        ).first()

        version2 = db.query(ContentHistory).filter(
            ContentHistory.id == version2_id
        ).first()

        if not version1:
            logger.warning(f"[{request_id}] Version 1 not found: version1_id={version1_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "VersionNotFound",
                    "message": f"Version with ID {version1_id} not found",
                    "request_id": request_id,
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                }
            )

        if not version2:
            logger.warning(f"[{request_id}] Version 2 not found: version2_id={version2_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "VersionNotFound",
                    "message": f"Version with ID {version2_id} not found",
                    "request_id": request_id,
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                }
            )

        # Calculate differences
        content_length_diff = len(version2.content) - len(version1.content)
        version_diff = version2.version_number - version1.version_number

        response = {
            "version1": {
                "id": version1.id,
                "version_number": version1.version_number,
                "content": version1.content,
                "is_draft": version1.is_draft,
                "created_at": version1.created_at,
                "updated_at": version1.updated_at,
                "parent_content_id": version1.parent_content_id
            },
            "version2": {
                "id": version2.id,
                "version_number": version2.version_number,
                "content": version2.content,
                "is_draft": version2.is_draft,
                "created_at": version2.created_at,
                "updated_at": version2.updated_at,
                "parent_content_id": version2.parent_content_id
            },
            "content_length_diff": content_length_diff,
            "version_diff": version_diff
        }

        logger.info(f"[{request_id}] Successfully compared versions")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[{request_id}] Error comparing versions: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "VersionComparisonError",
                "message": f"Failed to compare versions: {str(e)}",
                "request_id": request_id,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        )


@router.post(
    "/revert/{content_id}/{version_number}",
    response_model=CreateRevisionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Revert to version",
    description="Revert content to a previous version"
)
async def revert_to_version(
    content_id: int,
    version_number: int,
    request: RevertVersionRequest,
    request_id: str = Depends(get_request_id),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Revert content to a previous version.

    Args:
        content_id: Content ID to revert
        version_number: Version number to revert to
        request: Revert version request
        request_id: Unique request identifier
        db: Database session

    Returns:
        Create revision response with new version details

    Raises:
        HTTPException: If content or version not found or revert fails
    """
    logger.info(f"[{request_id}] Reverting content: content_id={content_id}, version_number={version_number}")

    try:
        # Find the version to revert to
        target_version = db.query(ContentHistory).filter(
            (ContentHistory.id == content_id) | (ContentHistory.parent_content_id == content_id),
            ContentHistory.version_number == version_number
        ).first()

        if not target_version:
            logger.warning(f"[{request_id}] Version not found: content_id={content_id}, version_number={version_number}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "VersionNotFound",
                    "message": f"Version {version_number} not found for content ID {content_id}",
                    "request_id": request_id,
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                }
            )

        # Get the original content to find current max version
        original_content = db.query(ContentHistory).filter(
            ContentHistory.id == content_id
        ).first()

        if not original_content:
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

        # Calculate new version number
        max_version = db.query(ContentHistory).filter(
            (ContentHistory.id == content_id) |
            (ContentHistory.parent_content_id == content_id)
        ).order_by(desc(ContentHistory.version_number)).first()

        new_version_number = (max_version.version_number if max_version else original_content.version_number) + 1

        # Create new content history record with reverted content
        revert_notes = f"Reverted to version {version_number}"
        if request.notes:
            revert_notes += f": {request.notes}"

        new_revision = ContentHistory(
            request_id=f"{original_content.request_id}_revert_v{new_version_number}",
            content_type=target_version.content_type,
            agent_name=target_version.agent_name,
            prompt=f"{target_version.prompt}\n\n{revert_notes}",
            parameters=target_version.parameters,
            content_metadata=target_version.content_metadata,
            content=target_version.content,  # Revert to old content
            content_format=target_version.content_format,
            model=target_version.model,
            tokens_used=0,  # No new tokens used for revert
            generation_time_ms=0,
            status="success",
            version_number=new_version_number,
            parent_content_id=content_id,
            is_draft=False,
            user_id=target_version.user_id,
            campaign_id=target_version.campaign_id
        )

        db.add(new_revision)
        db.commit()
        db.refresh(new_revision)

        logger.info(f"[{request_id}] Successfully reverted content: id={new_revision.id}, version={new_version_number}")

        response = {
            "id": new_revision.id,
            "content_id": content_id,
            "version_number": new_version_number,
            "parent_content_id": content_id,
            "created_at": new_revision.created_at,
            "message": f"Content reverted to version {version_number} as new version {new_version_number}"
        }

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[{request_id}] Error reverting version: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "VersionRevertError",
                "message": f"Failed to revert to version: {str(e)}",
                "request_id": request_id,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        )
