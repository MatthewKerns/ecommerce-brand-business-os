/**
 * TikTok Order Types - TikTok Shop Order Data Models
 *
 * Type definitions and Zod validation schemas for TikTok Shop orders.
 * Based on TikTok Shop Open API order structure.
 *
 * Zod schemas provide runtime validation when receiving data from TikTok API.
 * TypeScript types are inferred from schemas for compile-time type safety.
 */

import { z } from 'zod';
import { TikTokOrderStatus } from './common';

// ============================================================
// Zod Schemas
// ============================================================

/**
 * TikTok Shop recipient address schema
 */
export const TikTokAddressSchema = z.object({
  recipient_name: z.string(),
  phone_number: z.string(),
  full_address: z.string(),
  address_line_1: z.string().optional(),
  address_line_2: z.string().optional(),
  address_line_3: z.string().optional(),
  address_line_4: z.string().optional(),
  city: z.string().optional(),
  state: z.string().optional(),
  postal_code: z.string(),
  region_code: z.string(),
  district_info: z
    .array(
      z.object({
        address_level: z.string(),
        address_level_name: z.string(),
        address_name: z.string(),
      })
    )
    .optional(),
});

/**
 * TikTok Shop order item schema
 */
export const TikTokOrderItemSchema = z.object({
  id: z.string(),
  product_id: z.string(),
  product_name: z.string(),
  variant_id: z.string().optional(),
  variant_name: z.string().optional(),
  sku_id: z.string(),
  sku_name: z.string().optional(),
  sku_image: z.string().optional(),
  seller_sku: z.string().optional(),
  quantity: z.number().int().positive(),
  sale_price: z.number().nonnegative(),
  original_price: z.number().nonnegative().optional(),
  platform_discount: z.number().nonnegative().optional(),
  seller_discount: z.number().nonnegative().optional(),
  tax: z.number().nonnegative().optional(),
  small_order_fee: z.number().nonnegative().optional(),
  shipping_fee: z.number().nonnegative().optional(),
  sku_type: z.enum(['NORMAL', 'COMBO', 'VIRTUAL']).optional(),
  is_gift: z.boolean().optional(),
  display_status: z.string().optional(),
});

/**
 * TikTok Shop payment info schema
 */
export const TikTokPaymentInfoSchema = z.object({
  currency: z.string(),
  sub_total: z.number().nonnegative(),
  shipping_fee: z.number().nonnegative(),
  seller_discount: z.number().nonnegative().optional(),
  platform_discount: z.number().nonnegative().optional(),
  tax: z.number().nonnegative().optional(),
  total_amount: z.number().nonnegative(),
  original_total_product_price: z.number().nonnegative().optional(),
  original_shipping_fee: z.number().nonnegative().optional(),
  small_order_fee: z.number().nonnegative().optional(),
});

/**
 * TikTok Shop package schema
 */
export const TikTokPackageSchema = z.object({
  id: z.string(),
  shipping_provider_id: z.string().optional(),
  shipping_provider_name: z.string().optional(),
  tracking_number: z.string().optional(),
  items: z.array(
    z.object({
      order_item_id: z.string(),
      product_id: z.string(),
      sku_id: z.string(),
      quantity: z.number().int().positive(),
    })
  ),
  status: z.string().optional(),
  create_time: z.number().optional(),
  update_time: z.number().optional(),
});

/**
 * TikTok Shop buyer info schema
 */
export const TikTokBuyerInfoSchema = z.object({
  id: z.string().optional(),
  email: z.string().email().optional(),
  username: z.string().optional(),
});

/**
 * Complete TikTok Shop order schema
 */
export const TikTokOrderSchema = z.object({
  id: z.string(),
  status: z.nativeEnum(TikTokOrderStatus),
  create_time: z.number(),
  update_time: z.number(),
  payment_info: TikTokPaymentInfoSchema,
  recipient_address: TikTokAddressSchema,
  buyer_info: TikTokBuyerInfoSchema.optional(),
  items: z.array(TikTokOrderItemSchema),
  packages: z.array(TikTokPackageSchema).optional(),
  buyer_message: z.string().optional(),
  seller_note: z.string().optional(),
  shipping_type: z.string().optional(),
  delivery_option_id: z.string().optional(),
  delivery_option_name: z.string().optional(),
  delivery_option_description: z.string().optional(),
  is_cod: z.boolean().optional(),
  warehouse_id: z.string().optional(),
  fulfillment_type: z.enum(['FBT', 'FBS']).optional(),
  cancel_reason: z.string().optional(),
  cancel_user: z.string().optional(),
  rts_time: z.number().optional(),
  rts_sla_time: z.number().optional(),
  tts_time: z.number().optional(),
  tts_sla_time: z.number().optional(),
  collection_time: z.number().optional(),
  paid_time: z.number().optional(),
});

