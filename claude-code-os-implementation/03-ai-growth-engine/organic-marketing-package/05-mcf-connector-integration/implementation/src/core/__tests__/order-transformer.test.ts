/**
 * Order Transformer Tests
 */

import { OrderTransformer, createOrderTransformer } from '../order-transformer';
import { TikTokOrderStatus } from '../../types/common';
import type { NormalizedTikTokOrder } from '../../types/tiktok-order';
import type { Address } from '../../types/common';
import type { TikTokOrder } from '../../types/tiktok-order';

describe('OrderTransformer', () => {
  let transformer: OrderTransformer;

  beforeEach(() => {
    transformer = createOrderTransformer();
  });

  describe('transformOrder', () => {
    it('should transform a valid TikTok order to MCF format', () => {
      const { normalizedOrder, normalizedAddress } = createTestOrder();
      const result = transformer.transformOrder(normalizedOrder, normalizedAddress);

      expect(result.success).toBe(true);
      expect(result.errors).toHaveLength(0);
      expect(result.mcfOrderRequest).toBeDefined();

      const mcfOrder = result.mcfOrderRequest!;
      expect(mcfOrder.sellerFulfillmentOrderId).toBe(`TIKTOK-${normalizedOrder.id}`);
      expect(mcfOrder.displayableOrderId).toBe(normalizedOrder.id);
      expect(mcfOrder.items).toHaveLength(2);
      expect(mcfOrder.destinationAddress).toBeDefined();
    });

    it('should convert address correctly', () => {
      const { normalizedOrder, normalizedAddress } = createTestOrder();
      const result = transformer.transformOrder(normalizedOrder, normalizedAddress);

      expect(result.success).toBe(true);
      const mcfAddress = result.mcfOrderRequest!.destinationAddress;

      expect(mcfAddress.name).toBe(normalizedAddress.name);
      expect(mcfAddress.addressLine1).toBe(normalizedAddress.addressLine1);
      expect(mcfAddress.city).toBe(normalizedAddress.city);
      expect(mcfAddress.stateOrRegion).toBe(normalizedAddress.stateOrRegion);
      expect(mcfAddress.postalCode).toBe(normalizedAddress.postalCode);
      expect(mcfAddress.countryCode).toBe(normalizedAddress.countryCode);
      expect(mcfAddress.phone).toBe(normalizedAddress.phoneNumber);
    });

    it('should transform order items correctly', () => {
      const { normalizedOrder, normalizedAddress } = createTestOrder();
      const result = transformer.transformOrder(normalizedOrder, normalizedAddress);

      expect(result.success).toBe(true);
      const mcfItems = result.mcfOrderRequest!.items;

      expect(mcfItems).toHaveLength(2);
      expect(mcfItems[0].sellerSku).toBe(normalizedOrder.items[0].sku);
      expect(mcfItems[0].sellerFulfillmentOrderItemId).toBe(normalizedOrder.items[0].id);
      expect(mcfItems[0].quantity).toBe(normalizedOrder.items[0].quantity);
      expect(mcfItems[1].sellerSku).toBe(normalizedOrder.items[1].sku);
      expect(mcfItems[1].quantity).toBe(normalizedOrder.items[1].quantity);
    });

    it('should include item prices when configured', () => {
      transformer = createOrderTransformer({
        includeItemPrices: true,
      });

      const { normalizedOrder, normalizedAddress } = createTestOrder();
      const result = transformer.transformOrder(normalizedOrder, normalizedAddress);

      expect(result.success).toBe(true);
      const mcfItems = result.mcfOrderRequest!.items;

      expect(mcfItems[0].perUnitPrice).toBeDefined();
      expect(mcfItems[0].perUnitPrice!.value).toBe(normalizedOrder.items[0].price);
      expect(mcfItems[0].perUnitPrice!.currencyCode).toBe(normalizedOrder.payment.currency);

      expect(mcfItems[0].perUnitDeclaredValue).toBeDefined();
      expect(mcfItems[0].perUnitDeclaredValue!.value).toBe(normalizedOrder.items[0].price);
    });

    it('should not include item prices when disabled', () => {
      transformer = createOrderTransformer({
        includeItemPrices: false,
      });

      const { normalizedOrder, normalizedAddress } = createTestOrder();
      const result = transformer.transformOrder(normalizedOrder, normalizedAddress);

      expect(result.success).toBe(true);
      const mcfItems = result.mcfOrderRequest!.items;

      expect(mcfItems[0].perUnitPrice).toBeUndefined();
      expect(mcfItems[0].perUnitDeclaredValue).toBeUndefined();
    });

    it('should use default shipping speed', () => {
      const { normalizedOrder, normalizedAddress } = createTestOrder();
      const result = transformer.transformOrder(normalizedOrder, normalizedAddress);

      expect(result.success).toBe(true);
      expect(result.mcfOrderRequest!.shippingSpeedCategory).toBe('Standard');
    });

    it('should map expedited shipping type to Expedited speed', () => {
      const { normalizedOrder, normalizedAddress } = createTestOrder();
      normalizedOrder.rawOrder.shipping_type = 'EXPEDITED';

      const result = transformer.transformOrder(normalizedOrder, normalizedAddress);

      expect(result.success).toBe(true);
      expect(result.mcfOrderRequest!.shippingSpeedCategory).toBe('Expedited');
    });

    it('should map priority shipping type to Priority speed', () => {
      const { normalizedOrder, normalizedAddress } = createTestOrder();
      normalizedOrder.rawOrder.shipping_type = 'PRIORITY';

      const result = transformer.transformOrder(normalizedOrder, normalizedAddress);

      expect(result.success).toBe(true);
      expect(result.mcfOrderRequest!.shippingSpeedCategory).toBe('Priority');
    });

    it('should detect express delivery from delivery option name', () => {
      const { normalizedOrder, normalizedAddress } = createTestOrder();
      normalizedOrder.rawOrder.delivery_option_name = 'Express Delivery';

      const result = transformer.transformOrder(normalizedOrder, normalizedAddress);

      expect(result.success).toBe(true);
      expect(result.mcfOrderRequest!.shippingSpeedCategory).toBe('Expedited');
    });

    it('should detect priority from next-day delivery option', () => {
      const { normalizedOrder, normalizedAddress } = createTestOrder();
      normalizedOrder.rawOrder.delivery_option_name = 'Next Day Delivery';

      const result = transformer.transformOrder(normalizedOrder, normalizedAddress);

      expect(result.success).toBe(true);
      expect(result.mcfOrderRequest!.shippingSpeedCategory).toBe('Priority');
    });

    it('should include order comment when buyer message present', () => {
      transformer = createOrderTransformer({
        includeOrderComment: true,
      });

      const { normalizedOrder, normalizedAddress } = createTestOrder();
      normalizedOrder.buyerMessage = 'Please gift wrap';

      const result = transformer.transformOrder(normalizedOrder, normalizedAddress);

      expect(result.success).toBe(true);
      expect(result.mcfOrderRequest!.displayableOrderComment).toContain('Buyer: Please gift wrap');
    });

    it('should include seller note in order comment', () => {
      transformer = createOrderTransformer({
        includeOrderComment: true,
      });

      const { normalizedOrder, normalizedAddress } = createTestOrder();
      normalizedOrder.sellerNote = 'Fragile item';

      const result = transformer.transformOrder(normalizedOrder, normalizedAddress);

      expect(result.success).toBe(true);
      expect(result.mcfOrderRequest!.displayableOrderComment).toContain('Note: Fragile item');
    });

    it('should combine buyer message and seller note in comment', () => {
      transformer = createOrderTransformer({
        includeOrderComment: true,
      });

      const { normalizedOrder, normalizedAddress } = createTestOrder();
      normalizedOrder.buyerMessage = 'Please gift wrap';
      normalizedOrder.sellerNote = 'Fragile item';

      const result = transformer.transformOrder(normalizedOrder, normalizedAddress);

      expect(result.success).toBe(true);
      const comment = result.mcfOrderRequest!.displayableOrderComment!;
      expect(comment).toContain('Buyer: Please gift wrap');
      expect(comment).toContain('Note: Fragile item');
    });

    it('should truncate long order comments to 1000 characters', () => {
      transformer = createOrderTransformer({
        includeOrderComment: true,
      });

      const { normalizedOrder, normalizedAddress } = createTestOrder();
      // Create a very long message
      normalizedOrder.buyerMessage = 'A'.repeat(1500);

      const result = transformer.transformOrder(normalizedOrder, normalizedAddress);

      expect(result.success).toBe(true);
      const comment = result.mcfOrderRequest!.displayableOrderComment!;
      expect(comment.length).toBeLessThanOrEqual(1000);
      expect(comment.endsWith('...')).toBe(true);
    });

    it('should not include comment when disabled', () => {
      transformer = createOrderTransformer({
        includeOrderComment: false,
      });

      const { normalizedOrder, normalizedAddress } = createTestOrder();
      normalizedOrder.buyerMessage = 'Please gift wrap';

      const result = transformer.transformOrder(normalizedOrder, normalizedAddress);

      expect(result.success).toBe(true);
      expect(result.mcfOrderRequest!.displayableOrderComment).toBeUndefined();
    });

    it('should use custom default shipping speed', () => {
      transformer = createOrderTransformer({
        defaultShippingSpeed: 'Expedited',
      });

      const { normalizedOrder, normalizedAddress } = createTestOrder();
      const result = transformer.transformOrder(normalizedOrder, normalizedAddress);

      expect(result.success).toBe(true);
      expect(result.mcfOrderRequest!.shippingSpeedCategory).toBe('Expedited');
    });

    it('should use custom fulfillment policy', () => {
      transformer = createOrderTransformer({
        defaultFulfillmentPolicy: 'FillAll',
      });

      const { normalizedOrder, normalizedAddress } = createTestOrder();
      const result = transformer.transformOrder(normalizedOrder, normalizedAddress);

      expect(result.success).toBe(true);
      expect(result.mcfOrderRequest!.fulfillmentPolicy).toBe('FillAll');
    });

    it('should include notification emails when configured', () => {
      transformer = createOrderTransformer({
        notificationEmails: ['admin@example.com', 'ops@example.com'],
      });

      const { normalizedOrder, normalizedAddress } = createTestOrder();
      const result = transformer.transformOrder(normalizedOrder, normalizedAddress);

      expect(result.success).toBe(true);
      expect(result.mcfOrderRequest!.notificationEmails).toEqual([
        'admin@example.com',
        'ops@example.com',
      ]);
    });

    it('should format order date correctly', () => {
      const { normalizedOrder, normalizedAddress } = createTestOrder();
      const result = transformer.transformOrder(normalizedOrder, normalizedAddress);

      expect(result.success).toBe(true);
      const orderDate = result.mcfOrderRequest!.displayableOrderDate;
      expect(orderDate).toMatch(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$/);
    });
  });

  describe('SKU mapping', () => {
    it('should map TikTok SKU to Amazon SKU when mapping exists', () => {
      transformer = createOrderTransformer({
        skuMappings: [
          { tiktokSku: 'TT-WIDGET-001', amazonSku: 'AMZN-WIDGET-XYZ' },
        ],
      });

      const { normalizedOrder, normalizedAddress } = createTestOrder();
      normalizedOrder.items[0].sku = 'TT-WIDGET-001';

      const result = transformer.transformOrder(normalizedOrder, normalizedAddress);

      expect(result.success).toBe(true);
      expect(result.mcfOrderRequest!.items[0].sellerSku).toBe('AMZN-WIDGET-XYZ');
    });

    it('should use TikTok SKU directly when no mapping exists', () => {
      const { normalizedOrder, normalizedAddress } = createTestOrder();
      normalizedOrder.items[0].sku = 'UNMAPPED-SKU';

      const result = transformer.transformOrder(normalizedOrder, normalizedAddress);

      expect(result.success).toBe(true);
      expect(result.mcfOrderRequest!.items[0].sellerSku).toBe('UNMAPPED-SKU');
    });

    it('should warn when no SKU mapping found', () => {
      const { normalizedOrder, normalizedAddress } = createTestOrder();
      normalizedOrder.items[0].sku = 'UNMAPPED-SKU';

      const result = transformer.transformOrder(normalizedOrder, normalizedAddress);

      expect(result.success).toBe(true);
      expect(result.warnings).toBeDefined();
      expect(result.warnings).toContainEqual(
        expect.objectContaining({
          field: 'items[0].sku',
          message: expect.stringContaining('No SKU mapping found'),
        })
      );
    });

    it('should support adding SKU mapping', () => {
      transformer.addSKUMapping('TT-NEW-001', 'AMZN-NEW-001');

      const { normalizedOrder, normalizedAddress } = createTestOrder();
      normalizedOrder.items[0].sku = 'TT-NEW-001';

      const result = transformer.transformOrder(normalizedOrder, normalizedAddress);

      expect(result.success).toBe(true);
      expect(result.mcfOrderRequest!.items[0].sellerSku).toBe('AMZN-NEW-001');
    });

    it('should support removing SKU mapping', () => {
      transformer.addSKUMapping('TT-TEMP-001', 'AMZN-TEMP-001');
      transformer.removeSKUMapping('TT-TEMP-001');

      const { normalizedOrder, normalizedAddress } = createTestOrder();
      normalizedOrder.items[0].sku = 'TT-TEMP-001';

      const result = transformer.transformOrder(normalizedOrder, normalizedAddress);

      expect(result.success).toBe(true);
      expect(result.mcfOrderRequest!.items[0].sellerSku).toBe('TT-TEMP-001');
      expect(result.warnings).toBeDefined();
    });

    it('should replace existing SKU mapping when adding duplicate', () => {
      transformer.addSKUMapping('TT-PROD-001', 'AMZN-PROD-OLD');
      transformer.addSKUMapping('TT-PROD-001', 'AMZN-PROD-NEW');

      const mappings = transformer.getSKUMappings();
      const prodMappings = mappings.filter(m => m.tiktokSku === 'TT-PROD-001');

      expect(prodMappings).toHaveLength(1);
      expect(prodMappings[0].amazonSku).toBe('AMZN-PROD-NEW');
    });

    it('should get all SKU mappings', () => {
      transformer.addSKUMapping('TT-001', 'AMZN-001');
      transformer.addSKUMapping('TT-002', 'AMZN-002');

      const mappings = transformer.getSKUMappings();

      expect(mappings).toHaveLength(2);
      expect(mappings).toContainEqual({ tiktokSku: 'TT-001', amazonSku: 'AMZN-001' });
      expect(mappings).toContainEqual({ tiktokSku: 'TT-002', amazonSku: 'AMZN-002' });
    });
  });

  describe('configuration', () => {
    it('should update configuration', () => {
      transformer.updateConfig({
        defaultShippingSpeed: 'Priority',
        includeItemPrices: false,
      });

      const config = transformer.getConfig();

      expect(config.defaultShippingSpeed).toBe('Priority');
      expect(config.includeItemPrices).toBe(false);
    });

    it('should get current configuration', () => {
      transformer = createOrderTransformer({
        defaultShippingSpeed: 'Expedited',
        notificationEmails: ['test@example.com'],
      });

      const config = transformer.getConfig();

      expect(config.defaultShippingSpeed).toBe('Expedited');
      expect(config.notificationEmails).toEqual(['test@example.com']);
    });

    it('should preserve unmodified config values when updating', () => {
      transformer = createOrderTransformer({
        defaultShippingSpeed: 'Expedited',
        notificationEmails: ['test@example.com'],
      });

      transformer.updateConfig({
        defaultFulfillmentPolicy: 'FillAll',
      });

      const config = transformer.getConfig();

      expect(config.defaultShippingSpeed).toBe('Expedited');
      expect(config.notificationEmails).toEqual(['test@example.com']);
      expect(config.defaultFulfillmentPolicy).toBe('FillAll');
    });
  });

  describe('edge cases', () => {
    it('should handle order with no buyer message or seller note', () => {
      transformer = createOrderTransformer({
        includeOrderComment: true,
      });

      const { normalizedOrder, normalizedAddress } = createTestOrder();
      delete normalizedOrder.buyerMessage;
      delete normalizedOrder.sellerNote;

      const result = transformer.transformOrder(normalizedOrder, normalizedAddress);

      expect(result.success).toBe(true);
      expect(result.mcfOrderRequest!.displayableOrderComment).toBeUndefined();
    });

    it('should handle address without phone number', () => {
      const { normalizedOrder, normalizedAddress } = createTestOrder();
      delete normalizedAddress.phoneNumber;

      const result = transformer.transformOrder(normalizedOrder, normalizedAddress);

      expect(result.success).toBe(true);
      expect(result.mcfOrderRequest!.destinationAddress.phone).toBeUndefined();
    });

    it('should handle address without addressLine2', () => {
      const { normalizedOrder, normalizedAddress } = createTestOrder();
      delete normalizedAddress.addressLine2;

      const result = transformer.transformOrder(normalizedOrder, normalizedAddress);

      expect(result.success).toBe(true);
      expect(result.mcfOrderRequest!.destinationAddress.addressLine2).toBeUndefined();
    });

    it('should handle single item order', () => {
      const { normalizedOrder, normalizedAddress } = createTestOrder();
      normalizedOrder.items = [normalizedOrder.items[0]];

      const result = transformer.transformOrder(normalizedOrder, normalizedAddress);

      expect(result.success).toBe(true);
      expect(result.mcfOrderRequest!.items).toHaveLength(1);
    });

    it('should handle multiple items with mixed SKU mappings', () => {
      transformer = createOrderTransformer({
        skuMappings: [
          { tiktokSku: 'TT-MAPPED', amazonSku: 'AMZN-MAPPED' },
        ],
      });

      const { normalizedOrder, normalizedAddress } = createTestOrder();
      normalizedOrder.items[0].sku = 'TT-MAPPED';
      normalizedOrder.items[1].sku = 'TT-UNMAPPED';

      const result = transformer.transformOrder(normalizedOrder, normalizedAddress);

      expect(result.success).toBe(true);
      expect(result.mcfOrderRequest!.items[0].sellerSku).toBe('AMZN-MAPPED');
      expect(result.mcfOrderRequest!.items[1].sellerSku).toBe('TT-UNMAPPED');
      expect(result.warnings).toHaveLength(1);
    });
  });
});

