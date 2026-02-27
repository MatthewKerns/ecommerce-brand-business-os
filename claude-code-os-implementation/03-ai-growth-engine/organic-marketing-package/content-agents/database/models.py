"""
Database models for AI Content Agents.
Defines SQLAlchemy ORM models for content history, API usage, and performance metrics.
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Boolean, CheckConstraint, Column, DateTime, ForeignKey,
    Integer, Numeric, String, Text, Index
)
from sqlalchemy.orm import relationship
from .connection import Base


class ContentHistory(Base):
    """
    Stores all generated content with metadata for historical tracking and analysis.

    Attributes:
        id: Primary key
        request_id: Unique identifier for the request
        content_type: Type of content (blog, social, amazon, competitor, other)
        agent_name: Name of the agent that generated the content
        prompt: The prompt used to generate content
        parameters: JSON parameters used in generation
        content_metadata: Additional JSON metadata (maps to 'metadata' column)
        content: The generated content
        content_format: Format of the content (default: markdown)
        model: AI model used for generation
        tokens_used: Number of tokens consumed
        generation_time_ms: Time taken to generate in milliseconds
        status: Generation status (success, partial, failed, pending)
        error_message: Error details if generation failed
        created_at: Timestamp when record was created
        updated_at: Timestamp when record was last updated
        user_id: Optional user identifier
        campaign_id: Optional campaign identifier
    """
    __tablename__ = "content_history"

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Request Identification
    request_id = Column(String(50), unique=True, nullable=False, index=True)

    # Content Classification
    content_type = Column(String(20), nullable=False, index=True)
    agent_name = Column(String(50), nullable=False)

    # Request Details
    prompt = Column(Text, nullable=False)
    parameters = Column(Text)  # JSON stored as text
    content_metadata = Column("metadata", Text)  # JSON stored as text, mapped from 'metadata' column

    # Generated Content
    content = Column(Text, nullable=False)
    content_format = Column(String(20), default="markdown")

    # Generation Details
    model = Column(String(100), nullable=False)
    tokens_used = Column(Integer, nullable=False)
    generation_time_ms = Column(Integer, nullable=False)

    # Status Tracking
    status = Column(String(20), default="success")
    error_message = Column(Text)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Optional User Context
    user_id = Column(String(50), index=True)
    campaign_id = Column(String(50), index=True)

    # Relationships
    api_usage_records = relationship("APIUsage", back_populates="content", cascade="all, delete-orphan")
    performance_metrics = relationship("PerformanceMetrics", back_populates="content", cascade="all, delete-orphan")

    # Table constraints
    __table_args__ = (
        CheckConstraint(
            "content_type IN ('blog', 'social', 'amazon', 'competitor', 'other')",
            name="check_content_type"
        ),
        CheckConstraint(
            "status IN ('success', 'partial', 'failed', 'pending')",
            name="check_status"
        ),
        CheckConstraint("tokens_used >= 0", name="check_tokens_used"),
        CheckConstraint("generation_time_ms >= 0", name="check_generation_time"),
        Index("idx_content_history_type_date", "content_type", "created_at"),
    )

    def __repr__(self):
        return f"<ContentHistory(id={self.id}, request_id='{self.request_id}', type='{self.content_type}')>"


class APIUsage(Base):
    """
    Tracks all API calls to Anthropic for usage monitoring, cost management, and rate limiting.

    Attributes:
        id: Primary key
        request_id: Identifier for the request
        content_id: Foreign key to content_history
        endpoint: API endpoint called
        method: HTTP method used
        model: AI model used
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens
        total_tokens: Total tokens used
        api_latency_ms: API response latency in milliseconds
        total_request_time_ms: Total request time in milliseconds
        estimated_cost_usd: Estimated cost in USD
        status_code: HTTP status code
        success: Whether the API call succeeded
        error_type: Type of error if failed
        error_message: Error details if failed
        called_at: Timestamp of the API call
        user_id: Optional user identifier
        api_key_hash: Hash of the API key used
    """
    __tablename__ = "api_usage"

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Request Identification
    request_id = Column(String(50), nullable=False, index=True)
    content_id = Column(Integer, ForeignKey("content_history.id", ondelete="SET NULL"))

    # API Call Details
    endpoint = Column(String(100), nullable=False)
    method = Column(String(10), nullable=False)

    # Model and Tokens
    model = Column(String(100), nullable=False)
    input_tokens = Column(Integer, nullable=False, default=0)
    output_tokens = Column(Integer, nullable=False, default=0)
    total_tokens = Column(Integer, nullable=False, default=0)

    # Timing
    api_latency_ms = Column(Integer, nullable=False)
    total_request_time_ms = Column(Integer, nullable=False)

    # Cost Tracking
    estimated_cost_usd = Column(Numeric(10, 6))

    # Response Status
    status_code = Column(Integer)
    success = Column(Boolean, default=True)
    error_type = Column(String(50))
    error_message = Column(Text)

    # Timestamps
    called_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Rate Limiting Context
    user_id = Column(String(50), index=True)
    api_key_hash = Column(String(64), index=True)

    # Relationships
    content = relationship("ContentHistory", back_populates="api_usage_records")

    # Table constraints
    __table_args__ = (
        CheckConstraint("input_tokens >= 0", name="check_input_tokens"),
        CheckConstraint("output_tokens >= 0", name="check_output_tokens"),
        CheckConstraint("total_tokens >= 0", name="check_total_tokens"),
        CheckConstraint("api_latency_ms >= 0", name="check_api_latency"),
        CheckConstraint("total_request_time_ms >= 0", name="check_total_request_time"),
        CheckConstraint("status_code >= 100 AND status_code < 600", name="check_status_code"),
        Index("idx_api_usage_model_date", "model", "called_at"),
    )

    def __repr__(self):
        return f"<APIUsage(id={self.id}, request_id='{self.request_id}', model='{self.model}')>"


class PerformanceMetrics(Base):
    """
    Records detailed performance metrics for system optimization and monitoring.

    Attributes:
        id: Primary key
        request_id: Identifier for the request
        content_id: Foreign key to content_history
        total_duration_ms: Total duration in milliseconds
        prompt_preparation_ms: Time spent preparing prompt
        api_call_ms: Time spent on API call
        response_processing_ms: Time spent processing response
        file_save_ms: Time spent saving to file
        memory_usage_mb: Memory usage in megabytes
        cpu_percent: CPU usage percentage
        content_length_chars: Content length in characters
        content_length_words: Content length in words
        validation_passed: Whether validation passed
        validation_errors: JSON validation errors
        cache_hit: Whether cache was hit
        cache_key: Cache key used
        retry_count: Number of retries
        retry_reasons: JSON retry reasons
        measured_at: Timestamp of measurement
    """
    __tablename__ = "performance_metrics"

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Request Identification
    request_id = Column(String(50), nullable=False)
    content_id = Column(Integer, ForeignKey("content_history.id", ondelete="SET NULL"))

    # Performance Measurements
    total_duration_ms = Column(Integer, nullable=False)
    prompt_preparation_ms = Column(Integer)
    api_call_ms = Column(Integer, nullable=False)
    response_processing_ms = Column(Integer)
    file_save_ms = Column(Integer)

    # Resource Usage
    memory_usage_mb = Column(Numeric(10, 2))
    cpu_percent = Column(Numeric(5, 2))

    # Quality Metrics
    content_length_chars = Column(Integer)
    content_length_words = Column(Integer)
    validation_passed = Column(Boolean, default=True)
    validation_errors = Column(Text)  # JSON stored as text

    # Cache Performance
    cache_hit = Column(Boolean, default=False)
    cache_key = Column(String(255))

    # Retry Information
    retry_count = Column(Integer, default=0)
    retry_reasons = Column(Text)  # JSON stored as text

    # Timestamp
    measured_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    content = relationship("ContentHistory", back_populates="performance_metrics")

    # Table constraints
    __table_args__ = (
        CheckConstraint("total_duration_ms >= 0", name="check_total_duration"),
        CheckConstraint("api_call_ms >= 0", name="check_api_call_ms"),
        CheckConstraint("retry_count >= 0", name="check_retry_count"),
        CheckConstraint("content_length_chars >= 0", name="check_content_length_chars"),
        CheckConstraint("content_length_words >= 0", name="check_content_length_words"),
        Index("idx_perf_metrics_duration", "total_duration_ms"),
        Index("idx_perf_metrics_cache", "cache_hit", "measured_at"),
    )

    def __repr__(self):
        return f"<PerformanceMetrics(id={self.id}, request_id='{self.request_id}', duration={self.total_duration_ms}ms)>"


class AEOCitationTest(Base):
    """
    Tracks AI assistant citation tests for AEO (Agentic Engine Optimization) monitoring.

    Attributes:
        id: Primary key
        test_id: Unique identifier for the test
        query: The query sent to the AI assistant
        ai_assistant: Name of AI assistant tested (chatgpt, claude, perplexity, gemini, copilot)
        query_category: Category of query (product_discovery, problem_solving, comparison, purchase_intent, educational)
        brand_mentioned: Whether brand was mentioned in response
        brand_recommended: Whether brand was explicitly recommended
        citation_position: Position of brand mention (1-10, null if not mentioned)
        response_text: Full or partial response from AI assistant
        response_metadata: JSON metadata about the response
        test_date: When the test was performed
        tester_name: Name of person who performed the test
        notes: Additional notes or observations
        created_at: Timestamp when record was created
    """
    __tablename__ = "aeo_citation_test"
class CitationRecord(Base):
    """
    Tracks brand mentions and citations from AI assistants for monitoring and optimization.

    Attributes:
        id: Primary key
        query: The test query sent to AI assistant
        ai_platform: AI platform queried (chatgpt, claude, perplexity)
        response_text: Full response from AI assistant
        brand_mentioned: Whether brand was cited in response
        citation_context: Snippet showing how brand was mentioned
        position_in_response: Position of brand mention (1st, 2nd, etc.)
        brand_name: Name of the brand being tracked
        competitor_mentioned: Whether competitors were also mentioned
        response_metadata: JSON metadata about the response (maps to 'metadata' column)
        query_timestamp: When the query was executed
        response_time_ms: Time taken to receive response
        created_at: Timestamp when record was created
        updated_at: Timestamp when record was last updated
        campaign_id: Optional campaign identifier
    """
    __tablename__ = "citation_records"

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Test Identification
    test_id = Column(String(50), unique=True, nullable=False, index=True)

    # Query Details
    query = Column(Text, nullable=False)
    ai_assistant = Column(String(20), nullable=False, index=True)
    query_category = Column(String(30), nullable=False, index=True)

    # Citation Metrics
    brand_mentioned = Column(Boolean, default=False, nullable=False, index=True)
    brand_recommended = Column(Boolean, default=False, nullable=False)
    citation_position = Column(Integer)

    # Response Details
    response_text = Column(Text)
    response_metadata = Column(Text)  # JSON stored as text

    # Test Context
    test_date = Column(DateTime, nullable=False, index=True)
    tester_name = Column(String(100))
    notes = Column(Text)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    # Query Details
    query = Column(Text, nullable=False)
    ai_platform = Column(String(20), nullable=False, index=True)

    # Response Details
    response_text = Column(Text, nullable=False)
    response_time_ms = Column(Integer)

    # Citation Analysis
    brand_mentioned = Column(Boolean, default=False, index=True)
    citation_context = Column(Text)
    position_in_response = Column(Integer)
    brand_name = Column(String(100), nullable=False, index=True)
    competitor_mentioned = Column(Boolean, default=False)

    # Metadata
    response_metadata = Column("metadata", Text)  # JSON stored as text, mapped from 'metadata' column

    # Timestamps
    query_timestamp = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Optional Context
    campaign_id = Column(String(50), index=True)

    # Table constraints
    __table_args__ = (
        CheckConstraint(
            "ai_assistant IN ('chatgpt', 'claude', 'perplexity', 'gemini', 'copilot', 'other')",
            name="check_ai_assistant"
        ),
        CheckConstraint(
            "query_category IN ('product_discovery', 'problem_solving', 'comparison', 'purchase_intent', 'educational', 'other')",
            name="check_query_category"
        ),
        CheckConstraint("citation_position >= 1 AND citation_position <= 10", name="check_citation_position"),
        Index("idx_aeo_citation_assistant_date", "ai_assistant", "test_date"),
        Index("idx_aeo_citation_category_date", "query_category", "test_date"),
        Index("idx_aeo_citation_mentioned", "brand_mentioned", "test_date"),
    )

    def __repr__(self):
        return f"<AEOCitationTest(id={self.id}, test_id='{self.test_id}', assistant='{self.ai_assistant}', mentioned={self.brand_mentioned})>"


# Models from 010 - AEO Implementation

class AEOCitationTest(Base):
    """
    Tracks AI assistant citation tests for AEO (Agentic Engine Optimization) monitoring.

    Attributes:
        id: Primary key
        test_id: Unique identifier for the test
        query: The query sent to the AI assistant
        ai_assistant: Name of AI assistant tested (chatgpt, claude, perplexity, gemini, copilot)
        query_category: Category of query (product_discovery, problem_solving, comparison, purchase_intent, educational)
        brand_mentioned: Whether brand was mentioned in response
        brand_recommended: Whether brand was explicitly recommended
        citation_position: Position of brand mention (1-10, null if not mentioned)
        response_text: Full or partial response from AI assistant
        response_metadata: JSON metadata about the response
        test_date: When the test was performed
        tester_name: Name of person who performed the test
        notes: Additional notes or observations
        created_at: Timestamp when record was created
    """
    __tablename__ = "aeo_citation_test"
            "ai_platform IN ('chatgpt', 'claude', 'perplexity')",
            name="check_ai_platform"
        ),
        CheckConstraint("response_time_ms >= 0", name="check_response_time"),
        CheckConstraint("position_in_response >= 0", name="check_position"),
        Index("idx_citation_platform_date", "ai_platform", "query_timestamp"),
        Index("idx_citation_brand_mentioned", "brand_name", "brand_mentioned", "query_timestamp"),
    )

    def __repr__(self):
        return f"<CitationRecord(id={self.id}, brand='{self.brand_name}', platform='{self.ai_platform}', mentioned={self.brand_mentioned})>"


class CompetitorCitation(Base):
    """
    Tracks competitor mentions in AI assistant responses for comparison analysis.

    Attributes:
        id: Primary key
        query: The test query sent to AI assistant
        ai_platform: AI platform queried (chatgpt, claude, perplexity)
        competitor_name: Name of the competitor brand
        competitor_mentioned: Whether competitor was cited in response
        citation_context: Snippet showing how competitor was mentioned
        position_in_response: Position of competitor mention (1st, 2nd, etc.)
        response_text: Full response from AI assistant
        response_time_ms: Time taken to receive response
        citation_record_id: Optional foreign key to citation_record for same query
        competitor_metadata: JSON metadata about the competitor (maps to 'metadata' column)
        query_timestamp: When the query was executed
        created_at: Timestamp when record was created
        updated_at: Timestamp when record was last updated
        campaign_id: Optional campaign identifier
    """
    __tablename__ = "competitor_citations"

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Test Identification
    test_id = Column(String(50), unique=True, nullable=False, index=True)

    # Query Details
    query = Column(Text, nullable=False)
    ai_assistant = Column(String(20), nullable=False, index=True)
    query_category = Column(String(30), nullable=False, index=True)

    # Citation Metrics
    brand_mentioned = Column(Boolean, default=False, nullable=False, index=True)
    brand_recommended = Column(Boolean, default=False, nullable=False)
    citation_position = Column(Integer)

    # Response Details
    response_text = Column(Text)
    response_metadata = Column(Text)  # JSON stored as text

    # Test Context
    test_date = Column(DateTime, nullable=False, index=True)
    tester_name = Column(String(100))
    notes = Column(Text)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    # Query Details
    query = Column(Text, nullable=False)
    ai_platform = Column(String(20), nullable=False, index=True)

    # Competitor Identification
    competitor_name = Column(String(100), nullable=False, index=True)

    # Citation Analysis
    competitor_mentioned = Column(Boolean, default=False, index=True)
    citation_context = Column(Text)
    position_in_response = Column(Integer)

    # Response Details
    response_text = Column(Text, nullable=False)
    response_time_ms = Column(Integer)

    # Cross-Reference
    citation_record_id = Column(Integer, ForeignKey("citation_records.id", ondelete="SET NULL"))

    # Metadata
    competitor_metadata = Column("metadata", Text)  # JSON stored as text, mapped from 'metadata' column

    # Timestamps
    query_timestamp = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Optional Context
    campaign_id = Column(String(50), index=True)

    # Table constraints
    __table_args__ = (
        CheckConstraint(
            "ai_assistant IN ('chatgpt', 'claude', 'perplexity', 'gemini', 'copilot', 'other')",
            name="check_ai_assistant"
        ),
        CheckConstraint(
            "query_category IN ('product_discovery', 'problem_solving', 'comparison', 'purchase_intent', 'educational', 'other')",
            name="check_query_category"
        ),
        CheckConstraint("citation_position >= 1 AND citation_position <= 10", name="check_citation_position"),
        Index("idx_aeo_citation_assistant_date", "ai_assistant", "test_date"),
        Index("idx_aeo_citation_category_date", "query_category", "test_date"),
        Index("idx_aeo_citation_mentioned", "brand_mentioned", "test_date"),
    )

    def __repr__(self):
        return f"<AEOCitationTest(id={self.id}, test_id='{self.test_id}', assistant='{self.ai_assistant}', mentioned={self.brand_mentioned})>"
            "ai_platform IN ('chatgpt', 'claude', 'perplexity')",
            name="check_competitor_ai_platform"
        ),
        CheckConstraint("response_time_ms >= 0", name="check_competitor_response_time"),
        CheckConstraint("position_in_response >= 0", name="check_competitor_position"),
        Index("idx_competitor_platform_date", "ai_platform", "query_timestamp"),
        Index("idx_competitor_name_mentioned", "competitor_name", "competitor_mentioned", "query_timestamp"),
    )

    def __repr__(self):
        return f"<CompetitorCitation(id={self.id}, competitor='{self.competitor_name}', platform='{self.ai_platform}', mentioned={self.competitor_mentioned})>"


class OptimizationRecommendation(Base):
    """
    Stores AI-generated optimization recommendations for improving citation rates.

    Attributes:
        id: Primary key
        recommendation_type: Type of recommendation (content, keyword, structure, technical, other)
        title: Short title of the recommendation
        description: Detailed description of the recommendation
        priority: Priority level (high, medium, low)
        status: Implementation status (pending, implemented, dismissed, archived)
        citation_record_id: Optional foreign key to related citation record
        ai_platform: Optional AI platform this targets (chatgpt, claude, perplexity, all)
        expected_impact: Expected impact score (0-100)
        actual_impact: Measured impact score after implementation (0-100)
        implementation_effort: Estimated effort (low, medium, high)
        recommendation_metadata: JSON metadata about the recommendation (maps to 'metadata' column)
        created_at: Timestamp when recommendation was created
        updated_at: Timestamp when recommendation was last updated
        implemented_at: Timestamp when recommendation was implemented
        dismissed_at: Timestamp when recommendation was dismissed
        dismissal_reason: Reason for dismissal if status is dismissed
        campaign_id: Optional campaign identifier
        user_id: Optional user identifier
    """
    __tablename__ = "optimization_recommendations"

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Recommendation Classification
    recommendation_type = Column(String(20), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)

    # Priority and Status
    priority = Column(String(10), nullable=False, default="medium", index=True)
    status = Column(String(20), nullable=False, default="pending", index=True)

    # Cross-Reference
    citation_record_id = Column(Integer, ForeignKey("citation_records.id", ondelete="SET NULL"))
    ai_platform = Column(String(20), index=True)

    # Impact Metrics
    expected_impact = Column(Integer)
    actual_impact = Column(Integer)
    implementation_effort = Column(String(10))

    # Metadata
    recommendation_metadata = Column("metadata", Text)  # JSON stored as text, mapped from 'metadata' column

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    implemented_at = Column(DateTime)
    dismissed_at = Column(DateTime)

    # Dismissal Details
    dismissal_reason = Column(Text)

    # Optional Context
    campaign_id = Column(String(50), index=True)
    user_id = Column(String(50), index=True)

    # Table constraints
    __table_args__ = (
        CheckConstraint(
            "recommendation_type IN ('content', 'keyword', 'structure', 'technical', 'other')",
            name="check_recommendation_type"
        ),
        CheckConstraint(
            "priority IN ('high', 'medium', 'low')",
            name="check_priority"
        ),
        CheckConstraint(
            "status IN ('pending', 'implemented', 'dismissed', 'archived')",
            name="check_recommendation_status"
        ),
        CheckConstraint(
            "ai_platform IN ('chatgpt', 'claude', 'perplexity', 'all') OR ai_platform IS NULL",
            name="check_recommendation_ai_platform"
        ),
        CheckConstraint(
            "implementation_effort IN ('low', 'medium', 'high') OR implementation_effort IS NULL",
            name="check_implementation_effort"
        ),
        CheckConstraint(
            "expected_impact >= 0 AND expected_impact <= 100 OR expected_impact IS NULL",
            name="check_expected_impact"
        ),
        CheckConstraint(
            "actual_impact >= 0 AND actual_impact <= 100 OR actual_impact IS NULL",
            name="check_actual_impact"
        ),
        Index("idx_recommendation_status_priority", "status", "priority", "created_at"),
        Index("idx_recommendation_type_platform", "recommendation_type", "ai_platform"),
    )

    def __repr__(self):
        return f"<OptimizationRecommendation(id={self.id}, type='{self.recommendation_type}', priority='{self.priority}', status='{self.status}')>"


class AlertRecord(Base):
    """
    Tracks alerts for citation monitoring events such as rate drops or competitor gains.

    Attributes:
        id: Primary key
        alert_type: Type of alert (citation_drop, competitor_gain, threshold_breach, other)
        alert_severity: Severity level (high, medium, low)
        status: Alert status (active, acknowledged, resolved, dismissed)
        title: Short title of the alert
        message: Detailed alert message
        citation_record_id: Optional foreign key to related citation record
        competitor_citation_id: Optional foreign key to related competitor citation
        brand_name: Name of the brand related to alert
        competitor_name: Optional name of competitor related to alert
        ai_platform: Optional AI platform this relates to (chatgpt, claude, perplexity, all)
        metric_name: Name of metric that triggered alert
        previous_value: Previous metric value before trigger
        current_value: Current metric value that triggered alert
        threshold_value: Threshold value that was breached
        change_percentage: Percentage change in metric
        alert_metadata: JSON metadata about the alert (maps to 'metadata' column)
        triggered_at: Timestamp when alert was triggered
        acknowledged_at: Timestamp when alert was acknowledged
        acknowledged_by: User who acknowledged the alert
        resolved_at: Timestamp when alert was resolved
        resolved_by: User who resolved the alert
        dismissed_at: Timestamp when alert was dismissed
        dismissed_by: User who dismissed the alert
        dismissal_reason: Reason for dismissal if status is dismissed
        resolution_notes: Notes about resolution if status is resolved
        created_at: Timestamp when record was created
        updated_at: Timestamp when record was last updated
        campaign_id: Optional campaign identifier
        user_id: Optional user identifier
    """
    __tablename__ = "alert_records"

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Alert Classification
    alert_type = Column(String(20), nullable=False, index=True)
    alert_severity = Column(String(10), nullable=False, default="medium", index=True)
    status = Column(String(20), nullable=False, default="active", index=True)

    # Alert Content
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)

    # Cross-References
    citation_record_id = Column(Integer, ForeignKey("citation_records.id", ondelete="SET NULL"))
    competitor_citation_id = Column(Integer, ForeignKey("competitor_citations.id", ondelete="SET NULL"))

    # Context
    brand_name = Column(String(100), index=True)
    competitor_name = Column(String(100), index=True)
    ai_platform = Column(String(20), index=True)

    # Metrics
    metric_name = Column(String(100))
    previous_value = Column(Numeric(10, 2))
    current_value = Column(Numeric(10, 2))
    threshold_value = Column(Numeric(10, 2))
    change_percentage = Column(Numeric(10, 2))

    # Metadata
    alert_metadata = Column("metadata", Text)  # JSON stored as text, mapped from 'metadata' column

    # Timestamps
    triggered_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    acknowledged_at = Column(DateTime)
    resolved_at = Column(DateTime)
    dismissed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Action Tracking
    acknowledged_by = Column(String(50))
    resolved_by = Column(String(50))
    dismissed_by = Column(String(50))
    dismissal_reason = Column(Text)
    resolution_notes = Column(Text)

    # Optional Context
    campaign_id = Column(String(50), index=True)
    user_id = Column(String(50), index=True)

    # Table constraints
    __table_args__ = (
        CheckConstraint(
            "alert_type IN ('citation_drop', 'competitor_gain', 'threshold_breach', 'other')",
            name="check_alert_type"
        ),
        CheckConstraint(
            "alert_severity IN ('high', 'medium', 'low')",
            name="check_alert_severity"
        ),
        CheckConstraint(
            "status IN ('active', 'acknowledged', 'resolved', 'dismissed')",
            name="check_alert_status"
        ),
        CheckConstraint(
            "ai_platform IN ('chatgpt', 'claude', 'perplexity', 'all') OR ai_platform IS NULL",
            name="check_alert_ai_platform"
        ),
        Index("idx_alert_type_severity_status", "alert_type", "alert_severity", "status"),
        Index("idx_alert_triggered_at", "triggered_at"),
        Index("idx_alert_brand_platform", "brand_name", "ai_platform"),
    )

    def __repr__(self):
        return f"<AlertRecord(id={self.id}, type='{self.alert_type}', severity='{self.alert_severity}', status='{self.status}')>"


# Models from 011 - Citation Monitoring System

class CitationRecord(Base):
    """
    Tracks brand mentions and citations from AI assistants for monitoring and optimization.

    Attributes:
        id: Primary key
        query: The test query sent to AI assistant
        ai_platform: AI platform queried (chatgpt, claude, perplexity)
        response_text: Full response from AI assistant
        brand_mentioned: Whether brand was cited in response
        citation_context: Snippet showing how brand was mentioned
        position_in_response: Position of brand mention (1st, 2nd, etc.)
        brand_name: Name of the brand being tracked
        competitor_mentioned: Whether competitors were also mentioned
        response_metadata: JSON metadata about the response (maps to 'metadata' column)
        query_timestamp: When the query was executed
        response_time_ms: Time taken to receive response
        created_at: Timestamp when record was created
        updated_at: Timestamp when record was last updated
        campaign_id: Optional campaign identifier
    """
    __tablename__ = "citation_records"

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Query Details
    query = Column(Text, nullable=False)
    ai_platform = Column(String(20), nullable=False, index=True)

    # Response Details
    response_text = Column(Text, nullable=False)
    response_time_ms = Column(Integer)

    # Citation Analysis
    brand_mentioned = Column(Boolean, default=False, index=True)
    citation_context = Column(Text)
    position_in_response = Column(Integer)
    brand_name = Column(String(100), nullable=False, index=True)
    competitor_mentioned = Column(Boolean, default=False)

    # Metadata
    response_metadata = Column("metadata", Text)  # JSON stored as text, mapped from 'metadata' column

    # Timestamps
    query_timestamp = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Optional Context
    campaign_id = Column(String(50), index=True)

    # Table constraints
    __table_args__ = (
        CheckConstraint(
            "ai_platform IN ('chatgpt', 'claude', 'perplexity')",
            name="check_ai_platform"
        ),
        CheckConstraint("response_time_ms >= 0", name="check_response_time"),
        CheckConstraint("position_in_response >= 0", name="check_position"),
        Index("idx_citation_platform_date", "ai_platform", "query_timestamp"),
        Index("idx_citation_brand_mentioned", "brand_name", "brand_mentioned", "query_timestamp"),
    )

    def __repr__(self):
        return f"<CitationRecord(id={self.id}, brand='{self.brand_name}', platform='{self.ai_platform}', mentioned={self.brand_mentioned})>"


class CompetitorCitation(Base):
    """
    Tracks competitor mentions in AI assistant responses for comparison analysis.

    Attributes:
        id: Primary key
        query: The test query sent to AI assistant
        ai_platform: AI platform queried (chatgpt, claude, perplexity)
        competitor_name: Name of the competitor brand
        competitor_mentioned: Whether competitor was cited in response
        citation_context: Snippet showing how competitor was mentioned
        position_in_response: Position of competitor mention (1st, 2nd, etc.)
        response_text: Full response from AI assistant
        response_time_ms: Time taken to receive response
        citation_record_id: Optional foreign key to citation_record for same query
        competitor_metadata: JSON metadata about the competitor (maps to 'metadata' column)
        query_timestamp: When the query was executed
        created_at: Timestamp when record was created
        updated_at: Timestamp when record was last updated
        campaign_id: Optional campaign identifier
    """
    __tablename__ = "competitor_citations"

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Query Details
    query = Column(Text, nullable=False)
    ai_platform = Column(String(20), nullable=False, index=True)

    # Competitor Identification
    competitor_name = Column(String(100), nullable=False, index=True)

    # Citation Analysis
    competitor_mentioned = Column(Boolean, default=False, index=True)
    citation_context = Column(Text)
    position_in_response = Column(Integer)

    # Response Details
    response_text = Column(Text, nullable=False)
    response_time_ms = Column(Integer)

    # Cross-Reference
    citation_record_id = Column(Integer, ForeignKey("citation_records.id", ondelete="SET NULL"))

    # Metadata
    competitor_metadata = Column("metadata", Text)  # JSON stored as text, mapped from 'metadata' column

    # Timestamps
    query_timestamp = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Optional Context
    campaign_id = Column(String(50), index=True)

    # Table constraints
    __table_args__ = (
        CheckConstraint(
            "ai_platform IN ('chatgpt', 'claude', 'perplexity')",
            name="check_competitor_ai_platform"
        ),
        CheckConstraint("response_time_ms >= 0", name="check_competitor_response_time"),
        CheckConstraint("position_in_response >= 0", name="check_competitor_position"),
        Index("idx_competitor_platform_date", "ai_platform", "query_timestamp"),
        Index("idx_competitor_name_mentioned", "competitor_name", "competitor_mentioned", "query_timestamp"),
    )

    def __repr__(self):
        return f"<CompetitorCitation(id={self.id}, competitor='{self.competitor_name}', platform='{self.ai_platform}', mentioned={self.competitor_mentioned})>"


class OptimizationRecommendation(Base):
    """
    Stores AI-generated optimization recommendations for improving citation rates.

    Attributes:
        id: Primary key
        recommendation_type: Type of recommendation (content, keyword, structure, technical, other)
        title: Short title of the recommendation
        description: Detailed description of the recommendation
        priority: Priority level (high, medium, low)
        status: Implementation status (pending, implemented, dismissed, archived)
        citation_record_id: Optional foreign key to related citation record
        ai_platform: Optional AI platform this targets (chatgpt, claude, perplexity, all)
        expected_impact: Expected impact score (0-100)
        actual_impact: Measured impact score after implementation (0-100)
        implementation_effort: Estimated effort (low, medium, high)
        recommendation_metadata: JSON metadata about the recommendation (maps to 'metadata' column)
        created_at: Timestamp when recommendation was created
        updated_at: Timestamp when recommendation was last updated
        implemented_at: Timestamp when recommendation was implemented
        dismissed_at: Timestamp when recommendation was dismissed
        dismissal_reason: Reason for dismissal if status is dismissed
        campaign_id: Optional campaign identifier
        user_id: Optional user identifier
    """
    __tablename__ = "optimization_recommendations"

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Recommendation Classification
    recommendation_type = Column(String(20), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)

    # Priority and Status
    priority = Column(String(10), nullable=False, default="medium", index=True)
    status = Column(String(20), nullable=False, default="pending", index=True)

    # Cross-Reference
    citation_record_id = Column(Integer, ForeignKey("citation_records.id", ondelete="SET NULL"))
    ai_platform = Column(String(20), index=True)

    # Impact Metrics
    expected_impact = Column(Integer)
    actual_impact = Column(Integer)
    implementation_effort = Column(String(10))

    # Metadata
    recommendation_metadata = Column("metadata", Text)  # JSON stored as text, mapped from 'metadata' column

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    implemented_at = Column(DateTime)
    dismissed_at = Column(DateTime)

    # Dismissal Details
    dismissal_reason = Column(Text)

    # Optional Context
    campaign_id = Column(String(50), index=True)
    user_id = Column(String(50), index=True)

    # Table constraints
    __table_args__ = (
        CheckConstraint(
            "recommendation_type IN ('content', 'keyword', 'structure', 'technical', 'other')",
            name="check_recommendation_type"
        ),
        CheckConstraint(
            "priority IN ('high', 'medium', 'low')",
            name="check_priority"
        ),
        CheckConstraint(
            "status IN ('pending', 'implemented', 'dismissed', 'archived')",
            name="check_recommendation_status"
        ),
        CheckConstraint(
            "ai_platform IN ('chatgpt', 'claude', 'perplexity', 'all') OR ai_platform IS NULL",
            name="check_recommendation_ai_platform"
        ),
        CheckConstraint(
            "implementation_effort IN ('low', 'medium', 'high') OR implementation_effort IS NULL",
            name="check_implementation_effort"
        ),
        CheckConstraint(
            "expected_impact >= 0 AND expected_impact <= 100 OR expected_impact IS NULL",
            name="check_expected_impact"
        ),
        CheckConstraint(
            "actual_impact >= 0 AND actual_impact <= 100 OR actual_impact IS NULL",
            name="check_actual_impact"
        ),
        Index("idx_recommendation_status_priority", "status", "priority", "created_at"),
        Index("idx_recommendation_type_platform", "recommendation_type", "ai_platform"),
    )

    def __repr__(self):
        return f"<OptimizationRecommendation(id={self.id}, type='{self.recommendation_type}', priority='{self.priority}', status='{self.status}')>"


class AlertRecord(Base):
    """
    Tracks alerts for citation monitoring events such as rate drops or competitor gains.

    Attributes:
        id: Primary key
        alert_type: Type of alert (citation_drop, competitor_gain, threshold_breach, other)
        alert_severity: Severity level (high, medium, low)
        status: Alert status (active, acknowledged, resolved, dismissed)
        title: Short title of the alert
        message: Detailed alert message
        citation_record_id: Optional foreign key to related citation record
        competitor_citation_id: Optional foreign key to related competitor citation
        brand_name: Name of the brand related to alert
        competitor_name: Optional name of competitor related to alert
        ai_platform: Optional AI platform this relates to (chatgpt, claude, perplexity, all)
        metric_name: Name of metric that triggered alert
        previous_value: Previous metric value before trigger
        current_value: Current metric value that triggered alert
        threshold_value: Threshold value that was breached
        change_percentage: Percentage change in metric
        alert_metadata: JSON metadata about the alert (maps to 'metadata' column)
        triggered_at: Timestamp when alert was triggered
        acknowledged_at: Timestamp when alert was acknowledged
        acknowledged_by: User who acknowledged the alert
        resolved_at: Timestamp when alert was resolved
        resolved_by: User who resolved the alert
        dismissed_at: Timestamp when alert was dismissed
        dismissed_by: User who dismissed the alert
        dismissal_reason: Reason for dismissal if status is dismissed
        resolution_notes: Notes about resolution if status is resolved
        created_at: Timestamp when record was created
        updated_at: Timestamp when record was last updated
        campaign_id: Optional campaign identifier
        user_id: Optional user identifier
    """
    __tablename__ = "alert_records"

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Alert Classification
    alert_type = Column(String(20), nullable=False, index=True)
    alert_severity = Column(String(10), nullable=False, default="medium", index=True)
    status = Column(String(20), nullable=False, default="active", index=True)

    # Alert Content
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)

    # Cross-References
    citation_record_id = Column(Integer, ForeignKey("citation_records.id", ondelete="SET NULL"))
    competitor_citation_id = Column(Integer, ForeignKey("competitor_citations.id", ondelete="SET NULL"))

    # Context
    brand_name = Column(String(100), index=True)
    competitor_name = Column(String(100), index=True)
    ai_platform = Column(String(20), index=True)

    # Metrics
    metric_name = Column(String(100))
    previous_value = Column(Numeric(10, 2))
    current_value = Column(Numeric(10, 2))
    threshold_value = Column(Numeric(10, 2))
    change_percentage = Column(Numeric(10, 2))

    # Metadata
    alert_metadata = Column("metadata", Text)  # JSON stored as text, mapped from 'metadata' column

    # Timestamps
    triggered_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    acknowledged_at = Column(DateTime)
    resolved_at = Column(DateTime)
    dismissed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Action Tracking
    acknowledged_by = Column(String(50))
    resolved_by = Column(String(50))
    dismissed_by = Column(String(50))
    dismissal_reason = Column(Text)
    resolution_notes = Column(Text)

    # Optional Context
    campaign_id = Column(String(50), index=True)
    user_id = Column(String(50), index=True)

    # Table constraints
    __table_args__ = (
        CheckConstraint(
            "alert_type IN ('citation_drop', 'competitor_gain', 'threshold_breach', 'other')",
            name="check_alert_type"
        ),
        CheckConstraint(
            "alert_severity IN ('high', 'medium', 'low')",
            name="check_alert_severity"
