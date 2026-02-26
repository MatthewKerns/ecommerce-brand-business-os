"use strict";
/**
 * Order Transformer - Transforms TikTok orders to Amazon MCF format
 *
 * Features:
 * - Converts validated TikTok orders to MCF fulfillment order format
 * - Maps product SKUs between TikTok and Amazon
 * - Determines appropriate shipping speed based on order requirements
 * - Formats addresses to meet MCF API requirements
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.OrderTransformer = void 0;
exports.createOrderTransformer = createOrderTransformer;
const common_1 = require("../types/common");
// ============================================================
// Constants
// ============================================================
const DEFAULT_TRANSFORMER_CONFIG = {
    skuMappings: [],
    defaultShippingSpeed: 'Standard',
    defaultFulfillmentPolicy: 'FillOrKill',
    notificationEmails: [],
    includeOrderComment: true,
    includeItemPrices: true,
};
// Shipping speed mapping based on TikTok delivery requirements
const TIKTOK_TO_MCF_SHIPPING_SPEED = {
    STANDARD: 'Standard',
    EXPEDITED: 'Expedited',
    PRIORITY: 'Priority',
    SAME_DAY: 'Priority', // Map same-day to priority as closest match
    NEXT_DAY: 'Priority',
    TWO_DAY: 'Expedited',
};
// ============================================================
// Helper Functions
// ============================================================
/**
 * Map TikTok SKU to Amazon SKU using provided mappings
 */
function mapSKU(tiktokSku, mappings) {
    const mapping = mappings.find(m => m.tiktokSku === tiktokSku);
    return mapping ? mapping.amazonSku : null;
}
/**
 * Determine shipping speed based on TikTok order requirements
 */
function determineShippingSpeed(order, defaultSpeed) {
    // If TikTok order has shipping type specified, try to map it
    const shippingType = order.rawOrder.shipping_type;
    if (shippingType) {
        const upperShippingType = shippingType.toUpperCase();
        const mappedSpeed = TIKTOK_TO_MCF_SHIPPING_SPEED[upperShippingType];
        if (mappedSpeed) {
            return mappedSpeed;
        }
    }
    // Check delivery option for speed hints
    const deliveryOption = order.rawOrder.delivery_option_name;
    if (deliveryOption) {
        const upperDeliveryOption = deliveryOption.toUpperCase();
        if (upperDeliveryOption.includes('EXPRESS') || upperDeliveryOption.includes('EXPEDITED')) {
            return 'Expedited';
        }
        if (upperDeliveryOption.includes('PRIORITY') || upperDeliveryOption.includes('NEXT')) {
            return 'Priority';
        }
    }
    return defaultSpeed;
}
/**
 * Convert normalized address to MCF address format
 */
function convertToMCFAddress(address) {
    return {
        name: address.name,
        addressLine1: address.addressLine1,
        addressLine2: address.addressLine2,
        city: address.city,
        stateOrRegion: address.stateOrRegion,
        postalCode: address.postalCode,
        countryCode: address.countryCode,
        phone: address.phoneNumber,
    };
}
/**
 * Generate order comment from TikTok order data
 */
function generateOrderComment(order) {
    const comments = [];
    if (order.buyerMessage) {
        comments.push(`Buyer: ${order.buyerMessage}`);
    }
    if (order.sellerNote) {
        comments.push(`Note: ${order.sellerNote}`);
    }
    if (comments.length === 0) {
        return undefined;
    }
    // Truncate to 1000 characters (MCF limit)
    const fullComment = comments.join(' | ');
    return fullComment.length <= 1000 ? fullComment : fullComment.substring(0, 997) + '...';
}
/**
 * Format date to ISO 8601 string for MCF API
 */
function formatDateForMCF(date) {
    return date.toISOString();
}
// ============================================================
// OrderTransformer Class
// ============================================================
/**
 * OrderTransformer converts validated TikTok orders to Amazon MCF format
 */
