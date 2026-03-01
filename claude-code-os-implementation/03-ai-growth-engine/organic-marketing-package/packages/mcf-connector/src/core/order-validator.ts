/**
 * Order Validator - Validates TikTok orders and normalizes addresses for MCF
 *
 * Features:
 * - Validates required order fields
 * - Normalizes addresses to meet Amazon MCF requirements
 * - Checks for invalid data formats
 * - Provides clear validation error messages
 */

import type { TikTokOrder, NormalizedTikTokOrder } from '../types/tiktok-order';
import type { Address } from '../types/common';
import { ErrorCode, TikTokOrderStatus } from '../types/common';

// ============================================================
// Types
// ============================================================

export interface ValidationError {
  field: string;
  message: string;
  code: string;
}

export interface ValidationWarning {
  field: string;
  message: string;
}

export interface OrderValidationResult {
  valid: boolean;
  errors: ValidationError[];
  warnings?: ValidationWarning[];
  normalizedOrder?: NormalizedTikTokOrder;
  normalizedAddress?: Address;
}

export interface ValidatorConfig {
  strictMode?: boolean;
  maxAddressLength?: number;
  requiredPhoneNumber?: boolean;
  allowedCountries?: string[];
}

// ============================================================
// Constants
// ============================================================

const DEFAULT_VALIDATOR_CONFIG: Required<ValidatorConfig> = {
  strictMode: false,
  maxAddressLength: 180,
  requiredPhoneNumber: true,
  allowedCountries: ['US', 'CA', 'MX', 'GB', 'FR', 'DE', 'IT', 'ES', 'JP', 'AU'],
};

// Amazon MCF address field length limits
const MCF_ADDRESS_LIMITS = {
  name: 50,
  addressLine1: 180,
  addressLine2: 60,
  addressLine3: 60,
  city: 50,
  stateOrRegion: 150,
  postalCode: 20,
  countryCode: 2,
  phone: 20,
};

// Valid order statuses for fulfillment
const VALID_FULFILLMENT_STATUSES = [
  TikTokOrderStatus.AWAITING_SHIPMENT,
  TikTokOrderStatus.AWAITING_COLLECTION,
];

// US state abbreviations for normalization
const US_STATE_ABBREV: Record<string, string> = {
  alabama: 'AL',
  alaska: 'AK',
  arizona: 'AZ',
  arkansas: 'AR',
  california: 'CA',
  colorado: 'CO',
  connecticut: 'CT',
  delaware: 'DE',
  florida: 'FL',
  georgia: 'GA',
  hawaii: 'HI',
  idaho: 'ID',
  illinois: 'IL',
  indiana: 'IN',
  iowa: 'IA',
  kansas: 'KS',
  kentucky: 'KY',
  louisiana: 'LA',
  maine: 'ME',
  maryland: 'MD',
  massachusetts: 'MA',
  michigan: 'MI',
  minnesota: 'MN',
  mississippi: 'MS',
  missouri: 'MO',
  montana: 'MT',
  nebraska: 'NE',
  nevada: 'NV',
  'new hampshire': 'NH',
  'new jersey': 'NJ',
  'new mexico': 'NM',
  'new york': 'NY',
  'north carolina': 'NC',
  'north dakota': 'ND',
  ohio: 'OH',
  oklahoma: 'OK',
  oregon: 'OR',
  pennsylvania: 'PA',
  'rhode island': 'RI',
  'south carolina': 'SC',
  'south dakota': 'SD',
  tennessee: 'TN',
  texas: 'TX',
  utah: 'UT',
  vermont: 'VT',
  virginia: 'VA',
  washington: 'WA',
  'west virginia': 'WV',
  wisconsin: 'WI',
  wyoming: 'WY',
};

// ============================================================
// Helper Functions
// ============================================================

/**
 * Normalize whitespace in a string
 */
function normalizeWhitespace(str: string): string {
  return str.trim().replace(/\s+/g, ' ');
}

/**
 * Truncate string to max length
 */
function truncate(str: string, maxLength: number): string {
  if (str.length <= maxLength) {
    return str;
  }
  return str.substring(0, maxLength);
}

/**
 * Normalize phone number (remove non-digit characters)
 */
