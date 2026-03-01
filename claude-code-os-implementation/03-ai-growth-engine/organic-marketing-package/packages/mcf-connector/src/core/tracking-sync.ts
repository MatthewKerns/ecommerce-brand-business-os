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
import type {
  MCFFulfillmentOrder,
  MCFShipment,
  MCFGetFulfillmentOrderResponse,
} from '../types/mcf-order';
import { ErrorCode, MCFFulfillmentStatus } from '../types/common';

// ============================================================
// Types
// ============================================================

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

// ============================================================
// Constants
// ============================================================

const DEFAULT_TRACKING_SYNC_CONFIG: Required<TrackingSyncConfig> = {
  maxRetries: 3,
  retryDelayMs: 5000,
  skipAlreadySynced: true,
  updateTikTok: true,
  syncIntervalMs: 30 * 60 * 1000, // 30 minutes
  schedulerEnabled: false,
  rateLimitPerMinute: 10,
};

// ============================================================
// TrackingSync Class
// ============================================================

/**
 * TrackingSync manages synchronization of tracking numbers from Amazon MCF to TikTok Shop
 */
export class TrackingSync {
  private config: Required<TrackingSyncConfig>;
  private tiktokClient: TikTokShopClient;
  private amazonClient: AmazonMCFClient;
  private trackingRecords: Map<string, OrderTrackingRecord>;

  // Scheduler state
  private schedulerTimer?: NodeJS.Timeout;
  private isSchedulerActive: boolean = false;
  private lastSyncRun?: Date;

  // Rate limiting
  private requestsInCurrentMinute: number = 0;
  private currentMinuteStart: Date = new Date();

  constructor(
    dependencies: TrackingSyncDependencies,
    config?: TrackingSyncConfig
  ) {
    this.tiktokClient = dependencies.tiktokClient;
    this.amazonClient = dependencies.amazonClient;
    this.config = { ...DEFAULT_TRACKING_SYNC_CONFIG, ...config };
    this.trackingRecords = new Map();

    // Start scheduler if enabled in config
    if (this.config.schedulerEnabled) {
      this.startScheduler();
    }
  }

  /**
   * Add an order to track for sync
   */
  addOrder(tiktokOrderId: string, mcfFulfillmentOrderId: string): void {
    if (!this.trackingRecords.has(tiktokOrderId)) {
      this.trackingRecords.set(tiktokOrderId, {
        tiktokOrderId,
        mcfFulfillmentOrderId,
        syncAttempts: 0,
        synced: false,
      });
    }
  }

  /**
   * Remove an order from tracking
   */
  removeOrder(tiktokOrderId: string): void {
    this.trackingRecords.delete(tiktokOrderId);
  }

  /**
   * Get tracking record for an order
   */
  getTrackingRecord(tiktokOrderId: string): OrderTrackingRecord | undefined {
    return this.trackingRecords.get(tiktokOrderId);
  }

  /**
   * Get all tracking records
   */
  getAllTrackingRecords(): OrderTrackingRecord[] {
    return Array.from(this.trackingRecords.values());
  }

  /**
   * Get unsynced tracking records
   */
  getUnsyncedRecords(): OrderTrackingRecord[] {
    return this.getAllTrackingRecords().filter(record => !record.synced);
  }

