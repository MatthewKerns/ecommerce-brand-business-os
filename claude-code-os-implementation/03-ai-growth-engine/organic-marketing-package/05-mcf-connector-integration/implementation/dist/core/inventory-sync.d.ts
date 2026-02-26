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
/**
 * Amazon FBA Inventory Summary schema
 * Based on SP-API FBA Inventory API v1
 */
export declare const InventorySummarySchema: z.ZodObject<{
    asin: z.ZodOptional<z.ZodString>;
    fnSku: z.ZodOptional<z.ZodString>;
    sellerSku: z.ZodString;
    condition: z.ZodOptional<z.ZodEnum<["NewItem", "NewWithWarranty", "NewOEM", "NewOpenBox", "UsedLikeNew", "UsedVeryGood", "UsedGood", "UsedAcceptable", "UsedPoor", "UsedRefurbished", "CollectibleLikeNew", "CollectibleVeryGood", "CollectibleGood", "CollectibleAcceptable", "CollectiblePoor", "RefurbishedWithWarranty", "Refurbished", "Club"]>>;
    inventoryDetails: z.ZodOptional<z.ZodObject<{
        fulfillableQuantity: z.ZodOptional<z.ZodNumber>;
        inboundWorkingQuantity: z.ZodOptional<z.ZodNumber>;
        inboundShippedQuantity: z.ZodOptional<z.ZodNumber>;
        inboundReceivingQuantity: z.ZodOptional<z.ZodNumber>;
        reservedQuantity: z.ZodOptional<z.ZodObject<{
            totalReservedQuantity: z.ZodOptional<z.ZodNumber>;
            pendingCustomerOrderQuantity: z.ZodOptional<z.ZodNumber>;
            pendingTransshipmentQuantity: z.ZodOptional<z.ZodNumber>;
            fcProcessingQuantity: z.ZodOptional<z.ZodNumber>;
        }, "strip", z.ZodTypeAny, {
            totalReservedQuantity?: number | undefined;
            pendingCustomerOrderQuantity?: number | undefined;
            pendingTransshipmentQuantity?: number | undefined;
            fcProcessingQuantity?: number | undefined;
        }, {
            totalReservedQuantity?: number | undefined;
            pendingCustomerOrderQuantity?: number | undefined;
            pendingTransshipmentQuantity?: number | undefined;
            fcProcessingQuantity?: number | undefined;
        }>>;
        researchingQuantity: z.ZodOptional<z.ZodObject<{
            totalResearchingQuantity: z.ZodOptional<z.ZodNumber>;
            researchingQuantityBreakdown: z.ZodOptional<z.ZodArray<z.ZodObject<{
                name: z.ZodString;
                quantity: z.ZodNumber;
            }, "strip", z.ZodTypeAny, {
                quantity: number;
                name: string;
            }, {
                quantity: number;
                name: string;
            }>, "many">>;
        }, "strip", z.ZodTypeAny, {
            totalResearchingQuantity?: number | undefined;
            researchingQuantityBreakdown?: {
                quantity: number;
                name: string;
            }[] | undefined;
        }, {
            totalResearchingQuantity?: number | undefined;
            researchingQuantityBreakdown?: {
                quantity: number;
                name: string;
            }[] | undefined;
        }>>;
        unfulfillableQuantity: z.ZodOptional<z.ZodNumber>;
    }, "strip", z.ZodTypeAny, {
        fulfillableQuantity?: number | undefined;
        inboundWorkingQuantity?: number | undefined;
        inboundShippedQuantity?: number | undefined;
        inboundReceivingQuantity?: number | undefined;
        reservedQuantity?: {
            totalReservedQuantity?: number | undefined;
            pendingCustomerOrderQuantity?: number | undefined;
            pendingTransshipmentQuantity?: number | undefined;
            fcProcessingQuantity?: number | undefined;
        } | undefined;
        researchingQuantity?: {
            totalResearchingQuantity?: number | undefined;
            researchingQuantityBreakdown?: {
                quantity: number;
                name: string;
            }[] | undefined;
        } | undefined;
        unfulfillableQuantity?: number | undefined;
    }, {
        fulfillableQuantity?: number | undefined;
        inboundWorkingQuantity?: number | undefined;
        inboundShippedQuantity?: number | undefined;
        inboundReceivingQuantity?: number | undefined;
        reservedQuantity?: {
            totalReservedQuantity?: number | undefined;
            pendingCustomerOrderQuantity?: number | undefined;
            pendingTransshipmentQuantity?: number | undefined;
            fcProcessingQuantity?: number | undefined;
        } | undefined;
        researchingQuantity?: {
            totalResearchingQuantity?: number | undefined;
            researchingQuantityBreakdown?: {
                quantity: number;
                name: string;
            }[] | undefined;
        } | undefined;
        unfulfillableQuantity?: number | undefined;
    }>>;
    lastUpdatedTime: z.ZodOptional<z.ZodString>;
    productName: z.ZodOptional<z.ZodString>;
    totalQuantity: z.ZodOptional<z.ZodNumber>;
}, "strip", z.ZodTypeAny, {
    sellerSku: string;
    asin?: string | undefined;
    fnSku?: string | undefined;
    condition?: "NewItem" | "NewWithWarranty" | "NewOEM" | "NewOpenBox" | "UsedLikeNew" | "UsedVeryGood" | "UsedGood" | "UsedAcceptable" | "UsedPoor" | "UsedRefurbished" | "CollectibleLikeNew" | "CollectibleVeryGood" | "CollectibleGood" | "CollectibleAcceptable" | "CollectiblePoor" | "RefurbishedWithWarranty" | "Refurbished" | "Club" | undefined;
    inventoryDetails?: {
        fulfillableQuantity?: number | undefined;
        inboundWorkingQuantity?: number | undefined;
        inboundShippedQuantity?: number | undefined;
        inboundReceivingQuantity?: number | undefined;
        reservedQuantity?: {
            totalReservedQuantity?: number | undefined;
            pendingCustomerOrderQuantity?: number | undefined;
            pendingTransshipmentQuantity?: number | undefined;
            fcProcessingQuantity?: number | undefined;
        } | undefined;
        researchingQuantity?: {
            totalResearchingQuantity?: number | undefined;
            researchingQuantityBreakdown?: {
                quantity: number;
                name: string;
            }[] | undefined;
        } | undefined;
        unfulfillableQuantity?: number | undefined;
    } | undefined;
    lastUpdatedTime?: string | undefined;
    productName?: string | undefined;
    totalQuantity?: number | undefined;
}, {
    sellerSku: string;
    asin?: string | undefined;
    fnSku?: string | undefined;
    condition?: "NewItem" | "NewWithWarranty" | "NewOEM" | "NewOpenBox" | "UsedLikeNew" | "UsedVeryGood" | "UsedGood" | "UsedAcceptable" | "UsedPoor" | "UsedRefurbished" | "CollectibleLikeNew" | "CollectibleVeryGood" | "CollectibleGood" | "CollectibleAcceptable" | "CollectiblePoor" | "RefurbishedWithWarranty" | "Refurbished" | "Club" | undefined;
    inventoryDetails?: {
        fulfillableQuantity?: number | undefined;
        inboundWorkingQuantity?: number | undefined;
        inboundShippedQuantity?: number | undefined;
        inboundReceivingQuantity?: number | undefined;
        reservedQuantity?: {
            totalReservedQuantity?: number | undefined;
            pendingCustomerOrderQuantity?: number | undefined;
            pendingTransshipmentQuantity?: number | undefined;
            fcProcessingQuantity?: number | undefined;
        } | undefined;
        researchingQuantity?: {
            totalResearchingQuantity?: number | undefined;
            researchingQuantityBreakdown?: {
                quantity: number;
                name: string;
            }[] | undefined;
        } | undefined;
        unfulfillableQuantity?: number | undefined;
    } | undefined;
    lastUpdatedTime?: string | undefined;
    productName?: string | undefined;
    totalQuantity?: number | undefined;
}>;
export declare const GetInventorySummariesResponseSchema: z.ZodObject<{
    granularity: z.ZodObject<{
        granularityType: z.ZodEnum<["Marketplace"]>;
        granularityId: z.ZodString;
    }, "strip", z.ZodTypeAny, {
        granularityType: "Marketplace";
        granularityId: string;
    }, {
        granularityType: "Marketplace";
        granularityId: string;
    }>;
    inventorySummaries: z.ZodArray<z.ZodObject<{
        asin: z.ZodOptional<z.ZodString>;
        fnSku: z.ZodOptional<z.ZodString>;
        sellerSku: z.ZodString;
        condition: z.ZodOptional<z.ZodEnum<["NewItem", "NewWithWarranty", "NewOEM", "NewOpenBox", "UsedLikeNew", "UsedVeryGood", "UsedGood", "UsedAcceptable", "UsedPoor", "UsedRefurbished", "CollectibleLikeNew", "CollectibleVeryGood", "CollectibleGood", "CollectibleAcceptable", "CollectiblePoor", "RefurbishedWithWarranty", "Refurbished", "Club"]>>;
        inventoryDetails: z.ZodOptional<z.ZodObject<{
            fulfillableQuantity: z.ZodOptional<z.ZodNumber>;
            inboundWorkingQuantity: z.ZodOptional<z.ZodNumber>;
            inboundShippedQuantity: z.ZodOptional<z.ZodNumber>;
            inboundReceivingQuantity: z.ZodOptional<z.ZodNumber>;
            reservedQuantity: z.ZodOptional<z.ZodObject<{
                totalReservedQuantity: z.ZodOptional<z.ZodNumber>;
                pendingCustomerOrderQuantity: z.ZodOptional<z.ZodNumber>;
                pendingTransshipmentQuantity: z.ZodOptional<z.ZodNumber>;
                fcProcessingQuantity: z.ZodOptional<z.ZodNumber>;
            }, "strip", z.ZodTypeAny, {
                totalReservedQuantity?: number | undefined;
                pendingCustomerOrderQuantity?: number | undefined;
                pendingTransshipmentQuantity?: number | undefined;
                fcProcessingQuantity?: number | undefined;
            }, {
                totalReservedQuantity?: number | undefined;
                pendingCustomerOrderQuantity?: number | undefined;
                pendingTransshipmentQuantity?: number | undefined;
                fcProcessingQuantity?: number | undefined;
            }>>;
            researchingQuantity: z.ZodOptional<z.ZodObject<{
                totalResearchingQuantity: z.ZodOptional<z.ZodNumber>;
                researchingQuantityBreakdown: z.ZodOptional<z.ZodArray<z.ZodObject<{
                    name: z.ZodString;
                    quantity: z.ZodNumber;
                }, "strip", z.ZodTypeAny, {
                    quantity: number;
                    name: string;
                }, {
                    quantity: number;
                    name: string;
                }>, "many">>;
            }, "strip", z.ZodTypeAny, {
                totalResearchingQuantity?: number | undefined;
                researchingQuantityBreakdown?: {
                    quantity: number;
                    name: string;
                }[] | undefined;
            }, {
                totalResearchingQuantity?: number | undefined;
                researchingQuantityBreakdown?: {
                    quantity: number;
                    name: string;
                }[] | undefined;
            }>>;
            unfulfillableQuantity: z.ZodOptional<z.ZodNumber>;
        }, "strip", z.ZodTypeAny, {
            fulfillableQuantity?: number | undefined;
            inboundWorkingQuantity?: number | undefined;
            inboundShippedQuantity?: number | undefined;
            inboundReceivingQuantity?: number | undefined;
            reservedQuantity?: {
                totalReservedQuantity?: number | undefined;
                pendingCustomerOrderQuantity?: number | undefined;
                pendingTransshipmentQuantity?: number | undefined;
                fcProcessingQuantity?: number | undefined;
            } | undefined;
            researchingQuantity?: {
                totalResearchingQuantity?: number | undefined;
                researchingQuantityBreakdown?: {
                    quantity: number;
                    name: string;
                }[] | undefined;
            } | undefined;
            unfulfillableQuantity?: number | undefined;
        }, {
            fulfillableQuantity?: number | undefined;
            inboundWorkingQuantity?: number | undefined;
            inboundShippedQuantity?: number | undefined;
            inboundReceivingQuantity?: number | undefined;
            reservedQuantity?: {
                totalReservedQuantity?: number | undefined;
                pendingCustomerOrderQuantity?: number | undefined;
                pendingTransshipmentQuantity?: number | undefined;
                fcProcessingQuantity?: number | undefined;
            } | undefined;
            researchingQuantity?: {
                totalResearchingQuantity?: number | undefined;
                researchingQuantityBreakdown?: {
                    quantity: number;
                    name: string;
                }[] | undefined;
            } | undefined;
            unfulfillableQuantity?: number | undefined;
        }>>;
        lastUpdatedTime: z.ZodOptional<z.ZodString>;
        productName: z.ZodOptional<z.ZodString>;
        totalQuantity: z.ZodOptional<z.ZodNumber>;
    }, "strip", z.ZodTypeAny, {
        sellerSku: string;
        asin?: string | undefined;
        fnSku?: string | undefined;
        condition?: "NewItem" | "NewWithWarranty" | "NewOEM" | "NewOpenBox" | "UsedLikeNew" | "UsedVeryGood" | "UsedGood" | "UsedAcceptable" | "UsedPoor" | "UsedRefurbished" | "CollectibleLikeNew" | "CollectibleVeryGood" | "CollectibleGood" | "CollectibleAcceptable" | "CollectiblePoor" | "RefurbishedWithWarranty" | "Refurbished" | "Club" | undefined;
        inventoryDetails?: {
            fulfillableQuantity?: number | undefined;
            inboundWorkingQuantity?: number | undefined;
            inboundShippedQuantity?: number | undefined;
            inboundReceivingQuantity?: number | undefined;
            reservedQuantity?: {
                totalReservedQuantity?: number | undefined;
                pendingCustomerOrderQuantity?: number | undefined;
                pendingTransshipmentQuantity?: number | undefined;
                fcProcessingQuantity?: number | undefined;
            } | undefined;
            researchingQuantity?: {
                totalResearchingQuantity?: number | undefined;
                researchingQuantityBreakdown?: {
                    quantity: number;
                    name: string;
                }[] | undefined;
            } | undefined;
            unfulfillableQuantity?: number | undefined;
        } | undefined;
        lastUpdatedTime?: string | undefined;
        productName?: string | undefined;
        totalQuantity?: number | undefined;
    }, {
        sellerSku: string;
        asin?: string | undefined;
        fnSku?: string | undefined;
        condition?: "NewItem" | "NewWithWarranty" | "NewOEM" | "NewOpenBox" | "UsedLikeNew" | "UsedVeryGood" | "UsedGood" | "UsedAcceptable" | "UsedPoor" | "UsedRefurbished" | "CollectibleLikeNew" | "CollectibleVeryGood" | "CollectibleGood" | "CollectibleAcceptable" | "CollectiblePoor" | "RefurbishedWithWarranty" | "Refurbished" | "Club" | undefined;
        inventoryDetails?: {
            fulfillableQuantity?: number | undefined;
            inboundWorkingQuantity?: number | undefined;
            inboundShippedQuantity?: number | undefined;
            inboundReceivingQuantity?: number | undefined;
            reservedQuantity?: {
                totalReservedQuantity?: number | undefined;
                pendingCustomerOrderQuantity?: number | undefined;
                pendingTransshipmentQuantity?: number | undefined;
                fcProcessingQuantity?: number | undefined;
            } | undefined;
            researchingQuantity?: {
                totalResearchingQuantity?: number | undefined;
                researchingQuantityBreakdown?: {
                    quantity: number;
                    name: string;
                }[] | undefined;
            } | undefined;
            unfulfillableQuantity?: number | undefined;
        } | undefined;
        lastUpdatedTime?: string | undefined;
        productName?: string | undefined;
        totalQuantity?: number | undefined;
    }>, "many">;
    pagination: z.ZodOptional<z.ZodObject<{
        nextToken: z.ZodOptional<z.ZodString>;
    }, "strip", z.ZodTypeAny, {
        nextToken?: string | undefined;
    }, {
        nextToken?: string | undefined;
    }>>;
}, "strip", z.ZodTypeAny, {
    granularity: {
        granularityType: "Marketplace";
        granularityId: string;
    };
    inventorySummaries: {
        sellerSku: string;
        asin?: string | undefined;
        fnSku?: string | undefined;
        condition?: "NewItem" | "NewWithWarranty" | "NewOEM" | "NewOpenBox" | "UsedLikeNew" | "UsedVeryGood" | "UsedGood" | "UsedAcceptable" | "UsedPoor" | "UsedRefurbished" | "CollectibleLikeNew" | "CollectibleVeryGood" | "CollectibleGood" | "CollectibleAcceptable" | "CollectiblePoor" | "RefurbishedWithWarranty" | "Refurbished" | "Club" | undefined;
        inventoryDetails?: {
            fulfillableQuantity?: number | undefined;
            inboundWorkingQuantity?: number | undefined;
            inboundShippedQuantity?: number | undefined;
            inboundReceivingQuantity?: number | undefined;
            reservedQuantity?: {
                totalReservedQuantity?: number | undefined;
                pendingCustomerOrderQuantity?: number | undefined;
                pendingTransshipmentQuantity?: number | undefined;
                fcProcessingQuantity?: number | undefined;
            } | undefined;
            researchingQuantity?: {
                totalResearchingQuantity?: number | undefined;
                researchingQuantityBreakdown?: {
                    quantity: number;
                    name: string;
                }[] | undefined;
            } | undefined;
            unfulfillableQuantity?: number | undefined;
        } | undefined;
        lastUpdatedTime?: string | undefined;
        productName?: string | undefined;
        totalQuantity?: number | undefined;
    }[];
    pagination?: {
        nextToken?: string | undefined;
    } | undefined;
}, {
    granularity: {
        granularityType: "Marketplace";
        granularityId: string;
    };
    inventorySummaries: {
        sellerSku: string;
        asin?: string | undefined;
        fnSku?: string | undefined;
        condition?: "NewItem" | "NewWithWarranty" | "NewOEM" | "NewOpenBox" | "UsedLikeNew" | "UsedVeryGood" | "UsedGood" | "UsedAcceptable" | "UsedPoor" | "UsedRefurbished" | "CollectibleLikeNew" | "CollectibleVeryGood" | "CollectibleGood" | "CollectibleAcceptable" | "CollectiblePoor" | "RefurbishedWithWarranty" | "Refurbished" | "Club" | undefined;
        inventoryDetails?: {
            fulfillableQuantity?: number | undefined;
            inboundWorkingQuantity?: number | undefined;
            inboundShippedQuantity?: number | undefined;
            inboundReceivingQuantity?: number | undefined;
            reservedQuantity?: {
                totalReservedQuantity?: number | undefined;
                pendingCustomerOrderQuantity?: number | undefined;
                pendingTransshipmentQuantity?: number | undefined;
                fcProcessingQuantity?: number | undefined;
            } | undefined;
            researchingQuantity?: {
                totalResearchingQuantity?: number | undefined;
                researchingQuantityBreakdown?: {
                    quantity: number;
                    name: string;
                }[] | undefined;
            } | undefined;
            unfulfillableQuantity?: number | undefined;
        } | undefined;
        lastUpdatedTime?: string | undefined;
        productName?: string | undefined;
        totalQuantity?: number | undefined;
    }[];
    pagination?: {
        nextToken?: string | undefined;
    } | undefined;
}>;
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
    cacheTtlMs?: number;
    lowStockThreshold?: number;
    enableCaching?: boolean;
    batchSize?: number;
    safetyStock?: number;
}
/**
 * Dependencies for InventorySync service
 */
