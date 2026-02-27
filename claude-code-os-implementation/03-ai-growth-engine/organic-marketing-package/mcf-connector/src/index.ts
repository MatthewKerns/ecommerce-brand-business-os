/**
 * MCF Connector - TikTok Shop to Amazon MCF Order Routing
 *
 * Main entry point for the TikTok Shop to Amazon Multi-Channel Fulfillment integration
 */

// ============================================================
// Export Configuration Loader
// ============================================================

export { loadConfig } from './config';

// ============================================================
// Export API Clients
// ============================================================

export { TikTokShopClient } from './clients/tiktok-shop-client';
export type {
  TikTokShopClientConfig,
  TikTokApiResponse,
  TikTokShopError,
} from './clients/tiktok-shop-client';

export { AmazonMCFClient } from './clients/amazon-mcf-client';
export type {
  AmazonMCFClientConfig,
  LWATokenResponse,
  AmazonApiError,
} from './clients/amazon-mcf-client';

// ============================================================
// Export Core Services
// ============================================================

export { OrderValidator } from './core/order-validator';
export type {
  ValidatorConfig,
  OrderValidationResult,
  ValidationError,
  ValidationWarning,
} from './core/order-validator';

export { OrderTransformer } from './core/order-transformer';
export type {
  TransformerConfig,
  OrderTransformationResult,
  TransformationError,
  TransformationWarning,
  SKUMapping,
} from './core/order-transformer';

export { OrderRouter } from './core/order-router';
export type {
  OrderRouterConfig,
  OrderRouterDependencies,
  OrderRoutingResult,
  OrderRoutingSuccess,
  OrderRoutingError,
  OrderRoutingWarning,
  BatchRoutingResult,
} from './core/order-router';

export { TrackingSync } from './core/tracking-sync';
export type {
  TrackingSyncConfig,
  TrackingSyncDependencies,
  OrderTrackingRecord,
  TrackingSyncResult,
  TrackingSyncError,
  BatchTrackingSyncResult,
} from './core/tracking-sync';

export { InventorySync } from './core/inventory-sync';
export type {
  InventorySyncConfig,
  InventorySyncDependencies,
  InventorySummary,
  InventoryCheckResult,
  InventorySyncError,
  InventoryCacheEntry,
  BatchInventoryCheckResult,
} from './core/inventory-sync';

// ============================================================
// Export Type Definitions
// ============================================================

// Configuration types
export type {
  MCFConnectorConfig,
  TikTokShopConfig,
  AmazonMCFConfig,
  ConnectorConfig,
  DatabaseConfig,
  RetryConfig,
} from './types/config';

// TikTok order types
export type {
  TikTokOrder,
  TikTokOrderItem,
  TikTokAddress,
  TikTokPaymentInfo,
  TikTokPackage,
  TikTokBuyerInfo,
  NormalizedTikTokOrder,
  TikTokOrderValidationResult,
} from './types/tiktok-order';

// TikTok analytics types
export type {
  TikTokVideoMetrics,
  TikTokVideoListResponse,
  TikTokVideoMetricsParams,
  TikTokAccountAnalytics,
  TikTokAccountAnalyticsParams,
  TikTokProductAnalytics,
  TikTokProductAnalyticsParams,
} from './types/tiktok-analytics';

// MCF order types
export type {
  MCFAddress,
  MCFOrderItem,
  MCFFulfillmentOrder,
  MCFFulfillmentOrderRequest,
  MCFShipment,
  MCFPackageTrackingDetails,
  CreateMCFOrderParams,
  NormalizedMCFOrder,
  MCFOrderValidationResult,
  MCFTrackingInfo,
} from './types/mcf-order';

// Common types
export type {
  Address,
  OrderItem,
  TrackingInfo,
  ConnectorError,
  Result,
  SuccessResult,
  ErrorResult,
  PaginationParams,
  PaginatedResponse,
  WebhookEvent,
  PartialBy,
  RequiredBy,
} from './types/common';

export {
  TikTokOrderStatus,
  MCFFulfillmentStatus,
  ProcessingStatus,
  ShipmentCarrier,
  ErrorCode,
  WebhookEventType,
} from './types/common';

// ============================================================
// Main MCF Connector Orchestrator
// ============================================================

