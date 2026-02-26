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
/**
 * Amazon MCF destination address schema
 */
export declare const MCFAddressSchema: z.ZodObject<{
    name: z.ZodString;
    addressLine1: z.ZodString;
    addressLine2: z.ZodOptional<z.ZodString>;
    addressLine3: z.ZodOptional<z.ZodString>;
    city: z.ZodOptional<z.ZodString>;
    districtOrCounty: z.ZodOptional<z.ZodString>;
    stateOrRegion: z.ZodString;
    postalCode: z.ZodString;
    countryCode: z.ZodString;
    phone: z.ZodOptional<z.ZodString>;
    email: z.ZodOptional<z.ZodString>;
}, "strip", z.ZodTypeAny, {
    name: string;
    addressLine1: string;
    stateOrRegion: string;
    postalCode: string;
    countryCode: string;
    city?: string | undefined;
    email?: string | undefined;
    addressLine2?: string | undefined;
    addressLine3?: string | undefined;
    districtOrCounty?: string | undefined;
    phone?: string | undefined;
}, {
    name: string;
    addressLine1: string;
    stateOrRegion: string;
    postalCode: string;
    countryCode: string;
    city?: string | undefined;
    email?: string | undefined;
    addressLine2?: string | undefined;
    addressLine3?: string | undefined;
    districtOrCounty?: string | undefined;
    phone?: string | undefined;
}>;
/**
 * Amazon MCF fulfillment order item schema
 */
export declare const MCFOrderItemSchema: z.ZodObject<{
    sellerSku: z.ZodString;
    sellerFulfillmentOrderItemId: z.ZodString;
    quantity: z.ZodNumber;
    giftMessage: z.ZodOptional<z.ZodString>;
    displayableComment: z.ZodOptional<z.ZodString>;
    fulfillmentNetworkSku: z.ZodOptional<z.ZodString>;
    orderItemDisposition: z.ZodOptional<z.ZodString>;
    perUnitDeclaredValue: z.ZodOptional<z.ZodObject<{
        currencyCode: z.ZodString;
        value: z.ZodNumber;
    }, "strip", z.ZodTypeAny, {
        value: number;
        currencyCode: string;
    }, {
        value: number;
        currencyCode: string;
    }>>;
    perUnitPrice: z.ZodOptional<z.ZodObject<{
        currencyCode: z.ZodString;
        value: z.ZodNumber;
    }, "strip", z.ZodTypeAny, {
        value: number;
        currencyCode: string;
    }, {
        value: number;
        currencyCode: string;
    }>>;
    perUnitTax: z.ZodOptional<z.ZodObject<{
        currencyCode: z.ZodString;
        value: z.ZodNumber;
    }, "strip", z.ZodTypeAny, {
        value: number;
        currencyCode: string;
    }, {
        value: number;
        currencyCode: string;
    }>>;
}, "strip", z.ZodTypeAny, {
    quantity: number;
    sellerSku: string;
    sellerFulfillmentOrderItemId: string;
    giftMessage?: string | undefined;
    displayableComment?: string | undefined;
    fulfillmentNetworkSku?: string | undefined;
    orderItemDisposition?: string | undefined;
    perUnitDeclaredValue?: {
        value: number;
        currencyCode: string;
    } | undefined;
    perUnitPrice?: {
        value: number;
        currencyCode: string;
    } | undefined;
    perUnitTax?: {
        value: number;
        currencyCode: string;
    } | undefined;
}, {
    quantity: number;
    sellerSku: string;
    sellerFulfillmentOrderItemId: string;
    giftMessage?: string | undefined;
    displayableComment?: string | undefined;
    fulfillmentNetworkSku?: string | undefined;
    orderItemDisposition?: string | undefined;
    perUnitDeclaredValue?: {
        value: number;
        currencyCode: string;
    } | undefined;
    perUnitPrice?: {
        value: number;
        currencyCode: string;
    } | undefined;
    perUnitTax?: {
        value: number;
        currencyCode: string;
    } | undefined;
}>;
/**
 * Amazon MCF notification email list schema
 */
export declare const MCFNotificationEmailListSchema: z.ZodOptional<z.ZodArray<z.ZodString, "many">>;
/**
 * Amazon MCF shipping speed category schema
 */
export declare const MCFShippingSpeedCategorySchema: z.ZodEnum<["Standard", "Expedited", "Priority", "ScheduledDelivery"]>;
/**
 * Amazon MCF fulfillment policy schema
 */
export declare const MCFFulfillmentPolicySchema: z.ZodEnum<["FillOrKill", "FillAll", "FillAllAvailable"]>;
/**
 * Amazon MCF fulfillment action schema
 */
export declare const MCFFulfillmentActionSchema: z.ZodEnum<["Ship", "Hold"]>;
/**
 * Amazon MCF COD (Cash on Delivery) settings schema
 */
export declare const MCFCODSettingsSchema: z.ZodOptional<z.ZodObject<{
    isCodRequired: z.ZodBoolean;
    codCharge: z.ZodOptional<z.ZodObject<{
        currencyCode: z.ZodString;
        value: z.ZodNumber;
    }, "strip", z.ZodTypeAny, {
        value: number;
        currencyCode: string;
    }, {
        value: number;
        currencyCode: string;
    }>>;
    codChargeTax: z.ZodOptional<z.ZodObject<{
        currencyCode: z.ZodString;
        value: z.ZodNumber;
    }, "strip", z.ZodTypeAny, {
        value: number;
        currencyCode: string;
    }, {
        value: number;
        currencyCode: string;
    }>>;
    shippingCharge: z.ZodOptional<z.ZodObject<{
        currencyCode: z.ZodString;
        value: z.ZodNumber;
    }, "strip", z.ZodTypeAny, {
        value: number;
        currencyCode: string;
    }, {
        value: number;
        currencyCode: string;
    }>>;
    shippingChargeTax: z.ZodOptional<z.ZodObject<{
        currencyCode: z.ZodString;
        value: z.ZodNumber;
    }, "strip", z.ZodTypeAny, {
        value: number;
        currencyCode: string;
    }, {
        value: number;
        currencyCode: string;
    }>>;
}, "strip", z.ZodTypeAny, {
    isCodRequired: boolean;
    codCharge?: {
        value: number;
        currencyCode: string;
    } | undefined;
    codChargeTax?: {
        value: number;
        currencyCode: string;
    } | undefined;
    shippingCharge?: {
        value: number;
        currencyCode: string;
    } | undefined;
    shippingChargeTax?: {
        value: number;
        currencyCode: string;
    } | undefined;
}, {
    isCodRequired: boolean;
    codCharge?: {
        value: number;
        currencyCode: string;
    } | undefined;
    codChargeTax?: {
        value: number;
        currencyCode: string;
    } | undefined;
    shippingCharge?: {
        value: number;
        currencyCode: string;
    } | undefined;
    shippingChargeTax?: {
        value: number;
        currencyCode: string;
    } | undefined;
}>>;
/**
 * Amazon MCF delivery window schema
 */
export declare const MCFDeliveryWindowSchema: z.ZodOptional<z.ZodObject<{
    startDate: z.ZodString;
    endDate: z.ZodString;
}, "strip", z.ZodTypeAny, {
    startDate: string;
    endDate: string;
}, {
    startDate: string;
    endDate: string;
}>>;
/**
 * Amazon MCF feature settings schema
 */
export declare const MCFFeatureSettingsSchema: z.ZodOptional<z.ZodObject<{
    featureName: z.ZodString;
    featureFulfillmentPolicy: z.ZodEnum<["Required", "NotRequired"]>;
}, "strip", z.ZodTypeAny, {
    featureName: string;
    featureFulfillmentPolicy: "Required" | "NotRequired";
}, {
    featureName: string;
    featureFulfillmentPolicy: "Required" | "NotRequired";
}>>;
/**
 * Complete Amazon MCF fulfillment order creation request schema
 */
