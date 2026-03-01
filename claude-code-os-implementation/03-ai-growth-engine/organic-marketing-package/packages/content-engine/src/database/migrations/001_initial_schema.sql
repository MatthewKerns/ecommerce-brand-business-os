-- AI Content Agents Database Schema - Initial Migration
-- Migration: 001_initial_schema
-- Description: Create initial database schema with content_history, api_usage, and performance_metrics tables
-- Database: SQLite (development) / PostgreSQL (production)
-- Version: 0.3.0
-- Applied: Initial setup

-- ============================================================================
-- TABLE: content_history
-- Description: Stores all generated content with metadata for historical
--              tracking and analysis
-- ============================================================================

CREATE TABLE content_history (
    -- Primary Key
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Request Identification
    request_id VARCHAR(50) UNIQUE NOT NULL,

    -- Content Classification
    content_type VARCHAR(20) NOT NULL,
    agent_name VARCHAR(50) NOT NULL,

    -- Request Details
    prompt TEXT NOT NULL,
    parameters JSON,
    metadata JSON,

    -- Generated Content
    content TEXT NOT NULL,
    content_format VARCHAR(20) DEFAULT 'markdown',

    -- Generation Details
    model VARCHAR(100) NOT NULL,
    tokens_used INTEGER NOT NULL,
    generation_time_ms INTEGER NOT NULL,

    -- Status Tracking
    status VARCHAR(20) DEFAULT 'success',
    error_message TEXT,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Optional User Context
    user_id VARCHAR(50),
    campaign_id VARCHAR(50),

    -- Constraints
    CHECK (content_type IN ('blog', 'social', 'amazon', 'competitor', 'other')),
    CHECK (status IN ('success', 'partial', 'failed', 'pending')),
    CHECK (tokens_used >= 0),
    CHECK (generation_time_ms >= 0)
);

-- Indexes for content_history

-- Fast lookup by request ID
CREATE UNIQUE INDEX idx_content_history_request_id
ON content_history(request_id);

-- Filter by content type
CREATE INDEX idx_content_history_content_type
ON content_history(content_type);

-- Filter by date range (most common query pattern)
CREATE INDEX idx_content_history_created_at
ON content_history(created_at DESC);

-- Filter by user
CREATE INDEX idx_content_history_user_id
ON content_history(user_id)
WHERE user_id IS NOT NULL;

-- Filter by campaign
CREATE INDEX idx_content_history_campaign_id
ON content_history(campaign_id)
WHERE campaign_id IS NOT NULL;

-- Composite index for common analytics queries
CREATE INDEX idx_content_history_type_date
ON content_history(content_type, created_at DESC);

-- Status monitoring
CREATE INDEX idx_content_history_status
ON content_history(status)
WHERE status != 'success';

-- ============================================================================
-- TABLE: api_usage
-- Description: Tracks all API calls to Anthropic for usage monitoring,
--              cost management, and rate limiting
-- ============================================================================

CREATE TABLE api_usage (
    -- Primary Key
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Request Identification
    request_id VARCHAR(50) NOT NULL,
    content_id INTEGER,

    -- API Call Details
    endpoint VARCHAR(100) NOT NULL,
    method VARCHAR(10) NOT NULL,

    -- Model and Tokens
    model VARCHAR(100) NOT NULL,
    input_tokens INTEGER NOT NULL DEFAULT 0,
    output_tokens INTEGER NOT NULL DEFAULT 0,
    total_tokens INTEGER NOT NULL DEFAULT 0,

    -- Timing
    api_latency_ms INTEGER NOT NULL,
    total_request_time_ms INTEGER NOT NULL,

    -- Cost Tracking
    estimated_cost_usd DECIMAL(10, 6),

    -- Response Status
    status_code INTEGER,
    success BOOLEAN DEFAULT TRUE,
    error_type VARCHAR(50),
    error_message TEXT,

    -- Timestamps
    called_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Rate Limiting Context
    user_id VARCHAR(50),
    api_key_hash VARCHAR(64),

    -- Foreign Key
    FOREIGN KEY (content_id) REFERENCES content_history(id) ON DELETE SET NULL,

    -- Constraints
    CHECK (input_tokens >= 0),
    CHECK (output_tokens >= 0),
    CHECK (total_tokens >= 0),
    CHECK (api_latency_ms >= 0),
    CHECK (total_request_time_ms >= 0),
    CHECK (status_code >= 100 AND status_code < 600)
);

