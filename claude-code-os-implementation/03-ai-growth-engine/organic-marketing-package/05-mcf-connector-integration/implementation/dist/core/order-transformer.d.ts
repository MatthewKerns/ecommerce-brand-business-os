/**
 * Order Transformer - Transforms TikTok orders to Amazon MCF format
 *
 * Features:
 * - Converts validated TikTok orders to MCF fulfillment order format
 * - Maps product SKUs between TikTok and Amazon
 * - Determines appropriate shipping speed based on order requirements
 * - Formats addresses to meet MCF API requirements
 */
import type { NormalizedTikTokOrder } from '../types/tiktok-order';
import type { Address } from '../types/common';
import type { MCFFulfillmentOrderRequest, MCFShippingSpeedCategory, MCFFulfillmentPolicy } from '../types/mcf-order';
export interface TransformationError {
    field: string;
    message: string;
    code: string;
}
export interface TransformationWarning {
    field: string;
    message: string;
}
export interface OrderTransformationResult {
    success: boolean;
    errors: TransformationError[];
    warnings?: TransformationWarning[];
    mcfOrderRequest?: MCFFulfillmentOrderRequest;
}
export interface SKUMapping {
    tiktokSku: string;
    amazonSku: string;
}
export interface TransformerConfig {
    skuMappings?: SKUMapping[];
    defaultShippingSpeed?: MCFShippingSpeedCategory;
    defaultFulfillmentPolicy?: MCFFulfillmentPolicy;
    notificationEmails?: string[];
    includeOrderComment?: boolean;
    includeItemPrices?: boolean;
}
/**
 * OrderTransformer converts validated TikTok orders to Amazon MCF format
 */
export declare class OrderTransformer {
    private config;
    constructor(config?: TransformerConfig);
    /**
     * Transform a normalized TikTok order to MCF order request format
     */
    transformOrder(order: NormalizedTikTokOrder, normalizedAddress: Address): OrderTransformationResult;
    /**
     * Add SKU mapping
     */
    addSKUMapping(tiktokSku: string, amazonSku: string): void;
    /**
     * Remove SKU mapping
     */
    removeSKUMapping(tiktokSku: string): void;
    /**
     * Get all SKU mappings
     */
    getSKUMappings(): SKUMapping[];
    /**
     * Update configuration
     */
    updateConfig(config: Partial<TransformerConfig>): void;
    /**
     * Get current configuration
     */
    getConfig(): Required<TransformerConfig>;
}
/**
 * Create a new order transformer instance
 */
export declare function createOrderTransformer(config?: TransformerConfig): OrderTransformer;
//# sourceMappingURL=order-transformer.d.ts.map