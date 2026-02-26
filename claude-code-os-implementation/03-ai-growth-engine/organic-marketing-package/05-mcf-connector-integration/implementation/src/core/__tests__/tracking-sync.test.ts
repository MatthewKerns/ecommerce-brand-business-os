/**
 * Tracking Sync Tests
 */

import {
  TrackingSync,
  createTrackingSync,
  type TrackingSyncDependencies,
  type OrderTrackingRecord,
} from '../tracking-sync';
import { ErrorCode, MCFFulfillmentStatus } from '../../types/common';
import type {
  MCFFulfillmentOrder,
  MCFGetFulfillmentOrderResponse,
  MCFShipment,
} from '../../types/mcf-order';

// ============================================================
// Mock Implementations
// ============================================================

const createMockTikTokClient = () => ({
  getOrderDetail: jest.fn(),
  getOrders: jest.fn(),
  updateTrackingInfo: jest.fn(),
  refreshAccessToken: jest.fn(),
  testConnection: jest.fn(),
});

const createMockAmazonClient = () => ({
  createFulfillmentOrder: jest.fn(),
  getFulfillmentOrder: jest.fn(),
  getPackageTracking: jest.fn(),
  refreshAccessToken: jest.fn(),
  testConnection: jest.fn(),
});

// ============================================================
// Test Data Factories
// ============================================================

function createMCFFulfillmentOrderResponse(
  orderId: string,
  status: MCFFulfillmentStatus,
  trackingNumber?: string
): MCFGetFulfillmentOrderResponse {
  const fulfillmentOrder: MCFFulfillmentOrder = {
    sellerFulfillmentOrderId: `TIKTOK-${orderId}`,
    marketplaceId: 'ATVPDKIKX0DER',
    displayableOrderId: orderId,
    displayableOrderDate: new Date().toISOString(),
    displayableOrderComment: 'Test order',
    shippingSpeedCategory: 'Standard',
    deliveryWindow: undefined,
    destinationAddress: {
      name: 'John Doe',
      addressLine1: '123 Main St',
      city: 'San Francisco',
      stateOrRegion: 'CA',
      postalCode: '94105',
      countryCode: 'US',
    },
    fulfillmentAction: 'Ship',
    fulfillmentPolicy: 'FillOrKill',
    fulfillmentOrderStatus: status,
    statusUpdatedDate: status === MCFFulfillmentStatus.COMPLETE ? new Date().toISOString() : undefined,
    receivedDate: new Date().toISOString(),
  };

  const fulfillmentShipments: MCFShipment[] = trackingNumber ? [
    {
      amazonShipmentId: 'SHIP123',
      fulfillmentCenterId: 'PHX3',
      fulfillmentShipmentStatus: 'SHIPPED',
      shippingDate: new Date().toISOString(),
      estimatedArrivalDate: new Date().toISOString(),
      fulfillmentShipmentItem: [
        {
          sellerSku: 'SKU123',
          sellerFulfillmentOrderItemId: 'item-1',
          quantity: 2,
        },
      ],
      fulfillmentShipmentPackage: [
        {
          packageNumber: 1,
          carrierCode: 'UPS',
          trackingNumber: trackingNumber,
        },
      ],
    },
  ] : [];

  return {
    fulfillmentOrder,
    fulfillmentOrderItems: [
      {
        sellerSku: 'SKU123',
        sellerFulfillmentOrderItemId: 'item-1',
        quantity: 2,
      },
    ],
    fulfillmentShipments,
  };
}

// ============================================================
// Tests
// ============================================================

