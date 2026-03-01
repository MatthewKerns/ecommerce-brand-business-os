"""
AEO (Answer Engine Optimization) content generation routes.

This module defines API endpoints for AEO content generation, citation tracking,
content optimization, and AEO metrics using the AEOOptimizationAgent and database models.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pathlib import Path
import json
import logging
import time

from pydantic import BaseModel, Field
from sqlalchemy import func, desc, Integer
from sqlalchemy.orm import Session

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
from agents.aeo_optimization_agent import AEOOptimizationAgent
# Backward-compatible alias for existing instantiations
AEOAgent = AEOOptimizationAgent
from database.connection import get_db_session
from database.models import (
    CitationTracking,
    CitationRecord,
    CompetitorCitation,
    OptimizationRecommendation,
)
from config.config import (
    BRAND_NAME,
    COMPETITOR_BRANDS,
    AEO_CONFIG,
    AEO_OUTPUT_DIR,
    HIGH_VALUE_SEARCH_TERMS,
)

# Configure logging
logger = logging.getLogger(__name__)


# ============================================================================
# Request/Response Models for Citation & Optimization Endpoints
# ============================================================================

class CitationAnalyzeRequest(BaseModel):
    """Request model for analyzing citation opportunities."""
    queries: Optional[List[str]] = Field(
        default=None,
        description="Specific queries to analyze. Uses default high-value queries if not provided."
    )
    platforms: List[str] = Field(
        default=["chatgpt", "perplexity", "claude", "google_ai"],
        description="AI platforms to analyze"
    )
    brand_name: str = Field(
        default=BRAND_NAME,
        description="Brand name to track citations for"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "queries": ["best trading card binder", "how to protect valuable cards"],
                "platforms": ["chatgpt", "perplexity", "claude"],
                "brand_name": "Infinity Vault"
            }
        }


class ContentOptimizeRequest(BaseModel):
    """Request model for optimizing content for AI citations."""
    content: str = Field(
        ...,
        min_length=50,
        max_length=50000,
        description="Content to optimize for AI citation"
    )
    target_queries: Optional[List[str]] = Field(
        default_factory=list,
        description="Target queries this content should rank for"
    )
    optimization_level: str = Field(
        default="standard",
        pattern="^(light|standard|aggressive)$",
        description="How aggressively to optimize (light, standard, aggressive)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "content": "# Trading Card Storage Guide\n\nLearn the best ways to store...",
                "target_queries": ["best card storage", "how to store trading cards"],
                "optimization_level": "standard"
            }
        }


class BlogGenerateRequest(BaseModel):
    """Request model for generating citation-optimized blog posts."""
    topic: str = Field(
        ...,
        min_length=10,
        max_length=500,
        description="Blog post topic"
    )
    target_queries: Optional[List[str]] = Field(
        default_factory=list,
        description="AI assistant queries this post should target"
    )
    word_count: int = Field(
        default=1500,
        ge=500,
        le=5000,
        description="Target word count"
    )
    include_faq_schema: bool = Field(
        default=True,
        description="Whether to generate FAQ schema alongside the post"
    )
    include_product_schema: bool = Field(
        default=False,
        description="Whether to include product schema markup"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "topic": "Complete Guide to Protecting Valuable Trading Cards",
                "target_queries": ["how to protect trading cards", "best card protection"],
                "word_count": 2000,
                "include_faq_schema": True,
                "include_product_schema": False
            }
        }

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


# ============================================================================
# Citation Tracking Endpoints
# ============================================================================

@router.get(
    "/citations/track",
    summary="Get current citation status",
    description="Retrieve current citation tracking data across AI platforms"
)
async def get_citation_status(
    request_id: str = Depends(get_request_id),
    platform: Optional[str] = Query(None, description="Filter by AI platform"),
    days: int = Query(30, ge=1, le=365, description="Number of days to look back"),
    limit: int = Query(50, ge=1, le=200, description="Maximum number of records")
) -> Dict[str, Any]:
    """
    Get current citation tracking status across AI platforms.

    Returns recent citation tracking records with aggregated statistics.
    """
    logger.info(f"[{request_id}] Getting citation status: platform={platform}, days={days}")
    start_time = time.time()

    try:
        db = get_db_session()
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)

            # Build query
            query = db.query(CitationTracking).filter(
                CitationTracking.created_at >= cutoff_date
            )
            if platform:
                query = query.filter(CitationTracking.platform == platform)

            # Get records
            records = query.order_by(desc(CitationTracking.created_at)).limit(limit).all()

            # Calculate aggregate stats
            total_query = db.query(CitationTracking).filter(
                CitationTracking.created_at >= cutoff_date
            )
            if platform:
                total_query = total_query.filter(CitationTracking.platform == platform)

            total_records = total_query.count()
            mentioned_count = total_query.filter(
                CitationTracking.brand_mentioned == True
            ).count()

            citation_rate = (mentioned_count / total_records * 100) if total_records > 0 else 0

            # Average opportunity score
            avg_score_result = total_query.with_entities(
                func.avg(CitationTracking.opportunity_score)
            ).scalar()
            avg_opportunity_score = float(avg_score_result) if avg_score_result else 0

            # Platform breakdown
            platform_stats = db.query(
                CitationTracking.platform,
                func.count(CitationTracking.id).label("total"),
                func.sum(
                    func.cast(CitationTracking.brand_mentioned, Integer)
                ).label("mentioned")
            ).filter(
                CitationTracking.created_at >= cutoff_date
            ).group_by(CitationTracking.platform).all()

            platforms_breakdown = {}
            for stat in platform_stats:
                total = stat.total or 0
                mentioned = stat.mentioned or 0
                platforms_breakdown[stat.platform] = {
                    "total_queries": total,
                    "brand_mentioned": mentioned,
                    "citation_rate": round(mentioned / total * 100, 1) if total > 0 else 0
                }

            # Build record list
            citation_records = []
            for record in records:
                citation_records.append({
                    "tracking_id": record.tracking_id,
                    "platform": record.platform,
                    "query": record.query,
                    "brand_mentioned": record.brand_mentioned,
                    "citation_url": record.citation_url,
                    "citation_context": record.citation_context,
                    "opportunity_score": record.opportunity_score,
                    "query_category": record.query_category,
                    "created_at": record.created_at.isoformat() + "Z" if record.created_at else None,
                })

            generation_time_ms = int((time.time() - start_time) * 1000)

            return {
                "request_id": request_id,
                "summary": {
                    "total_tracked": total_records,
                    "brand_mentioned": mentioned_count,
                    "citation_rate_percent": round(citation_rate, 1),
                    "avg_opportunity_score": round(avg_opportunity_score, 1),
                    "period_days": days,
                },
                "platforms": platforms_breakdown,
                "records": citation_records,
                "metadata": {
                    "generation_time_ms": generation_time_ms,
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                },
                "status": "success"
            }
        finally:
            db.close()

    except Exception as e:
        logger.error(f"[{request_id}] Error getting citation status: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "CitationTrackingError",
                "message": f"Failed to get citation status: {str(e)}",
                "request_id": request_id,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        )



@router.post(
    "/citations/analyze",
    summary="Analyze citation opportunities",
    description="Analyze current citation landscape and identify optimization opportunities"
)
async def analyze_citation_opportunities(
    request: CitationAnalyzeRequest,
    request_id: str = Depends(get_request_id)
) -> Dict[str, Any]:
    """
    Analyze citation opportunities across AI platforms.

    Queries the database for recent citation data and generates
    an analysis of opportunities for improvement.
    """
    logger.info(f"[{request_id}] Analyzing citation opportunities for brand='{request.brand_name}'")
    start_time = time.time()

    try:
        db = get_db_session()
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=30)

            # Get recent citation data
            recent_citations = db.query(CitationTracking).filter(
                CitationTracking.created_at >= cutoff_date
            ).all()

            # Identify missed opportunities (brand not mentioned, high opportunity score)
            missed_opportunities = []
            for citation in recent_citations:
                if not citation.brand_mentioned and citation.opportunity_score >= AEO_CONFIG.get("opportunity_score_medium", 40):
                    competitor_data = None
                    if citation.competitor_citations:
                        try:
                            competitor_data = json.loads(citation.competitor_citations) if isinstance(citation.competitor_citations, str) else citation.competitor_citations
                        except (json.JSONDecodeError, TypeError):
                            competitor_data = None

                    missed_opportunities.append({
                        "query": citation.query,
                        "platform": citation.platform,
                        "opportunity_score": citation.opportunity_score,
                        "competitors_cited": competitor_data,
                        "query_category": citation.query_category,
                        "date": citation.created_at.isoformat() + "Z" if citation.created_at else None,
                    })

            # Sort by opportunity score descending
            missed_opportunities.sort(key=lambda x: x["opportunity_score"], reverse=True)

            # Get optimization recommendations from database
            recommendations = db.query(OptimizationRecommendation).filter(
                OptimizationRecommendation.status == "pending"
            ).order_by(
                desc(OptimizationRecommendation.expected_impact)
            ).limit(10).all()

            recommendation_list = []
            for rec in recommendations:
                recommendation_list.append({
                    "id": rec.id,
                    "type": rec.recommendation_type,
                    "title": rec.title,
                    "description": rec.description,
                    "priority": rec.priority,
                    "expected_impact": rec.expected_impact,
                    "effort": rec.implementation_effort,
                    "ai_platform": rec.ai_platform,
                })

            # Platform-level analysis
            platform_analysis = {}
            for platform_name in request.platforms:
                platform_citations = [c for c in recent_citations if c.platform == platform_name]
                total = len(platform_citations)
                mentioned = sum(1 for c in platform_citations if c.brand_mentioned)

                platform_analysis[platform_name] = {
                    "total_queries": total,
                    "brand_mentioned": mentioned,
                    "citation_rate": round(mentioned / total * 100, 1) if total > 0 else 0,
                    "avg_opportunity_score": round(
                        sum(c.opportunity_score for c in platform_citations) / total, 1
                    ) if total > 0 else 0,
                    "top_missed_queries": [
                        c.query for c in platform_citations
                        if not c.brand_mentioned
                    ][:5]
                }

            generation_time_ms = int((time.time() - start_time) * 1000)

            return {
                "request_id": request_id,
                "brand": request.brand_name,
                "analysis_period_days": 30,
                "missed_opportunities": missed_opportunities[:20],
                "total_missed_opportunities": len(missed_opportunities),
                "recommendations": recommendation_list,
                "platform_analysis": platform_analysis,
                "metadata": {
                    "generation_time_ms": generation_time_ms,
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                },
                "status": "success"
            }
        finally:
            db.close()

    except Exception as e:
        logger.error(f"[{request_id}] Error analyzing citations: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "CitationAnalysisError",
                "message": f"Failed to analyze citations: {str(e)}",
                "request_id": request_id,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        )


@router.get(
    "/citations/competitors",
    summary="Compare competitor citations",
    description="Get competitor citation comparison data across AI platforms"
)
async def get_competitor_citations(
    request_id: str = Depends(get_request_id),
    days: int = Query(30, ge=1, le=365, description="Number of days to look back"),
    competitor: Optional[str] = Query(None, description="Filter by specific competitor name"),
    platform: Optional[str] = Query(None, description="Filter by AI platform")
) -> Dict[str, Any]:
    """
    Compare brand citations against competitors across AI platforms.
    """
    logger.info(f"[{request_id}] Getting competitor citation comparison: days={days}, competitor={competitor}")
    start_time = time.time()

    try:
        db = get_db_session()
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)

            # Build competitor citation query
            query = db.query(CompetitorCitation).filter(
                CompetitorCitation.query_timestamp >= cutoff_date
            )
            if competitor:
                query = query.filter(CompetitorCitation.competitor_name == competitor)
            if platform:
                query = query.filter(CompetitorCitation.ai_platform == platform)

            competitor_records = query.all()

            # Aggregate by competitor
            competitor_stats = {}
            for record in competitor_records:
                name = record.competitor_name
                if name not in competitor_stats:
                    competitor_stats[name] = {
                        "total_queries": 0,
                        "times_mentioned": 0,
                        "platforms": {},
                    }
                competitor_stats[name]["total_queries"] += 1
                if record.competitor_mentioned:
                    competitor_stats[name]["times_mentioned"] += 1

                plat = record.ai_platform
                if plat not in competitor_stats[name]["platforms"]:
                    competitor_stats[name]["platforms"][plat] = {"total": 0, "mentioned": 0}
                competitor_stats[name]["platforms"][plat]["total"] += 1
                if record.competitor_mentioned:
                    competitor_stats[name]["platforms"][plat]["mentioned"] += 1

            # Calculate citation rates
            competitor_comparison = []
            for name, stats in competitor_stats.items():
                total = stats["total_queries"]
                mentioned = stats["times_mentioned"]
                platform_rates = {}
                for plat, plat_stats in stats["platforms"].items():
                    pt = plat_stats["total"]
                    pm = plat_stats["mentioned"]
                    platform_rates[plat] = round(pm / pt * 100, 1) if pt > 0 else 0

                competitor_comparison.append({
                    "competitor": name,
                    "total_queries": total,
                    "times_mentioned": mentioned,
                    "citation_rate_percent": round(mentioned / total * 100, 1) if total > 0 else 0,
                    "platform_rates": platform_rates,
                })

            # Sort by citation rate descending
            competitor_comparison.sort(key=lambda x: x["citation_rate_percent"], reverse=True)

            # Get brand stats for same period
            brand_total = db.query(CitationTracking).filter(
                CitationTracking.created_at >= cutoff_date
            )
            if platform:
                brand_total = brand_total.filter(CitationTracking.platform == platform)

            brand_count = brand_total.count()
            brand_mentioned = brand_total.filter(
                CitationTracking.brand_mentioned == True
            ).count()
            brand_rate = round(brand_mentioned / brand_count * 100, 1) if brand_count > 0 else 0

            generation_time_ms = int((time.time() - start_time) * 1000)

            return {
                "request_id": request_id,
                "period_days": days,
                "brand_stats": {
                    "brand": BRAND_NAME,
                    "total_queries": brand_count,
                    "times_mentioned": brand_mentioned,
                    "citation_rate_percent": brand_rate,
                },
                "competitors": competitor_comparison,
                "monitored_competitors": COMPETITOR_BRANDS,
                "metadata": {
                    "generation_time_ms": generation_time_ms,
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                },
                "status": "success"
            }
        finally:
            db.close()

    except Exception as e:
        logger.error(f"[{request_id}] Error getting competitor citations: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "CompetitorCitationError",
                "message": f"Failed to get competitor citations: {str(e)}",
                "request_id": request_id,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        )


# ============================================================================
# Content Optimization Endpoints
# ============================================================================

@router.post(
    "/content/optimize",
    summary="Optimize content for AI citations",
    description="Analyze and optimize existing content to improve AI citation rates"
)
async def optimize_content_for_citations(
    request: ContentOptimizeRequest,
    request_id: str = Depends(get_request_id)
) -> Dict[str, Any]:
    """
    Optimize content for better AI assistant citation.

    Uses the AEO agent to analyze content and provide optimization suggestions.
    """
    logger.info(f"[{request_id}] Optimizing content for citations: level={request.optimization_level}")
    start_time = time.time()

    try:
        agent = AEOAgent()

        # Build optimization prompt
        target_queries_text = ""
        if request.target_queries:
            target_queries_text = "\n".join(f"- {q}" for q in request.target_queries)

        prompt = f"""Analyze the following content for AI citation optimization and provide specific improvements.