import { TikTokShopClient } from './clients/tiktok-shop-client';
import { AmazonMCFClient } from './clients/amazon-mcf-client';
import { OrderValidator } from './core/order-validator';
import { OrderTransformer } from './core/order-transformer';
import { OrderRouter } from './core/order-router';
import { TrackingSync } from './core/tracking-sync';
import { InventorySync } from './core/inventory-sync';
import type { MCFConnectorConfig } from './types/config';
import type { OrderRoutingResult, BatchRoutingResult } from './core/order-router';
import type { TrackingSyncResult, BatchTrackingSyncResult } from './core/tracking-sync';
import type { InventoryCheckResult } from './core/inventory-sync';

export interface MCFConnectorOptions {
  config: MCFConnectorConfig;
  /**
   * Enable inventory sync (default: true)
   * When disabled, inventory checks are skipped during order routing
   */
  enableInventorySync?: boolean;
  /**
   * Enable automatic tracking sync scheduler (default: false)
   * When enabled, tracking sync runs automatically at configured intervals
   */
  enableTrackingSyncScheduler?: boolean;
}

/**
 * MCFConnector - Main orchestrator class
 *
 * Provides high-level API for TikTok Shop to Amazon MCF integration
 */
export class MCFConnector {
  public tiktok: TikTokShopClient;
  public amazon: AmazonMCFClient;
  public validator: OrderValidator;
  public transformer: OrderTransformer;
  public router: OrderRouter;
  public trackingSync: TrackingSync;
  public inventorySync?: InventorySync;

  private config: MCFConnectorConfig;

  constructor(options: MCFConnectorOptions) {
    this.config = options.config;

    // Initialize API clients
    this.tiktok = new TikTokShopClient({
      appKey: this.config.tiktok.appKey,
      appSecret: this.config.tiktok.appSecret,
      shopId: this.config.tiktok.shopId,
      apiBaseUrl: this.config.tiktok.apiBaseUrl,
      accessToken: this.config.tiktok.accessToken,
      refreshToken: this.config.tiktok.refreshToken,
    });

    this.amazon = new AmazonMCFClient({
      clientId: this.config.amazon.clientId,
      clientSecret: this.config.amazon.clientSecret,
      refreshToken: this.config.amazon.refreshToken,
      sellerId: this.config.amazon.sellerId,
      marketplaceId: this.config.amazon.marketplaceId,
      region: this.config.amazon.region,
      apiBaseUrl: this.config.amazon.apiBaseUrl,
      awsAccessKey: this.config.amazon.awsAccessKey,
      awsSecretKey: this.config.amazon.awsSecretKey,
    });

    // Initialize core services
    this.validator = new OrderValidator({
      strictMode: true,
      allowedCountries: ['US', 'CA', 'GB'],
    });

    this.transformer = new OrderTransformer({
      defaultShippingSpeed: 'Standard',
      includeItemPrices: true,
      includeOrderComment: true,
    });

    // Initialize inventory sync (optional)
    if (options.enableInventorySync !== false) {
      this.inventorySync = new InventorySync(
        { amazonClient: this.amazon },
        {
          cacheTtlMs: 5 * 60 * 1000, // 5 minutes
          safetyStock: 5,
          lowStockThreshold: 10,
          batchSize: 50,
        }
      );
    }

    // Initialize order router
    this.router = new OrderRouter(
      {
        tiktokClient: this.tiktok,
        amazonClient: this.amazon,
        validator: this.validator,
        transformer: this.transformer,
        inventorySync: this.inventorySync,
      },
      {
        continueOnError: true,
        maxConcurrentOrders: 5,
      }
    );

    // Initialize tracking sync
    const trackingSyncIntervalMs = this.config.connector.trackingSyncIntervalMinutes * 60 * 1000;
    this.trackingSync = new TrackingSync(
      {
        tiktokClient: this.tiktok,
        amazonClient: this.amazon,
      },
      {
        maxRetries: this.config.connector.retry.maxRetries || 3,
        skipAlreadySynced: true,
        updateTikTok: true,
        retryDelayMs: this.config.connector.retry.initialDelay || 1000,
        syncIntervalMs: trackingSyncIntervalMs,
        schedulerEnabled: options.enableTrackingSyncScheduler || false,
        rateLimitPerMinute: 10,
      }
    );
  }