function normalizePhoneNumber(phone: string): string {
  const digits = phone.replace(/\D/g, '');

  // If it starts with 1 (US/Canada country code) and is 11 digits, keep it
  if (digits.length === 11 && digits.startsWith('1')) {
    return `+${digits}`;
  }

  // If 10 digits (US/Canada without country code), add +1
  if (digits.length === 10) {
    return `+1${digits}`;
  }

  // Otherwise just return with + prefix if not already there
  if (digits.length > 0 && !phone.startsWith('+')) {
    return `+${digits}`;
  }

  return digits;
}

/**
 * Normalize US state names to 2-letter abbreviations
 */
function normalizeState(state: string): string {
  const normalized = state.trim().toLowerCase();

  // If already 2 letters, uppercase and return
  if (normalized.length === 2) {
    return normalized.toUpperCase();
  }

  // Try to find abbreviation for full state name
  return US_STATE_ABBREV[normalized] || state.trim();
}

/**
 * Normalize country code to ISO 3166-1 alpha-2
 */
function normalizeCountryCode(countryCode: string): string {
  return countryCode.trim().toUpperCase();
}

/**
 * Validate postal code format
 */
function isValidPostalCode(postalCode: string, countryCode: string): boolean {
  const normalized = postalCode.trim();

  if (normalized.length === 0) {
    return false;
  }

  // US ZIP codes: 5 digits or 5+4 format
  if (countryCode === 'US') {
    return /^\d{5}(-\d{4})?$/.test(normalized);
  }

  // Canadian postal codes: A1A 1A1 format
  if (countryCode === 'CA') {
    return /^[A-Z]\d[A-Z]\s?\d[A-Z]\d$/i.test(normalized);
  }

  // UK postal codes: Complex format
  if (countryCode === 'GB') {
    return /^[A-Z]{1,2}\d{1,2}[A-Z]?\s?\d[A-Z]{2}$/i.test(normalized);
  }

  // For other countries, just check it's not empty
  return normalized.length > 0;
}

/**
 * Parse TikTok address to extract structured fields
 */
function parseAddress(tiktokAddress: TikTokOrder['recipient_address']): {
  addressLine1: string;
  addressLine2?: string;
  city?: string;
  state?: string;
} {
  // Use provided structured fields if available
  if (tiktokAddress.address_line_1) {
    return {
      addressLine1: tiktokAddress.address_line_1,
      addressLine2: tiktokAddress.address_line_2 || undefined,
      city: tiktokAddress.city || undefined,
      state: tiktokAddress.state || undefined,
    };
  }

  // Otherwise try to parse full_address
  const fullAddress = tiktokAddress.full_address.trim();
  const lines = fullAddress.split('\n').map(line => line.trim()).filter(line => line.length > 0);

  if (lines.length === 0) {
    return {
      addressLine1: fullAddress,
    };
  }

  // First line is always address line 1
  const addressLine1 = lines[0];

  // If multiple lines, second line might be address line 2 or city/state
  const addressLine2 = lines.length > 1 ? lines[1] : undefined;

  return {
    addressLine1,
    addressLine2,
    city: tiktokAddress.city,
    state: tiktokAddress.state,
  };
}

// ============================================================
// OrderValidator Class
// ============================================================

/**
 * OrderValidator validates TikTok orders and normalizes addresses for Amazon MCF
 */
export class OrderValidator {
  private config: Required<ValidatorConfig>;

  constructor(config?: ValidatorConfig) {
    this.config = { ...DEFAULT_VALIDATOR_CONFIG, ...config };
  }