export declare const MCFFulfillmentOrderRequestSchema: z.ZodObject<{
    marketplaceId: z.ZodOptional<z.ZodString>;
    sellerFulfillmentOrderId: z.ZodString;
    displayableOrderId: z.ZodString;
    displayableOrderDate: z.ZodString;
    displayableOrderComment: z.ZodOptional<z.ZodString>;
    shippingSpeedCategory: z.ZodEnum<["Standard", "Expedited", "Priority", "ScheduledDelivery"]>;
    deliveryWindow: z.ZodOptional<z.ZodObject<{
        startDate: z.ZodString;
        endDate: z.ZodString;
    }, "strip", z.ZodTypeAny, {
        startDate: string;
        endDate: string;
    }, {
        startDate: string;
        endDate: string;
    }>>;
    destinationAddress: z.ZodObject<{
        name: z.ZodString;
        addressLine1: z.ZodString;
        addressLine2: z.ZodOptional<z.ZodString>;
        addressLine3: z.ZodOptional<z.ZodString>;
        city: z.ZodOptional<z.ZodString>;
        districtOrCounty: z.ZodOptional<z.ZodString>;
        stateOrRegion: z.ZodString;
        postalCode: z.ZodString;
        countryCode: z.ZodString;
        phone: z.ZodOptional<z.ZodString>;
        email: z.ZodOptional<z.ZodString>;
    }, "strip", z.ZodTypeAny, {
        name: string;
        addressLine1: string;
        stateOrRegion: string;
        postalCode: string;
        countryCode: string;
        city?: string | undefined;
        email?: string | undefined;
        addressLine2?: string | undefined;
        addressLine3?: string | undefined;
        districtOrCounty?: string | undefined;
        phone?: string | undefined;
    }, {
        name: string;
        addressLine1: string;
        stateOrRegion: string;
        postalCode: string;
        countryCode: string;
        city?: string | undefined;
        email?: string | undefined;
        addressLine2?: string | undefined;
        addressLine3?: string | undefined;
        districtOrCounty?: string | undefined;
        phone?: string | undefined;
    }>;
    fulfillmentAction: z.ZodOptional<z.ZodEnum<["Ship", "Hold"]>>;
    fulfillmentPolicy: z.ZodOptional<z.ZodEnum<["FillOrKill", "FillAll", "FillAllAvailable"]>>;
    codSettings: z.ZodOptional<z.ZodObject<{
        isCodRequired: z.ZodBoolean;
        codCharge: z.ZodOptional<z.ZodObject<{
            currencyCode: z.ZodString;
            value: z.ZodNumber;
        }, "strip", z.ZodTypeAny, {
            value: number;
            currencyCode: string;
        }, {
            value: number;
            currencyCode: string;
        }>>;
        codChargeTax: z.ZodOptional<z.ZodObject<{
            currencyCode: z.ZodString;
            value: z.ZodNumber;
        }, "strip", z.ZodTypeAny, {
            value: number;
            currencyCode: string;
        }, {
            value: number;
            currencyCode: string;
        }>>;
        shippingCharge: z.ZodOptional<z.ZodObject<{
            currencyCode: z.ZodString;
            value: z.ZodNumber;
        }, "strip", z.ZodTypeAny, {
            value: number;
            currencyCode: string;
        }, {
            value: number;
            currencyCode: string;
        }>>;
        shippingChargeTax: z.ZodOptional<z.ZodObject<{
            currencyCode: z.ZodString;
            value: z.ZodNumber;
        }, "strip", z.ZodTypeAny, {
            value: number;
            currencyCode: string;
        }, {
            value: number;
            currencyCode: string;
        }>>;
    }, "strip", z.ZodTypeAny, {
        isCodRequired: boolean;
        codCharge?: {
            value: number;
            currencyCode: string;
        } | undefined;
        codChargeTax?: {
            value: number;
            currencyCode: string;
        } | undefined;
        shippingCharge?: {
            value: number;
            currencyCode: string;
        } | undefined;
        shippingChargeTax?: {
            value: number;
            currencyCode: string;
        } | undefined;
    }, {
        isCodRequired: boolean;
        codCharge?: {
            value: number;
            currencyCode: string;
        } | undefined;
        codChargeTax?: {
            value: number;
            currencyCode: string;
        } | undefined;
        shippingCharge?: {
            value: number;
            currencyCode: string;
        } | undefined;
        shippingChargeTax?: {
            value: number;
            currencyCode: string;
        } | undefined;
    }>>;
    shipFromCountryCode: z.ZodOptional<z.ZodString>;
    notificationEmails: z.ZodOptional<z.ZodArray<z.ZodString, "many">>;
    featureConstraints: z.ZodOptional<z.ZodArray<z.ZodOptional<z.ZodObject<{
        featureName: z.ZodString;
        featureFulfillmentPolicy: z.ZodEnum<["Required", "NotRequired"]>;
    }, "strip", z.ZodTypeAny, {
        featureName: string;
        featureFulfillmentPolicy: "Required" | "NotRequired";
    }, {
        featureName: string;
        featureFulfillmentPolicy: "Required" | "NotRequired";
    }>>, "many">>;
    items: z.ZodArray<z.ZodObject<{
        sellerSku: z.ZodString;
        sellerFulfillmentOrderItemId: z.ZodString;
        quantity: z.ZodNumber;
        giftMessage: z.ZodOptional<z.ZodString>;
        displayableComment: z.ZodOptional<z.ZodString>;
        fulfillmentNetworkSku: z.ZodOptional<z.ZodString>;
        orderItemDisposition: z.ZodOptional<z.ZodString>;
        perUnitDeclaredValue: z.ZodOptional<z.ZodObject<{
            currencyCode: z.ZodString;
            value: z.ZodNumber;
        }, "strip", z.ZodTypeAny, {
            value: number;
            currencyCode: string;
        }, {
            value: number;
            currencyCode: string;
        }>>;
        perUnitPrice: z.ZodOptional<z.ZodObject<{
            currencyCode: z.ZodString;
            value: z.ZodNumber;
        }, "strip", z.ZodTypeAny, {
            value: number;
            currencyCode: string;
        }, {
            value: number;
            currencyCode: string;
        }>>;
        perUnitTax: z.ZodOptional<z.ZodObject<{
            currencyCode: z.ZodString;
            value: z.ZodNumber;
        }, "strip", z.ZodTypeAny, {
            value: number;
            currencyCode: string;
        }, {
            value: number;
            currencyCode: string;
        }>>;
    }, "strip", z.ZodTypeAny, {
        quantity: number;
        sellerSku: string;
        sellerFulfillmentOrderItemId: string;
        giftMessage?: string | undefined;
        displayableComment?: string | undefined;
        fulfillmentNetworkSku?: string | undefined;
        orderItemDisposition?: string | undefined;
        perUnitDeclaredValue?: {
            value: number;
            currencyCode: string;
        } | undefined;
        perUnitPrice?: {
            value: number;
            currencyCode: string;
        } | undefined;
        perUnitTax?: {
            value: number;
            currencyCode: string;
        } | undefined;
    }, {
        quantity: number;
        sellerSku: string;
        sellerFulfillmentOrderItemId: string;
        giftMessage?: string | undefined;
        displayableComment?: string | undefined;
        fulfillmentNetworkSku?: string | undefined;
        orderItemDisposition?: string | undefined;
        perUnitDeclaredValue?: {
            value: number;
            currencyCode: string;
        } | undefined;
        perUnitPrice?: {
            value: number;
            currencyCode: string;
        } | undefined;
        perUnitTax?: {
            value: number;
            currencyCode: string;
        } | undefined;
    }>, "many">;
}, "strip", z.ZodTypeAny, {
    items: {
        quantity: number;
        sellerSku: string;
        sellerFulfillmentOrderItemId: string;
        giftMessage?: string | undefined;
        displayableComment?: string | undefined;
        fulfillmentNetworkSku?: string | undefined;
        orderItemDisposition?: string | undefined;
        perUnitDeclaredValue?: {
            value: number;
            currencyCode: string;
        } | undefined;
        perUnitPrice?: {
            value: number;
            currencyCode: string;
        } | undefined;
        perUnitTax?: {
            value: number;
            currencyCode: string;
        } | undefined;
    }[];
    sellerFulfillmentOrderId: string;
    displayableOrderId: string;
    displayableOrderDate: string;
    shippingSpeedCategory: "Standard" | "Expedited" | "Priority" | "ScheduledDelivery";
    destinationAddress: {
        name: string;
        addressLine1: string;
        stateOrRegion: string;
        postalCode: string;
        countryCode: string;
        city?: string | undefined;
        email?: string | undefined;
        addressLine2?: string | undefined;
        addressLine3?: string | undefined;
        districtOrCounty?: string | undefined;
        phone?: string | undefined;
    };
    marketplaceId?: string | undefined;
    displayableOrderComment?: string | undefined;
    deliveryWindow?: {
        startDate: string;
        endDate: string;
    } | undefined;
    fulfillmentAction?: "Ship" | "Hold" | undefined;
    fulfillmentPolicy?: "FillOrKill" | "FillAll" | "FillAllAvailable" | undefined;
    codSettings?: {
        isCodRequired: boolean;
        codCharge?: {
            value: number;
            currencyCode: string;
        } | undefined;
        codChargeTax?: {
            value: number;
            currencyCode: string;
        } | undefined;
        shippingCharge?: {
            value: number;
            currencyCode: string;
        } | undefined;
        shippingChargeTax?: {
            value: number;
            currencyCode: string;
        } | undefined;
    } | undefined;
    shipFromCountryCode?: string | undefined;
    notificationEmails?: string[] | undefined;
    featureConstraints?: ({
        featureName: string;
        featureFulfillmentPolicy: "Required" | "NotRequired";
    } | undefined)[] | undefined;
}, {
    items: {
        quantity: number;
        sellerSku: string;
        sellerFulfillmentOrderItemId: string;
        giftMessage?: string | undefined;
        displayableComment?: string | undefined;
        fulfillmentNetworkSku?: string | undefined;
        orderItemDisposition?: string | undefined;
        perUnitDeclaredValue?: {
            value: number;
            currencyCode: string;
        } | undefined;
        perUnitPrice?: {
            value: number;
            currencyCode: string;
        } | undefined;
        perUnitTax?: {
            value: number;
            currencyCode: string;
        } | undefined;
    }[];
    sellerFulfillmentOrderId: string;
    displayableOrderId: string;
    displayableOrderDate: string;
    shippingSpeedCategory: "Standard" | "Expedited" | "Priority" | "ScheduledDelivery";
    destinationAddress: {
        name: string;
        addressLine1: string;
        stateOrRegion: string;
        postalCode: string;
        countryCode: string;
        city?: string | undefined;
        email?: string | undefined;
        addressLine2?: string | undefined;
        addressLine3?: string | undefined;
        districtOrCounty?: string | undefined;
        phone?: string | undefined;
    };
    marketplaceId?: string | undefined;
    displayableOrderComment?: string | undefined;
    deliveryWindow?: {
        startDate: string;
        endDate: string;
    } | undefined;
    fulfillmentAction?: "Ship" | "Hold" | undefined;
    fulfillmentPolicy?: "FillOrKill" | "FillAll" | "FillAllAvailable" | undefined;
    codSettings?: {
        isCodRequired: boolean;
        codCharge?: {
            value: number;
            currencyCode: string;
        } | undefined;
        codChargeTax?: {
            value: number;
            currencyCode: string;
        } | undefined;
        shippingCharge?: {
            value: number;
            currencyCode: string;
        } | undefined;
        shippingChargeTax?: {
            value: number;
            currencyCode: string;
        } | undefined;
    } | undefined;
    shipFromCountryCode?: string | undefined;
    notificationEmails?: string[] | undefined;
    featureConstraints?: ({
        featureName: string;
        featureFulfillmentPolicy: "Required" | "NotRequired";
    } | undefined)[] | undefined;
}>;
/**
 * Amazon MCF fulfillment order response schema
 */
