"""
Competitor analysis routes.

This module defines API endpoints for competitor analysis using the CompetitorAgent.
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
from agents.competitor_agent import CompetitorAgent

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/competitor",
    tags=["competitor"],
    responses={
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)


# ============================================================================
# Request Models
# ============================================================================

class CompetitorListingRequest(BaseModel):
    """Request model for competitor listing analysis."""
    competitor_name: str = Field(
        ...,
        min_length=2,
        max_length=200,
        description="Competitor brand name"
    )
    product_title: str = Field(
        ...,
        min_length=10,
        max_length=500,
        description="Their product title"
    )
    bullet_points: List[str] = Field(
        ...,
        min_length=1,
        max_length=10,
        description="Their bullet points"
    )
    description: str = Field(
        ...,
        min_length=50,
        max_length=10000,
        description="Their product description"
    )
    price: Optional[float] = Field(
        None,
        ge=0,
        description="Product price"
    )
    rating: Optional[float] = Field(
        None,
        ge=0,
        le=5,
        description="Star rating"
    )
    review_count: Optional[int] = Field(
        None,
        ge=0,
        description="Number of reviews"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "competitor_name": "Generic Card Storage Co",
                "product_title": "Card Binder for Pokemon and MTG Cards - 9 Pocket Pages",
                "bullet_points": [
                    "Holds up to 360 cards",
                    "Made of durable materials",
                    "Clear pockets for visibility"
                ],
                "description": "Store your trading cards safely...",
                "price": 19.99,
                "rating": 4.2,
                "review_count": 1523
            }
        }


class CompetitorReviewsRequest(BaseModel):
    """Request model for competitor review analysis."""
    competitor_name: str = Field(
        ...,
        min_length=2,
        max_length=200,
        description="Competitor name"
    )
    positive_reviews: List[str] = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Positive review excerpts"
    )
    negative_reviews: List[str] = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Negative review excerpts"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "competitor_name": "Generic Card Storage Co",
                "positive_reviews": [
                    "Love the quality, very sturdy",
                    "Perfect size for my Pokemon collection",
                    "Great value for the price"
                ],
                "negative_reviews": [
                    "Pages started falling out after a month",
                    "Cards scratch against the plastic",
                    "Not worth the money"
                ]
            }
        }


class MultipleCompetitorsRequest(BaseModel):
    """Request model for comparing multiple competitors."""
    competitors: List[Dict[str, Any]] = Field(
        ...,
        min_length=2,
        max_length=10,
        description="List of competitor information"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "competitors": [
                    {
                        "name": "Competitor A",
                        "price": 19.99,
                        "rating": 4.2,
                        "positioning": "Budget-friendly storage",
                        "key_features": "Basic 9-pocket pages, standard binding",
                        "weaknesses": "Quality issues reported"
                    },
                    {
                        "name": "Competitor B",
                        "price": 39.99,
                        "rating": 4.7,
                        "positioning": "Premium collector storage",
                        "key_features": "Archival-quality pages, metal binding",
                        "weaknesses": "High price point, limited availability"
                    }
                ]
            }
        }


class ContentGapRequest(BaseModel):
    """Request model for content gap analysis."""
    competitor_content: List[Dict[str, str]] = Field(
        ...,
        min_length=1,
        max_length=100,
        description="List of competitor content pieces"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "competitor_content": [
                    {
                        "competitor_name": "Competitor A",
                        "content_type": "blog",
                        "topic": "How to organize your Pokemon card collection",
                        "performance": "10K views, 200 shares"
                    },
                    {
                        "competitor_name": "Competitor B",
                        "content_type": "video",
                        "topic": "Best binders for MTG cards",
                        "performance": "50K views, 1K likes"
                    }
                ]
            }
        }


# ============================================================================
# Response Models
# ============================================================================

class CompetitorAnalysisResponse(BaseModel):
    """Response model for competitor analysis."""
    request_id: str = Field(
        ...,
        description="Unique identifier for the request"
    )
    analysis: str = Field(
        ...,
        description="The generated competitor analysis"
    )
    file_path: str = Field(
        ...,
        description="Path where the analysis was saved"
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

@router.post("/analyze-listing", response_model=CompetitorAnalysisResponse)
async def analyze_competitor_listing(
    request: CompetitorListingRequest,
    request_id: str = Depends(get_request_id)
) -> CompetitorAnalysisResponse:
    """
    Analyze a competitor's Amazon listing.

    Args:
        request: Competitor listing analysis request
        request_id: Unique request identifier

    Returns:
        CompetitorAnalysisResponse with analysis

    Raises:
        HTTPException: If analysis fails
    """
    logger.info(f"[{request_id}] Analyzing competitor listing for '{request.competitor_name}'")

    try:
        start_time = time.time()

        # Initialize agent
        agent = CompetitorAgent()

        # Analyze competitor listing
        analysis, file_path = agent.analyze_competitor_listing(
            competitor_name=request.competitor_name,
            product_title=request.product_title,
            bullet_points=request.bullet_points,
            description=request.description,
            price=request.price,
            rating=request.rating,
            review_count=request.review_count
        )

        generation_time = int((time.time() - start_time) * 1000)

        # Create response
        response = CompetitorAnalysisResponse(
            request_id=request_id,
            analysis=analysis,
            file_path=str(file_path),
            metadata=ContentMetadata(
                agent="competitor_agent",
                model="claude-sonnet-4-5-20250929",
                tokens_used=0,
                generation_time_ms=generation_time,
                timestamp=datetime.utcnow()
            ),
            status="success"
        )

        logger.info(f"[{request_id}] Successfully analyzed competitor listing in {generation_time}ms")
        return response

    except Exception as e:
        logger.error(f"[{request_id}] Error analyzing competitor listing: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze competitor listing: {str(e)}"
        )


@router.post("/analyze-reviews", response_model=CompetitorAnalysisResponse)
async def analyze_competitor_reviews(
    request: CompetitorReviewsRequest,
    request_id: str = Depends(get_request_id)
) -> CompetitorAnalysisResponse:
    """
    Analyze competitor reviews for insights.

    Args:
        request: Competitor reviews analysis request
        request_id: Unique request identifier

    Returns:
        CompetitorAnalysisResponse with insights

    Raises:
        HTTPException: If analysis fails
    """
    logger.info(f"[{request_id}] Analyzing reviews for competitor '{request.competitor_name}'")

    try:
        start_time = time.time()

        # Initialize agent
        agent = CompetitorAgent()

        # Analyze competitor reviews
        analysis, file_path = agent.analyze_competitor_reviews(
            competitor_name=request.competitor_name,
            positive_reviews=request.positive_reviews,
            negative_reviews=request.negative_reviews
        )

        generation_time = int((time.time() - start_time) * 1000)

        # Create response
        response = CompetitorAnalysisResponse(
            request_id=request_id,
            analysis=analysis,
            file_path=str(file_path),
            metadata=ContentMetadata(
                agent="competitor_agent",
                model="claude-sonnet-4-5-20250929",
                tokens_used=0,
                generation_time_ms=generation_time,
                timestamp=datetime.utcnow()
            ),
            status="success"
        )

        logger.info(f"[{request_id}] Successfully analyzed competitor reviews in {generation_time}ms")
        return response

    except Exception as e:
        logger.error(f"[{request_id}] Error analyzing competitor reviews: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze competitor reviews: {str(e)}"
        )


@router.post("/compare-multiple", response_model=CompetitorAnalysisResponse)
async def compare_multiple_competitors(
    request: MultipleCompetitorsRequest,
    request_id: str = Depends(get_request_id)
) -> CompetitorAnalysisResponse:
    """
    Compare multiple competitors side-by-side.

    Args:
        request: Multiple competitors comparison request
        request_id: Unique request identifier

    Returns:
        CompetitorAnalysisResponse with comparison

    Raises:
        HTTPException: If comparison fails
    """
    logger.info(f"[{request_id}] Comparing {len(request.competitors)} competitors")

    try:
        start_time = time.time()

        # Initialize agent
        agent = CompetitorAgent()

        # Compare competitors
        analysis, file_path = agent.compare_multiple_competitors(
            competitors=request.competitors
        )

        generation_time = int((time.time() - start_time) * 1000)

        # Create response
        response = CompetitorAnalysisResponse(
            request_id=request_id,
            analysis=analysis,
            file_path=str(file_path),
            metadata=ContentMetadata(
                agent="competitor_agent",
                model="claude-sonnet-4-5-20250929",
                tokens_used=0,
                generation_time_ms=generation_time,
                timestamp=datetime.utcnow()
            ),
            status="success"
        )

        logger.info(f"[{request_id}] Successfully compared competitors in {generation_time}ms")
        return response

    except Exception as e:
        logger.error(f"[{request_id}] Error comparing competitors: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to compare competitors: {str(e)}"
        )


@router.post("/content-gaps", response_model=CompetitorAnalysisResponse)
async def identify_content_gaps(
    request: ContentGapRequest,
    request_id: str = Depends(get_request_id)
) -> CompetitorAnalysisResponse:
    """
    Identify content opportunities based on competitor content.

    Args:
        request: Content gap analysis request
        request_id: Unique request identifier

    Returns:
        CompetitorAnalysisResponse with gap analysis

    Raises:
        HTTPException: If analysis fails
    """
    logger.info(f"[{request_id}] Analyzing {len(request.competitor_content)} pieces of competitor content")

    try:
        start_time = time.time()

        # Initialize agent
        agent = CompetitorAgent()

        # Identify content gaps
        analysis, file_path = agent.identify_content_gaps(
            competitor_content=request.competitor_content
        )

        generation_time = int((time.time() - start_time) * 1000)

        # Create response
        response = CompetitorAnalysisResponse(
            request_id=request_id,
            analysis=analysis,
            file_path=str(file_path),
            metadata=ContentMetadata(
                agent="competitor_agent",
                model="claude-sonnet-4-5-20250929",
                tokens_used=0,
                generation_time_ms=generation_time,
                timestamp=datetime.utcnow()
            ),
            status="success"
        )

        logger.info(f"[{request_id}] Successfully identified content gaps in {generation_time}ms")
        return response

    except Exception as e:
        logger.error(f"[{request_id}] Error identifying content gaps: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to identify content gaps: {str(e)}"
        )