  /**
   * Validate a TikTok order and normalize data for MCF
   */
  validateOrder(order: TikTokOrder): OrderValidationResult {
    const errors: ValidationError[] = [];
    const warnings: ValidationWarning[] = [];

    // Validate order ID
    if (!order.id || order.id.trim().length === 0) {
      errors.push({
        field: 'id',
        message: 'Order ID is required',
        code: ErrorCode.INVALID_ORDER_DATA,
      });
    }

    // Validate order status
    if (!VALID_FULFILLMENT_STATUSES.includes(order.status)) {
      errors.push({
        field: 'status',
        message: `Order status ${order.status} is not eligible for fulfillment. Must be AWAITING_SHIPMENT or AWAITING_COLLECTION.`,
        code: ErrorCode.INVALID_ORDER_DATA,
      });
    }

    // Validate order has items
    if (!order.items || order.items.length === 0) {
      errors.push({
        field: 'items',
        message: 'Order must have at least one item',
        code: ErrorCode.INVALID_ORDER_DATA,
      });
    } else {
      // Validate each item
      order.items.forEach((item, index) => {
        if (!item.sku_id || item.sku_id.trim().length === 0) {
          errors.push({
            field: `items[${index}].sku_id`,
            message: 'Item SKU ID is required',
            code: ErrorCode.INVALID_PRODUCT_SKU,
          });
        }

        if (!item.seller_sku || item.seller_sku.trim().length === 0) {
          warnings.push({
            field: `items[${index}].seller_sku`,
            message: 'Item seller SKU is missing - using sku_id as fallback',
          });
        }

        if (item.quantity <= 0) {
          errors.push({
            field: `items[${index}].quantity`,
            message: 'Item quantity must be positive',
            code: ErrorCode.INVALID_ORDER_DATA,
          });
        }
      });
    }

    // Validate address
    const addressValidation = this.validateAddress(order.recipient_address);
    errors.push(...addressValidation.errors);
    if (addressValidation.warnings) {
      warnings.push(...addressValidation.warnings);
    }

    // If validation failed, return early
    if (errors.length > 0) {
      return {
        valid: false,
        errors,
        warnings: warnings.length > 0 ? warnings : undefined,
      };
    }

    // Normalize the order
    const normalizedOrder = this.normalizeOrder(order);
    const normalizedAddress = addressValidation.normalizedAddress!;

    return {
      valid: true,
      errors: [],
      warnings: warnings.length > 0 ? warnings : undefined,
      normalizedOrder,
      normalizedAddress,
    };
  }

  /**
   * Validate and normalize address for Amazon MCF
   */
  validateAddress(address: TikTokOrder['recipient_address']): {
    errors: ValidationError[];
    warnings?: ValidationWarning[];
    normalizedAddress?: Address;
  } {
    const errors: ValidationError[] = [];
    const warnings: ValidationWarning[] = [];

    // Validate recipient name
    if (!address.recipient_name || address.recipient_name.trim().length === 0) {
      errors.push({
        field: 'recipient_address.recipient_name',
        message: 'Recipient name is required',
        code: ErrorCode.INVALID_ADDRESS,
      });
    }

    // Validate phone number
    if (this.config.requiredPhoneNumber && (!address.phone_number || address.phone_number.trim().length === 0)) {
      errors.push({
        field: 'recipient_address.phone_number',
        message: 'Phone number is required',
        code: ErrorCode.INVALID_ADDRESS,
      });
    }

    // Validate postal code
    if (!address.postal_code || address.postal_code.trim().length === 0) {
      errors.push({
        field: 'recipient_address.postal_code',
        message: 'Postal code is required',
        code: ErrorCode.INVALID_ADDRESS,
      });
    }

    // Validate country code
    if (!address.region_code || address.region_code.trim().length === 0) {
      errors.push({
        field: 'recipient_address.region_code',
        message: 'Country code is required',
        code: ErrorCode.INVALID_ADDRESS,
      });
    } else {
      const countryCode = normalizeCountryCode(address.region_code);

      // Check if country is allowed
      if (this.config.allowedCountries.length > 0 && !this.config.allowedCountries.includes(countryCode)) {
        errors.push({
          field: 'recipient_address.region_code',
          message: `Country ${countryCode} is not supported for MCF fulfillment`,
          code: ErrorCode.INVALID_ADDRESS,
        });
      }

      // Validate postal code format
      if (address.postal_code && !isValidPostalCode(address.postal_code, countryCode)) {
        if (this.config.strictMode) {
          errors.push({
            field: 'recipient_address.postal_code',
            message: `Postal code ${address.postal_code} is not valid for country ${countryCode}`,
            code: ErrorCode.INVALID_ADDRESS,
          });
        } else {
          warnings.push({
            field: 'recipient_address.postal_code',
            message: `Postal code ${address.postal_code} may not be valid for country ${countryCode}`,
          });
        }
      }
    }

    // Validate address has some content
    if (!address.full_address && !address.address_line_1) {
      errors.push({
        field: 'recipient_address.full_address',
        message: 'Address line 1 is required',
        code: ErrorCode.INVALID_ADDRESS,
      });
    }

    // If validation failed, return early
    if (errors.length > 0) {
      return {
        errors,
        warnings: warnings.length > 0 ? warnings : undefined,
      };
    }

    // Normalize the address
    const normalizedAddress = this.normalizeAddress(address);

    return {
      errors: [],
      warnings: warnings.length > 0 ? warnings : undefined,
      normalizedAddress,
    };
  }