export declare const MCFFulfillmentOrderSchema: z.ZodObject<{
    sellerFulfillmentOrderId: z.ZodString;
    marketplaceId: z.ZodString;
    displayableOrderId: z.ZodString;
    displayableOrderDate: z.ZodString;
    displayableOrderComment: z.ZodOptional<z.ZodString>;
    shippingSpeedCategory: z.ZodEnum<["Standard", "Expedited", "Priority", "ScheduledDelivery"]>;
    deliveryWindow: z.ZodOptional<z.ZodObject<{
        startDate: z.ZodString;
        endDate: z.ZodString;
    }, "strip", z.ZodTypeAny, {
        startDate: string;
        endDate: string;
    }, {
        startDate: string;
        endDate: string;
    }>>;
    destinationAddress: z.ZodObject<{
        name: z.ZodString;
        addressLine1: z.ZodString;
        addressLine2: z.ZodOptional<z.ZodString>;
        addressLine3: z.ZodOptional<z.ZodString>;
        city: z.ZodOptional<z.ZodString>;
        districtOrCounty: z.ZodOptional<z.ZodString>;
        stateOrRegion: z.ZodString;
        postalCode: z.ZodString;
        countryCode: z.ZodString;
        phone: z.ZodOptional<z.ZodString>;
        email: z.ZodOptional<z.ZodString>;
    }, "strip", z.ZodTypeAny, {
        name: string;
        addressLine1: string;
        stateOrRegion: string;
        postalCode: string;
        countryCode: string;
        city?: string | undefined;
        email?: string | undefined;
        addressLine2?: string | undefined;
        addressLine3?: string | undefined;
        districtOrCounty?: string | undefined;
        phone?: string | undefined;
    }, {
        name: string;
        addressLine1: string;
        stateOrRegion: string;
        postalCode: string;
        countryCode: string;
        city?: string | undefined;
        email?: string | undefined;
        addressLine2?: string | undefined;
        addressLine3?: string | undefined;
        districtOrCounty?: string | undefined;
        phone?: string | undefined;
    }>;
    fulfillmentAction: z.ZodOptional<z.ZodEnum<["Ship", "Hold"]>>;
    fulfillmentPolicy: z.ZodOptional<z.ZodEnum<["FillOrKill", "FillAll", "FillAllAvailable"]>>;
    codSettings: z.ZodOptional<z.ZodObject<{
        isCodRequired: z.ZodBoolean;
        codCharge: z.ZodOptional<z.ZodObject<{
            currencyCode: z.ZodString;
            value: z.ZodNumber;
        }, "strip", z.ZodTypeAny, {
            value: number;
            currencyCode: string;
        }, {
            value: number;
            currencyCode: string;
        }>>;
        codChargeTax: z.ZodOptional<z.ZodObject<{
            currencyCode: z.ZodString;
            value: z.ZodNumber;
        }, "strip", z.ZodTypeAny, {
            value: number;
            currencyCode: string;
        }, {
            value: number;
            currencyCode: string;
        }>>;
        shippingCharge: z.ZodOptional<z.ZodObject<{
            currencyCode: z.ZodString;
            value: z.ZodNumber;
        }, "strip", z.ZodTypeAny, {
            value: number;
            currencyCode: string;
        }, {
            value: number;
            currencyCode: string;
        }>>;
        shippingChargeTax: z.ZodOptional<z.ZodObject<{
            currencyCode: z.ZodString;
            value: z.ZodNumber;
        }, "strip", z.ZodTypeAny, {
            value: number;
            currencyCode: string;
        }, {
            value: number;
            currencyCode: string;
        }>>;
    }, "strip", z.ZodTypeAny, {
        isCodRequired: boolean;
        codCharge?: {
            value: number;
            currencyCode: string;
        } | undefined;
        codChargeTax?: {
            value: number;
            currencyCode: string;
        } | undefined;
        shippingCharge?: {
            value: number;
            currencyCode: string;
        } | undefined;
        shippingChargeTax?: {
            value: number;
            currencyCode: string;
        } | undefined;
    }, {
        isCodRequired: boolean;
        codCharge?: {
            value: number;
            currencyCode: string;
        } | undefined;
        codChargeTax?: {
            value: number;
            currencyCode: string;
        } | undefined;
        shippingCharge?: {
            value: number;
            currencyCode: string;
        } | undefined;
        shippingChargeTax?: {
            value: number;
            currencyCode: string;
        } | undefined;
    }>>;
    receivedDate: z.ZodOptional<z.ZodString>;
    fulfillmentOrderStatus: z.ZodNativeEnum<typeof MCFFulfillmentStatus>;
    statusUpdatedDate: z.ZodOptional<z.ZodString>;
    notificationEmails: z.ZodOptional<z.ZodArray<z.ZodString, "many">>;
    featureConstraints: z.ZodOptional<z.ZodArray<z.ZodOptional<z.ZodObject<{
        featureName: z.ZodString;
        featureFulfillmentPolicy: z.ZodEnum<["Required", "NotRequired"]>;
    }, "strip", z.ZodTypeAny, {
        featureName: string;
        featureFulfillmentPolicy: "Required" | "NotRequired";
    }, {
        featureName: string;
        featureFulfillmentPolicy: "Required" | "NotRequired";
    }>>, "many">>;
}, "strip", z.ZodTypeAny, {
    marketplaceId: string;
    sellerFulfillmentOrderId: string;
    displayableOrderId: string;
    displayableOrderDate: string;
    shippingSpeedCategory: "Standard" | "Expedited" | "Priority" | "ScheduledDelivery";
    destinationAddress: {
        name: string;
        addressLine1: string;
        stateOrRegion: string;
        postalCode: string;
        countryCode: string;
        city?: string | undefined;
        email?: string | undefined;
        addressLine2?: string | undefined;
        addressLine3?: string | undefined;
        districtOrCounty?: string | undefined;
        phone?: string | undefined;
    };
    fulfillmentOrderStatus: MCFFulfillmentStatus;
    displayableOrderComment?: string | undefined;
    deliveryWindow?: {
        startDate: string;
        endDate: string;
    } | undefined;
    fulfillmentAction?: "Ship" | "Hold" | undefined;
    fulfillmentPolicy?: "FillOrKill" | "FillAll" | "FillAllAvailable" | undefined;
    codSettings?: {
        isCodRequired: boolean;
        codCharge?: {
            value: number;
            currencyCode: string;
        } | undefined;
        codChargeTax?: {
            value: number;
            currencyCode: string;
        } | undefined;
        shippingCharge?: {
            value: number;
            currencyCode: string;
        } | undefined;
        shippingChargeTax?: {
            value: number;
            currencyCode: string;
        } | undefined;
    } | undefined;
    notificationEmails?: string[] | undefined;
    featureConstraints?: ({
        featureName: string;
        featureFulfillmentPolicy: "Required" | "NotRequired";
    } | undefined)[] | undefined;
    receivedDate?: string | undefined;
    statusUpdatedDate?: string | undefined;
}, {
    marketplaceId: string;
    sellerFulfillmentOrderId: string;
    displayableOrderId: string;
    displayableOrderDate: string;
    shippingSpeedCategory: "Standard" | "Expedited" | "Priority" | "ScheduledDelivery";
    destinationAddress: {
        name: string;
        addressLine1: string;
        stateOrRegion: string;
        postalCode: string;
        countryCode: string;
        city?: string | undefined;
        email?: string | undefined;
        addressLine2?: string | undefined;
        addressLine3?: string | undefined;
        districtOrCounty?: string | undefined;
        phone?: string | undefined;
    };
    fulfillmentOrderStatus: MCFFulfillmentStatus;
    displayableOrderComment?: string | undefined;
    deliveryWindow?: {
        startDate: string;
        endDate: string;
    } | undefined;
    fulfillmentAction?: "Ship" | "Hold" | undefined;
    fulfillmentPolicy?: "FillOrKill" | "FillAll" | "FillAllAvailable" | undefined;
    codSettings?: {
        isCodRequired: boolean;
        codCharge?: {
            value: number;
            currencyCode: string;
        } | undefined;
        codChargeTax?: {
            value: number;
            currencyCode: string;
        } | undefined;
        shippingCharge?: {
            value: number;
            currencyCode: string;
        } | undefined;
        shippingChargeTax?: {
            value: number;
            currencyCode: string;
        } | undefined;
    } | undefined;
    notificationEmails?: string[] | undefined;
    featureConstraints?: ({
        featureName: string;
        featureFulfillmentPolicy: "Required" | "NotRequired";
    } | undefined)[] | undefined;
    receivedDate?: string | undefined;
    statusUpdatedDate?: string | undefined;
}>;
/**
 * Amazon MCF fulfillment shipment item schema
 */
export declare const MCFShipmentItemSchema: z.ZodObject<{
    sellerSku: z.ZodString;
    sellerFulfillmentOrderItemId: z.ZodString;
    quantity: z.ZodNumber;
    packageNumber: z.ZodOptional<z.ZodNumber>;
}, "strip", z.ZodTypeAny, {
    quantity: number;
    sellerSku: string;
    sellerFulfillmentOrderItemId: string;
    packageNumber?: number | undefined;
}, {
    quantity: number;
    sellerSku: string;
    sellerFulfillmentOrderItemId: string;
    packageNumber?: number | undefined;
}>;
/**
 * Amazon MCF fulfillment shipment package schema
 */
export declare const MCFShipmentPackageSchema: z.ZodObject<{
    packageNumber: z.ZodNumber;
    carrierCode: z.ZodString;
    trackingNumber: z.ZodOptional<z.ZodString>;
    estimatedArrivalDate: z.ZodOptional<z.ZodString>;
}, "strip", z.ZodTypeAny, {
    packageNumber: number;
    carrierCode: string;
    trackingNumber?: string | undefined;
    estimatedArrivalDate?: string | undefined;
}, {
    packageNumber: number;
    carrierCode: string;
    trackingNumber?: string | undefined;
    estimatedArrivalDate?: string | undefined;
}>;
/**
 * Amazon MCF fulfillment shipment schema
 */
export declare const MCFShipmentSchema: z.ZodObject<{
    amazonShipmentId: z.ZodString;
    fulfillmentCenterId: z.ZodString;
    fulfillmentShipmentStatus: z.ZodEnum<["PENDING", "SHIPPED", "CANCELLED_BY_FULFILLER", "CANCELLED_BY_SELLER"]>;
    shippingDate: z.ZodOptional<z.ZodString>;
    estimatedArrivalDate: z.ZodOptional<z.ZodString>;
    shippingNotes: z.ZodOptional<z.ZodArray<z.ZodString, "many">>;
    fulfillmentShipmentItem: z.ZodArray<z.ZodObject<{
        sellerSku: z.ZodString;
        sellerFulfillmentOrderItemId: z.ZodString;
        quantity: z.ZodNumber;
        packageNumber: z.ZodOptional<z.ZodNumber>;
    }, "strip", z.ZodTypeAny, {
        quantity: number;
        sellerSku: string;
        sellerFulfillmentOrderItemId: string;
        packageNumber?: number | undefined;
    }, {
        quantity: number;
        sellerSku: string;
        sellerFulfillmentOrderItemId: string;
        packageNumber?: number | undefined;
    }>, "many">;
    fulfillmentShipmentPackage: z.ZodOptional<z.ZodArray<z.ZodObject<{
        packageNumber: z.ZodNumber;
        carrierCode: z.ZodString;
        trackingNumber: z.ZodOptional<z.ZodString>;
        estimatedArrivalDate: z.ZodOptional<z.ZodString>;
    }, "strip", z.ZodTypeAny, {
        packageNumber: number;
        carrierCode: string;
        trackingNumber?: string | undefined;
        estimatedArrivalDate?: string | undefined;
    }, {
        packageNumber: number;
        carrierCode: string;
        trackingNumber?: string | undefined;
        estimatedArrivalDate?: string | undefined;
    }>, "many">>;
}, "strip", z.ZodTypeAny, {
    amazonShipmentId: string;
    fulfillmentCenterId: string;
    fulfillmentShipmentStatus: "PENDING" | "SHIPPED" | "CANCELLED_BY_FULFILLER" | "CANCELLED_BY_SELLER";
    fulfillmentShipmentItem: {
        quantity: number;
        sellerSku: string;
        sellerFulfillmentOrderItemId: string;
        packageNumber?: number | undefined;
    }[];
    estimatedArrivalDate?: string | undefined;
    shippingDate?: string | undefined;
    shippingNotes?: string[] | undefined;
    fulfillmentShipmentPackage?: {
        packageNumber: number;
        carrierCode: string;
        trackingNumber?: string | undefined;
        estimatedArrivalDate?: string | undefined;
    }[] | undefined;
}, {
    amazonShipmentId: string;
    fulfillmentCenterId: string;
    fulfillmentShipmentStatus: "PENDING" | "SHIPPED" | "CANCELLED_BY_FULFILLER" | "CANCELLED_BY_SELLER";
    fulfillmentShipmentItem: {
        quantity: number;
        sellerSku: string;
        sellerFulfillmentOrderItemId: string;
        packageNumber?: number | undefined;
    }[];
    estimatedArrivalDate?: string | undefined;
    shippingDate?: string | undefined;
    shippingNotes?: string[] | undefined;
    fulfillmentShipmentPackage?: {
        packageNumber: number;
        carrierCode: string;
        trackingNumber?: string | undefined;
        estimatedArrivalDate?: string | undefined;
    }[] | undefined;
}>;
/**
 * Amazon MCF get fulfillment order response schema
 */