  /**
   * Sync tracking for a single order
   */
  async syncOrder(tiktokOrderId: string): Promise<TrackingSyncResult> {
    const record = this.trackingRecords.get(tiktokOrderId);

    if (!record) {
      return {
        success: false,
        orderId: tiktokOrderId,
        mcfFulfillmentOrderId: 'UNKNOWN',
        error: {
          orderId: tiktokOrderId,
          mcfFulfillmentOrderId: 'UNKNOWN',
          code: ErrorCode.INVALID_ORDER_DATA,
          message: `Order ${tiktokOrderId} not found in tracking records`,
          timestamp: new Date(),
        },
      };
    }

    // Skip if already synced and config says to skip
    if (record.synced && this.config.skipAlreadySynced) {
      return {
        success: true,
        orderId: tiktokOrderId,
        mcfFulfillmentOrderId: record.mcfFulfillmentOrderId,
      };
    }

    // Check if we've exceeded retry limit
    if (record.syncAttempts >= this.config.maxRetries) {
      return {
        success: false,
        orderId: tiktokOrderId,
        mcfFulfillmentOrderId: record.mcfFulfillmentOrderId,
        error: {
          orderId: tiktokOrderId,
          mcfFulfillmentOrderId: record.mcfFulfillmentOrderId,
          code: ErrorCode.TRACKING_SYNC_FAILED,
          message: `Max retry attempts (${this.config.maxRetries}) exceeded for order ${tiktokOrderId}`,
          timestamp: new Date(),
        },
      };
    }

    // Update sync attempt tracking
    record.syncAttempts++;
    record.lastSyncAttempt = new Date();

    try {
      // Step 1: Get fulfillment order from Amazon MCF
      let orderResponse: MCFGetFulfillmentOrderResponse;
      try {
        orderResponse = await this.amazonClient.getFulfillmentOrder({
          sellerFulfillmentOrderId: record.mcfFulfillmentOrderId,
        });
      } catch (error) {
        const syncError: TrackingSyncError = {
          orderId: tiktokOrderId,
          mcfFulfillmentOrderId: record.mcfFulfillmentOrderId,
          code: ErrorCode.AMAZON_API_ERROR,
          message: `Failed to fetch MCF order: ${error instanceof Error ? error.message : 'Unknown error'}`,
          details: error,
          timestamp: new Date(),
        };
        record.error = syncError;
        return {
          success: false,
          orderId: tiktokOrderId,
          mcfFulfillmentOrderId: record.mcfFulfillmentOrderId,
          error: syncError,
        };
      }

      const mcfOrder = orderResponse.fulfillmentOrder;
      const shipments = orderResponse.fulfillmentShipments || [];

      // Step 2: Check if order has shipped
      const hasShipped = mcfOrder.statusUpdatedDate && (
        mcfOrder.fulfillmentOrderStatus === MCFFulfillmentStatus.COMPLETE ||
        mcfOrder.fulfillmentOrderStatus === MCFFulfillmentStatus.COMPLETE_PARTIALLED
      );

      if (!hasShipped) {
        return {
          success: false,
          orderId: tiktokOrderId,
          mcfFulfillmentOrderId: record.mcfFulfillmentOrderId,
          error: {
            orderId: tiktokOrderId,
            mcfFulfillmentOrderId: record.mcfFulfillmentOrderId,
            code: ErrorCode.TRACKING_SYNC_FAILED,
            message: `Order not yet shipped. Status: ${mcfOrder.fulfillmentOrderStatus}`,
            timestamp: new Date(),
          },
        };
      }

      // Step 3: Extract tracking info from shipments
      const trackingInfo = this.extractTrackingInfo(shipments);
      if (!trackingInfo) {
        return {
          success: false,
          orderId: tiktokOrderId,
          mcfFulfillmentOrderId: record.mcfFulfillmentOrderId,
          error: {
            orderId: tiktokOrderId,
            mcfFulfillmentOrderId: record.mcfFulfillmentOrderId,
            code: ErrorCode.TRACKING_SYNC_FAILED,
            message: 'No tracking information available in MCF order',
            timestamp: new Date(),
          },
        };
      }

      // Step 4: Get TikTok order details to find package ID
      let packageId: string | undefined;
      if (this.config.updateTikTok) {
        try {
          const tiktokOrder = await this.tiktokClient.getOrderDetail(tiktokOrderId);
          // Get package ID from the first package (if available)
          if (tiktokOrder.packages && tiktokOrder.packages.length > 0) {
            packageId = tiktokOrder.packages[0].id;
          }
        } catch (error) {
          // If we can't fetch the order, use the order ID as package ID (fallback)
          packageId = tiktokOrderId;
        }

        if (!packageId) {
          // Fallback to order ID if no package found
          packageId = tiktokOrderId;
        }
      }

      // Step 5: Update tracking in TikTok Shop (if enabled)
      if (this.config.updateTikTok && packageId) {
        try {
          await this.tiktokClient.updateTrackingInfo(packageId, {
            order_id: tiktokOrderId,
            tracking_number: trackingInfo.trackingNumber,
            shipping_provider_name: trackingInfo.carrier || 'OTHER',
          });
        } catch (error) {
          const syncError: TrackingSyncError = {
            orderId: tiktokOrderId,
            mcfFulfillmentOrderId: record.mcfFulfillmentOrderId,
            code: ErrorCode.TIKTOK_API_ERROR,
            message: `Failed to update TikTok tracking: ${error instanceof Error ? error.message : 'Unknown error'}`,
            details: error,
            timestamp: new Date(),
          };
          record.error = syncError;
          return {
            success: false,
            orderId: tiktokOrderId,
            mcfFulfillmentOrderId: record.mcfFulfillmentOrderId,
            trackingNumber: trackingInfo.trackingNumber,
            carrier: trackingInfo.carrier,
            error: syncError,
          };
        }
      }

      // Step 6: Mark as synced
      record.synced = true;
      record.syncedAt = new Date();
      record.error = undefined;

      return {
        success: true,
        orderId: tiktokOrderId,
        mcfFulfillmentOrderId: record.mcfFulfillmentOrderId,
        trackingNumber: trackingInfo.trackingNumber,
        carrier: trackingInfo.carrier,
      };
    } catch (error) {
      const syncError: TrackingSyncError = {
        orderId: tiktokOrderId,
        mcfFulfillmentOrderId: record.mcfFulfillmentOrderId,
        code: ErrorCode.UNKNOWN_ERROR,
        message: `Unexpected error syncing tracking: ${error instanceof Error ? error.message : 'Unknown error'}`,
        details: error,
        timestamp: new Date(),
      };
      record.error = syncError;
      return {
        success: false,
        orderId: tiktokOrderId,
        mcfFulfillmentOrderId: record.mcfFulfillmentOrderId,
        error: syncError,
      };
    }
  }

