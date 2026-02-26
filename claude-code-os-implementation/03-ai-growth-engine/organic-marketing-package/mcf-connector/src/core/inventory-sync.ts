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

import type { AmazonMCFClient } from '../clients/amazon-mcf-client';
import { ErrorCode } from '../types/common';
import { z } from 'zod';

// ============================================================
// Zod Schemas for Amazon FBA Inventory API
// ============================================================

/**
 * Amazon FBA Inventory Summary schema
 * Based on SP-API FBA Inventory API v1
 */
export const InventorySummarySchema = z.object({
  asin: z.string().optional(),
  fnSku: z.string().optional(), // Fulfillment Network SKU (Amazon's internal SKU)
  sellerSku: z.string(),
  condition: z.enum(['NewItem', 'NewWithWarranty', 'NewOEM', 'NewOpenBox', 'UsedLikeNew', 'UsedVeryGood', 'UsedGood', 'UsedAcceptable', 'UsedPoor', 'UsedRefurbished', 'CollectibleLikeNew', 'CollectibleVeryGood', 'CollectibleGood', 'CollectibleAcceptable', 'CollectiblePoor', 'RefurbishedWithWarranty', 'Refurbished', 'Club']).optional(),
  inventoryDetails: z.object({
    fulfillableQuantity: z.number().int().nonnegative().optional(),
    inboundWorkingQuantity: z.number().int().nonnegative().optional(),
    inboundShippedQuantity: z.number().int().nonnegative().optional(),
    inboundReceivingQuantity: z.number().int().nonnegative().optional(),
    reservedQuantity: z.object({
      totalReservedQuantity: z.number().int().nonnegative().optional(),
      pendingCustomerOrderQuantity: z.number().int().nonnegative().optional(),
      pendingTransshipmentQuantity: z.number().int().nonnegative().optional(),
      fcProcessingQuantity: z.number().int().nonnegative().optional(),
    }).optional(),
    researchingQuantity: z.object({
      totalResearchingQuantity: z.number().int().nonnegative().optional(),
      researchingQuantityBreakdown: z.array(z.object({
        name: z.string(),
        quantity: z.number().int().nonnegative(),
      })).optional(),
    }).optional(),
    unfulfillableQuantity: z.number().int().nonnegative().optional(),
  }).optional(),
  lastUpdatedTime: z.string().optional(), // ISO 8601 date-time
  productName: z.string().optional(),
  totalQuantity: z.number().int().nonnegative().optional(),
});

export const GetInventorySummariesResponseSchema = z.object({
  granularity: z.object({
    granularityType: z.enum(['Marketplace']),
    granularityId: z.string(),
  }),
  inventorySummaries: z.array(InventorySummarySchema),
  pagination: z.object({
    nextToken: z.string().optional(),
  }).optional(),
});

// ============================================================
// Types
// ============================================================

/**
 * Amazon FBA Inventory Summary
 */
export type InventorySummary = z.infer<typeof InventorySummarySchema>;

/**
 * Get Inventory Summaries API Response
 */
export type GetInventorySummariesResponse = z.infer<typeof GetInventorySummariesResponseSchema>;

/**
 * Inventory cache entry
 */
export interface InventoryCacheEntry {
  sku: string;
  fulfillableQuantity: number;
  totalQuantity: number;
  reserved: number;
  inbound: number;
  unfulfillable: number;
  lastUpdated: Date;
  expiresAt: Date;
}

/**
 * Inventory check result for a single SKU
 */
export interface InventoryCheckResult {
  sku: string;
  available: number;
  requested: number;
  sufficient: boolean;
  lowStock: boolean;
  cached: boolean;
  lastUpdated?: Date;
  error?: InventorySyncError;
}

/**
 * Batch inventory check result
 */
export interface BatchInventoryCheckResult {
  totalSkus: number;
  sufficientCount: number;
  insufficientCount: number;
  lowStockCount: number;
  errorCount: number;
  results: InventoryCheckResult[];
  errors: InventorySyncError[];
}

/**
 * Inventory sync error
 */
export interface InventorySyncError {
  sku: string;
  code: ErrorCode;
  message: string;
  details?: unknown;
  timestamp: Date;
}

/**
 * Inventory sync configuration
 */
export interface InventorySyncConfig {
  cacheTtlMs?: number; // Cache time-to-live in milliseconds
  lowStockThreshold?: number; // Warn when stock below this level
  enableCaching?: boolean; // Enable inventory caching
  batchSize?: number; // Max SKUs per batch request
  safetyStock?: number; // Reserve this much stock (don't consider available)
}

/**
 * Dependencies for InventorySync service
 */
export interface InventorySyncDependencies {
  amazonClient: AmazonMCFClient;
}

// ============================================================
// Constants
// ============================================================

