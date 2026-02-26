/**
 * Inventory Sync Tests
 */

import {
  InventorySync,
  createInventorySync,
  type InventorySyncDependencies,
  type GetInventorySummariesResponse,
  type InventorySummary,
} from '../inventory-sync';
import { ErrorCode } from '../../types/common';

// ============================================================
// Mock Implementations
// ============================================================

const createMockAmazonClient = () => ({
  createFulfillmentOrder: jest.fn(),
  getFulfillmentOrder: jest.fn(),
  getPackageTracking: jest.fn(),
  refreshAccessToken: jest.fn(),
  testConnection: jest.fn(),
  getInventorySummaries: jest.fn(),
});

// ============================================================
// Test Data Factories
// ============================================================

function createInventorySummary(
  sku: string,
  fulfillableQuantity: number,
  options?: {
    reserved?: number;
    inbound?: number;
    unfulfillable?: number;
  }
): InventorySummary {
  return {
    sellerSku: sku,
    asin: `ASIN-${sku}`,
    fnSku: `FN-${sku}`,
    condition: 'NewItem',
    inventoryDetails: {
      fulfillableQuantity,
      inboundWorkingQuantity: options?.inbound ?? 0,
      inboundShippedQuantity: 0,
      inboundReceivingQuantity: 0,
      reservedQuantity: {
        totalReservedQuantity: options?.reserved ?? 0,
        pendingCustomerOrderQuantity: options?.reserved ?? 0,
        pendingTransshipmentQuantity: 0,
        fcProcessingQuantity: 0,
      },
      researchingQuantity: {
        totalResearchingQuantity: 0,
      },
      unfulfillableQuantity: options?.unfulfillable ?? 0,
    },
    lastUpdatedTime: new Date().toISOString(),
    productName: `Product ${sku}`,
    totalQuantity: fulfillableQuantity + (options?.reserved ?? 0) + (options?.unfulfillable ?? 0),
  };
}

function createInventorySummariesResponse(
  summaries: InventorySummary[]
): GetInventorySummariesResponse {
  return {
    granularity: {
      granularityType: 'Marketplace',
      granularityId: 'ATVPDKIKX0DER',
    },
    inventorySummaries: summaries,
    pagination: {},
  };
}

// ============================================================
// Tests
// ============================================================