export declare const MCFGetFulfillmentOrderResponseSchema: z.ZodObject<{
    fulfillmentOrder: z.ZodObject<{
        sellerFulfillmentOrderId: z.ZodString;
        marketplaceId: z.ZodString;
        displayableOrderId: z.ZodString;
        displayableOrderDate: z.ZodString;
        displayableOrderComment: z.ZodOptional<z.ZodString>;
        shippingSpeedCategory: z.ZodEnum<["Standard", "Expedited", "Priority", "ScheduledDelivery"]>;
        deliveryWindow: z.ZodOptional<z.ZodObject<{
            startDate: z.ZodString;
            endDate: z.ZodString;
        }, "strip", z.ZodTypeAny, {
            startDate: string;
            endDate: string;
        }, {
            startDate: string;
            endDate: string;
        }>>;
        destinationAddress: z.ZodObject<{
            name: z.ZodString;
            addressLine1: z.ZodString;
            addressLine2: z.ZodOptional<z.ZodString>;
            addressLine3: z.ZodOptional<z.ZodString>;
            city: z.ZodOptional<z.ZodString>;
            districtOrCounty: z.ZodOptional<z.ZodString>;
            stateOrRegion: z.ZodString;
            postalCode: z.ZodString;
            countryCode: z.ZodString;
            phone: z.ZodOptional<z.ZodString>;
            email: z.ZodOptional<z.ZodString>;
        }, "strip", z.ZodTypeAny, {
            name: string;
            addressLine1: string;
            stateOrRegion: string;
            postalCode: string;
            countryCode: string;
            city?: string | undefined;
            email?: string | undefined;
            addressLine2?: string | undefined;
            addressLine3?: string | undefined;
            districtOrCounty?: string | undefined;
            phone?: string | undefined;
        }, {
            name: string;
            addressLine1: string;
            stateOrRegion: string;
            postalCode: string;
            countryCode: string;
            city?: string | undefined;
            email?: string | undefined;
            addressLine2?: string | undefined;
            addressLine3?: string | undefined;
            districtOrCounty?: string | undefined;
            phone?: string | undefined;
        }>;
        fulfillmentAction: z.ZodOptional<z.ZodEnum<["Ship", "Hold"]>>;
        fulfillmentPolicy: z.ZodOptional<z.ZodEnum<["FillOrKill", "FillAll", "FillAllAvailable"]>>;
        codSettings: z.ZodOptional<z.ZodObject<{
            isCodRequired: z.ZodBoolean;
            codCharge: z.ZodOptional<z.ZodObject<{
                currencyCode: z.ZodString;
                value: z.ZodNumber;
            }, "strip", z.ZodTypeAny, {
                value: number;
                currencyCode: string;
            }, {
                value: number;
                currencyCode: string;
            }>>;
            codChargeTax: z.ZodOptional<z.ZodObject<{
                currencyCode: z.ZodString;
                value: z.ZodNumber;
            }, "strip", z.ZodTypeAny, {
                value: number;
                currencyCode: string;
            }, {
                value: number;
                currencyCode: string;
            }>>;
            shippingCharge: z.ZodOptional<z.ZodObject<{
                currencyCode: z.ZodString;
                value: z.ZodNumber;
            }, "strip", z.ZodTypeAny, {
                value: number;
                currencyCode: string;
            }, {
                value: number;
                currencyCode: string;
            }>>;
            shippingChargeTax: z.ZodOptional<z.ZodObject<{
                currencyCode: z.ZodString;
                value: z.ZodNumber;
            }, "strip", z.ZodTypeAny, {
                value: number;
                currencyCode: string;
            }, {
                value: number;
                currencyCode: string;
            }>>;
        }, "strip", z.ZodTypeAny, {
            isCodRequired: boolean;
            codCharge?: {
                value: number;
                currencyCode: string;
            } | undefined;
            codChargeTax?: {
                value: number;
                currencyCode: string;
            } | undefined;
            shippingCharge?: {
                value: number;
                currencyCode: string;
            } | undefined;
            shippingChargeTax?: {
                value: number;
                currencyCode: string;
            } | undefined;
        }, {
            isCodRequired: boolean;
            codCharge?: {
                value: number;
                currencyCode: string;
            } | undefined;
            codChargeTax?: {
                value: number;
                currencyCode: string;
            } | undefined;
            shippingCharge?: {
                value: number;
                currencyCode: string;
            } | undefined;
            shippingChargeTax?: {
                value: number;
                currencyCode: string;
            } | undefined;
        }>>;
        receivedDate: z.ZodOptional<z.ZodString>;
        fulfillmentOrderStatus: z.ZodNativeEnum<typeof MCFFulfillmentStatus>;
        statusUpdatedDate: z.ZodOptional<z.ZodString>;
        notificationEmails: z.ZodOptional<z.ZodArray<z.ZodString, "many">>;
        featureConstraints: z.ZodOptional<z.ZodArray<z.ZodOptional<z.ZodObject<{
            featureName: z.ZodString;
            featureFulfillmentPolicy: z.ZodEnum<["Required", "NotRequired"]>;
        }, "strip", z.ZodTypeAny, {
            featureName: string;
            featureFulfillmentPolicy: "Required" | "NotRequired";
        }, {
            featureName: string;
            featureFulfillmentPolicy: "Required" | "NotRequired";
        }>>, "many">>;
    }, "strip", z.ZodTypeAny, {
        marketplaceId: string;
        sellerFulfillmentOrderId: string;
        displayableOrderId: string;
        displayableOrderDate: string;
        shippingSpeedCategory: "Standard" | "Expedited" | "Priority" | "ScheduledDelivery";
        destinationAddress: {
            name: string;
            addressLine1: string;
            stateOrRegion: string;
            postalCode: string;
            countryCode: string;
            city?: string | undefined;
            email?: string | undefined;
            addressLine2?: string | undefined;
            addressLine3?: string | undefined;
            districtOrCounty?: string | undefined;
            phone?: string | undefined;
        };
        fulfillmentOrderStatus: MCFFulfillmentStatus;
        displayableOrderComment?: string | undefined;
        deliveryWindow?: {
            startDate: string;
            endDate: string;
        } | undefined;
        fulfillmentAction?: "Ship" | "Hold" | undefined;
        fulfillmentPolicy?: "FillOrKill" | "FillAll" | "FillAllAvailable" | undefined;
        codSettings?: {
            isCodRequired: boolean;
            codCharge?: {
                value: number;
                currencyCode: string;
            } | undefined;
            codChargeTax?: {
                value: number;
                currencyCode: string;
            } | undefined;
            shippingCharge?: {
                value: number;
                currencyCode: string;
            } | undefined;
            shippingChargeTax?: {
                value: number;
                currencyCode: string;
            } | undefined;
        } | undefined;
        notificationEmails?: string[] | undefined;
        featureConstraints?: ({
            featureName: string;
            featureFulfillmentPolicy: "Required" | "NotRequired";
        } | undefined)[] | undefined;
        receivedDate?: string | undefined;
        statusUpdatedDate?: string | undefined;
    }, {
        marketplaceId: string;
        sellerFulfillmentOrderId: string;
        displayableOrderId: string;
        displayableOrderDate: string;
        shippingSpeedCategory: "Standard" | "Expedited" | "Priority" | "ScheduledDelivery";
        destinationAddress: {
            name: string;
            addressLine1: string;
            stateOrRegion: string;
            postalCode: string;
            countryCode: string;
            city?: string | undefined;
            email?: string | undefined;
            addressLine2?: string | undefined;
            addressLine3?: string | undefined;
            districtOrCounty?: string | undefined;
            phone?: string | undefined;
        };
        fulfillmentOrderStatus: MCFFulfillmentStatus;
        displayableOrderComment?: string | undefined;
        deliveryWindow?: {
            startDate: string;
            endDate: string;
        } | undefined;
        fulfillmentAction?: "Ship" | "Hold" | undefined;
        fulfillmentPolicy?: "FillOrKill" | "FillAll" | "FillAllAvailable" | undefined;
        codSettings?: {
            isCodRequired: boolean;
            codCharge?: {
                value: number;
                currencyCode: string;
            } | undefined;
            codChargeTax?: {
                value: number;
                currencyCode: string;
            } | undefined;
            shippingCharge?: {
                value: number;
                currencyCode: string;
            } | undefined;
            shippingChargeTax?: {
                value: number;
                currencyCode: string;
            } | undefined;
        } | undefined;
        notificationEmails?: string[] | undefined;
        featureConstraints?: ({
            featureName: string;
            featureFulfillmentPolicy: "Required" | "NotRequired";
        } | undefined)[] | undefined;
        receivedDate?: string | undefined;
        statusUpdatedDate?: string | undefined;
    }>;
    fulfillmentOrderItems: z.ZodArray<z.ZodObject<{
        sellerSku: z.ZodString;
        sellerFulfillmentOrderItemId: z.ZodString;
        quantity: z.ZodNumber;
        giftMessage: z.ZodOptional<z.ZodString>;
        displayableComment: z.ZodOptional<z.ZodString>;
        fulfillmentNetworkSku: z.ZodOptional<z.ZodString>;
        orderItemDisposition: z.ZodOptional<z.ZodString>;
        perUnitDeclaredValue: z.ZodOptional<z.ZodObject<{
            currencyCode: z.ZodString;
            value: z.ZodNumber;
        }, "strip", z.ZodTypeAny, {
            value: number;
            currencyCode: string;
        }, {
            value: number;
            currencyCode: string;
        }>>;
        perUnitPrice: z.ZodOptional<z.ZodObject<{
            currencyCode: z.ZodString;
            value: z.ZodNumber;
        }, "strip", z.ZodTypeAny, {
            value: number;
            currencyCode: string;
        }, {
            value: number;
            currencyCode: string;
        }>>;
        perUnitTax: z.ZodOptional<z.ZodObject<{
            currencyCode: z.ZodString;
            value: z.ZodNumber;
        }, "strip", z.ZodTypeAny, {
            value: number;
            currencyCode: string;
        }, {
            value: number;
            currencyCode: string;
        }>>;
    }, "strip", z.ZodTypeAny, {
        quantity: number;
        sellerSku: string;
        sellerFulfillmentOrderItemId: string;
        giftMessage?: string | undefined;
        displayableComment?: string | undefined;
        fulfillmentNetworkSku?: string | undefined;
        orderItemDisposition?: string | undefined;
        perUnitDeclaredValue?: {
            value: number;
            currencyCode: string;
        } | undefined;
        perUnitPrice?: {
            value: number;
            currencyCode: string;
        } | undefined;
        perUnitTax?: {
            value: number;
            currencyCode: string;
        } | undefined;
    }, {
        quantity: number;
        sellerSku: string;
        sellerFulfillmentOrderItemId: string;
        giftMessage?: string | undefined;
        displayableComment?: string | undefined;
        fulfillmentNetworkSku?: string | undefined;
        orderItemDisposition?: string | undefined;
        perUnitDeclaredValue?: {
            value: number;
            currencyCode: string;
        } | undefined;
        perUnitPrice?: {
            value: number;
            currencyCode: string;
        } | undefined;
        perUnitTax?: {
            value: number;
            currencyCode: string;
        } | undefined;
    }>, "many">;
    fulfillmentShipments: z.ZodOptional<z.ZodArray<z.ZodObject<{
        amazonShipmentId: z.ZodString;
        fulfillmentCenterId: z.ZodString;
        fulfillmentShipmentStatus: z.ZodEnum<["PENDING", "SHIPPED", "CANCELLED_BY_FULFILLER", "CANCELLED_BY_SELLER"]>;
        shippingDate: z.ZodOptional<z.ZodString>;
        estimatedArrivalDate: z.ZodOptional<z.ZodString>;
        shippingNotes: z.ZodOptional<z.ZodArray<z.ZodString, "many">>;
        fulfillmentShipmentItem: z.ZodArray<z.ZodObject<{
            sellerSku: z.ZodString;
            sellerFulfillmentOrderItemId: z.ZodString;
            quantity: z.ZodNumber;
            packageNumber: z.ZodOptional<z.ZodNumber>;
        }, "strip", z.ZodTypeAny, {
            quantity: number;
            sellerSku: string;
            sellerFulfillmentOrderItemId: string;
            packageNumber?: number | undefined;
        }, {
            quantity: number;
            sellerSku: string;
            sellerFulfillmentOrderItemId: string;
            packageNumber?: number | undefined;
        }>, "many">;
        fulfillmentShipmentPackage: z.ZodOptional<z.ZodArray<z.ZodObject<{
            packageNumber: z.ZodNumber;
            carrierCode: z.ZodString;
            trackingNumber: z.ZodOptional<z.ZodString>;
            estimatedArrivalDate: z.ZodOptional<z.ZodString>;
        }, "strip", z.ZodTypeAny, {
            packageNumber: number;
            carrierCode: string;
            trackingNumber?: string | undefined;
            estimatedArrivalDate?: string | undefined;
        }, {
            packageNumber: number;
            carrierCode: string;
            trackingNumber?: string | undefined;
            estimatedArrivalDate?: string | undefined;
        }>, "many">>;
    }, "strip", z.ZodTypeAny, {
        amazonShipmentId: string;
        fulfillmentCenterId: string;
        fulfillmentShipmentStatus: "PENDING" | "SHIPPED" | "CANCELLED_BY_FULFILLER" | "CANCELLED_BY_SELLER";
        fulfillmentShipmentItem: {
            quantity: number;
            sellerSku: string;
            sellerFulfillmentOrderItemId: string;
            packageNumber?: number | undefined;
        }[];
        estimatedArrivalDate?: string | undefined;
        shippingDate?: string | undefined;
        shippingNotes?: string[] | undefined;
        fulfillmentShipmentPackage?: {
            packageNumber: number;
            carrierCode: string;
            trackingNumber?: string | undefined;
            estimatedArrivalDate?: string | undefined;
        }[] | undefined;
    }, {
        amazonShipmentId: string;
        fulfillmentCenterId: string;
        fulfillmentShipmentStatus: "PENDING" | "SHIPPED" | "CANCELLED_BY_FULFILLER" | "CANCELLED_BY_SELLER";
        fulfillmentShipmentItem: {
            quantity: number;
            sellerSku: string;
            sellerFulfillmentOrderItemId: string;
            packageNumber?: number | undefined;
        }[];
        estimatedArrivalDate?: string | undefined;
        shippingDate?: string | undefined;
        shippingNotes?: string[] | undefined;
        fulfillmentShipmentPackage?: {
            packageNumber: number;
            carrierCode: string;
            trackingNumber?: string | undefined;
            estimatedArrivalDate?: string | undefined;
        }[] | undefined;
    }>, "many">>;
    returnItems: z.ZodOptional<z.ZodArray<z.ZodAny, "many">>;
    returnAuthorizations: z.ZodOptional<z.ZodArray<z.ZodAny, "many">>;
}, "strip", z.ZodTypeAny, {
    fulfillmentOrder: {
        marketplaceId: string;
        sellerFulfillmentOrderId: string;
        displayableOrderId: string;
        displayableOrderDate: string;
        shippingSpeedCategory: "Standard" | "Expedited" | "Priority" | "ScheduledDelivery";
        destinationAddress: {
            name: string;
            addressLine1: string;
            stateOrRegion: string;
            postalCode: string;
            countryCode: string;
            city?: string | undefined;
            email?: string | undefined;
            addressLine2?: string | undefined;
            addressLine3?: string | undefined;
            districtOrCounty?: string | undefined;
            phone?: string | undefined;
        };
        fulfillmentOrderStatus: MCFFulfillmentStatus;
        displayableOrderComment?: string | undefined;
        deliveryWindow?: {
            startDate: string;
            endDate: string;
        } | undefined;
        fulfillmentAction?: "Ship" | "Hold" | undefined;
        fulfillmentPolicy?: "FillOrKill" | "FillAll" | "FillAllAvailable" | undefined;
        codSettings?: {
            isCodRequired: boolean;
            codCharge?: {
                value: number;
                currencyCode: string;
            } | undefined;
            codChargeTax?: {
                value: number;
                currencyCode: string;
            } | undefined;
            shippingCharge?: {
                value: number;
                currencyCode: string;
            } | undefined;
            shippingChargeTax?: {
                value: number;
                currencyCode: string;
            } | undefined;
        } | undefined;
        notificationEmails?: string[] | undefined;
        featureConstraints?: ({
            featureName: string;
            featureFulfillmentPolicy: "Required" | "NotRequired";
        } | undefined)[] | undefined;
        receivedDate?: string | undefined;
        statusUpdatedDate?: string | undefined;
    };
    fulfillmentOrderItems: {
        quantity: number;
        sellerSku: string;
        sellerFulfillmentOrderItemId: string;
        giftMessage?: string | undefined;
        displayableComment?: string | undefined;
        fulfillmentNetworkSku?: string | undefined;
        orderItemDisposition?: string | undefined;
        perUnitDeclaredValue?: {
            value: number;
            currencyCode: string;
        } | undefined;
        perUnitPrice?: {
            value: number;
            currencyCode: string;
        } | undefined;
        perUnitTax?: {
            value: number;
            currencyCode: string;
        } | undefined;
    }[];
    fulfillmentShipments?: {
        amazonShipmentId: string;
        fulfillmentCenterId: string;
        fulfillmentShipmentStatus: "PENDING" | "SHIPPED" | "CANCELLED_BY_FULFILLER" | "CANCELLED_BY_SELLER";
        fulfillmentShipmentItem: {
            quantity: number;
            sellerSku: string;
            sellerFulfillmentOrderItemId: string;
            packageNumber?: number | undefined;
        }[];
        estimatedArrivalDate?: string | undefined;
        shippingDate?: string | undefined;
        shippingNotes?: string[] | undefined;
        fulfillmentShipmentPackage?: {
            packageNumber: number;
            carrierCode: string;
            trackingNumber?: string | undefined;
            estimatedArrivalDate?: string | undefined;
        }[] | undefined;
    }[] | undefined;
    returnItems?: any[] | undefined;
    returnAuthorizations?: any[] | undefined;
}, {
    fulfillmentOrder: {
        marketplaceId: string;
        sellerFulfillmentOrderId: string;
        displayableOrderId: string;
        displayableOrderDate: string;
        shippingSpeedCategory: "Standard" | "Expedited" | "Priority" | "ScheduledDelivery";
        destinationAddress: {
            name: string;
            addressLine1: string;
            stateOrRegion: string;
            postalCode: string;
            countryCode: string;
            city?: string | undefined;
            email?: string | undefined;
            addressLine2?: string | undefined;
            addressLine3?: string | undefined;
            districtOrCounty?: string | undefined;
            phone?: string | undefined;
        };
        fulfillmentOrderStatus: MCFFulfillmentStatus;
        displayableOrderComment?: string | undefined;
        deliveryWindow?: {
            startDate: string;
            endDate: string;
        } | undefined;
        fulfillmentAction?: "Ship" | "Hold" | undefined;
        fulfillmentPolicy?: "FillOrKill" | "FillAll" | "FillAllAvailable" | undefined;
        codSettings?: {
            isCodRequired: boolean;
            codCharge?: {
                value: number;
                currencyCode: string;
            } | undefined;
            codChargeTax?: {
                value: number;
                currencyCode: string;
            } | undefined;
            shippingCharge?: {
                value: number;
                currencyCode: string;
            } | undefined;
            shippingChargeTax?: {
                value: number;
                currencyCode: string;
            } | undefined;
        } | undefined;
        notificationEmails?: string[] | undefined;
        featureConstraints?: ({
            featureName: string;
            featureFulfillmentPolicy: "Required" | "NotRequired";
        } | undefined)[] | undefined;
        receivedDate?: string | undefined;
        statusUpdatedDate?: string | undefined;
    };
    fulfillmentOrderItems: {
        quantity: number;
        sellerSku: string;
        sellerFulfillmentOrderItemId: string;
        giftMessage?: string | undefined;
        displayableComment?: string | undefined;
        fulfillmentNetworkSku?: string | undefined;
        orderItemDisposition?: string | undefined;
        perUnitDeclaredValue?: {
            value: number;
            currencyCode: string;
        } | undefined;
        perUnitPrice?: {
            value: number;
            currencyCode: string;
        } | undefined;
        perUnitTax?: {
            value: number;
            currencyCode: string;
        } | undefined;
    }[];
    fulfillmentShipments?: {
        amazonShipmentId: string;
        fulfillmentCenterId: string;
        fulfillmentShipmentStatus: "PENDING" | "SHIPPED" | "CANCELLED_BY_FULFILLER" | "CANCELLED_BY_SELLER";
        fulfillmentShipmentItem: {
            quantity: number;
            sellerSku: string;
            sellerFulfillmentOrderItemId: string;
            packageNumber?: number | undefined;
        }[];
        estimatedArrivalDate?: string | undefined;
        shippingDate?: string | undefined;
        shippingNotes?: string[] | undefined;
        fulfillmentShipmentPackage?: {
            packageNumber: number;
            carrierCode: string;
            trackingNumber?: string | undefined;
            estimatedArrivalDate?: string | undefined;
        }[] | undefined;
    }[] | undefined;
    returnItems?: any[] | undefined;
    returnAuthorizations?: any[] | undefined;
}>;
/**
 * Amazon MCF create fulfillment order response schema
 */