  /**
   * Normalize address to meet Amazon MCF requirements
   */
  private normalizeAddress(tiktokAddress: TikTokOrder['recipient_address']): Address {
    const countryCode = normalizeCountryCode(tiktokAddress.region_code);
    const parsedAddress = parseAddress(tiktokAddress);

    // Normalize name (truncate if too long)
    const name = truncate(normalizeWhitespace(tiktokAddress.recipient_name), MCF_ADDRESS_LIMITS.name);

    // Normalize address lines
    const addressLine1 = truncate(
      normalizeWhitespace(parsedAddress.addressLine1),
      MCF_ADDRESS_LIMITS.addressLine1
    );

    const addressLine2 = parsedAddress.addressLine2
      ? truncate(normalizeWhitespace(parsedAddress.addressLine2), MCF_ADDRESS_LIMITS.addressLine2)
      : undefined;

    // Normalize city
    const city = parsedAddress.city
      ? truncate(normalizeWhitespace(parsedAddress.city), MCF_ADDRESS_LIMITS.city)
      : tiktokAddress.city
      ? truncate(normalizeWhitespace(tiktokAddress.city), MCF_ADDRESS_LIMITS.city)
      : '';

    // Normalize state/region
    const state = parsedAddress.state || tiktokAddress.state || '';
    const stateOrRegion = countryCode === 'US'
      ? normalizeState(state)
      : truncate(normalizeWhitespace(state), MCF_ADDRESS_LIMITS.stateOrRegion);

    // Normalize postal code
    const postalCode = truncate(
      normalizeWhitespace(tiktokAddress.postal_code),
      MCF_ADDRESS_LIMITS.postalCode
    );

    // Normalize phone number
    const phoneNumber = tiktokAddress.phone_number
      ? truncate(normalizePhoneNumber(tiktokAddress.phone_number), MCF_ADDRESS_LIMITS.phone)
      : undefined;

    return {
      name,
      addressLine1,
      addressLine2,
      city,
      stateOrRegion,
      postalCode,
      countryCode,
      phoneNumber,
    };
  }

  /**
   * Normalize TikTok order to internal format
   */
  private normalizeOrder(order: TikTokOrder): NormalizedTikTokOrder {
    return {
      id: order.id,
      status: order.status,
      createdAt: new Date(order.create_time * 1000),
      updatedAt: new Date(order.update_time * 1000),
      paidAt: order.paid_time ? new Date(order.paid_time * 1000) : undefined,

      customer: {
        name: order.recipient_address.recipient_name,
        email: order.buyer_info?.email,
        phone: order.recipient_address.phone_number,
      },

      shippingAddress: {
        name: order.recipient_address.recipient_name,
        addressLine1: order.recipient_address.address_line_1 || order.recipient_address.full_address,
        addressLine2: order.recipient_address.address_line_2,
        city: order.recipient_address.city,
        state: order.recipient_address.state,
        postalCode: order.recipient_address.postal_code,
        countryCode: order.recipient_address.region_code,
        phoneNumber: order.recipient_address.phone_number,
      },

      items: order.items.map(item => ({
        id: item.id,
        productId: item.product_id,
        productName: item.product_name,
        sku: item.seller_sku || item.sku_id,
        quantity: item.quantity,
        price: item.sale_price,
        totalPrice: item.sale_price * item.quantity,
      })),

      payment: {
        currency: order.payment_info.currency,
        subtotal: order.payment_info.sub_total,
        shippingFee: order.payment_info.shipping_fee,
        tax: order.payment_info.tax || 0,
        discounts: (order.payment_info.seller_discount || 0) + (order.payment_info.platform_discount || 0),
        total: order.payment_info.total_amount,
      },

      fulfillmentType: order.fulfillment_type,

      packages: order.packages?.map(pkg => ({
        id: pkg.id,
        trackingNumber: pkg.tracking_number,
        carrier: pkg.shipping_provider_name,
        items: pkg.items.map(item => ({
          orderItemId: item.order_item_id,
          quantity: item.quantity,
        })),
      })),

      buyerMessage: order.buyer_message,
      sellerNote: order.seller_note,

      rawOrder: order,
    };
  }
}

/**
 * Create a new order validator instance
 */
export function createOrderValidator(config?: ValidatorConfig): OrderValidator {
  return new OrderValidator(config);
}
