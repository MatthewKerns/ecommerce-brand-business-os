/**
 * Amazon MCF Order Types - Multi-Channel Fulfillment Order Data Models
 *
 * Type definitions and Zod validation schemas for Amazon MCF fulfillment orders.
 * Based on Amazon Selling Partner API (SP-API) Fulfillment Outbound API.
 *
 * Zod schemas provide runtime validation when sending/receiving data from Amazon MCF API.
 * TypeScript types are inferred from schemas for compile-time type safety.
 */

import { z } from 'zod';
import { MCFFulfillmentStatus, ShipmentCarrier } from './common';

// ============================================================
// Zod Schemas
// ============================================================

/**
 * Amazon MCF destination address schema
 */
export const MCFAddressSchema = z.object({
  name: z.string().max(50),
  addressLine1: z.string().max(180),
  addressLine2: z.string().max(60).optional(),
  addressLine3: z.string().max(60).optional(),
  city: z.string().max(50).optional(),
  districtOrCounty: z.string().max(150).optional(),
  stateOrRegion: z.string().max(150),
  postalCode: z.string().max(20),
  countryCode: z.string().length(2), // ISO 3166-1 alpha-2
  phone: z.string().max(20).optional(),
  email: z.string().email().optional(),
});

/**
 * Amazon MCF fulfillment order item schema
 */
export const MCFOrderItemSchema = z.object({
  sellerSku: z.string().max(50),
  sellerFulfillmentOrderItemId: z.string().max(50),
  quantity: z.number().int().positive(),
  giftMessage: z.string().max(512).optional(),
  displayableComment: z.string().max(250).optional(),
  fulfillmentNetworkSku: z.string().optional(), // Assigned by Amazon
  orderItemDisposition: z.string().optional(),
  perUnitDeclaredValue: z
    .object({
      currencyCode: z.string().length(3), // ISO 4217
      value: z.number().nonnegative(),
    })
    .optional(),
  perUnitPrice: z
    .object({
      currencyCode: z.string().length(3),
      value: z.number().nonnegative(),
    })
    .optional(),
  perUnitTax: z
    .object({
      currencyCode: z.string().length(3),
      value: z.number().nonnegative(),
    })
    .optional(),
});

/**
 * Amazon MCF notification email list schema
 */
export const MCFNotificationEmailListSchema = z.array(z.string().email()).optional();

/**
 * Amazon MCF shipping speed category schema
 */
export const MCFShippingSpeedCategorySchema = z.enum([
  'Standard',
  'Expedited',
  'Priority',
  'ScheduledDelivery',
]);

/**
 * Amazon MCF fulfillment policy schema
 */
export const MCFFulfillmentPolicySchema = z.enum([
  'FillOrKill', // All items must be available or order fails
  'FillAll', // Fulfill all available items
  'FillAllAvailable', // Create multiple shipments if needed
]);

/**
 * Amazon MCF fulfillment action schema
 */
export const MCFFulfillmentActionSchema = z.enum([
  'Ship', // Ship the order immediately
  'Hold', // Hold the order for future shipment
]);

/**
 * Amazon MCF COD (Cash on Delivery) settings schema
 */
export const MCFCODSettingsSchema = z
  .object({
    isCodRequired: z.boolean(),
    codCharge: z
      .object({
        currencyCode: z.string().length(3),
        value: z.number().nonnegative(),
      })
      .optional(),
    codChargeTax: z
      .object({
        currencyCode: z.string().length(3),
        value: z.number().nonnegative(),
      })
      .optional(),
    shippingCharge: z
      .object({
        currencyCode: z.string().length(3),
        value: z.number().nonnegative(),
      })
      .optional(),
    shippingChargeTax: z
      .object({
        currencyCode: z.string().length(3),
        value: z.number().nonnegative(),
      })
      .optional(),
  })
  .optional();

/**
 * Amazon MCF delivery window schema
 */
export const MCFDeliveryWindowSchema = z
  .object({
    startDate: z.string(), // ISO 8601 date-time
    endDate: z.string(), // ISO 8601 date-time
  })
  .optional();

/**
 * Amazon MCF feature settings schema
 */
export const MCFFeatureSettingsSchema = z
  .object({
    featureName: z.string(),
    featureFulfillmentPolicy: z.enum(['Required', 'NotRequired']),
  })
  .optional();

/**
 * Complete Amazon MCF fulfillment order creation request schema
 */
