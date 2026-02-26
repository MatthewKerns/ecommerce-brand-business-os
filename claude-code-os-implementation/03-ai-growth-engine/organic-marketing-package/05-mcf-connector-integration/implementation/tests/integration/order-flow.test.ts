/**
 * Integration Tests - End-to-End Order Flow
 *
 * Tests the complete order flow from TikTok Shop to Amazon MCF:
 * 1. Fetch TikTok order
 * 2. Validate order data
 * 3. Transform to MCF format
 * 4. Create MCF fulfillment order
 * 5. Sync tracking information back to TikTok
 * 6. Inventory validation
 */

import { MCFConnector, type MCFConnectorOptions } from '../../src/index';
import { TikTokOrderStatus, MCFFulfillmentStatus, ErrorCode } from '../../src/types/common';
import type { TikTokOrder } from '../../src/types/tiktok-order';
import type { MCFFulfillmentOrder, CreateMCFOrderParams } from '../../src/types/mcf-order';
import type { TikTokShopClient } from '../../src/clients/tiktok-shop-client';
import type { AmazonMCFClient } from '../../src/clients/amazon-mcf-client';

// ============================================================
// Mock Data Factories
// ============================================================

function createMockTikTokOrder(orderId: string = 'TT-123456'): TikTokOrder {
  return {
    id: orderId,
    status: TikTokOrderStatus.AWAITING_SHIPMENT,
    create_time: Math.floor(Date.now() / 1000),
    update_time: Math.floor(Date.now() / 1000),
    paid_time: Math.floor(Date.now() / 1000),
    recipient_address: {
      recipient_name: 'John Doe',
      phone_number: '+1-555-0100',
      full_address: '123 Main St, Apt 4B, San Francisco, CA 94102, United States',
      address_line_1: '123 Main St',
      address_line_2: 'Apt 4B',
      address_line_3: '',
      address_line_4: '',
      city: 'San Francisco',
      state: 'California',
      postal_code: '94102',
      region_code: 'CA',
      district_code: '',
      country: 'United States',
      country_code: 'US',
    },
    item_list: [
      {
        id: 'ITEM-001',
        product_id: 'PROD-001',
        product_name: 'Test Product',
        sku_id: 'SKU-001',
        seller_sku: 'TIKTOK-SKU-001',
        quantity: 2,
        sale_price: 29.99,
        original_price: 39.99,
        platform_discount: 5.0,
        seller_discount: 5.0,
        currency: 'USD',
      },
    ],
    payment_info: {
      currency: 'USD',
      sub_total: 59.98,
      shipping_fee: 5.0,
      seller_discount: 10.0,
      platform_discount: 0.0,
      tax: 5.4,
      total_amount: 60.38,
    },
    delivery_option: 'Standard Shipping',
    buyer_message: 'Please leave at front door',
    seller_note: '',
    packages: [],
    buyer_info: {
      id: 'BUYER-001',
      email: 'buyer@example.com',
    },
  };
}

function createMockMCFFulfillmentOrder(orderId: string = 'MCF-123456'): MCFFulfillmentOrder {
  return {
    sellerFulfillmentOrderId: orderId,
    marketplaceId: 'ATVPDKIKX0DER',
    displayableOrderId: orderId,
    displayableOrderDate: new Date().toISOString(),
    displayableOrderComment: 'TikTok Shop Order - Please leave at front door',
    shippingSpeedCategory: 'Standard',
    destinationAddress: {
      name: 'John Doe',
      addressLine1: '123 Main St',
      addressLine2: 'Apt 4B',
      city: 'San Francisco',
      stateOrRegion: 'CA',
      postalCode: '94102',
      countryCode: 'US',
      phone: '+15550100',
    },
    fulfillmentPolicy: 'FillOrKill',
    receivedDate: new Date().toISOString(),
    fulfillmentOrderStatus: MCFFulfillmentStatus.RECEIVED,
    statusUpdatedDate: new Date().toISOString(),
    notificationEmails: [],
  };
}

