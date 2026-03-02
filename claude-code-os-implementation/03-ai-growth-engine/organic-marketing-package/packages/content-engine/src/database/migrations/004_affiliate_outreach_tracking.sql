-- Migration 004: Affiliate Outreach Tracking
-- Tracks TikTok Shop affiliate campaigns, invitations, and performance
-- Supports the automated outreach system (MADA playbook)

-- Affiliate outreach campaigns
CREATE TABLE IF NOT EXISTS affiliate_campaigns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    campaign_name TEXT NOT NULL UNIQUE,
    collaboration_id TEXT,
    product_ids TEXT NOT NULL,  -- JSON array
    commission_rate REAL NOT NULL DEFAULT 15.0,
    status TEXT NOT NULL DEFAULT 'active',  -- active, paused, completed
    search_filters TEXT,  -- JSON object with filter criteria
    daily_outreach_target INTEGER NOT NULL DEFAULT 50,
    invitation_message TEXT,
    total_invitations_sent INTEGER NOT NULL DEFAULT 0,
    total_accepted INTEGER NOT NULL DEFAULT 0,
    total_rejected INTEGER NOT NULL DEFAULT 0,
    total_pending INTEGER NOT NULL DEFAULT 0,
    videos_received INTEGER NOT NULL DEFAULT 0,
    gmv_generated REAL NOT NULL DEFAULT 0.0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Individual outreach invitations
CREATE TABLE IF NOT EXISTS affiliate_invitations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    campaign_id INTEGER NOT NULL REFERENCES affiliate_campaigns(id),
    creator_id TEXT NOT NULL,
    creator_nickname TEXT,
    creator_followers INTEGER,
    creator_gmv_30d REAL,
    invitation_message TEXT,
    status TEXT NOT NULL DEFAULT 'sent',  -- sent, pending, accepted, rejected, expired
    sent_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    responded_at TIMESTAMP,
    follow_up_count INTEGER NOT NULL DEFAULT 0,
    last_follow_up_at TIMESTAMP,
    notes TEXT
);

-- Outreach run log (daily execution tracking)
CREATE TABLE IF NOT EXISTS affiliate_outreach_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    campaign_id INTEGER NOT NULL REFERENCES affiliate_campaigns(id),
    run_date DATE NOT NULL,
    invitations_sent INTEGER NOT NULL DEFAULT 0,
    invitations_failed INTEGER NOT NULL DEFAULT 0,
    tier_at_run INTEGER NOT NULL DEFAULT 1,
    remaining_actions_after INTEGER,
    run_duration_seconds REAL,
    error_message TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Affiliate creator profiles (cached from API)
CREATE TABLE IF NOT EXISTS affiliate_creators (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    creator_id TEXT NOT NULL UNIQUE,
    nickname TEXT,
    avatar_url TEXT,
    follower_count INTEGER,
    bio TEXT,
    categories TEXT,  -- JSON array
    gmv_30d REAL,
    sales_30d INTEGER,
    video_count INTEGER,
    engagement_rate REAL,
    first_seen_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Affiliate performance snapshots (daily tracking)
CREATE TABLE IF NOT EXISTS affiliate_performance_daily (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    snapshot_date DATE NOT NULL,
    total_affiliate_gmv REAL NOT NULL DEFAULT 0.0,
    total_affiliate_orders INTEGER NOT NULL DEFAULT 0,
    total_commission_paid REAL NOT NULL DEFAULT 0.0,
    active_creators INTEGER NOT NULL DEFAULT 0,
    videos_posted INTEGER NOT NULL DEFAULT 0,
    total_video_views INTEGER NOT NULL DEFAULT 0,
    outreach_tier INTEGER NOT NULL DEFAULT 1,
    weekly_actions_used INTEGER NOT NULL DEFAULT 0,
    weekly_actions_limit INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(snapshot_date)
);

-- Tier progression tracking
CREATE TABLE IF NOT EXISTS affiliate_tier_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tier_level INTEGER NOT NULL,
    unlocked_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    affiliate_gmv_at_unlock REAL,
    notes TEXT
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_invitations_campaign ON affiliate_invitations(campaign_id);
CREATE INDEX IF NOT EXISTS idx_invitations_creator ON affiliate_invitations(creator_id);
CREATE INDEX IF NOT EXISTS idx_invitations_status ON affiliate_invitations(status);
CREATE INDEX IF NOT EXISTS idx_outreach_runs_campaign ON affiliate_outreach_runs(campaign_id);
CREATE INDEX IF NOT EXISTS idx_outreach_runs_date ON affiliate_outreach_runs(run_date);
CREATE INDEX IF NOT EXISTS idx_creators_gmv ON affiliate_creators(gmv_30d DESC);
CREATE INDEX IF NOT EXISTS idx_creators_followers ON affiliate_creators(follower_count DESC);
CREATE INDEX IF NOT EXISTS idx_performance_date ON affiliate_performance_daily(snapshot_date);
