/**
 * Order Router Tests
 */

import { OrderRouter, createOrderRouter, type OrderRouterDependencies } from '../order-router';
import { TikTokOrderStatus, ErrorCode } from '../../types/common';
import type { TikTokOrder } from '../../types/tiktok-order';
import type { Address } from '../../types/common';
import type { MCFFulfillmentOrderRequest, MCFFulfillmentOrder } from '../../types/mcf-order';

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

const createMockValidator = () => ({
  validateOrder: jest.fn(),
  validateAddress: jest.fn(),
});

const createMockTransformer = () => ({
  transformOrder: jest.fn(),
  addSKUMapping: jest.fn(),
  removeSKUMapping: jest.fn(),
  getSKUMappings: jest.fn(),
  updateConfig: jest.fn(),
  getConfig: jest.fn(),
});

// ============================================================
// Test Data Factories
// ============================================================

function createValidTikTokOrder(orderId: string = 'TEST123'): TikTokOrder {
  return {
    id: orderId,
    status: TikTokOrderStatus.AWAITING_SHIPMENT,
    create_time: Math.floor(Date.now() / 1000),
    update_time: Math.floor(Date.now() / 1000),
    paid_time: Math.floor(Date.now() / 1000),

    recipient_address: {
      recipient_name: 'John Doe',
      phone_number: '+1-555-0100',
      full_address: '123 Main St, Apt 4B',
      address_line_1: '123 Main St',
      address_line_2: 'Apt 4B',
      city: 'San Francisco',
      state: 'CA',
      postal_code: '94105',
      region_code: 'US',
    },

    items: [
      {
        id: 'item-1',
        product_id: 'prod-1',
        product_name: 'Test Product',
        sku_id: 'SKU123',
        seller_sku: 'SELLER-SKU-123',
        quantity: 2,
        sale_price: 29.99,
      },
    ],

    payment_info: {
      currency: 'USD',
      sub_total: 59.98,
      shipping_fee: 5.00,
      tax: 5.40,
      total_amount: 70.38,
      seller_discount: 0,
      platform_discount: 0,
    },

    fulfillment_type: 'FULFILLED_BY_SELLER',
    shipping_type: 'STANDARD',
    delivery_option_name: 'Standard Shipping',

    buyer_info: {
      email: 'customer@example.com',
    },

    buyer_message: 'Please gift wrap',
    seller_note: 'VIP customer',
  };
}

function createNormalizedAddress(): Address {
  return {
    name: 'John Doe',
    addressLine1: '123 Main St',
    addressLine2: 'Apt 4B',
    city: 'San Francisco',
    stateOrRegion: 'CA',
    postalCode: '94105',
    countryCode: 'US',
    phoneNumber: '+15550100',
  };
}

function createMCFOrderRequest(): MCFFulfillmentOrderRequest {
  return {
    sellerFulfillmentOrderId: 'TIKTOK-TEST123',
    displayableOrderId: 'TEST123',
    displayableOrderDate: new Date().toISOString(),
    displayableOrderComment: 'Buyer: Please gift wrap | Note: VIP customer',
    shippingSpeedCategory: 'Standard',
    destinationAddress: {
      name: 'John Doe',
      addressLine1: '123 Main St',
      addressLine2: 'Apt 4B',
      city: 'San Francisco',
      stateOrRegion: 'CA',
      postalCode: '94105',
      countryCode: 'US',
      phone: '+15550100',
    },
    fulfillmentPolicy: 'FillOrKill',
    fulfillmentAction: 'Ship',
    items: [
      {
        sellerSku: 'AMAZON-SKU-123',
        sellerFulfillmentOrderItemId: 'item-1',
        quantity: 2,
      },
    ],
  };
}

function createMCFFulfillmentOrder(): MCFFulfillmentOrder {
  return {
    sellerFulfillmentOrderId: 'TIKTOK-TEST123',
    displayableOrderId: 'TEST123',
    displayableOrderDate: new Date().toISOString(),
    shippingSpeedCategory: 'Standard',
    deliveryWindow: undefined,
    destinationAddress: {
      name: 'John Doe',
      addressLine1: '123 Main St',
      addressLine2: 'Apt 4B',
      city: 'San Francisco',
      stateOrRegion: 'CA',
      postalCode: '94105',
      countryCode: 'US',
      phone: '+15550100',
    },
    fulfillmentAction: 'Ship',
    fulfillmentPolicy: 'FillOrKill',
    fulfillmentOrderStatus: 'Received',
    statusUpdatedDate: new Date().toISOString(),
    receivedDate: new Date().toISOString(),
    items: [
      {
        sellerSku: 'AMAZON-SKU-123',
        sellerFulfillmentOrderItemId: 'item-1',
        quantity: 2,
        cancelledQuantity: 0,
        unfulfillableQuantity: 0,
      },
    ],
  };
}

