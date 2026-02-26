"use strict";
/**
 * MCF Connector - TikTok Shop to Amazon MCF Order Routing
 *
 * Main entry point for the TikTok Shop to Amazon Multi-Channel Fulfillment integration
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.MCFConnector = exports.WebhookEventType = exports.ErrorCode = exports.ShipmentCarrier = exports.ProcessingStatus = exports.MCFFulfillmentStatus = exports.TikTokOrderStatus = exports.InventorySync = exports.TrackingSync = exports.OrderRouter = exports.OrderTransformer = exports.OrderValidator = exports.AmazonMCFClient = exports.TikTokShopClient = exports.loadConfig = void 0;
// ============================================================
// Export Configuration Loader
// ============================================================
var config_1 = require("./config");
Object.defineProperty(exports, "loadConfig", { enumerable: true, get: function () { return config_1.loadConfig; } });
// ============================================================
// Export API Clients
// ============================================================
var tiktok_shop_client_1 = require("./clients/tiktok-shop-client");
Object.defineProperty(exports, "TikTokShopClient", { enumerable: true, get: function () { return tiktok_shop_client_1.TikTokShopClient; } });
var amazon_mcf_client_1 = require("./clients/amazon-mcf-client");
Object.defineProperty(exports, "AmazonMCFClient", { enumerable: true, get: function () { return amazon_mcf_client_1.AmazonMCFClient; } });
// ============================================================
// Export Core Services
// ============================================================
var order_validator_1 = require("./core/order-validator");
Object.defineProperty(exports, "OrderValidator", { enumerable: true, get: function () { return order_validator_1.OrderValidator; } });
var order_transformer_1 = require("./core/order-transformer");
Object.defineProperty(exports, "OrderTransformer", { enumerable: true, get: function () { return order_transformer_1.OrderTransformer; } });
var order_router_1 = require("./core/order-router");
Object.defineProperty(exports, "OrderRouter", { enumerable: true, get: function () { return order_router_1.OrderRouter; } });
var tracking_sync_1 = require("./core/tracking-sync");
Object.defineProperty(exports, "TrackingSync", { enumerable: true, get: function () { return tracking_sync_1.TrackingSync; } });
var inventory_sync_1 = require("./core/inventory-sync");
Object.defineProperty(exports, "InventorySync", { enumerable: true, get: function () { return inventory_sync_1.InventorySync; } });
var common_1 = require("./types/common");
Object.defineProperty(exports, "TikTokOrderStatus", { enumerable: true, get: function () { return common_1.TikTokOrderStatus; } });
Object.defineProperty(exports, "MCFFulfillmentStatus", { enumerable: true, get: function () { return common_1.MCFFulfillmentStatus; } });
Object.defineProperty(exports, "ProcessingStatus", { enumerable: true, get: function () { return common_1.ProcessingStatus; } });
Object.defineProperty(exports, "ShipmentCarrier", { enumerable: true, get: function () { return common_1.ShipmentCarrier; } });
Object.defineProperty(exports, "ErrorCode", { enumerable: true, get: function () { return common_1.ErrorCode; } });
Object.defineProperty(exports, "WebhookEventType", { enumerable: true, get: function () { return common_1.WebhookEventType; } });
// ============================================================
// Main MCF Connector Orchestrator
// ============================================================
const tiktok_shop_client_2 = require("./clients/tiktok-shop-client");
const amazon_mcf_client_2 = require("./clients/amazon-mcf-client");
const order_validator_2 = require("./core/order-validator");
const order_transformer_2 = require("./core/order-transformer");
const order_router_2 = require("./core/order-router");
const tracking_sync_2 = require("./core/tracking-sync");
const inventory_sync_2 = require("./core/inventory-sync");
/**
 * MCFConnector - Main orchestrator class
 *
 * Provides high-level API for TikTok Shop to Amazon MCF integration
 */