// ============================================================
// Test Helpers
// ============================================================

/**
 * Create a complete valid test order
 */
function createTestOrder(): {
  normalizedOrder: NormalizedTikTokOrder;
  normalizedAddress: Address;
} {
  const rawOrder: TikTokOrder = {
    id: 'TTORDER123456',
    status: TikTokOrderStatus.AWAITING_SHIPMENT,
    create_time: Math.floor(Date.now() / 1000) - 3600,
    update_time: Math.floor(Date.now() / 1000),
    paid_time: Math.floor(Date.now() / 1000) - 3000,
    recipient_address: {
      recipient_name: 'John Doe',
      phone_number: '+14155551234',
      full_address: '123 Main St, San Francisco, CA 94102',
      address_line_1: '123 Main St',
      city: 'San Francisco',
      state: 'CA',
      postal_code: '94102',
      region_code: 'US',
    },
    buyer_info: {
      email: 'john.doe@example.com',
    },
    items: [
      {
        id: 'ITEM001',
        product_id: 'PROD001',
        product_name: 'Test Widget',
        sku_id: 'SKU001',
        seller_sku: 'SELLER-SKU-001',
        quantity: 2,
        sale_price: 29.99,
      },
      {
        id: 'ITEM002',
        product_id: 'PROD002',
        product_name: 'Test Gadget',
        sku_id: 'SKU002',
        seller_sku: 'SELLER-SKU-002',
        quantity: 1,
        sale_price: 49.99,
      },
    ],
    payment_info: {
      currency: 'USD',
      sub_total: 109.97,
      shipping_fee: 5.99,
      total_amount: 115.96,
    },
  };

  const normalizedOrder: NormalizedTikTokOrder = {
    id: rawOrder.id,
    status: rawOrder.status,
    createdAt: new Date(rawOrder.create_time * 1000),
    updatedAt: new Date(rawOrder.update_time * 1000),
    paidAt: new Date(rawOrder.paid_time! * 1000),

    customer: {
      name: rawOrder.recipient_address.recipient_name,
      email: rawOrder.buyer_info?.email,
      phone: rawOrder.recipient_address.phone_number,
    },

    shippingAddress: {
      name: rawOrder.recipient_address.recipient_name,
      addressLine1: rawOrder.recipient_address.address_line_1!,
      addressLine2: rawOrder.recipient_address.address_line_2,
      city: rawOrder.recipient_address.city,
      state: rawOrder.recipient_address.state,
      postalCode: rawOrder.recipient_address.postal_code,
      countryCode: rawOrder.recipient_address.region_code,
      phoneNumber: rawOrder.recipient_address.phone_number,
    },

    items: [
      {
        id: 'ITEM001',
        productId: 'PROD001',
        productName: 'Test Widget',
        sku: 'SELLER-SKU-001',
        quantity: 2,
        price: 29.99,
        totalPrice: 59.98,
      },
      {
        id: 'ITEM002',
        productId: 'PROD002',
        productName: 'Test Gadget',
        sku: 'SELLER-SKU-002',
        quantity: 1,
        price: 49.99,
        totalPrice: 49.99,
      },
    ],

    payment: {
      currency: 'USD',
      subtotal: 109.97,
      shippingFee: 5.99,
      tax: 0,
      discounts: 0,
      total: 115.96,
    },

    rawOrder,
  };

  const normalizedAddress: Address = {
    name: 'John Doe',
    addressLine1: '123 Main St',
    addressLine2: undefined,
    city: 'San Francisco',
    stateOrRegion: 'CA',
    postalCode: '94102',
    countryCode: 'US',
    phoneNumber: '+14155551234',
  };

  return { normalizedOrder, normalizedAddress };
}
