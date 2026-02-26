/**
 * Order Validator Tests
 */

import { OrderValidator, createOrderValidator } from '../order-validator';
import { TikTokOrderStatus, ErrorCode } from '../../types/common';
import type { TikTokOrder } from '../../types/tiktok-order';

describe('OrderValidator', () => {
  let validator: OrderValidator;

  beforeEach(() => {
    validator = createOrderValidator();
  });

  describe('validateOrder', () => {
    it('should validate a complete valid order', () => {
      const order: TikTokOrder = createValidOrder();
      const result = validator.validateOrder(order);

      expect(result.valid).toBe(true);
      expect(result.errors).toHaveLength(0);
      expect(result.normalizedOrder).toBeDefined();
      expect(result.normalizedAddress).toBeDefined();
    });

    it('should reject order without ID', () => {
      const order = createValidOrder();
      order.id = '';

      const result = validator.validateOrder(order);

      expect(result.valid).toBe(false);
      expect(result.errors).toContainEqual(
        expect.objectContaining({
          field: 'id',
          code: ErrorCode.INVALID_ORDER_DATA,
        })
      );
    });

    it('should reject order with invalid status', () => {
      const order = createValidOrder();
      order.status = TikTokOrderStatus.UNPAID;

      const result = validator.validateOrder(order);

      expect(result.valid).toBe(false);
      expect(result.errors).toContainEqual(
        expect.objectContaining({
          field: 'status',
          code: ErrorCode.INVALID_ORDER_DATA,
        })
      );
    });

    it('should accept order with AWAITING_SHIPMENT status', () => {
      const order = createValidOrder();
      order.status = TikTokOrderStatus.AWAITING_SHIPMENT;

      const result = validator.validateOrder(order);

      expect(result.valid).toBe(true);
    });

    it('should accept order with AWAITING_COLLECTION status', () => {
      const order = createValidOrder();
      order.status = TikTokOrderStatus.AWAITING_COLLECTION;

      const result = validator.validateOrder(order);

      expect(result.valid).toBe(true);
    });

    it('should reject order without items', () => {
      const order = createValidOrder();
      order.items = [];

      const result = validator.validateOrder(order);

      expect(result.valid).toBe(false);
      expect(result.errors).toContainEqual(
        expect.objectContaining({
          field: 'items',
          code: ErrorCode.INVALID_ORDER_DATA,
        })
      );
    });

    it('should reject order with item missing SKU', () => {
      const order = createValidOrder();
      order.items[0].sku_id = '';

      const result = validator.validateOrder(order);

      expect(result.valid).toBe(false);
      expect(result.errors).toContainEqual(
        expect.objectContaining({
          field: 'items[0].sku_id',
          code: ErrorCode.INVALID_PRODUCT_SKU,
        })
      );
    });

    it('should warn when item is missing seller SKU', () => {
      const order = createValidOrder();
      order.items[0].seller_sku = undefined;

      const result = validator.validateOrder(order);

      expect(result.valid).toBe(true);
      expect(result.warnings).toContainEqual(
        expect.objectContaining({
          field: 'items[0].seller_sku',
        })
      );
    });

    it('should reject order with zero quantity item', () => {
      const order = createValidOrder();
      order.items[0].quantity = 0;

      const result = validator.validateOrder(order);

      expect(result.valid).toBe(false);
      expect(result.errors).toContainEqual(
        expect.objectContaining({
          field: 'items[0].quantity',
          code: ErrorCode.INVALID_ORDER_DATA,
        })
      );
    });

    it('should reject order with negative quantity item', () => {
      const order = createValidOrder();
      order.items[0].quantity = -5;

      const result = validator.validateOrder(order);

      expect(result.valid).toBe(false);
      expect(result.errors).toContainEqual(
        expect.objectContaining({
          field: 'items[0].quantity',
          code: ErrorCode.INVALID_ORDER_DATA,
        })
      );
    });

    it('should normalize order data correctly', () => {
      const order = createValidOrder();
      const result = validator.validateOrder(order);

      expect(result.valid).toBe(true);
      expect(result.normalizedOrder).toMatchObject({
        id: order.id,
        status: order.status,
        customer: {
          name: order.recipient_address.recipient_name,
          phone: order.recipient_address.phone_number,
        },
        items: expect.arrayContaining([
          expect.objectContaining({
            sku: order.items[0].seller_sku,
            quantity: order.items[0].quantity,
          }),
        ]),
      });
    });

    it('should handle multiple validation errors', () => {
      const order = createValidOrder();
      order.id = '';
      order.status = TikTokOrderStatus.CANCELLED;
      order.items = [];

      const result = validator.validateOrder(order);

      expect(result.valid).toBe(false);
      expect(result.errors.length).toBeGreaterThanOrEqual(3);
    });
  });

  describe('validateAddress', () => {
    it('should validate a complete valid address', () => {
      const order = createValidOrder();
      const result = validator.validateAddress(order.recipient_address);

      expect(result.errors).toHaveLength(0);
      expect(result.normalizedAddress).toBeDefined();
    });

    it('should reject address without recipient name', () => {
      const order = createValidOrder();
      order.recipient_address.recipient_name = '';

      const result = validator.validateAddress(order.recipient_address);

      expect(result.errors).toContainEqual(
        expect.objectContaining({
          field: 'recipient_address.recipient_name',
          code: ErrorCode.INVALID_ADDRESS,
        })
      );
    });

    it('should reject address without phone number when required', () => {
      const order = createValidOrder();
      order.recipient_address.phone_number = '';

      const result = validator.validateAddress(order.recipient_address);

      expect(result.errors).toContainEqual(
        expect.objectContaining({
          field: 'recipient_address.phone_number',
          code: ErrorCode.INVALID_ADDRESS,
        })
      );
    });

    it('should allow missing phone number when not required', () => {
      const validatorNoPhone = createOrderValidator({ requiredPhoneNumber: false });
      const order = createValidOrder();
      order.recipient_address.phone_number = '';

      const result = validatorNoPhone.validateAddress(order.recipient_address);

      expect(result.errors).not.toContainEqual(
        expect.objectContaining({
          field: 'recipient_address.phone_number',
        })
      );
    });

    it('should reject address without postal code', () => {
      const order = createValidOrder();
      order.recipient_address.postal_code = '';

      const result = validator.validateAddress(order.recipient_address);

      expect(result.errors).toContainEqual(
        expect.objectContaining({
          field: 'recipient_address.postal_code',
          code: ErrorCode.INVALID_ADDRESS,
        })
      );
    });

    it('should reject address without country code', () => {
      const order = createValidOrder();
      order.recipient_address.region_code = '';

      const result = validator.validateAddress(order.recipient_address);

      expect(result.errors).toContainEqual(
        expect.objectContaining({
          field: 'recipient_address.region_code',
          code: ErrorCode.INVALID_ADDRESS,
        })
      );
    });

    it('should reject unsupported country when allowedCountries is set', () => {
      const order = createValidOrder();
      order.recipient_address.region_code = 'ZZ';

      const result = validator.validateAddress(order.recipient_address);

      expect(result.errors).toContainEqual(
        expect.objectContaining({
          field: 'recipient_address.region_code',
          code: ErrorCode.INVALID_ADDRESS,
        })
      );
    });

    it('should reject address without address line', () => {
      const order = createValidOrder();
      order.recipient_address.full_address = '';
      order.recipient_address.address_line_1 = undefined;

      const result = validator.validateAddress(order.recipient_address);

      expect(result.errors).toContainEqual(
        expect.objectContaining({
          field: 'recipient_address.full_address',
          code: ErrorCode.INVALID_ADDRESS,
        })
      );
    });

    it('should validate US postal code format', () => {
      const order = createValidOrder();
      order.recipient_address.region_code = 'US';
      order.recipient_address.postal_code = '12345';

      const result = validator.validateAddress(order.recipient_address);

      expect(result.errors).not.toContainEqual(
        expect.objectContaining({
          field: 'recipient_address.postal_code',
        })
      );
    });

    it('should validate US ZIP+4 format', () => {
      const order = createValidOrder();
      order.recipient_address.region_code = 'US';
      order.recipient_address.postal_code = '12345-6789';

      const result = validator.validateAddress(order.recipient_address);

      expect(result.errors).not.toContainEqual(
        expect.objectContaining({
          field: 'recipient_address.postal_code',
        })
      );
    });

    it('should warn about invalid US postal code in non-strict mode', () => {
      const order = createValidOrder();
      order.recipient_address.region_code = 'US';
      order.recipient_address.postal_code = 'INVALID';

      const result = validator.validateAddress(order.recipient_address);

      expect(result.warnings).toContainEqual(
        expect.objectContaining({
          field: 'recipient_address.postal_code',
        })
      );
    });

    it('should reject invalid US postal code in strict mode', () => {
      const strictValidator = createOrderValidator({ strictMode: true });
      const order = createValidOrder();
      order.recipient_address.region_code = 'US';
      order.recipient_address.postal_code = 'INVALID';

      const result = strictValidator.validateAddress(order.recipient_address);

      expect(result.errors).toContainEqual(
        expect.objectContaining({
          field: 'recipient_address.postal_code',
          code: ErrorCode.INVALID_ADDRESS,
        })
      );
    });

    it('should validate Canadian postal code format', () => {
      const order = createValidOrder();
      order.recipient_address.region_code = 'CA';
      order.recipient_address.postal_code = 'K1A 0B1';

      const result = validator.validateAddress(order.recipient_address);

      expect(result.errors).not.toContainEqual(
        expect.objectContaining({
          field: 'recipient_address.postal_code',
        })
      );
    });

    it('should validate UK postal code format', () => {
      const order = createValidOrder();
      order.recipient_address.region_code = 'GB';
      order.recipient_address.postal_code = 'SW1A 1AA';

      const result = validator.validateAddress(order.recipient_address);

      expect(result.errors).not.toContainEqual(
        expect.objectContaining({
          field: 'recipient_address.postal_code',
        })
      );
    });
  });

  describe('address normalization', () => {
    it('should normalize address with structured fields', () => {
      const order = createValidOrder();
      const result = validator.validateOrder(order);

      expect(result.valid).toBe(true);
      expect(result.normalizedAddress).toMatchObject({
        name: 'John Doe',
        addressLine1: '123 Main St',
        addressLine2: 'Apt 4B',
        city: 'San Francisco',
        stateOrRegion: 'CA',
        postalCode: '94102',
        countryCode: 'US',
        phoneNumber: expect.stringMatching(/^\+1/),
      });
    });

    it('should normalize whitespace in address fields', () => {
      const order = createValidOrder();
      order.recipient_address.recipient_name = '  John   Doe  ';
      order.recipient_address.address_line_1 = '  123   Main   St  ';

      const result = validator.validateOrder(order);

      expect(result.valid).toBe(true);
      expect(result.normalizedAddress?.name).toBe('John Doe');
      expect(result.normalizedAddress?.addressLine1).toBe('123 Main St');
    });

    it('should truncate long address fields to MCF limits', () => {
      const order = createValidOrder();
      order.recipient_address.recipient_name = 'A'.repeat(100);
      order.recipient_address.address_line_1 = 'B'.repeat(200);

      const result = validator.validateOrder(order);

      expect(result.valid).toBe(true);
      expect(result.normalizedAddress?.name.length).toBeLessThanOrEqual(50);
      expect(result.normalizedAddress?.addressLine1.length).toBeLessThanOrEqual(180);
    });

    it('should normalize US state name to abbreviation', () => {
      const order = createValidOrder();
      order.recipient_address.region_code = 'US';
      order.recipient_address.state = 'California';

      const result = validator.validateOrder(order);

      expect(result.valid).toBe(true);
      expect(result.normalizedAddress?.stateOrRegion).toBe('CA');
    });

    it('should normalize lowercase state name', () => {
      const order = createValidOrder();
      order.recipient_address.region_code = 'US';
      order.recipient_address.state = 'new york';

      const result = validator.validateOrder(order);

      expect(result.valid).toBe(true);
      expect(result.normalizedAddress?.stateOrRegion).toBe('NY');
    });

    it('should keep existing state abbreviation', () => {
      const order = createValidOrder();
      order.recipient_address.region_code = 'US';
      order.recipient_address.state = 'ca';

      const result = validator.validateOrder(order);

      expect(result.valid).toBe(true);
      expect(result.normalizedAddress?.stateOrRegion).toBe('CA');
    });

    it('should normalize phone number to E.164 format', () => {
      const order = createValidOrder();
      order.recipient_address.phone_number = '(555) 123-4567';

      const result = validator.validateOrder(order);

      expect(result.valid).toBe(true);
      expect(result.normalizedAddress?.phoneNumber).toBe('+15551234567');
    });

    it('should handle 10-digit phone number', () => {
      const order = createValidOrder();
      order.recipient_address.phone_number = '5551234567';

      const result = validator.validateOrder(order);

      expect(result.valid).toBe(true);
      expect(result.normalizedAddress?.phoneNumber).toBe('+15551234567');
    });

    it('should handle 11-digit phone number with country code', () => {
      const order = createValidOrder();
      order.recipient_address.phone_number = '15551234567';

      const result = validator.validateOrder(order);

      expect(result.valid).toBe(true);
      expect(result.normalizedAddress?.phoneNumber).toBe('+15551234567');
    });

    it('should normalize country code to uppercase', () => {
      const order = createValidOrder();
      order.recipient_address.region_code = 'us';

      const result = validator.validateOrder(order);

      expect(result.valid).toBe(true);
      expect(result.normalizedAddress?.countryCode).toBe('US');
    });

    it('should use full_address when structured fields are missing', () => {
      const order = createValidOrder();
      order.recipient_address.address_line_1 = undefined;
      order.recipient_address.address_line_2 = undefined;
      order.recipient_address.full_address = '456 Oak Avenue\nSuite 200\nNew York, NY 10001';

      const result = validator.validateOrder(order);

      expect(result.valid).toBe(true);
      expect(result.normalizedAddress?.addressLine1).toBe('456 Oak Avenue');
      expect(result.normalizedAddress?.addressLine2).toBe('Suite 200');
    });

    it('should prefer structured fields over full_address', () => {
      const order = createValidOrder();
      order.recipient_address.address_line_1 = '789 Pine St';
      order.recipient_address.full_address = '456 Oak Avenue';

      const result = validator.validateOrder(order);

      expect(result.valid).toBe(true);
      expect(result.normalizedAddress?.addressLine1).toBe('789 Pine St');
    });
  });

  describe('configuration options', () => {
    it('should respect strictMode configuration', () => {
      const strictValidator = createOrderValidator({ strictMode: true });
      const order = createValidOrder();
      order.recipient_address.postal_code = 'INVALID';

      const result = strictValidator.validateAddress(order.recipient_address);

      expect(result.errors.length).toBeGreaterThan(0);
    });

    it('should respect requiredPhoneNumber configuration', () => {
      const noPhoneValidator = createOrderValidator({ requiredPhoneNumber: false });
      const order = createValidOrder();
      order.recipient_address.phone_number = '';

      const result = noPhoneValidator.validateAddress(order.recipient_address);

      expect(result.errors).not.toContainEqual(
        expect.objectContaining({
          field: 'recipient_address.phone_number',
        })
      );
    });

    it('should respect allowedCountries configuration', () => {
      const usOnlyValidator = createOrderValidator({ allowedCountries: ['US'] });
      const order = createValidOrder();
      order.recipient_address.region_code = 'CA';

      const result = usOnlyValidator.validateAddress(order.recipient_address);

      expect(result.errors).toContainEqual(
        expect.objectContaining({
          field: 'recipient_address.region_code',
        })
      );
    });
  });
});

