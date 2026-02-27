-- AI Content Agents Database Schema - Abandoned Cart Recovery
-- Migration: 002_abandoned_cart_schema
-- Description: Create abandoned cart tracking schema with cart sessions, items, and recovery email history
-- Database: SQLite (development) / PostgreSQL (production)
-- Version: 0.3.1
-- Applied: Abandoned Cart Recovery feature

-- ============================================================================
-- TABLE: abandoned_carts
-- Description: Tracks abandoned shopping cart sessions for recovery campaigns
-- ============================================================================

CREATE TABLE abandoned_carts (
    -- Primary Key
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Cart Identification
    cart_id VARCHAR(100) UNIQUE NOT NULL,

    -- User Information
    user_id VARCHAR(50),
    email VARCHAR(255) NOT NULL,

    -- Platform and Source
    platform VARCHAR(20) NOT NULL,

    -- Cart Data
    cart_data TEXT,
    cart_url VARCHAR(500),

    -- Value Tracking
    total_value DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',

    -- Status Tracking
    status VARCHAR(20) DEFAULT 'active',

    -- Timestamps
    abandoned_at TIMESTAMP,
    recovered_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Constraints
    CHECK (platform IN ('website', 'tiktok_shop')),
    CHECK (status IN ('active', 'abandoned', 'recovered', 'expired')),
    CHECK (total_value >= 0)
);

-- Indexes for abandoned_carts

-- Fast lookup by cart ID
CREATE UNIQUE INDEX idx_abandoned_carts_cart_id
ON abandoned_carts(cart_id);

-- Filter by email (for recovery lookups)
CREATE INDEX idx_abandoned_carts_email
ON abandoned_carts(email);

-- Filter by user
CREATE INDEX idx_abandoned_carts_user_id
ON abandoned_carts(user_id)
WHERE user_id IS NOT NULL;

-- Filter by platform (website vs TikTok Shop)
CREATE INDEX idx_abandoned_carts_platform
ON abandoned_carts(platform);

-- Filter by status
CREATE INDEX idx_abandoned_carts_status
ON abandoned_carts(status);

-- Time-series queries by creation date
CREATE INDEX idx_abandoned_carts_created_at
ON abandoned_carts(created_at DESC);

-- Composite index for email and status (common recovery query)
CREATE INDEX idx_abandoned_carts_email_status
ON abandoned_carts(email, status);

-- Abandoned timestamp for recovery job queries
CREATE INDEX idx_abandoned_carts_abandoned_at
ON abandoned_carts(abandoned_at)
WHERE abandoned_at IS NOT NULL;

-- ============================================================================
-- TABLE: cart_items
-- Description: Stores individual products in abandoned carts for recovery
--              email personalization
-- ============================================================================

CREATE TABLE cart_items (
    -- Primary Key
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Cart Reference
    cart_id INTEGER NOT NULL,

    -- Product Information
    product_id VARCHAR(100) NOT NULL,
    product_name VARCHAR(255) NOT NULL,
    product_image_url VARCHAR(500),

    -- Quantity and Pricing
    quantity INTEGER NOT NULL DEFAULT 1,
    price DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',

    -- Timestamp
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Foreign Key
    FOREIGN KEY (cart_id) REFERENCES abandoned_carts(id) ON DELETE CASCADE,

    -- Constraints
    CHECK (quantity > 0),
    CHECK (price >= 0)
);

-- Indexes for cart_items

-- Link to abandoned cart
CREATE INDEX idx_cart_items_cart_id
ON cart_items(cart_id);

-- Product lookup
CREATE INDEX idx_cart_items_product_id
ON cart_items(product_id);

-- ============================================================================
-- TABLE: cart_recovery_emails
-- Description: Tracks recovery email sequences sent to abandoned cart owners
-- ============================================================================

CREATE TABLE cart_recovery_emails (
    -- Primary Key
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Cart Reference
    cart_id INTEGER NOT NULL,

    -- Email Sequence
    sequence_number INTEGER NOT NULL,
    email_type VARCHAR(20) NOT NULL,

    -- Engagement Tracking
    sent_at TIMESTAMP,
    opened_at TIMESTAMP,
    clicked_at TIMESTAMP,

    -- Status Tracking
    status VARCHAR(20) DEFAULT 'pending',
    error_message TEXT,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Foreign Key
    FOREIGN KEY (cart_id) REFERENCES abandoned_carts(id) ON DELETE CASCADE,

    -- Constraints
    CHECK (email_type IN ('reminder', 'urgency', 'offer')),
    CHECK (status IN ('pending', 'sent', 'opened', 'clicked', 'bounced', 'failed')),
    CHECK (sequence_number BETWEEN 1 AND 3)
);

-- Indexes for cart_recovery_emails

-- Link to abandoned cart
CREATE INDEX idx_recovery_emails_cart_id
ON cart_recovery_emails(cart_id);

-- Composite index for cart and sequence (unique recovery emails)
CREATE INDEX idx_recovery_emails_cart_sequence
ON cart_recovery_emails(cart_id, sequence_number);

-- Time-series queries by sent date
CREATE INDEX idx_recovery_emails_sent_at
ON cart_recovery_emails(sent_at DESC)
WHERE sent_at IS NOT NULL;

-- Status monitoring
CREATE INDEX idx_recovery_emails_status
ON cart_recovery_emails(status);

-- Composite index for status and sent timestamp (common analytics query)
CREATE INDEX idx_recovery_emails_status_sent
ON cart_recovery_emails(status, sent_at);

-- Email engagement tracking
CREATE INDEX idx_recovery_emails_created_at
ON cart_recovery_emails(created_at DESC);
