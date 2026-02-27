"""
Database models for AI Content Agents.
Defines SQLAlchemy ORM models for content history, API usage, performance metrics, and Klaviyo integration.
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


class KlaviyoProfile(Base):
    """
    Stores customer profiles synced from Klaviyo for local tracking and analysis.

    Attributes:
        id: Primary key
        klaviyo_profile_id: Klaviyo's unique profile ID
        email: Customer email address
        phone_number: Phone number in E.164 format
        external_id: External system ID (e.g., from TikTok Shop)
        first_name: First/given name
        last_name: Last/family name
        organization: Company/organization name
        title: Job title
        image_url: URL to profile image
        subscription_status: Email subscription status (subscribed, unsubscribed, never_subscribed)
        subscribed_at: When profile subscribed to email
        unsubscribed_at: When profile unsubscribed from email
        address1: First line of address
        address2: Second line of address
        city: City name
        region: State/province/region
        country: Country name or code
        zip: Postal/ZIP code
        timezone: IANA timezone
        latitude: Geographic latitude
        longitude: Geographic longitude
        properties: JSON custom properties/attributes
        created_at: Timestamp when record was created
        updated_at: Timestamp when record was last updated
        last_synced_at: Timestamp of last sync with Klaviyo
    """
    __tablename__ = "klaviyo_profiles"

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Klaviyo Identifiers
    klaviyo_profile_id = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), index=True)
    phone_number = Column(String(20))
    external_id = Column(String(100), index=True)

    # Personal Information
    first_name = Column(String(100))
    last_name = Column(String(100))
    organization = Column(String(200))
    title = Column(String(100))
    image_url = Column(String(500))

    # Subscription Status
    subscription_status = Column(String(20), default="never_subscribed")
    subscribed_at = Column(DateTime)
    unsubscribed_at = Column(DateTime)

    # Location Information
    address1 = Column(String(255))
    address2 = Column(String(255))
    city = Column(String(100))
    region = Column(String(100))
    country = Column(String(100))
    zip = Column(String(20))
    timezone = Column(String(50))
    latitude = Column(Numeric(10, 7))
    longitude = Column(Numeric(10, 7))

    # Custom Properties
    properties = Column(Text)  # JSON stored as text

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_synced_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    sync_history = relationship("KlaviyoSyncHistory", back_populates="profile", cascade="all, delete-orphan")

    # Table constraints
    __table_args__ = (
        CheckConstraint(
            "subscription_status IN ('subscribed', 'unsubscribed', 'never_subscribed')",
            name="check_subscription_status"
        ),
        Index("idx_klaviyo_profile_email", "email"),
        Index("idx_klaviyo_profile_external_id", "external_id"),
        Index("idx_klaviyo_profile_sync", "last_synced_at"),
    )

    def __repr__(self):
        return f"<KlaviyoProfile(id={self.id}, klaviyo_id='{self.klaviyo_profile_id}', email='{self.email}')>"


class KlaviyoSyncHistory(Base):
    """
    Tracks synchronization operations between our system and Klaviyo.

    Attributes:
        id: Primary key
        profile_id: Foreign key to klaviyo_profiles (optional, for profile-specific syncs)
        sync_type: Type of sync operation (profile_sync, event_sync, list_sync, segment_sync)
        sync_direction: Direction of sync (to_klaviyo, from_klaviyo, bidirectional)
        status: Sync status (pending, in_progress, completed, failed, partial)
        records_processed: Number of records processed
        records_succeeded: Number of records successfully synced
        records_failed: Number of records that failed
        error_message: Error details if sync failed
        error_details: JSON detailed error information
        sync_metadata: JSON metadata about the sync operation
        started_at: When sync started
        completed_at: When sync completed
        duration_ms: Sync duration in milliseconds
        created_at: Timestamp when record was created
    """
    __tablename__ = "klaviyo_sync_history"

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Profile Reference (optional, for profile-specific syncs)
    profile_id = Column(Integer, ForeignKey("klaviyo_profiles.id", ondelete="SET NULL"), index=True)

    # Sync Operation Details
    sync_type = Column(String(50), nullable=False, index=True)
    sync_direction = Column(String(20), nullable=False)
    status = Column(String(20), default="pending", nullable=False)

    # Sync Results
    records_processed = Column(Integer, default=0)
    records_succeeded = Column(Integer, default=0)
    records_failed = Column(Integer, default=0)

    # Error Tracking
    error_message = Column(Text)
    error_details = Column(Text)  # JSON stored as text

    # Sync Metadata
    sync_metadata = Column(Text)  # JSON stored as text

    # Timing
    started_at = Column(DateTime, default=datetime.utcnow, index=True)
    completed_at = Column(DateTime)
    duration_ms = Column(Integer)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    profile = relationship("KlaviyoProfile", back_populates="sync_history")

    # Table constraints
    __table_args__ = (
        CheckConstraint(
            "sync_type IN ('profile_sync', 'event_sync', 'list_sync', 'segment_sync', 'bulk_sync')",
            name="check_sync_type"
        ),
        CheckConstraint(
            "sync_direction IN ('to_klaviyo', 'from_klaviyo', 'bidirectional')",
            name="check_sync_direction"
        ),
        CheckConstraint(
            "status IN ('pending', 'in_progress', 'completed', 'failed', 'partial')",
            name="check_sync_status"
        ),
        CheckConstraint("records_processed >= 0", name="check_records_processed"),
        CheckConstraint("records_succeeded >= 0", name="check_records_succeeded"),
        CheckConstraint("records_failed >= 0", name="check_records_failed"),
        CheckConstraint("duration_ms >= 0", name="check_duration_ms"),
        Index("idx_sync_history_type_date", "sync_type", "started_at"),
        Index("idx_sync_history_status", "status"),
    )

    def __repr__(self):
        return f"<KlaviyoSyncHistory(id={self.id}, type='{self.sync_type}', status='{self.status}')>"


class KlaviyoSegment(Base):
    """
    Stores Klaviyo segment definitions for customer segmentation and targeting.

    Attributes:
        id: Primary key
        klaviyo_segment_id: Klaviyo's unique segment ID
        name: Segment name
        segment_type: Type of segment (standard, custom, dynamic)
        definition: JSON segment filter definition (criteria for inclusion)
        description: Human-readable description of the segment
        profile_count: Estimated number of profiles in segment
        is_active: Whether segment is actively used
        last_profile_count_update: When profile count was last updated
        created_at: Timestamp when record was created
        updated_at: Timestamp when record was last updated
        last_synced_at: Timestamp of last sync with Klaviyo
    """
    __tablename__ = "klaviyo_segments"

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Klaviyo Identifiers
    klaviyo_segment_id = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)

    # Segment Details
    segment_type = Column(String(20), default="standard")
    definition = Column(Text)  # JSON stored as text
    description = Column(Text)

    # Segment Metrics
    profile_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)

    # Timestamps
    last_profile_count_update = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_synced_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Table constraints
    __table_args__ = (
        CheckConstraint(
            "segment_type IN ('standard', 'custom', 'dynamic')",
            name="check_segment_type"
        ),
        CheckConstraint("profile_count >= 0", name="check_profile_count"),
        Index("idx_klaviyo_segment_name", "name"),
        Index("idx_klaviyo_segment_active", "is_active"),
        Index("idx_klaviyo_segment_sync", "last_synced_at"),
    )

    def __repr__(self):
        return f"<KlaviyoSegment(id={self.id}, klaviyo_id='{self.klaviyo_segment_id}', name='{self.name}')>"
