# Database Schema Documentation

## Overview

This document defines the database schema for the AI Content Agents service. The schema is designed to track content generation history, monitor API usage, and collect performance metrics for optimization and cost management.

## Design Principles

1. **Audit Trail**: Complete history of all content generation requests
2. **Cost Tracking**: Detailed token usage and API call monitoring
3. **Performance Visibility**: Metrics for identifying bottlenecks and optimization opportunities
4. **Scalability**: Indexed for efficient querying at scale
5. **Data Retention**: Support for archival and compliance requirements

## Database Technology

### Development
- **SQLite**: Lightweight, file-based database for local development
- **Location**: `ai-content-agents/data/content_agents.db`
- **Migrations**: SQL-based migration files in `database/migrations/`

### Production (Future)
- **PostgreSQL**: Production-grade relational database
- **Features**: Advanced indexing, partitioning, replication
- **Managed Service**: AWS RDS, Google Cloud SQL, or similar

## Schema Overview

```
┌─────────────────────┐
│ content_history     │
│ (generated content) │
└──────────┬──────────┘
           │
           │ FK: content_id
           │
┌──────────┴──────────┐
│ api_usage           │
│ (API call tracking) │
└──────────┬──────────┘
           │
           │ FK: content_id
           │
┌──────────┴──────────┐
│ performance_metrics │
│ (execution stats)   │
└─────────────────────┘
```

## Table Definitions

### 1. content_history

Stores all generated content with metadata for historical tracking and analysis.

#### Schema

```sql
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
```

#### Indexes

```sql
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
```

#### Column Descriptions

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER | Auto-incrementing primary key |
| `request_id` | VARCHAR(50) | Unique identifier for each request (e.g., "req_abc123def456") |
| `content_type` | VARCHAR(20) | Type of content: blog, social, amazon, competitor |
| `agent_name` | VARCHAR(50) | Name of agent that generated content (e.g., "blog_agent") |
| `prompt` | TEXT | User-provided prompt or topic |
| `parameters` | JSON | Generation parameters (temperature, max_tokens, format, etc.) |
| `metadata` | JSON | Additional metadata (pillar, keywords, target_audience, etc.) |
| `content` | TEXT | Generated content output |
| `content_format` | VARCHAR(20) | Output format (markdown, json, html, plain) |
| `model` | VARCHAR(100) | Anthropic model used (e.g., "claude-sonnet-4-5-20250929") |
| `tokens_used` | INTEGER | Total tokens consumed (input + output) |
| `generation_time_ms` | INTEGER | Time taken to generate content in milliseconds |
| `status` | VARCHAR(20) | Generation status: success, partial, failed, pending |
| `error_message` | TEXT | Error details if status is failed |
| `created_at` | TIMESTAMP | When the request was created |
| `updated_at` | TIMESTAMP | Last modification timestamp |
| `user_id` | VARCHAR(50) | Optional user identifier for multi-user systems |
| `campaign_id` | VARCHAR(50) | Optional campaign identifier for grouping content |

#### Example Data

```sql
INSERT INTO content_history (
    request_id, content_type, agent_name, prompt, parameters,
    content, model, tokens_used, generation_time_ms, status
) VALUES (
    'req_abc123def456',
    'blog',
    'blog_agent',
    'Write about tactical backpacks for urban professionals',
    '{"pillar": "Battle-Ready Lifestyle", "target_word_count": 1500, "format": "listicle"}',
    '# 7 Best Tactical Backpacks for Urban Professionals\n\n...',
    'claude-sonnet-4-5-20250929',
    3241,
    3421,
    'success'
);
```

---

### 2. api_usage

Tracks all API calls to Anthropic for usage monitoring, cost management, and rate limiting.

#### Schema

```sql
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
```

#### Indexes

```sql
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
```