-- Indexes for api_usage

-- Fast lookup by request ID
CREATE INDEX idx_api_usage_request_id
ON api_usage(request_id);

-- Link to content history
CREATE INDEX idx_api_usage_content_id
ON api_usage(content_id)
WHERE content_id IS NOT NULL;

-- Time-series queries
CREATE INDEX idx_api_usage_called_at
ON api_usage(called_at DESC);

-- Cost analysis
CREATE INDEX idx_api_usage_model_date
ON api_usage(model, called_at DESC);

-- Error monitoring
CREATE INDEX idx_api_usage_errors
ON api_usage(success, error_type)
WHERE success = FALSE;

-- Rate limiting by user
CREATE INDEX idx_api_usage_user_date
ON api_usage(user_id, called_at DESC)
WHERE user_id IS NOT NULL;

-- Rate limiting by API key
CREATE INDEX idx_api_usage_apikey_date
ON api_usage(api_key_hash, called_at DESC)
WHERE api_key_hash IS NOT NULL;

-- ============================================================================
-- TABLE: performance_metrics
-- Description: Records detailed performance metrics for system optimization
--              and monitoring
-- ============================================================================

CREATE TABLE performance_metrics (
    -- Primary Key
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Request Identification
    request_id VARCHAR(50) NOT NULL,
    content_id INTEGER,

    -- Performance Measurements
    total_duration_ms INTEGER NOT NULL,
    prompt_preparation_ms INTEGER,
    api_call_ms INTEGER NOT NULL,
    response_processing_ms INTEGER,
    file_save_ms INTEGER,

    -- Resource Usage
    memory_usage_mb DECIMAL(10, 2),
    cpu_percent DECIMAL(5, 2),

    -- Quality Metrics
    content_length_chars INTEGER,
    content_length_words INTEGER,
    validation_passed BOOLEAN DEFAULT TRUE,
    validation_errors JSON,

    -- Cache Performance
    cache_hit BOOLEAN DEFAULT FALSE,
    cache_key VARCHAR(255),

    -- Retry Information
    retry_count INTEGER DEFAULT 0,
    retry_reasons JSON,

    -- Timestamp
    measured_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Foreign Key
    FOREIGN KEY (content_id) REFERENCES content_history(id) ON DELETE SET NULL,

    -- Constraints
    CHECK (total_duration_ms >= 0),
    CHECK (api_call_ms >= 0),
    CHECK (retry_count >= 0),
    CHECK (content_length_chars >= 0),
    CHECK (content_length_words >= 0)
);

-- Indexes for performance_metrics

-- Link to content history
CREATE INDEX idx_perf_metrics_content_id
ON performance_metrics(content_id)
WHERE content_id IS NOT NULL;

-- Time-series analysis
CREATE INDEX idx_perf_metrics_measured_at
ON performance_metrics(measured_at DESC);

-- Performance analysis
CREATE INDEX idx_perf_metrics_duration
ON performance_metrics(total_duration_ms);

-- Slow request identification
CREATE INDEX idx_perf_metrics_slow_requests
ON performance_metrics(api_call_ms DESC)
WHERE api_call_ms > 5000;

-- Cache analysis
CREATE INDEX idx_perf_metrics_cache
ON performance_metrics(cache_hit, measured_at DESC);

-- Error tracking
CREATE INDEX idx_perf_metrics_validation
ON performance_metrics(validation_passed)
WHERE validation_passed = FALSE;
