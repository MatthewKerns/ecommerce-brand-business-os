"""
AEO (Answer Engine Optimization) content generation routes.

This module defines API endpoints for AEO content generation using the AEOAgent.
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
import logging
import time

from api.dependencies import get_request_id
from api.models import (
    ContentResponse,
    ContentMetadata,
    ErrorResponse,
    FAQGenerationRequest,
    FAQSchemaRequest,
    ProductSchemaRequest,
    AIOptimizedContentRequest,
    ComparisonContentRequest,
    FAQContentResponse,
    SchemaResponse
)
from agents.aeo_agent import AEOAgent

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/aeo",
    tags=["aeo"],
    responses={
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)


# ============================================================================
# Endpoints
# ============================================================================

@router.post(
    "/generate-faq",
    response_model=FAQContentResponse,
    summary="Generate FAQ content",
    description="Generate FAQ content optimized for AI assistant citation"
)
async def generate_faq_content(
    request: FAQGenerationRequest,
    request_id: str = Depends(get_request_id)
) -> Dict[str, Any]:
    """
    Generate FAQ content.

    Args:
        request: FAQ generation request
        request_id: Unique request identifier

    Returns:
        FAQ content response with generated content and metadata

    Raises:
        HTTPException: If content generation fails
    """
    logger.info(f"[{request_id}] Generating FAQ content: topic='{request.topic}', num_questions={request.num_questions}")
    start_time = time.time()

    try:
        # Initialize agent
        agent = AEOAgent()

        # Generate FAQ content
        content, file_path = agent.generate_faq_content(
            topic=request.topic,
            num_questions=request.num_questions,
            target_audience=request.target_audience,
            include_product_mentions=request.include_product_mentions
        )

        # Calculate generation time
        generation_time_ms = int((time.time() - start_time) * 1000)

        # Build response
        response = {
            "request_id": request_id,
            "content": content,
            "file_path": str(file_path),
            "metadata": {
                "agent": "aeo_agent",
                "model": "claude-sonnet-4-5-20250929",
                "tokens_used": 0,  # TODO: Implement token tracking
                "generation_time_ms": generation_time_ms,
                "timestamp": datetime.utcnow()
            },
            "status": "success"
        }

        logger.info(f"[{request_id}] Successfully generated FAQ content in {generation_time_ms}ms")
        return response

    except Exception as e:
        logger.error(f"[{request_id}] Error generating FAQ content: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "FAQGenerationError",
                "message": f"Failed to generate FAQ content: {str(e)}",
                "request_id": request_id,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        )


@router.post(
    "/generate-faq-schema",
    response_model=SchemaResponse,
    summary="Generate FAQ schema",
    description="Generate JSON-LD FAQ schema markup for AI parsing"
)
async def generate_faq_schema(
    request: FAQSchemaRequest,
    request_id: str = Depends(get_request_id)
) -> Dict[str, Any]:
    """
    Generate FAQ schema.

    Args:
        request: FAQ schema generation request
        request_id: Unique request identifier

    Returns:
        Schema response with generated JSON-LD and metadata

    Raises:
        HTTPException: If schema generation fails
    """
    logger.info(f"[{request_id}] Generating FAQ schema: num_items={len(request.faq_items)}")
    start_time = time.time()

    try:
        # Initialize agent
        agent = AEOAgent()

        # Generate FAQ schema
        schema = agent.generate_faq_schema(faq_items=request.faq_items)

        # Calculate generation time
        generation_time_ms = int((time.time() - start_time) * 1000)

        # Build response
        response = {
            "request_id": request_id,
            "schema": schema,
            "schema_type": "FAQPage",
            "metadata": {
                "agent": "aeo_agent",
                "model": "claude-sonnet-4-5-20250929",
                "tokens_used": 0,  # No tokens used for schema generation
                "generation_time_ms": generation_time_ms,
                "timestamp": datetime.utcnow()
            },
            "status": "success"
        }

        logger.info(f"[{request_id}] Successfully generated FAQ schema in {generation_time_ms}ms")
        return response

    except Exception as e:
        logger.error(f"[{request_id}] Error generating FAQ schema: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "FAQSchemaGenerationError",
                "message": f"Failed to generate FAQ schema: {str(e)}",
                "request_id": request_id,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        )


@router.post(
    "/generate-product-schema",
    response_model=SchemaResponse,
    summary="Generate Product schema",
    description="Generate JSON-LD Product schema markup for AI parsing"
)
async def generate_product_schema(
    request: ProductSchemaRequest,
    request_id: str = Depends(get_request_id)
) -> Dict[str, Any]:
    """
    Generate Product schema.

    Args:
        request: Product schema generation request
        request_id: Unique request identifier

    Returns:
        Schema response with generated JSON-LD and metadata

    Raises:
        HTTPException: If schema generation fails
    """
    product_name = request.product_data.get('name', 'Unknown Product')
    logger.info(f"[{request_id}] Generating Product schema: product='{product_name}'")
    start_time = time.time()

    try:
        # Initialize agent
        agent = AEOAgent()

        # Generate Product schema
        schema = agent.generate_product_schema(product_data=request.product_data)

        # Calculate generation time
        generation_time_ms = int((time.time() - start_time) * 1000)

        # Build response
        response = {
            "request_id": request_id,
            "schema": schema,
            "schema_type": "Product",
            "metadata": {
                "agent": "aeo_agent",
                "model": "claude-sonnet-4-5-20250929",
                "tokens_used": 0,  # No tokens used for schema generation
                "generation_time_ms": generation_time_ms,
                "timestamp": datetime.utcnow()
            },
            "status": "success"
        }

        logger.info(f"[{request_id}] Successfully generated Product schema in {generation_time_ms}ms")
        return response

    except Exception as e:
        logger.error(f"[{request_id}] Error generating Product schema: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "ProductSchemaGenerationError",
                "message": f"Failed to generate Product schema: {str(e)}",
                "request_id": request_id,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        )


@router.post(
    "/generate-ai-content",
    response_model=FAQContentResponse,
    summary="Generate AI-optimized content",
    description="Generate content specifically optimized for AI assistant citation"
)
async def generate_ai_optimized_content(
    request: AIOptimizedContentRequest,
    request_id: str = Depends(get_request_id)
) -> Dict[str, Any]:
    """
    Generate AI-optimized content.

    Args:
        request: AI-optimized content generation request
        request_id: Unique request identifier

    Returns:
        Content response with generated content and metadata

    Raises:
        HTTPException: If content generation fails
    """
    logger.info(f"[{request_id}] Generating AI-optimized content: question='{request.question}', type={request.content_type}")
    start_time = time.time()

    try:
        # Initialize agent
        agent = AEOAgent()

        # Generate AI-optimized content
        content, file_path = agent.generate_ai_optimized_content(
            question=request.question,
            content_type=request.content_type,
            include_sources=request.include_sources
        )

        # Calculate generation time
        generation_time_ms = int((time.time() - start_time) * 1000)

        # Build response
        response = {
            "request_id": request_id,
            "content": content,
            "file_path": str(file_path),
            "metadata": {
                "agent": "aeo_agent",
                "model": "claude-sonnet-4-5-20250929",
                "tokens_used": 0,  # TODO: Implement token tracking
                "generation_time_ms": generation_time_ms,
                "timestamp": datetime.utcnow()
            },
            "status": "success"
        }

        logger.info(f"[{request_id}] Successfully generated AI-optimized content in {generation_time_ms}ms")
        return response

    except Exception as e:
        logger.error(f"[{request_id}] Error generating AI-optimized content: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "AIContentGenerationError",
                "message": f"Failed to generate AI-optimized content: {str(e)}",
                "request_id": request_id,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        )


@router.post(
    "/generate-comparison",
    response_model=FAQContentResponse,
    summary="Generate comparison content",
    description="Generate comparison content optimized for 'best' and 'vs' queries"
)
async def generate_comparison_content(
    request: ComparisonContentRequest,
    request_id: str = Depends(get_request_id)
) -> Dict[str, Any]:
    """
    Generate comparison content.

    Args:
        request: Comparison content generation request
        request_id: Unique request identifier

    Returns:
        Content response with generated comparison and metadata

    Raises:
        HTTPException: If content generation fails
    """
    logger.info(f"[{request_id}] Generating comparison content: topic='{request.comparison_topic}', items={len(request.items_to_compare)}")
    start_time = time.time()

    try:
        # Initialize agent
        agent = AEOAgent()

        # Generate comparison content
        content, file_path = agent.generate_comparison_content(
            comparison_topic=request.comparison_topic,
            items_to_compare=request.items_to_compare,
            include_recommendation=request.include_recommendation
        )

        # Calculate generation time
        generation_time_ms = int((time.time() - start_time) * 1000)

        # Build response
        response = {
            "request_id": request_id,
            "content": content,
            "file_path": str(file_path),
            "metadata": {
                "agent": "aeo_agent",
                "model": "claude-sonnet-4-5-20250929",
                "tokens_used": 0,  # TODO: Implement token tracking
                "generation_time_ms": generation_time_ms,
                "timestamp": datetime.utcnow()
            },
            "status": "success"
        }

        logger.info(f"[{request_id}] Successfully generated comparison content in {generation_time_ms}ms")
        return response

    except Exception as e:
        logger.error(f"[{request_id}] Error generating comparison content: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "ComparisonGenerationError",
                "message": f"Failed to generate comparison content: {str(e)}",
                "request_id": request_id,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        )


@router.get(
    "/health",
    summary="Health check",
    description="Check if the AEO router is operational"
)
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint.

    Returns:
        Health status
    """
    return {
        "status": "healthy",
        "service": "aeo",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
