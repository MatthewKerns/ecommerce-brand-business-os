-- AI Content Agents Database Schema - AEO Citation Tracking Migration
-- Migration: 002_aeo_citation_tracking
-- Description: Add aeo_citation_test table for tracking AI assistant citation tests and AEO performance
-- Database: SQLite (development) / PostgreSQL (production)
-- Version: 0.3.0
-- Applied: 2026-02-26

-- ============================================================================
-- TABLE: aeo_citation_test
-- Description: Tracks AI assistant citation tests for AEO (Agentic Engine
--              Optimization) monitoring and performance measurement
-- ============================================================================

CREATE TABLE aeo_citation_test (
    -- Primary Key
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Test Identification
    test_id VARCHAR(50) UNIQUE NOT NULL,

    -- Query Details
    query TEXT NOT NULL,
    ai_assistant VARCHAR(20) NOT NULL,
    query_category VARCHAR(30) NOT NULL,

    -- Citation Metrics
    brand_mentioned BOOLEAN DEFAULT FALSE NOT NULL,
    brand_recommended BOOLEAN DEFAULT FALSE NOT NULL,
    citation_position INTEGER,

    -- Response Details
    response_text TEXT,
    response_metadata JSON,

    -- Test Context
    test_date TIMESTAMP NOT NULL,
    tester_name VARCHAR(100),
    notes TEXT,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Constraints
    CHECK (ai_assistant IN ('chatgpt', 'claude', 'perplexity', 'gemini', 'copilot', 'other')),
    CHECK (query_category IN ('product_discovery', 'problem_solving', 'comparison', 'purchase_intent', 'educational', 'other')),
    CHECK (citation_position >= 1 AND citation_position <= 10)
);

-- Indexes for aeo_citation_test

-- Fast lookup by test ID
CREATE UNIQUE INDEX idx_aeo_citation_test_id
ON aeo_citation_test(test_id);

-- Filter by AI assistant
CREATE INDEX idx_aeo_citation_ai_assistant
ON aeo_citation_test(ai_assistant);

-- Filter by query category
CREATE INDEX idx_aeo_citation_query_category
ON aeo_citation_test(query_category);

-- Filter by brand mention status
CREATE INDEX idx_aeo_citation_brand_mentioned
ON aeo_citation_test(brand_mentioned);

-- Time-series queries by test date
CREATE INDEX idx_aeo_citation_test_date
ON aeo_citation_test(test_date DESC);

-- Time-series queries by created date
CREATE INDEX idx_aeo_citation_created_at
ON aeo_citation_test(created_at DESC);

-- Composite index for AI assistant performance analysis
CREATE INDEX idx_aeo_citation_assistant_date
ON aeo_citation_test(ai_assistant, test_date DESC);

-- Composite index for query category analysis
CREATE INDEX idx_aeo_citation_category_date
ON aeo_citation_test(query_category, test_date DESC);

-- Composite index for citation rate analysis
CREATE INDEX idx_aeo_citation_mentioned_date
ON aeo_citation_test(brand_mentioned, test_date DESC);

-- Performance analysis for successful citations
CREATE INDEX idx_aeo_citation_position
ON aeo_citation_test(citation_position)
WHERE citation_position IS NOT NULL;

-- Recommendation tracking
CREATE INDEX idx_aeo_citation_recommended
ON aeo_citation_test(brand_recommended, test_date DESC)
WHERE brand_recommended = TRUE;
