"""
SEO analysis and optimization routes.

This module defines API endpoints for SEO analysis, keyword research,
and internal linking suggestions using the SEOAgent.
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
import logging
import time

from api.dependencies import get_request_id
from api.models import (
    SEOAnalysisRequest,
    SEOAnalysisResponse,
    KeywordResearchRequest,
    ContentMetadata,
    ErrorResponse,
    KeywordMetrics,
    SEOScore,
    SEORecommendation
)
from pydantic import BaseModel, Field
from agents.seo_agent import SEOAgent

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/seo",
    tags=["seo"],
    responses={
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)


# ============================================================================
# Request Models
# ============================================================================

class ContentAnalysisRequest(BaseModel):
    """Request model for SEO content analysis."""
    content: str = Field(
        ...,
        min_length=50,
        max_length=50000,
        description="Content to analyze for SEO"
    )
    target_keyword: Optional[str] = Field(
        None,
        description="Primary target keyword to analyze for"
    )
    title: Optional[str] = Field(
        None,
        description="Content title (extracted from content if not provided)"
    )
    include_recommendations: bool = Field(
        default=True,
        description="Whether to include optimization recommendations"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "content": "# Tactical Backpacks for Urban Professionals\n\nDiscover the best tactical backpacks...",
                "target_keyword": "tactical backpack",
                "title": "Tactical Backpacks for Urban Professionals",
                "include_recommendations": True
            }
        }


class InternalLinksRequest(BaseModel):
    """Request model for internal linking suggestions."""
    content: str = Field(
        ...,
        min_length=50,
        max_length=50000,
        description="Content to analyze for internal linking"
    )
    title: str = Field(
        ...,
        min_length=5,
        max_length=500,
        description="Content title"
    )
    content_pillar: Optional[str] = Field(
        None,
        description="Content pillar for relevance matching"
    )
    max_suggestions: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Maximum number of link suggestions"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "content": "# Tactical Backpacks Guide\n\nLearn about choosing the right tactical backpack...",
                "title": "Complete Guide to Tactical Backpacks",
                "content_pillar": "Gear & Equipment",
                "max_suggestions": 5
            }
        }


# ============================================================================
# Response Models
# ============================================================================

class SEOAnalysisDetailedResponse(BaseModel):
    """Response model for detailed SEO analysis."""
    request_id: str = Field(
        ...,
        description="Unique identifier for the request"
    )
    seo_score: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Overall SEO score (0-100)"
    )
    grade: str = Field(
        ...,
        description="Letter grade (A-F)"
    )
    keyword_optimization: Dict[str, Any] = Field(
        ...,
        description="Keyword optimization details"
    )
    content_quality: Dict[str, Any] = Field(
        ...,
        description="Content quality metrics"
    )
    structure: Dict[str, Any] = Field(
        ...,
        description="Content structure analysis"
    )
    readability: Dict[str, Any] = Field(
        ...,
        description="Readability metrics"
    )
    recommendations: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="SEO optimization recommendations"
    )
    issues: List[str] = Field(
        default_factory=list,
        description="List of SEO issues found"
    )
    metadata: ContentMetadata = Field(
        ...,
        description="Metadata about the analysis process"
    )
    status: str = Field(
        default="success",
        description="Status of the analysis"
    )


class KeywordResearchResponse(BaseModel):
    """Response model for keyword research."""
    request_id: str = Field(
        ...,
        description="Unique identifier for the request"
    )
    keywords: List[Dict[str, Any]] = Field(
        ...,
        description="List of keyword suggestions with metrics"
    )
    seed_keywords: List[str] = Field(
        ...,
        description="Original seed keywords used"
    )
    topic: str = Field(
        ...,
        description="Topic used for research"
    )
    metadata: ContentMetadata = Field(
        ...,
        description="Metadata about the research process"
    )
    status: str = Field(
        default="success",
        description="Status of the research"
    )


class InternalLinksResponse(BaseModel):
    """Response model for internal linking suggestions."""
    request_id: str = Field(
        ...,
        description="Unique identifier for the request"
    )
    suggestions: List[Dict[str, Any]] = Field(
        ...,
        description="List of internal link suggestions"
    )
    total_suggestions: int = Field(
        ...,
        description="Total number of suggestions"
    )
    content_title: str = Field(
        ...,
        description="Title of content being analyzed"
    )
    metadata: ContentMetadata = Field(
        ...,
        description="Metadata about the analysis process"
    )
    status: str = Field(
        default="success",
        description="Status of the analysis"
    )


# ============================================================================
# Route Handlers
# ============================================================================

@router.post(
    "/analyze",
    response_model=SEOAnalysisDetailedResponse,
    summary="Analyze content for SEO",
    description="Performs comprehensive SEO analysis on provided content"
)
async def analyze_content_seo(
    request: ContentAnalysisRequest,
    request_id: str = Depends(get_request_id)
) -> SEOAnalysisDetailedResponse:
    """
    Analyze content for SEO optimization.

    Args:
        request: Content analysis request with content and target keyword
        request_id: Unique request identifier from dependency

    Returns:
        Detailed SEO analysis with scores, recommendations, and issues

    Raises:
        HTTPException: If analysis fails
    """
    start_time = time.time()
    logger.info(f"[{request_id}] Starting SEO content analysis")

    try:
        # Initialize SEO agent
        seo_agent = SEOAgent()

        # Extract title from content if not provided
        title = request.title
        if not title:
            # Extract from first heading
            lines = request.content.split('\n')
            for line in lines:
                if line.strip().startswith('#'):
                    title = line.strip().lstrip('#').strip()
                    break
            if not title:
                title = "Untitled Content"

        # Prepare analysis input
        content_data = {
            'title': title,
            'content': request.content,
            'target_keyword': request.target_keyword or ""
        }

        # Perform SEO analysis
        logger.info(f"[{request_id}] Analyzing content with target keyword: {request.target_keyword}")
        analysis_result = seo_agent.analyze_content_seo(content_data)

        # Calculate generation time
        generation_time_ms = int((time.time() - start_time) * 1000)

        # Build metadata
        metadata = ContentMetadata(
            agent="seo_agent",
            model="claude-sonnet-4-5-20250929",
            tokens_used=0,  # Not tracked for analysis
            generation_time_ms=generation_time_ms,
            timestamp=datetime.utcnow()
        )

        # Build response
        response = SEOAnalysisDetailedResponse(
            request_id=request_id,
            seo_score=analysis_result.get('total_score', 0.0),
            grade=analysis_result.get('grade', 'F'),
            keyword_optimization=analysis_result.get('keyword_optimization', {}),
            content_quality=analysis_result.get('content_quality', {}),
            structure=analysis_result.get('content_structure', {}),
            readability=analysis_result.get('readability', {}),
            recommendations=analysis_result.get('recommendations', []) if request.include_recommendations else [],
            issues=analysis_result.get('issues', []),
            metadata=metadata,
            status="success"
        )

        logger.info(
            f"[{request_id}] SEO analysis completed - "
            f"Score: {response.seo_score:.1f}, Grade: {response.grade}, "
            f"Time: {generation_time_ms}ms"
        )

        return response

    except Exception as e:
        logger.error(f"[{request_id}] SEO analysis failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"SEO analysis failed: {str(e)}"
        )


@router.post(
    "/keywords/research",
    response_model=KeywordResearchResponse,
    summary="Research keywords for a topic",
    description="Performs AI-powered keyword research and returns suggestions"
)
async def research_keywords(
    request: KeywordResearchRequest,
    request_id: str = Depends(get_request_id)
) -> KeywordResearchResponse:
    """
    Research keywords for a given topic.

    Args:
        request: Keyword research request with seed keywords and topic
        request_id: Unique request identifier from dependency

    Returns:
        Keyword suggestions with metrics and relevance scores

    Raises:
        HTTPException: If research fails
    """
    start_time = time.time()
    logger.info(
        f"[{request_id}] Starting keyword research - "
        f"Topic: {request.topic}, Seeds: {request.seed_keywords}"
    )

    try:
        # Initialize SEO agent
        seo_agent = SEOAgent()

        # Perform keyword research
        keywords = seo_agent.research_keywords(
            topic=request.topic,
            seed_keywords=request.seed_keywords,
            max_keywords=request.max_keywords
        )

        # Calculate generation time
        generation_time_ms = int((time.time() - start_time) * 1000)

        # Build metadata
        metadata = ContentMetadata(
            agent="seo_agent",
            model="claude-sonnet-4-5-20250929",
            tokens_used=0,  # Not tracked for research
            generation_time_ms=generation_time_ms,
            timestamp=datetime.utcnow()
        )

        # Build response
        response = KeywordResearchResponse(
            request_id=request_id,
            keywords=keywords,
            seed_keywords=request.seed_keywords,
            topic=request.topic,
            metadata=metadata,
            status="success"
        )

        logger.info(
            f"[{request_id}] Keyword research completed - "
            f"Found {len(keywords)} keywords in {generation_time_ms}ms"
        )

        return response

    except Exception as e:
        logger.error(f"[{request_id}] Keyword research failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Keyword research failed: {str(e)}"
        )


@router.post(
    "/internal-links/suggest",
    response_model=InternalLinksResponse,
    summary="Get internal linking suggestions",
    description="Analyzes content and suggests relevant internal links to existing content"
)
async def suggest_internal_links(
    request: InternalLinksRequest,
    request_id: str = Depends(get_request_id)
) -> InternalLinksResponse:
    """
    Suggest internal links for content.

    Args:
        request: Internal linking request with content and title
        request_id: Unique request identifier from dependency

    Returns:
        List of internal linking suggestions with relevance scores

    Raises:
        HTTPException: If suggestion generation fails
    """
    start_time = time.time()
    logger.info(f"[{request_id}] Starting internal link suggestion for: {request.title}")

    try:
        # Initialize SEO agent
        seo_agent = SEOAgent()

        # Get internal link suggestions
        suggestions = seo_agent.suggest_internal_links(
            content=request.content,
            title=request.title,
            content_pillar=request.content_pillar
        )

        # Limit to max_suggestions
        limited_suggestions = suggestions[:request.max_suggestions]

        # Calculate generation time
        generation_time_ms = int((time.time() - start_time) * 1000)

        # Build metadata
        metadata = ContentMetadata(
            agent="seo_agent",
            model="claude-sonnet-4-5-20250929",
            tokens_used=0,  # Not tracked for suggestions
            generation_time_ms=generation_time_ms,
            timestamp=datetime.utcnow()
        )

        # Build response
        response = InternalLinksResponse(
            request_id=request_id,
            suggestions=limited_suggestions,
            total_suggestions=len(limited_suggestions),
            content_title=request.title,
            metadata=metadata,
            status="success"
        )

        logger.info(
            f"[{request_id}] Internal link suggestions completed - "
            f"Found {len(limited_suggestions)} suggestions in {generation_time_ms}ms"
        )

        return response

    except Exception as e:
        logger.error(f"[{request_id}] Internal link suggestion failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal link suggestion failed: {str(e)}"
        )


@router.get(
    "/health",
    summary="SEO service health check",
    description="Check if SEO service is operational"
)
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint for SEO service.

    Returns:
        Dict containing service health status
    """
    return {
        "service": "seo",
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