class OrderTransformer {
    config;
    constructor(config) {
        this.config = { ...DEFAULT_TRANSFORMER_CONFIG, ...config };
    }
    /**
     * Transform a normalized TikTok order to MCF order request format
     */
    transformOrder(order, normalizedAddress) {
        const errors = [];
        const warnings = [];
        // Transform items with SKU mapping
        const mcfItems = [];
        for (let i = 0; i < order.items.length; i++) {
            const item = order.items[i];
            // Try to map SKU
            let amazonSku = mapSKU(item.sku, this.config.skuMappings);
            if (!amazonSku) {
                // If no mapping found, use TikTok SKU directly and warn
                amazonSku = item.sku;
                warnings.push({
                    field: `items[${i}].sku`,
                    message: `No SKU mapping found for TikTok SKU '${item.sku}', using directly as Amazon SKU`,
                });
            }
            // Build MCF item
            const mcfItem = {
                sellerSku: amazonSku,
                sellerFulfillmentOrderItemId: item.id,
                quantity: item.quantity,
            };
            // Add price information if configured
            if (this.config.includeItemPrices && item.price !== undefined) {
                mcfItem.perUnitPrice = {
                    currencyCode: order.payment.currency,
                    value: item.price,
                };
                // Add declared value (use price as declared value)
                mcfItem.perUnitDeclaredValue = {
                    currencyCode: order.payment.currency,
                    value: item.price,
                };
            }
            mcfItems.push(mcfItem);
        }
        // Validate we have at least one item
        if (mcfItems.length === 0) {
            errors.push({
                field: 'items',
                message: 'Order must have at least one valid item after transformation',
                code: common_1.ErrorCode.TRANSFORMATION_FAILED,
            });
            return {
                success: false,
                errors,
                warnings: warnings.length > 0 ? warnings : undefined,
            };
        }
        // Determine shipping speed
        const shippingSpeed = determineShippingSpeed(order, this.config.defaultShippingSpeed);
        // Convert address to MCF format
        const mcfAddress = convertToMCFAddress(normalizedAddress);
        // Generate order comment
        const orderComment = this.config.includeOrderComment
            ? generateOrderComment(order)
            : undefined;
        // Build MCF fulfillment order request
        const mcfOrderRequest = {
            sellerFulfillmentOrderId: `TIKTOK-${order.id}`,
            displayableOrderId: order.id,
            displayableOrderDate: formatDateForMCF(order.createdAt),
            displayableOrderComment: orderComment,
            shippingSpeedCategory: shippingSpeed,
            destinationAddress: mcfAddress,
            fulfillmentPolicy: this.config.defaultFulfillmentPolicy,
            fulfillmentAction: 'Ship',
            deliveryWindow: undefined,
            codSettings: undefined,
            notificationEmails: this.config.notificationEmails.length > 0
                ? this.config.notificationEmails
                : undefined,
            featureConstraints: undefined,
            items: mcfItems,
        };
        return {
            success: true,
            errors: [],
            warnings: warnings.length > 0 ? warnings : undefined,
            mcfOrderRequest,
        };
    }
    /**
     * Add SKU mapping
     */
    addSKUMapping(tiktokSku, amazonSku) {
        // Remove existing mapping if present
        this.config.skuMappings = this.config.skuMappings.filter(m => m.tiktokSku !== tiktokSku);
        // Add new mapping
        this.config.skuMappings.push({ tiktokSku, amazonSku });
    }
    /**
     * Remove SKU mapping
     */
    removeSKUMapping(tiktokSku) {
        this.config.skuMappings = this.config.skuMappings.filter(m => m.tiktokSku !== tiktokSku);
    }
    /**
     * Get all SKU mappings
     */
    getSKUMappings() {
        return [...this.config.skuMappings];
    }
    /**
     * Update configuration
     */
    updateConfig(config) {
        this.config = { ...this.config, ...config };
    }
    /**
     * Get current configuration
     */
    getConfig() {
        return { ...this.config };
    }
}
exports.OrderTransformer = OrderTransformer;
/**
 * Create a new order transformer instance
 */
function createOrderTransformer(config) {
    return new OrderTransformer(config);
}
//# sourceMappingURL=order-transformer.js.map