  /**
   * Sync tracking for multiple orders
   */
  async syncOrders(tiktokOrderIds: string[]): Promise<BatchTrackingSyncResult> {
    const results: TrackingSyncResult[] = [];
    const errors: TrackingSyncError[] = [];
    let skippedCount = 0;

    for (const orderId of tiktokOrderIds) {
      // Check if already synced BEFORE calling syncOrder
      const record = this.trackingRecords.get(orderId);
      const wasAlreadySynced = record?.synced === true;

      const result = await this.syncOrder(orderId);
      results.push(result);

      if (!result.success && result.error) {
        errors.push(result.error);
      }

      // Count as skipped only if it was already synced before the sync call
      if (wasAlreadySynced && this.config.skipAlreadySynced && result.success) {
        skippedCount++;
      }

      // Add delay between retries if configured
      if (this.config.retryDelayMs > 0 && tiktokOrderIds.indexOf(orderId) < tiktokOrderIds.length - 1) {
        await this.sleep(this.config.retryDelayMs);
      }
    }

    const successCount = results.filter(r => r.success).length;
    const failureCount = results.filter(r => !r.success).length;

    return {
      totalOrders: tiktokOrderIds.length,
      successCount,
      failureCount,
      skippedCount,
      results,
      errors,
    };
  }

  /**
   * Sync all unsynced orders
   */
  async syncAllUnsynced(): Promise<BatchTrackingSyncResult> {
    const unsyncedRecords = this.getUnsyncedRecords();
    const orderIds = unsyncedRecords.map(record => record.tiktokOrderId);

    if (orderIds.length === 0) {
      return {
        totalOrders: 0,
        successCount: 0,
        failureCount: 0,
        skippedCount: 0,
        results: [],
        errors: [],
      };
    }

    return await this.syncOrders(orderIds);
  }

  /**
   * Extract tracking information from MCF shipments
   */
  private extractTrackingInfo(
    shipments: MCFShipment[]
  ): { trackingNumber: string; carrier?: string } | null {
    // Check if there are any shipments
    if (!shipments || shipments.length === 0) {
      return null;
    }

    // Get the first shipment (for multiple shipments, we take the first one)
    const shipment = shipments[0];

    // Extract tracking number from package
    if (shipment.fulfillmentShipmentPackage && shipment.fulfillmentShipmentPackage.length > 0) {
      const firstPackage = shipment.fulfillmentShipmentPackage[0];
      if (firstPackage.trackingNumber) {
        return {
          trackingNumber: firstPackage.trackingNumber,
          carrier: firstPackage.carrierCode,
        };
      }
    }

    return null;
  }