// ============================================================
// Tests
// ============================================================

describe('OrderRouter', () => {
  let router: OrderRouter;
  let mockTikTokClient: ReturnType<typeof createMockTikTokClient>;
  let mockAmazonClient: ReturnType<typeof createMockAmazonClient>;
  let mockValidator: ReturnType<typeof createMockValidator>;
  let mockTransformer: ReturnType<typeof createMockTransformer>;

  beforeEach(() => {
    mockTikTokClient = createMockTikTokClient();
    mockAmazonClient = createMockAmazonClient();
    mockValidator = createMockValidator();
    mockTransformer = createMockTransformer();

    const dependencies: OrderRouterDependencies = {
      tiktokClient: mockTikTokClient as any,
      amazonClient: mockAmazonClient as any,
      validator: mockValidator as any,
      transformer: mockTransformer as any,
    };

    router = createOrderRouter(dependencies);
  });

  describe('routeOrder', () => {
    it('should successfully route an order through the full pipeline', async () => {
      const orderId = 'TEST123';
      const tiktokOrder = createValidTikTokOrder(orderId);
      const normalizedAddress = createNormalizedAddress();
      const mcfRequest = createMCFOrderRequest();
      const mcfOrder = createMCFFulfillmentOrder();

      // Setup mocks
      mockTikTokClient.getOrderDetail.mockResolvedValue({ order: tiktokOrder });
      mockValidator.validateOrder.mockReturnValue({
        valid: true,
        errors: [],
        normalizedOrder: {
          id: orderId,
          status: TikTokOrderStatus.AWAITING_SHIPMENT,
          createdAt: new Date(),
          updatedAt: new Date(),
          customer: { name: 'John Doe', email: 'customer@example.com', phone: '+1-555-0100' },
          shippingAddress: normalizedAddress,
          items: [{ id: 'item-1', productId: 'prod-1', productName: 'Test Product', sku: 'SELLER-SKU-123', quantity: 2, price: 29.99, totalPrice: 59.98 }],
          payment: { currency: 'USD', subtotal: 59.98, shippingFee: 5.00, tax: 5.40, discounts: 0, total: 70.38 },
          fulfillmentType: 'FULFILLED_BY_SELLER',
          rawOrder: tiktokOrder,
        },
        normalizedAddress,
      });
      mockTransformer.transformOrder.mockReturnValue({
        success: true,
        errors: [],
        mcfOrderRequest: mcfRequest,
      });
      mockAmazonClient.createFulfillmentOrder.mockResolvedValue({});
      mockAmazonClient.getFulfillmentOrder.mockResolvedValue({ fulfillmentOrder: mcfOrder });

      // Execute
      const result = await router.routeOrder(orderId);

      // Verify
      expect(result.success).toBe(true);
      expect(result.orderId).toBe(orderId);
      expect(result.successResult).toBeDefined();
      expect(result.successResult?.tiktokOrder).toEqual(tiktokOrder);
      expect(result.successResult?.mcfFulfillmentOrderId).toBe('TIKTOK-TEST123');
      expect(result.successResult?.mcfOrder).toEqual(mcfOrder);
      expect(result.error).toBeUndefined();

      // Verify call sequence
      expect(mockTikTokClient.getOrderDetail).toHaveBeenCalledWith(orderId);
      expect(mockValidator.validateOrder).toHaveBeenCalledWith(tiktokOrder);
      expect(mockTransformer.transformOrder).toHaveBeenCalled();
      expect(mockAmazonClient.createFulfillmentOrder).toHaveBeenCalledWith(mcfRequest);
      expect(mockAmazonClient.getFulfillmentOrder).toHaveBeenCalledWith('TIKTOK-TEST123');
    });

    it('should handle TikTok fetch failure', async () => {
      const orderId = 'TEST123';
      const error = new Error('TikTok API timeout');

      mockTikTokClient.getOrderDetail.mockRejectedValue(error);

      const result = await router.routeOrder(orderId);

      expect(result.success).toBe(false);
      expect(result.orderId).toBe(orderId);
      expect(result.error).toBeDefined();
      expect(result.error?.stage).toBe('fetch');
      expect(result.error?.code).toBe(ErrorCode.TIKTOK_API_ERROR);
      expect(result.error?.message).toContain('Failed to fetch order from TikTok');
      expect(result.successResult).toBeUndefined();
    });

    it('should handle validation failure', async () => {
      const orderId = 'TEST123';
      const tiktokOrder = createValidTikTokOrder(orderId);

      mockTikTokClient.getOrderDetail.mockResolvedValue({ order: tiktokOrder });
      mockValidator.validateOrder.mockReturnValue({
        valid: false,
        errors: [
          { field: 'recipient_address.postal_code', message: 'Invalid postal code', code: ErrorCode.INVALID_ADDRESS },
        ],
      });

      const result = await router.routeOrder(orderId);

      expect(result.success).toBe(false);
      expect(result.orderId).toBe(orderId);
      expect(result.error).toBeDefined();
      expect(result.error?.stage).toBe('validate');
      expect(result.error?.code).toBe(ErrorCode.VALIDATION_FAILED);
      expect(result.error?.message).toContain('Order validation failed');
      expect(result.successResult).toBeUndefined();
    });

    it('should collect validation warnings in success result', async () => {
      const orderId = 'TEST123';
      const tiktokOrder = createValidTikTokOrder(orderId);
      const normalizedAddress = createNormalizedAddress();
      const mcfRequest = createMCFOrderRequest();

      mockTikTokClient.getOrderDetail.mockResolvedValue({ order: tiktokOrder });
      mockValidator.validateOrder.mockReturnValue({
        valid: true,
        errors: [],
        warnings: [
          { field: 'items[0].seller_sku', message: 'Missing seller SKU' },
        ],
        normalizedOrder: {
          id: orderId,
          status: TikTokOrderStatus.AWAITING_SHIPMENT,
          createdAt: new Date(),
          updatedAt: new Date(),
          customer: { name: 'John Doe', email: 'customer@example.com', phone: '+1-555-0100' },
          shippingAddress: normalizedAddress,
          items: [{ id: 'item-1', productId: 'prod-1', productName: 'Test Product', sku: 'SKU123', quantity: 2, price: 29.99, totalPrice: 59.98 }],
          payment: { currency: 'USD', subtotal: 59.98, shippingFee: 5.00, tax: 5.40, discounts: 0, total: 70.38 },
          fulfillmentType: 'FULFILLED_BY_SELLER',
          rawOrder: tiktokOrder,
        },
        normalizedAddress,
      });
      mockTransformer.transformOrder.mockReturnValue({
        success: true,
        errors: [],
        mcfOrderRequest: mcfRequest,
      });
      mockAmazonClient.createFulfillmentOrder.mockResolvedValue({});

      const result = await router.routeOrder(orderId);

      expect(result.success).toBe(true);
      expect(result.successResult?.warnings).toBeDefined();
      expect(result.successResult?.warnings).toHaveLength(1);
      expect(result.successResult?.warnings?.[0].stage).toBe('validate');
      expect(result.successResult?.warnings?.[0].message).toContain('Missing seller SKU');
    });

    it('should handle transformation failure', async () => {
      const orderId = 'TEST123';
      const tiktokOrder = createValidTikTokOrder(orderId);
      const normalizedAddress = createNormalizedAddress();

      mockTikTokClient.getOrderDetail.mockResolvedValue({ order: tiktokOrder });
      mockValidator.validateOrder.mockReturnValue({
        valid: true,
        errors: [],
        normalizedOrder: {
          id: orderId,
          status: TikTokOrderStatus.AWAITING_SHIPMENT,
          createdAt: new Date(),
          updatedAt: new Date(),
          customer: { name: 'John Doe', email: 'customer@example.com', phone: '+1-555-0100' },
          shippingAddress: normalizedAddress,
          items: [],
          payment: { currency: 'USD', subtotal: 0, shippingFee: 0, tax: 0, discounts: 0, total: 0 },
          fulfillmentType: 'FULFILLED_BY_SELLER',
          rawOrder: tiktokOrder,
        },
        normalizedAddress,
      });
      mockTransformer.transformOrder.mockReturnValue({
        success: false,
        errors: [
          { field: 'items', message: 'No valid items', code: ErrorCode.TRANSFORMATION_FAILED },
        ],
      });

      const result = await router.routeOrder(orderId);

      expect(result.success).toBe(false);
      expect(result.orderId).toBe(orderId);
      expect(result.error).toBeDefined();
      expect(result.error?.stage).toBe('transform');
      expect(result.error?.code).toBe(ErrorCode.TRANSFORMATION_FAILED);
      expect(result.error?.message).toContain('Order transformation failed');
      expect(result.successResult).toBeUndefined();
    });

    it('should collect transformation warnings in success result', async () => {
      const orderId = 'TEST123';
      const tiktokOrder = createValidTikTokOrder(orderId);
      const normalizedAddress = createNormalizedAddress();
      const mcfRequest = createMCFOrderRequest();

      mockTikTokClient.getOrderDetail.mockResolvedValue({ order: tiktokOrder });
      mockValidator.validateOrder.mockReturnValue({
        valid: true,
        errors: [],
        normalizedOrder: {
          id: orderId,
          status: TikTokOrderStatus.AWAITING_SHIPMENT,
          createdAt: new Date(),
          updatedAt: new Date(),
          customer: { name: 'John Doe', email: 'customer@example.com', phone: '+1-555-0100' },
          shippingAddress: normalizedAddress,
          items: [{ id: 'item-1', productId: 'prod-1', productName: 'Test Product', sku: 'SKU123', quantity: 2, price: 29.99, totalPrice: 59.98 }],
          payment: { currency: 'USD', subtotal: 59.98, shippingFee: 5.00, tax: 5.40, discounts: 0, total: 70.38 },
          fulfillmentType: 'FULFILLED_BY_SELLER',
          rawOrder: tiktokOrder,
        },
        normalizedAddress,
      });
      mockTransformer.transformOrder.mockReturnValue({
        success: true,
        errors: [],
        warnings: [
          { field: 'items[0].sku', message: 'No SKU mapping found' },
        ],
        mcfOrderRequest: mcfRequest,
      });
      mockAmazonClient.createFulfillmentOrder.mockResolvedValue({});

      const result = await router.routeOrder(orderId);

      expect(result.success).toBe(true);
      expect(result.successResult?.warnings).toBeDefined();
      expect(result.successResult?.warnings).toHaveLength(1);
      expect(result.successResult?.warnings?.[0].stage).toBe('transform');
      expect(result.successResult?.warnings?.[0].message).toContain('No SKU mapping found');
    });

    it('should handle MCF creation failure', async () => {
      const orderId = 'TEST123';
      const tiktokOrder = createValidTikTokOrder(orderId);
      const normalizedAddress = createNormalizedAddress();
      const mcfRequest = createMCFOrderRequest();
      const error = new Error('MCF API error: insufficient inventory');

      mockTikTokClient.getOrderDetail.mockResolvedValue({ order: tiktokOrder });
      mockValidator.validateOrder.mockReturnValue({
        valid: true,
        errors: [],
        normalizedOrder: {
          id: orderId,
          status: TikTokOrderStatus.AWAITING_SHIPMENT,
          createdAt: new Date(),
          updatedAt: new Date(),
          customer: { name: 'John Doe', email: 'customer@example.com', phone: '+1-555-0100' },
          shippingAddress: normalizedAddress,
          items: [{ id: 'item-1', productId: 'prod-1', productName: 'Test Product', sku: 'SELLER-SKU-123', quantity: 2, price: 29.99, totalPrice: 59.98 }],
          payment: { currency: 'USD', subtotal: 59.98, shippingFee: 5.00, tax: 5.40, discounts: 0, total: 70.38 },
          fulfillmentType: 'FULFILLED_BY_SELLER',
          rawOrder: tiktokOrder,
        },
        normalizedAddress,
      });
      mockTransformer.transformOrder.mockReturnValue({
        success: true,
        errors: [],
        mcfOrderRequest: mcfRequest,
      });
      mockAmazonClient.createFulfillmentOrder.mockRejectedValue(error);

      const result = await router.routeOrder(orderId);

      expect(result.success).toBe(false);
      expect(result.orderId).toBe(orderId);
      expect(result.error).toBeDefined();
      expect(result.error?.stage).toBe('create_mcf');
      expect(result.error?.code).toBe(ErrorCode.MCF_API_ERROR);
      expect(result.error?.message).toContain('Failed to create MCF fulfillment order');
      expect(result.successResult).toBeUndefined();
    });

    it('should succeed even if fetching MCF order details fails', async () => {
      const orderId = 'TEST123';
      const tiktokOrder = createValidTikTokOrder(orderId);
      const normalizedAddress = createNormalizedAddress();
      const mcfRequest = createMCFOrderRequest();

      mockTikTokClient.getOrderDetail.mockResolvedValue({ order: tiktokOrder });
      mockValidator.validateOrder.mockReturnValue({
        valid: true,
        errors: [],
        normalizedOrder: {
          id: orderId,
          status: TikTokOrderStatus.AWAITING_SHIPMENT,
          createdAt: new Date(),
          updatedAt: new Date(),
          customer: { name: 'John Doe', email: 'customer@example.com', phone: '+1-555-0100' },
          shippingAddress: normalizedAddress,
          items: [{ id: 'item-1', productId: 'prod-1', productName: 'Test Product', sku: 'SELLER-SKU-123', quantity: 2, price: 29.99, totalPrice: 59.98 }],
          payment: { currency: 'USD', subtotal: 59.98, shippingFee: 5.00, tax: 5.40, discounts: 0, total: 70.38 },
          fulfillmentType: 'FULFILLED_BY_SELLER',
          rawOrder: tiktokOrder,
        },
        normalizedAddress,
      });
      mockTransformer.transformOrder.mockReturnValue({
        success: true,
        errors: [],
        mcfOrderRequest: mcfRequest,
      });
      mockAmazonClient.createFulfillmentOrder.mockResolvedValue({});
      mockAmazonClient.getFulfillmentOrder.mockRejectedValue(new Error('Order not found yet'));

      const result = await router.routeOrder(orderId);

      expect(result.success).toBe(true);
      expect(result.successResult?.mcfFulfillmentOrderId).toBe('TIKTOK-TEST123');
      expect(result.successResult?.mcfOrder).toBeUndefined();
    });
  });

  describe('routeOrders', () => {
    it('should route multiple orders successfully', async () => {
      const orderIds = ['TEST1', 'TEST2', 'TEST3'];
      const normalizedAddress = createNormalizedAddress();
      const mcfRequest = createMCFOrderRequest();

      mockTikTokClient.getOrderDetail.mockImplementation((orderId: string) =>
        Promise.resolve({ order: createValidTikTokOrder(orderId) })
      );
      mockValidator.validateOrder.mockImplementation((order: TikTokOrder) => ({
        valid: true,
        errors: [],
        normalizedOrder: {
          id: order.id,
          status: TikTokOrderStatus.AWAITING_SHIPMENT,
          createdAt: new Date(),
          updatedAt: new Date(),
          customer: { name: 'John Doe', email: 'customer@example.com', phone: '+1-555-0100' },
          shippingAddress: normalizedAddress,
          items: [{ id: 'item-1', productId: 'prod-1', productName: 'Test Product', sku: 'SELLER-SKU-123', quantity: 2, price: 29.99, totalPrice: 59.98 }],
          payment: { currency: 'USD', subtotal: 59.98, shippingFee: 5.00, tax: 5.40, discounts: 0, total: 70.38 },
          fulfillmentType: 'FULFILLED_BY_SELLER',
          rawOrder: order,
        },
        normalizedAddress,
      }));
      mockTransformer.transformOrder.mockReturnValue({
        success: true,
        errors: [],
        mcfOrderRequest: mcfRequest,
      });
      mockAmazonClient.createFulfillmentOrder.mockResolvedValue({});

      const result = await router.routeOrders(orderIds);

      expect(result.totalOrders).toBe(3);
      expect(result.successCount).toBe(3);
      expect(result.failureCount).toBe(0);
      expect(result.results).toHaveLength(3);
      expect(result.errors).toHaveLength(0);
      expect(result.results.every(r => r.success)).toBe(true);
    });

    it('should continue on error by default', async () => {
      const orderIds = ['TEST1', 'TEST2', 'TEST3'];
      const normalizedAddress = createNormalizedAddress();
      const mcfRequest = createMCFOrderRequest();

      mockTikTokClient.getOrderDetail.mockImplementation((orderId: string) => {
        if (orderId === 'TEST2') {
          return Promise.reject(new Error('Order not found'));
        }
        return Promise.resolve({ order: createValidTikTokOrder(orderId) });
      });
      mockValidator.validateOrder.mockReturnValue({
        valid: true,
        errors: [],
        normalizedOrder: {
          id: 'TEST1',
          status: TikTokOrderStatus.AWAITING_SHIPMENT,
          createdAt: new Date(),
          updatedAt: new Date(),
          customer: { name: 'John Doe', email: 'customer@example.com', phone: '+1-555-0100' },
          shippingAddress: normalizedAddress,
          items: [{ id: 'item-1', productId: 'prod-1', productName: 'Test Product', sku: 'SELLER-SKU-123', quantity: 2, price: 29.99, totalPrice: 59.98 }],
          payment: { currency: 'USD', subtotal: 59.98, shippingFee: 5.00, tax: 5.40, discounts: 0, total: 70.38 },
          fulfillmentType: 'FULFILLED_BY_SELLER',
          rawOrder: createValidTikTokOrder('TEST1'),
        },
        normalizedAddress,
      });
      mockTransformer.transformOrder.mockReturnValue({
        success: true,
        errors: [],
        mcfOrderRequest: mcfRequest,
      });
      mockAmazonClient.createFulfillmentOrder.mockResolvedValue({});

      const result = await router.routeOrders(orderIds);

      expect(result.totalOrders).toBe(3);
      expect(result.successCount).toBe(2);
      expect(result.failureCount).toBe(1);
      expect(result.results).toHaveLength(3);
      expect(result.errors).toHaveLength(1);
      expect(result.errors[0].orderId).toBe('TEST2');
    });

    it('should stop on error when continueOnError is false', async () => {
      const orderIds = ['TEST1', 'TEST2', 'TEST3'];
      const normalizedAddress = createNormalizedAddress();
      const mcfRequest = createMCFOrderRequest();

      router.updateConfig({ continueOnError: false });

      mockTikTokClient.getOrderDetail.mockImplementation((orderId: string) => {
        if (orderId === 'TEST2') {
          return Promise.reject(new Error('Order not found'));
        }
        return Promise.resolve({ order: createValidTikTokOrder(orderId) });
      });
      mockValidator.validateOrder.mockReturnValue({
        valid: true,
        errors: [],
        normalizedOrder: {
          id: 'TEST1',
          status: TikTokOrderStatus.AWAITING_SHIPMENT,
          createdAt: new Date(),
          updatedAt: new Date(),
          customer: { name: 'John Doe', email: 'customer@example.com', phone: '+1-555-0100' },
          shippingAddress: normalizedAddress,
          items: [{ id: 'item-1', productId: 'prod-1', productName: 'Test Product', sku: 'SELLER-SKU-123', quantity: 2, price: 29.99, totalPrice: 59.98 }],
          payment: { currency: 'USD', subtotal: 59.98, shippingFee: 5.00, tax: 5.40, discounts: 0, total: 70.38 },
          fulfillmentType: 'FULFILLED_BY_SELLER',
          rawOrder: createValidTikTokOrder('TEST1'),
        },
        normalizedAddress,
      });
      mockTransformer.transformOrder.mockReturnValue({
        success: true,
        errors: [],
        mcfOrderRequest: mcfRequest,
      });
      mockAmazonClient.createFulfillmentOrder.mockResolvedValue({});

      const result = await router.routeOrders(orderIds);

      // Should have processed batch 1 (TEST1, TEST2, TEST3) all together since maxConcurrent = 5
      // But stopped after finding error in TEST2
      expect(result.failureCount).toBeGreaterThan(0);
      expect(result.errors.length).toBeGreaterThan(0);
    });

    it('should respect maxConcurrentOrders limit', async () => {
      const orderIds = ['TEST1', 'TEST2', 'TEST3', 'TEST4', 'TEST5', 'TEST6'];
      const normalizedAddress = createNormalizedAddress();
      const mcfRequest = createMCFOrderRequest();

      router.updateConfig({ maxConcurrentOrders: 2 });

      let concurrentCalls = 0;
      let maxConcurrent = 0;

      mockTikTokClient.getOrderDetail.mockImplementation(async (orderId: string) => {
        concurrentCalls++;
        maxConcurrent = Math.max(maxConcurrent, concurrentCalls);
        await new Promise(resolve => setTimeout(resolve, 10));
        concurrentCalls--;
        return { order: createValidTikTokOrder(orderId) };
      });

      mockValidator.validateOrder.mockReturnValue({
        valid: true,
        errors: [],
        normalizedOrder: {
          id: 'TEST1',
          status: TikTokOrderStatus.AWAITING_SHIPMENT,
          createdAt: new Date(),
          updatedAt: new Date(),
          customer: { name: 'John Doe', email: 'customer@example.com', phone: '+1-555-0100' },
          shippingAddress: normalizedAddress,
          items: [{ id: 'item-1', productId: 'prod-1', productName: 'Test Product', sku: 'SELLER-SKU-123', quantity: 2, price: 29.99, totalPrice: 59.98 }],
          payment: { currency: 'USD', subtotal: 59.98, shippingFee: 5.00, tax: 5.40, discounts: 0, total: 70.38 },
          fulfillmentType: 'FULFILLED_BY_SELLER',
          rawOrder: createValidTikTokOrder('TEST1'),
        },
        normalizedAddress,
      });
      mockTransformer.transformOrder.mockReturnValue({
        success: true,
        errors: [],
        mcfOrderRequest: mcfRequest,
      });
      mockAmazonClient.createFulfillmentOrder.mockResolvedValue({});

      const result = await router.routeOrders(orderIds);

      expect(result.totalOrders).toBe(6);
      expect(result.successCount).toBe(6);
      expect(maxConcurrent).toBeLessThanOrEqual(2);
    });

    it('should handle empty order list', async () => {
      const result = await router.routeOrders([]);

      expect(result.totalOrders).toBe(0);
      expect(result.successCount).toBe(0);
      expect(result.failureCount).toBe(0);
      expect(result.results).toHaveLength(0);
      expect(result.errors).toHaveLength(0);
    });
  });

  describe('routePendingOrders', () => {
    it('should fetch and route all pending orders', async () => {
      const awaitingShipmentOrders = [
        createValidTikTokOrder('TEST1'),
        createValidTikTokOrder('TEST2'),
      ];
      const awaitingCollectionOrders = [
        createValidTikTokOrder('TEST3'),
      ];
      const normalizedAddress = createNormalizedAddress();
      const mcfRequest = createMCFOrderRequest();

      mockTikTokClient.getOrders.mockImplementation((params: any) => {
        if (params.order_status === TikTokOrderStatus.AWAITING_SHIPMENT) {
          return Promise.resolve({
            orders: awaitingShipmentOrders,
            more: false,
            next_page_token: undefined,
          });
        } else if (params.order_status === TikTokOrderStatus.AWAITING_COLLECTION) {
          return Promise.resolve({
            orders: awaitingCollectionOrders,
            more: false,
            next_page_token: undefined,
          });
        }
        return Promise.resolve({ orders: [], more: false, next_page_token: undefined });
      });

      mockTikTokClient.getOrderDetail.mockImplementation((orderId: string) => {
        const allOrders = [...awaitingShipmentOrders, ...awaitingCollectionOrders];
        const order = allOrders.find(o => o.id === orderId);
        return Promise.resolve({ order: order! });
      });

      mockValidator.validateOrder.mockReturnValue({
        valid: true,
        errors: [],
        normalizedOrder: {
          id: 'TEST1',
          status: TikTokOrderStatus.AWAITING_SHIPMENT,
          createdAt: new Date(),
          updatedAt: new Date(),
          customer: { name: 'John Doe', email: 'customer@example.com', phone: '+1-555-0100' },
          shippingAddress: normalizedAddress,
          items: [{ id: 'item-1', productId: 'prod-1', productName: 'Test Product', sku: 'SELLER-SKU-123', quantity: 2, price: 29.99, totalPrice: 59.98 }],
          payment: { currency: 'USD', subtotal: 59.98, shippingFee: 5.00, tax: 5.40, discounts: 0, total: 70.38 },
          fulfillmentType: 'FULFILLED_BY_SELLER',
          rawOrder: createValidTikTokOrder('TEST1'),
        },
        normalizedAddress,
      });
      mockTransformer.transformOrder.mockReturnValue({
        success: true,
        errors: [],
        mcfOrderRequest: mcfRequest,
      });
      mockAmazonClient.createFulfillmentOrder.mockResolvedValue({});

      const result = await router.routePendingOrders();

      expect(result.totalOrders).toBe(3);
      expect(result.successCount).toBe(3);
      expect(result.failureCount).toBe(0);
      expect(mockTikTokClient.getOrders).toHaveBeenCalledTimes(2);
    });

    it('should handle pagination when fetching pending orders', async () => {
      const page1Orders = [createValidTikTokOrder('TEST1')];
      const page2Orders = [createValidTikTokOrder('TEST2')];
      const normalizedAddress = createNormalizedAddress();
      const mcfRequest = createMCFOrderRequest();

      mockTikTokClient.getOrders.mockImplementation((params: any) => {
        if (params.order_status === TikTokOrderStatus.AWAITING_SHIPMENT) {
          if (!params.page_token) {
            return Promise.resolve({
              orders: page1Orders,
              more: true,
              next_page_token: 'token123',
            });
          } else if (params.page_token === 'token123') {
            return Promise.resolve({
              orders: page2Orders,
              more: false,
              next_page_token: undefined,
            });
          }
        }
        return Promise.resolve({ orders: [], more: false, next_page_token: undefined });
      });

      mockTikTokClient.getOrderDetail.mockImplementation((orderId: string) => {
        const allOrders = [...page1Orders, ...page2Orders];
        const order = allOrders.find(o => o.id === orderId);
        return Promise.resolve({ order: order! });
      });

      mockValidator.validateOrder.mockReturnValue({
        valid: true,
        errors: [],
        normalizedOrder: {
          id: 'TEST1',
          status: TikTokOrderStatus.AWAITING_SHIPMENT,
          createdAt: new Date(),
          updatedAt: new Date(),
          customer: { name: 'John Doe', email: 'customer@example.com', phone: '+1-555-0100' },
          shippingAddress: normalizedAddress,
          items: [{ id: 'item-1', productId: 'prod-1', productName: 'Test Product', sku: 'SELLER-SKU-123', quantity: 2, price: 29.99, totalPrice: 59.98 }],
          payment: { currency: 'USD', subtotal: 59.98, shippingFee: 5.00, tax: 5.40, discounts: 0, total: 70.38 },
          fulfillmentType: 'FULFILLED_BY_SELLER',
          rawOrder: createValidTikTokOrder('TEST1'),
        },
        normalizedAddress,
      });
      mockTransformer.transformOrder.mockReturnValue({
        success: true,
        errors: [],
        mcfOrderRequest: mcfRequest,
      });
      mockAmazonClient.createFulfillmentOrder.mockResolvedValue({});

      const result = await router.routePendingOrders();

      expect(result.totalOrders).toBe(2);
      expect(result.successCount).toBe(2);
      expect(mockTikTokClient.getOrders).toHaveBeenCalledWith(
        expect.objectContaining({ page_token: 'token123' })
      );
    });

    it('should return empty result when no pending orders', async () => {
      mockTikTokClient.getOrders.mockResolvedValue({
        orders: [],
        more: false,
        next_page_token: undefined,
      });

      const result = await router.routePendingOrders();

      expect(result.totalOrders).toBe(0);
      expect(result.successCount).toBe(0);
      expect(result.failureCount).toBe(0);
      expect(result.results).toHaveLength(0);
    });

    it('should handle error fetching pending orders', async () => {
      mockTikTokClient.getOrders.mockRejectedValue(new Error('TikTok API error'));

      const result = await router.routePendingOrders();

      expect(result.totalOrders).toBe(0);
      expect(result.successCount).toBe(0);
      expect(result.failureCount).toBe(0);
      expect(result.errors).toHaveLength(1);
      expect(result.errors[0].code).toBe(ErrorCode.TIKTOK_API_ERROR);
    });
  });

  describe('configuration', () => {
    it('should use default configuration', () => {
      const config = router.getConfig();

      expect(config.continueOnError).toBe(true);
      expect(config.maxConcurrentOrders).toBe(5);
    });

    it('should allow updating configuration', () => {
      router.updateConfig({
        continueOnError: false,
        maxConcurrentOrders: 10,
      });

      const config = router.getConfig();

      expect(config.continueOnError).toBe(false);
      expect(config.maxConcurrentOrders).toBe(10);
    });

    it('should partially update configuration', () => {
      router.updateConfig({ maxConcurrentOrders: 3 });

      const config = router.getConfig();

      expect(config.continueOnError).toBe(true);
      expect(config.maxConcurrentOrders).toBe(3);
    });
  });

  describe('createOrderRouter', () => {
    it('should create order router instance', () => {
      const dependencies: OrderRouterDependencies = {
        tiktokClient: mockTikTokClient as any,
        amazonClient: mockAmazonClient as any,
        validator: mockValidator as any,
        transformer: mockTransformer as any,
      };

      const newRouter = createOrderRouter(dependencies, {
        continueOnError: false,
      });

      expect(newRouter).toBeInstanceOf(OrderRouter);
      expect(newRouter.getConfig().continueOnError).toBe(false);
    });
  });
});
