/**
 * Tracking Sync Service - Synchronizes tracking numbers from Amazon MCF to TikTok Shop
 *
 * Features:
 * - Polls Amazon MCF for tracking updates on fulfilled orders
 * - Syncs tracking numbers back to TikTok Shop
 * - Tracks sync status and retries failed syncs
 * - Configurable polling interval and retry behavior
 * - Automatic scheduling with configurable sync intervals (default: 30 minutes)
 * - Rate limiting to prevent API throttling (default: 10 requests per minute)
 * - Start/stop scheduler control for production deployments
 */
import type { TikTokShopClient } from '../clients/tiktok-shop-client';
import type { AmazonMCFClient } from '../clients/amazon-mcf-client';
import { ErrorCode } from '../types/common';
/**
 * Order tracking record to sync
 */
export interface OrderTrackingRecord {
    tiktokOrderId: string;
    mcfFulfillmentOrderId: string;
    lastSyncAttempt?: Date;
    syncAttempts: number;
    synced: boolean;
    syncedAt?: Date;
    error?: TrackingSyncError;
}
/**
 * Tracking sync error
 */
export interface TrackingSyncError {
    orderId: string;
    mcfFulfillmentOrderId: string;
    code: ErrorCode;
    message: string;
    details?: unknown;
    timestamp: Date;
}
/**
 * Tracking sync result for a single order
 */
export interface TrackingSyncResult {
    success: boolean;
    orderId: string;
    mcfFulfillmentOrderId: string;
    trackingNumber?: string;
    carrier?: string;
    error?: TrackingSyncError;
}
/**
 * Batch tracking sync result
 */
export interface BatchTrackingSyncResult {
    totalOrders: number;
    successCount: number;
    failureCount: number;
    skippedCount: number;
    results: TrackingSyncResult[];
    errors: TrackingSyncError[];
}
/**
 * Tracking sync configuration
 */
export interface TrackingSyncConfig {
    maxRetries?: number;
    retryDelayMs?: number;
    skipAlreadySynced?: boolean;
    updateTikTok?: boolean;
    syncIntervalMs?: number;
    schedulerEnabled?: boolean;
    rateLimitPerMinute?: number;
}
/**
 * Dependencies for TrackingSync service
 */
export interface TrackingSyncDependencies {
    tiktokClient: TikTokShopClient;
    amazonClient: AmazonMCFClient;
}
/**
 * TrackingSync manages synchronization of tracking numbers from Amazon MCF to TikTok Shop
 */
export declare class TrackingSync {
    private config;
    private tiktokClient;
    private amazonClient;
    private trackingRecords;
    private schedulerTimer?;
    private isSchedulerActive;
    private lastSyncRun?;
    private requestsInCurrentMinute;
    private currentMinuteStart;
    constructor(dependencies: TrackingSyncDependencies, config?: TrackingSyncConfig);
    /**
     * Add an order to track for sync
     */
    addOrder(tiktokOrderId: string, mcfFulfillmentOrderId: string): void;
    /**
     * Remove an order from tracking
     */
    removeOrder(tiktokOrderId: string): void;
    /**
     * Get tracking record for an order
     */
    getTrackingRecord(tiktokOrderId: string): OrderTrackingRecord | undefined;
    /**
     * Get all tracking records
     */
    getAllTrackingRecords(): OrderTrackingRecord[];
    /**
     * Get unsynced tracking records
     */
    getUnsyncedRecords(): OrderTrackingRecord[];
    /**
     * Sync tracking for a single order
     */
    syncOrder(tiktokOrderId: string): Promise<TrackingSyncResult>;
    /**
     * Sync tracking for multiple orders
     */
    syncOrders(tiktokOrderIds: string[]): Promise<BatchTrackingSyncResult>;
    /**
     * Sync all unsynced orders
     */
    syncAllUnsynced(): Promise<BatchTrackingSyncResult>;
    /**
     * Extract tracking information from MCF shipments
     */
    private extractTrackingInfo;
    /**
     * Sleep for specified milliseconds
     */
    private sleep;
    /**
     * Reset rate limit counter if we've moved to a new minute
     */
    private resetRateLimitIfNeeded;
    /**
     * Enforce rate limiting before making API requests
     */
    private enforceRateLimit;
    /**
     * Start the automatic tracking sync scheduler
     */
    startScheduler(): void;
    /**
     * Stop the automatic tracking sync scheduler
     */
    stopScheduler(): void;
    /**
     * Check if the scheduler is currently running
     */
    isSchedulerRunning(): boolean;
    /**
     * Run scheduled sync (called by scheduler)
     */
    private runScheduledSync;
    /**
     * Update configuration
     */
    updateConfig(config: Partial<TrackingSyncConfig>): void;
    /**
     * Get current configuration
     */
    getConfig(): Required<TrackingSyncConfig>;
    /**
     * Clear all tracking records
     */
    clearRecords(): void;
    /**
     * Get sync statistics
     */
    getStats(): {
        total: number;
        synced: number;
        unsynced: number;
        failed: number;
        schedulerRunning: boolean;
        lastSyncRun?: Date;
    };
}
/**
 * Create a new tracking sync instance
 */
export declare function createTrackingSync(dependencies: TrackingSyncDependencies, config?: TrackingSyncConfig): TrackingSync;
//# sourceMappingURL=tracking-sync.d.ts.map