#### Column Descriptions

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER | Auto-incrementing primary key |
| `request_id` | VARCHAR(50) | Links to content_history.request_id |
| `content_id` | INTEGER | Foreign key to content_history table |
| `endpoint` | VARCHAR(100) | API endpoint called (e.g., "/v1/messages") |
| `method` | VARCHAR(10) | HTTP method (GET, POST, etc.) |
| `model` | VARCHAR(100) | Anthropic model identifier |
| `input_tokens` | INTEGER | Number of input tokens sent |
| `output_tokens` | INTEGER | Number of output tokens received |
| `total_tokens` | INTEGER | Sum of input and output tokens |
| `api_latency_ms` | INTEGER | Time waiting for Anthropic API response |
| `total_request_time_ms` | INTEGER | Total request time including processing |
| `estimated_cost_usd` | DECIMAL(10,6) | Estimated cost based on token pricing |
| `status_code` | INTEGER | HTTP status code returned |
| `success` | BOOLEAN | Whether the API call succeeded |
| `error_type` | VARCHAR(50) | Error classification (timeout, rate_limit, etc.) |
| `error_message` | TEXT | Detailed error message |
| `called_at` | TIMESTAMP | When the API call was made |
| `user_id` | VARCHAR(50) | User making the request (for rate limiting) |
| `api_key_hash` | VARCHAR(64) | SHA-256 hash of API key (for tracking, never store raw keys) |

#### Example Data

```sql
INSERT INTO api_usage (
    request_id, content_id, endpoint, method, model,
    input_tokens, output_tokens, total_tokens,
    api_latency_ms, total_request_time_ms,
    estimated_cost_usd, status_code, success
) VALUES (
    'req_abc123def456',
    1,
    '/v1/messages',
    'POST',
    'claude-sonnet-4-5-20250929',
    823,
    2418,
    3241,
    3192,
    3421,
    0.048615,
    200,
    TRUE
);
```

---

### 3. performance_metrics

Records detailed performance metrics for system optimization and monitoring.

#### Schema

```sql
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
```

#### Indexes

```sql
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
```

#### Column Descriptions

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER | Auto-incrementing primary key |
| `request_id` | VARCHAR(50) | Links to content_history.request_id |
| `content_id` | INTEGER | Foreign key to content_history table |
| `total_duration_ms` | INTEGER | End-to-end request duration |
| `prompt_preparation_ms` | INTEGER | Time to build and prepare prompts |
| `api_call_ms` | INTEGER | Time spent calling Anthropic API |
| `response_processing_ms` | INTEGER | Time to process API response |
| `file_save_ms` | INTEGER | Time to save content to disk/database |
| `memory_usage_mb` | DECIMAL(10,2) | Memory consumed during operation |
| `cpu_percent` | DECIMAL(5,2) | CPU utilization percentage |
| `content_length_chars` | INTEGER | Character count of generated content |
| `content_length_words` | INTEGER | Word count of generated content |
| `validation_passed` | BOOLEAN | Whether output validation succeeded |
| `validation_errors` | JSON | Validation error details if any |
| `cache_hit` | BOOLEAN | Whether result came from cache |
| `cache_key` | VARCHAR(255) | Cache key used for lookup |
| `retry_count` | INTEGER | Number of retries attempted |
| `retry_reasons` | JSON | Reasons for retries (timeouts, errors, etc.) |
| `measured_at` | TIMESTAMP | When metrics were recorded |

#### Example Data

```sql
INSERT INTO performance_metrics (
    request_id, content_id, total_duration_ms,
    prompt_preparation_ms, api_call_ms, response_processing_ms,
    content_length_chars, content_length_words,
    validation_passed, cache_hit, retry_count
) VALUES (
    'req_abc123def456',
    1,
    3421,
    147,
    3192,
    82,
    8473,
    1547,
    TRUE,
    FALSE,
    0
);
```

---

## Relationships

```sql
-- Content history is the parent table
content_history (1) ──→ (0..1) api_usage
                  ↓
                  └──→ (0..1) performance_metrics

-- Each content generation request:
-- - Creates 1 content_history record
-- - Creates 1 api_usage record (when API is called)
-- - Creates 1 performance_metrics record
```