/**
 * TikTok order list response schema
 */
export const TikTokOrderListResponseSchema = z.object({
  orders: z.array(TikTokOrderSchema),
  total: z.number().int().nonnegative(),
  more: z.boolean(),
  next_page_token: z.string().optional(),
});

/**
 * TikTok order detail response schema
 */
export const TikTokOrderDetailResponseSchema = z.object({
  order: TikTokOrderSchema,
});

/**
 * TikTok tracking update request schema
 */
export const TikTokTrackingUpdateSchema = z.object({
  order_id: z.string(),
  tracking_number: z.string(),
  shipping_provider_id: z.string().optional(),
  shipping_provider_name: z.string().optional(),
  upload_time: z.number().optional(),
});

// ============================================================
// TypeScript Types (Inferred from Zod Schemas)
// ============================================================

/**
 * TikTok Shop recipient address
 */
export type TikTokAddress = z.infer<typeof TikTokAddressSchema>;

/**
 * TikTok Shop order item
 */
export type TikTokOrderItem = z.infer<typeof TikTokOrderItemSchema>;

/**
 * TikTok Shop payment information
 */
export type TikTokPaymentInfo = z.infer<typeof TikTokPaymentInfoSchema>;

/**
 * TikTok Shop package information
 */
export type TikTokPackage = z.infer<typeof TikTokPackageSchema>;

/**
 * TikTok Shop buyer information
 */
export type TikTokBuyerInfo = z.infer<typeof TikTokBuyerInfoSchema>;

/**
 * Complete TikTok Shop order
 */
export type TikTokOrder = z.infer<typeof TikTokOrderSchema>;

/**
 * TikTok order list API response
 */
export type TikTokOrderListResponse = z.infer<typeof TikTokOrderListResponseSchema>;

/**
 * TikTok order detail API response
 */
export type TikTokOrderDetailResponse = z.infer<typeof TikTokOrderDetailResponseSchema>;

/**
 * TikTok tracking update request
 */
export type TikTokTrackingUpdate = z.infer<typeof TikTokTrackingUpdateSchema>;

// ============================================================
// Helper Types
// ============================================================

/**
 * TikTok order filter parameters for listing orders
 */
export interface TikTokOrderListParams {
  create_time_from?: number;
  create_time_to?: number;
  update_time_from?: number;
  update_time_to?: number;
  order_status?: TikTokOrderStatus | TikTokOrderStatus[];
  page_size?: number;
  page_token?: string;
  sort_by?: 'CREATE_TIME' | 'UPDATE_TIME';
  sort_order?: 'ASC' | 'DESC';
}

/**
 * Normalized TikTok order for internal processing
 *
 * Simplified structure with normalized field names for easier processing.
 * This is the internal representation after initial validation.
 */
export interface NormalizedTikTokOrder {
  id: string;
  status: TikTokOrderStatus;
  createdAt: Date;
  updatedAt: Date;
  paidAt?: Date;

  // Customer information
  customer: {
    name: string;
    email?: string;
    phone: string;
  };

  // Shipping address
  shippingAddress: {
    name: string;
    addressLine1: string;
    addressLine2?: string;
    city?: string;
    state?: string;
    postalCode: string;
    countryCode: string;
    phoneNumber: string;
  };

  // Order items
  items: Array<{
    id: string;
    productId: string;
    productName: string;
    sku: string;
    quantity: number;
    price: number;
    totalPrice: number;
  }>;

  // Payment
  payment: {
    currency: string;
    subtotal: number;
    shippingFee: number;
    tax: number;
    discounts: number;
    total: number;
  };

  // Fulfillment
  fulfillmentType?: 'FBT' | 'FBS';
  packages?: Array<{
    id: string;
    trackingNumber?: string;
    carrier?: string;
    items: Array<{
      orderItemId: string;
      quantity: number;
    }>;
  }>;

  // Notes
  buyerMessage?: string;
  sellerNote?: string;

  // Metadata
  rawOrder: TikTokOrder;
}

/**
 * TikTok order validation result
 */
export interface TikTokOrderValidationResult {
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