// ============================================================
// Test Helpers
// ============================================================

function createValidOrder(): TikTokOrder {
  return {
    id: 'TT123456789',
    status: TikTokOrderStatus.AWAITING_SHIPMENT,
    create_time: Math.floor(Date.now() / 1000) - 3600,
    update_time: Math.floor(Date.now() / 1000),
    paid_time: Math.floor(Date.now() / 1000) - 3000,
    payment_info: {
      currency: 'USD',
      sub_total: 29.99,
      shipping_fee: 5.99,
      seller_discount: 0,
      platform_discount: 0,
      tax: 2.40,
      total_amount: 38.38,
    },
    recipient_address: {
      recipient_name: 'John Doe',
      phone_number: '+15551234567',
      full_address: '123 Main St, Apt 4B, San Francisco, CA 94102',
      address_line_1: '123 Main St',
      address_line_2: 'Apt 4B',
      city: 'San Francisco',
      state: 'CA',
      postal_code: '94102',
      region_code: 'US',
    },
    items: [
      {
        id: 'item1',
        product_id: 'prod123',
        product_name: 'Test Product',
        sku_id: 'SKU123',
        seller_sku: 'MY-SKU-123',
        quantity: 2,
        sale_price: 14.995,
        original_price: 19.99,
      },
    ],
    buyer_info: {
      email: 'john.doe@example.com',
    },
  };
}
