"use strict";
/**
 * Inventory Sync Service - Manages inventory synchronization with Amazon FBA
 *
 * Features:
 * - Checks Amazon FBA inventory levels for SKUs
 * - Prevents overselling by validating inventory before order creation
 * - Caches inventory data to reduce API calls
 * - Configurable low inventory thresholds and warnings
 * - Batch inventory checks for efficiency
 * - Automatic cache invalidation with configurable TTL
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.InventorySync = exports.GetInventorySummariesResponseSchema = exports.InventorySummarySchema = void 0;
exports.createInventorySync = createInventorySync;
const common_1 = require("../types/common");
const zod_1 = require("zod");
// ============================================================
// Zod Schemas for Amazon FBA Inventory API
// ============================================================
/**
 * Amazon FBA Inventory Summary schema
 * Based on SP-API FBA Inventory API v1
 */
exports.InventorySummarySchema = zod_1.z.object({
    asin: zod_1.z.string().optional(),
    fnSku: zod_1.z.string().optional(), // Fulfillment Network SKU (Amazon's internal SKU)
    sellerSku: zod_1.z.string(),
    condition: zod_1.z.enum(['NewItem', 'NewWithWarranty', 'NewOEM', 'NewOpenBox', 'UsedLikeNew', 'UsedVeryGood', 'UsedGood', 'UsedAcceptable', 'UsedPoor', 'UsedRefurbished', 'CollectibleLikeNew', 'CollectibleVeryGood', 'CollectibleGood', 'CollectibleAcceptable', 'CollectiblePoor', 'RefurbishedWithWarranty', 'Refurbished', 'Club']).optional(),
    inventoryDetails: zod_1.z.object({
        fulfillableQuantity: zod_1.z.number().int().nonnegative().optional(),
        inboundWorkingQuantity: zod_1.z.number().int().nonnegative().optional(),
        inboundShippedQuantity: zod_1.z.number().int().nonnegative().optional(),
        inboundReceivingQuantity: zod_1.z.number().int().nonnegative().optional(),
        reservedQuantity: zod_1.z.object({
            totalReservedQuantity: zod_1.z.number().int().nonnegative().optional(),
            pendingCustomerOrderQuantity: zod_1.z.number().int().nonnegative().optional(),
            pendingTransshipmentQuantity: zod_1.z.number().int().nonnegative().optional(),
            fcProcessingQuantity: zod_1.z.number().int().nonnegative().optional(),
        }).optional(),
        researchingQuantity: zod_1.z.object({
            totalResearchingQuantity: zod_1.z.number().int().nonnegative().optional(),
            researchingQuantityBreakdown: zod_1.z.array(zod_1.z.object({
                name: zod_1.z.string(),
                quantity: zod_1.z.number().int().nonnegative(),
            })).optional(),
        }).optional(),
        unfulfillableQuantity: zod_1.z.number().int().nonnegative().optional(),
    }).optional(),
    lastUpdatedTime: zod_1.z.string().optional(), // ISO 8601 date-time
    productName: zod_1.z.string().optional(),
    totalQuantity: zod_1.z.number().int().nonnegative().optional(),
});
exports.GetInventorySummariesResponseSchema = zod_1.z.object({
    granularity: zod_1.z.object({
        granularityType: zod_1.z.enum(['Marketplace']),
        granularityId: zod_1.z.string(),
    }),
    inventorySummaries: zod_1.z.array(exports.InventorySummarySchema),
    pagination: zod_1.z.object({
        nextToken: zod_1.z.string().optional(),
    }).optional(),
});
// ============================================================
// Constants
// ============================================================
const DEFAULT_INVENTORY_SYNC_CONFIG = {
    cacheTtlMs: 5 * 60 * 1000, // 5 minutes
    lowStockThreshold: 10,
    enableCaching: true,
    batchSize: 50, // Amazon allows up to 50 SKUs per request
    safetyStock: 0,
};
// API path for FBA Inventory
const GET_INVENTORY_SUMMARIES_PATH = '/fba/inventory/v1/summaries';
// ============================================================
// Helper Functions
// ============================================================
/**
 * Sleep for specified milliseconds
 */
function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}
// ============================================================
// InventorySync Class
// ============================================================
/**
 * InventorySync manages inventory synchronization with Amazon FBA
 */
