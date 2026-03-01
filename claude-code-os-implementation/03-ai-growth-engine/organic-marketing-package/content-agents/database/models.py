"""
Database models for AI Content Agents.
Defines SQLAlchemy ORM models for content history, API usage, and performance metrics.
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Boolean, CheckConstraint, Column, DateTime, Enum, ForeignKey,
    Integer, JSON, Numeric, String, Text, Index
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
        seo_score: SEO score (0-100)
        seo_grade: SEO grade (A, B, C, D, F)
        target_keyword: Primary target keyword for SEO
        meta_description: SEO meta description
        internal_links: JSON array of internal linking suggestions
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

    # SEO Metadata
    seo_score = Column(Numeric(5, 2))
    seo_grade = Column(String(1))
    target_keyword = Column(String(200))
    meta_description = Column(String(160))
    internal_links = Column(Text)  # JSON stored as text

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
        CheckConstraint("seo_score >= 0 AND seo_score <= 100", name="check_seo_score"),
        CheckConstraint(
            "seo_grade IN ('A', 'B', 'C', 'D', 'F')",
            name="check_seo_grade"
        ),
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


class CitationRecord(Base):
    """
    Tracks brand mentions and citations from AI assistants for manual test monitoring.

    Attributes:
        id: Primary key
        test_id: Unique identifier for the test run
        query: The test query sent to AI assistant
        ai_assistant: AI assistant queried (chatgpt, claude, perplexity, gemini, copilot, other)
        query_category: Category of query (product_discovery, comparison, etc.)
        brand_mentioned: Whether brand was cited in response
        brand_recommended: Whether brand was recommended
        citation_position: Position of brand mention (1-10)
        response_text: Full response from AI assistant
        response_metadata: JSON metadata about the response
        test_date: When the test was executed
        tester_name: Name of person who ran the test
        notes: Additional notes about the test
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
            "ai_platform IN ('chatgpt', 'claude', 'perplexity', 'gemini', 'copilot')",
            name="check_competitor_ai_platform"
        ),
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
    )


# ============================================================================
# TikTok Channel Models (from Phase 2)
# ============================================================================