export declare const MCFCreateFulfillmentOrderResponseSchema: z.ZodObject<{
    fulfillmentOrder: z.ZodOptional<z.ZodObject<{
        sellerFulfillmentOrderId: z.ZodString;
        marketplaceId: z.ZodString;
        displayableOrderId: z.ZodString;
        displayableOrderDate: z.ZodString;
        displayableOrderComment: z.ZodOptional<z.ZodString>;
        shippingSpeedCategory: z.ZodEnum<["Standard", "Expedited", "Priority", "ScheduledDelivery"]>;
        deliveryWindow: z.ZodOptional<z.ZodObject<{
            startDate: z.ZodString;
            endDate: z.ZodString;
        }, "strip", z.ZodTypeAny, {
            startDate: string;
            endDate: string;
        }, {
            startDate: string;
            endDate: string;
        }>>;
        destinationAddress: z.ZodObject<{
            name: z.ZodString;
            addressLine1: z.ZodString;
            addressLine2: z.ZodOptional<z.ZodString>;
            addressLine3: z.ZodOptional<z.ZodString>;
            city: z.ZodOptional<z.ZodString>;
            districtOrCounty: z.ZodOptional<z.ZodString>;
            stateOrRegion: z.ZodString;
            postalCode: z.ZodString;
            countryCode: z.ZodString;
            phone: z.ZodOptional<z.ZodString>;
            email: z.ZodOptional<z.ZodString>;
        }, "strip", z.ZodTypeAny, {
            name: string;
            addressLine1: string;
            stateOrRegion: string;
            postalCode: string;
            countryCode: string;
            city?: string | undefined;
            email?: string | undefined;
            addressLine2?: string | undefined;
            addressLine3?: string | undefined;
            districtOrCounty?: string | undefined;
            phone?: string | undefined;
        }, {
            name: string;
            addressLine1: string;
            stateOrRegion: string;
            postalCode: string;
            countryCode: string;
            city?: string | undefined;
            email?: string | undefined;
            addressLine2?: string | undefined;
            addressLine3?: string | undefined;
            districtOrCounty?: string | undefined;
            phone?: string | undefined;
        }>;
        fulfillmentAction: z.ZodOptional<z.ZodEnum<["Ship", "Hold"]>>;
        fulfillmentPolicy: z.ZodOptional<z.ZodEnum<["FillOrKill", "FillAll", "FillAllAvailable"]>>;
        codSettings: z.ZodOptional<z.ZodObject<{
            isCodRequired: z.ZodBoolean;
            codCharge: z.ZodOptional<z.ZodObject<{
                currencyCode: z.ZodString;
                value: z.ZodNumber;
            }, "strip", z.ZodTypeAny, {
                value: number;
                currencyCode: string;
            }, {
                value: number;
                currencyCode: string;
            }>>;
            codChargeTax: z.ZodOptional<z.ZodObject<{
                currencyCode: z.ZodString;
                value: z.ZodNumber;
            }, "strip", z.ZodTypeAny, {
                value: number;
                currencyCode: string;
            }, {
                value: number;
                currencyCode: string;
            }>>;
            shippingCharge: z.ZodOptional<z.ZodObject<{
                currencyCode: z.ZodString;
                value: z.ZodNumber;
            }, "strip", z.ZodTypeAny, {
                value: number;
                currencyCode: string;
            }, {
                value: number;
                currencyCode: string;
            }>>;
            shippingChargeTax: z.ZodOptional<z.ZodObject<{
                currencyCode: z.ZodString;
                value: z.ZodNumber;
            }, "strip", z.ZodTypeAny, {
                value: number;
                currencyCode: string;
            }, {
                value: number;
                currencyCode: string;
            }>>;
        }, "strip", z.ZodTypeAny, {
            isCodRequired: boolean;
            codCharge?: {
                value: number;
                currencyCode: string;
            } | undefined;
            codChargeTax?: {
                value: number;
                currencyCode: string;
            } | undefined;
            shippingCharge?: {
                value: number;
                currencyCode: string;
            } | undefined;
            shippingChargeTax?: {
                value: number;
                currencyCode: string;
            } | undefined;
        }, {
            isCodRequired: boolean;
            codCharge?: {
                value: number;
                currencyCode: string;
            } | undefined;
            codChargeTax?: {
                value: number;
                currencyCode: string;
            } | undefined;
            shippingCharge?: {
                value: number;
                currencyCode: string;
            } | undefined;
            shippingChargeTax?: {
                value: number;
                currencyCode: string;
            } | undefined;
        }>>;
        receivedDate: z.ZodOptional<z.ZodString>;
        fulfillmentOrderStatus: z.ZodNativeEnum<typeof MCFFulfillmentStatus>;
        statusUpdatedDate: z.ZodOptional<z.ZodString>;
        notificationEmails: z.ZodOptional<z.ZodArray<z.ZodString, "many">>;
        featureConstraints: z.ZodOptional<z.ZodArray<z.ZodOptional<z.ZodObject<{
            featureName: z.ZodString;
            featureFulfillmentPolicy: z.ZodEnum<["Required", "NotRequired"]>;
        }, "strip", z.ZodTypeAny, {
            featureName: string;
            featureFulfillmentPolicy: "Required" | "NotRequired";
        }, {
            featureName: string;
            featureFulfillmentPolicy: "Required" | "NotRequired";
        }>>, "many">>;
    }, "strip", z.ZodTypeAny, {
        marketplaceId: string;
        sellerFulfillmentOrderId: string;
        displayableOrderId: string;
        displayableOrderDate: string;
        shippingSpeedCategory: "Standard" | "Expedited" | "Priority" | "ScheduledDelivery";
        destinationAddress: {
            name: string;
            addressLine1: string;
            stateOrRegion: string;
            postalCode: string;
            countryCode: string;
            city?: string | undefined;
            email?: string | undefined;
            addressLine2?: string | undefined;
            addressLine3?: string | undefined;
            districtOrCounty?: string | undefined;
            phone?: string | undefined;
        };
        fulfillmentOrderStatus: MCFFulfillmentStatus;
        displayableOrderComment?: string | undefined;
        deliveryWindow?: {
            startDate: string;
            endDate: string;
        } | undefined;
        fulfillmentAction?: "Ship" | "Hold" | undefined;
        fulfillmentPolicy?: "FillOrKill" | "FillAll" | "FillAllAvailable" | undefined;
        codSettings?: {
            isCodRequired: boolean;
            codCharge?: {
                value: number;
                currencyCode: string;
            } | undefined;
            codChargeTax?: {
                value: number;
                currencyCode: string;
            } | undefined;
            shippingCharge?: {
                value: number;
                currencyCode: string;
            } | undefined;
            shippingChargeTax?: {
                value: number;
                currencyCode: string;
            } | undefined;
        } | undefined;
        notificationEmails?: string[] | undefined;
        featureConstraints?: ({
            featureName: string;
            featureFulfillmentPolicy: "Required" | "NotRequired";
        } | undefined)[] | undefined;
        receivedDate?: string | undefined;
        statusUpdatedDate?: string | undefined;
    }, {
        marketplaceId: string;
        sellerFulfillmentOrderId: string;
        displayableOrderId: string;
        displayableOrderDate: string;
        shippingSpeedCategory: "Standard" | "Expedited" | "Priority" | "ScheduledDelivery";
        destinationAddress: {
            name: string;
            addressLine1: string;
            stateOrRegion: string;
            postalCode: string;
            countryCode: string;
            city?: string | undefined;
            email?: string | undefined;
            addressLine2?: string | undefined;
            addressLine3?: string | undefined;
            districtOrCounty?: string | undefined;
            phone?: string | undefined;
        };
        fulfillmentOrderStatus: MCFFulfillmentStatus;
        displayableOrderComment?: string | undefined;
        deliveryWindow?: {
            startDate: string;
            endDate: string;
        } | undefined;
        fulfillmentAction?: "Ship" | "Hold" | undefined;
        fulfillmentPolicy?: "FillOrKill" | "FillAll" | "FillAllAvailable" | undefined;
        codSettings?: {
            isCodRequired: boolean;
            codCharge?: {
                value: number;
                currencyCode: string;
            } | undefined;
            codChargeTax?: {
                value: number;
                currencyCode: string;
            } | undefined;
            shippingCharge?: {
                value: number;
                currencyCode: string;
            } | undefined;
            shippingChargeTax?: {
                value: number;
                currencyCode: string;
            } | undefined;
        } | undefined;
        notificationEmails?: string[] | undefined;
        featureConstraints?: ({
            featureName: string;
            featureFulfillmentPolicy: "Required" | "NotRequired";
        } | undefined)[] | undefined;
        receivedDate?: string | undefined;
        statusUpdatedDate?: string | undefined;
    }>>;
    errors: z.ZodOptional<z.ZodArray<z.ZodObject<{
        code: z.ZodString;
        message: z.ZodString;
        details: z.ZodOptional<z.ZodString>;
    }, "strip", z.ZodTypeAny, {
        code: string;
        message: string;
        details?: string | undefined;
    }, {
        code: string;
        message: string;
        details?: string | undefined;
    }>, "many">>;
}, "strip", z.ZodTypeAny, {
    fulfillmentOrder?: {
        marketplaceId: string;
        sellerFulfillmentOrderId: string;
        displayableOrderId: string;
        displayableOrderDate: string;
        shippingSpeedCategory: "Standard" | "Expedited" | "Priority" | "ScheduledDelivery";
        destinationAddress: {
            name: string;
            addressLine1: string;
            stateOrRegion: string;
            postalCode: string;
            countryCode: string;
            city?: string | undefined;
            email?: string | undefined;
            addressLine2?: string | undefined;
            addressLine3?: string | undefined;
            districtOrCounty?: string | undefined;
            phone?: string | undefined;
        };
        fulfillmentOrderStatus: MCFFulfillmentStatus;
        displayableOrderComment?: string | undefined;
        deliveryWindow?: {
            startDate: string;
            endDate: string;
        } | undefined;
        fulfillmentAction?: "Ship" | "Hold" | undefined;
        fulfillmentPolicy?: "FillOrKill" | "FillAll" | "FillAllAvailable" | undefined;
        codSettings?: {
            isCodRequired: boolean;
            codCharge?: {
                value: number;
                currencyCode: string;
            } | undefined;
            codChargeTax?: {
                value: number;
                currencyCode: string;
            } | undefined;
            shippingCharge?: {
                value: number;
                currencyCode: string;
            } | undefined;
            shippingChargeTax?: {
                value: number;
                currencyCode: string;
            } | undefined;
        } | undefined;
        notificationEmails?: string[] | undefined;
        featureConstraints?: ({
            featureName: string;
            featureFulfillmentPolicy: "Required" | "NotRequired";
        } | undefined)[] | undefined;
        receivedDate?: string | undefined;
        statusUpdatedDate?: string | undefined;
    } | undefined;
    errors?: {
        code: string;
        message: string;
        details?: string | undefined;
    }[] | undefined;
}, {
    fulfillmentOrder?: {
        marketplaceId: string;
        sellerFulfillmentOrderId: string;
        displayableOrderId: string;
        displayableOrderDate: string;
        shippingSpeedCategory: "Standard" | "Expedited" | "Priority" | "ScheduledDelivery";
        destinationAddress: {
            name: string;
            addressLine1: string;
            stateOrRegion: string;
            postalCode: string;
            countryCode: string;
            city?: string | undefined;
            email?: string | undefined;
            addressLine2?: string | undefined;
            addressLine3?: string | undefined;
            districtOrCounty?: string | undefined;
            phone?: string | undefined;
        };
        fulfillmentOrderStatus: MCFFulfillmentStatus;
        displayableOrderComment?: string | undefined;
        deliveryWindow?: {
            startDate: string;
            endDate: string;
        } | undefined;
        fulfillmentAction?: "Ship" | "Hold" | undefined;
        fulfillmentPolicy?: "FillOrKill" | "FillAll" | "FillAllAvailable" | undefined;
        codSettings?: {
            isCodRequired: boolean;
            codCharge?: {
                value: number;
                currencyCode: string;
            } | undefined;
            codChargeTax?: {
                value: number;
                currencyCode: string;
            } | undefined;
            shippingCharge?: {
                value: number;
                currencyCode: string;
            } | undefined;
            shippingChargeTax?: {
                value: number;
                currencyCode: string;
            } | undefined;
        } | undefined;
        notificationEmails?: string[] | undefined;
        featureConstraints?: ({
            featureName: string;
            featureFulfillmentPolicy: "Required" | "NotRequired";
        } | undefined)[] | undefined;
        receivedDate?: string | undefined;
        statusUpdatedDate?: string | undefined;
    } | undefined;
    errors?: {
        code: string;
        message: string;
        details?: string | undefined;
    }[] | undefined;
}>;
/**
 * Amazon MCF update fulfillment order request schema
 */