CONTENT TO OPTIMIZE:
{request.content[:10000]}

TARGET QUERIES THIS SHOULD RANK FOR:
{target_queries_text if target_queries_text else "General product discovery and educational queries"}

OPTIMIZATION LEVEL: {request.optimization_level}

Provide your analysis as a structured response with:

1. CITATION READINESS SCORE (0-100): How likely AI assistants are to cite this content
2. STRENGTHS: What the content does well for AI citation
3. WEAKNESSES: What prevents AI assistants from citing this content
4. SPECIFIC IMPROVEMENTS: Concrete changes to improve citation likelihood
5. RECOMMENDED STRUCTURE: How to restructure for optimal AI parsing
6. QUERY ALIGNMENT: How well the content answers the target queries
7. OPTIMIZED VERSION SNIPPETS: Key sections rewritten for better citation

Be specific and actionable. Focus on what AI assistants look for when deciding to cite content."""

        system_context = """You are an AEO (Answer Engine Optimization) expert.
Analyze content for citation potential by AI assistants (ChatGPT, Claude, Perplexity, Google AI).
Focus on: definitive answers, structured data, authoritative tone, quotable sections,
clear headings, front-loaded answers, and specific factual content."""

        content, file_path = agent.generate_and_save(
            prompt=prompt,
            output_dir=AEO_OUTPUT_DIR,
            system_context=system_context,
            metadata={
                "type": "content_optimization",
                "optimization_level": request.optimization_level,
                "target_queries": request.target_queries,
            },
            max_tokens=4096
        )

        generation_time_ms = int((time.time() - start_time) * 1000)

        return {
            "request_id": request_id,
            "optimization_analysis": content,
            "optimization_level": request.optimization_level,
            "target_queries": request.target_queries,
            "file_path": str(file_path),
            "metadata": {
                "agent": "aeo_agent",
                "model": "claude-sonnet-4-5-20250929",
                "tokens_used": 0,
                "generation_time_ms": generation_time_ms,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            },
            "status": "success"
        }

    except Exception as e:
        logger.error(f"[{request_id}] Error optimizing content: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "ContentOptimizationError",
                "message": f"Failed to optimize content: {str(e)}",
                "request_id": request_id,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        )


@router.post(
    "/blog/generate",
    summary="Generate citation-optimized blog post",
    description="Generate a blog post optimized for AI assistant citation with optional schema markup"
)
async def generate_citation_optimized_blog(
    request: BlogGenerateRequest,
    request_id: str = Depends(get_request_id)
) -> Dict[str, Any]:
    """
    Generate a citation-optimized blog post with optional FAQ and Product schema.
    """
    logger.info(f"[{request_id}] Generating citation-optimized blog: topic='{request.topic}'")
    start_time = time.time()

    try:
        agent = AEOAgent()

        # Build target queries section
        target_queries_text = ""
        if request.target_queries:
            target_queries_text = "TARGET AI QUERIES TO ANSWER:\n" + "\n".join(
                f"- {q}" for q in request.target_queries
            )

        prompt = f"""Write a comprehensive, citation-optimized blog post.