export interface InventorySyncDependencies {
    amazonClient: AmazonMCFClient;
}
/**
 * InventorySync manages inventory synchronization with Amazon FBA
 */
export declare class InventorySync {
    private config;
    private amazonClient;
    private inventoryCache;
    constructor(dependencies: InventorySyncDependencies, config?: InventorySyncConfig);
    /**
     * Check inventory for a single SKU
     */
    checkInventory(sku: string, requestedQuantity: number): Promise<InventoryCheckResult>;
    /**
     * Check inventory for multiple SKUs (with quantities)
     */
    checkInventoryBatch(skuQuantities: Array<{
        sku: string;
        quantity: number;
    }>): Promise<BatchInventoryCheckResult>;
    /**
     * Refresh inventory cache for specific SKUs
     */
    refreshInventory(skus: string[]): Promise<void>;
    /**
     * Clear inventory cache
     */
    clearCache(): void;
    /**
     * Clear expired cache entries
     */
    clearExpiredCache(): void;
    /**
     * Get cached inventory for a SKU (if not expired)
     */
    private getCachedInventory;
    /**
     * Fetch inventory from Amazon FBA API and update cache
     */
    private fetchInventoryFromAmazon;
    /**
     * Update configuration
     */
    updateConfig(config: Partial<InventorySyncConfig>): void;
    /**
     * Get current configuration
     */
    getConfig(): Required<InventorySyncConfig>;
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
    };
    /**
     * Get low stock SKUs from cache
     */
    getLowStockSkus(): Array<{
        sku: string;
        available: number;
        threshold: number;
    }>;
}
/**
 * Create a new inventory sync instance
 */
export declare function createInventorySync(dependencies: InventorySyncDependencies, config?: InventorySyncConfig): InventorySync;
//# sourceMappingURL=inventory-sync.d.ts.map