describe('TrackingSync', () => {
  let mockTikTokClient: ReturnType<typeof createMockTikTokClient>;
  let mockAmazonClient: ReturnType<typeof createMockAmazonClient>;
  let dependencies: TrackingSyncDependencies;

  beforeEach(() => {
    mockTikTokClient = createMockTikTokClient();
    mockAmazonClient = createMockAmazonClient();
    dependencies = {
      tiktokClient: mockTikTokClient as any,
      amazonClient: mockAmazonClient as any,
    };
  });

  describe('constructor', () => {
    it('should create tracking sync with default config', () => {
      const trackingSync = new TrackingSync(dependencies);
      const config = trackingSync.getConfig();

      expect(config.maxRetries).toBe(3);
      expect(config.retryDelayMs).toBe(5000);
      expect(config.skipAlreadySynced).toBe(true);
      expect(config.updateTikTok).toBe(true);
    });

    it('should create tracking sync with custom config', () => {
      const trackingSync = new TrackingSync(dependencies, {
        maxRetries: 5,
        retryDelayMs: 10000,
        skipAlreadySynced: false,
        updateTikTok: false,
      });
      const config = trackingSync.getConfig();

      expect(config.maxRetries).toBe(5);
      expect(config.retryDelayMs).toBe(10000);
      expect(config.skipAlreadySynced).toBe(false);
      expect(config.updateTikTok).toBe(false);
    });

    it('should create tracking sync via factory function', () => {
      const trackingSync = createTrackingSync(dependencies);
      expect(trackingSync).toBeInstanceOf(TrackingSync);
    });
  });

  describe('addOrder', () => {
    it('should add order to tracking records', () => {
      const trackingSync = new TrackingSync(dependencies);
      trackingSync.addOrder('ORDER123', 'TIKTOK-ORDER123');

      const record = trackingSync.getTrackingRecord('ORDER123');
      expect(record).toBeDefined();
      expect(record?.tiktokOrderId).toBe('ORDER123');
      expect(record?.mcfFulfillmentOrderId).toBe('TIKTOK-ORDER123');
      expect(record?.synced).toBe(false);
      expect(record?.syncAttempts).toBe(0);
    });

    it('should not duplicate order if already exists', () => {
      const trackingSync = new TrackingSync(dependencies);
      trackingSync.addOrder('ORDER123', 'TIKTOK-ORDER123');
      trackingSync.addOrder('ORDER123', 'TIKTOK-ORDER123-DIFFERENT');

      const records = trackingSync.getAllTrackingRecords();
      expect(records.length).toBe(1);
      expect(records[0].mcfFulfillmentOrderId).toBe('TIKTOK-ORDER123');
    });
  });

  describe('removeOrder', () => {
    it('should remove order from tracking records', () => {
      const trackingSync = new TrackingSync(dependencies);
      trackingSync.addOrder('ORDER123', 'TIKTOK-ORDER123');
      trackingSync.removeOrder('ORDER123');

      const record = trackingSync.getTrackingRecord('ORDER123');
      expect(record).toBeUndefined();
    });
  });

  describe('getTrackingRecord', () => {
    it('should return tracking record for order', () => {
      const trackingSync = new TrackingSync(dependencies);
      trackingSync.addOrder('ORDER123', 'TIKTOK-ORDER123');

      const record = trackingSync.getTrackingRecord('ORDER123');
      expect(record).toBeDefined();
      expect(record?.tiktokOrderId).toBe('ORDER123');
    });

    it('should return undefined for non-existent order', () => {
      const trackingSync = new TrackingSync(dependencies);
      const record = trackingSync.getTrackingRecord('NONEXISTENT');
      expect(record).toBeUndefined();
    });
  });

  describe('getAllTrackingRecords', () => {
    it('should return all tracking records', () => {
      const trackingSync = new TrackingSync(dependencies);
      trackingSync.addOrder('ORDER1', 'TIKTOK-ORDER1');
      trackingSync.addOrder('ORDER2', 'TIKTOK-ORDER2');
      trackingSync.addOrder('ORDER3', 'TIKTOK-ORDER3');

      const records = trackingSync.getAllTrackingRecords();
      expect(records.length).toBe(3);
    });

    it('should return empty array when no records', () => {
      const trackingSync = new TrackingSync(dependencies);
      const records = trackingSync.getAllTrackingRecords();
      expect(records).toEqual([]);
    });
  });

  describe('getUnsyncedRecords', () => {
    it('should return only unsynced records', () => {
      const trackingSync = new TrackingSync(dependencies);
      trackingSync.addOrder('ORDER1', 'TIKTOK-ORDER1');
      trackingSync.addOrder('ORDER2', 'TIKTOK-ORDER2');
      trackingSync.addOrder('ORDER3', 'TIKTOK-ORDER3');

      const record1 = trackingSync.getTrackingRecord('ORDER1');
      if (record1) record1.synced = true;

      const unsyncedRecords = trackingSync.getUnsyncedRecords();
      expect(unsyncedRecords.length).toBe(2);
      expect(unsyncedRecords.find(r => r.tiktokOrderId === 'ORDER1')).toBeUndefined();
    });
  });

  describe('syncOrder', () => {
    it('should successfully sync tracking for completed order', async () => {
      const trackingSync = new TrackingSync(dependencies);
      trackingSync.addOrder('ORDER123', 'TIKTOK-ORDER123');

      const orderResponse = createMCFFulfillmentOrderResponse('ORDER123', MCFFulfillmentStatus.COMPLETE, 'TRACK123');
      mockAmazonClient.getFulfillmentOrder.mockResolvedValue(orderResponse);
      mockTikTokClient.getOrderDetail.mockResolvedValue({
        id: 'ORDER123',
        packages: [{ id: 'PKG123' }],
      } as any);
      mockTikTokClient.updateTrackingInfo.mockResolvedValue({
        order_id: 'ORDER123',
        updated: true,
      });

      const result = await trackingSync.syncOrder('ORDER123');

      expect(result.success).toBe(true);
      expect(result.orderId).toBe('ORDER123');
      expect(result.trackingNumber).toBe('TRACK123');
      expect(result.carrier).toBe('UPS');
      expect(mockAmazonClient.getFulfillmentOrder).toHaveBeenCalledWith({
        sellerFulfillmentOrderId: 'TIKTOK-ORDER123',
      });
      expect(mockTikTokClient.updateTrackingInfo).toHaveBeenCalledWith('PKG123', {
        order_id: 'ORDER123',
        tracking_number: 'TRACK123',
        shipping_provider_name: 'UPS',
      });

      const record = trackingSync.getTrackingRecord('ORDER123');
      expect(record?.synced).toBe(true);
      expect(record?.syncedAt).toBeDefined();
      expect(record?.syncAttempts).toBe(1);
    });

    it('should return error when order not in tracking records', async () => {
      const trackingSync = new TrackingSync(dependencies);

      const result = await trackingSync.syncOrder('NONEXISTENT');

      expect(result.success).toBe(false);
      expect(result.error?.code).toBe(ErrorCode.INVALID_ORDER_DATA);
      expect(result.error?.message).toContain('not found in tracking records');
    });

    it('should skip already synced order when skipAlreadySynced is true', async () => {
      const trackingSync = new TrackingSync(dependencies, {
        skipAlreadySynced: true,
      });
      trackingSync.addOrder('ORDER123', 'TIKTOK-ORDER123');

      const record = trackingSync.getTrackingRecord('ORDER123');
      if (record) {
        record.synced = true;
        record.syncedAt = new Date();
      }

      const result = await trackingSync.syncOrder('ORDER123');

      expect(result.success).toBe(true);
      expect(mockAmazonClient.getFulfillmentOrder).not.toHaveBeenCalled();
      expect(mockTikTokClient.updateTrackingInfo).not.toHaveBeenCalled();
    });

    it('should re-sync already synced order when skipAlreadySynced is false', async () => {
      const trackingSync = new TrackingSync(dependencies, {
        skipAlreadySynced: false,
      });
      trackingSync.addOrder('ORDER123', 'TIKTOK-ORDER123');

      const record = trackingSync.getTrackingRecord('ORDER123');
      if (record) {
        record.synced = true;
        record.syncedAt = new Date();
      }

      const orderResponse = createMCFFulfillmentOrderResponse('ORDER123', MCFFulfillmentStatus.COMPLETE, 'TRACK123');
      mockAmazonClient.getFulfillmentOrder.mockResolvedValue(orderResponse);
      mockTikTokClient.updateTrackingInfo.mockResolvedValue({
        order_id: 'ORDER123',
        updated: true,
      });

      const result = await trackingSync.syncOrder('ORDER123');

      expect(result.success).toBe(true);
      expect(mockAmazonClient.getFulfillmentOrder).toHaveBeenCalled();
    });

    it('should return error when max retries exceeded', async () => {
      const trackingSync = new TrackingSync(dependencies, {
        maxRetries: 3,
      });
      trackingSync.addOrder('ORDER123', 'TIKTOK-ORDER123');

      const record = trackingSync.getTrackingRecord('ORDER123');
      if (record) {
        record.syncAttempts = 3;
      }

      const result = await trackingSync.syncOrder('ORDER123');

      expect(result.success).toBe(false);
      expect(result.error?.code).toBe(ErrorCode.TRACKING_SYNC_FAILED);
      expect(result.error?.message).toContain('Max retry attempts');
      expect(mockAmazonClient.getFulfillmentOrder).not.toHaveBeenCalled();
    });

    it('should handle MCF API error when fetching order', async () => {
      const trackingSync = new TrackingSync(dependencies);
      trackingSync.addOrder('ORDER123', 'TIKTOK-ORDER123');

      mockAmazonClient.getFulfillmentOrder.mockRejectedValue(
        new Error('MCF API unavailable')
      );

      const result = await trackingSync.syncOrder('ORDER123');

      expect(result.success).toBe(false);
      expect(result.error?.code).toBe(ErrorCode.AMAZON_API_ERROR);
      expect(result.error?.message).toContain('Failed to fetch MCF order');

      const record = trackingSync.getTrackingRecord('ORDER123');
      expect(record?.error).toBeDefined();
      expect(record?.syncAttempts).toBe(1);
    });

    it('should return error when order not yet shipped', async () => {
      const trackingSync = new TrackingSync(dependencies);
      trackingSync.addOrder('ORDER123', 'TIKTOK-ORDER123');

      const orderResponse = createMCFFulfillmentOrderResponse('ORDER123', MCFFulfillmentStatus.PROCESSING);
      mockAmazonClient.getFulfillmentOrder.mockResolvedValue(orderResponse);

      const result = await trackingSync.syncOrder('ORDER123');

      expect(result.success).toBe(false);
      expect(result.error?.code).toBe(ErrorCode.TRACKING_SYNC_FAILED);
      expect(result.error?.message).toContain('Order not yet shipped');
      expect(mockTikTokClient.updateTrackingInfo).not.toHaveBeenCalled();
    });

    it('should return error when no tracking information available', async () => {
      const trackingSync = new TrackingSync(dependencies);
      trackingSync.addOrder('ORDER123', 'TIKTOK-ORDER123');

      const orderResponse = createMCFFulfillmentOrderResponse('ORDER123', MCFFulfillmentStatus.COMPLETE);
      mockAmazonClient.getFulfillmentOrder.mockResolvedValue(orderResponse);

      const result = await trackingSync.syncOrder('ORDER123');

      expect(result.success).toBe(false);
      expect(result.error?.code).toBe(ErrorCode.TRACKING_SYNC_FAILED);
      expect(result.error?.message).toContain('No tracking information available');
      expect(mockTikTokClient.updateTrackingInfo).not.toHaveBeenCalled();
    });

    it('should handle TikTok API error when updating tracking', async () => {
      const trackingSync = new TrackingSync(dependencies);
      trackingSync.addOrder('ORDER123', 'TIKTOK-ORDER123');

      const orderResponse = createMCFFulfillmentOrderResponse('ORDER123', MCFFulfillmentStatus.COMPLETE, 'TRACK123');
      mockAmazonClient.getFulfillmentOrder.mockResolvedValue(orderResponse);
      mockTikTokClient.updateTrackingInfo.mockRejectedValue(
        new Error('TikTok API rate limit')
      );

      const result = await trackingSync.syncOrder('ORDER123');

      expect(result.success).toBe(false);
      expect(result.error?.code).toBe(ErrorCode.TIKTOK_API_ERROR);
      expect(result.error?.message).toContain('Failed to update TikTok tracking');
      expect(result.trackingNumber).toBe('TRACK123');

      const record = trackingSync.getTrackingRecord('ORDER123');
      expect(record?.synced).toBe(false);
      expect(record?.error).toBeDefined();
    });

    it('should not update TikTok when updateTikTok is false', async () => {
      const trackingSync = new TrackingSync(dependencies, {
        updateTikTok: false,
      });
      trackingSync.addOrder('ORDER123', 'TIKTOK-ORDER123');

      const orderResponse = createMCFFulfillmentOrderResponse('ORDER123', MCFFulfillmentStatus.COMPLETE, 'TRACK123');
      mockAmazonClient.getFulfillmentOrder.mockResolvedValue(orderResponse);

      const result = await trackingSync.syncOrder('ORDER123');

      expect(result.success).toBe(true);
      expect(result.trackingNumber).toBe('TRACK123');
      expect(mockTikTokClient.updateTrackingInfo).not.toHaveBeenCalled();

      const record = trackingSync.getTrackingRecord('ORDER123');
      expect(record?.synced).toBe(true);
    });

    it('should handle unexpected errors', async () => {
      const trackingSync = new TrackingSync(dependencies);
      trackingSync.addOrder('ORDER123', 'TIKTOK-ORDER123');

      // Create a special mock that throws a non-Error object (to test the outer catch)
      mockAmazonClient.getFulfillmentOrder.mockRejectedValue('Non-error object');

      const result = await trackingSync.syncOrder('ORDER123');

      expect(result.success).toBe(false);
      expect(result.error?.code).toBe(ErrorCode.AMAZON_API_ERROR);
      expect(result.error?.message).toContain('Failed to fetch MCF order');
    });
  });

  describe('syncOrders', () => {
    it('should sync multiple orders successfully', async () => {
      const trackingSync = new TrackingSync(dependencies, {
        retryDelayMs: 0,
      });
      trackingSync.addOrder('ORDER1', 'TIKTOK-ORDER1');
      trackingSync.addOrder('ORDER2', 'TIKTOK-ORDER2');
      trackingSync.addOrder('ORDER3', 'TIKTOK-ORDER3');

      mockAmazonClient.getFulfillmentOrder.mockImplementation(async (params) => {
        const extractedOrderId = params.sellerFulfillmentOrderId.replace('TIKTOK-', '');
        return createMCFFulfillmentOrderResponse(
          extractedOrderId,
          MCFFulfillmentStatus.COMPLETE,
          `TRACK-${extractedOrderId}`
        );
      });
      mockTikTokClient.getOrderDetail.mockImplementation(async (orderId) => ({
        id: orderId,
        packages: [{ id: `PKG-${orderId}` }],
      } as any));
      mockTikTokClient.updateTrackingInfo.mockResolvedValue({
        updated: true,
      });

      const result = await trackingSync.syncOrders(['ORDER1', 'ORDER2', 'ORDER3']);

      expect(result.totalOrders).toBe(3);
      expect(result.successCount).toBe(3);
      expect(result.failureCount).toBe(0);
      expect(result.results.length).toBe(3);
      expect(result.errors.length).toBe(0);
    });

    it('should handle partial failures in batch sync', async () => {
      const trackingSync = new TrackingSync(dependencies, {
        retryDelayMs: 0,
      });
      trackingSync.addOrder('ORDER1', 'TIKTOK-ORDER1');
      trackingSync.addOrder('ORDER2', 'TIKTOK-ORDER2');
      trackingSync.addOrder('ORDER3', 'TIKTOK-ORDER3');

      mockAmazonClient.getFulfillmentOrder.mockImplementation(async (params) => {
        if (params.sellerFulfillmentOrderId === 'TIKTOK-ORDER2') {
          throw new Error('MCF API error');
        }
        const extractedOrderId = params.sellerFulfillmentOrderId.replace('TIKTOK-', '');
        return createMCFFulfillmentOrderResponse(
          extractedOrderId,
          MCFFulfillmentStatus.COMPLETE,
          `TRACK-${extractedOrderId}`
        );
      });
      mockTikTokClient.getOrderDetail.mockImplementation(async (orderId) => ({
        id: orderId,
        packages: [{ id: `PKG-${orderId}` }],
      } as any));
      mockTikTokClient.updateTrackingInfo.mockResolvedValue({
        updated: true,
      });

      const result = await trackingSync.syncOrders(['ORDER1', 'ORDER2', 'ORDER3']);

      expect(result.totalOrders).toBe(3);
      expect(result.successCount).toBe(2);
      expect(result.failureCount).toBe(1);
      expect(result.errors.length).toBe(1);
      expect(result.errors[0].orderId).toBe('ORDER2');
    });

    it('should count skipped orders correctly', async () => {
      const trackingSync = new TrackingSync(dependencies, {
        skipAlreadySynced: true,
        retryDelayMs: 0,
      });
      trackingSync.addOrder('ORDER1', 'TIKTOK-ORDER1');
      trackingSync.addOrder('ORDER2', 'TIKTOK-ORDER2');

      const record1 = trackingSync.getTrackingRecord('ORDER1');
      if (record1) {
        record1.synced = true;
      }

      mockAmazonClient.getFulfillmentOrder.mockResolvedValue(
        createMCFFulfillmentOrderResponse('ORDER2', MCFFulfillmentStatus.COMPLETE, 'TRACK2')
      );
      mockTikTokClient.getOrderDetail.mockResolvedValue({
        id: 'ORDER2',
        packages: [{ id: 'PKG-ORDER2' }],
      } as any);
      mockTikTokClient.updateTrackingInfo.mockResolvedValue({
        updated: true,
      });

      const result = await trackingSync.syncOrders(['ORDER1', 'ORDER2']);

      expect(result.totalOrders).toBe(2);
      expect(result.successCount).toBe(2);
      expect(result.skippedCount).toBe(1);
    });
  });

  describe('syncAllUnsynced', () => {
    it('should sync all unsynced orders', async () => {
      const trackingSync = new TrackingSync(dependencies, {
        retryDelayMs: 0,
      });
      trackingSync.addOrder('ORDER1', 'TIKTOK-ORDER1');
      trackingSync.addOrder('ORDER2', 'TIKTOK-ORDER2');
      trackingSync.addOrder('ORDER3', 'TIKTOK-ORDER3');

      const record1 = trackingSync.getTrackingRecord('ORDER1');
      if (record1) {
        record1.synced = true;
      }

      mockAmazonClient.getFulfillmentOrder.mockImplementation(async (params) => {
        const extractedOrderId = params.sellerFulfillmentOrderId.replace('TIKTOK-', '');
        return createMCFFulfillmentOrderResponse(
          extractedOrderId,
          MCFFulfillmentStatus.COMPLETE,
          `TRACK-${extractedOrderId}`
        );
      });
      mockTikTokClient.getOrderDetail.mockImplementation(async (orderId) => ({
        id: orderId,
        packages: [{ id: `PKG-${orderId}` }],
      } as any));
      mockTikTokClient.updateTrackingInfo.mockResolvedValue({
        updated: true,
      });

      const result = await trackingSync.syncAllUnsynced();

      expect(result.totalOrders).toBe(2);
      expect(result.successCount).toBe(2);
      expect(mockAmazonClient.getFulfillmentOrder).toHaveBeenCalledTimes(2);
    });

    it('should return empty result when no unsynced orders', async () => {
      const trackingSync = new TrackingSync(dependencies);

      const result = await trackingSync.syncAllUnsynced();

      expect(result.totalOrders).toBe(0);
      expect(result.successCount).toBe(0);
      expect(result.failureCount).toBe(0);
      expect(result.results.length).toBe(0);
    });
  });

  describe('updateConfig', () => {
    it('should update configuration', () => {
      const trackingSync = new TrackingSync(dependencies);
      trackingSync.updateConfig({
        maxRetries: 10,
        skipAlreadySynced: false,
      });

      const config = trackingSync.getConfig();
      expect(config.maxRetries).toBe(10);
      expect(config.skipAlreadySynced).toBe(false);
      expect(config.retryDelayMs).toBe(5000);
    });
  });

  describe('clearRecords', () => {
    it('should clear all tracking records', () => {
      const trackingSync = new TrackingSync(dependencies);
      trackingSync.addOrder('ORDER1', 'TIKTOK-ORDER1');
      trackingSync.addOrder('ORDER2', 'TIKTOK-ORDER2');

      trackingSync.clearRecords();

      const records = trackingSync.getAllTrackingRecords();
      expect(records.length).toBe(0);
    });
  });

  describe('getStats', () => {
    it('should return correct statistics', () => {
      const trackingSync = new TrackingSync(dependencies);
      trackingSync.addOrder('ORDER1', 'TIKTOK-ORDER1');
      trackingSync.addOrder('ORDER2', 'TIKTOK-ORDER2');
      trackingSync.addOrder('ORDER3', 'TIKTOK-ORDER3');
      trackingSync.addOrder('ORDER4', 'TIKTOK-ORDER4');

      const record1 = trackingSync.getTrackingRecord('ORDER1');
      if (record1) {
        record1.synced = true;
      }

      const record2 = trackingSync.getTrackingRecord('ORDER2');
      if (record2) {
        record2.synced = true;
      }

      const record3 = trackingSync.getTrackingRecord('ORDER3');
      if (record3) {
        record3.error = {
          orderId: 'ORDER3',
          mcfFulfillmentOrderId: 'TIKTOK-ORDER3',
          code: ErrorCode.TRACKING_SYNC_FAILED,
          message: 'Sync failed',
          timestamp: new Date(),
        };
      }

      const stats = trackingSync.getStats();

      expect(stats.total).toBe(4);
      expect(stats.synced).toBe(2);
      expect(stats.unsynced).toBe(2);
      expect(stats.failed).toBe(1);
    });

    it('should return zeros when no records', () => {
      const trackingSync = new TrackingSync(dependencies);
      const stats = trackingSync.getStats();

      expect(stats.total).toBe(0);
      expect(stats.synced).toBe(0);
      expect(stats.unsynced).toBe(0);
      expect(stats.failed).toBe(0);
    });
  });
});
