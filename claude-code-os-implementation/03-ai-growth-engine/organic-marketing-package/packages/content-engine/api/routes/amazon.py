"""
Amazon listing optimization routes.

This module defines API endpoints for Amazon listing content generation using the AmazonAgent.
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
from agents.amazon_agent import AmazonAgent

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/amazon",
    tags=["amazon"],
    responses={
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)


# ============================================================================
# Request Models
# ============================================================================

class ProductTitleRequest(BaseModel):
    """Request model for Amazon product title generation."""
    product_name: str = Field(
        ...,
        min_length=5,
        max_length=200,
        description="Product name"
    )
    key_features: List[str] = Field(
        ...,
        min_length=1,
        max_length=10,
        description="Main features to highlight"
    )
    target_keywords: List[str] = Field(
        ...,
        min_length=1,
        max_length=20,
        description="SEO keywords to include"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "product_name": "Trading Card Binder",
                "key_features": ["Scratch-resistant pages", "9-pocket design", "Lifetime warranty"],
                "target_keywords": ["card binder", "pokemon storage", "TCG binder", "trading card holder"]
            }
        }


class BulletPointsRequest(BaseModel):
    """Request model for Amazon bullet points generation."""
    product_name: str = Field(
        ...,
        min_length=5,
        max_length=200,
        description="Product name"
    )
    features: List[Dict[str, str]] = Field(
        ...,
        min_length=3,
        max_length=10,
        description="List of feature/benefit pairs"
    )
    target_audience: str = Field(
        default="Tournament players and serious collectors",
        description="Target customer segment"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "product_name": "Trading Card Binder",
                "features": [
                    {"feature": "Scratch-resistant pages", "benefit": "Keep cards pristine"},
                    {"feature": "Reinforced binding", "benefit": "Withstand tournament travel"},
                    {"feature": "Clear pocket design", "benefit": "Easy card viewing"}
                ],
                "target_audience": "Competitive TCG players"
            }
        }


class ProductDescriptionRequest(BaseModel):
    """Request model for Amazon product description generation."""
    product_name: str = Field(
        ...,
        min_length=5,
        max_length=200,
        description="Product name"
    )
    long_description: str = Field(
        ...,
        min_length=50,
        max_length=2000,
        description="Detailed product information"
    )
    usp: str = Field(
        ...,
        min_length=10,
        max_length=500,
        description="Unique selling proposition"
    )
    warranty_info: Optional[str] = Field(
        default="Lifetime warranty",
        description="Warranty details"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "product_name": "Trading Card Binder",
                "long_description": "Professional-grade trading card storage designed for tournament players...",
                "usp": "Battle-ready equipment with lifetime warranty - not commodity storage",
                "warranty_info": "Lifetime warranty on all materials and craftsmanship"
            }
        }


class APlusContentRequest(BaseModel):
    """Request model for Amazon A+ Content generation."""
    product_name: str = Field(
        ...,
        min_length=5,
        max_length=200,
        description="Product name"
    )
    modules: List[str] = Field(
        ...,
        min_length=1,
        max_length=7,
        description="List of A+ module types to create"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "product_name": "Trading Card Binder",
                "modules": [
                    "Hero image with headline",
                    "Feature comparison chart",
                    "Product benefits grid",
                    "Brand story section"
                ]
            }
        }


class OptimizeListingRequest(BaseModel):
    """Request model for listing optimization."""
    current_title: str = Field(
        ...,
        min_length=10,
        max_length=500,
        description="Current product title"
    )
    current_bullets: List[str] = Field(
        ...,
        min_length=1,
        max_length=10,
        description="Current bullet points"
    )
    current_description: str = Field(
        ...,
        min_length=50,
        max_length=5000,
        description="Current product description"
    )
    performance_data: Optional[Dict[str, Any]] = Field(
        None,
        description="Optional performance metrics (CTR, conversion rate, etc.)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "current_title": "Card Binder for Pokemon Cards",
                "current_bullets": [
                    "Holds cards",
                    "Made of plastic",
                    "Has pages"
                ],
                "current_description": "This is a binder for your trading cards...",
                "performance_data": {
                    "ctr": 0.03,
                    "conversion_rate": 0.08,
                    "impressions": 5000
                }
            }
        }


class BackendKeywordsRequest(BaseModel):
    """Request model for backend keywords generation."""
    product_name: str = Field(
        ...,
        min_length=5,
        max_length=200,
        description="Product name"
    )
    category: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="Product category"
    )
    target_use_cases: List[str] = Field(
        ...,
        min_length=1,
        max_length=20,
        description="How customers use the product"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "product_name": "Trading Card Binder",
                "category": "Trading Card Storage",
                "target_use_cases": [
                    "Tournament play",
                    "Card collection storage",
                    "Display rare cards",
                    "Travel with cards"
                ]
            }
        }


# ============================================================================
# Response Models
# ============================================================================

class AmazonContentResponse(BaseModel):
    """Response model for Amazon content generation."""
    request_id: str = Field(
        ...,
        description="Unique identifier for the request"
    )
    content: str = Field(
        ...,
        description="The generated Amazon content"
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


# ============================================================================
# Route Handlers
# ============================================================================

@router.post("/title", response_model=AmazonContentResponse)
async def generate_product_title(
    request: ProductTitleRequest,
    request_id: str = Depends(get_request_id)
) -> AmazonContentResponse:
    """
    Generate an optimized Amazon product title.

    Args:
        request: Product title generation request
        request_id: Unique request identifier

    Returns:
        AmazonContentResponse with generated title

    Raises:
        HTTPException: If generation fails
    """
    logger.info(f"[{request_id}] Generating Amazon product title for '{request.product_name}'")

    try:
        start_time = time.time()

        # Initialize agent
        agent = AmazonAgent()

        # Generate product title
        content, file_path = agent.generate_product_title(
            product_name=request.product_name,
            key_features=request.key_features,
            target_keywords=request.target_keywords
        )

        generation_time = int((time.time() - start_time) * 1000)

        # Create response
        response = AmazonContentResponse(
            request_id=request_id,
            content=content,
            file_path=str(file_path),
            metadata=ContentMetadata(
                agent="amazon_agent",
                model="claude-sonnet-4-5-20250929",
                tokens_used=0,
                generation_time_ms=generation_time,
                timestamp=datetime.utcnow()
            ),
            status="success"
        )

        logger.info(f"[{request_id}] Successfully generated product title in {generation_time}ms")
        return response

    except Exception as e:
        logger.error(f"[{request_id}] Error generating product title: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate product title: {str(e)}"
        )


@router.post("/bullets", response_model=AmazonContentResponse)
async def generate_bullet_points(
    request: BulletPointsRequest,
    request_id: str = Depends(get_request_id)
) -> AmazonContentResponse:
    """
    Generate Amazon bullet points.

    Args:
        request: Bullet points generation request
        request_id: Unique request identifier

    Returns:
        AmazonContentResponse with generated bullets

    Raises:
        HTTPException: If generation fails
    """
    logger.info(f"[{request_id}] Generating Amazon bullet points for '{request.product_name}'")

    try:
        start_time = time.time()

        # Initialize agent
        agent = AmazonAgent()

        # Generate bullet points
        content, file_path = agent.generate_bullet_points(
            product_name=request.product_name,
            features=request.features,
            target_audience=request.target_audience
        )

        generation_time = int((time.time() - start_time) * 1000)

        # Create response
        response = AmazonContentResponse(
            request_id=request_id,
            content=content,
            file_path=str(file_path),
            metadata=ContentMetadata(
                agent="amazon_agent",
                model="claude-sonnet-4-5-20250929",
                tokens_used=0,
                generation_time_ms=generation_time,
                timestamp=datetime.utcnow()
            ),
            status="success"
        )

        logger.info(f"[{request_id}] Successfully generated bullet points in {generation_time}ms")
        return response

    except Exception as e:
        logger.error(f"[{request_id}] Error generating bullet points: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate bullet points: {str(e)}"
        )


@router.post("/description", response_model=AmazonContentResponse)
async def generate_product_description(
    request: ProductDescriptionRequest,
    request_id: str = Depends(get_request_id)
) -> AmazonContentResponse:
    """
    Generate Amazon product description.

    Args:
        request: Product description generation request
        request_id: Unique request identifier

    Returns:
        AmazonContentResponse with generated description

    Raises:
        HTTPException: If generation fails
    """
    logger.info(f"[{request_id}] Generating Amazon product description for '{request.product_name}'")

    try:
        start_time = time.time()

        # Initialize agent
        agent = AmazonAgent()

        # Generate product description
        content, file_path = agent.generate_product_description(
            product_name=request.product_name,
            long_description=request.long_description,
            usp=request.usp,
            warranty_info=request.warranty_info
        )

        generation_time = int((time.time() - start_time) * 1000)

        # Create response
        response = AmazonContentResponse(
            request_id=request_id,
            content=content,
            file_path=str(file_path),
            metadata=ContentMetadata(
                agent="amazon_agent",
                model="claude-sonnet-4-5-20250929",
                tokens_used=0,
                generation_time_ms=generation_time,
                timestamp=datetime.utcnow()
            ),
            status="success"
        )

        logger.info(f"[{request_id}] Successfully generated product description in {generation_time}ms")
        return response

    except Exception as e:
        logger.error(f"[{request_id}] Error generating product description: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate product description: {str(e)}"
        )


@router.post("/a-plus", response_model=AmazonContentResponse)
async def generate_a_plus_content(
    request: APlusContentRequest,
    request_id: str = Depends(get_request_id)
) -> AmazonContentResponse:
    """
    Generate Amazon A+ Content.

    Args:
        request: A+ Content generation request
        request_id: Unique request identifier

    Returns:
        AmazonContentResponse with generated A+ content

    Raises:
        HTTPException: If generation fails
    """
    logger.info(f"[{request_id}] Generating Amazon A+ Content for '{request.product_name}'")

    try:
        start_time = time.time()

        # Initialize agent
        agent = AmazonAgent()

        # Generate A+ Content
        content, file_path = agent.generate_a_plus_content(
            product_name=request.product_name,
            modules=request.modules
        )

        generation_time = int((time.time() - start_time) * 1000)

        # Create response
        response = AmazonContentResponse(
            request_id=request_id,
            content=content,
            file_path=str(file_path),
            metadata=ContentMetadata(
                agent="amazon_agent",
                model="claude-sonnet-4-5-20250929",
                tokens_used=0,
                generation_time_ms=generation_time,
                timestamp=datetime.utcnow()
            ),
            status="success"
        )

        logger.info(f"[{request_id}] Successfully generated A+ Content in {generation_time}ms")
        return response

    except Exception as e:
        logger.error(f"[{request_id}] Error generating A+ Content: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate A+ Content: {str(e)}"
        )


@router.post("/optimize", response_model=AmazonContentResponse)
async def optimize_existing_listing(
    request: OptimizeListingRequest,
    request_id: str = Depends(get_request_id)
) -> AmazonContentResponse:
    """
    Analyze and optimize an existing Amazon listing.

    Args:
        request: Listing optimization request
        request_id: Unique request identifier

    Returns:
        AmazonContentResponse with optimization report

    Raises:
        HTTPException: If optimization fails
    """
    logger.info(f"[{request_id}] Optimizing existing Amazon listing")

    try:
        start_time = time.time()

        # Initialize agent
        agent = AmazonAgent()

        # Optimize listing
        content, file_path = agent.optimize_existing_listing(
            current_title=request.current_title,
            current_bullets=request.current_bullets,
            current_description=request.current_description,
            performance_data=request.performance_data
        )

        generation_time = int((time.time() - start_time) * 1000)

        # Create response
        response = AmazonContentResponse(
            request_id=request_id,
            content=content,
            file_path=str(file_path),
            metadata=ContentMetadata(
                agent="amazon_agent",
                model="claude-sonnet-4-5-20250929",
                tokens_used=0,
                generation_time_ms=generation_time,
                timestamp=datetime.utcnow()
            ),
            status="success"
        )

        logger.info(f"[{request_id}] Successfully optimized listing in {generation_time}ms")
        return response

    except Exception as e:
        logger.error(f"[{request_id}] Error optimizing listing: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to optimize listing: {str(e)}"
        )


@router.post("/backend-keywords", response_model=AmazonContentResponse)
async def generate_backend_keywords(
    request: BackendKeywordsRequest,
    request_id: str = Depends(get_request_id)
) -> AmazonContentResponse:
    """
    Generate Amazon backend search terms.

    Args:
        request: Backend keywords generation request
        request_id: Unique request identifier

    Returns:
        AmazonContentResponse with generated keywords

    Raises:
        HTTPException: If generation fails
    """
    logger.info(f"[{request_id}] Generating Amazon backend keywords for '{request.product_name}'")

    try:
        start_time = time.time()

        # Initialize agent
        agent = AmazonAgent()

        # Generate backend keywords
        content, file_path = agent.generate_backend_keywords(
            product_name=request.product_name,
            category=request.category,
            target_use_cases=request.target_use_cases
        )

        generation_time = int((time.time() - start_time) * 1000)

        # Create response
        response = AmazonContentResponse(
            request_id=request_id,
            content=content,
            file_path=str(file_path),
            metadata=ContentMetadata(
                agent="amazon_agent",
                model="claude-sonnet-4-5-20250929",
                tokens_used=0,
                generation_time_ms=generation_time,
                timestamp=datetime.utcnow()
            ),
            status="success"
        )

        logger.info(f"[{request_id}] Successfully generated backend keywords in {generation_time}ms")
        return response

    except Exception as e:
        logger.error(f"[{request_id}] Error generating backend keywords: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate backend keywords: {str(e)}"
        )
