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


class ScheduledContent(Base):
    """
    Stores scheduled TikTok content for automatic publishing.

    Attributes:
        id: Primary key
        content_type: Type of content (video, post)
        content_data: JSON data containing content details (stored as text)
        scheduled_time: When the content should be published
        status: Current status (pending, published, failed)
        retry_count: Number of publish attempts made
        max_retries: Maximum number of retry attempts allowed
        tiktok_video_id: TikTok video ID after successful publish
        error_message: Error details if publishing failed
        created_at: Timestamp when scheduled content was created
        updated_at: Timestamp when record was last updated
        published_at: Timestamp when content was successfully published
    """
    __tablename__ = "scheduled_content"

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Content Details
    content_type = Column(String(20), nullable=False, index=True)
    content_data = Column(Text, nullable=False)  # JSON stored as text

    # Scheduling
    scheduled_time = Column(DateTime, nullable=False, index=True)

    # Status Tracking
    status = Column(String(20), nullable=False, default="pending", index=True)
    retry_count = Column(Integer, nullable=False, default=0)
    max_retries = Column(Integer, nullable=False, default=3)

    # Publish Results
    tiktok_video_id = Column(String(100))
    error_message = Column(Text)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = Column(DateTime)

    # Relationships
    # Note: PublishLog relationship will be added in subtask-1-2
    # publish_logs = relationship("PublishLog", back_populates="scheduled_content", cascade="all, delete-orphan")

    # Table constraints
    __table_args__ = (
        CheckConstraint(
            "content_type IN ('video', 'post')",
            name="check_scheduled_content_type"
        ),
        CheckConstraint(
            "status IN ('pending', 'published', 'failed')",
            name="check_scheduled_status"
        ),
        CheckConstraint("retry_count >= 0", name="check_retry_count"),
        CheckConstraint("max_retries >= 0", name="check_max_retries"),
        Index("idx_scheduled_content_status_time", "status", "scheduled_time"),
    )

    def __repr__(self):
        return f"<ScheduledContent(id={self.id}, type='{self.content_type}', status='{self.status}', scheduled_time='{self.scheduled_time}')>"