function createMockMCFShipment() {
  return {
    amazonShipmentId: 'SHIP-001',
    fulfillmentCenterId: 'PHX6',
    fulfillmentShipmentStatus: 'SHIPPED',
    shippingDate: new Date().toISOString(),
    estimatedArrivalDate: new Date(Date.now() + 3 * 24 * 60 * 60 * 1000).toISOString(),
    fulfillmentShipmentPackage: [
      {
        packageNumber: 1,
        carrierCode: 'USPS',
        trackingNumber: '9400111899562941234567',
      },
    ],
  };
}

// ============================================================
// Mock Connector Setup
// ============================================================

function createMockConnector(): {
  connector: MCFConnector;
  mocks: {
    tiktokClient: jest.Mocked<TikTokShopClient>;
    amazonClient: jest.Mocked<AmazonMCFClient>;
  };
} {
  const mockTikTokClient = {
    getOrderDetail: jest.fn(),
    getOrders: jest.fn(),
    updateTrackingInfo: jest.fn(),
    refreshAccessToken: jest.fn(),
    testConnection: jest.fn().mockResolvedValue(true),
  } as unknown as jest.Mocked<TikTokShopClient>;

  const mockAmazonClient = {
    createFulfillmentOrder: jest.fn(),
    getFulfillmentOrder: jest.fn(),
    getPackageTracking: jest.fn(),
    refreshAccessToken: jest.fn(),
    testConnection: jest.fn().mockResolvedValue(true),
  } as unknown as jest.Mocked<AmazonMCFClient>;

  const options: MCFConnectorOptions = {
    config: {
      tiktok: {
        appKey: 'test-app-key',
        appSecret: 'test-app-secret',
        shopId: 'test-shop-id',
        apiBaseUrl: 'https://test-api.tiktok.com',
        accessToken: 'test-access-token',
        refreshToken: 'test-refresh-token',
      },
      amazon: {
        clientId: 'test-client-id',
        clientSecret: 'test-client-secret',
        refreshToken: 'test-refresh-token',
        sellerId: 'test-seller-id',
        marketplaceId: 'ATVPDKIKX0DER',
        region: 'us-east-1',
        apiBaseUrl: 'https://test-api.amazon.com',
        awsAccessKey: 'test-access-key',
        awsSecretKey: 'test-secret-key',
      },
      connector: {
        orderPollingIntervalMinutes: 5,
        trackingSyncIntervalMinutes: 30,
        retry: {
          maxRetries: 3,
          initialDelay: 1000,
          maxDelay: 10000,
          backoffMultiplier: 2,
        },
      },
      database: {
        host: 'localhost',
        port: 5432,
        database: 'test_mcf',
        username: 'test_user',
        password: 'test_pass',
      },
    },
    enableInventorySync: true,
    enableTrackingSyncScheduler: false,
  };

  const connector = new MCFConnector(options);

  // Replace clients with mocks
  (connector as any).tiktok = mockTikTokClient;
  (connector as any).amazon = mockAmazonClient;

  // Re-initialize router with mocked clients
  connector.router = (connector as any).router.constructor.call(
    Object.create((connector as any).router.constructor.prototype),
    {
      tiktokClient: mockTikTokClient,
      amazonClient: mockAmazonClient,
      validator: connector.validator,
      transformer: connector.transformer,
      inventorySync: connector.inventorySync,
    },
    { continueOnError: true, maxConcurrentOrders: 5 }
  );

  // Re-initialize tracking sync with mocked clients
  connector.trackingSync = (connector as any).trackingSync.constructor.call(
    Object.create((connector as any).trackingSync.constructor.prototype),
    {
      tiktokClient: mockTikTokClient,
      amazonClient: mockAmazonClient,
    },
    {
      maxRetries: 3,
      skipAlreadySynced: true,
      updateTikTok: true,
      retryDelayMs: 1000,
      syncIntervalMs: 1800000,
      schedulerEnabled: false,
      rateLimitPerMinute: 10,
    }
  );

  return {
    connector,
    mocks: {
      tiktokClient: mockTikTokClient,
      amazonClient: mockAmazonClient,
    },
  };
}