class TikTokChannel(Base):
    """
    Represents a TikTok channel with element-based theming.

    Attributes:
        id: Primary key
        element: Element theme (air, water, earth, fire)
        channel_name: Full channel name
        channel_handle: TikTok username/handle
        description: Channel description
        target_audience: Target audience description
        content_focus: Content focus areas
        posting_schedule: JSON schedule configuration
        is_active: Whether channel is active
        created_at: When channel was created
        updated_at: When channel was last updated
    """
    __tablename__ = "tiktok_channels"

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Channel Identity
    element = Column(String(10), nullable=False, unique=True, index=True)
    channel_name = Column(String(100), nullable=False)
    channel_handle = Column(String(50), unique=True, index=True)

    # Channel Details
    description = Column(Text)
    target_audience = Column(Text)
    content_focus = Column(Text)

    # Schedule
    posting_schedule = Column(JSON)

    # Status
    is_active = Column(Boolean, default=True, index=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    content = relationship("ChannelContent", back_populates="channel", cascade="all, delete-orphan")
    scheduled_content = relationship("ScheduledContent", back_populates="channel", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<TikTokChannel(id={self.id}, element='{self.element}', handle='{self.channel_handle}')>"


class ChannelContent(Base):
    """
    Stores content generated for TikTok channels.

    Attributes:
        id: Primary key
        channel_id: Foreign key to TikTokChannel
        content_type: Type of content (hook, caption, hashtags, etc.)
        content_theme: Theme/topic of content
        content_text: The actual content text
        metadata: JSON metadata (keywords, tone, etc.)
        performance_score: Content performance score
        is_used: Whether content has been used
        used_at: When content was used
        created_at: When content was created
    """
    __tablename__ = "channel_content"

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Foreign Keys
    channel_id = Column(Integer, ForeignKey('tiktok_channels.id'), nullable=False, index=True)

    # Content Details
    content_type = Column(String(50), nullable=False, index=True)
    content_theme = Column(String(100))
    content_text = Column(Text, nullable=False)

    # Metadata
    content_metadata = Column("metadata", JSON)  # Mapped to 'metadata' column
    performance_score = Column(Numeric(3, 2))

    # Usage Tracking
    is_used = Column(Boolean, default=False, index=True)
    used_at = Column(DateTime)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    channel = relationship("TikTokChannel", back_populates="content")

    def __repr__(self):
        return f"<ChannelContent(id={self.id}, channel_id={self.channel_id}, type='{self.content_type}')>"


class ScheduledContent(Base):
    """
    Tracks scheduled posts for TikTok channels.

    Attributes:
        id: Primary key
        channel_id: Foreign key to TikTokChannel
        content_id: Foreign key to ChannelContent
        scheduled_time: When to post
        status: Post status (pending, posted, failed, cancelled)
        post_url: URL of posted content
        error_message: Error if posting failed
        retry_count: Number of retry attempts
        created_at: When schedule was created
        posted_at: When actually posted
    """
    __tablename__ = "scheduled_content"

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Foreign Keys
    channel_id = Column(Integer, ForeignKey('tiktok_channels.id'), nullable=False, index=True)
    content_id = Column(Integer, ForeignKey('channel_content.id'))

    # Schedule Details
    scheduled_time = Column(DateTime, nullable=False, index=True)
    status = Column(String(20), default='pending', index=True)

    # Post Results
    post_url = Column(String(500))
    error_message = Column(Text)
    retry_count = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    posted_at = Column(DateTime)

    # Relationships
    channel = relationship("TikTokChannel", back_populates="scheduled_content")

    def __repr__(self):
        return f"<ScheduledContent(id={self.id}, channel_id={self.channel_id}, status='{self.status}')>"


class PublishLog(Base):
    """
    Logs all publishing attempts and results.

    Attributes:
        id: Primary key
        scheduled_content_id: Foreign key to ScheduledContent
        attempt_number: Which attempt this was
        status: Result of attempt
        error_details: Error information if failed
        api_response: Raw API response
        attempt_time: When attempt was made
    """
    __tablename__ = "publish_log"

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Foreign Keys
    scheduled_content_id = Column(Integer, ForeignKey('scheduled_content.id'), nullable=False, index=True)

    # Log Details
    attempt_number = Column(Integer, nullable=False)
    status = Column(String(20), nullable=False, index=True)
    error_details = Column(Text)
    api_response = Column(JSON)

    # Timestamp
    attempt_time = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<PublishLog(id={self.id}, scheduled_id={self.scheduled_content_id}, status='{self.status}')>"


# ============================================================================
# Klaviyo Email Platform Models (from worktree 014)
# ============================================================================

class KlaviyoProfile(Base):
    """
    Stores customer profiles synced from Klaviyo for local tracking and analysis.
    
    This table maintains a local cache of Klaviyo customer profiles to support
    email campaign optimization and user behavior tracking without requiring
    constant API calls. It stores both Klaviyo-specific identifiers and custom
    properties relevant to our marketing automation workflows.
    
    Attributes:
        id: Primary key for local database
        klaviyo_profile_id: Unique identifier from Klaviyo
        email: Customer email address
        first_name: Customer first name
        last_name: Customer last name
        phone_number: Optional phone number
        external_id: Optional external identifier (e.g., from Clerk)
        properties: JSON field for custom properties
        lists: JSON array of list IDs the profile belongs to
        segments: JSON array of segment IDs the profile belongs to
        last_synced: Timestamp of last sync from Klaviyo
        created_at: When the local record was created
        updated_at: When the local record was last updated
    """
    __tablename__ = "klaviyo_profiles"

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Klaviyo Identifiers
    klaviyo_profile_id = Column(String(100), unique=True, nullable=False, index=True)
    
    # Contact Information
    email = Column(String(255), nullable=False, index=True)
    first_name = Column(String(100))
    last_name = Column(String(100))
    phone_number = Column(String(50))
    
    # External Integration
    external_id = Column(String(100), index=True)  # Clerk user ID
    
    # Klaviyo Data
    properties = Column(JSON, default=dict)  # Custom properties
    lists = Column(JSON, default=list)  # List memberships
    segments = Column(JSON, default=list)  # Segment memberships
    
    # Sync Metadata
    last_synced = Column(DateTime, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<KlaviyoProfile(id={self.id}, email='{self.email}', klaviyo_id='{self.klaviyo_profile_id}')>"


class KlaviyoSyncHistory(Base):
    """
    Tracks synchronization history between local database and Klaviyo.
    
    This table logs all sync operations with Klaviyo to maintain an audit trail
    and support debugging of integration issues. It captures both successful
    syncs and failures with detailed error information.
    
    Attributes:
        id: Primary key
        sync_type: Type of sync operation (e.g., 'profile_update', 'event_track')
        sync_direction: Direction of sync ('to_klaviyo', 'from_klaviyo')
        entity_type: Type of entity synced ('profile', 'event', 'list', 'segment')
        entity_id: ID of the entity being synced
        status: Sync status ('success', 'failed', 'pending')
        error_message: Error details if sync failed
        request_data: JSON of the request sent
        response_data: JSON of the response received
        started_at: When the sync started
        completed_at: When the sync completed
        created_at: When this record was created
    """
    __tablename__ = "klaviyo_sync_history"

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Sync Details
    sync_type = Column(String(50), nullable=False, index=True)
    sync_direction = Column(Enum('to_klaviyo', 'from_klaviyo'), nullable=False)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(String(100), nullable=False)
    
    # Status
    status = Column(Enum('success', 'failed', 'pending'), nullable=False, index=True)
    error_message = Column(Text)
    
    # Request/Response Data
    request_data = Column(JSON)
    response_data = Column(JSON)
    
    # Timing
    started_at = Column(DateTime, nullable=False)
    completed_at = Column(DateTime)
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<KlaviyoSyncHistory(id={self.id}, type='{self.sync_type}', status='{self.status}')>"


class KlaviyoSegment(Base):
    """
    Stores Klaviyo segment definitions for local reference.
    
    This table maintains a cache of Klaviyo segments to support rapid
    segmentation decisions and reduce API calls during campaign planning.
    
    Attributes:
        id: Primary key
        klaviyo_segment_id: Unique identifier from Klaviyo
        name: Segment name
        description: Segment description
        definition: JSON representation of segment rules
        profile_count: Number of profiles in segment (cached)
        last_synced: When segment was last synced from Klaviyo
        created_at: When local record was created
        updated_at: When local record was updated
    """
    __tablename__ = "klaviyo_segments"

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Klaviyo Data
    klaviyo_segment_id = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    definition = Column(JSON)  # Segment rules/criteria
    profile_count = Column(Integer, default=0)
    
    # Sync Metadata
    last_synced = Column(DateTime, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<KlaviyoSegment(id={self.id}, name='{self.name}', profiles={self.profile_count})>"


# ============================================================================
# AEO Citation Tracking Models (from AEO Optimizer implementation)
# ============================================================================

class CitationTracking(Base):
    """
    Tracks automated citation monitoring across AI platforms.

    This model records the results of automated queries to AI platforms
    (ChatGPT, Perplexity, Claude, Google AI) to monitor whether and how
    the brand is being cited. It captures competitor citations and calculates
    opportunity scores for optimization.

    Attributes:
        id: Primary key
        tracking_id: Unique identifier for this tracking run
        platform: AI platform queried (chatgpt, perplexity, claude, google_ai)
        query: The query sent to the AI platform
        brand_mentioned: Whether the brand was mentioned in the response
        citation_url: URL cited by the AI platform (if any)
        citation_context: Snippet of text around the brand mention
        competitor_citations: JSON of competitor brands cited in the response
        opportunity_score: Calculated optimization opportunity (0-100)
        response_text: Full response text from the AI platform
        response_time_ms: Response latency in milliseconds
        query_category: Category of the query (product_discovery, comparison, etc.)
        batch_id: Identifier for grouping queries in a single monitoring run
        created_at: When the tracking record was created
        updated_at: When the tracking record was last updated
    """
    __tablename__ = "citation_tracking"

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Tracking Identification
    tracking_id = Column(String(50), unique=True, nullable=False, index=True)
    batch_id = Column(String(50), index=True)

    # Platform and Query
    platform = Column(String(20), nullable=False, index=True)
    query = Column(Text, nullable=False)
    query_category = Column(String(30), index=True)

    # Citation Results
    brand_mentioned = Column(Boolean, default=False, nullable=False, index=True)
    citation_url = Column(String(500))
    citation_context = Column(Text)

    # Competitor Analysis
    competitor_citations = Column(Text)  # JSON stored as text

    # Scoring
    opportunity_score = Column(Integer, default=0)

    # Response Details
    response_text = Column(Text)
    response_time_ms = Column(Integer)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Table constraints
    __table_args__ = (
        CheckConstraint(
            "platform IN ('chatgpt', 'perplexity', 'claude', 'google_ai')",
            name="check_tracking_platform"
        ),
        CheckConstraint(
            "query_category IN ('product_discovery', 'problem_solving', 'comparison', "
            "'purchase_intent', 'educational', 'other') OR query_category IS NULL",
            name="check_tracking_query_category"
        ),
        CheckConstraint(
            "opportunity_score >= 0 AND opportunity_score <= 100",
            name="check_opportunity_score"
        ),
        Index("idx_tracking_platform_date", "platform", "created_at"),
        Index("idx_tracking_mentioned_date", "brand_mentioned", "created_at"),
        Index("idx_tracking_batch", "batch_id", "platform"),
        Index("idx_tracking_opportunity", "opportunity_score", "created_at"),
    )

    def __repr__(self):
        return (
            f"<CitationTracking(id={self.id}, tracking_id='{self.tracking_id}', "
            f"platform='{self.platform}', mentioned={self.brand_mentioned}, "
            f"score={self.opportunity_score})>"
        )
