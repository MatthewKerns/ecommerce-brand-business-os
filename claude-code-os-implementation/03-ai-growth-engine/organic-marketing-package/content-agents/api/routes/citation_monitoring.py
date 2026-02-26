"""
Citation monitoring routes.

This module defines API endpoints for AI citation monitoring and optimization.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
import logging
import time

from api.dependencies import get_request_id
from api.models import ErrorResponse
from pydantic import BaseModel, Field

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/citation-monitoring",
    tags=["citation-monitoring"],
    responses={
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)


# ============================================================================
# Request Models
# ============================================================================

class TestQueryRequest(BaseModel):
    """Request model for testing AI assistant queries."""
    query: str = Field(
        ...,
        min_length=5,
        max_length=500,
        description="The test query to send to AI assistants"
    )
    platforms: List[str] = Field(
        default=["chatgpt", "claude", "perplexity"],
        description="AI platforms to query (chatgpt, claude, perplexity)"
    )
    brand_name: str = Field(
        default="BattlBox",
        description="Brand name to monitor for citations"
    )
    competitor_names: Optional[List[str]] = Field(
        default_factory=list,
        description="Competitor names to track"
    )
    save_to_db: bool = Field(
        default=True,
        description="Whether to save results to database"
    )
    model: Optional[str] = Field(
        None,
        description="Specific AI model to use (platform-dependent)"
    )
    temperature: float = Field(
        default=1.0,
        ge=0.0,
        le=2.0,
        description="Temperature for AI response generation"
    )
    timeout: int = Field(
        default=30,
        ge=5,
        le=120,
        description="Timeout in seconds for each query"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "query": "What are the best tactical gear subscription boxes?",
                "platforms": ["chatgpt", "claude"],
                "brand_name": "BattlBox",
                "competitor_names": ["Carnivore Club", "Tactical Gear Box"],
                "save_to_db": True,
                "temperature": 1.0,
                "timeout": 30
            }
        }


class CitationAnalysisRequest(BaseModel):
    """Request model for analyzing citation patterns."""
    days: int = Field(
        default=30,
        ge=1,
        le=365,
        description="Number of days to analyze"
    )
    platform: Optional[str] = Field(
        None,
        pattern="^(chatgpt|claude|perplexity)$",
        description="Filter by specific AI platform"
    )
    brand_name: str = Field(
        default="BattlBox",
        description="Brand name to analyze"
    )
    include_competitors: bool = Field(
        default=True,
        description="Whether to include competitor comparison"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "days": 30,
                "platform": "chatgpt",
                "brand_name": "BattlBox",
                "include_competitors": True
            }
        }


class RecommendationRequest(BaseModel):
    """Request model for generating optimization recommendations."""
    days: int = Field(
        default=30,
        ge=7,
        le=365,
        description="Number of days to analyze for recommendations"
    )
    platform: Optional[str] = Field(
        None,
        pattern="^(chatgpt|claude|perplexity)$",
        description="Focus recommendations for specific platform"
    )
    brand_name: str = Field(
        default="BattlBox",
        description="Brand name"
    )
    competitor_names: Optional[List[str]] = Field(
        default_factory=list,
        description="Competitor names for comparison"
    )
    save_to_db: bool = Field(
        default=True,
        description="Whether to save recommendations to database"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "days": 30,
                "platform": "chatgpt",
                "brand_name": "BattlBox",
                "competitor_names": ["Carnivore Club", "Tactical Gear Box"],
                "save_to_db": True
            }
        }


# ============================================================================
# Response Models
# ============================================================================

class CitationResult(BaseModel):
    """Citation result for a single AI platform."""
    platform: str = Field(
        ...,
        description="AI platform (chatgpt, claude, perplexity)"
    )
    brand_mentioned: bool = Field(
        ...,
        description="Whether brand was mentioned"
    )
    citation_context: Optional[str] = Field(
        None,
        description="Context snippet of brand mention"
    )
    position_in_response: Optional[int] = Field(
        None,
        description="Position of brand mention (1st, 2nd, etc.)"
    )
    competitors_mentioned: List[str] = Field(
        default_factory=list,
        description="List of competitors mentioned"
    )
    response_time_ms: int = Field(
        ...,
        description="Response time in milliseconds"
    )
    response_text: str = Field(
        ...,
        description="Full response from AI assistant"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "platform": "chatgpt",
                "brand_mentioned": True,
                "citation_context": "...BattlBox offers a curated selection of tactical and survival gear...",
                "position_in_response": 2,
                "competitors_mentioned": ["Carnivore Club"],
                "response_time_ms": 2341,
                "response_text": "When looking for tactical gear subscription boxes..."
            }
        }


class TestQueryResponse(BaseModel):
    """Response model for test query results."""
    request_id: str = Field(
        ...,
        description="Unique identifier for the request"
    )
    query: str = Field(
        ...,
        description="The test query that was sent"
    )
    results: List[CitationResult] = Field(
        ...,
        description="Citation results from each platform"
    )
    brand_name: str = Field(
        ...,
        description="Brand name that was monitored"
    )
    total_platforms: int = Field(
        ...,
        description="Number of platforms queried"
    )
    citations_found: int = Field(
        ...,
        description="Number of platforms where brand was cited"
    )
    citation_rate: float = Field(
        ...,
        description="Citation rate (0.0 - 1.0)"
    )
    timestamp: datetime = Field(
        ...,
        description="Timestamp of the test"
    )
    saved_to_db: bool = Field(
        ...,
        description="Whether results were saved to database"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "request_id": "req_abc123def456",
                "query": "What are the best tactical gear subscription boxes?",
                "results": [
                    {
                        "platform": "chatgpt",
                        "brand_mentioned": True,
                        "citation_context": "...BattlBox offers a curated selection...",
                        "position_in_response": 2,
                        "competitors_mentioned": ["Carnivore Club"],
                        "response_time_ms": 2341,
                        "response_text": "When looking for tactical gear..."
                    }
                ],
                "brand_name": "BattlBox",
                "total_platforms": 3,
                "citations_found": 2,
                "citation_rate": 0.67,
                "timestamp": "2024-02-26T10:30:45Z",
                "saved_to_db": True
            }
        }


class CitationRecordResponse(BaseModel):
    """Response model for a single citation record."""
    id: int = Field(
        ...,
        description="Citation record ID"
    )
    query: str = Field(
        ...,
        description="The test query"
    )
    ai_platform: str = Field(
        ...,
        description="AI platform (chatgpt, claude, perplexity)"
    )
    brand_mentioned: bool = Field(
        ...,
        description="Whether brand was mentioned"
    )
    citation_context: Optional[str] = Field(
        None,
        description="Context snippet of brand mention"
    )
    position_in_response: Optional[int] = Field(
        None,
        description="Position of brand mention"
    )
    competitor_mentioned: bool = Field(
        ...,
        description="Whether competitors were mentioned"
    )
    query_timestamp: datetime = Field(
        ...,
        description="When query was executed"
    )
    response_time_ms: Optional[int] = Field(
        None,
        description="Response time in milliseconds"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "id": 123,
                "query": "Best tactical gear subscription boxes",
                "ai_platform": "chatgpt",
                "brand_mentioned": True,
                "citation_context": "...BattlBox offers a curated selection...",
                "position_in_response": 2,
                "competitor_mentioned": True,
                "query_timestamp": "2024-02-26T10:30:45Z",
                "response_time_ms": 2341
            }
        }


class CitationListResponse(BaseModel):
    """Response model for list of citation records."""
    request_id: str = Field(
        ...,
        description="Unique identifier for the request"
    )
    citations: List[CitationRecordResponse] = Field(
        ...,
        description="List of citation records"
    )
    total_count: int = Field(
        ...,
        description="Total number of records"
    )
    filter_days: Optional[int] = Field(
        None,
        description="Number of days filtered"
    )
    filter_platform: Optional[str] = Field(
        None,
        description="Platform filter applied"
    )
    citation_rate: float = Field(
        ...,
        description="Overall citation rate (0.0 - 1.0)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "request_id": "req_abc123def456",
                "citations": [],
                "total_count": 45,
                "filter_days": 30,
                "filter_platform": "chatgpt",
                "citation_rate": 0.67
            }
        }


class RecommendationResponse(BaseModel):
    """Response model for a single optimization recommendation."""
    id: int = Field(
        ...,
        description="Recommendation ID"
    )
    recommendation_type: str = Field(
        ...,
        description="Type (content, keyword, structure, technical, other)"
    )
    title: str = Field(
        ...,
        description="Short title"
    )
    description: str = Field(
        ...,
        description="Detailed description"
    )
    priority: str = Field(
        ...,
        description="Priority level (high, medium, low)"
    )
    status: str = Field(
        ...,
        description="Status (pending, implemented, dismissed, archived)"
    )
    ai_platform: Optional[str] = Field(
        None,
        description="Target platform (chatgpt, claude, perplexity, all)"
    )
    expected_impact: Optional[int] = Field(
        None,
        description="Expected impact score (0-100)"
    )
    actual_impact: Optional[int] = Field(
        None,
        description="Measured impact score (0-100)"
    )
    implementation_effort: Optional[str] = Field(
        None,
        description="Estimated effort (low, medium, high)"
    )
    created_at: datetime = Field(
        ...,
        description="Creation timestamp"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "id": 45,
                "recommendation_type": "content",
                "title": "Improve product comparison content",
                "description": "Add detailed comparison tables showing BattlBox vs competitors...",
                "priority": "high",
                "status": "pending",
                "ai_platform": "chatgpt",
                "expected_impact": 75,
                "actual_impact": None,
                "implementation_effort": "medium",
                "created_at": "2024-02-26T10:30:45Z"
            }
        }


class RecommendationListResponse(BaseModel):
    """Response model for list of optimization recommendations."""
    request_id: str = Field(
        ...,
        description="Unique identifier for the request"
    )
    recommendations: List[RecommendationResponse] = Field(
        ...,
        description="List of recommendations"
    )
    total_count: int = Field(
        ...,
        description="Total number of recommendations"
    )
    by_priority: Dict[str, int] = Field(
        ...,
        description="Count by priority level"
    )
    by_type: Dict[str, int] = Field(
        ...,
        description="Count by recommendation type"
    )
    by_status: Dict[str, int] = Field(
        ...,
        description="Count by status"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "request_id": "req_abc123def456",
                "recommendations": [],
                "total_count": 12,
                "by_priority": {"high": 3, "medium": 6, "low": 3},
                "by_type": {"content": 5, "keyword": 4, "structure": 3},
                "by_status": {"pending": 10, "implemented": 2}
            }
        }


class ComparisonStats(BaseModel):
    """Statistics for brand or competitor."""
    name: str = Field(
        ...,
        description="Brand or competitor name"
    )
    total_queries: int = Field(
        ...,
        description="Total number of queries"
    )
    citations: int = Field(
        ...,
        description="Number of citations"
    )
    citation_rate: float = Field(
        ...,
        description="Citation rate (0.0 - 1.0)"
    )
    average_position: Optional[float] = Field(
        None,
        description="Average position when cited"
    )
    by_platform: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict,
        description="Platform-specific statistics"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "name": "BattlBox",
                "total_queries": 45,
                "citations": 30,
                "citation_rate": 0.67,
                "average_position": 1.8,
                "by_platform": {
                    "chatgpt": {
                        "queries": 15,
                        "citations": 12,
                        "citation_rate": 0.8
                    }
                }
            }
        }


class ComparisonResponse(BaseModel):
    """Response model for competitor comparison analysis."""
    request_id: str = Field(
        ...,
        description="Unique identifier for the request"
    )
    brand_stats: ComparisonStats = Field(
        ...,
        description="Statistics for the brand"
    )
    competitor_stats: List[ComparisonStats] = Field(
        default_factory=list,
        description="Statistics for competitors"
    )
    analysis_period_days: int = Field(
        ...,
        description="Number of days analyzed"
    )
    platform_filter: Optional[str] = Field(
        None,
        description="Platform filter applied"
    )
    summary: Dict[str, Any] = Field(
        ...,
        description="Summary insights and recommendations"
    )
    timestamp: datetime = Field(
        ...,
        description="Analysis timestamp"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "request_id": "req_abc123def456",
                "brand_stats": {
                    "name": "BattlBox",
                    "total_queries": 45,
                    "citations": 30,
                    "citation_rate": 0.67,
                    "average_position": 1.8
                },
                "competitor_stats": [],
                "analysis_period_days": 30,
                "platform_filter": None,
                "summary": {
                    "brand_rank": 2,
                    "leading_competitor": "Carnivore Club",
                    "recommended_actions": []
                },
                "timestamp": "2024-02-26T10:30:45Z"
            }
        }


# ============================================================================
# Route Handlers
# ============================================================================

@router.post(
    "/test-query",
    response_model=TestQueryResponse,
    summary="Test AI assistant query",
    description="Send a test query to AI assistants and analyze brand citations"
)
async def test_query(
    request: TestQueryRequest,
    request_id: str = Depends(get_request_id)
) -> Dict[str, Any]:
    """
    Test query against AI assistants and analyze citations.

    Args:
        request: Test query request with query text and platforms
        request_id: Unique request identifier

    Returns:
        Test query response with citation results from each platform

    Raises:
        HTTPException: If query execution fails
    """
    logger.info(
        f"[{request_id}] Testing query on platforms: {request.platforms}, "
        f"query='{request.query[:50]}...'"
    )
    start_time = time.time()

    try:
        # Import agent and database dependencies
        from agents.citation_monitoring_agent import CitationMonitoringAgent
        from database.models import CitationRecord, CompetitorCitation
        from database.connection import get_db_session

        # Initialize agent
        agent = CitationMonitoringAgent()

        # Validate platforms
        available_platforms = agent.get_available_platforms()
        invalid_platforms = [p for p in request.platforms if p.lower() not in available_platforms]
        if invalid_platforms:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "InvalidPlatformsError",
                    "message": f"The following platforms are not available: {', '.join(invalid_platforms)}",
                    "available_platforms": available_platforms,
                    "request_id": request_id,
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                }
            )

        # Process each platform
        results = []
        db_session = get_db_session() if request.save_to_db else None

        try:
            for platform in request.platforms:
                platform_lower = platform.lower()
                logger.info(f"[{request_id}] Querying {platform_lower}...")
                platform_start_time = time.time()

                try:
                    # Build query kwargs
                    query_kwargs = {}
                    if request.model:
                        query_kwargs['model'] = request.model
                    if request.temperature is not None:
                        query_kwargs['temperature'] = request.temperature
                    if request.timeout:
                        query_kwargs['timeout'] = request.timeout

                    # Query the AI assistant
                    response = agent.query_ai_assistant(
                        query=request.query,
                        platform=platform_lower,
                        **query_kwargs
                    )

                    # Extract response text based on platform
                    if platform_lower == "chatgpt" or platform_lower == "perplexity":
                        response_text = response.get('choices', [{}])[0].get('message', {}).get('content', '')
                    elif platform_lower == "claude":
                        content_blocks = response.get('content', [])
                        response_text = ' '.join([block.get('text', '') for block in content_blocks if block.get('type') == 'text'])
                    else:
                        response_text = str(response)

                    # Calculate response time
                    response_time_ms = int((time.time() - platform_start_time) * 1000)

                    # Analyze citation
                    analysis = agent.analyze_citation(
                        query=request.query,
                        response_text=response_text,
                        platform=platform_lower,
                        brand_name=request.brand_name,
                        competitor_names=request.competitor_names if request.competitor_names else None,
                        response_metadata=response
                    )

                    # Build citation result
                    competitors_mentioned = [
                        comp['competitor_name']
                        for comp in analysis.get('competitor_details', [])
                        if comp.get('mentioned', False)
                    ]

                    citation_result = CitationResult(
                        platform=platform_lower,
                        brand_mentioned=analysis['brand_mentioned'],
                        citation_context=analysis['citation_context'],
                        position_in_response=analysis['position_in_response'],
                        competitors_mentioned=competitors_mentioned,
                        response_time_ms=response_time_ms,
                        response_text=response_text
                    )
                    results.append(citation_result)

                    # Save to database if requested
                    if request.save_to_db and db_session:
                        # Save citation record
                        citation_record = CitationRecord(
                            query=request.query,
                            ai_platform=platform_lower,
                            response_text=response_text,
                            brand_mentioned=analysis['brand_mentioned'],
                            citation_context=analysis['citation_context'],
                            position_in_response=analysis['position_in_response'],
                            brand_name=request.brand_name,
                            competitor_mentioned=analysis['competitor_mentioned'],
                            response_metadata=None,  # Could serialize response here if needed
                            query_timestamp=datetime.utcnow(),
                            response_time_ms=response_time_ms
                        )
                        db_session.add(citation_record)
                        db_session.flush()  # Flush to get the ID

                        # Save competitor citations
                        for comp_detail in analysis.get('competitor_details', []):
                            if comp_detail.get('mentioned', False):
                                competitor_citation = CompetitorCitation(
                                    query=request.query,
                                    ai_platform=platform_lower,
                                    competitor_name=comp_detail['competitor_name'],
                                    competitor_mentioned=True,
                                    citation_context=comp_detail.get('citation_context'),
                                    position_in_response=comp_detail.get('position_in_response'),
                                    response_text=response_text,
                                    response_time_ms=response_time_ms,
                                    citation_record_id=citation_record.id,
                                    query_timestamp=datetime.utcnow()
                                )
                                db_session.add(competitor_citation)

                        logger.debug(f"[{request_id}] Saved citation record for {platform_lower}")

                    logger.info(
                        f"[{request_id}] {platform_lower} query complete: "
                        f"brand_mentioned={analysis['brand_mentioned']}, "
                        f"competitors_found={len(competitors_mentioned)}"
                    )

                except Exception as e:
                    logger.error(f"[{request_id}] Error querying {platform_lower}: {e}", exc_info=True)
                    # Continue with other platforms instead of failing completely
                    citation_result = CitationResult(
                        platform=platform_lower,
                        brand_mentioned=False,
                        citation_context=None,
                        position_in_response=None,
                        competitors_mentioned=[],
                        response_time_ms=int((time.time() - platform_start_time) * 1000),
                        response_text=f"Error: {str(e)}"
                    )
                    results.append(citation_result)

            # Commit database changes if any
            if request.save_to_db and db_session:
                db_session.commit()
                logger.info(f"[{request_id}] Committed citation records to database")

        finally:
            # Close database session
            if db_session:
                db_session.close()

        # Calculate statistics
        total_platforms = len(results)
        citations_found = sum(1 for r in results if r.brand_mentioned)
        citation_rate = citations_found / total_platforms if total_platforms > 0 else 0.0

        # Calculate total time
        total_time_ms = int((time.time() - start_time) * 1000)

        # Build response
        response = {
            "request_id": request_id,
            "query": request.query,
            "results": [r.dict() for r in results],
            "brand_name": request.brand_name,
            "total_platforms": total_platforms,
            "citations_found": citations_found,
            "citation_rate": citation_rate,
            "timestamp": datetime.utcnow(),
            "saved_to_db": request.save_to_db
        }

        logger.info(
            f"[{request_id}] Query test complete in {total_time_ms}ms: "
            f"{citations_found}/{total_platforms} platforms cited brand "
            f"({citation_rate*100:.1f}% citation rate)"
        )
        return response

    except HTTPException:
        # Re-raise HTTP exceptions
        raise

    except Exception as e:
        logger.error(f"[{request_id}] Error testing query: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "QueryTestError",
                "message": f"Failed to test query: {str(e)}",
                "request_id": request_id,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        )


@router.get(
    "/citations",
    response_model=CitationListResponse,
    summary="Get citation records",
    description="Retrieve citation records with optional filtering by date range, platform, and brand"
)
async def get_citations(
    days: Optional[int] = Query(
        default=30,
        ge=1,
        le=365,
        description="Number of days to retrieve (from today backwards)"
    ),
    platform: Optional[str] = Query(
        default=None,
        pattern="^(chatgpt|claude|perplexity)$",
        description="Filter by AI platform"
    ),
    brand_name: Optional[str] = Query(
        default="BattlBox",
        description="Filter by brand name"
    ),
    limit: Optional[int] = Query(
        default=100,
        ge=1,
        le=1000,
        description="Maximum number of records to return"
    ),
    request_id: str = Depends(get_request_id)
) -> Dict[str, Any]:
    """
    Get citation records with optional filtering.

    Args:
        days: Number of days to retrieve (from today backwards)
        platform: Filter by specific AI platform
        brand_name: Filter by brand name
        limit: Maximum number of records to return
        request_id: Unique request identifier

    Returns:
        Citation list response with citation records and statistics

    Raises:
        HTTPException: If database query fails
    """
    logger.info(
        f"[{request_id}] Retrieving citations: days={days}, "
        f"platform={platform}, brand_name={brand_name}, limit={limit}"
    )
    start_time = time.time()

    try:
        # Import database dependencies
        from database.models import CitationRecord
        from database.connection import get_db_session
        from datetime import timedelta

        # Get database session
        db_session = get_db_session()

        try:
            # Build query
            query = db_session.query(CitationRecord)

            # Apply brand filter
            if brand_name:
                query = query.filter(CitationRecord.brand_name == brand_name)

            # Apply platform filter
            if platform:
                query = query.filter(CitationRecord.ai_platform == platform.lower())

            # Apply date filter
            if days:
                cutoff_date = datetime.utcnow() - timedelta(days=days)
                query = query.filter(CitationRecord.query_timestamp >= cutoff_date)

            # Order by timestamp descending (most recent first)
            query = query.order_by(CitationRecord.query_timestamp.desc())

            # Apply limit
            query = query.limit(limit)

            # Execute query
            records = query.all()

            # Convert to response models
            citations = []
            for record in records:
                citation = CitationRecordResponse(
                    id=record.id,
                    query=record.query,
                    ai_platform=record.ai_platform,
                    brand_mentioned=record.brand_mentioned,
                    citation_context=record.citation_context,
                    position_in_response=record.position_in_response,
                    competitor_mentioned=record.competitor_mentioned,
                    query_timestamp=record.query_timestamp,
                    response_time_ms=record.response_time_ms
                )
                citations.append(citation)

            # Calculate statistics
            total_count = len(citations)
            citations_found = sum(1 for c in citations if c.brand_mentioned)
            citation_rate = citations_found / total_count if total_count > 0 else 0.0

            # Calculate query time
            query_time_ms = int((time.time() - start_time) * 1000)

            # Build response
            response = {
                "request_id": request_id,
                "citations": [c.dict() for c in citations],
                "total_count": total_count,
                "filter_days": days,
                "filter_platform": platform,
                "citation_rate": citation_rate
            }

            logger.info(
                f"[{request_id}] Retrieved {total_count} citations in {query_time_ms}ms: "
                f"citation_rate={citation_rate:.2%}"
            )
            return response

        finally:
            # Close database session
            db_session.close()

    except Exception as e:
        logger.error(f"[{request_id}] Error retrieving citations: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "CitationRetrievalError",
                "message": f"Failed to retrieve citations: {str(e)}",
                "request_id": request_id,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        )


# ============================================================================
# Additional Route Handlers (to be implemented in subsequent subtasks)
# ============================================================================

# Placeholder comment: Additional route handlers will be implemented in:
# - subtask-4-4: GET /recommendations endpoint
# - subtask-6-3: GET /alerts endpoint
