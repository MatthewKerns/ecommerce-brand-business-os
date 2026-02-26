"""
TikTok Channel Management Routes

This module defines API endpoints for managing TikTok channels in the 4-channel strategy
(Air, Water, Fire, Earth) and generating channel-specific content.
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
import logging
import time

from api.dependencies import get_request_id
from api.models import ContentMetadata, ErrorResponse
from pydantic import BaseModel, Field
from agents.tiktok_channel_agent import TikTokChannelAgent

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/tiktok-channels",
    tags=["tiktok-channels"],
    responses={
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)


# ============================================================================
# Request Models
# ============================================================================

class CreateChannelRequest(BaseModel):
    """Request model for creating a new TikTok channel."""
    channel_name: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="Name of the TikTok channel"
    )
    element_theme: str = Field(
        ...,
        pattern="^(air|water|fire|earth)$",
        description="Element theme for the channel"
    )
    description: Optional[str] = Field(
        None,
        description="Channel description and purpose"
    )
    target_audience: Optional[str] = Field(
        None,
        description="Target audience description"
    )
    posting_schedule: Optional[Dict[str, Any]] = Field(
        None,
        description="Posting schedule configuration"
    )
    branding_guidelines: Optional[Dict[str, Any]] = Field(
        None,
        description="Branding guidelines for the channel"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "channel_name": "QuickTCG Air",
                "element_theme": "air",
                "description": "Fast-paced TikTok tips and tournament prep",
                "target_audience": "Competitive TCG players seeking quick wins",
                "posting_schedule": {
                    "frequency": "daily",
                    "days": ["Mon", "Tue", "Wed", "Thu", "Fri"],
                    "best_times": ["07:00", "12:00", "18:00"]
                },
                "branding_guidelines": {
                    "hashtags": ["#QuickTCG", "#AirStrategy"],
                    "visual_style": "Fast cuts, energetic music"
                }
            }
        }


class UpdateChannelRequest(BaseModel):
    """Request model for updating a TikTok channel."""
    channel_name: Optional[str] = Field(
        None,
        min_length=3,
        max_length=100,
        description="New channel name"
    )
    description: Optional[str] = Field(
        None,
        description="Updated channel description"
    )
    target_audience: Optional[str] = Field(
        None,
        description="Updated target audience"
    )
    posting_schedule: Optional[Dict[str, Any]] = Field(
        None,
        description="Updated posting schedule"
    )
    branding_guidelines: Optional[Dict[str, Any]] = Field(
        None,
        description="Updated branding guidelines"
    )
    is_active: Optional[bool] = Field(
        None,
        description="Channel active status"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "posting_schedule": {
                    "frequency": "twice_daily",
                    "days": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
                    "best_times": ["08:00", "19:00"]
                },
                "is_active": True
            }
        }


class ContentGenerationRequest(BaseModel):
    """Request model for generating channel-specific content."""
    channel_element: str = Field(
        ...,
        pattern="^(air|water|fire|earth)$",
        description="Channel element (air, water, fire, earth)"
    )
    topic: str = Field(
        ...,
        min_length=10,
        max_length=500,
        description="Content topic/theme"
    )
    content_type: str = Field(
        ...,
        pattern="^(video_script|content_calendar|multi_channel_strategy)$",
        description="Type of content to generate"
    )
    product: Optional[str] = Field(
        None,
        description="Optional product to feature (for video scripts)"
    )
    include_product_link: bool = Field(
        default=False,
        description="Include product CTA (for video scripts)"
    )
    num_days: int = Field(
        default=7,
        ge=1,
        le=30,
        description="Number of days for content calendar"
    )
    include_topics: bool = Field(
        default=True,
        description="Include specific topics in calendar"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "channel_element": "air",
                "topic": "Quick deck building tips",
                "content_type": "video_script",
                "product": "Tournament Deck Box",
                "include_product_link": False
            }
        }


# ============================================================================
# Response Models
# ============================================================================

class ChannelResponse(BaseModel):
    """Response model for a single TikTok channel."""
    request_id: str = Field(
        ...,
        description="Unique identifier for the request"
    )
    channel: Dict[str, Any] = Field(
        ...,
        description="Channel information"
    )
    status: str = Field(
        default="success",
        description="Status of the request"
    )


class ChannelsListResponse(BaseModel):
    """Response model for list of TikTok channels."""
    request_id: str = Field(
        ...,
        description="Unique identifier for the request"
    )
    channels: List[Dict[str, Any]] = Field(
        ...,
        description="List of all channels"
    )
    total_channels: int = Field(
        ...,
        description="Total number of channels"
    )
    status: str = Field(
        default="success",
        description="Status of the request"
    )


class ChannelMutationResponse(BaseModel):
    """Response model for channel creation/update/deletion."""
    request_id: str = Field(
        ...,
        description="Unique identifier for the request"
    )
    message: str = Field(
        ...,
        description="Success message"
    )
    channel: Optional[Dict[str, Any]] = Field(
        None,
        description="Updated channel information"
    )
    status: str = Field(
        default="success",
        description="Status of the request"
    )


class ContentGenerationResponse(BaseModel):
    """Response model for content generation."""
    request_id: str = Field(
        ...,
        description="Unique identifier for the request"
    )
    content: str = Field(
        ...,
        description="The generated content"
    )
    file_path: str = Field(
        ...,
        description="Path where the content was saved"
    )
    metadata: Dict[str, Any] = Field(
        ...,
        description="Content metadata"
    )
    status: str = Field(
        default="success",
        description="Status of the request"
    )


# ============================================================================
# Route Handlers
# ============================================================================

@router.get("", response_model=ChannelsListResponse)
async def list_all_channels(
    request_id: str = Depends(get_request_id)
) -> ChannelsListResponse:
    """
    List all TikTok channels.

    Returns:
        ChannelsListResponse with all channels

    Raises:
        HTTPException: If retrieval fails
    """
    logger.info(f"[{request_id}] Listing all TikTok channels")

    try:
        # Initialize agent
        agent = TikTokChannelAgent()

        # Get all channels
        channels = agent.list_channels()

        # Create response
        response = ChannelsListResponse(
            request_id=request_id,
            channels=channels,
            total_channels=len(channels),
            status="success"
        )

        logger.info(f"[{request_id}] Successfully retrieved {len(channels)} channels")
        return response

    except Exception as e:
        logger.error(f"[{request_id}] Error listing channels: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list channels: {str(e)}"
        )


@router.get("/{channel_element}", response_model=ChannelResponse)
async def get_channel(
    channel_element: str,
    request_id: str = Depends(get_request_id)
) -> ChannelResponse:
    """
    Get a specific TikTok channel by element theme.

    Args:
        channel_element: Channel element (air, water, fire, earth)
        request_id: Unique request identifier

    Returns:
        ChannelResponse with channel details

    Raises:
        HTTPException: If channel not found or retrieval fails
    """
    logger.info(f"[{request_id}] Getting channel: element='{channel_element}'")

    try:
        # Initialize agent
        agent = TikTokChannelAgent()

        # Get channel
        channel = agent.get_channel(channel_element)

        # Create response
        response = ChannelResponse(
            request_id=request_id,
            channel=channel,
            status="success"
        )

        logger.info(f"[{request_id}] Successfully retrieved channel '{channel_element}'")
        return response

    except ValueError as e:
        logger.warning(f"[{request_id}] Channel not found: {e}")
        raise HTTPException(
            status_code=404,
            detail=f"Channel not found: {str(e)}"
        )
    except Exception as e:
        logger.error(f"[{request_id}] Error getting channel: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get channel: {str(e)}"
        )


@router.post("", response_model=ChannelMutationResponse)
async def create_channel(
    request: CreateChannelRequest,
    request_id: str = Depends(get_request_id)
) -> ChannelMutationResponse:
    """
    Create a new TikTok channel.

    Args:
        request: Channel creation request
        request_id: Unique request identifier

    Returns:
        ChannelMutationResponse with created channel

    Raises:
        HTTPException: If creation fails
    """
    logger.info(
        f"[{request_id}] Creating channel: "
        f"name='{request.channel_name}', element='{request.element_theme}'"
    )

    try:
        # Initialize agent
        agent = TikTokChannelAgent()

        # Create channel
        channel = agent.create_channel(
            channel_name=request.channel_name,
            element_theme=request.element_theme,
            description=request.description,
            target_audience=request.target_audience,
            posting_schedule=request.posting_schedule,
            branding_guidelines=request.branding_guidelines
        )

        # Create response
        response = ChannelMutationResponse(
            request_id=request_id,
            message=f"Channel '{request.channel_name}' created successfully",
            channel=channel,
            status="success"
        )

        logger.info(f"[{request_id}] Successfully created channel '{request.channel_name}'")
        return response

    except ValueError as e:
        logger.warning(f"[{request_id}] Invalid channel data: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Invalid channel data: {str(e)}"
        )
    except Exception as e:
        logger.error(f"[{request_id}] Error creating channel: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create channel: {str(e)}"
        )


@router.put("/{channel_element}", response_model=ChannelMutationResponse)
async def update_channel(
    channel_element: str,
    request: UpdateChannelRequest,
    request_id: str = Depends(get_request_id)
) -> ChannelMutationResponse:
    """
    Update a TikTok channel.

    Args:
        channel_element: Channel element (air, water, fire, earth)
        request: Channel update request
        request_id: Unique request identifier

    Returns:
        ChannelMutationResponse with updated channel

    Raises:
        HTTPException: If channel not found or update fails
    """
    logger.info(f"[{request_id}] Updating channel: element='{channel_element}'")

    try:
        # Initialize agent
        agent = TikTokChannelAgent()

        # Prepare updates (exclude None values)
        updates = {}
        if request.channel_name is not None:
            updates["channel_name"] = request.channel_name
        if request.description is not None:
            updates["description"] = request.description
        if request.target_audience is not None:
            updates["target_audience"] = request.target_audience
        if request.posting_schedule is not None:
            updates["posting_schedule"] = request.posting_schedule
        if request.branding_guidelines is not None:
            updates["branding_guidelines"] = request.branding_guidelines
        if request.is_active is not None:
            updates["is_active"] = request.is_active

        # Update channel
        updated_channel = agent.update_channel(channel_element, **updates)

        # Create response
        response = ChannelMutationResponse(
            request_id=request_id,
            message=f"Channel '{channel_element}' updated successfully",
            channel=updated_channel,
            status="success"
        )

        logger.info(f"[{request_id}] Successfully updated channel '{channel_element}'")
        return response

    except ValueError as e:
        logger.warning(f"[{request_id}] Channel not found or invalid data: {e}")
        raise HTTPException(
            status_code=404,
            detail=f"Channel not found or invalid data: {str(e)}"
        )
    except Exception as e:
        logger.error(f"[{request_id}] Error updating channel: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update channel: {str(e)}"
        )


@router.delete("/{channel_element}", response_model=ChannelMutationResponse)
async def deactivate_channel(
    channel_element: str,
    request_id: str = Depends(get_request_id)
) -> ChannelMutationResponse:
    """
    Deactivate a TikTok channel (soft delete).

    Args:
        channel_element: Channel element (air, water, fire, earth)
        request_id: Unique request identifier

    Returns:
        ChannelMutationResponse with deactivation confirmation

    Raises:
        HTTPException: If channel not found or deactivation fails
    """
    logger.info(f"[{request_id}] Deactivating channel: element='{channel_element}'")

    try:
        # Initialize agent
        agent = TikTokChannelAgent()

        # Deactivate channel by updating is_active to False
        updated_channel = agent.update_channel(channel_element, is_active=False)

        # Create response
        response = ChannelMutationResponse(
            request_id=request_id,
            message=f"Channel '{channel_element}' deactivated successfully",
            channel=updated_channel,
            status="success"
        )

        logger.info(f"[{request_id}] Successfully deactivated channel '{channel_element}'")
        return response

    except ValueError as e:
        logger.warning(f"[{request_id}] Channel not found: {e}")
        raise HTTPException(
            status_code=404,
            detail=f"Channel not found: {str(e)}"
        )
    except Exception as e:
        logger.error(f"[{request_id}] Error deactivating channel: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to deactivate channel: {str(e)}"
        )


@router.post("/content/generate", response_model=ContentGenerationResponse)
async def generate_channel_content(
    request: ContentGenerationRequest,
    request_id: str = Depends(get_request_id)
) -> ContentGenerationResponse:
    """
    Generate channel-specific content (video scripts, calendars, or multi-channel strategy).

    Args:
        request: Content generation request with channel element, topic, and content type
        request_id: Unique request identifier

    Returns:
        ContentGenerationResponse with generated content and file path

    Raises:
        HTTPException: If generation fails or channel not found
    """
    logger.info(
        f"[{request_id}] Generating content: "
        f"channel='{request.channel_element}', topic='{request.topic}', "
        f"type='{request.content_type}'"
    )

    try:
        # Initialize agent
        agent = TikTokChannelAgent()

        # Generate content based on content_type
        if request.content_type == "video_script":
            content, file_path = agent.generate_channel_video_script(
                channel_element=request.channel_element,
                topic=request.topic,
                product=request.product,
                include_product_link=request.include_product_link
            )
            metadata = {
                "content_type": "video_script",
                "channel_element": request.channel_element,
                "topic": request.topic,
                "product": request.product,
                "include_product_link": request.include_product_link
            }

        elif request.content_type == "content_calendar":
            content, file_path = agent.generate_channel_content_calendar(
                channel_element=request.channel_element,
                num_days=request.num_days,
                include_topics=request.include_topics
            )
            metadata = {
                "content_type": "content_calendar",
                "channel_element": request.channel_element,
                "num_days": request.num_days,
                "include_topics": request.include_topics
            }

        elif request.content_type == "multi_channel_strategy":
            content, file_path = agent.generate_multi_channel_strategy(
                time_period="weekly"
            )
            metadata = {
                "content_type": "multi_channel_strategy",
                "time_period": "weekly"
            }

        else:
            raise ValueError(f"Unknown content_type: {request.content_type}")

        # Create response
        response = ContentGenerationResponse(
            request_id=request_id,
            content=content,
            file_path=str(file_path),
            metadata=metadata,
            status="success"
        )

        logger.info(
            f"[{request_id}] Successfully generated {request.content_type} "
            f"for '{request.channel_element}': {file_path}"
        )
        return response

    except ValueError as e:
        logger.warning(f"[{request_id}] Invalid request: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Invalid request: {str(e)}"
        )
    except Exception as e:
        logger.error(f"[{request_id}] Error generating content: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate content: {str(e)}"
        )
