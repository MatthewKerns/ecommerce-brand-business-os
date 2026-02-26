"use strict";
/**
 * Amazon MCF Order Types - Multi-Channel Fulfillment Order Data Models
 *
 * Type definitions and Zod validation schemas for Amazon MCF fulfillment orders.
 * Based on Amazon Selling Partner API (SP-API) Fulfillment Outbound API.
 *
 * Zod schemas provide runtime validation when sending/receiving data from Amazon MCF API.
 * TypeScript types are inferred from schemas for compile-time type safety.
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.MCFPackageTrackingDetailsSchema = exports.MCFTrackingEventSchema = exports.MCFCancelFulfillmentOrderResponseSchema = exports.MCFUpdateFulfillmentOrderRequestSchema = exports.MCFCreateFulfillmentOrderResponseSchema = exports.MCFGetFulfillmentOrderResponseSchema = exports.MCFShipmentSchema = exports.MCFShipmentPackageSchema = exports.MCFShipmentItemSchema = exports.MCFFulfillmentOrderSchema = exports.MCFFulfillmentOrderRequestSchema = exports.MCFFeatureSettingsSchema = exports.MCFDeliveryWindowSchema = exports.MCFCODSettingsSchema = exports.MCFFulfillmentActionSchema = exports.MCFFulfillmentPolicySchema = exports.MCFShippingSpeedCategorySchema = exports.MCFNotificationEmailListSchema = exports.MCFOrderItemSchema = exports.MCFAddressSchema = void 0;
const zod_1 = require("zod");
const common_1 = require("./common");
// ============================================================
// Zod Schemas
// ============================================================
/**
 * Amazon MCF destination address schema
 */
exports.MCFAddressSchema = zod_1.z.object({
    name: zod_1.z.string().max(50),
    addressLine1: zod_1.z.string().max(180),
    addressLine2: zod_1.z.string().max(60).optional(),
    addressLine3: zod_1.z.string().max(60).optional(),
    city: zod_1.z.string().max(50).optional(),
    districtOrCounty: zod_1.z.string().max(150).optional(),
    stateOrRegion: zod_1.z.string().max(150),
    postalCode: zod_1.z.string().max(20),
    countryCode: zod_1.z.string().length(2), // ISO 3166-1 alpha-2
    phone: zod_1.z.string().max(20).optional(),
    email: zod_1.z.string().email().optional(),
});
/**
 * Amazon MCF fulfillment order item schema
 */
exports.MCFOrderItemSchema = zod_1.z.object({
    sellerSku: zod_1.z.string().max(50),
    sellerFulfillmentOrderItemId: zod_1.z.string().max(50),
    quantity: zod_1.z.number().int().positive(),
    giftMessage: zod_1.z.string().max(512).optional(),
    displayableComment: zod_1.z.string().max(250).optional(),
    fulfillmentNetworkSku: zod_1.z.string().optional(), // Assigned by Amazon
    orderItemDisposition: zod_1.z.string().optional(),
    perUnitDeclaredValue: zod_1.z
        .object({
        currencyCode: zod_1.z.string().length(3), // ISO 4217
        value: zod_1.z.number().nonnegative(),
    })
        .optional(),
    perUnitPrice: zod_1.z
        .object({
        currencyCode: zod_1.z.string().length(3),
        value: zod_1.z.number().nonnegative(),
    })
        .optional(),
    perUnitTax: zod_1.z
        .object({
        currencyCode: zod_1.z.string().length(3),
        value: zod_1.z.number().nonnegative(),
    })
        .optional(),
});
/**
 * Amazon MCF notification email list schema
 */
exports.MCFNotificationEmailListSchema = zod_1.z.array(zod_1.z.string().email()).optional();
/**
 * Amazon MCF shipping speed category schema
 */
exports.MCFShippingSpeedCategorySchema = zod_1.z.enum([
    'Standard',
    'Expedited',
    'Priority',
    'ScheduledDelivery',
]);
/**
 * Amazon MCF fulfillment policy schema
 */
exports.MCFFulfillmentPolicySchema = zod_1.z.enum([
    'FillOrKill', // All items must be available or order fails
    'FillAll', // Fulfill all available items
    'FillAllAvailable', // Create multiple shipments if needed
]);
/**
 * Amazon MCF fulfillment action schema
 */
exports.MCFFulfillmentActionSchema = zod_1.z.enum([
    'Ship', // Ship the order immediately
    'Hold', // Hold the order for future shipment
]);
/**
 * Amazon MCF COD (Cash on Delivery) settings schema
 */