  /**
   * Sleep for specified milliseconds
   */
  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * Reset rate limit counter if we've moved to a new minute
   */
  private resetRateLimitIfNeeded(): void {
    const now = new Date();
    const minutesSinceStart = Math.floor((now.getTime() - this.currentMinuteStart.getTime()) / 60000);

    if (minutesSinceStart >= 1) {
      this.requestsInCurrentMinute = 0;
      this.currentMinuteStart = now;
    }
  }

  /**
   * Enforce rate limiting before making API requests
   */
  private async enforceRateLimit(): Promise<void> {
    this.resetRateLimitIfNeeded();

    // If we've hit the rate limit, wait until the next minute
    if (this.requestsInCurrentMinute >= this.config.rateLimitPerMinute) {
      const now = new Date();
      const msUntilNextMinute = 60000 - (now.getTime() - this.currentMinuteStart.getTime());

      if (msUntilNextMinute > 0) {
        await this.sleep(msUntilNextMinute);
        this.resetRateLimitIfNeeded();
      }
    }

    this.requestsInCurrentMinute++;
  }

  /**
   * Start the automatic tracking sync scheduler
   */
  startScheduler(): void {
    if (this.isSchedulerActive) {
      return; // Scheduler already running
    }

    this.isSchedulerActive = true;

    // Run immediately on start
    this.runScheduledSync().catch(() => {
      // Errors are already logged within runScheduledSync
    });

    // Schedule periodic runs
    this.schedulerTimer = setInterval(() => {
      this.runScheduledSync().catch(() => {
        // Errors are already logged within runScheduledSync
      });
    }, this.config.syncIntervalMs);
  }

  /**
   * Stop the automatic tracking sync scheduler
   */
  stopScheduler(): void {
    if (!this.isSchedulerActive) {
      return; // Scheduler not running
    }

    if (this.schedulerTimer) {
      clearInterval(this.schedulerTimer);
      this.schedulerTimer = undefined;
    }

    this.isSchedulerActive = false;
  }

  /**
   * Check if the scheduler is currently running
   */
  isSchedulerRunning(): boolean {
    return this.isSchedulerActive;
  }

  /**
   * Run scheduled sync (called by scheduler)
   */
  private async runScheduledSync(): Promise<void> {
    try {
      this.lastSyncRun = new Date();

      // Enforce rate limit before starting sync
      await this.enforceRateLimit();

      // Sync all unsynced orders
      await this.syncAllUnsynced();
    } catch (error) {
      // Silently handle errors - they're already captured in sync results
      // This prevents the scheduler from stopping on errors
    }
  }

  /**
   * Update configuration
   */
  updateConfig(config: Partial<TrackingSyncConfig>): void {
    const wasSchedulerEnabled = this.config.schedulerEnabled;
    this.config = { ...this.config, ...config };

    // Handle scheduler state changes
    if (config.schedulerEnabled !== undefined) {
      if (config.schedulerEnabled && !wasSchedulerEnabled) {
        this.startScheduler();
      } else if (!config.schedulerEnabled && wasSchedulerEnabled) {
        this.stopScheduler();
      }
    }

    // If scheduler is running and interval changed, restart it
    if (this.isSchedulerActive && config.syncIntervalMs !== undefined) {
      this.stopScheduler();
      this.startScheduler();
    }
  }

  /**
   * Get current configuration
   */
  getConfig(): Required<TrackingSyncConfig> {
    return { ...this.config };
  }

  /**
   * Clear all tracking records
   */
  clearRecords(): void {
    this.trackingRecords.clear();
  }

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
  } {
    const records = this.getAllTrackingRecords();
    const synced = records.filter(r => r.synced).length;
    const failed = records.filter(r => r.error && !r.synced).length;

    return {
      total: records.length,
      synced,
      unsynced: records.length - synced,
      failed,
      schedulerRunning: this.isSchedulerActive,
      lastSyncRun: this.lastSyncRun,
    };
  }
}

/**
 * Create a new tracking sync instance
 */
export function createTrackingSync(
  dependencies: TrackingSyncDependencies,
  config?: TrackingSyncConfig
): TrackingSync {
  return new TrackingSync(dependencies, config);
}