  /**
   * Test connectivity to both TikTok Shop and Amazon MCF APIs
   */
  async testConnections(): Promise<{ tiktok: boolean; amazon: boolean }> {
    const [tiktokOk, amazonOk] = await Promise.allSettled([
      this.tiktok.testConnection(),
      this.amazon.testConnection(),
    ]);

    return {
      tiktok: tiktokOk.status === 'fulfilled' && tiktokOk.value,
      amazon: amazonOk.status === 'fulfilled' && amazonOk.value,
    };
  }

  /**
   * Route a single TikTok order to Amazon MCF
   *
   * @param orderId - TikTok order ID
   * @returns Order routing result
   */
  async routeOrder(orderId: string): Promise<OrderRoutingResult> {
    return await this.router.routeOrder(orderId);
  }

  /**
   * Route multiple TikTok orders to Amazon MCF
   *
   * @param orderIds - Array of TikTok order IDs
   * @returns Batch routing results
   */
  async routeOrders(orderIds: string[]): Promise<BatchRoutingResult> {
    return await this.router.routeOrders(orderIds);
  }

  /**
   * Route all pending TikTok orders to Amazon MCF
   *
   * Automatically fetches all AWAITING_SHIPMENT and AWAITING_COLLECTION orders
   * from TikTok Shop and routes them to Amazon MCF.
   *
   * @returns Batch routing results
   */
  async routePendingOrders(): Promise<BatchRoutingResult> {
    return await this.router.routePendingOrders();
  }

  /**
   * Sync tracking number for a specific order
   *
   * @param tiktokOrderId - TikTok order ID
   * @returns Tracking sync result
   */
  async syncTracking(tiktokOrderId: string): Promise<TrackingSyncResult> {
    return await this.trackingSync.syncOrder(tiktokOrderId);
  }

  /**
   * Add order to tracking sync queue
   *
   * @param tiktokOrderId - TikTok order ID
   * @param mcfFulfillmentOrderId - Amazon MCF fulfillment order ID
   */
  addOrderToTrackingQueue(tiktokOrderId: string, mcfFulfillmentOrderId: string): void {
    this.trackingSync.addOrder(tiktokOrderId, mcfFulfillmentOrderId);
  }

  /**
   * Sync tracking numbers for all unsynced orders
   *
   * @returns Batch tracking sync results
   */
  async syncAllTracking(): Promise<BatchTrackingSyncResult> {
    return await this.trackingSync.syncAllUnsynced();
  }

  /**
   * Check inventory for a specific SKU
   *
   * @param sku - Amazon seller SKU
   * @param quantity - Required quantity (default: 1)
   * @returns Inventory check result
   */
  async checkInventory(sku: string, quantity: number = 1): Promise<InventoryCheckResult> {
    if (!this.inventorySync) {
      throw new Error('Inventory sync is not enabled');
    }
    return await this.inventorySync.checkInventory(sku, quantity);
  }

  /**
   * Get low stock SKUs
   *
   * @returns Array of SKUs with low stock details
   */
  getLowStockSkus(): Array<{ sku: string; available: number; threshold: number }> {
    if (!this.inventorySync) {
      throw new Error('Inventory sync is not enabled');
    }
    return this.inventorySync.getLowStockSkus();
  }

  /**
   * Add SKU mapping for order transformation
   *
   * @param tiktokSku - TikTok product SKU
   * @param amazonSku - Amazon seller SKU
   */
  addSkuMapping(tiktokSku: string, amazonSku: string): void {
    this.transformer.addSKUMapping(tiktokSku, amazonSku);
  }

  /**
   * Start automatic tracking sync scheduler
   *
   * The scheduler runs at the configured interval (default: 30 minutes)
   */
  startTrackingSyncScheduler(): void {
    this.trackingSync.startScheduler();
  }

  /**
   * Stop automatic tracking sync scheduler
   */
  stopTrackingSyncScheduler(): void {
    this.trackingSync.stopScheduler();
  }

  /**
   * Get tracking sync statistics
   */
  getTrackingSyncStats() {
    return this.trackingSync.getStats();
  }

  /**
   * Graceful shutdown - cleanup resources and stop schedulers
   */
  async shutdown(): Promise<void> {
    this.trackingSync.stopScheduler();
  }
}