export const MCFFulfillmentOrderRequestSchema = z.object({
  marketplaceId: z.string().optional(),
  sellerFulfillmentOrderId: z.string().max(40),
  displayableOrderId: z.string().max(40),
  displayableOrderDate: z.string(), // ISO 8601 date-time
  displayableOrderComment: z.string().max(1000).optional(),
  shippingSpeedCategory: MCFShippingSpeedCategorySchema,
  deliveryWindow: MCFDeliveryWindowSchema,
  destinationAddress: MCFAddressSchema,
  fulfillmentAction: MCFFulfillmentActionSchema.optional(),
  fulfillmentPolicy: MCFFulfillmentPolicySchema.optional(),
  codSettings: MCFCODSettingsSchema,
  shipFromCountryCode: z.string().length(2).optional(),
  notificationEmails: MCFNotificationEmailListSchema,
  featureConstraints: z.array(MCFFeatureSettingsSchema).optional(),
  items: z.array(MCFOrderItemSchema).min(1),
});

/**
 * Amazon MCF fulfillment order response schema
 */
export const MCFFulfillmentOrderSchema = z.object({
  sellerFulfillmentOrderId: z.string(),
  marketplaceId: z.string(),
  displayableOrderId: z.string(),
  displayableOrderDate: z.string(),
  displayableOrderComment: z.string().optional(),
  shippingSpeedCategory: MCFShippingSpeedCategorySchema,
  deliveryWindow: MCFDeliveryWindowSchema,
  destinationAddress: MCFAddressSchema,
  fulfillmentAction: MCFFulfillmentActionSchema.optional(),
  fulfillmentPolicy: MCFFulfillmentPolicySchema.optional(),
  codSettings: MCFCODSettingsSchema,
  receivedDate: z.string().optional(),
  fulfillmentOrderStatus: z.nativeEnum(MCFFulfillmentStatus),
  statusUpdatedDate: z.string().optional(),
  notificationEmails: MCFNotificationEmailListSchema,
  featureConstraints: z.array(MCFFeatureSettingsSchema).optional(),
});

/**
 * Amazon MCF fulfillment shipment item schema
 */
export const MCFShipmentItemSchema = z.object({
  sellerSku: z.string(),
  sellerFulfillmentOrderItemId: z.string(),
  quantity: z.number().int().nonnegative(),
  packageNumber: z.number().int().positive().optional(),
});

/**
 * Amazon MCF fulfillment shipment package schema
 */
export const MCFShipmentPackageSchema = z.object({
  packageNumber: z.number().int().positive(),
  carrierCode: z.string(),
  trackingNumber: z.string().optional(),
  estimatedArrivalDate: z.string().optional(), // ISO 8601 date-time
});

/**
 * Amazon MCF fulfillment shipment schema
 */
export const MCFShipmentSchema = z.object({
  amazonShipmentId: z.string(),
  fulfillmentCenterId: z.string(),
  fulfillmentShipmentStatus: z.enum([
    'PENDING',
    'SHIPPED',
    'CANCELLED_BY_FULFILLER',
    'CANCELLED_BY_SELLER',
  ]),
  shippingDate: z.string().optional(), // ISO 8601 date-time
  estimatedArrivalDate: z.string().optional(), // ISO 8601 date-time
  shippingNotes: z.array(z.string()).optional(),
  fulfillmentShipmentItem: z.array(MCFShipmentItemSchema),
  fulfillmentShipmentPackage: z.array(MCFShipmentPackageSchema).optional(),
});

/**
 * Amazon MCF get fulfillment order response schema
 */
export const MCFGetFulfillmentOrderResponseSchema = z.object({
  fulfillmentOrder: MCFFulfillmentOrderSchema,
  fulfillmentOrderItems: z.array(MCFOrderItemSchema),
  fulfillmentShipments: z.array(MCFShipmentSchema).optional(),
  returnItems: z.array(z.any()).optional(),
  returnAuthorizations: z.array(z.any()).optional(),
});

/**
 * Amazon MCF create fulfillment order response schema
 */
export const MCFCreateFulfillmentOrderResponseSchema = z.object({
  fulfillmentOrder: MCFFulfillmentOrderSchema.optional(),
  errors: z
    .array(
      z.object({
        code: z.string(),
        message: z.string(),
        details: z.string().optional(),
      })
    )
    .optional(),
});

/**
 * Amazon MCF update fulfillment order request schema
 */