const DEFAULT_INVENTORY_SYNC_CONFIG: Required<InventorySyncConfig> = {
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
function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// ============================================================
// InventorySync Class
// ============================================================

/**
 * InventorySync manages inventory synchronization with Amazon FBA
 */
export class InventorySync {
  private config: Required<InventorySyncConfig>;
  private amazonClient: AmazonMCFClient;
  private inventoryCache: Map<string, InventoryCacheEntry>;

  constructor(
    dependencies: InventorySyncDependencies,
    config?: InventorySyncConfig
  ) {
    this.amazonClient = dependencies.amazonClient;
    this.config = { ...DEFAULT_INVENTORY_SYNC_CONFIG, ...config };
    this.inventoryCache = new Map();
  }

  /**
   * Check inventory for a single SKU
   */
  async checkInventory(sku: string, requestedQuantity: number): Promise<InventoryCheckResult> {
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
            code: ErrorCode.INVENTORY_CHECK_FAILED,
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
    } catch (error) {
      const syncError: InventorySyncError = {
        sku,
        code: ErrorCode.INVENTORY_CHECK_FAILED,
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
  async checkInventoryBatch(
    skuQuantities: Array<{ sku: string; quantity: number }>
  ): Promise<BatchInventoryCheckResult> {
    const results: InventoryCheckResult[] = [];
    const errors: InventorySyncError[] = [];

    // Process in batches based on batchSize config
    for (let i = 0; i < skuQuantities.length; i += this.config.batchSize) {
      const batch = skuQuantities.slice(i, i + this.config.batchSize);

      // Check which SKUs are in cache
      const cachedResults: InventoryCheckResult[] = [];
      const skusToFetch: Array<{ sku: string; quantity: number }> = [];

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
          const inventoryData = await this.fetchInventoryFromAmazon(
            skusToFetch.map(item => item.sku)
          );

          // Create a map for quick lookup
          const inventoryMap = new Map(
            inventoryData.map(inv => [inv.sku, inv])
          );

          for (const item of skusToFetch) {
            const inventory = inventoryMap.get(item.sku);

            if (!inventory) {
              const error: InventorySyncError = {
                sku: item.sku,
                code: ErrorCode.INVENTORY_CHECK_FAILED,
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
        } catch (error) {
          // If batch fetch fails, mark all SKUs in this batch as errors
          for (const item of skusToFetch) {
            const syncError: InventorySyncError = {
              sku: item.sku,
              code: ErrorCode.INVENTORY_CHECK_FAILED,
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
  async refreshInventory(skus: string[]): Promise<void> {
    // Process in batches
    for (let i = 0; i < skus.length; i += this.config.batchSize) {
      const batch = skus.slice(i, i + this.config.batchSize);
      await this.fetchInventoryFromAmazon(batch);
    }
  }

  /**
   * Clear inventory cache
   */
  clearCache(): void {
    this.inventoryCache.clear();
  }

  /**
   * Clear expired cache entries
   */
  clearExpiredCache(): void {
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
  private getCachedInventory(sku: string): InventoryCacheEntry | null {
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
  private async fetchInventoryFromAmazon(skus: string[]): Promise<InventoryCacheEntry[]> {
    if (skus.length === 0) {
      return [];
    }

    // Call Amazon FBA Inventory API
    // Note: This uses a custom method we'll need to add to AmazonMCFClient
    // For now, we'll use a type assertion and assume the method exists
    const amazonClient = this.amazonClient as AmazonMCFClient & {
      getInventorySummaries?: (params: { sellerSkus: string[]; marketplaceIds?: string[] }) => Promise<GetInventorySummariesResponse>;
    };

    if (!amazonClient.getInventorySummaries) {
      throw new Error('AmazonMCFClient.getInventorySummaries method not implemented');
    }

    try {
      const response = await amazonClient.getInventorySummaries({
        sellerSkus: skus,
      });

      const inventoryEntries: InventoryCacheEntry[] = [];
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

        const entry: InventoryCacheEntry = {
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
    } catch (error) {
      throw new Error(`Failed to fetch inventory from Amazon: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Update configuration
   */
  updateConfig(config: Partial<InventorySyncConfig>): void {
    this.config = { ...this.config, ...config };

    // Clear cache if caching was disabled
    if (config.enableCaching === false) {
      this.clearCache();
    }
  }

  /**
   * Get current configuration
   */
  getConfig(): Required<InventorySyncConfig> {
    return { ...this.config };
  }

  /**
   * Get cache statistics
   */
  getCacheStats(): {
    size: number;
    entries: Array<{
      sku: string;
      available: number;
      reserved: number;
      inbound: number;
      unfulfillable: number;
      lastUpdated: Date;
      expiresAt: Date;
    }>;
  } {
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
  getLowStockSkus(): Array<{ sku: string; available: number; threshold: number }> {
    const lowStockSkus: Array<{ sku: string; available: number; threshold: number }> = [];

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

/**
 * Create a new inventory sync instance
 */
export function createInventorySync(
  dependencies: InventorySyncDependencies,
  config?: InventorySyncConfig
): InventorySync {
  return new InventorySync(dependencies, config);
}
