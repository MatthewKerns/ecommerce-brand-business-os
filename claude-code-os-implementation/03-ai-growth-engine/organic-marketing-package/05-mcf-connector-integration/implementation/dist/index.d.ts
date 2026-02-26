/**
 * MCF Connector - TikTok Shop to Amazon MCF Order Routing
 *
 * Main entry point for the TikTok Shop to Amazon Multi-Channel Fulfillment integration
 */
export { loadConfig } from './config';
export { TikTokShopClient } from './clients/tiktok-shop-client';
export type { TikTokShopClientConfig, TikTokApiResponse, TikTokShopError, } from './clients/tiktok-shop-client';
export { AmazonMCFClient } from './clients/amazon-mcf-client';
export type { AmazonMCFClientConfig, LWATokenResponse, AmazonApiError, } from './clients/amazon-mcf-client';
export { OrderValidator } from './core/order-validator';
export type { ValidatorConfig, OrderValidationResult, ValidationError, ValidationWarning, } from './core/order-validator';
export { OrderTransformer } from './core/order-transformer';
export type { TransformerConfig, OrderTransformationResult, TransformationError, TransformationWarning, SKUMapping, } from './core/order-transformer';
export { OrderRouter } from './core/order-router';
export type { OrderRouterConfig, OrderRouterDependencies, OrderRoutingResult, OrderRoutingSuccess, OrderRoutingError, OrderRoutingWarning, BatchRoutingResult, } from './core/order-router';
export { TrackingSync } from './core/tracking-sync';
export type { TrackingSyncConfig, TrackingSyncDependencies, OrderTrackingRecord, TrackingSyncResult, TrackingSyncError, BatchTrackingSyncResult, } from './core/tracking-sync';
export { InventorySync } from './core/inventory-sync';
export type { InventorySyncConfig, InventorySyncDependencies, InventorySummary, InventoryCheckResult, InventorySyncError, InventoryCacheEntry, BatchInventoryCheckResult, } from './core/inventory-sync';
export type { MCFConnectorConfig, TikTokShopConfig, AmazonMCFConfig, ConnectorConfig, DatabaseConfig, RetryConfig, } from './types/config';
export type { TikTokOrder, TikTokOrderItem, TikTokAddress, TikTokPaymentInfo, TikTokPackage, TikTokBuyerInfo, NormalizedTikTokOrder, TikTokOrderValidationResult, } from './types/tiktok-order';
export type { MCFAddress, MCFOrderItem, MCFFulfillmentOrder, MCFFulfillmentOrderRequest, MCFShipment, MCFPackageTrackingDetails, CreateMCFOrderParams, NormalizedMCFOrder, MCFOrderValidationResult, MCFTrackingInfo, } from './types/mcf-order';
export type { Address, OrderItem, TrackingInfo, ConnectorError, Result, SuccessResult, ErrorResult, PaginationParams, PaginatedResponse, WebhookEvent, PartialBy, RequiredBy, } from './types/common';
export { TikTokOrderStatus, MCFFulfillmentStatus, ProcessingStatus, ShipmentCarrier, ErrorCode, WebhookEventType, } from './types/common';
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
export declare class MCFConnector {
    tiktok: TikTokShopClient;
    amazon: AmazonMCFClient;
    validator: OrderValidator;
    transformer: OrderTransformer;
    router: OrderRouter;
    trackingSync: TrackingSync;
    inventorySync?: InventorySync;
    private config;
    constructor(options: MCFConnectorOptions);
    /**
     * Test connectivity to both TikTok Shop and Amazon MCF APIs
     */
    testConnections(): Promise<{
        tiktok: boolean;
        amazon: boolean;
    }>;
    /**
     * Route a single TikTok order to Amazon MCF
     *
     * @param orderId - TikTok order ID
     * @returns Order routing result
     */
    routeOrder(orderId: string): Promise<OrderRoutingResult>;
    /**
     * Route multiple TikTok orders to Amazon MCF
     *
     * @param orderIds - Array of TikTok order IDs
     * @returns Batch routing results
     */
    routeOrders(orderIds: string[]): Promise<BatchRoutingResult>;
    /**
     * Route all pending TikTok orders to Amazon MCF
     *
     * Automatically fetches all AWAITING_SHIPMENT and AWAITING_COLLECTION orders
     * from TikTok Shop and routes them to Amazon MCF.
     *
     * @returns Batch routing results
     */
    routePendingOrders(): Promise<BatchRoutingResult>;
    /**
     * Sync tracking number for a specific order
     *
     * @param tiktokOrderId - TikTok order ID
     * @returns Tracking sync result
     */
    syncTracking(tiktokOrderId: string): Promise<TrackingSyncResult>;
    /**
     * Add order to tracking sync queue
     *
     * @param tiktokOrderId - TikTok order ID
     * @param mcfFulfillmentOrderId - Amazon MCF fulfillment order ID
     */
    addOrderToTrackingQueue(tiktokOrderId: string, mcfFulfillmentOrderId: string): void;
    /**
     * Sync tracking numbers for all unsynced orders
     *
     * @returns Batch tracking sync results
     */
    syncAllTracking(): Promise<BatchTrackingSyncResult>;
    /**
     * Check inventory for a specific SKU
     *
     * @param sku - Amazon seller SKU
     * @param quantity - Required quantity (default: 1)
     * @returns Inventory check result
     */
    checkInventory(sku: string, quantity?: number): Promise<InventoryCheckResult>;
    /**
     * Get low stock SKUs
     *
     * @returns Array of SKUs with low stock details
     */
    getLowStockSkus(): Array<{
        sku: string;
        available: number;
        threshold: number;
    }>;
    /**
     * Add SKU mapping for order transformation
     *
     * @param tiktokSku - TikTok product SKU
     * @param amazonSku - Amazon seller SKU
     */
    addSkuMapping(tiktokSku: string, amazonSku: string): void;
    /**
     * Start automatic tracking sync scheduler
     *
     * The scheduler runs at the configured interval (default: 30 minutes)
     */
    startTrackingSyncScheduler(): void;
    /**
     * Stop automatic tracking sync scheduler
     */
    stopTrackingSyncScheduler(): void;
    /**
     * Get tracking sync statistics
     */
    getTrackingSyncStats(): {
        total: number;
        synced: number;
        unsynced: number;
        failed: number;
        schedulerRunning: boolean;
        lastSyncRun?: Date;
    };
    /**
     * Graceful shutdown - cleanup resources and stop schedulers
     */
    shutdown(): Promise<void>;
}
//# sourceMappingURL=index.d.ts.map