## Migration Strategy

### Migration Files

Migrations are stored in `ai-content-agents/database/migrations/` with sequential numbering:

```
migrations/
├── 001_initial_schema.sql
├── 002_add_user_tracking.sql
├── 003_add_campaign_support.sql
└── 004_add_cache_metrics.sql
```

### Migration Format

Each migration file includes:

```sql
-- Migration: 001_initial_schema.sql
-- Description: Create initial database schema
-- Author: AI Content Agents Team
-- Date: 2024-02-26

-- Up Migration
BEGIN TRANSACTION;

CREATE TABLE content_history (
    -- table definition...
);

CREATE TABLE api_usage (
    -- table definition...
);

-- Record migration
CREATE TABLE IF NOT EXISTS schema_migrations (
    version INTEGER PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO schema_migrations (version, name)
VALUES (1, '001_initial_schema');

COMMIT;

-- Down Migration (for rollback)
-- BEGIN TRANSACTION;
-- DROP TABLE api_usage;
-- DROP TABLE content_history;
-- DELETE FROM schema_migrations WHERE version = 1;
-- COMMIT;
```

### Running Migrations

```bash
# Initialize database
python ai-content-agents/database/init_db.py

# Apply all pending migrations
python ai-content-agents/database/init_db.py --migrate

# Dry run (show what would be executed)
python ai-content-agents/database/init_db.py --dry-run

# Rollback last migration
python ai-content-agents/database/init_db.py --rollback
```

## Example Queries

### Content Analytics

```sql
-- Most generated content types
SELECT
    content_type,
    COUNT(*) as count,
    AVG(tokens_used) as avg_tokens,
    AVG(generation_time_ms) as avg_time_ms
FROM content_history
WHERE created_at >= DATE('now', '-30 days')
GROUP BY content_type
ORDER BY count DESC;

-- Daily content generation volume
SELECT
    DATE(created_at) as date,
    COUNT(*) as requests,
    SUM(tokens_used) as total_tokens
FROM content_history
GROUP BY DATE(created_at)
ORDER BY date DESC
LIMIT 30;

-- Failed generation attempts
SELECT
    request_id,
    content_type,
    error_message,
    created_at
FROM content_history
WHERE status = 'failed'
ORDER BY created_at DESC
LIMIT 50;
```

### Cost Analysis

```sql
-- Monthly cost by model
SELECT
    model,
    DATE_TRUNC('month', called_at) as month,
    COUNT(*) as api_calls,
    SUM(total_tokens) as total_tokens,
    SUM(estimated_cost_usd) as total_cost
FROM api_usage
WHERE success = TRUE
GROUP BY model, DATE_TRUNC('month', called_at)
ORDER BY month DESC, total_cost DESC;

-- Cost per content type
SELECT
    ch.content_type,
    COUNT(*) as requests,
    SUM(au.estimated_cost_usd) as total_cost,
    AVG(au.estimated_cost_usd) as avg_cost_per_request
FROM content_history ch
JOIN api_usage au ON ch.id = au.content_id
WHERE ch.created_at >= DATE('now', '-30 days')
GROUP BY ch.content_type
ORDER BY total_cost DESC;

-- Top users by cost
SELECT
    user_id,
    COUNT(*) as api_calls,
    SUM(total_tokens) as tokens_used,
    SUM(estimated_cost_usd) as total_cost
FROM api_usage
WHERE user_id IS NOT NULL
  AND called_at >= DATE('now', '-30 days')
GROUP BY user_id
ORDER BY total_cost DESC
LIMIT 10;
```

### Performance Monitoring