export const MCFUpdateFulfillmentOrderRequestSchema = z.object({
  marketplaceId: z.string().optional(),
  displayableOrderId: z.string().max(40).optional(),
  displayableOrderDate: z.string().optional(),
  displayableOrderComment: z.string().max(1000).optional(),
  shippingSpeedCategory: MCFShippingSpeedCategorySchema.optional(),
  destinationAddress: MCFAddressSchema.optional(),
  fulfillmentAction: MCFFulfillmentActionSchema.optional(),
  fulfillmentPolicy: MCFFulfillmentPolicySchema.optional(),
  shipFromCountryCode: z.string().length(2).optional(),
  notificationEmails: MCFNotificationEmailListSchema,
  featureConstraints: z.array(MCFFeatureSettingsSchema).optional(),
  items: z.array(MCFOrderItemSchema).optional(),
});

/**
 * Amazon MCF cancel fulfillment order response schema
 */
export const MCFCancelFulfillmentOrderResponseSchema = z.object({
  errors: z
    .array(
      z.object({
        code: z.string(),
        message: z.string(),
        details: z.string().optional(),
      })
    )
    .optional(),
});

/**
 * Amazon MCF tracking event schema
 */
export const MCFTrackingEventSchema = z.object({
  eventDate: z.string(), // ISO 8601 date-time
  eventAddress: MCFAddressSchema.partial().optional(),
  eventCode: z.string(),
  eventDescription: z.string(),
});

/**
 * Amazon MCF package tracking details schema
 */
export const MCFPackageTrackingDetailsSchema = z.object({
  packageNumber: z.number().int().positive(),
  trackingNumber: z.string().optional(),
  carrierCode: z.string().optional(),
  carrierPhoneNumber: z.string().optional(),
  carrierURL: z.string().optional(),
  shipDate: z.string().optional(), // ISO 8601 date-time
  estimatedArrivalDate: z.string().optional(), // ISO 8601 date-time
  shipToAddress: MCFAddressSchema.partial().optional(),
  currentStatus: z.string().optional(),
  currentStatusDescription: z.string().optional(),
  signedForBy: z.string().optional(),
  additionalLocationInfo: z.string().optional(),
  trackingEvents: z.array(MCFTrackingEventSchema).optional(),
});

// ============================================================
// TypeScript Types (Inferred from Zod Schemas)
// ============================================================

/**
 * Amazon MCF destination address
 */
export type MCFAddress = z.infer<typeof MCFAddressSchema>;

/**
 * Amazon MCF fulfillment order item
 */
export type MCFOrderItem = z.infer<typeof MCFOrderItemSchema>;

/**
 * Amazon MCF shipping speed category
 */
export type MCFShippingSpeedCategory = z.infer<typeof MCFShippingSpeedCategorySchema>;

/**
 * Amazon MCF fulfillment policy
 */
export type MCFFulfillmentPolicy = z.infer<typeof MCFFulfillmentPolicySchema>;

/**
 * Amazon MCF fulfillment action
 */
export type MCFFulfillmentAction = z.infer<typeof MCFFulfillmentActionSchema>;

/**
 * Amazon MCF COD settings
 */
export type MCFCODSettings = z.infer<typeof MCFCODSettingsSchema>;

/**
 * Amazon MCF delivery window
 */
export type MCFDeliveryWindow = z.infer<typeof MCFDeliveryWindowSchema>;

/**
 * Amazon MCF feature settings
 */
export type MCFFeatureSettings = z.infer<typeof MCFFeatureSettingsSchema>;

/**
 * Amazon MCF fulfillment order creation request
 */
export type MCFFulfillmentOrderRequest = z.infer<typeof MCFFulfillmentOrderRequestSchema>;

/**
 * Amazon MCF fulfillment order
 */
export type MCFFulfillmentOrder = z.infer<typeof MCFFulfillmentOrderSchema>;

/**
 * Amazon MCF shipment item
 */
export type MCFShipmentItem = z.infer<typeof MCFShipmentItemSchema>;

/**
 * Amazon MCF shipment package
 */
export type MCFShipmentPackage = z.infer<typeof MCFShipmentPackageSchema>;

/**
 * Amazon MCF shipment
 */
export type MCFShipment = z.infer<typeof MCFShipmentSchema>;

/**
 * Amazon MCF get fulfillment order API response
 */