describe('InventorySync', () => {
  let mockAmazonClient: ReturnType<typeof createMockAmazonClient>;
  let dependencies: InventorySyncDependencies;

  beforeEach(() => {
    mockAmazonClient = createMockAmazonClient();
    dependencies = {
      amazonClient: mockAmazonClient as any,
    };
    jest.clearAllMocks();
  });

  describe('Constructor and Configuration', () => {
    it('should create instance with default config', () => {
      const service = new InventorySync(dependencies);
      const config = service.getConfig();

      expect(config.cacheTtlMs).toBe(5 * 60 * 1000); // 5 minutes
      expect(config.lowStockThreshold).toBe(10);
      expect(config.enableCaching).toBe(true);
      expect(config.batchSize).toBe(50);
      expect(config.safetyStock).toBe(0);
    });

    it('should create instance with custom config', () => {
      const service = new InventorySync(dependencies, {
        cacheTtlMs: 10 * 60 * 1000,
        lowStockThreshold: 20,
        enableCaching: false,
        batchSize: 25,
        safetyStock: 5,
      });
      const config = service.getConfig();

      expect(config.cacheTtlMs).toBe(10 * 60 * 1000);
      expect(config.lowStockThreshold).toBe(20);
      expect(config.enableCaching).toBe(false);
      expect(config.batchSize).toBe(25);
      expect(config.safetyStock).toBe(5);
    });

    it('should create instance using factory function', () => {
      const service = createInventorySync(dependencies);
      expect(service).toBeInstanceOf(InventorySync);
    });
  });

  describe('checkInventory', () => {
    it('should check inventory for single SKU with sufficient stock', async () => {
      const service = new InventorySync(dependencies, { enableCaching: false });

      mockAmazonClient.getInventorySummaries.mockResolvedValue(
        createInventorySummariesResponse([
          createInventorySummary('SKU123', 100),
        ])
      );

      const result = await service.checkInventory('SKU123', 10);

      expect(result.sku).toBe('SKU123');
      expect(result.available).toBe(100);
      expect(result.requested).toBe(10);
      expect(result.sufficient).toBe(true);
      expect(result.lowStock).toBe(false);
      expect(result.cached).toBe(false);
      expect(result.error).toBeUndefined();
      expect(mockAmazonClient.getInventorySummaries).toHaveBeenCalledWith({
        sellerSkus: ['SKU123'],
      });
    });

    it('should check inventory for single SKU with insufficient stock', async () => {
      const service = new InventorySync(dependencies, { enableCaching: false });

      mockAmazonClient.getInventorySummaries.mockResolvedValue(
        createInventorySummariesResponse([
          createInventorySummary('SKU123', 5),
        ])
      );

      const result = await service.checkInventory('SKU123', 10);

      expect(result.sku).toBe('SKU123');
      expect(result.available).toBe(5);
      expect(result.requested).toBe(10);
      expect(result.sufficient).toBe(false);
      expect(result.lowStock).toBe(true);
      expect(result.cached).toBe(false);
    });

    it('should apply safety stock when checking availability', async () => {
      const service = new InventorySync(dependencies, {
        enableCaching: false,
        safetyStock: 5,
      });

      mockAmazonClient.getInventorySummaries.mockResolvedValue(
        createInventorySummariesResponse([
          createInventorySummary('SKU123', 20),
        ])
      );

      const result = await service.checkInventory('SKU123', 10);

      expect(result.available).toBe(15); // 20 - 5 safety stock
      expect(result.requested).toBe(10);
      expect(result.sufficient).toBe(true);
    });

    it('should identify low stock based on threshold', async () => {
      const service = new InventorySync(dependencies, {
        enableCaching: false,
        lowStockThreshold: 20,
      });

      mockAmazonClient.getInventorySummaries.mockResolvedValue(
        createInventorySummariesResponse([
          createInventorySummary('SKU123', 15),
        ])
      );

      const result = await service.checkInventory('SKU123', 5);

      expect(result.sufficient).toBe(true);
      expect(result.lowStock).toBe(true); // 15 <= 20 threshold
    });

    it('should handle SKU not found in inventory', async () => {
      const service = new InventorySync(dependencies, { enableCaching: false });

      mockAmazonClient.getInventorySummaries.mockResolvedValue(
        createInventorySummariesResponse([])
      );

      const result = await service.checkInventory('SKU-NOT-FOUND', 10);

      expect(result.sku).toBe('SKU-NOT-FOUND');
      expect(result.available).toBe(0);
      expect(result.sufficient).toBe(false);
      expect(result.lowStock).toBe(true);
      expect(result.error).toBeDefined();
      expect(result.error?.code).toBe(ErrorCode.INVENTORY_CHECK_FAILED);
      expect(result.error?.message).toContain('not found in Amazon FBA inventory');
    });

    it('should handle API errors gracefully', async () => {
      const service = new InventorySync(dependencies, { enableCaching: false });

      mockAmazonClient.getInventorySummaries.mockRejectedValue(
        new Error('API Error')
      );

      const result = await service.checkInventory('SKU123', 10);

      expect(result.sku).toBe('SKU123');
      expect(result.available).toBe(0);
      expect(result.sufficient).toBe(false);
      expect(result.error).toBeDefined();
      expect(result.error?.code).toBe(ErrorCode.INVENTORY_CHECK_FAILED);
      expect(result.error?.message).toContain('Failed to check inventory');
    });

    it('should use cached data when available', async () => {
      const service = new InventorySync(dependencies, {
        enableCaching: true,
        cacheTtlMs: 10 * 60 * 1000, // 10 minutes
      });

      // First call - cache miss
      mockAmazonClient.getInventorySummaries.mockResolvedValue(
        createInventorySummariesResponse([
          createInventorySummary('SKU123', 100),
        ])
      );

      const result1 = await service.checkInventory('SKU123', 10);
      expect(result1.cached).toBe(false);
      expect(mockAmazonClient.getInventorySummaries).toHaveBeenCalledTimes(1);

      // Second call - cache hit
      const result2 = await service.checkInventory('SKU123', 10);
      expect(result2.cached).toBe(true);
      expect(result2.available).toBe(100);
      expect(result2.sufficient).toBe(true);
      expect(mockAmazonClient.getInventorySummaries).toHaveBeenCalledTimes(1); // No additional API call
    });

    it('should not cache when caching is disabled', async () => {
      const service = new InventorySync(dependencies, { enableCaching: false });

      mockAmazonClient.getInventorySummaries.mockResolvedValue(
        createInventorySummariesResponse([
          createInventorySummary('SKU123', 100),
        ])
      );

      await service.checkInventory('SKU123', 10);
      await service.checkInventory('SKU123', 10);

      expect(mockAmazonClient.getInventorySummaries).toHaveBeenCalledTimes(2);
    });
  });

  describe('checkInventoryBatch', () => {
    it('should check inventory for multiple SKUs', async () => {
      const service = new InventorySync(dependencies, { enableCaching: false });

      mockAmazonClient.getInventorySummaries.mockResolvedValue(
        createInventorySummariesResponse([
          createInventorySummary('SKU1', 100),
          createInventorySummary('SKU2', 50),
          createInventorySummary('SKU3', 5),
        ])
      );

      const result = await service.checkInventoryBatch([
        { sku: 'SKU1', quantity: 10 },
        { sku: 'SKU2', quantity: 20 },
        { sku: 'SKU3', quantity: 10 },
      ]);

      expect(result.totalSkus).toBe(3);
      expect(result.sufficientCount).toBe(2); // SKU1 and SKU2
      expect(result.insufficientCount).toBe(1); // SKU3
      expect(result.lowStockCount).toBe(1); // SKU3 (below threshold of 10)
      expect(result.errorCount).toBe(0);
      expect(result.results).toHaveLength(3);
    });

    it('should process batches according to batchSize config', async () => {
      const service = new InventorySync(dependencies, {
        enableCaching: false,
        batchSize: 2,
      });

      mockAmazonClient.getInventorySummaries
        .mockResolvedValueOnce(
          createInventorySummariesResponse([
            createInventorySummary('SKU1', 100),
            createInventorySummary('SKU2', 100),
          ])
        )
        .mockResolvedValueOnce(
          createInventorySummariesResponse([
            createInventorySummary('SKU3', 100),
          ])
        );

      await service.checkInventoryBatch([
        { sku: 'SKU1', quantity: 10 },
        { sku: 'SKU2', quantity: 10 },
        { sku: 'SKU3', quantity: 10 },
      ]);

      expect(mockAmazonClient.getInventorySummaries).toHaveBeenCalledTimes(2);
      expect(mockAmazonClient.getInventorySummaries).toHaveBeenNthCalledWith(1, {
        sellerSkus: ['SKU1', 'SKU2'],
      });
      expect(mockAmazonClient.getInventorySummaries).toHaveBeenNthCalledWith(2, {
        sellerSkus: ['SKU3'],
      });
    });

    it('should use cached data for some SKUs and fetch others', async () => {
      const service = new InventorySync(dependencies, { enableCaching: true });

      // Pre-populate cache with SKU1
      mockAmazonClient.getInventorySummaries.mockResolvedValueOnce(
        createInventorySummariesResponse([
          createInventorySummary('SKU1', 100),
        ])
      );
      await service.checkInventory('SKU1', 10);

      // Now check batch with SKU1 (cached) and SKU2 (not cached)
      mockAmazonClient.getInventorySummaries.mockResolvedValueOnce(
        createInventorySummariesResponse([
          createInventorySummary('SKU2', 50),
        ])
      );

      const result = await service.checkInventoryBatch([
        { sku: 'SKU1', quantity: 10 },
        { sku: 'SKU2', quantity: 20 },
      ]);

      expect(result.totalSkus).toBe(2);
      expect(result.results[0].cached).toBe(true); // SKU1 from cache
      expect(result.results[1].cached).toBe(false); // SKU2 fetched
      expect(mockAmazonClient.getInventorySummaries).toHaveBeenCalledTimes(2); // Once for pre-cache, once for SKU2
    });

    it('should handle missing SKUs in batch response', async () => {
      const service = new InventorySync(dependencies, { enableCaching: false });

      // Only return SKU1, not SKU2
      mockAmazonClient.getInventorySummaries.mockResolvedValue(
        createInventorySummariesResponse([
          createInventorySummary('SKU1', 100),
        ])
      );

      const result = await service.checkInventoryBatch([
        { sku: 'SKU1', quantity: 10 },
        { sku: 'SKU2', quantity: 10 },
      ]);

      expect(result.totalSkus).toBe(2);
      expect(result.sufficientCount).toBe(1);
      expect(result.insufficientCount).toBe(1);
      expect(result.errorCount).toBe(1);
      expect(result.errors).toHaveLength(1);
      expect(result.errors[0].sku).toBe('SKU2');
      expect(result.errors[0].code).toBe(ErrorCode.INVENTORY_CHECK_FAILED);
    });

    it('should handle batch API errors', async () => {
      const service = new InventorySync(dependencies, { enableCaching: false });

      mockAmazonClient.getInventorySummaries.mockRejectedValue(
        new Error('API Error')
      );

      const result = await service.checkInventoryBatch([
        { sku: 'SKU1', quantity: 10 },
        { sku: 'SKU2', quantity: 10 },
      ]);

      expect(result.totalSkus).toBe(2);
      expect(result.sufficientCount).toBe(0);
      expect(result.insufficientCount).toBe(2);
      expect(result.errorCount).toBe(2);
      expect(result.errors).toHaveLength(2);
    });

    it('should return empty result for empty batch', async () => {
      const service = new InventorySync(dependencies);

      const result = await service.checkInventoryBatch([]);

      expect(result.totalSkus).toBe(0);
      expect(result.sufficientCount).toBe(0);
      expect(result.insufficientCount).toBe(0);
      expect(result.lowStockCount).toBe(0);
      expect(result.errorCount).toBe(0);
      expect(result.results).toHaveLength(0);
      expect(mockAmazonClient.getInventorySummaries).not.toHaveBeenCalled();
    });
  });

  describe('Cache Management', () => {
    it('should clear all cache entries', async () => {
      const service = new InventorySync(dependencies, { enableCaching: true });

      mockAmazonClient.getInventorySummaries.mockResolvedValue(
        createInventorySummariesResponse([
          createInventorySummary('SKU123', 100),
        ])
      );

      await service.checkInventory('SKU123', 10);
      let stats = service.getCacheStats();
      expect(stats.size).toBe(1);

      service.clearCache();
      stats = service.getCacheStats();
      expect(stats.size).toBe(0);
    });

    it('should clear expired cache entries only', async () => {
      const service = new InventorySync(dependencies, {
        enableCaching: true,
        cacheTtlMs: 100, // 100ms TTL
      });

      mockAmazonClient.getInventorySummaries.mockResolvedValue(
        createInventorySummariesResponse([
          createInventorySummary('SKU1', 100),
        ])
      );

      await service.checkInventory('SKU1', 10);

      // Wait for cache to expire
      await new Promise(resolve => setTimeout(resolve, 150));

      // Add a new non-expired entry
      mockAmazonClient.getInventorySummaries.mockResolvedValue(
        createInventorySummariesResponse([
          createInventorySummary('SKU2', 100),
        ])
      );
      await service.checkInventory('SKU2', 10);

      service.clearExpiredCache();
      const stats = service.getCacheStats();
      expect(stats.size).toBe(1);
      expect(stats.entries[0].sku).toBe('SKU2');
    });

    it('should refresh inventory for specific SKUs', async () => {
      const service = new InventorySync(dependencies, { enableCaching: true });

      mockAmazonClient.getInventorySummaries.mockResolvedValue(
        createInventorySummariesResponse([
          createInventorySummary('SKU1', 100),
          createInventorySummary('SKU2', 50),
        ])
      );

      await service.refreshInventory(['SKU1', 'SKU2']);

      const stats = service.getCacheStats();
      expect(stats.size).toBe(2);
      expect(mockAmazonClient.getInventorySummaries).toHaveBeenCalledWith({
        sellerSkus: ['SKU1', 'SKU2'],
      });
    });

    it('should get cache statistics', async () => {
      const service = new InventorySync(dependencies, { enableCaching: true });

      mockAmazonClient.getInventorySummaries.mockResolvedValue(
        createInventorySummariesResponse([
          createInventorySummary('SKU123', 100),
        ])
      );

      await service.checkInventory('SKU123', 10);

      const stats = service.getCacheStats();
      expect(stats.size).toBe(1);
      expect(stats.entries).toHaveLength(1);
      expect(stats.entries[0].sku).toBe('SKU123');
      expect(stats.entries[0].available).toBe(100);
      expect(stats.entries[0].lastUpdated).toBeInstanceOf(Date);
      expect(stats.entries[0].expiresAt).toBeInstanceOf(Date);
    });

    it('should identify low stock SKUs from cache', async () => {
      const service = new InventorySync(dependencies, {
        enableCaching: true,
        lowStockThreshold: 20,
      });

      mockAmazonClient.getInventorySummaries.mockResolvedValue(
        createInventorySummariesResponse([
          createInventorySummary('SKU1', 100),
          createInventorySummary('SKU2', 15),
          createInventorySummary('SKU3', 5),
        ])
      );

      await service.checkInventoryBatch([
        { sku: 'SKU1', quantity: 10 },
        { sku: 'SKU2', quantity: 10 },
        { sku: 'SKU3', quantity: 10 },
      ]);

      const lowStockSkus = service.getLowStockSkus();
      expect(lowStockSkus).toHaveLength(2);
      expect(lowStockSkus.map(s => s.sku)).toEqual(['SKU2', 'SKU3']);
      expect(lowStockSkus[0].threshold).toBe(20);
    });
  });

  describe('Configuration Management', () => {
    it('should update configuration', () => {
      const service = new InventorySync(dependencies);

      service.updateConfig({
        lowStockThreshold: 50,
        batchSize: 25,
      });

      const config = service.getConfig();
      expect(config.lowStockThreshold).toBe(50);
      expect(config.batchSize).toBe(25);
      expect(config.cacheTtlMs).toBe(5 * 60 * 1000); // Unchanged
    });

    it('should clear cache when caching is disabled via updateConfig', async () => {
      const service = new InventorySync(dependencies, { enableCaching: true });

      mockAmazonClient.getInventorySummaries.mockResolvedValue(
        createInventorySummariesResponse([
          createInventorySummary('SKU123', 100),
        ])
      );

      await service.checkInventory('SKU123', 10);
      expect(service.getCacheStats().size).toBe(1);

      service.updateConfig({ enableCaching: false });
      expect(service.getCacheStats().size).toBe(0);
    });
  });

  describe('Error Handling', () => {
    it('should throw error if getInventorySummaries method not implemented', async () => {
      const mockAmazonClientWithoutInventory = {
        createFulfillmentOrder: jest.fn(),
        getFulfillmentOrder: jest.fn(),
        getPackageTracking: jest.fn(),
        refreshAccessToken: jest.fn(),
        testConnection: jest.fn(),
        // Missing getInventorySummaries
      };

      const service = new InventorySync({
        amazonClient: mockAmazonClientWithoutInventory as any,
      }, { enableCaching: false });

      const result = await service.checkInventory('SKU123', 10);

      expect(result.error).toBeDefined();
      expect(result.error?.code).toBe(ErrorCode.INVENTORY_CHECK_FAILED);
      expect(result.error?.message).toContain('getInventorySummaries method not implemented');
    });
  });

  describe('Edge Cases', () => {
    it('should handle zero fulfillable quantity', async () => {
      const service = new InventorySync(dependencies, { enableCaching: false });

      mockAmazonClient.getInventorySummaries.mockResolvedValue(
        createInventorySummariesResponse([
          createInventorySummary('SKU123', 0),
        ])
      );

      const result = await service.checkInventory('SKU123', 10);

      expect(result.available).toBe(0);
      expect(result.sufficient).toBe(false);
      expect(result.lowStock).toBe(true);
    });

    it('should handle negative available quantity after safety stock', async () => {
      const service = new InventorySync(dependencies, {
        enableCaching: false,
        safetyStock: 100,
      });

      mockAmazonClient.getInventorySummaries.mockResolvedValue(
        createInventorySummariesResponse([
          createInventorySummary('SKU123', 50),
        ])
      );

      const result = await service.checkInventory('SKU123', 10);

      expect(result.available).toBe(0); // Max(0, 50 - 100) = 0
      expect(result.sufficient).toBe(false);
    });

    it('should handle inventory with reserved and inbound quantities', async () => {
      const service = new InventorySync(dependencies, { enableCaching: true });

      mockAmazonClient.getInventorySummaries.mockResolvedValue(
        createInventorySummariesResponse([
          createInventorySummary('SKU123', 100, {
            reserved: 20,
            inbound: 30,
            unfulfillable: 5,
          }),
        ])
      );

      await service.checkInventory('SKU123', 10);

      const stats = service.getCacheStats();
      expect(stats.entries[0].available).toBe(100); // fulfillableQuantity
      expect(stats.entries[0].reserved).toBe(20);
      expect(stats.entries[0].inbound).toBe(30);
      expect(stats.entries[0].unfulfillable).toBe(5);
    });
  });
});
