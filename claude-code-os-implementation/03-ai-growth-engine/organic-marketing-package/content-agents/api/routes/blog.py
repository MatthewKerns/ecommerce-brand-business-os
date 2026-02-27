"""
Blog content generation routes.

This module defines API endpoints for blog content generation using the BlogAgent.
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
from agents.blog_agent import BlogAgent

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/blog",
    tags=["blog"],
    responses={
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)


# ============================================================================
# Request Models
# ============================================================================

class BlogPostRequest(BaseModel):
    """Request model for blog post generation."""
    topic: str = Field(
        ...,
        min_length=10,
        max_length=500,
        description="The blog post topic"
    )
    content_pillar: Optional[str] = Field(
        None,
        description="Content pillar (Battle-Ready Lifestyle, Gear & Equipment, etc.)"
    )
    target_keywords: Optional[List[str]] = Field(
        default_factory=list,
        description="SEO keywords to target"
    )
    target_keyword: Optional[str] = Field(
        None,
        max_length=100,
        description="Primary target keyword for SEO optimization"
    )
    word_count: int = Field(
        default=1000,
        ge=300,
        le=5000,
        description="Target word count"
    )
    include_cta: bool = Field(
        default=True,
        description="Whether to include a call-to-action"
    )
    include_seo_analysis: bool = Field(
        default=False,
        description="Whether to include SEO analysis with the content"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "topic": "How to Organize Your Trading Card Collection",
                "content_pillar": "Gear & Equipment",
                "target_keywords": ["trading card storage", "card organization", "TCG collection"],
                "target_keyword": "trading card storage",
                "word_count": 1500,
                "include_cta": True,
                "include_seo_analysis": True
            }
        }


class BlogSeriesRequest(BaseModel):
    """Request model for blog series generation."""
    series_topic: str = Field(
        ...,
        min_length=10,
        max_length=500,
        description="The overarching series topic"
    )
    num_posts: int = Field(
        default=3,
        ge=2,
        le=10,
        description="Number of posts in the series"
    )
    content_pillar: Optional[str] = Field(
        None,
        description="Content pillar for the series"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "series_topic": "Complete Guide to Tournament Preparation",
                "num_posts": 5,
                "content_pillar": "Battle-Ready Lifestyle"
            }
        }


class ListicleRequest(BaseModel):
    """Request model for listicle generation."""
    topic: str = Field(
        ...,
        min_length=10,
        max_length=500,
        description="The listicle topic"
    )
    num_items: int = Field(
        default=10,
        ge=3,
        le=25,
        description="Number of items in the list"
    )
    content_pillar: Optional[str] = Field(
        None,
        description="Content pillar"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "topic": "Essential Accessories Every TCG Player Needs",
                "num_items": 10,
                "content_pillar": "Gear & Equipment"
            }
        }


class HowToGuideRequest(BaseModel):
    """Request model for how-to guide generation."""
    topic: str = Field(
        ...,
        min_length=10,
        max_length=500,
        description="The how-to topic"
    )
    target_audience: str = Field(
        default="Tournament players",
        description="Target reader audience"
    )
    difficulty_level: str = Field(
        default="beginner",
        pattern="^(beginner|intermediate|advanced)$",
        description="Difficulty level"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "topic": "How to Double Sleeve Your Trading Cards",
                "target_audience": "Competitive players",
                "difficulty_level": "beginner"
            }
        }


# ============================================================================
# Response Models
# ============================================================================

class BlogContentResponse(BaseModel):
    """Response model for blog content generation."""
    request_id: str = Field(
        ...,
        description="Unique identifier for the request"
    )
    content: str = Field(
        ...,
        description="The generated blog content"
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


class BlogSeriesResponse(BaseModel):
    """Response model for blog series generation."""
    request_id: str = Field(
        ...,
        description="Unique identifier for the request"
    )
    outline: str = Field(
        ...,
        description="The generated series outline"
    )
    file_path: str = Field(
        ...,
        description="Path where the outline was saved"
    )
    num_posts: int = Field(
        ...,
        description="Number of posts in the series"
    )
    metadata: ContentMetadata = Field(
        ...,
        description="Metadata about the generation process"
    )
    status: str = Field(
        default="success",
        description="Status of the content generation"
    )


# ============================================================================
# Endpoints
# ============================================================================

@router.post(
    "/generate",
    response_model=BlogContentResponse,
    summary="Generate a blog post",
    description="Generate a complete SEO-optimized blog post on the specified topic"
)
async def generate_blog_post(
    request: BlogPostRequest,
    request_id: str = Depends(get_request_id)
) -> Dict[str, Any]:
    """
    Generate a blog post.

    Args:
        request: Blog post generation request
        request_id: Unique request identifier

    Returns:
        Blog content response with generated content and metadata

    Raises:
        HTTPException: If content generation fails
    """
    logger.info(f"[{request_id}] Generating blog post: topic='{request.topic}'")
    start_time = time.time()

    try:
        # Initialize agent
        agent = BlogAgent()

        # Generate blog post
        content, file_path, seo_analysis = agent.generate_blog_post(
            topic=request.topic,
            content_pillar=request.content_pillar,
            target_keywords=request.target_keywords if request.target_keywords else None,
            word_count=request.word_count,
            include_cta=request.include_cta,
            include_seo_analysis=request.include_seo_analysis
        )

        # Calculate generation time
        generation_time_ms = int((time.time() - start_time) * 1000)

        # Build response
        response = {
            "request_id": request_id,
            "content": content,
            "file_path": str(file_path),
            "metadata": {
                "agent": "blog_agent",
                "model": "claude-sonnet-4-5-20250929",
                "tokens_used": 0,  # TODO: Implement token tracking
                "generation_time_ms": generation_time_ms,
                "timestamp": datetime.utcnow()
            },
            "status": "success"
        }

        # Add SEO data to response if analysis was performed
        if seo_analysis:
            response["seo_score"] = seo_analysis.get("total_score", 0.0)
            response["seo_grade"] = seo_analysis.get("grade", "N/A")

            # Generate and include meta description
            meta_description = agent.generate_meta_description(content)
            response["meta_description"] = meta_description

            # Include full SEO analysis details
            response["seo_analysis"] = {
                "score": seo_analysis.get("total_score", 0.0),
                "grade": seo_analysis.get("grade", "N/A"),
                "word_count": seo_analysis.get("word_count", 0),
                "keyword_optimization": seo_analysis.get("keyword_optimization", {}),
                "content_quality": seo_analysis.get("content_quality", {}),
                "structure": seo_analysis.get("content_structure", {}),
                "readability": seo_analysis.get("readability", {}),
                "issues": seo_analysis.get("issues", []),
                "recommendations": seo_analysis.get("recommendations", [])
            }

        logger.info(f"[{request_id}] Successfully generated blog post in {generation_time_ms}ms")
        return response

    except Exception as e:
        logger.error(f"[{request_id}] Error generating blog post: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "BlogGenerationError",
                "message": f"Failed to generate blog post: {str(e)}",
                "request_id": request_id,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        )


@router.post(
    "/series",
    response_model=BlogSeriesResponse,
    summary="Generate a blog series outline",
    description="Generate an outline for a multi-part blog series"
)
async def generate_blog_series(
    request: BlogSeriesRequest,
    request_id: str = Depends(get_request_id)
) -> Dict[str, Any]:
    """
    Generate a blog series outline.

    Args:
        request: Blog series generation request
        request_id: Unique request identifier

    Returns:
        Blog series response with outline and metadata

    Raises:
        HTTPException: If content generation fails
    """
    logger.info(f"[{request_id}] Generating blog series: topic='{request.series_topic}', num_posts={request.num_posts}")
    start_time = time.time()

    try:
        # Initialize agent
        agent = BlogAgent()

        # Generate blog series outline
        results = agent.generate_blog_series(
            series_topic=request.series_topic,
            num_posts=request.num_posts,
            content_pillar=request.content_pillar
        )

        # Extract outline and path (returns list with one tuple)
        outline, file_path = results[0]

        # Calculate generation time
        generation_time_ms = int((time.time() - start_time) * 1000)

        # Build response
        response = {
            "request_id": request_id,
            "outline": outline,
            "file_path": str(file_path),
            "num_posts": request.num_posts,
            "metadata": {
                "agent": "blog_agent",
                "model": "claude-sonnet-4-5-20250929",
                "tokens_used": 0,  # TODO: Implement token tracking
                "generation_time_ms": generation_time_ms,
                "timestamp": datetime.utcnow()
            },
            "status": "success"
        }

        logger.info(f"[{request_id}] Successfully generated blog series outline in {generation_time_ms}ms")
        return response

    except Exception as e:
        logger.error(f"[{request_id}] Error generating blog series: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "BlogSeriesGenerationError",
                "message": f"Failed to generate blog series: {str(e)}",
                "request_id": request_id,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        )


@router.post(
    "/listicle",
    response_model=BlogContentResponse,
    summary="Generate a listicle blog post",
    description="Generate a listicle-style blog post with numbered items"
)
async def generate_listicle(
    request: ListicleRequest,
    request_id: str = Depends(get_request_id)
) -> Dict[str, Any]:
    """
    Generate a listicle blog post.

    Args:
        request: Listicle generation request
        request_id: Unique request identifier

    Returns:
        Blog content response with generated listicle and metadata

    Raises:
        HTTPException: If content generation fails
    """
    logger.info(f"[{request_id}] Generating listicle: topic='{request.topic}', num_items={request.num_items}")
    start_time = time.time()

    try:
        # Initialize agent
        agent = BlogAgent()

        # Generate listicle
        content, file_path = agent.generate_listicle(
            topic=request.topic,
            num_items=request.num_items,
            content_pillar=request.content_pillar
        )

        # Calculate generation time
        generation_time_ms = int((time.time() - start_time) * 1000)

        # Build response
        response = {
            "request_id": request_id,
            "content": content,
            "file_path": str(file_path),
            "metadata": {
                "agent": "blog_agent",
                "model": "claude-sonnet-4-5-20250929",
                "tokens_used": 0,  # TODO: Implement token tracking
                "generation_time_ms": generation_time_ms,
                "timestamp": datetime.utcnow()
            },
            "status": "success"
        }

        logger.info(f"[{request_id}] Successfully generated listicle in {generation_time_ms}ms")
        return response

    except Exception as e:
        logger.error(f"[{request_id}] Error generating listicle: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "ListicleGenerationError",
                "message": f"Failed to generate listicle: {str(e)}",
                "request_id": request_id,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        )


@router.post(
    "/how-to",
    response_model=BlogContentResponse,
    summary="Generate a how-to guide",
    description="Generate a step-by-step how-to guide blog post"
)
async def generate_how_to_guide(
    request: HowToGuideRequest,
    request_id: str = Depends(get_request_id)
) -> Dict[str, Any]:
    """
    Generate a how-to guide blog post.

    Args:
        request: How-to guide generation request
        request_id: Unique request identifier

    Returns:
        Blog content response with generated guide and metadata

    Raises:
        HTTPException: If content generation fails
    """
    logger.info(f"[{request_id}] Generating how-to guide: topic='{request.topic}', level={request.difficulty_level}")
    start_time = time.time()

    try:
        # Initialize agent
        agent = BlogAgent()

        # Generate how-to guide
        content, file_path = agent.generate_how_to_guide(
            topic=request.topic,
            target_audience=request.target_audience,
            difficulty_level=request.difficulty_level
        )

        # Calculate generation time
        generation_time_ms = int((time.time() - start_time) * 1000)

        # Build response
        response = {
            "request_id": request_id,
            "content": content,
            "file_path": str(file_path),
            "metadata": {
                "agent": "blog_agent",
                "model": "claude-sonnet-4-5-20250929",
                "tokens_used": 0,  # TODO: Implement token tracking
                "generation_time_ms": generation_time_ms,
                "timestamp": datetime.utcnow()
            },
            "status": "success"
        }

        logger.info(f"[{request_id}] Successfully generated how-to guide in {generation_time_ms}ms")
        return response

    except Exception as e:
        logger.error(f"[{request_id}] Error generating how-to guide: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "HowToGuideGenerationError",
                "message": f"Failed to generate how-to guide: {str(e)}",
                "request_id": request_id,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        )