class InventorySync {
    config;
    amazonClient;
    inventoryCache;
    constructor(dependencies, config) {
        this.amazonClient = dependencies.amazonClient;
        this.config = { ...DEFAULT_INVENTORY_SYNC_CONFIG, ...config };
        this.inventoryCache = new Map();
    }
    /**
     * Check inventory for a single SKU
     */
    async checkInventory(sku, requestedQuantity) {
        // Check cache first (if enabled)
        if (this.config.enableCaching) {
            const cached = this.getCachedInventory(sku);
            if (cached) {
                const available = Math.max(0, cached.fulfillableQuantity - this.config.safetyStock);
                const sufficient = available >= requestedQuantity;
                const lowStock = cached.fulfillableQuantity <= this.config.lowStockThreshold;
                return {
                    sku,
                    available,
                    requested: requestedQuantity,
                    sufficient,
                    lowStock,
                    cached: true,
                    lastUpdated: cached.lastUpdated,
                };
            }
        }
        // Fetch from Amazon API
        try {
            const inventoryData = await this.fetchInventoryFromAmazon([sku]);
            if (inventoryData.length === 0) {
                return {
                    sku,
                    available: 0,
                    requested: requestedQuantity,
                    sufficient: false,
                    lowStock: true,
                    cached: false,
                    error: {
                        sku,
                        code: common_1.ErrorCode.INVENTORY_CHECK_FAILED,
                        message: `SKU ${sku} not found in Amazon FBA inventory`,
                        timestamp: new Date(),
                    },
                };
            }
            const inventory = inventoryData[0];
            const fulfillableQty = inventory.fulfillableQuantity;
            const available = Math.max(0, fulfillableQty - this.config.safetyStock);
            const sufficient = available >= requestedQuantity;
            const lowStock = fulfillableQty <= this.config.lowStockThreshold;
            return {
                sku,
                available,
                requested: requestedQuantity,
                sufficient,
                lowStock,
                cached: false,
                lastUpdated: new Date(),
            };
        }
        catch (error) {
            const syncError = {
                sku,
                code: common_1.ErrorCode.INVENTORY_CHECK_FAILED,
                message: `Failed to check inventory for SKU ${sku}: ${error instanceof Error ? error.message : 'Unknown error'}`,
                details: error,
                timestamp: new Date(),
            };
            return {
                sku,
                available: 0,
                requested: requestedQuantity,
                sufficient: false,
                lowStock: true,
                cached: false,
                error: syncError,
            };
        }
    }
    /**
     * Check inventory for multiple SKUs (with quantities)
     */
    async checkInventoryBatch(skuQuantities) {
        const results = [];
        const errors = [];
        // Process in batches based on batchSize config
        for (let i = 0; i < skuQuantities.length; i += this.config.batchSize) {
            const batch = skuQuantities.slice(i, i + this.config.batchSize);
            // Check which SKUs are in cache
            const cachedResults = [];
            const skusToFetch = [];
            for (const item of batch) {
                if (this.config.enableCaching) {
                    const cached = this.getCachedInventory(item.sku);
                    if (cached) {
                        const available = Math.max(0, cached.fulfillableQuantity - this.config.safetyStock);
                        const sufficient = available >= item.quantity;
                        const lowStock = cached.fulfillableQuantity <= this.config.lowStockThreshold;
                        cachedResults.push({
                            sku: item.sku,
                            available,
                            requested: item.quantity,
                            sufficient,
                            lowStock,
                            cached: true,
                            lastUpdated: cached.lastUpdated,
                        });
                        continue;
                    }
                }
                skusToFetch.push(item);
            }
            // Add cached results
            results.push(...cachedResults);
            // Fetch non-cached SKUs from Amazon
            if (skusToFetch.length > 0) {
                try {
                    const inventoryData = await this.fetchInventoryFromAmazon(skusToFetch.map(item => item.sku));
                    // Create a map for quick lookup
                    const inventoryMap = new Map(inventoryData.map(inv => [inv.sku, inv]));
                    for (const item of skusToFetch) {
                        const inventory = inventoryMap.get(item.sku);
                        if (!inventory) {
                            const error = {
                                sku: item.sku,
                                code: common_1.ErrorCode.INVENTORY_CHECK_FAILED,
                                message: `SKU ${item.sku} not found in Amazon FBA inventory`,
                                timestamp: new Date(),
                            };
                            errors.push(error);
                            results.push({
                                sku: item.sku,
                                available: 0,
                                requested: item.quantity,
                                sufficient: false,
                                lowStock: true,
                                cached: false,
                                error,
                            });
                            continue;
                        }
                        const available = Math.max(0, inventory.fulfillableQuantity - this.config.safetyStock);
                        const sufficient = available >= item.quantity;
                        const lowStock = inventory.fulfillableQuantity <= this.config.lowStockThreshold;
                        results.push({
                            sku: item.sku,
                            available,
                            requested: item.quantity,
                            sufficient,
                            lowStock,
                            cached: false,
                            lastUpdated: new Date(),
                        });
                    }
                }
                catch (error) {
                    // If batch fetch fails, mark all SKUs in this batch as errors
                    for (const item of skusToFetch) {
                        const syncError = {
                            sku: item.sku,
                            code: common_1.ErrorCode.INVENTORY_CHECK_FAILED,
                            message: `Failed to check inventory: ${error instanceof Error ? error.message : 'Unknown error'}`,
                            details: error,
                            timestamp: new Date(),
                        };
                        errors.push(syncError);
                        results.push({
                            sku: item.sku,
                            available: 0,
                            requested: item.quantity,
                            sufficient: false,
                            lowStock: true,
                            cached: false,
                            error: syncError,
                        });
                    }
                }
            }
        }
        const sufficientCount = results.filter(r => r.sufficient).length;
        const insufficientCount = results.filter(r => !r.sufficient).length;
        const lowStockCount = results.filter(r => r.lowStock).length;
        const errorCount = errors.length;
        return {
            totalSkus: skuQuantities.length,
            sufficientCount,
            insufficientCount,
            lowStockCount,
            errorCount,
            results,
            errors,
        };
    }
    /**
     * Refresh inventory cache for specific SKUs
     */
    async refreshInventory(skus) {
        // Process in batches
        for (let i = 0; i < skus.length; i += this.config.batchSize) {
            const batch = skus.slice(i, i + this.config.batchSize);
            await this.fetchInventoryFromAmazon(batch);
        }
    }
    /**
     * Clear inventory cache
     */
    clearCache() {
        this.inventoryCache.clear();
    }
    /**
     * Clear expired cache entries
     */
    clearExpiredCache() {
        const now = new Date();
        for (const [sku, entry] of this.inventoryCache.entries()) {
            if (entry.expiresAt < now) {
                this.inventoryCache.delete(sku);
            }
        }
    }
    /**
     * Get cached inventory for a SKU (if not expired)
     */
    getCachedInventory(sku) {
        const cached = this.inventoryCache.get(sku);
        if (!cached) {
            return null;
        }
        // Check if expired
        if (cached.expiresAt < new Date()) {
            this.inventoryCache.delete(sku);
            return null;
        }
        return cached;
    }
    /**
     * Fetch inventory from Amazon FBA API and update cache
     */
    async fetchInventoryFromAmazon(skus) {
        if (skus.length === 0) {
            return [];
        }
        // Call Amazon FBA Inventory API
        // Note: This uses a custom method we'll need to add to AmazonMCFClient
        // For now, we'll use a type assertion and assume the method exists
        const amazonClient = this.amazonClient;
        if (!amazonClient.getInventorySummaries) {
            throw new Error('AmazonMCFClient.getInventorySummaries method not implemented');
        }
        try {
            const response = await amazonClient.getInventorySummaries({
                sellerSkus: skus,
            });
            const inventoryEntries = [];
            const now = new Date();
            const expiresAt = new Date(now.getTime() + this.config.cacheTtlMs);
            for (const summary of response.inventorySummaries) {
                const fulfillableQty = summary.inventoryDetails?.fulfillableQuantity ?? 0;
                const totalQty = summary.totalQuantity ?? 0;
                const reserved = summary.inventoryDetails?.reservedQuantity?.totalReservedQuantity ?? 0;
                const inbound = (summary.inventoryDetails?.inboundWorkingQuantity ?? 0) +
                    (summary.inventoryDetails?.inboundShippedQuantity ?? 0) +
                    (summary.inventoryDetails?.inboundReceivingQuantity ?? 0);
                const unfulfillable = summary.inventoryDetails?.unfulfillableQuantity ?? 0;
                const entry = {
                    sku: summary.sellerSku,
                    fulfillableQuantity: fulfillableQty,
                    totalQuantity: totalQty,
                    reserved,
                    inbound,
                    unfulfillable,
                    lastUpdated: now,
                    expiresAt,
                };
                inventoryEntries.push(entry);
                // Update cache
                if (this.config.enableCaching) {
                    this.inventoryCache.set(summary.sellerSku, entry);
                }
            }
            return inventoryEntries;
        }
        catch (error) {
            throw new Error(`Failed to fetch inventory from Amazon: ${error instanceof Error ? error.message : 'Unknown error'}`);
        }
    }
    /**
     * Update configuration
     */
    updateConfig(config) {
        this.config = { ...this.config, ...config };
        // Clear cache if caching was disabled
        if (config.enableCaching === false) {
            this.clearCache();
        }
    }
    /**
     * Get current configuration
     */
    getConfig() {
        return { ...this.config };
    }
    /**
     * Get cache statistics
     */
    getCacheStats() {
        const entries = Array.from(this.inventoryCache.entries()).map(([sku, entry]) => ({
            sku,
            available: entry.fulfillableQuantity,
            reserved: entry.reserved,
            inbound: entry.inbound,
            unfulfillable: entry.unfulfillable,
            lastUpdated: entry.lastUpdated,
            expiresAt: entry.expiresAt,
        }));
        return {
            size: this.inventoryCache.size,
            entries,
        };
    }
    /**
     * Get low stock SKUs from cache
     */
    getLowStockSkus() {
        const lowStockSkus = [];
        for (const [sku, entry] of this.inventoryCache.entries()) {
            if (entry.fulfillableQuantity <= this.config.lowStockThreshold) {
                lowStockSkus.push({
                    sku,
                    available: entry.fulfillableQuantity,
                    threshold: this.config.lowStockThreshold,
                });
            }
        }
        return lowStockSkus;
    }
}
exports.InventorySync = InventorySync;
/**
 * Create a new inventory sync instance
 */
function createInventorySync(dependencies, config) {
    return new InventorySync(dependencies, config);
}
//# sourceMappingURL=inventory-sync.js.map