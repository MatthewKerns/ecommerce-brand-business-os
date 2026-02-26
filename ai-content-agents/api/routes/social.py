"""
Social media content generation routes.

This module defines API endpoints for social media content generation using the SocialAgent.
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
import logging
import time

from api.dependencies import get_request_id
from api.models import ContentResponse, ContentMetadata, ErrorResponse
from pydantic import BaseModel, Field
from agents.social_agent import SocialAgent

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/social",
    tags=["social"],
    responses={
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)


# ============================================================================
# Request Models
# ============================================================================

class InstagramPostRequest(BaseModel):
    """Request model for Instagram post generation."""
    topic: str = Field(
        ...,
        min_length=10,
        max_length=500,
        description="Post topic/theme"
    )
    content_pillar: Optional[str] = Field(
        None,
        description="Content pillar alignment"
    )
    image_description: Optional[str] = Field(
        None,
        description="Description of the accompanying image"
    )
    include_hashtags: bool = Field(
        default=True,
        description="Whether to include hashtags"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "topic": "Tournament preparation checklist for TCG players",
                "content_pillar": "Battle-Ready Lifestyle",
                "image_description": "Player organizing cards in Infinity Vault binder",
                "include_hashtags": True
            }
        }


class RedditPostRequest(BaseModel):
    """Request model for Reddit post generation."""
    subreddit: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Target subreddit (without r/)"
    )
    topic: str = Field(
        ...,
        min_length=10,
        max_length=500,
        description="Post topic"
    )
    post_type: str = Field(
        default="discussion",
        pattern="^(discussion|question|guide|showcase)$",
        description="Type of Reddit post"
    )
    include_product_mention: bool = Field(
        default=False,
        description="Whether to subtly mention products"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "subreddit": "PokemonTCG",
                "topic": "Best practices for storing rare cards long-term",
                "post_type": "guide",
                "include_product_mention": False
            }
        }


class ContentCalendarRequest(BaseModel):
    """Request model for content calendar generation."""
    platform: str = Field(
        ...,
        pattern="^(instagram|reddit|discord|twitter)$",
        description="Platform for content calendar"
    )
    num_days: int = Field(
        default=7,
        ge=1,
        le=30,
        description="Number of days to plan"
    )
    content_pillar: Optional[str] = Field(
        None,
        description="Focus on specific pillar or mix"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "platform": "instagram",
                "num_days": 7,
                "content_pillar": "Gear & Equipment"
            }
        }


class CarouselScriptRequest(BaseModel):
    """Request model for Instagram carousel generation."""
    topic: str = Field(
        ...,
        min_length=10,
        max_length=500,
        description="Carousel topic"
    )
    num_slides: int = Field(
        default=10,
        ge=3,
        le=10,
        description="Number of slides"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "topic": "10 Must-Have Accessories for Tournament Players",
                "num_slides": 10
            }
        }


class BatchPostsRequest(BaseModel):
    """Request model for batch post generation."""
    platform: str = Field(
        ...,
        pattern="^(instagram|reddit)$",
        description="Platform to generate for"
    )
    num_posts: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Number of posts to generate"
    )
    content_mix: Optional[List[str]] = Field(
        None,
        description="List of content pillars to cycle through"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "platform": "instagram",
                "num_posts": 5,
                "content_mix": ["Battle-Ready Lifestyle", "Gear & Equipment"]
            }
        }


# ============================================================================
# Response Models
# ============================================================================

class SocialContentResponse(BaseModel):
    """Response model for social content generation."""
    request_id: str = Field(
        ...,
        description="Unique identifier for the request"
    )
    content: str = Field(
        ...,
        description="The generated social content"
    )
    file_path: str = Field(
        ...,
        description="Path where the content was saved"
    )
    metadata: ContentMetadata = Field(
        ...,
        description="Metadata about the generation process"
    )
    status: str = Field(
        default="success",
        description="Status of the content generation"
    )


class BatchPostsResponse(BaseModel):
    """Response model for batch post generation."""
    request_id: str = Field(
        ...,
        description="Unique identifier for the request"
    )
    posts: List[Dict[str, str]] = Field(
        ...,
        description="List of generated posts with content and file paths"
    )
    total_generated: int = Field(
        ...,
        description="Total number of posts generated"
    )
    metadata: ContentMetadata = Field(
        ...,
        description="Metadata about the generation process"
    )
    status: str = Field(
        default="success",
        description="Status of the batch generation"
    )


# ============================================================================
# Route Handlers
# ============================================================================

@router.post("/instagram", response_model=SocialContentResponse)
async def generate_instagram_post(
    request: InstagramPostRequest,
    request_id: str = Depends(get_request_id)
) -> SocialContentResponse:
    """
    Generate an Instagram post with caption and hashtags.

    Args:
        request: Instagram post generation request
        request_id: Unique request identifier

    Returns:
        SocialContentResponse with generated content

    Raises:
        HTTPException: If generation fails
    """
    logger.info(f"[{request_id}] Generating Instagram post: topic='{request.topic}'")

    try:
        start_time = time.time()

        # Initialize agent
        agent = SocialAgent()

        # Generate Instagram post
        content, file_path = agent.generate_instagram_post(
            topic=request.topic,
            content_pillar=request.content_pillar,
            image_description=request.image_description,
            include_hashtags=request.include_hashtags
        )

        generation_time = int((time.time() - start_time) * 1000)

        # Create response
        response = SocialContentResponse(
            request_id=request_id,
            content=content,
            file_path=str(file_path),
            metadata=ContentMetadata(
                agent="social_agent",
                model="claude-sonnet-4-5-20250929",
                tokens_used=0,  # Would need to track from agent
                generation_time_ms=generation_time,
                timestamp=datetime.utcnow()
            ),
            status="success"
        )

        logger.info(f"[{request_id}] Successfully generated Instagram post in {generation_time}ms")
        return response

    except Exception as e:
        logger.error(f"[{request_id}] Error generating Instagram post: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate Instagram post: {str(e)}"
        )


@router.post("/reddit", response_model=SocialContentResponse)
async def generate_reddit_post(
    request: RedditPostRequest,
    request_id: str = Depends(get_request_id)
) -> SocialContentResponse:
    """
    Generate a Reddit post with title and body.

    Args:
        request: Reddit post generation request
        request_id: Unique request identifier

    Returns:
        SocialContentResponse with generated content

    Raises:
        HTTPException: If generation fails
    """
    logger.info(f"[{request_id}] Generating Reddit post: subreddit=r/{request.subreddit}, topic='{request.topic}'")

    try:
        start_time = time.time()

        # Initialize agent
        agent = SocialAgent()

        # Generate Reddit post
        content, file_path = agent.generate_reddit_post(
            subreddit=request.subreddit,
            topic=request.topic,
            post_type=request.post_type,
            include_product_mention=request.include_product_mention
        )

        generation_time = int((time.time() - start_time) * 1000)

        # Create response
        response = SocialContentResponse(
            request_id=request_id,
            content=content,
            file_path=str(file_path),
            metadata=ContentMetadata(
                agent="social_agent",
                model="claude-sonnet-4-5-20250929",
                tokens_used=0,
                generation_time_ms=generation_time,
                timestamp=datetime.utcnow()
            ),
            status="success"
        )

        logger.info(f"[{request_id}] Successfully generated Reddit post in {generation_time}ms")
        return response

    except Exception as e:
        logger.error(f"[{request_id}] Error generating Reddit post: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate Reddit post: {str(e)}"
        )


@router.post("/calendar", response_model=SocialContentResponse)
async def generate_content_calendar(
    request: ContentCalendarRequest,
    request_id: str = Depends(get_request_id)
) -> SocialContentResponse:
    """
    Generate a content calendar for a platform.

    Args:
        request: Content calendar generation request
        request_id: Unique request identifier

    Returns:
        SocialContentResponse with generated calendar

    Raises:
        HTTPException: If generation fails
    """
    logger.info(f"[{request_id}] Generating {request.num_days}-day content calendar for {request.platform}")

    try:
        start_time = time.time()

        # Initialize agent
        agent = SocialAgent()

        # Generate content calendar
        content, file_path = agent.generate_content_calendar(
            platform=request.platform,
            num_days=request.num_days,
            content_pillar=request.content_pillar
        )

        generation_time = int((time.time() - start_time) * 1000)

        # Create response
        response = SocialContentResponse(
            request_id=request_id,
            content=content,
            file_path=str(file_path),
            metadata=ContentMetadata(
                agent="social_agent",
                model="claude-sonnet-4-5-20250929",
                tokens_used=0,
                generation_time_ms=generation_time,
                timestamp=datetime.utcnow()
            ),
            status="success"
        )

        logger.info(f"[{request_id}] Successfully generated content calendar in {generation_time}ms")
        return response

    except Exception as e:
        logger.error(f"[{request_id}] Error generating content calendar: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate content calendar: {str(e)}"
        )


@router.post("/carousel", response_model=SocialContentResponse)
async def generate_carousel_script(
    request: CarouselScriptRequest,
    request_id: str = Depends(get_request_id)
) -> SocialContentResponse:
    """
    Generate an Instagram carousel script.

    Args:
        request: Carousel script generation request
        request_id: Unique request identifier

    Returns:
        SocialContentResponse with generated script

    Raises:
        HTTPException: If generation fails
    """
    logger.info(f"[{request_id}] Generating carousel script: topic='{request.topic}', slides={request.num_slides}")

    try:
        start_time = time.time()

        # Initialize agent
        agent = SocialAgent()

        # Generate carousel script
        content, file_path = agent.generate_carousel_script(
            topic=request.topic,
            num_slides=request.num_slides
        )

        generation_time = int((time.time() - start_time) * 1000)

        # Create response
        response = SocialContentResponse(
            request_id=request_id,
            content=content,
            file_path=str(file_path),
            metadata=ContentMetadata(
                agent="social_agent",
                model="claude-sonnet-4-5-20250929",
                tokens_used=0,
                generation_time_ms=generation_time,
                timestamp=datetime.utcnow()
            ),
            status="success"
        )

        logger.info(f"[{request_id}] Successfully generated carousel script in {generation_time}ms")
        return response

    except Exception as e:
        logger.error(f"[{request_id}] Error generating carousel script: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate carousel script: {str(e)}"
        )


@router.post("/batch", response_model=BatchPostsResponse)
async def batch_generate_posts(
    request: BatchPostsRequest,
    request_id: str = Depends(get_request_id)
) -> BatchPostsResponse:
    """
    Batch generate multiple posts for a platform.

    Args:
        request: Batch posts generation request
        request_id: Unique request identifier

    Returns:
        BatchPostsResponse with generated posts

    Raises:
        HTTPException: If generation fails
    """
    logger.info(f"[{request_id}] Batch generating {request.num_posts} posts for {request.platform}")

    try:
        start_time = time.time()

        # Initialize agent
        agent = SocialAgent()

        # Batch generate posts
        results = agent.batch_generate_posts(
            platform=request.platform,
            num_posts=request.num_posts,
            content_mix=request.content_mix
        )

        generation_time = int((time.time() - start_time) * 1000)

        # Format results
        posts = [
            {"content": content, "file_path": str(file_path)}
            for content, file_path in results
        ]

        # Create response
        response = BatchPostsResponse(
            request_id=request_id,
            posts=posts,
            total_generated=len(posts),
            metadata=ContentMetadata(
                agent="social_agent",
                model="claude-sonnet-4-5-20250929",
                tokens_used=0,
                generation_time_ms=generation_time,
                timestamp=datetime.utcnow()
            ),
            status="success"
        )

        logger.info(f"[{request_id}] Successfully generated {len(posts)} posts in {generation_time}ms")
        return response

    except Exception as e:
        logger.error(f"[{request_id}] Error batch generating posts: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to batch generate posts: {str(e)}"
        )
