"use strict";
/**
 * TikTok Order Types - TikTok Shop Order Data Models
 *
 * Type definitions and Zod validation schemas for TikTok Shop orders.
 * Based on TikTok Shop Open API order structure.
 *
 * Zod schemas provide runtime validation when receiving data from TikTok API.
 * TypeScript types are inferred from schemas for compile-time type safety.
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.TikTokTrackingUpdateSchema = exports.TikTokOrderDetailResponseSchema = exports.TikTokOrderListResponseSchema = exports.TikTokOrderSchema = exports.TikTokBuyerInfoSchema = exports.TikTokPackageSchema = exports.TikTokPaymentInfoSchema = exports.TikTokOrderItemSchema = exports.TikTokAddressSchema = void 0;
const zod_1 = require("zod");
const common_1 = require("./common");
// ============================================================
// Zod Schemas
// ============================================================
/**
 * TikTok Shop recipient address schema
 */
exports.TikTokAddressSchema = zod_1.z.object({
    recipient_name: zod_1.z.string(),
    phone_number: zod_1.z.string(),
    full_address: zod_1.z.string(),
    address_line_1: zod_1.z.string().optional(),
    address_line_2: zod_1.z.string().optional(),
    address_line_3: zod_1.z.string().optional(),
    address_line_4: zod_1.z.string().optional(),
    city: zod_1.z.string().optional(),
    state: zod_1.z.string().optional(),
    postal_code: zod_1.z.string(),
    region_code: zod_1.z.string(),
    district_info: zod_1.z
        .array(zod_1.z.object({
        address_level: zod_1.z.string(),
        address_level_name: zod_1.z.string(),
        address_name: zod_1.z.string(),
    }))
        .optional(),
});
/**
 * TikTok Shop order item schema
 */
exports.TikTokOrderItemSchema = zod_1.z.object({
    id: zod_1.z.string(),
    product_id: zod_1.z.string(),
    product_name: zod_1.z.string(),
    variant_id: zod_1.z.string().optional(),
    variant_name: zod_1.z.string().optional(),
    sku_id: zod_1.z.string(),
    sku_name: zod_1.z.string().optional(),
    sku_image: zod_1.z.string().optional(),
    seller_sku: zod_1.z.string().optional(),
    quantity: zod_1.z.number().int().positive(),
    sale_price: zod_1.z.number().nonnegative(),
    original_price: zod_1.z.number().nonnegative().optional(),
    platform_discount: zod_1.z.number().nonnegative().optional(),
    seller_discount: zod_1.z.number().nonnegative().optional(),
    tax: zod_1.z.number().nonnegative().optional(),
    small_order_fee: zod_1.z.number().nonnegative().optional(),
    shipping_fee: zod_1.z.number().nonnegative().optional(),
    sku_type: zod_1.z.enum(['NORMAL', 'COMBO', 'VIRTUAL']).optional(),
    is_gift: zod_1.z.boolean().optional(),
    display_status: zod_1.z.string().optional(),
});
/**
 * TikTok Shop payment info schema
 */
exports.TikTokPaymentInfoSchema = zod_1.z.object({
    currency: zod_1.z.string(),
    sub_total: zod_1.z.number().nonnegative(),
    shipping_fee: zod_1.z.number().nonnegative(),
    seller_discount: zod_1.z.number().nonnegative().optional(),
    platform_discount: zod_1.z.number().nonnegative().optional(),
    tax: zod_1.z.number().nonnegative().optional(),
    total_amount: zod_1.z.number().nonnegative(),
    original_total_product_price: zod_1.z.number().nonnegative().optional(),
    original_shipping_fee: zod_1.z.number().nonnegative().optional(),
    small_order_fee: zod_1.z.number().nonnegative().optional(),
});
/**
 * TikTok Shop package schema
 */
exports.TikTokPackageSchema = zod_1.z.object({
    id: zod_1.z.string(),
    shipping_provider_id: zod_1.z.string().optional(),
    shipping_provider_name: zod_1.z.string().optional(),
    tracking_number: zod_1.z.string().optional(),
    items: zod_1.z.array(zod_1.z.object({
        order_item_id: zod_1.z.string(),
        product_id: zod_1.z.string(),
        sku_id: zod_1.z.string(),
        quantity: zod_1.z.number().int().positive(),
    })),
    status: zod_1.z.string().optional(),
    create_time: zod_1.z.number().optional(),
    update_time: zod_1.z.number().optional(),
});
/**
 * TikTok Shop buyer info schema
 */
exports.TikTokBuyerInfoSchema = zod_1.z.object({
    id: zod_1.z.string().optional(),
    email: zod_1.z.string().email().optional(),
    username: zod_1.z.string().optional(),
});
/**
 * Complete TikTok Shop order schema
 */
exports.TikTokOrderSchema = zod_1.z.object({
    id: zod_1.z.string(),
    status: zod_1.z.nativeEnum(common_1.TikTokOrderStatus),
    create_time: zod_1.z.number(),
    update_time: zod_1.z.number(),
    payment_info: exports.TikTokPaymentInfoSchema,
    recipient_address: exports.TikTokAddressSchema,
    buyer_info: exports.TikTokBuyerInfoSchema.optional(),
    items: zod_1.z.array(exports.TikTokOrderItemSchema),
    packages: zod_1.z.array(exports.TikTokPackageSchema).optional(),
    buyer_message: zod_1.z.string().optional(),
    seller_note: zod_1.z.string().optional(),
    shipping_type: zod_1.z.string().optional(),
    delivery_option_id: zod_1.z.string().optional(),
    delivery_option_name: zod_1.z.string().optional(),
    delivery_option_description: zod_1.z.string().optional(),
    is_cod: zod_1.z.boolean().optional(),
    warehouse_id: zod_1.z.string().optional(),
    fulfillment_type: zod_1.z.enum(['FBT', 'FBS']).optional(),
    cancel_reason: zod_1.z.string().optional(),
    cancel_user: zod_1.z.string().optional(),
    rts_time: zod_1.z.number().optional(),
    rts_sla_time: zod_1.z.number().optional(),
    tts_time: zod_1.z.number().optional(),
    tts_sla_time: zod_1.z.number().optional(),
    collection_time: zod_1.z.number().optional(),
    paid_time: zod_1.z.number().optional(),
});
/**
 * TikTok order list response schema
 */
exports.TikTokOrderListResponseSchema = zod_1.z.object({
    orders: zod_1.z.array(exports.TikTokOrderSchema),
    total: zod_1.z.number().int().nonnegative(),
    more: zod_1.z.boolean(),
    next_page_token: zod_1.z.string().optional(),
});
/**
 * TikTok order detail response schema
 */
exports.TikTokOrderDetailResponseSchema = zod_1.z.object({
    order: exports.TikTokOrderSchema,
});
/**
 * TikTok tracking update request schema
 */
exports.TikTokTrackingUpdateSchema = zod_1.z.object({
    order_id: zod_1.z.string(),
    tracking_number: zod_1.z.string(),
    shipping_provider_id: zod_1.z.string().optional(),
    shipping_provider_name: zod_1.z.string().optional(),
    upload_time: zod_1.z.number().optional(),
});
//# sourceMappingURL=tiktok-order.js.map