// ============================================================
// Integration Tests
// ============================================================

describe('Order Flow Integration Tests', () => {
  describe('End-to-End Order Routing', () => {
    it('should successfully route a TikTok order to Amazon MCF', async () => {
      const { connector, mocks } = createMockConnector();
      const mockOrder = createMockTikTokOrder('TT-12345');
      const mockMCFOrder = createMockMCFFulfillmentOrder('TT-12345');

      // Setup mocks
      mocks.tiktokClient.getOrderDetail.mockResolvedValue(mockOrder);
      mocks.amazonClient.createFulfillmentOrder.mockResolvedValue(mockMCFOrder);
      mocks.amazonClient.getFulfillmentOrder.mockResolvedValue(mockMCFOrder);

      // Add SKU mapping
      connector.addSkuMapping('TIKTOK-SKU-001', 'AMAZON-SKU-001');

      // Route the order
      const result = await connector.routeOrder('TT-12345');

      // Assertions
      expect(result.success).toBe(true);
      expect(result.orderId).toBe('TT-12345');
      expect(mocks.tiktokClient.getOrderDetail).toHaveBeenCalledWith('TT-12345');
      expect(mocks.amazonClient.createFulfillmentOrder).toHaveBeenCalled();

      if (result.success) {
        expect(result.mcfOrder).toBeDefined();
        expect(result.mcfOrder?.sellerFulfillmentOrderId).toBe('TT-12345');
      }
    });

    it('should handle validation errors gracefully', async () => {
      const { connector, mocks } = createMockConnector();
      const invalidOrder = createMockTikTokOrder('TT-INVALID');

      // Create invalid order (missing required address fields)
      invalidOrder.recipient_address.recipient_name = '';
      invalidOrder.recipient_address.address_line_1 = '';

      mocks.tiktokClient.getOrderDetail.mockResolvedValue(invalidOrder);

      const result = await connector.routeOrder('TT-INVALID');

      expect(result.success).toBe(false);
      if (!result.success) {
        expect(result.error).toBeDefined();
        expect(result.stage).toBe('validate');
        expect(result.error.code).toBe(ErrorCode.VALIDATION_FAILED);
      }
    });

    it('should handle insufficient inventory', async () => {
      const { connector, mocks } = createMockConnector();
      const mockOrder = createMockTikTokOrder('TT-INVENTORY');

      mocks.tiktokClient.getOrderDetail.mockResolvedValue(mockOrder);

      // Mock insufficient inventory
      if (connector.inventorySync) {
        (connector.inventorySync as any).checkInventoryBatch = jest.fn().mockResolvedValue({
          totalSkus: 1,
          sufficientCount: 0,
          insufficientCount: 1,
          lowStockCount: 0,
          errorCount: 0,
          results: [
            {
              sku: 'TIKTOK-SKU-001',
              available: 1,
              requested: 2,
              sufficient: false,
              lowStock: false,
            },
          ],
          errors: [],
        });
      }

      const result = await connector.routeOrder('TT-INVENTORY');

      expect(result.success).toBe(false);
      if (!result.success) {
        expect(result.error?.code).toBe(ErrorCode.INSUFFICIENT_INVENTORY);
        expect(result.stage).toBe('check_inventory');
      }
    });

    it('should handle API failures with proper error messages', async () => {
      const { connector, mocks } = createMockConnector();

      mocks.tiktokClient.getOrderDetail.mockRejectedValue(
        new Error('TikTok API Error: Rate limit exceeded')
      );

      const result = await connector.routeOrder('TT-ERROR');

      expect(result.success).toBe(false);
      if (!result.success) {
        expect(result.error).toBeDefined();
        expect(result.stage).toBe('fetch');
        expect(result.error.message).toContain('TikTok API Error');
      }
    });

    it('should collect warnings during validation and transformation', async () => {
      const { connector, mocks } = createMockConnector();
      const mockOrder = createMockTikTokOrder('TT-WARNINGS');
      const mockMCFOrder = createMockMCFFulfillmentOrder('TT-WARNINGS');

      // Order with missing seller_sku (should generate warning)
      mockOrder.item_list[0].seller_sku = '';

      mocks.tiktokClient.getOrderDetail.mockResolvedValue(mockOrder);
      mocks.amazonClient.createFulfillmentOrder.mockResolvedValue(mockMCFOrder);
      mocks.amazonClient.getFulfillmentOrder.mockResolvedValue(mockMCFOrder);

      const result = await connector.routeOrder('TT-WARNINGS');

      expect(result.success).toBe(true);
      if (result.success) {
        expect(result.warnings).toBeDefined();
        expect(result.warnings.length).toBeGreaterThan(0);
      }
    });
  });

  describe('Batch Order Routing', () => {
    it('should route multiple orders concurrently', async () => {
      const { connector, mocks } = createMockConnector();
      const orderIds = ['TT-001', 'TT-002', 'TT-003'];

      // Setup mocks for all orders
      orderIds.forEach((orderId) => {
        mocks.tiktokClient.getOrderDetail.mockResolvedValueOnce(createMockTikTokOrder(orderId));
        mocks.amazonClient.createFulfillmentOrder.mockResolvedValueOnce(
          createMockMCFFulfillmentOrder(orderId)
        );
        mocks.amazonClient.getFulfillmentOrder.mockResolvedValueOnce(
          createMockMCFFulfillmentOrder(orderId)
        );
      });

      connector.addSkuMapping('TIKTOK-SKU-001', 'AMAZON-SKU-001');

      const result = await connector.routeOrders(orderIds);

      expect(result.total).toBe(3);
      expect(result.successful).toBe(3);
      expect(result.failed).toBe(0);
      expect(result.results.length).toBe(3);
      expect(result.results.every((r) => r.success)).toBe(true);
    });

    it('should continue processing on individual failures when configured', async () => {
      const { connector, mocks } = createMockConnector();
      const orderIds = ['TT-SUCCESS', 'TT-FAIL', 'TT-SUCCESS-2'];

      // First order succeeds
      mocks.tiktokClient.getOrderDetail.mockResolvedValueOnce(
        createMockTikTokOrder('TT-SUCCESS')
      );
      mocks.amazonClient.createFulfillmentOrder.mockResolvedValueOnce(
        createMockMCFFulfillmentOrder('TT-SUCCESS')
      );
      mocks.amazonClient.getFulfillmentOrder.mockResolvedValueOnce(
        createMockMCFFulfillmentOrder('TT-SUCCESS')
      );

      // Second order fails
      mocks.tiktokClient.getOrderDetail.mockRejectedValueOnce(new Error('API Error'));

      // Third order succeeds
      mocks.tiktokClient.getOrderDetail.mockResolvedValueOnce(
        createMockTikTokOrder('TT-SUCCESS-2')
      );
      mocks.amazonClient.createFulfillmentOrder.mockResolvedValueOnce(
        createMockMCFFulfillmentOrder('TT-SUCCESS-2')
      );
      mocks.amazonClient.getFulfillmentOrder.mockResolvedValueOnce(
        createMockMCFFulfillmentOrder('TT-SUCCESS-2')
      );

      connector.addSkuMapping('TIKTOK-SKU-001', 'AMAZON-SKU-001');

      const result = await connector.routeOrders(orderIds);

      expect(result.total).toBe(3);
      expect(result.successful).toBe(2);
      expect(result.failed).toBe(1);
    });
  });

  describe('Pending Orders Processing', () => {
    it('should fetch and route all pending orders', async () => {
      const { connector, mocks } = createMockConnector();

      const pendingOrders = [
        createMockTikTokOrder('TT-PENDING-1'),
        createMockTikTokOrder('TT-PENDING-2'),
      ];

      mocks.tiktokClient.getOrders.mockResolvedValue({
        orders: pendingOrders,
        total: 2,
        hasMore: false,
      });

      pendingOrders.forEach((order) => {
        mocks.tiktokClient.getOrderDetail.mockResolvedValueOnce(order);
        mocks.amazonClient.createFulfillmentOrder.mockResolvedValueOnce(
          createMockMCFFulfillmentOrder(order.id)
        );
        mocks.amazonClient.getFulfillmentOrder.mockResolvedValueOnce(
          createMockMCFFulfillmentOrder(order.id)
        );
      });

      connector.addSkuMapping('TIKTOK-SKU-001', 'AMAZON-SKU-001');

      const result = await connector.routePendingOrders();

      expect(result.total).toBe(2);
      expect(result.successful).toBe(2);
      expect(mocks.tiktokClient.getOrders).toHaveBeenCalled();
    });

    it('should handle pagination when fetching pending orders', async () => {
      const { connector, mocks } = createMockConnector();

      // First page
      mocks.tiktokClient.getOrders.mockResolvedValueOnce({
        orders: [createMockTikTokOrder('TT-PAGE-1')],
        total: 2,
        hasMore: true,
      });

      // Second page
      mocks.tiktokClient.getOrders.mockResolvedValueOnce({
        orders: [createMockTikTokOrder('TT-PAGE-2')],
        total: 2,
        hasMore: false,
      });

      ['TT-PAGE-1', 'TT-PAGE-2'].forEach((orderId) => {
        mocks.tiktokClient.getOrderDetail.mockResolvedValueOnce(createMockTikTokOrder(orderId));
        mocks.amazonClient.createFulfillmentOrder.mockResolvedValueOnce(
          createMockMCFFulfillmentOrder(orderId)
        );
        mocks.amazonClient.getFulfillmentOrder.mockResolvedValueOnce(
          createMockMCFFulfillmentOrder(orderId)
        );
      });

      connector.addSkuMapping('TIKTOK-SKU-001', 'AMAZON-SKU-001');

      const result = await connector.routePendingOrders();

      expect(result.total).toBe(2);
      expect(mocks.tiktokClient.getOrders).toHaveBeenCalledTimes(2);
    });
  });

  describe('Tracking Sync Integration', () => {
    it('should sync tracking numbers from MCF to TikTok', async () => {
      const { connector, mocks } = createMockConnector();
      const mockMCFOrder = createMockMCFFulfillmentOrder('TT-TRACKING');
      const mockShipment = createMockMCFShipment();

      // Add order to tracking queue
      connector.addOrderToTrackingQueue('TT-TRACKING', 'TT-TRACKING');

      // Mock MCF responses
      mocks.amazonClient.getFulfillmentOrder.mockResolvedValue({
        ...mockMCFOrder,
        fulfillmentOrderStatus: MCFFulfillmentStatus.COMPLETE,
        fulfillmentShipment: [mockShipment],
      });

      mocks.amazonClient.getPackageTracking.mockResolvedValue({
        packageNumber: 1,
        trackingNumber: '9400111899562941234567',
        carrierCode: 'USPS',
        carrierPhoneNumber: '1-800-275-8777',
        carrierURL: 'https://tools.usps.com/go/TrackConfirmAction',
        shipDate: new Date().toISOString(),
        estimatedArrivalDate: new Date(Date.now() + 3 * 24 * 60 * 60 * 1000).toISOString(),
        shipToAddress: mockMCFOrder.destinationAddress,
        currentStatus: 'IN_TRANSIT',
        currentStatusDescription: 'Package is in transit',
        signedForBy: undefined,
        additionalLocationInfo: 'Left at front door',
        trackingEvents: [],
      });

      mocks.tiktokClient.updateTrackingInfo.mockResolvedValue({ success: true });

      const result = await connector.syncTracking('TT-TRACKING');

      expect(result.success).toBe(true);
      if (result.success) {
        expect(result.trackingNumber).toBe('9400111899562941234567');
        expect(result.carrier).toBe('USPS');
        expect(mocks.tiktokClient.updateTrackingInfo).toHaveBeenCalledWith(
          'TT-TRACKING',
          expect.objectContaining({
            trackingNumber: '9400111899562941234567',
            carrier: 'USPS',
          })
        );
      }
    });

    it('should handle tracking sync failures gracefully', async () => {
      const { connector, mocks } = createMockConnector();

      connector.addOrderToTrackingQueue('TT-FAIL', 'MCF-FAIL');

      mocks.amazonClient.getFulfillmentOrder.mockRejectedValue(new Error('MCF API Error'));

      const result = await connector.syncTracking('TT-FAIL');

      expect(result.success).toBe(false);
      if (!result.success) {
        expect(result.error).toBeDefined();
        expect(result.error.message).toContain('MCF API Error');
      }
    });

    it('should skip already synced orders when configured', async () => {
      const { connector, mocks } = createMockConnector();

      // Add and sync order once
      connector.addOrderToTrackingQueue('TT-SYNCED', 'MCF-SYNCED');

      const mockMCFOrder = createMockMCFFulfillmentOrder('TT-SYNCED');
      const mockShipment = createMockMCFShipment();

      mocks.amazonClient.getFulfillmentOrder.mockResolvedValue({
        ...mockMCFOrder,
        fulfillmentOrderStatus: MCFFulfillmentStatus.COMPLETE,
        fulfillmentShipment: [mockShipment],
      });

      mocks.amazonClient.getPackageTracking.mockResolvedValue({
        packageNumber: 1,
        trackingNumber: '9400111899562941234567',
        carrierCode: 'USPS',
        carrierPhoneNumber: '1-800-275-8777',
        carrierURL: 'https://tools.usps.com/go/TrackConfirmAction',
        shipDate: new Date().toISOString(),
        estimatedArrivalDate: new Date(Date.now() + 3 * 24 * 60 * 60 * 1000).toISOString(),
        shipToAddress: mockMCFOrder.destinationAddress,
        currentStatus: 'IN_TRANSIT',
        currentStatusDescription: 'Package is in transit',
        signedForBy: undefined,
        additionalLocationInfo: 'Left at front door',
        trackingEvents: [],
      });

      mocks.tiktokClient.updateTrackingInfo.mockResolvedValue({ success: true });

      // First sync
      const result1 = await connector.syncTracking('TT-SYNCED');
      expect(result1.success).toBe(true);

      // Reset mocks
      mocks.tiktokClient.updateTrackingInfo.mockClear();

      // Second sync attempt - should skip
      const result2 = await connector.syncTracking('TT-SYNCED');
      expect(result2.success).toBe(false);
      if (!result2.success) {
        expect(result2.error.code).toBe(ErrorCode.TRACKING_ALREADY_SYNCED);
      }
    });
  });

  describe('Inventory Validation', () => {
    it('should validate inventory before creating MCF orders', async () => {
      const { connector, mocks } = createMockConnector();
      const mockOrder = createMockTikTokOrder('TT-INV-CHECK');

      mocks.tiktokClient.getOrderDetail.mockResolvedValue(mockOrder);

      // Mock sufficient inventory
      if (connector.inventorySync) {
        (connector.inventorySync as any).checkInventoryBatch = jest.fn().mockResolvedValue({
          totalSkus: 1,
          sufficientCount: 1,
          insufficientCount: 0,
          lowStockCount: 0,
          errorCount: 0,
          results: [
            {
              sku: 'TIKTOK-SKU-001',
              available: 100,
              requested: 2,
              sufficient: true,
              lowStock: false,
            },
          ],
          errors: [],
        });
      }

      mocks.amazonClient.createFulfillmentOrder.mockResolvedValue(
        createMockMCFFulfillmentOrder('TT-INV-CHECK')
      );
      mocks.amazonClient.getFulfillmentOrder.mockResolvedValue(
        createMockMCFFulfillmentOrder('TT-INV-CHECK')
      );

      const result = await connector.routeOrder('TT-INV-CHECK');

      expect(result.success).toBe(true);
      if (connector.inventorySync) {
        expect((connector.inventorySync as any).checkInventoryBatch).toHaveBeenCalled();
      }
    });

    it('should generate warnings for low stock items', async () => {
      const { connector, mocks } = createMockConnector();
      const mockOrder = createMockTikTokOrder('TT-LOW-STOCK');

      mocks.tiktokClient.getOrderDetail.mockResolvedValue(mockOrder);

      // Mock low stock but sufficient
      if (connector.inventorySync) {
        (connector.inventorySync as any).checkInventoryBatch = jest.fn().mockResolvedValue({
          totalSkus: 1,
          sufficientCount: 1,
          insufficientCount: 0,
          lowStockCount: 1,
          errorCount: 0,
          results: [
            {
              sku: 'TIKTOK-SKU-001',
              available: 8,
              requested: 2,
              sufficient: true,
              lowStock: true,
            },
          ],
          errors: [],
        });
      }

      mocks.amazonClient.createFulfillmentOrder.mockResolvedValue(
        createMockMCFFulfillmentOrder('TT-LOW-STOCK')
      );
      mocks.amazonClient.getFulfillmentOrder.mockResolvedValue(
        createMockMCFFulfillmentOrder('TT-LOW-STOCK')
      );

      connector.addSkuMapping('TIKTOK-SKU-001', 'AMAZON-SKU-001');

      const result = await connector.routeOrder('TT-LOW-STOCK');

      expect(result.success).toBe(true);
      if (result.success) {
        expect(result.warnings).toBeDefined();
        const lowStockWarning = result.warnings?.find((w) => w.message.includes('low stock'));
        expect(lowStockWarning).toBeDefined();
      }
    });
  });

  describe('Connection Testing', () => {
    it('should verify connectivity to both TikTok and Amazon APIs', async () => {
      const { connector, mocks } = createMockConnector();

      mocks.tiktokClient.testConnection.mockResolvedValue(true);
      mocks.amazonClient.testConnection.mockResolvedValue(true);

      const result = await connector.testConnections();

      expect(result.tiktok).toBe(true);
      expect(result.amazon).toBe(true);
    });

    it('should handle connection failures', async () => {
      const { connector, mocks } = createMockConnector();

      mocks.tiktokClient.testConnection.mockRejectedValue(new Error('Connection failed'));
      mocks.amazonClient.testConnection.mockResolvedValue(true);

      const result = await connector.testConnections();

      expect(result.tiktok).toBe(false);
      expect(result.amazon).toBe(true);
    });
  });

  describe('SKU Mapping', () => {
    it('should transform orders using SKU mappings', async () => {
      const { connector, mocks } = createMockConnector();
      const mockOrder = createMockTikTokOrder('TT-SKU-MAP');
      const mockMCFOrder = createMockMCFFulfillmentOrder('TT-SKU-MAP');

      mocks.tiktokClient.getOrderDetail.mockResolvedValue(mockOrder);
      mocks.amazonClient.createFulfillmentOrder.mockImplementation((params) => {
        // Verify SKU mapping was applied
        expect(params.items[0].sellerSku).toBe('AMAZON-MAPPED-SKU');
        return Promise.resolve(mockMCFOrder);
      });
      mocks.amazonClient.getFulfillmentOrder.mockResolvedValue(mockMCFOrder);

      // Add SKU mapping
      connector.addSkuMapping('TIKTOK-SKU-001', 'AMAZON-MAPPED-SKU');

      const result = await connector.routeOrder('TT-SKU-MAP');

      expect(result.success).toBe(true);
      expect(mocks.amazonClient.createFulfillmentOrder).toHaveBeenCalled();
    });
  });

  describe('Graceful Shutdown', () => {
    it('should cleanup resources on shutdown', async () => {
      const { connector } = createMockConnector();

      // Start scheduler (if implemented)
      connector.startTrackingSyncScheduler();

      // Shutdown should stop scheduler
      await connector.shutdown();

      const stats = connector.getTrackingSyncStats();
      expect(stats.schedulerRunning).toBe(false);
    });
  });
});