class MCFConnector {
    tiktok;
    amazon;
    validator;
    transformer;
    router;
    trackingSync;
    inventorySync;
    config;
    constructor(options) {
        this.config = options.config;
        // Initialize API clients
        this.tiktok = new tiktok_shop_client_2.TikTokShopClient({
            appKey: this.config.tiktok.appKey,
            appSecret: this.config.tiktok.appSecret,
            shopId: this.config.tiktok.shopId,
            apiBaseUrl: this.config.tiktok.apiBaseUrl,
            accessToken: this.config.tiktok.accessToken,
            refreshToken: this.config.tiktok.refreshToken,
        });
        this.amazon = new amazon_mcf_client_2.AmazonMCFClient({
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
        this.validator = new order_validator_2.OrderValidator({
            strictMode: true,
            allowedCountries: ['US', 'CA', 'GB'],
        });
        this.transformer = new order_transformer_2.OrderTransformer({
            defaultShippingSpeed: 'Standard',
            includeItemPrices: true,
            includeOrderComment: true,
        });
        // Initialize inventory sync (optional)
        if (options.enableInventorySync !== false) {
            this.inventorySync = new inventory_sync_2.InventorySync({ amazonClient: this.amazon }, {
                cacheTtlMs: 5 * 60 * 1000, // 5 minutes
                safetyStock: 5,
                lowStockThreshold: 10,
                batchSize: 50,
            });
        }
        // Initialize order router
        this.router = new order_router_2.OrderRouter({
            tiktokClient: this.tiktok,
            amazonClient: this.amazon,
            validator: this.validator,
            transformer: this.transformer,
            inventorySync: this.inventorySync,
        }, {
            continueOnError: true,
            maxConcurrentOrders: 5,
        });
        // Initialize tracking sync
        const trackingSyncIntervalMs = this.config.connector.trackingSyncIntervalMinutes * 60 * 1000;
        this.trackingSync = new tracking_sync_2.TrackingSync({
            tiktokClient: this.tiktok,
            amazonClient: this.amazon,
        }, {
            maxRetries: this.config.connector.retry.maxRetries || 3,
            skipAlreadySynced: true,
            updateTikTok: true,
            retryDelayMs: this.config.connector.retry.initialDelay || 1000,
            syncIntervalMs: trackingSyncIntervalMs,
            schedulerEnabled: options.enableTrackingSyncScheduler || false,
            rateLimitPerMinute: 10,
        });
    }
    /**
     * Test connectivity to both TikTok Shop and Amazon MCF APIs
     */
    async testConnections() {
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
    async routeOrder(orderId) {
        return await this.router.routeOrder(orderId);
    }
    /**
     * Route multiple TikTok orders to Amazon MCF
     *
     * @param orderIds - Array of TikTok order IDs
     * @returns Batch routing results
     */
    async routeOrders(orderIds) {
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
    async routePendingOrders() {
        return await this.router.routePendingOrders();
    }
    /**
     * Sync tracking number for a specific order
     *
     * @param tiktokOrderId - TikTok order ID
     * @returns Tracking sync result
     */
    async syncTracking(tiktokOrderId) {
        return await this.trackingSync.syncOrder(tiktokOrderId);
    }
    /**
     * Add order to tracking sync queue
     *
     * @param tiktokOrderId - TikTok order ID
     * @param mcfFulfillmentOrderId - Amazon MCF fulfillment order ID
     */
    addOrderToTrackingQueue(tiktokOrderId, mcfFulfillmentOrderId) {
        this.trackingSync.addOrder(tiktokOrderId, mcfFulfillmentOrderId);
    }
    /**
     * Sync tracking numbers for all unsynced orders
     *
     * @returns Batch tracking sync results
     */
    async syncAllTracking() {
        return await this.trackingSync.syncAllUnsynced();
    }
    /**
     * Check inventory for a specific SKU
     *
     * @param sku - Amazon seller SKU
     * @param quantity - Required quantity (default: 1)
     * @returns Inventory check result
     */
    async checkInventory(sku, quantity = 1) {
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
    getLowStockSkus() {
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
    addSkuMapping(tiktokSku, amazonSku) {
        this.transformer.addSKUMapping(tiktokSku, amazonSku);
    }
    /**
     * Start automatic tracking sync scheduler
     *
     * The scheduler runs at the configured interval (default: 30 minutes)
     */
    startTrackingSyncScheduler() {
        this.trackingSync.startScheduler();
    }
    /**
     * Stop automatic tracking sync scheduler
     */
    stopTrackingSyncScheduler() {
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
    async shutdown() {
        this.trackingSync.stopScheduler();
    }
}
exports.MCFConnector = MCFConnector;
//# sourceMappingURL=index.js.map