export declare const MCFUpdateFulfillmentOrderRequestSchema: z.ZodObject<{
    marketplaceId: z.ZodOptional<z.ZodString>;
    displayableOrderId: z.ZodOptional<z.ZodString>;
    displayableOrderDate: z.ZodOptional<z.ZodString>;
    displayableOrderComment: z.ZodOptional<z.ZodString>;
    shippingSpeedCategory: z.ZodOptional<z.ZodEnum<["Standard", "Expedited", "Priority", "ScheduledDelivery"]>>;
    destinationAddress: z.ZodOptional<z.ZodObject<{
        name: z.ZodString;
        addressLine1: z.ZodString;
        addressLine2: z.ZodOptional<z.ZodString>;
        addressLine3: z.ZodOptional<z.ZodString>;
        city: z.ZodOptional<z.ZodString>;
        districtOrCounty: z.ZodOptional<z.ZodString>;
        stateOrRegion: z.ZodString;
        postalCode: z.ZodString;
        countryCode: z.ZodString;
        phone: z.ZodOptional<z.ZodString>;
        email: z.ZodOptional<z.ZodString>;
    }, "strip", z.ZodTypeAny, {
        name: string;
        addressLine1: string;
        stateOrRegion: string;
        postalCode: string;
        countryCode: string;
        city?: string | undefined;
        email?: string | undefined;
        addressLine2?: string | undefined;
        addressLine3?: string | undefined;
        districtOrCounty?: string | undefined;
        phone?: string | undefined;
    }, {
        name: string;
        addressLine1: string;
        stateOrRegion: string;
        postalCode: string;
        countryCode: string;
        city?: string | undefined;
        email?: string | undefined;
        addressLine2?: string | undefined;
        addressLine3?: string | undefined;
        districtOrCounty?: string | undefined;
        phone?: string | undefined;
    }>>;
    fulfillmentAction: z.ZodOptional<z.ZodEnum<["Ship", "Hold"]>>;
    fulfillmentPolicy: z.ZodOptional<z.ZodEnum<["FillOrKill", "FillAll", "FillAllAvailable"]>>;
    shipFromCountryCode: z.ZodOptional<z.ZodString>;
    notificationEmails: z.ZodOptional<z.ZodArray<z.ZodString, "many">>;
    featureConstraints: z.ZodOptional<z.ZodArray<z.ZodOptional<z.ZodObject<{
        featureName: z.ZodString;
        featureFulfillmentPolicy: z.ZodEnum<["Required", "NotRequired"]>;
    }, "strip", z.ZodTypeAny, {
        featureName: string;
        featureFulfillmentPolicy: "Required" | "NotRequired";
    }, {
        featureName: string;
        featureFulfillmentPolicy: "Required" | "NotRequired";
    }>>, "many">>;
    items: z.ZodOptional<z.ZodArray<z.ZodObject<{
        sellerSku: z.ZodString;
        sellerFulfillmentOrderItemId: z.ZodString;
        quantity: z.ZodNumber;
        giftMessage: z.ZodOptional<z.ZodString>;
        displayableComment: z.ZodOptional<z.ZodString>;
        fulfillmentNetworkSku: z.ZodOptional<z.ZodString>;
        orderItemDisposition: z.ZodOptional<z.ZodString>;
        perUnitDeclaredValue: z.ZodOptional<z.ZodObject<{
            currencyCode: z.ZodString;
            value: z.ZodNumber;
        }, "strip", z.ZodTypeAny, {
            value: number;
            currencyCode: string;
        }, {
            value: number;
            currencyCode: string;
        }>>;
        perUnitPrice: z.ZodOptional<z.ZodObject<{
            currencyCode: z.ZodString;
            value: z.ZodNumber;
        }, "strip", z.ZodTypeAny, {
            value: number;
            currencyCode: string;
        }, {
            value: number;
            currencyCode: string;
        }>>;
        perUnitTax: z.ZodOptional<z.ZodObject<{
            currencyCode: z.ZodString;
            value: z.ZodNumber;
        }, "strip", z.ZodTypeAny, {
            value: number;
            currencyCode: string;
        }, {
            value: number;
            currencyCode: string;
        }>>;
    }, "strip", z.ZodTypeAny, {
        quantity: number;
        sellerSku: string;
        sellerFulfillmentOrderItemId: string;
        giftMessage?: string | undefined;
        displayableComment?: string | undefined;
        fulfillmentNetworkSku?: string | undefined;
        orderItemDisposition?: string | undefined;
        perUnitDeclaredValue?: {
            value: number;
            currencyCode: string;
        } | undefined;
        perUnitPrice?: {
            value: number;
            currencyCode: string;
        } | undefined;
        perUnitTax?: {
            value: number;
            currencyCode: string;
        } | undefined;
    }, {
        quantity: number;
        sellerSku: string;
        sellerFulfillmentOrderItemId: string;
        giftMessage?: string | undefined;
        displayableComment?: string | undefined;
        fulfillmentNetworkSku?: string | undefined;
        orderItemDisposition?: string | undefined;
        perUnitDeclaredValue?: {
            value: number;
            currencyCode: string;
        } | undefined;
        perUnitPrice?: {
            value: number;
            currencyCode: string;
        } | undefined;
        perUnitTax?: {
            value: number;
            currencyCode: string;
        } | undefined;
    }>, "many">>;
}, "strip", z.ZodTypeAny, {
    items?: {
        quantity: number;
        sellerSku: string;
        sellerFulfillmentOrderItemId: string;
        giftMessage?: string | undefined;
        displayableComment?: string | undefined;
        fulfillmentNetworkSku?: string | undefined;
        orderItemDisposition?: string | undefined;
        perUnitDeclaredValue?: {
            value: number;
            currencyCode: string;
        } | undefined;
        perUnitPrice?: {
            value: number;
            currencyCode: string;
        } | undefined;
        perUnitTax?: {
            value: number;
            currencyCode: string;
        } | undefined;
    }[] | undefined;
    marketplaceId?: string | undefined;
    displayableOrderId?: string | undefined;
    displayableOrderDate?: string | undefined;
    displayableOrderComment?: string | undefined;
    shippingSpeedCategory?: "Standard" | "Expedited" | "Priority" | "ScheduledDelivery" | undefined;
    destinationAddress?: {
        name: string;
        addressLine1: string;
        stateOrRegion: string;
        postalCode: string;
        countryCode: string;
        city?: string | undefined;
        email?: string | undefined;
        addressLine2?: string | undefined;
        addressLine3?: string | undefined;
        districtOrCounty?: string | undefined;
        phone?: string | undefined;
    } | undefined;
    fulfillmentAction?: "Ship" | "Hold" | undefined;
    fulfillmentPolicy?: "FillOrKill" | "FillAll" | "FillAllAvailable" | undefined;
    shipFromCountryCode?: string | undefined;
    notificationEmails?: string[] | undefined;
    featureConstraints?: ({
        featureName: string;
        featureFulfillmentPolicy: "Required" | "NotRequired";
    } | undefined)[] | undefined;
}, {
    items?: {
        quantity: number;
        sellerSku: string;
        sellerFulfillmentOrderItemId: string;
        giftMessage?: string | undefined;
        displayableComment?: string | undefined;
        fulfillmentNetworkSku?: string | undefined;
        orderItemDisposition?: string | undefined;
        perUnitDeclaredValue?: {
            value: number;
            currencyCode: string;
        } | undefined;
        perUnitPrice?: {
            value: number;
            currencyCode: string;
        } | undefined;
        perUnitTax?: {
            value: number;
            currencyCode: string;
        } | undefined;
    }[] | undefined;
    marketplaceId?: string | undefined;
    displayableOrderId?: string | undefined;
    displayableOrderDate?: string | undefined;
    displayableOrderComment?: string | undefined;
    shippingSpeedCategory?: "Standard" | "Expedited" | "Priority" | "ScheduledDelivery" | undefined;
    destinationAddress?: {
        name: string;
        addressLine1: string;
        stateOrRegion: string;
        postalCode: string;
        countryCode: string;
        city?: string | undefined;
        email?: string | undefined;
        addressLine2?: string | undefined;
        addressLine3?: string | undefined;
        districtOrCounty?: string | undefined;
        phone?: string | undefined;
    } | undefined;
    fulfillmentAction?: "Ship" | "Hold" | undefined;
    fulfillmentPolicy?: "FillOrKill" | "FillAll" | "FillAllAvailable" | undefined;
    shipFromCountryCode?: string | undefined;
    notificationEmails?: string[] | undefined;
    featureConstraints?: ({
        featureName: string;
        featureFulfillmentPolicy: "Required" | "NotRequired";
    } | undefined)[] | undefined;
}>;
/**
 * Amazon MCF cancel fulfillment order response schema
 */