TOPIC: {request.topic}
TARGET WORD COUNT: {request.word_count}

{target_queries_text}

CITATION OPTIMIZATION REQUIREMENTS:
1. Start with a clear, quotable summary paragraph that directly answers the topic
2. Use definitive language ("is", "means", "provides") throughout
3. Structure with clear H2/H3 headers optimized for AI parsing
4. Front-load direct answers in each section
5. Include specific details, statistics, and expert-level information
6. Make each section independently valuable and quotable
7. Use the Infinity Vault brand voice (confident, empowering, battle-ready)
8. Include natural product mentions where relevant
9. End with clear takeaways and actionable advice
10. Optimize for both human readers and AI extraction

STRUCTURE:
- **Title**: SEO-optimized, question-answering title
- **Summary**: 2-3 sentence quotable answer (the key citation target)
- **Introduction**: Why this matters to the reader
- **Main Sections**: Detailed, authoritative content with clear headers
- **FAQ Section**: 3-5 natural questions and concise answers
- **Conclusion**: Strong takeaway with call-to-action

Write the complete blog post now."""

        system_context = """You are a content strategist specializing in AEO (Answer Engine Optimization).
Create content that AI assistants (ChatGPT, Claude, Perplexity, Google AI) will want to cite.
Focus on authority, specificity, structure, and quotability.
Use the Infinity Vault brand voice: confident, empowering, battle-ready."""

        content, file_path = agent.generate_and_save(
            prompt=prompt,
            output_dir=AEO_OUTPUT_DIR,
            system_context=system_context,
            metadata={
                "type": "citation_optimized_blog",
                "topic": request.topic,
                "target_queries": request.target_queries,
                "word_count": request.word_count,
            },
            max_tokens=8192
        )

        response_data = {
            "request_id": request_id,
            "content": content,
            "file_path": str(file_path),
            "topic": request.topic,
            "schemas": {},
            "metadata": {
                "agent": "aeo_agent",
                "model": "claude-sonnet-4-5-20250929",
                "tokens_used": 0,
                "generation_time_ms": 0,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            },
            "status": "success"
        }

        # Generate FAQ schema if requested
        if request.include_faq_schema:
            try:
                # Extract FAQ items from the generated content
                faq_items = _extract_faq_from_content(content)
                if faq_items:
                    faq_schema = agent.generate_faq_schema(faq_items=faq_items)
                    response_data["schemas"]["faq"] = json.loads(faq_schema)
            except Exception as schema_err:
                logger.warning(f"[{request_id}] FAQ schema generation failed: {schema_err}")
                response_data["schemas"]["faq_error"] = str(schema_err)

        generation_time_ms = int((time.time() - start_time) * 1000)
        response_data["metadata"]["generation_time_ms"] = generation_time_ms

        logger.info(f"[{request_id}] Generated citation-optimized blog in {generation_time_ms}ms")
        return response_data

    except Exception as e:
        logger.error(f"[{request_id}] Error generating citation blog: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "BlogGenerationError",
                "message": f"Failed to generate citation-optimized blog: {str(e)}",
                "request_id": request_id,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        )


# ============================================================================
# Metrics & Dashboard Endpoints
# ============================================================================

@router.get(
    "/metrics/dashboard",
    summary="Get AEO metrics and trends",
    description="Get comprehensive AEO performance metrics for the dashboard"
)
async def get_aeo_dashboard_metrics(
    request_id: str = Depends(get_request_id),
    days: int = Query(30, ge=1, le=365, description="Number of days for trend data"),
) -> Dict[str, Any]:
    """
    Get comprehensive AEO metrics for the dashboard including
    citation rates, trends, platform breakdowns, and opportunity scoring.
    """
    logger.info(f"[{request_id}] Getting AEO dashboard metrics: days={days}")
    start_time = time.time()

    try:
        db = get_db_session()
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            prev_cutoff_date = cutoff_date - timedelta(days=days)

            # Current period stats
            current_total = db.query(CitationTracking).filter(
                CitationTracking.created_at >= cutoff_date
            ).count()

            current_mentioned = db.query(CitationTracking).filter(
                CitationTracking.created_at >= cutoff_date,
                CitationTracking.brand_mentioned == True
            ).count()

            current_rate = round(current_mentioned / current_total * 100, 1) if current_total > 0 else 0

            # Previous period stats (for trend)
            prev_total = db.query(CitationTracking).filter(
                CitationTracking.created_at >= prev_cutoff_date,
                CitationTracking.created_at < cutoff_date
            ).count()

            prev_mentioned = db.query(CitationTracking).filter(
                CitationTracking.created_at >= prev_cutoff_date,
                CitationTracking.created_at < cutoff_date,
                CitationTracking.brand_mentioned == True
            ).count()

            prev_rate = round(prev_mentioned / prev_total * 100, 1) if prev_total > 0 else 0
            rate_change = round(current_rate - prev_rate, 1)

            # Average opportunity score
            avg_opportunity = db.query(
                func.avg(CitationTracking.opportunity_score)
            ).filter(
                CitationTracking.created_at >= cutoff_date
            ).scalar()
            avg_opportunity = round(float(avg_opportunity), 1) if avg_opportunity else 0

            # Platform breakdown
            platform_data = db.query(
                CitationTracking.platform,
                func.count(CitationTracking.id).label("total"),
                func.sum(
                    func.cast(CitationTracking.brand_mentioned, Integer)
                ).label("mentioned"),
                func.avg(CitationTracking.opportunity_score).label("avg_score")
            ).filter(
                CitationTracking.created_at >= cutoff_date
            ).group_by(CitationTracking.platform).all()

            platforms = {}
            for row in platform_data:
                total = row.total or 0
                mentioned = row.mentioned or 0
                platforms[row.platform] = {
                    "total_queries": total,
                    "brand_mentioned": mentioned,
                    "citation_rate": round(mentioned / total * 100, 1) if total > 0 else 0,
                    "avg_opportunity_score": round(float(row.avg_score), 1) if row.avg_score else 0,
                }

            # Category breakdown
            category_data = db.query(
                CitationTracking.query_category,
                func.count(CitationTracking.id).label("total"),
                func.sum(
                    func.cast(CitationTracking.brand_mentioned, Integer)
                ).label("mentioned")
            ).filter(
                CitationTracking.created_at >= cutoff_date,
                CitationTracking.query_category.isnot(None)
            ).group_by(CitationTracking.query_category).all()

            categories = {}
            for row in category_data:
                total = row.total or 0
                mentioned = row.mentioned or 0
                categories[row.query_category] = {
                    "total": total,
                    "mentioned": mentioned,
                    "citation_rate": round(mentioned / total * 100, 1) if total > 0 else 0,
                }

            # Top opportunities (highest opportunity score, not mentioned)
            top_opportunities = db.query(CitationTracking).filter(
                CitationTracking.created_at >= cutoff_date,
                CitationTracking.brand_mentioned == False,
                CitationTracking.opportunity_score >= AEO_CONFIG.get("opportunity_score_medium", 40)
            ).order_by(
                desc(CitationTracking.opportunity_score)
            ).limit(10).all()

            opportunities_list = []
            for opp in top_opportunities:
                opportunities_list.append({
                    "query": opp.query,
                    "platform": opp.platform,
                    "opportunity_score": opp.opportunity_score,
                    "query_category": opp.query_category,
                })

            # Pending recommendations count
            pending_recommendations = db.query(OptimizationRecommendation).filter(
                OptimizationRecommendation.status == "pending"
            ).count()

            # Competitor overview
            competitor_overview = db.query(
                CompetitorCitation.competitor_name,
                func.count(CompetitorCitation.id).label("total"),
                func.sum(
                    func.cast(CompetitorCitation.competitor_mentioned, Integer)
                ).label("mentioned")
            ).filter(
                CompetitorCitation.query_timestamp >= cutoff_date
            ).group_by(CompetitorCitation.competitor_name).all()

            top_competitors = []
            for comp in competitor_overview:
                total = comp.total or 0
                mentioned = comp.mentioned or 0
                top_competitors.append({
                    "name": comp.competitor_name,
                    "citation_rate": round(mentioned / total * 100, 1) if total > 0 else 0,
                    "total_queries": total,
                })
            top_competitors.sort(key=lambda x: x["citation_rate"], reverse=True)

            generation_time_ms = int((time.time() - start_time) * 1000)

            return {
                "request_id": request_id,
                "overview": {
                    "citation_rate_percent": current_rate,
                    "citation_rate_change": rate_change,
                    "total_queries_tracked": current_total,
                    "brand_mentions": current_mentioned,
                    "avg_opportunity_score": avg_opportunity,
                    "pending_recommendations": pending_recommendations,
                    "period_days": days,
                },
                "platforms": platforms,
                "categories": categories,
                "top_opportunities": opportunities_list,
                "top_competitors": top_competitors[:5],
                "thresholds": {
                    "high_opportunity": AEO_CONFIG.get("opportunity_score_high", 70),
                    "medium_opportunity": AEO_CONFIG.get("opportunity_score_medium", 40),
                    "alert_citation_drop": AEO_CONFIG.get("alert_citation_drop_percent", 20),
                },
                "metadata": {
                    "generation_time_ms": generation_time_ms,
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                },
                "status": "success"
            }
        finally:
            db.close()

    except Exception as e:
        logger.error(f"[{request_id}] Error getting AEO metrics: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "AEOMetricsError",
                "message": f"Failed to get AEO metrics: {str(e)}",
                "request_id": request_id,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        )


# ============================================================================
# Helper Functions
# ============================================================================

def _extract_faq_from_content(content: str) -> List[Dict[str, str]]:
    """
    Extract FAQ question/answer pairs from generated blog content.

    Looks for patterns like "## Q: ..." or "**Q:** ..." followed by answer text.
    """
    faq_items = []
    lines = content.split("\n")
    current_question = None
    current_answer_lines = []

    for line in lines:
        stripped = line.strip()

        # Detect question patterns
        is_question = False
        question_text = ""

        if stripped.startswith("## ") and stripped.endswith("?"):
            question_text = stripped.lstrip("#").strip()
            is_question = True
        elif stripped.startswith("**Q:") or stripped.startswith("**Q."):
            question_text = stripped.replace("**Q:", "").replace("**Q.", "").strip().rstrip("**")
            is_question = True
        elif stripped.startswith("### ") and "?" in stripped:
            question_text = stripped.lstrip("#").strip()
            is_question = True

        if is_question and question_text:
            # Save previous Q&A pair
            if current_question and current_answer_lines:
                answer = " ".join(current_answer_lines).strip()
                if answer:
                    faq_items.append({
                        "question": current_question,
                        "answer": answer
                    })
            current_question = question_text
            current_answer_lines = []
        elif current_question and stripped and not stripped.startswith("#"):
            # Accumulate answer lines (skip empty lines and headers)
            clean_line = stripped.lstrip("**A:** ").lstrip("**A.** ").lstrip("A: ")
            if clean_line:
                current_answer_lines.append(clean_line)

    # Save last Q&A pair
    if current_question and current_answer_lines:
        answer = " ".join(current_answer_lines).strip()
        if answer:
            faq_items.append({
                "question": current_question,
                "answer": answer
            })

    return faq_items