exports.MCFCODSettingsSchema = zod_1.z
    .object({
    isCodRequired: zod_1.z.boolean(),
    codCharge: zod_1.z
        .object({
        currencyCode: zod_1.z.string().length(3),
        value: zod_1.z.number().nonnegative(),
    })
        .optional(),
    codChargeTax: zod_1.z
        .object({
        currencyCode: zod_1.z.string().length(3),
        value: zod_1.z.number().nonnegative(),
    })
        .optional(),
    shippingCharge: zod_1.z
        .object({
        currencyCode: zod_1.z.string().length(3),
        value: zod_1.z.number().nonnegative(),
    })
        .optional(),
    shippingChargeTax: zod_1.z
        .object({
        currencyCode: zod_1.z.string().length(3),
        value: zod_1.z.number().nonnegative(),
    })
        .optional(),
})
    .optional();
/**
 * Amazon MCF delivery window schema
 */
exports.MCFDeliveryWindowSchema = zod_1.z
    .object({
    startDate: zod_1.z.string(), // ISO 8601 date-time
    endDate: zod_1.z.string(), // ISO 8601 date-time
})
    .optional();
/**
 * Amazon MCF feature settings schema
 */
exports.MCFFeatureSettingsSchema = zod_1.z
    .object({
    featureName: zod_1.z.string(),
    featureFulfillmentPolicy: zod_1.z.enum(['Required', 'NotRequired']),
})
    .optional();
/**
 * Complete Amazon MCF fulfillment order creation request schema
 */
exports.MCFFulfillmentOrderRequestSchema = zod_1.z.object({
    marketplaceId: zod_1.z.string().optional(),
    sellerFulfillmentOrderId: zod_1.z.string().max(40),
    displayableOrderId: zod_1.z.string().max(40),
    displayableOrderDate: zod_1.z.string(), // ISO 8601 date-time
    displayableOrderComment: zod_1.z.string().max(1000).optional(),
    shippingSpeedCategory: exports.MCFShippingSpeedCategorySchema,
    deliveryWindow: exports.MCFDeliveryWindowSchema,
    destinationAddress: exports.MCFAddressSchema,
    fulfillmentAction: exports.MCFFulfillmentActionSchema.optional(),
    fulfillmentPolicy: exports.MCFFulfillmentPolicySchema.optional(),
    codSettings: exports.MCFCODSettingsSchema,
    shipFromCountryCode: zod_1.z.string().length(2).optional(),
    notificationEmails: exports.MCFNotificationEmailListSchema,
    featureConstraints: zod_1.z.array(exports.MCFFeatureSettingsSchema).optional(),
    items: zod_1.z.array(exports.MCFOrderItemSchema).min(1),
});
/**
 * Amazon MCF fulfillment order response schema
 */
exports.MCFFulfillmentOrderSchema = zod_1.z.object({
    sellerFulfillmentOrderId: zod_1.z.string(),
    marketplaceId: zod_1.z.string(),
    displayableOrderId: zod_1.z.string(),
    displayableOrderDate: zod_1.z.string(),
    displayableOrderComment: zod_1.z.string().optional(),
    shippingSpeedCategory: exports.MCFShippingSpeedCategorySchema,
    deliveryWindow: exports.MCFDeliveryWindowSchema,
    destinationAddress: exports.MCFAddressSchema,
    fulfillmentAction: exports.MCFFulfillmentActionSchema.optional(),
    fulfillmentPolicy: exports.MCFFulfillmentPolicySchema.optional(),
    codSettings: exports.MCFCODSettingsSchema,
    receivedDate: zod_1.z.string().optional(),
    fulfillmentOrderStatus: zod_1.z.nativeEnum(common_1.MCFFulfillmentStatus),
    statusUpdatedDate: zod_1.z.string().optional(),
    notificationEmails: exports.MCFNotificationEmailListSchema,
    featureConstraints: zod_1.z.array(exports.MCFFeatureSettingsSchema).optional(),
});
/**
 * Amazon MCF fulfillment shipment item schema
 */
exports.MCFShipmentItemSchema = zod_1.z.object({
    sellerSku: zod_1.z.string(),
    sellerFulfillmentOrderItemId: zod_1.z.string(),
    quantity: zod_1.z.number().int().nonnegative(),
    packageNumber: zod_1.z.number().int().positive().optional(),
});
/**
 * Amazon MCF fulfillment shipment package schema
 */
exports.MCFShipmentPackageSchema = zod_1.z.object({
    packageNumber: zod_1.z.number().int().positive(),
    carrierCode: zod_1.z.string(),
    trackingNumber: zod_1.z.string().optional(),
    estimatedArrivalDate: zod_1.z.string().optional(), // ISO 8601 date-time
});
/**
 * Amazon MCF fulfillment shipment schema
 */