export declare const MCFCancelFulfillmentOrderResponseSchema: z.ZodObject<{
    errors: z.ZodOptional<z.ZodArray<z.ZodObject<{
        code: z.ZodString;
        message: z.ZodString;
        details: z.ZodOptional<z.ZodString>;
    }, "strip", z.ZodTypeAny, {
        code: string;
        message: string;
        details?: string | undefined;
    }, {
        code: string;
        message: string;
        details?: string | undefined;
    }>, "many">>;
}, "strip", z.ZodTypeAny, {
    errors?: {
        code: string;
        message: string;
        details?: string | undefined;
    }[] | undefined;
}, {
    errors?: {
        code: string;
        message: string;
        details?: string | undefined;
    }[] | undefined;
}>;
/**
 * Amazon MCF tracking event schema
 */
export declare const MCFTrackingEventSchema: z.ZodObject<{
    eventDate: z.ZodString;
    eventAddress: z.ZodOptional<z.ZodObject<{
        name: z.ZodOptional<z.ZodString>;
        addressLine1: z.ZodOptional<z.ZodString>;
        addressLine2: z.ZodOptional<z.ZodOptional<z.ZodString>>;
        addressLine3: z.ZodOptional<z.ZodOptional<z.ZodString>>;
        city: z.ZodOptional<z.ZodOptional<z.ZodString>>;
        districtOrCounty: z.ZodOptional<z.ZodOptional<z.ZodString>>;
        stateOrRegion: z.ZodOptional<z.ZodString>;
        postalCode: z.ZodOptional<z.ZodString>;
        countryCode: z.ZodOptional<z.ZodString>;
        phone: z.ZodOptional<z.ZodOptional<z.ZodString>>;
        email: z.ZodOptional<z.ZodOptional<z.ZodString>>;
    }, "strip", z.ZodTypeAny, {
        city?: string | undefined;
        email?: string | undefined;
        name?: string | undefined;
        addressLine1?: string | undefined;
        addressLine2?: string | undefined;
        addressLine3?: string | undefined;
        districtOrCounty?: string | undefined;
        stateOrRegion?: string | undefined;
        postalCode?: string | undefined;
        countryCode?: string | undefined;
        phone?: string | undefined;
    }, {
        city?: string | undefined;
        email?: string | undefined;
        name?: string | undefined;
        addressLine1?: string | undefined;
        addressLine2?: string | undefined;
        addressLine3?: string | undefined;
        districtOrCounty?: string | undefined;
        stateOrRegion?: string | undefined;
        postalCode?: string | undefined;
        countryCode?: string | undefined;
        phone?: string | undefined;
    }>>;
    eventCode: z.ZodString;
    eventDescription: z.ZodString;
}, "strip", z.ZodTypeAny, {
    eventDate: string;
    eventCode: string;
    eventDescription: string;
    eventAddress?: {
        city?: string | undefined;
        email?: string | undefined;
        name?: string | undefined;
        addressLine1?: string | undefined;
        addressLine2?: string | undefined;
        addressLine3?: string | undefined;
        districtOrCounty?: string | undefined;
        stateOrRegion?: string | undefined;
        postalCode?: string | undefined;
        countryCode?: string | undefined;
        phone?: string | undefined;
    } | undefined;
}, {
    eventDate: string;
    eventCode: string;
    eventDescription: string;
    eventAddress?: {
        city?: string | undefined;
        email?: string | undefined;
        name?: string | undefined;
        addressLine1?: string | undefined;
        addressLine2?: string | undefined;
        addressLine3?: string | undefined;
        districtOrCounty?: string | undefined;
        stateOrRegion?: string | undefined;
        postalCode?: string | undefined;
        countryCode?: string | undefined;
        phone?: string | undefined;
    } | undefined;
}>;
/**
 * Amazon MCF package tracking details schema
 */