export type MCFGetFulfillmentOrderResponse = z.infer<typeof MCFGetFulfillmentOrderResponseSchema>;

/**
 * Amazon MCF create fulfillment order API response
 */
export type MCFCreateFulfillmentOrderResponse = z.infer<
  typeof MCFCreateFulfillmentOrderResponseSchema
>;

/**
 * Amazon MCF update fulfillment order request
 */
export type MCFUpdateFulfillmentOrderRequest = z.infer<
  typeof MCFUpdateFulfillmentOrderRequestSchema
>;

/**
 * Amazon MCF cancel fulfillment order response
 */
export type MCFCancelFulfillmentOrderResponse = z.infer<
  typeof MCFCancelFulfillmentOrderResponseSchema
>;

/**
 * Amazon MCF tracking event
 */
export type MCFTrackingEvent = z.infer<typeof MCFTrackingEventSchema>;

/**
 * Amazon MCF package tracking details
 */
export type MCFPackageTrackingDetails = z.infer<typeof MCFPackageTrackingDetailsSchema>;

// ============================================================
// Helper Types
// ============================================================

/**
 * Amazon MCF fulfillment order creation parameters
 *
 * Simplified interface for creating MCF orders from internal order data.
 * This is the interface used by the order transformer.
 */
export interface CreateMCFOrderParams {
  orderId: string; // TikTok order ID or other external order ID
  displayableOrderId: string; // User-friendly order ID
  orderDate: Date;
  orderComment?: string;
  shippingSpeed: MCFShippingSpeedCategory;
  destinationAddress: MCFAddress;
  items: Array<{
    sku: string;
    itemId: string;
    quantity: number;
    declaredValue?: {
      amount: number;
      currency: string;
    };
    price?: {
      amount: number;
      currency: string;
    };
    tax?: {
      amount: number;
      currency: string;
    };
  }>;
  notificationEmails?: string[];
  fulfillmentPolicy?: MCFFulfillmentPolicy;
  deliveryWindow?: {
    startDate: Date;
    endDate: Date;
  };
}

/**
 * Amazon MCF fulfillment order status parameters
 */
export interface GetMCFOrderParams {
  sellerFulfillmentOrderId: string;
}

/**
 * Normalized MCF order for internal processing
 *
 * Simplified structure with normalized field names for easier processing.
 * This is the internal representation after retrieving from Amazon MCF.
 */
export interface NormalizedMCFOrder {
  id: string; // sellerFulfillmentOrderId
  status: MCFFulfillmentStatus;
  createdAt: Date;
  updatedAt?: Date;

  // Destination information
  destination: {
    name: string;
    addressLine1: string;
    addressLine2?: string;
    city?: string;
    state: string;
    postalCode: string;
    countryCode: string;
    phone?: string;
    email?: string;
  };

  // Order items
  items: Array<{
    sku: string;
    itemId: string;
    quantity: number;
    price?: number;
    currency?: string;
  }>;

  // Shipments
  shipments?: Array<{
    shipmentId: string;
    status: string;
    fulfillmentCenter: string;
    shippedAt?: Date;
    estimatedArrival?: Date;
    packages: Array<{
      packageNumber: number;
      carrier: string;
      trackingNumber?: string;
      estimatedArrival?: Date;
    }>;
    items: Array<{
      sku: string;
      itemId: string;
      quantity: number;
      packageNumber?: number;
    }>;
  }>;

  // Metadata
  displayableOrderId: string;
  shippingSpeed: MCFShippingSpeedCategory;
  rawOrder: MCFGetFulfillmentOrderResponse;
}

/**
 * MCF order validation result
 */
export interface MCFOrderValidationResult {
  valid: boolean;
  errors: Array<{
    field: string;
    message: string;
    code: string;
  }>;
  warnings?: Array<{
    field: string;
    message: string;
  }>;
}

/**
 * MCF tracking information (simplified)
 */
export interface MCFTrackingInfo {
  orderId: string; // sellerFulfillmentOrderId
  packages: Array<{
    packageNumber: number;
    carrier: ShipmentCarrier;
    carrierCode: string;
    trackingNumber?: string;
    status?: string;
    statusDescription?: string;
    shippedAt?: Date;
    estimatedDelivery?: Date;
    deliveredAt?: Date;
    signedBy?: string;
    currentLocation?: string;
    events?: Array<{
      date: Date;
      code: string;
      description: string;
      location?: string;
    }>;
  }>;
}