exports.MCFShipmentSchema = zod_1.z.object({
    amazonShipmentId: zod_1.z.string(),
    fulfillmentCenterId: zod_1.z.string(),
    fulfillmentShipmentStatus: zod_1.z.enum([
        'PENDING',
        'SHIPPED',
        'CANCELLED_BY_FULFILLER',
        'CANCELLED_BY_SELLER',
    ]),
    shippingDate: zod_1.z.string().optional(), // ISO 8601 date-time
    estimatedArrivalDate: zod_1.z.string().optional(), // ISO 8601 date-time
    shippingNotes: zod_1.z.array(zod_1.z.string()).optional(),
    fulfillmentShipmentItem: zod_1.z.array(exports.MCFShipmentItemSchema),
    fulfillmentShipmentPackage: zod_1.z.array(exports.MCFShipmentPackageSchema).optional(),
});
/**
 * Amazon MCF get fulfillment order response schema
 */
exports.MCFGetFulfillmentOrderResponseSchema = zod_1.z.object({
    fulfillmentOrder: exports.MCFFulfillmentOrderSchema,
    fulfillmentOrderItems: zod_1.z.array(exports.MCFOrderItemSchema),
    fulfillmentShipments: zod_1.z.array(exports.MCFShipmentSchema).optional(),
    returnItems: zod_1.z.array(zod_1.z.any()).optional(),
    returnAuthorizations: zod_1.z.array(zod_1.z.any()).optional(),
});
/**
 * Amazon MCF create fulfillment order response schema
 */
exports.MCFCreateFulfillmentOrderResponseSchema = zod_1.z.object({
    fulfillmentOrder: exports.MCFFulfillmentOrderSchema.optional(),
    errors: zod_1.z
        .array(zod_1.z.object({
        code: zod_1.z.string(),
        message: zod_1.z.string(),
        details: zod_1.z.string().optional(),
    }))
        .optional(),
});
/**
 * Amazon MCF update fulfillment order request schema
 */
exports.MCFUpdateFulfillmentOrderRequestSchema = zod_1.z.object({
    marketplaceId: zod_1.z.string().optional(),
    displayableOrderId: zod_1.z.string().max(40).optional(),
    displayableOrderDate: zod_1.z.string().optional(),
    displayableOrderComment: zod_1.z.string().max(1000).optional(),
    shippingSpeedCategory: exports.MCFShippingSpeedCategorySchema.optional(),
    destinationAddress: exports.MCFAddressSchema.optional(),
    fulfillmentAction: exports.MCFFulfillmentActionSchema.optional(),
    fulfillmentPolicy: exports.MCFFulfillmentPolicySchema.optional(),
    shipFromCountryCode: zod_1.z.string().length(2).optional(),
    notificationEmails: exports.MCFNotificationEmailListSchema,
    featureConstraints: zod_1.z.array(exports.MCFFeatureSettingsSchema).optional(),
    items: zod_1.z.array(exports.MCFOrderItemSchema).optional(),
});
/**
 * Amazon MCF cancel fulfillment order response schema
 */
exports.MCFCancelFulfillmentOrderResponseSchema = zod_1.z.object({
    errors: zod_1.z
        .array(zod_1.z.object({
        code: zod_1.z.string(),
        message: zod_1.z.string(),
        details: zod_1.z.string().optional(),
    }))
        .optional(),
});
/**
 * Amazon MCF tracking event schema
 */
exports.MCFTrackingEventSchema = zod_1.z.object({
    eventDate: zod_1.z.string(), // ISO 8601 date-time
    eventAddress: exports.MCFAddressSchema.partial().optional(),
    eventCode: zod_1.z.string(),
    eventDescription: zod_1.z.string(),
});
/**
 * Amazon MCF package tracking details schema
 */
exports.MCFPackageTrackingDetailsSchema = zod_1.z.object({
    packageNumber: zod_1.z.number().int().positive(),
    trackingNumber: zod_1.z.string().optional(),
    carrierCode: zod_1.z.string().optional(),
    carrierPhoneNumber: zod_1.z.string().optional(),
    carrierURL: zod_1.z.string().optional(),
    shipDate: zod_1.z.string().optional(), // ISO 8601 date-time
    estimatedArrivalDate: zod_1.z.string().optional(), // ISO 8601 date-time
    shipToAddress: exports.MCFAddressSchema.partial().optional(),
    currentStatus: zod_1.z.string().optional(),
    currentStatusDescription: zod_1.z.string().optional(),
    signedForBy: zod_1.z.string().optional(),
    additionalLocationInfo: zod_1.z.string().optional(),
    trackingEvents: zod_1.z.array(exports.MCFTrackingEventSchema).optional(),
});
//# sourceMappingURL=mcf-order.js.map