```sql
-- Slowest requests by content type
SELECT
    ch.content_type,
    AVG(pm.total_duration_ms) as avg_duration,
    AVG(pm.api_call_ms) as avg_api_time,
    MAX(pm.total_duration_ms) as max_duration
FROM performance_metrics pm
JOIN content_history ch ON pm.content_id = ch.id
GROUP BY ch.content_type
ORDER BY avg_duration DESC;

-- Cache effectiveness
SELECT
    cache_hit,
    COUNT(*) as requests,
    AVG(total_duration_ms) as avg_duration_ms
FROM performance_metrics
WHERE measured_at >= DATE('now', '-7 days')
GROUP BY cache_hit;

-- Retry analysis
SELECT
    DATE(measured_at) as date,
    SUM(retry_count) as total_retries,
    COUNT(*) as total_requests,
    ROUND(100.0 * SUM(CASE WHEN retry_count > 0 THEN 1 ELSE 0 END) / COUNT(*), 2) as retry_percentage
FROM performance_metrics
GROUP BY DATE(measured_at)
ORDER BY date DESC
LIMIT 30;
```

### Rate Limiting Queries

```sql
-- Requests per user in last hour
SELECT
    user_id,
    COUNT(*) as requests_last_hour
FROM api_usage
WHERE user_id IS NOT NULL
  AND called_at >= DATETIME('now', '-1 hour')
GROUP BY user_id
HAVING requests_last_hour > 50
ORDER BY requests_last_hour DESC;

-- API key usage tracking
SELECT
    api_key_hash,
    COUNT(*) as total_requests,
    SUM(CASE WHEN success = FALSE THEN 1 ELSE 0 END) as failed_requests,
    MAX(called_at) as last_used
FROM api_usage
WHERE api_key_hash IS NOT NULL
GROUP BY api_key_hash
ORDER BY total_requests DESC;
```

## Data Retention Policy

### Recommended Retention Periods

| Table | Retention Period | Archive Strategy |
|-------|-----------------|------------------|
| `content_history` | 2 years active, archive after | Move to cold storage, keep metadata |
| `api_usage` | 1 year active, 3 years archive | Aggregate to daily summaries |
| `performance_metrics` | 90 days active, 1 year aggregated | Keep hourly/daily rollups |

### Archival Query

```sql
-- Archive old content to separate table
INSERT INTO content_history_archive
SELECT * FROM content_history
WHERE created_at < DATE('now', '-2 years');

DELETE FROM content_history
WHERE created_at < DATE('now', '-2 years');

-- Vacuum to reclaim space
VACUUM;
```

## Schema Evolution Best Practices

1. **Never Drop Columns**: Mark as deprecated instead
2. **Backward Compatible**: New columns must have defaults
3. **Test Migrations**: Always test on copy of production data
4. **Version Control**: All migrations in git with sequential numbers
5. **Rollback Plan**: Include down migration for every up migration

## Performance Optimization

### Partitioning Strategy (PostgreSQL)

```sql
-- Partition content_history by month
CREATE TABLE content_history_2024_02 PARTITION OF content_history
FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');

-- Partition api_usage by week
CREATE TABLE api_usage_2024_w08 PARTITION OF api_usage
FOR VALUES FROM ('2024-02-19') TO ('2024-02-26');
```

### Query Optimization Tips

1. **Use Indexes**: All FK and commonly filtered columns indexed
2. **Limit Scans**: Always include date range filters
3. **Aggregate Early**: Use materialized views for dashboards
4. **Batch Inserts**: Insert multiple rows in single transaction
5. **Connection Pool**: Reuse database connections

## Security Considerations

1. **No Sensitive Data**: Never store raw API keys, only hashes
2. **Encrypt at Rest**: Enable database encryption in production
3. **Row-Level Security**: Implement for multi-tenant scenarios
4. **Audit Logging**: Track all schema changes and data access
5. **Backup Strategy**: Daily backups with point-in-time recovery

## References

- [SQLite Documentation](https://www.sqlite.org/docs.html)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/)
- Database Migration Best Practices

## Changelog

- **v0.2.0** - Database schema documentation created
- **v0.3.0** - Planned: Initial schema implementation
- **v0.4.0** - Planned: Add user authentication tables
- **v0.5.0** - Planned: Add content template tables