export declare const MCFPackageTrackingDetailsSchema: z.ZodObject<{
    packageNumber: z.ZodNumber;
    trackingNumber: z.ZodOptional<z.ZodString>;
    carrierCode: z.ZodOptional<z.ZodString>;
    carrierPhoneNumber: z.ZodOptional<z.ZodString>;
    carrierURL: z.ZodOptional<z.ZodString>;
    shipDate: z.ZodOptional<z.ZodString>;
    estimatedArrivalDate: z.ZodOptional<z.ZodString>;
    shipToAddress: z.ZodOptional<z.ZodObject<{
        name: z.ZodOptional<z.ZodString>;
        addressLine1: z.ZodOptional<z.ZodString>;
        addressLine2: z.ZodOptional<z.ZodOptional<z.ZodString>>;
        addressLine3: z.ZodOptional<z.ZodOptional<z.ZodString>>;
        city: z.ZodOptional<z.ZodOptional<z.ZodString>>;
        districtOrCounty: z.ZodOptional<z.ZodOptional<z.ZodString>>;
        stateOrRegion: z.ZodOptional<z.ZodString>;
        postalCode: z.ZodOptional<z.ZodString>;
        countryCode: z.ZodOptional<z.ZodString>;
        phone: z.ZodOptional<z.ZodOptional<z.ZodString>>;
        email: z.ZodOptional<z.ZodOptional<z.ZodString>>;
    }, "strip", z.ZodTypeAny, {
        city?: string | undefined;
        email?: string | undefined;
        name?: string | undefined;
        addressLine1?: string | undefined;
        addressLine2?: string | undefined;
        addressLine3?: string | undefined;
        districtOrCounty?: string | undefined;
        stateOrRegion?: string | undefined;
        postalCode?: string | undefined;
        countryCode?: string | undefined;
        phone?: string | undefined;
    }, {
        city?: string | undefined;
        email?: string | undefined;
        name?: string | undefined;
        addressLine1?: string | undefined;
        addressLine2?: string | undefined;
        addressLine3?: string | undefined;
        districtOrCounty?: string | undefined;
        stateOrRegion?: string | undefined;
        postalCode?: string | undefined;
        countryCode?: string | undefined;
        phone?: string | undefined;
    }>>;
    currentStatus: z.ZodOptional<z.ZodString>;
    currentStatusDescription: z.ZodOptional<z.ZodString>;
    signedForBy: z.ZodOptional<z.ZodString>;
    additionalLocationInfo: z.ZodOptional<z.ZodString>;
    trackingEvents: z.ZodOptional<z.ZodArray<z.ZodObject<{
        eventDate: z.ZodString;
        eventAddress: z.ZodOptional<z.ZodObject<{
            name: z.ZodOptional<z.ZodString>;
            addressLine1: z.ZodOptional<z.ZodString>;
            addressLine2: z.ZodOptional<z.ZodOptional<z.ZodString>>;
            addressLine3: z.ZodOptional<z.ZodOptional<z.ZodString>>;
            city: z.ZodOptional<z.ZodOptional<z.ZodString>>;
            districtOrCounty: z.ZodOptional<z.ZodOptional<z.ZodString>>;
            stateOrRegion: z.ZodOptional<z.ZodString>;
            postalCode: z.ZodOptional<z.ZodString>;
            countryCode: z.ZodOptional<z.ZodString>;
            phone: z.ZodOptional<z.ZodOptional<z.ZodString>>;
            email: z.ZodOptional<z.ZodOptional<z.ZodString>>;
        }, "strip", z.ZodTypeAny, {
            city?: string | undefined;
            email?: string | undefined;
            name?: string | undefined;
            addressLine1?: string | undefined;
            addressLine2?: string | undefined;
            addressLine3?: string | undefined;
            districtOrCounty?: string | undefined;
            stateOrRegion?: string | undefined;
            postalCode?: string | undefined;
            countryCode?: string | undefined;
            phone?: string | undefined;
        }, {
            city?: string | undefined;
            email?: string | undefined;
            name?: string | undefined;
            addressLine1?: string | undefined;
            addressLine2?: string | undefined;
            addressLine3?: string | undefined;
            districtOrCounty?: string | undefined;
            stateOrRegion?: string | undefined;
            postalCode?: string | undefined;
            countryCode?: string | undefined;
            phone?: string | undefined;
        }>>;
        eventCode: z.ZodString;
        eventDescription: z.ZodString;
    }, "strip", z.ZodTypeAny, {
        eventDate: string;
        eventCode: string;
        eventDescription: string;
        eventAddress?: {
            city?: string | undefined;
            email?: string | undefined;
            name?: string | undefined;
            addressLine1?: string | undefined;
            addressLine2?: string | undefined;
            addressLine3?: string | undefined;
            districtOrCounty?: string | undefined;
            stateOrRegion?: string | undefined;
            postalCode?: string | undefined;
            countryCode?: string | undefined;
            phone?: string | undefined;
        } | undefined;
    }, {
        eventDate: string;
        eventCode: string;
        eventDescription: string;
        eventAddress?: {
            city?: string | undefined;
            email?: string | undefined;
            name?: string | undefined;
            addressLine1?: string | undefined;
            addressLine2?: string | undefined;
            addressLine3?: string | undefined;
            districtOrCounty?: string | undefined;
            stateOrRegion?: string | undefined;
            postalCode?: string | undefined;
            countryCode?: string | undefined;
            phone?: string | undefined;
        } | undefined;
    }>, "many">>;
}, "strip", z.ZodTypeAny, {
    packageNumber: number;
    carrierCode?: string | undefined;
    trackingNumber?: string | undefined;
    estimatedArrivalDate?: string | undefined;
    carrierPhoneNumber?: string | undefined;
    carrierURL?: string | undefined;
    shipDate?: string | undefined;
    shipToAddress?: {
        city?: string | undefined;
        email?: string | undefined;
        name?: string | undefined;
        addressLine1?: string | undefined;
        addressLine2?: string | undefined;
        addressLine3?: string | undefined;
        districtOrCounty?: string | undefined;
        stateOrRegion?: string | undefined;
        postalCode?: string | undefined;
        countryCode?: string | undefined;
        phone?: string | undefined;
    } | undefined;
    currentStatus?: string | undefined;
    currentStatusDescription?: string | undefined;
    signedForBy?: string | undefined;
    additionalLocationInfo?: string | undefined;
    trackingEvents?: {
        eventDate: string;
        eventCode: string;
        eventDescription: string;
        eventAddress?: {
            city?: string | undefined;
            email?: string | undefined;
            name?: string | undefined;
            addressLine1?: string | undefined;
            addressLine2?: string | undefined;
            addressLine3?: string | undefined;
            districtOrCounty?: string | undefined;
            stateOrRegion?: string | undefined;
            postalCode?: string | undefined;
            countryCode?: string | undefined;
            phone?: string | undefined;
        } | undefined;
    }[] | undefined;
}, {
    packageNumber: number;
    carrierCode?: string | undefined;
    trackingNumber?: string | undefined;
    estimatedArrivalDate?: string | undefined;
    carrierPhoneNumber?: string | undefined;
    carrierURL?: string | undefined;
    shipDate?: string | undefined;
    shipToAddress?: {
        city?: string | undefined;
        email?: string | undefined;
        name?: string | undefined;
        addressLine1?: string | undefined;
        addressLine2?: string | undefined;
        addressLine3?: string | undefined;
        districtOrCounty?: string | undefined;
        stateOrRegion?: string | undefined;
        postalCode?: string | undefined;
        countryCode?: string | undefined;
        phone?: string | undefined;
    } | undefined;
    currentStatus?: string | undefined;
    currentStatusDescription?: string | undefined;
    signedForBy?: string | undefined;
    additionalLocationInfo?: string | undefined;
    trackingEvents?: {
        eventDate: string;
        eventCode: string;
        eventDescription: string;
        eventAddress?: {
            city?: string | undefined;
            email?: string | undefined;
            name?: string | undefined;
            addressLine1?: string | undefined;
            addressLine2?: string | undefined;
            addressLine3?: string | undefined;
            districtOrCounty?: string | undefined;
            stateOrRegion?: string | undefined;
            postalCode?: string | undefined;
            countryCode?: string | undefined;
            phone?: string | undefined;
        } | undefined;
    }[] | undefined;
}>;
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
export type MCFCreateFulfillmentOrderResponse = z.infer<typeof MCFCreateFulfillmentOrderResponseSchema>;
/**
 * Amazon MCF update fulfillment order request
 */
export type MCFUpdateFulfillmentOrderRequest = z.infer<typeof MCFUpdateFulfillmentOrderRequestSchema>;
/**
 * Amazon MCF cancel fulfillment order response
 */
export type MCFCancelFulfillmentOrderResponse = z.infer<typeof MCFCancelFulfillmentOrderResponseSchema>;
/**
 * Amazon MCF tracking event
 */
export type MCFTrackingEvent = z.infer<typeof MCFTrackingEventSchema>;
/**
 * Amazon MCF package tracking details
 */
export type MCFPackageTrackingDetails = z.infer<typeof MCFPackageTrackingDetailsSchema>;
/**
 * Amazon MCF fulfillment order creation parameters
 *
 * Simplified interface for creating MCF orders from internal order data.
 * This is the interface used by the order transformer.
 */
export interface CreateMCFOrderParams {
    orderId: string;
    displayableOrderId: string;
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
    id: string;
    status: MCFFulfillmentStatus;
    createdAt: Date;
    updatedAt?: Date;
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
    items: Array<{
        sku: string;
        itemId: string;
        quantity: number;
        price?: number;
        currency?: string;
    }>;
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
    orderId: string;
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
//# sourceMappingURL=mcf-order.d.ts.map