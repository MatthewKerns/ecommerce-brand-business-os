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
/**
 * TikTok Shop recipient address schema
 */
export declare const TikTokAddressSchema: z.ZodObject<{
    recipient_name: z.ZodString;
    phone_number: z.ZodString;
    full_address: z.ZodString;
    address_line_1: z.ZodOptional<z.ZodString>;
    address_line_2: z.ZodOptional<z.ZodString>;
    address_line_3: z.ZodOptional<z.ZodString>;
    address_line_4: z.ZodOptional<z.ZodString>;
    city: z.ZodOptional<z.ZodString>;
    state: z.ZodOptional<z.ZodString>;
    postal_code: z.ZodString;
    region_code: z.ZodString;
    district_info: z.ZodOptional<z.ZodArray<z.ZodObject<{
        address_level: z.ZodString;
        address_level_name: z.ZodString;
        address_name: z.ZodString;
    }, "strip", z.ZodTypeAny, {
        address_level: string;
        address_level_name: string;
        address_name: string;
    }, {
        address_level: string;
        address_level_name: string;
        address_name: string;
    }>, "many">>;
}, "strip", z.ZodTypeAny, {
    recipient_name: string;
    phone_number: string;
    full_address: string;
    postal_code: string;
    region_code: string;
    address_line_1?: string | undefined;
    address_line_2?: string | undefined;
    address_line_3?: string | undefined;
    address_line_4?: string | undefined;
    city?: string | undefined;
    state?: string | undefined;
    district_info?: {
        address_level: string;
        address_level_name: string;
        address_name: string;
    }[] | undefined;
}, {
    recipient_name: string;
    phone_number: string;
    full_address: string;
    postal_code: string;
    region_code: string;
    address_line_1?: string | undefined;
    address_line_2?: string | undefined;
    address_line_3?: string | undefined;
    address_line_4?: string | undefined;
    city?: string | undefined;
    state?: string | undefined;
    district_info?: {
        address_level: string;
        address_level_name: string;
        address_name: string;
    }[] | undefined;
}>;
/**
 * TikTok Shop order item schema
 */
export declare const TikTokOrderItemSchema: z.ZodObject<{
    id: z.ZodString;
    product_id: z.ZodString;
    product_name: z.ZodString;
    variant_id: z.ZodOptional<z.ZodString>;
    variant_name: z.ZodOptional<z.ZodString>;
    sku_id: z.ZodString;
    sku_name: z.ZodOptional<z.ZodString>;
    sku_image: z.ZodOptional<z.ZodString>;
    seller_sku: z.ZodOptional<z.ZodString>;
    quantity: z.ZodNumber;
    sale_price: z.ZodNumber;
    original_price: z.ZodOptional<z.ZodNumber>;
    platform_discount: z.ZodOptional<z.ZodNumber>;
    seller_discount: z.ZodOptional<z.ZodNumber>;
    tax: z.ZodOptional<z.ZodNumber>;
    small_order_fee: z.ZodOptional<z.ZodNumber>;
    shipping_fee: z.ZodOptional<z.ZodNumber>;
    sku_type: z.ZodOptional<z.ZodEnum<["NORMAL", "COMBO", "VIRTUAL"]>>;
    is_gift: z.ZodOptional<z.ZodBoolean>;
    display_status: z.ZodOptional<z.ZodString>;
}, "strip", z.ZodTypeAny, {
    id: string;
    product_id: string;
    product_name: string;
    sku_id: string;
    quantity: number;
    sale_price: number;
    variant_id?: string | undefined;
    variant_name?: string | undefined;
    sku_name?: string | undefined;
    sku_image?: string | undefined;
    seller_sku?: string | undefined;
    original_price?: number | undefined;
    platform_discount?: number | undefined;
    seller_discount?: number | undefined;
    tax?: number | undefined;
    small_order_fee?: number | undefined;
    shipping_fee?: number | undefined;
    sku_type?: "NORMAL" | "COMBO" | "VIRTUAL" | undefined;
    is_gift?: boolean | undefined;
    display_status?: string | undefined;
}, {
    id: string;
    product_id: string;
    product_name: string;
    sku_id: string;
    quantity: number;
    sale_price: number;
    variant_id?: string | undefined;
    variant_name?: string | undefined;
    sku_name?: string | undefined;
    sku_image?: string | undefined;
    seller_sku?: string | undefined;
    original_price?: number | undefined;
    platform_discount?: number | undefined;
    seller_discount?: number | undefined;
    tax?: number | undefined;
    small_order_fee?: number | undefined;
    shipping_fee?: number | undefined;
    sku_type?: "NORMAL" | "COMBO" | "VIRTUAL" | undefined;
    is_gift?: boolean | undefined;
    display_status?: string | undefined;
}>;
/**
 * TikTok Shop payment info schema
 */
export declare const TikTokPaymentInfoSchema: z.ZodObject<{
    currency: z.ZodString;
    sub_total: z.ZodNumber;
    shipping_fee: z.ZodNumber;
    seller_discount: z.ZodOptional<z.ZodNumber>;
    platform_discount: z.ZodOptional<z.ZodNumber>;
    tax: z.ZodOptional<z.ZodNumber>;
    total_amount: z.ZodNumber;
    original_total_product_price: z.ZodOptional<z.ZodNumber>;
    original_shipping_fee: z.ZodOptional<z.ZodNumber>;
    small_order_fee: z.ZodOptional<z.ZodNumber>;
}, "strip", z.ZodTypeAny, {
    shipping_fee: number;
    currency: string;
    sub_total: number;
    total_amount: number;
    platform_discount?: number | undefined;
    seller_discount?: number | undefined;
    tax?: number | undefined;
    small_order_fee?: number | undefined;
    original_total_product_price?: number | undefined;
    original_shipping_fee?: number | undefined;
}, {
    shipping_fee: number;
    currency: string;
    sub_total: number;
    total_amount: number;
    platform_discount?: number | undefined;
    seller_discount?: number | undefined;
    tax?: number | undefined;
    small_order_fee?: number | undefined;
    original_total_product_price?: number | undefined;
    original_shipping_fee?: number | undefined;
}>;
/**
 * TikTok Shop package schema
 */
export declare const TikTokPackageSchema: z.ZodObject<{
    id: z.ZodString;
    shipping_provider_id: z.ZodOptional<z.ZodString>;
    shipping_provider_name: z.ZodOptional<z.ZodString>;
    tracking_number: z.ZodOptional<z.ZodString>;
    items: z.ZodArray<z.ZodObject<{
        order_item_id: z.ZodString;
        product_id: z.ZodString;
        sku_id: z.ZodString;
        quantity: z.ZodNumber;
    }, "strip", z.ZodTypeAny, {
        product_id: string;
        sku_id: string;
        quantity: number;
        order_item_id: string;
    }, {
        product_id: string;
        sku_id: string;
        quantity: number;
        order_item_id: string;
    }>, "many">;
    status: z.ZodOptional<z.ZodString>;
    create_time: z.ZodOptional<z.ZodNumber>;
    update_time: z.ZodOptional<z.ZodNumber>;
}, "strip", z.ZodTypeAny, {
    id: string;
    items: {
        product_id: string;
        sku_id: string;
        quantity: number;
        order_item_id: string;
    }[];
    status?: string | undefined;
    shipping_provider_id?: string | undefined;
    shipping_provider_name?: string | undefined;
    tracking_number?: string | undefined;
    create_time?: number | undefined;
    update_time?: number | undefined;
}, {
    id: string;
    items: {
        product_id: string;
        sku_id: string;
        quantity: number;
        order_item_id: string;
    }[];
    status?: string | undefined;
    shipping_provider_id?: string | undefined;
    shipping_provider_name?: string | undefined;
    tracking_number?: string | undefined;
    create_time?: number | undefined;
    update_time?: number | undefined;
}>;
/**
 * TikTok Shop buyer info schema
 */
export declare const TikTokBuyerInfoSchema: z.ZodObject<{
    id: z.ZodOptional<z.ZodString>;
    email: z.ZodOptional<z.ZodString>;
    username: z.ZodOptional<z.ZodString>;
}, "strip", z.ZodTypeAny, {
    id?: string | undefined;
    email?: string | undefined;
    username?: string | undefined;
}, {
    id?: string | undefined;
    email?: string | undefined;
    username?: string | undefined;
}>;
/**
 * Complete TikTok Shop order schema
 */
export declare const TikTokOrderSchema: z.ZodObject<{
    id: z.ZodString;
    status: z.ZodNativeEnum<typeof TikTokOrderStatus>;
    create_time: z.ZodNumber;
    update_time: z.ZodNumber;
    payment_info: z.ZodObject<{
        currency: z.ZodString;
        sub_total: z.ZodNumber;
        shipping_fee: z.ZodNumber;
        seller_discount: z.ZodOptional<z.ZodNumber>;
        platform_discount: z.ZodOptional<z.ZodNumber>;
        tax: z.ZodOptional<z.ZodNumber>;
        total_amount: z.ZodNumber;
        original_total_product_price: z.ZodOptional<z.ZodNumber>;
        original_shipping_fee: z.ZodOptional<z.ZodNumber>;
        small_order_fee: z.ZodOptional<z.ZodNumber>;
    }, "strip", z.ZodTypeAny, {
        shipping_fee: number;
        currency: string;
        sub_total: number;
        total_amount: number;
        platform_discount?: number | undefined;
        seller_discount?: number | undefined;
        tax?: number | undefined;
        small_order_fee?: number | undefined;
        original_total_product_price?: number | undefined;
        original_shipping_fee?: number | undefined;
    }, {
        shipping_fee: number;
        currency: string;
        sub_total: number;
        total_amount: number;
        platform_discount?: number | undefined;
        seller_discount?: number | undefined;
        tax?: number | undefined;
        small_order_fee?: number | undefined;
        original_total_product_price?: number | undefined;
        original_shipping_fee?: number | undefined;
    }>;
    recipient_address: z.ZodObject<{
        recipient_name: z.ZodString;
        phone_number: z.ZodString;
        full_address: z.ZodString;
        address_line_1: z.ZodOptional<z.ZodString>;
        address_line_2: z.ZodOptional<z.ZodString>;
        address_line_3: z.ZodOptional<z.ZodString>;
        address_line_4: z.ZodOptional<z.ZodString>;
        city: z.ZodOptional<z.ZodString>;
        state: z.ZodOptional<z.ZodString>;
        postal_code: z.ZodString;
        region_code: z.ZodString;
        district_info: z.ZodOptional<z.ZodArray<z.ZodObject<{
            address_level: z.ZodString;
            address_level_name: z.ZodString;
            address_name: z.ZodString;
        }, "strip", z.ZodTypeAny, {
            address_level: string;
            address_level_name: string;
            address_name: string;
        }, {
            address_level: string;
            address_level_name: string;
            address_name: string;
        }>, "many">>;
    }, "strip", z.ZodTypeAny, {
        recipient_name: string;
        phone_number: string;
        full_address: string;
        postal_code: string;
        region_code: string;
        address_line_1?: string | undefined;
        address_line_2?: string | undefined;
        address_line_3?: string | undefined;
        address_line_4?: string | undefined;
        city?: string | undefined;
        state?: string | undefined;
        district_info?: {
            address_level: string;
            address_level_name: string;
            address_name: string;
        }[] | undefined;
    }, {
        recipient_name: string;
        phone_number: string;
        full_address: string;
        postal_code: string;
        region_code: string;
        address_line_1?: string | undefined;
        address_line_2?: string | undefined;
        address_line_3?: string | undefined;
        address_line_4?: string | undefined;
        city?: string | undefined;
        state?: string | undefined;
        district_info?: {
            address_level: string;
            address_level_name: string;
            address_name: string;
        }[] | undefined;
    }>;
    buyer_info: z.ZodOptional<z.ZodObject<{
        id: z.ZodOptional<z.ZodString>;
        email: z.ZodOptional<z.ZodString>;
        username: z.ZodOptional<z.ZodString>;
    }, "strip", z.ZodTypeAny, {
        id?: string | undefined;
        email?: string | undefined;
        username?: string | undefined;
    }, {
        id?: string | undefined;
        email?: string | undefined;
        username?: string | undefined;
    }>>;
    items: z.ZodArray<z.ZodObject<{
        id: z.ZodString;
        product_id: z.ZodString;
        product_name: z.ZodString;
        variant_id: z.ZodOptional<z.ZodString>;
        variant_name: z.ZodOptional<z.ZodString>;
        sku_id: z.ZodString;
        sku_name: z.ZodOptional<z.ZodString>;
        sku_image: z.ZodOptional<z.ZodString>;
        seller_sku: z.ZodOptional<z.ZodString>;
        quantity: z.ZodNumber;
        sale_price: z.ZodNumber;
        original_price: z.ZodOptional<z.ZodNumber>;
        platform_discount: z.ZodOptional<z.ZodNumber>;
        seller_discount: z.ZodOptional<z.ZodNumber>;
        tax: z.ZodOptional<z.ZodNumber>;
        small_order_fee: z.ZodOptional<z.ZodNumber>;
        shipping_fee: z.ZodOptional<z.ZodNumber>;
        sku_type: z.ZodOptional<z.ZodEnum<["NORMAL", "COMBO", "VIRTUAL"]>>;
        is_gift: z.ZodOptional<z.ZodBoolean>;
        display_status: z.ZodOptional<z.ZodString>;
    }, "strip", z.ZodTypeAny, {
        id: string;
        product_id: string;
        product_name: string;
        sku_id: string;
        quantity: number;
        sale_price: number;
        variant_id?: string | undefined;
        variant_name?: string | undefined;
        sku_name?: string | undefined;
        sku_image?: string | undefined;
        seller_sku?: string | undefined;
        original_price?: number | undefined;
        platform_discount?: number | undefined;
        seller_discount?: number | undefined;
        tax?: number | undefined;
        small_order_fee?: number | undefined;
        shipping_fee?: number | undefined;
        sku_type?: "NORMAL" | "COMBO" | "VIRTUAL" | undefined;
        is_gift?: boolean | undefined;
        display_status?: string | undefined;
    }, {
        id: string;
        product_id: string;
        product_name: string;
        sku_id: string;
        quantity: number;
        sale_price: number;
        variant_id?: string | undefined;
        variant_name?: string | undefined;
        sku_name?: string | undefined;
        sku_image?: string | undefined;
        seller_sku?: string | undefined;
        original_price?: number | undefined;
        platform_discount?: number | undefined;
        seller_discount?: number | undefined;
        tax?: number | undefined;
        small_order_fee?: number | undefined;
        shipping_fee?: number | undefined;
        sku_type?: "NORMAL" | "COMBO" | "VIRTUAL" | undefined;
        is_gift?: boolean | undefined;
        display_status?: string | undefined;
    }>, "many">;
    packages: z.ZodOptional<z.ZodArray<z.ZodObject<{
        id: z.ZodString;
        shipping_provider_id: z.ZodOptional<z.ZodString>;
        shipping_provider_name: z.ZodOptional<z.ZodString>;
        tracking_number: z.ZodOptional<z.ZodString>;
        items: z.ZodArray<z.ZodObject<{
            order_item_id: z.ZodString;
            product_id: z.ZodString;
            sku_id: z.ZodString;
            quantity: z.ZodNumber;
        }, "strip", z.ZodTypeAny, {
            product_id: string;
            sku_id: string;
            quantity: number;
            order_item_id: string;
        }, {
            product_id: string;
            sku_id: string;
            quantity: number;
            order_item_id: string;
        }>, "many">;
        status: z.ZodOptional<z.ZodString>;
        create_time: z.ZodOptional<z.ZodNumber>;
        update_time: z.ZodOptional<z.ZodNumber>;
    }, "strip", z.ZodTypeAny, {
        id: string;
        items: {
            product_id: string;
            sku_id: string;
            quantity: number;
            order_item_id: string;
        }[];
        status?: string | undefined;
        shipping_provider_id?: string | undefined;
        shipping_provider_name?: string | undefined;
        tracking_number?: string | undefined;
        create_time?: number | undefined;
        update_time?: number | undefined;
    }, {
        id: string;
        items: {
            product_id: string;
            sku_id: string;
            quantity: number;
            order_item_id: string;
        }[];
        status?: string | undefined;
        shipping_provider_id?: string | undefined;
        shipping_provider_name?: string | undefined;
        tracking_number?: string | undefined;
        create_time?: number | undefined;
        update_time?: number | undefined;
    }>, "many">>;
    buyer_message: z.ZodOptional<z.ZodString>;
    seller_note: z.ZodOptional<z.ZodString>;
    shipping_type: z.ZodOptional<z.ZodString>;
    delivery_option_id: z.ZodOptional<z.ZodString>;
    delivery_option_name: z.ZodOptional<z.ZodString>;
    delivery_option_description: z.ZodOptional<z.ZodString>;
    is_cod: z.ZodOptional<z.ZodBoolean>;
    warehouse_id: z.ZodOptional<z.ZodString>;
    fulfillment_type: z.ZodOptional<z.ZodEnum<["FBT", "FBS"]>>;
    cancel_reason: z.ZodOptional<z.ZodString>;
    cancel_user: z.ZodOptional<z.ZodString>;
    rts_time: z.ZodOptional<z.ZodNumber>;
    rts_sla_time: z.ZodOptional<z.ZodNumber>;
    tts_time: z.ZodOptional<z.ZodNumber>;
    tts_sla_time: z.ZodOptional<z.ZodNumber>;
    collection_time: z.ZodOptional<z.ZodNumber>;
    paid_time: z.ZodOptional<z.ZodNumber>;
}, "strip", z.ZodTypeAny, {
    status: TikTokOrderStatus;
    id: string;
    items: {
        id: string;
        product_id: string;
        product_name: string;
        sku_id: string;
        quantity: number;
        sale_price: number;
        variant_id?: string | undefined;
        variant_name?: string | undefined;
        sku_name?: string | undefined;
        sku_image?: string | undefined;
        seller_sku?: string | undefined;
        original_price?: number | undefined;
        platform_discount?: number | undefined;
        seller_discount?: number | undefined;
        tax?: number | undefined;
        small_order_fee?: number | undefined;
        shipping_fee?: number | undefined;
        sku_type?: "NORMAL" | "COMBO" | "VIRTUAL" | undefined;
        is_gift?: boolean | undefined;
        display_status?: string | undefined;
    }[];
    create_time: number;
    update_time: number;
    payment_info: {
        shipping_fee: number;
        currency: string;
        sub_total: number;
        total_amount: number;
        platform_discount?: number | undefined;
        seller_discount?: number | undefined;
        tax?: number | undefined;
        small_order_fee?: number | undefined;
        original_total_product_price?: number | undefined;
        original_shipping_fee?: number | undefined;
    };
    recipient_address: {
        recipient_name: string;
        phone_number: string;
        full_address: string;
        postal_code: string;
        region_code: string;
        address_line_1?: string | undefined;
        address_line_2?: string | undefined;
        address_line_3?: string | undefined;
        address_line_4?: string | undefined;
        city?: string | undefined;
        state?: string | undefined;
        district_info?: {
            address_level: string;
            address_level_name: string;
            address_name: string;
        }[] | undefined;
    };
    buyer_info?: {
        id?: string | undefined;
        email?: string | undefined;
        username?: string | undefined;
    } | undefined;
    packages?: {
        id: string;
        items: {
            product_id: string;
            sku_id: string;
            quantity: number;
            order_item_id: string;
        }[];
        status?: string | undefined;
        shipping_provider_id?: string | undefined;
        shipping_provider_name?: string | undefined;
        tracking_number?: string | undefined;
        create_time?: number | undefined;
        update_time?: number | undefined;
    }[] | undefined;
    buyer_message?: string | undefined;
    seller_note?: string | undefined;
    shipping_type?: string | undefined;
    delivery_option_id?: string | undefined;
    delivery_option_name?: string | undefined;
    delivery_option_description?: string | undefined;
    is_cod?: boolean | undefined;
    warehouse_id?: string | undefined;
    fulfillment_type?: "FBT" | "FBS" | undefined;
    cancel_reason?: string | undefined;
    cancel_user?: string | undefined;
    rts_time?: number | undefined;
    rts_sla_time?: number | undefined;
    tts_time?: number | undefined;
    tts_sla_time?: number | undefined;
    collection_time?: number | undefined;
    paid_time?: number | undefined;
}, {
    status: TikTokOrderStatus;
    id: string;
    items: {
        id: string;
        product_id: string;
        product_name: string;
        sku_id: string;
        quantity: number;
        sale_price: number;
        variant_id?: string | undefined;
        variant_name?: string | undefined;
        sku_name?: string | undefined;
        sku_image?: string | undefined;
        seller_sku?: string | undefined;
        original_price?: number | undefined;
        platform_discount?: number | undefined;
        seller_discount?: number | undefined;
        tax?: number | undefined;
        small_order_fee?: number | undefined;
        shipping_fee?: number | undefined;
        sku_type?: "NORMAL" | "COMBO" | "VIRTUAL" | undefined;
        is_gift?: boolean | undefined;
        display_status?: string | undefined;
    }[];
    create_time: number;
    update_time: number;
    payment_info: {
        shipping_fee: number;
        currency: string;
        sub_total: number;
        total_amount: number;
        platform_discount?: number | undefined;
        seller_discount?: number | undefined;
        tax?: number | undefined;
        small_order_fee?: number | undefined;
        original_total_product_price?: number | undefined;
        original_shipping_fee?: number | undefined;
    };
    recipient_address: {
        recipient_name: string;
        phone_number: string;
        full_address: string;
        postal_code: string;
        region_code: string;
        address_line_1?: string | undefined;
        address_line_2?: string | undefined;
        address_line_3?: string | undefined;
        address_line_4?: string | undefined;
        city?: string | undefined;
        state?: string | undefined;
        district_info?: {
            address_level: string;
            address_level_name: string;
            address_name: string;
        }[] | undefined;
    };
    buyer_info?: {
        id?: string | undefined;
        email?: string | undefined;
        username?: string | undefined;
    } | undefined;
    packages?: {
        id: string;
        items: {
            product_id: string;
            sku_id: string;
            quantity: number;
            order_item_id: string;
        }[];
        status?: string | undefined;
        shipping_provider_id?: string | undefined;
        shipping_provider_name?: string | undefined;
        tracking_number?: string | undefined;
        create_time?: number | undefined;
        update_time?: number | undefined;
    }[] | undefined;
    buyer_message?: string | undefined;
    seller_note?: string | undefined;
    shipping_type?: string | undefined;
    delivery_option_id?: string | undefined;
    delivery_option_name?: string | undefined;
    delivery_option_description?: string | undefined;
    is_cod?: boolean | undefined;
    warehouse_id?: string | undefined;
    fulfillment_type?: "FBT" | "FBS" | undefined;
    cancel_reason?: string | undefined;
    cancel_user?: string | undefined;
    rts_time?: number | undefined;
    rts_sla_time?: number | undefined;
    tts_time?: number | undefined;
    tts_sla_time?: number | undefined;
    collection_time?: number | undefined;
    paid_time?: number | undefined;
}>;
/**
 * TikTok order list response schema
 */
export declare const TikTokOrderListResponseSchema: z.ZodObject<{
    orders: z.ZodArray<z.ZodObject<{
        id: z.ZodString;
        status: z.ZodNativeEnum<typeof TikTokOrderStatus>;
        create_time: z.ZodNumber;
        update_time: z.ZodNumber;
        payment_info: z.ZodObject<{
            currency: z.ZodString;
            sub_total: z.ZodNumber;
            shipping_fee: z.ZodNumber;
            seller_discount: z.ZodOptional<z.ZodNumber>;
            platform_discount: z.ZodOptional<z.ZodNumber>;
            tax: z.ZodOptional<z.ZodNumber>;
            total_amount: z.ZodNumber;
            original_total_product_price: z.ZodOptional<z.ZodNumber>;
            original_shipping_fee: z.ZodOptional<z.ZodNumber>;
            small_order_fee: z.ZodOptional<z.ZodNumber>;
        }, "strip", z.ZodTypeAny, {
            shipping_fee: number;
            currency: string;
            sub_total: number;
            total_amount: number;
            platform_discount?: number | undefined;
            seller_discount?: number | undefined;
            tax?: number | undefined;
            small_order_fee?: number | undefined;
            original_total_product_price?: number | undefined;
            original_shipping_fee?: number | undefined;
        }, {
            shipping_fee: number;
            currency: string;
            sub_total: number;
            total_amount: number;
            platform_discount?: number | undefined;
            seller_discount?: number | undefined;
            tax?: number | undefined;
            small_order_fee?: number | undefined;
            original_total_product_price?: number | undefined;
            original_shipping_fee?: number | undefined;
        }>;
        recipient_address: z.ZodObject<{
            recipient_name: z.ZodString;
            phone_number: z.ZodString;
            full_address: z.ZodString;
            address_line_1: z.ZodOptional<z.ZodString>;
            address_line_2: z.ZodOptional<z.ZodString>;
            address_line_3: z.ZodOptional<z.ZodString>;
            address_line_4: z.ZodOptional<z.ZodString>;
            city: z.ZodOptional<z.ZodString>;
            state: z.ZodOptional<z.ZodString>;
            postal_code: z.ZodString;
            region_code: z.ZodString;
            district_info: z.ZodOptional<z.ZodArray<z.ZodObject<{
                address_level: z.ZodString;
                address_level_name: z.ZodString;
                address_name: z.ZodString;
            }, "strip", z.ZodTypeAny, {
                address_level: string;
                address_level_name: string;
                address_name: string;
            }, {
                address_level: string;
                address_level_name: string;
                address_name: string;
            }>, "many">>;
        }, "strip", z.ZodTypeAny, {
            recipient_name: string;
            phone_number: string;
            full_address: string;
            postal_code: string;
            region_code: string;
            address_line_1?: string | undefined;
            address_line_2?: string | undefined;
            address_line_3?: string | undefined;
            address_line_4?: string | undefined;
            city?: string | undefined;
            state?: string | undefined;
            district_info?: {
                address_level: string;
                address_level_name: string;
                address_name: string;
            }[] | undefined;
        }, {
            recipient_name: string;
            phone_number: string;
            full_address: string;
            postal_code: string;
            region_code: string;
            address_line_1?: string | undefined;
            address_line_2?: string | undefined;
            address_line_3?: string | undefined;
            address_line_4?: string | undefined;
            city?: string | undefined;
            state?: string | undefined;
            district_info?: {
                address_level: string;
                address_level_name: string;
                address_name: string;
            }[] | undefined;
        }>;
        buyer_info: z.ZodOptional<z.ZodObject<{
            id: z.ZodOptional<z.ZodString>;
            email: z.ZodOptional<z.ZodString>;
            username: z.ZodOptional<z.ZodString>;
        }, "strip", z.ZodTypeAny, {
            id?: string | undefined;
            email?: string | undefined;
            username?: string | undefined;
        }, {
            id?: string | undefined;
            email?: string | undefined;
            username?: string | undefined;
        }>>;
        items: z.ZodArray<z.ZodObject<{
            id: z.ZodString;
            product_id: z.ZodString;
            product_name: z.ZodString;
            variant_id: z.ZodOptional<z.ZodString>;
            variant_name: z.ZodOptional<z.ZodString>;
            sku_id: z.ZodString;
            sku_name: z.ZodOptional<z.ZodString>;
            sku_image: z.ZodOptional<z.ZodString>;
            seller_sku: z.ZodOptional<z.ZodString>;
            quantity: z.ZodNumber;
            sale_price: z.ZodNumber;
            original_price: z.ZodOptional<z.ZodNumber>;
            platform_discount: z.ZodOptional<z.ZodNumber>;
            seller_discount: z.ZodOptional<z.ZodNumber>;
            tax: z.ZodOptional<z.ZodNumber>;
            small_order_fee: z.ZodOptional<z.ZodNumber>;
            shipping_fee: z.ZodOptional<z.ZodNumber>;
            sku_type: z.ZodOptional<z.ZodEnum<["NORMAL", "COMBO", "VIRTUAL"]>>;
            is_gift: z.ZodOptional<z.ZodBoolean>;
            display_status: z.ZodOptional<z.ZodString>;
        }, "strip", z.ZodTypeAny, {
            id: string;
            product_id: string;
            product_name: string;
            sku_id: string;
            quantity: number;
            sale_price: number;
            variant_id?: string | undefined;
            variant_name?: string | undefined;
            sku_name?: string | undefined;
            sku_image?: string | undefined;
            seller_sku?: string | undefined;
            original_price?: number | undefined;
            platform_discount?: number | undefined;
            seller_discount?: number | undefined;
            tax?: number | undefined;
            small_order_fee?: number | undefined;
            shipping_fee?: number | undefined;
            sku_type?: "NORMAL" | "COMBO" | "VIRTUAL" | undefined;
            is_gift?: boolean | undefined;
            display_status?: string | undefined;
        }, {
            id: string;
            product_id: string;
            product_name: string;
            sku_id: string;
            quantity: number;
            sale_price: number;
            variant_id?: string | undefined;
            variant_name?: string | undefined;
            sku_name?: string | undefined;
            sku_image?: string | undefined;
            seller_sku?: string | undefined;
            original_price?: number | undefined;
            platform_discount?: number | undefined;
            seller_discount?: number | undefined;
            tax?: number | undefined;
            small_order_fee?: number | undefined;
            shipping_fee?: number | undefined;
            sku_type?: "NORMAL" | "COMBO" | "VIRTUAL" | undefined;
            is_gift?: boolean | undefined;
            display_status?: string | undefined;
        }>, "many">;
        packages: z.ZodOptional<z.ZodArray<z.ZodObject<{
            id: z.ZodString;
            shipping_provider_id: z.ZodOptional<z.ZodString>;
            shipping_provider_name: z.ZodOptional<z.ZodString>;
            tracking_number: z.ZodOptional<z.ZodString>;
            items: z.ZodArray<z.ZodObject<{
                order_item_id: z.ZodString;
                product_id: z.ZodString;
                sku_id: z.ZodString;
                quantity: z.ZodNumber;
            }, "strip", z.ZodTypeAny, {
                product_id: string;
                sku_id: string;
                quantity: number;
                order_item_id: string;
            }, {
                product_id: string;
                sku_id: string;
                quantity: number;
                order_item_id: string;
            }>, "many">;
            status: z.ZodOptional<z.ZodString>;
            create_time: z.ZodOptional<z.ZodNumber>;
            update_time: z.ZodOptional<z.ZodNumber>;
        }, "strip", z.ZodTypeAny, {
            id: string;
            items: {
                product_id: string;
                sku_id: string;
                quantity: number;
                order_item_id: string;
            }[];
            status?: string | undefined;
            shipping_provider_id?: string | undefined;
            shipping_provider_name?: string | undefined;
            tracking_number?: string | undefined;
            create_time?: number | undefined;
            update_time?: number | undefined;
        }, {
            id: string;
            items: {
                product_id: string;
                sku_id: string;
                quantity: number;
                order_item_id: string;
            }[];
            status?: string | undefined;
            shipping_provider_id?: string | undefined;
            shipping_provider_name?: string | undefined;
            tracking_number?: string | undefined;
            create_time?: number | undefined;
            update_time?: number | undefined;
        }>, "many">>;
        buyer_message: z.ZodOptional<z.ZodString>;
        seller_note: z.ZodOptional<z.ZodString>;
        shipping_type: z.ZodOptional<z.ZodString>;
        delivery_option_id: z.ZodOptional<z.ZodString>;
        delivery_option_name: z.ZodOptional<z.ZodString>;
        delivery_option_description: z.ZodOptional<z.ZodString>;
        is_cod: z.ZodOptional<z.ZodBoolean>;
        warehouse_id: z.ZodOptional<z.ZodString>;
        fulfillment_type: z.ZodOptional<z.ZodEnum<["FBT", "FBS"]>>;
        cancel_reason: z.ZodOptional<z.ZodString>;
        cancel_user: z.ZodOptional<z.ZodString>;
        rts_time: z.ZodOptional<z.ZodNumber>;
        rts_sla_time: z.ZodOptional<z.ZodNumber>;
        tts_time: z.ZodOptional<z.ZodNumber>;
        tts_sla_time: z.ZodOptional<z.ZodNumber>;
        collection_time: z.ZodOptional<z.ZodNumber>;
        paid_time: z.ZodOptional<z.ZodNumber>;
    }, "strip", z.ZodTypeAny, {
        status: TikTokOrderStatus;
        id: string;
        items: {
            id: string;
            product_id: string;
            product_name: string;
            sku_id: string;
            quantity: number;
            sale_price: number;
            variant_id?: string | undefined;
            variant_name?: string | undefined;
            sku_name?: string | undefined;
            sku_image?: string | undefined;
            seller_sku?: string | undefined;
            original_price?: number | undefined;
            platform_discount?: number | undefined;
            seller_discount?: number | undefined;
            tax?: number | undefined;
            small_order_fee?: number | undefined;
            shipping_fee?: number | undefined;
            sku_type?: "NORMAL" | "COMBO" | "VIRTUAL" | undefined;
            is_gift?: boolean | undefined;
            display_status?: string | undefined;
        }[];
        create_time: number;
        update_time: number;
        payment_info: {
            shipping_fee: number;
            currency: string;
            sub_total: number;
            total_amount: number;
            platform_discount?: number | undefined;
            seller_discount?: number | undefined;
            tax?: number | undefined;
            small_order_fee?: number | undefined;
            original_total_product_price?: number | undefined;
            original_shipping_fee?: number | undefined;
        };
        recipient_address: {
            recipient_name: string;
            phone_number: string;
            full_address: string;
            postal_code: string;
            region_code: string;
            address_line_1?: string | undefined;
            address_line_2?: string | undefined;
            address_line_3?: string | undefined;
            address_line_4?: string | undefined;
            city?: string | undefined;
            state?: string | undefined;
            district_info?: {
                address_level: string;
                address_level_name: string;
                address_name: string;
            }[] | undefined;
        };
        buyer_info?: {
            id?: string | undefined;
            email?: string | undefined;
            username?: string | undefined;
        } | undefined;
        packages?: {
            id: string;
            items: {
                product_id: string;
                sku_id: string;
                quantity: number;
                order_item_id: string;
            }[];
            status?: string | undefined;
            shipping_provider_id?: string | undefined;
            shipping_provider_name?: string | undefined;
            tracking_number?: string | undefined;
            create_time?: number | undefined;
            update_time?: number | undefined;
        }[] | undefined;
        buyer_message?: string | undefined;
        seller_note?: string | undefined;
        shipping_type?: string | undefined;
        delivery_option_id?: string | undefined;
        delivery_option_name?: string | undefined;
        delivery_option_description?: string | undefined;
        is_cod?: boolean | undefined;
        warehouse_id?: string | undefined;
        fulfillment_type?: "FBT" | "FBS" | undefined;
        cancel_reason?: string | undefined;
        cancel_user?: string | undefined;
        rts_time?: number | undefined;
        rts_sla_time?: number | undefined;
        tts_time?: number | undefined;
        tts_sla_time?: number | undefined;
        collection_time?: number | undefined;
        paid_time?: number | undefined;
    }, {
        status: TikTokOrderStatus;
        id: string;
        items: {
            id: string;
            product_id: string;
            product_name: string;
            sku_id: string;
            quantity: number;
            sale_price: number;
            variant_id?: string | undefined;
            variant_name?: string | undefined;
            sku_name?: string | undefined;
            sku_image?: string | undefined;
            seller_sku?: string | undefined;
            original_price?: number | undefined;
            platform_discount?: number | undefined;
            seller_discount?: number | undefined;
            tax?: number | undefined;
            small_order_fee?: number | undefined;
            shipping_fee?: number | undefined;
            sku_type?: "NORMAL" | "COMBO" | "VIRTUAL" | undefined;
            is_gift?: boolean | undefined;
            display_status?: string | undefined;
        }[];
        create_time: number;
        update_time: number;
        payment_info: {
            shipping_fee: number;
            currency: string;
            sub_total: number;
            total_amount: number;
            platform_discount?: number | undefined;
            seller_discount?: number | undefined;
            tax?: number | undefined;
            small_order_fee?: number | undefined;
            original_total_product_price?: number | undefined;
            original_shipping_fee?: number | undefined;
        };
        recipient_address: {
            recipient_name: string;
            phone_number: string;
            full_address: string;
            postal_code: string;
            region_code: string;
            address_line_1?: string | undefined;
            address_line_2?: string | undefined;
            address_line_3?: string | undefined;
            address_line_4?: string | undefined;
            city?: string | undefined;
            state?: string | undefined;
            district_info?: {
                address_level: string;
                address_level_name: string;
                address_name: string;
            }[] | undefined;
        };
        buyer_info?: {
            id?: string | undefined;
            email?: string | undefined;
            username?: string | undefined;
        } | undefined;
        packages?: {
            id: string;
            items: {
                product_id: string;
                sku_id: string;
                quantity: number;
                order_item_id: string;
            }[];
            status?: string | undefined;
            shipping_provider_id?: string | undefined;
            shipping_provider_name?: string | undefined;
            tracking_number?: string | undefined;
            create_time?: number | undefined;
            update_time?: number | undefined;
        }[] | undefined;
        buyer_message?: string | undefined;
        seller_note?: string | undefined;
        shipping_type?: string | undefined;
        delivery_option_id?: string | undefined;
        delivery_option_name?: string | undefined;
        delivery_option_description?: string | undefined;
        is_cod?: boolean | undefined;
        warehouse_id?: string | undefined;
        fulfillment_type?: "FBT" | "FBS" | undefined;
        cancel_reason?: string | undefined;
        cancel_user?: string | undefined;
        rts_time?: number | undefined;
        rts_sla_time?: number | undefined;
        tts_time?: number | undefined;
        tts_sla_time?: number | undefined;
        collection_time?: number | undefined;
        paid_time?: number | undefined;
    }>, "many">;
    total: z.ZodNumber;
    more: z.ZodBoolean;
    next_page_token: z.ZodOptional<z.ZodString>;
}, "strip", z.ZodTypeAny, {
    orders: {
        status: TikTokOrderStatus;
        id: string;
        items: {
            id: string;
            product_id: string;
            product_name: string;
            sku_id: string;
            quantity: number;
            sale_price: number;
            variant_id?: string | undefined;
            variant_name?: string | undefined;
            sku_name?: string | undefined;
            sku_image?: string | undefined;
            seller_sku?: string | undefined;
            original_price?: number | undefined;
            platform_discount?: number | undefined;
            seller_discount?: number | undefined;
            tax?: number | undefined;
            small_order_fee?: number | undefined;
            shipping_fee?: number | undefined;
            sku_type?: "NORMAL" | "COMBO" | "VIRTUAL" | undefined;
            is_gift?: boolean | undefined;
            display_status?: string | undefined;
        }[];
        create_time: number;
        update_time: number;
        payment_info: {
            shipping_fee: number;
            currency: string;
            sub_total: number;
            total_amount: number;
            platform_discount?: number | undefined;
            seller_discount?: number | undefined;
            tax?: number | undefined;
            small_order_fee?: number | undefined;
            original_total_product_price?: number | undefined;
            original_shipping_fee?: number | undefined;
        };
        recipient_address: {
            recipient_name: string;
            phone_number: string;
            full_address: string;
            postal_code: string;
            region_code: string;
            address_line_1?: string | undefined;
            address_line_2?: string | undefined;
            address_line_3?: string | undefined;
            address_line_4?: string | undefined;
            city?: string | undefined;
            state?: string | undefined;
            district_info?: {
                address_level: string;
                address_level_name: string;
                address_name: string;
            }[] | undefined;
        };
        buyer_info?: {
            id?: string | undefined;
            email?: string | undefined;
            username?: string | undefined;
        } | undefined;
        packages?: {
            id: string;
            items: {
                product_id: string;
                sku_id: string;
                quantity: number;
                order_item_id: string;
            }[];
            status?: string | undefined;
            shipping_provider_id?: string | undefined;
            shipping_provider_name?: string | undefined;
            tracking_number?: string | undefined;
            create_time?: number | undefined;
            update_time?: number | undefined;
        }[] | undefined;
        buyer_message?: string | undefined;
        seller_note?: string | undefined;
        shipping_type?: string | undefined;
        delivery_option_id?: string | undefined;
        delivery_option_name?: string | undefined;
        delivery_option_description?: string | undefined;
        is_cod?: boolean | undefined;
        warehouse_id?: string | undefined;
        fulfillment_type?: "FBT" | "FBS" | undefined;
        cancel_reason?: string | undefined;
        cancel_user?: string | undefined;
        rts_time?: number | undefined;
        rts_sla_time?: number | undefined;
        tts_time?: number | undefined;
        tts_sla_time?: number | undefined;
        collection_time?: number | undefined;
        paid_time?: number | undefined;
    }[];
    total: number;
    more: boolean;
    next_page_token?: string | undefined;
}, {
    orders: {
        status: TikTokOrderStatus;
        id: string;
        items: {
            id: string;
            product_id: string;
            product_name: string;
            sku_id: string;
            quantity: number;
            sale_price: number;
            variant_id?: string | undefined;
            variant_name?: string | undefined;
            sku_name?: string | undefined;
            sku_image?: string | undefined;
            seller_sku?: string | undefined;
            original_price?: number | undefined;
            platform_discount?: number | undefined;
            seller_discount?: number | undefined;
            tax?: number | undefined;
            small_order_fee?: number | undefined;
            shipping_fee?: number | undefined;
            sku_type?: "NORMAL" | "COMBO" | "VIRTUAL" | undefined;
            is_gift?: boolean | undefined;
            display_status?: string | undefined;
        }[];
        create_time: number;
        update_time: number;
        payment_info: {
            shipping_fee: number;
            currency: string;
            sub_total: number;
            total_amount: number;
            platform_discount?: number | undefined;
            seller_discount?: number | undefined;
            tax?: number | undefined;
            small_order_fee?: number | undefined;
            original_total_product_price?: number | undefined;
            original_shipping_fee?: number | undefined;
        };
        recipient_address: {
            recipient_name: string;
            phone_number: string;
            full_address: string;
            postal_code: string;
            region_code: string;
            address_line_1?: string | undefined;
            address_line_2?: string | undefined;
            address_line_3?: string | undefined;
            address_line_4?: string | undefined;
            city?: string | undefined;
            state?: string | undefined;
            district_info?: {
                address_level: string;
                address_level_name: string;
                address_name: string;
            }[] | undefined;
        };
        buyer_info?: {
            id?: string | undefined;
            email?: string | undefined;
            username?: string | undefined;
        } | undefined;
        packages?: {
            id: string;
            items: {
                product_id: string;
                sku_id: string;
                quantity: number;
                order_item_id: string;
            }[];
            status?: string | undefined;
            shipping_provider_id?: string | undefined;
            shipping_provider_name?: string | undefined;
            tracking_number?: string | undefined;
            create_time?: number | undefined;
            update_time?: number | undefined;
        }[] | undefined;
        buyer_message?: string | undefined;
        seller_note?: string | undefined;
        shipping_type?: string | undefined;
        delivery_option_id?: string | undefined;
        delivery_option_name?: string | undefined;
        delivery_option_description?: string | undefined;
        is_cod?: boolean | undefined;
        warehouse_id?: string | undefined;
        fulfillment_type?: "FBT" | "FBS" | undefined;
        cancel_reason?: string | undefined;
        cancel_user?: string | undefined;
        rts_time?: number | undefined;
        rts_sla_time?: number | undefined;
        tts_time?: number | undefined;
        tts_sla_time?: number | undefined;
        collection_time?: number | undefined;
        paid_time?: number | undefined;
    }[];
    total: number;
    more: boolean;
    next_page_token?: string | undefined;
}>;
/**
 * TikTok order detail response schema
 */
export declare const TikTokOrderDetailResponseSchema: z.ZodObject<{
    order: z.ZodObject<{
        id: z.ZodString;
        status: z.ZodNativeEnum<typeof TikTokOrderStatus>;
        create_time: z.ZodNumber;
        update_time: z.ZodNumber;
        payment_info: z.ZodObject<{
            currency: z.ZodString;
            sub_total: z.ZodNumber;
            shipping_fee: z.ZodNumber;
            seller_discount: z.ZodOptional<z.ZodNumber>;
            platform_discount: z.ZodOptional<z.ZodNumber>;
            tax: z.ZodOptional<z.ZodNumber>;
            total_amount: z.ZodNumber;
            original_total_product_price: z.ZodOptional<z.ZodNumber>;
            original_shipping_fee: z.ZodOptional<z.ZodNumber>;
            small_order_fee: z.ZodOptional<z.ZodNumber>;
        }, "strip", z.ZodTypeAny, {
            shipping_fee: number;
            currency: string;
            sub_total: number;
            total_amount: number;
            platform_discount?: number | undefined;
            seller_discount?: number | undefined;
            tax?: number | undefined;
            small_order_fee?: number | undefined;
            original_total_product_price?: number | undefined;
            original_shipping_fee?: number | undefined;
        }, {
            shipping_fee: number;
            currency: string;
            sub_total: number;
            total_amount: number;
            platform_discount?: number | undefined;
            seller_discount?: number | undefined;
            tax?: number | undefined;
            small_order_fee?: number | undefined;
            original_total_product_price?: number | undefined;
            original_shipping_fee?: number | undefined;
        }>;
        recipient_address: z.ZodObject<{
            recipient_name: z.ZodString;
            phone_number: z.ZodString;
            full_address: z.ZodString;
            address_line_1: z.ZodOptional<z.ZodString>;
            address_line_2: z.ZodOptional<z.ZodString>;
            address_line_3: z.ZodOptional<z.ZodString>;
            address_line_4: z.ZodOptional<z.ZodString>;
            city: z.ZodOptional<z.ZodString>;
            state: z.ZodOptional<z.ZodString>;
            postal_code: z.ZodString;
            region_code: z.ZodString;
            district_info: z.ZodOptional<z.ZodArray<z.ZodObject<{
                address_level: z.ZodString;
                address_level_name: z.ZodString;
                address_name: z.ZodString;
            }, "strip", z.ZodTypeAny, {
                address_level: string;
                address_level_name: string;
                address_name: string;
            }, {
                address_level: string;
                address_level_name: string;
                address_name: string;
            }>, "many">>;
        }, "strip", z.ZodTypeAny, {
            recipient_name: string;
            phone_number: string;
            full_address: string;
            postal_code: string;
            region_code: string;
            address_line_1?: string | undefined;
            address_line_2?: string | undefined;
            address_line_3?: string | undefined;
            address_line_4?: string | undefined;
            city?: string | undefined;
            state?: string | undefined;
            district_info?: {
                address_level: string;
                address_level_name: string;
                address_name: string;
            }[] | undefined;
        }, {
            recipient_name: string;
            phone_number: string;
            full_address: string;
            postal_code: string;
            region_code: string;
            address_line_1?: string | undefined;
            address_line_2?: string | undefined;
            address_line_3?: string | undefined;
            address_line_4?: string | undefined;
            city?: string | undefined;
            state?: string | undefined;
            district_info?: {
                address_level: string;
                address_level_name: string;
                address_name: string;
            }[] | undefined;
        }>;
        buyer_info: z.ZodOptional<z.ZodObject<{
            id: z.ZodOptional<z.ZodString>;
            email: z.ZodOptional<z.ZodString>;
            username: z.ZodOptional<z.ZodString>;
        }, "strip", z.ZodTypeAny, {
            id?: string | undefined;
            email?: string | undefined;
            username?: string | undefined;
        }, {
            id?: string | undefined;
            email?: string | undefined;
            username?: string | undefined;
        }>>;
        items: z.ZodArray<z.ZodObject<{
            id: z.ZodString;
            product_id: z.ZodString;
            product_name: z.ZodString;
            variant_id: z.ZodOptional<z.ZodString>;
            variant_name: z.ZodOptional<z.ZodString>;
            sku_id: z.ZodString;
            sku_name: z.ZodOptional<z.ZodString>;
            sku_image: z.ZodOptional<z.ZodString>;
            seller_sku: z.ZodOptional<z.ZodString>;
            quantity: z.ZodNumber;
            sale_price: z.ZodNumber;
            original_price: z.ZodOptional<z.ZodNumber>;
            platform_discount: z.ZodOptional<z.ZodNumber>;
            seller_discount: z.ZodOptional<z.ZodNumber>;
            tax: z.ZodOptional<z.ZodNumber>;
            small_order_fee: z.ZodOptional<z.ZodNumber>;
            shipping_fee: z.ZodOptional<z.ZodNumber>;
            sku_type: z.ZodOptional<z.ZodEnum<["NORMAL", "COMBO", "VIRTUAL"]>>;
            is_gift: z.ZodOptional<z.ZodBoolean>;
            display_status: z.ZodOptional<z.ZodString>;
        }, "strip", z.ZodTypeAny, {
            id: string;
            product_id: string;
            product_name: string;
            sku_id: string;
            quantity: number;
            sale_price: number;
            variant_id?: string | undefined;
            variant_name?: string | undefined;
            sku_name?: string | undefined;
            sku_image?: string | undefined;
            seller_sku?: string | undefined;
            original_price?: number | undefined;
            platform_discount?: number | undefined;
            seller_discount?: number | undefined;
            tax?: number | undefined;
            small_order_fee?: number | undefined;
            shipping_fee?: number | undefined;
            sku_type?: "NORMAL" | "COMBO" | "VIRTUAL" | undefined;
            is_gift?: boolean | undefined;
            display_status?: string | undefined;
        }, {
            id: string;
            product_id: string;
            product_name: string;
            sku_id: string;
            quantity: number;
            sale_price: number;
            variant_id?: string | undefined;
            variant_name?: string | undefined;
            sku_name?: string | undefined;
            sku_image?: string | undefined;
            seller_sku?: string | undefined;
            original_price?: number | undefined;
            platform_discount?: number | undefined;
            seller_discount?: number | undefined;
            tax?: number | undefined;
            small_order_fee?: number | undefined;
            shipping_fee?: number | undefined;
            sku_type?: "NORMAL" | "COMBO" | "VIRTUAL" | undefined;
            is_gift?: boolean | undefined;
            display_status?: string | undefined;
        }>, "many">;
        packages: z.ZodOptional<z.ZodArray<z.ZodObject<{
            id: z.ZodString;
            shipping_provider_id: z.ZodOptional<z.ZodString>;
            shipping_provider_name: z.ZodOptional<z.ZodString>;
            tracking_number: z.ZodOptional<z.ZodString>;
            items: z.ZodArray<z.ZodObject<{
                order_item_id: z.ZodString;
                product_id: z.ZodString;
                sku_id: z.ZodString;
                quantity: z.ZodNumber;
            }, "strip", z.ZodTypeAny, {
                product_id: string;
                sku_id: string;
                quantity: number;
                order_item_id: string;
            }, {
                product_id: string;
                sku_id: string;
                quantity: number;
                order_item_id: string;
            }>, "many">;
            status: z.ZodOptional<z.ZodString>;
            create_time: z.ZodOptional<z.ZodNumber>;
            update_time: z.ZodOptional<z.ZodNumber>;
        }, "strip", z.ZodTypeAny, {
            id: string;
            items: {
                product_id: string;
                sku_id: string;
                quantity: number;
                order_item_id: string;
            }[];
            status?: string | undefined;
            shipping_provider_id?: string | undefined;
            shipping_provider_name?: string | undefined;
            tracking_number?: string | undefined;
            create_time?: number | undefined;
            update_time?: number | undefined;
        }, {
            id: string;
            items: {
                product_id: string;
                sku_id: string;
                quantity: number;
                order_item_id: string;
            }[];
            status?: string | undefined;
            shipping_provider_id?: string | undefined;
            shipping_provider_name?: string | undefined;
            tracking_number?: string | undefined;
            create_time?: number | undefined;
            update_time?: number | undefined;
        }>, "many">>;
        buyer_message: z.ZodOptional<z.ZodString>;
        seller_note: z.ZodOptional<z.ZodString>;
        shipping_type: z.ZodOptional<z.ZodString>;
        delivery_option_id: z.ZodOptional<z.ZodString>;
        delivery_option_name: z.ZodOptional<z.ZodString>;
        delivery_option_description: z.ZodOptional<z.ZodString>;
        is_cod: z.ZodOptional<z.ZodBoolean>;
        warehouse_id: z.ZodOptional<z.ZodString>;
        fulfillment_type: z.ZodOptional<z.ZodEnum<["FBT", "FBS"]>>;
        cancel_reason: z.ZodOptional<z.ZodString>;
        cancel_user: z.ZodOptional<z.ZodString>;
        rts_time: z.ZodOptional<z.ZodNumber>;
        rts_sla_time: z.ZodOptional<z.ZodNumber>;
        tts_time: z.ZodOptional<z.ZodNumber>;
        tts_sla_time: z.ZodOptional<z.ZodNumber>;
        collection_time: z.ZodOptional<z.ZodNumber>;
        paid_time: z.ZodOptional<z.ZodNumber>;
    }, "strip", z.ZodTypeAny, {
        status: TikTokOrderStatus;
        id: string;
        items: {
            id: string;
            product_id: string;
            product_name: string;
            sku_id: string;
            quantity: number;
            sale_price: number;
            variant_id?: string | undefined;
            variant_name?: string | undefined;
            sku_name?: string | undefined;
            sku_image?: string | undefined;
            seller_sku?: string | undefined;
            original_price?: number | undefined;
            platform_discount?: number | undefined;
            seller_discount?: number | undefined;
            tax?: number | undefined;
            small_order_fee?: number | undefined;
            shipping_fee?: number | undefined;
            sku_type?: "NORMAL" | "COMBO" | "VIRTUAL" | undefined;
            is_gift?: boolean | undefined;
            display_status?: string | undefined;
        }[];
        create_time: number;
        update_time: number;
        payment_info: {
            shipping_fee: number;
            currency: string;
            sub_total: number;
            total_amount: number;
            platform_discount?: number | undefined;
            seller_discount?: number | undefined;
            tax?: number | undefined;
            small_order_fee?: number | undefined;
            original_total_product_price?: number | undefined;
            original_shipping_fee?: number | undefined;
        };
        recipient_address: {
            recipient_name: string;
            phone_number: string;
            full_address: string;
            postal_code: string;
            region_code: string;
            address_line_1?: string | undefined;
            address_line_2?: string | undefined;
            address_line_3?: string | undefined;
            address_line_4?: string | undefined;
            city?: string | undefined;
            state?: string | undefined;
            district_info?: {
                address_level: string;
                address_level_name: string;
                address_name: string;
            }[] | undefined;
        };
        buyer_info?: {
            id?: string | undefined;
            email?: string | undefined;
            username?: string | undefined;
        } | undefined;
        packages?: {
            id: string;
            items: {
                product_id: string;
                sku_id: string;
                quantity: number;
                order_item_id: string;
            }[];
            status?: string | undefined;
            shipping_provider_id?: string | undefined;
            shipping_provider_name?: string | undefined;
            tracking_number?: string | undefined;
            create_time?: number | undefined;
            update_time?: number | undefined;
        }[] | undefined;
        buyer_message?: string | undefined;
        seller_note?: string | undefined;
        shipping_type?: string | undefined;
        delivery_option_id?: string | undefined;
        delivery_option_name?: string | undefined;
        delivery_option_description?: string | undefined;
        is_cod?: boolean | undefined;
        warehouse_id?: string | undefined;
        fulfillment_type?: "FBT" | "FBS" | undefined;
        cancel_reason?: string | undefined;
        cancel_user?: string | undefined;
        rts_time?: number | undefined;
        rts_sla_time?: number | undefined;
        tts_time?: number | undefined;
        tts_sla_time?: number | undefined;
        collection_time?: number | undefined;
        paid_time?: number | undefined;
    }, {
        status: TikTokOrderStatus;
        id: string;
        items: {
            id: string;
            product_id: string;
            product_name: string;
            sku_id: string;
            quantity: number;
            sale_price: number;
            variant_id?: string | undefined;
            variant_name?: string | undefined;
            sku_name?: string | undefined;
            sku_image?: string | undefined;
            seller_sku?: string | undefined;
            original_price?: number | undefined;
            platform_discount?: number | undefined;
            seller_discount?: number | undefined;
            tax?: number | undefined;
            small_order_fee?: number | undefined;
            shipping_fee?: number | undefined;
            sku_type?: "NORMAL" | "COMBO" | "VIRTUAL" | undefined;
            is_gift?: boolean | undefined;
            display_status?: string | undefined;
        }[];
        create_time: number;
        update_time: number;
        payment_info: {
            shipping_fee: number;
            currency: string;
            sub_total: number;
            total_amount: number;
            platform_discount?: number | undefined;
            seller_discount?: number | undefined;
            tax?: number | undefined;
            small_order_fee?: number | undefined;
            original_total_product_price?: number | undefined;
            original_shipping_fee?: number | undefined;
        };
        recipient_address: {
            recipient_name: string;
            phone_number: string;
            full_address: string;
            postal_code: string;
            region_code: string;
            address_line_1?: string | undefined;
            address_line_2?: string | undefined;
            address_line_3?: string | undefined;
            address_line_4?: string | undefined;
            city?: string | undefined;
            state?: string | undefined;
            district_info?: {
                address_level: string;
                address_level_name: string;
                address_name: string;
            }[] | undefined;
        };
        buyer_info?: {
            id?: string | undefined;
            email?: string | undefined;
            username?: string | undefined;
        } | undefined;
        packages?: {
            id: string;
            items: {
                product_id: string;
                sku_id: string;
                quantity: number;
                order_item_id: string;
            }[];
            status?: string | undefined;
            shipping_provider_id?: string | undefined;
            shipping_provider_name?: string | undefined;
            tracking_number?: string | undefined;
            create_time?: number | undefined;
            update_time?: number | undefined;
        }[] | undefined;
        buyer_message?: string | undefined;
        seller_note?: string | undefined;
        shipping_type?: string | undefined;
        delivery_option_id?: string | undefined;
        delivery_option_name?: string | undefined;
        delivery_option_description?: string | undefined;
        is_cod?: boolean | undefined;
        warehouse_id?: string | undefined;
        fulfillment_type?: "FBT" | "FBS" | undefined;
        cancel_reason?: string | undefined;
        cancel_user?: string | undefined;
        rts_time?: number | undefined;
        rts_sla_time?: number | undefined;
        tts_time?: number | undefined;
        tts_sla_time?: number | undefined;
        collection_time?: number | undefined;
        paid_time?: number | undefined;
    }>;
}, "strip", z.ZodTypeAny, {
    order: {
        status: TikTokOrderStatus;
        id: string;
        items: {
            id: string;
            product_id: string;
            product_name: string;
            sku_id: string;
            quantity: number;
            sale_price: number;
            variant_id?: string | undefined;
            variant_name?: string | undefined;
            sku_name?: string | undefined;
            sku_image?: string | undefined;
            seller_sku?: string | undefined;
            original_price?: number | undefined;
            platform_discount?: number | undefined;
            seller_discount?: number | undefined;
            tax?: number | undefined;
            small_order_fee?: number | undefined;
            shipping_fee?: number | undefined;
            sku_type?: "NORMAL" | "COMBO" | "VIRTUAL" | undefined;
            is_gift?: boolean | undefined;
            display_status?: string | undefined;
        }[];
        create_time: number;
        update_time: number;
        payment_info: {
            shipping_fee: number;
            currency: string;
            sub_total: number;
            total_amount: number;
            platform_discount?: number | undefined;
            seller_discount?: number | undefined;
            tax?: number | undefined;
            small_order_fee?: number | undefined;
            original_total_product_price?: number | undefined;
            original_shipping_fee?: number | undefined;
        };
        recipient_address: {
            recipient_name: string;
            phone_number: string;
            full_address: string;
            postal_code: string;
            region_code: string;
            address_line_1?: string | undefined;
            address_line_2?: string | undefined;
            address_line_3?: string | undefined;
            address_line_4?: string | undefined;
            city?: string | undefined;
            state?: string | undefined;
            district_info?: {
                address_level: string;
                address_level_name: string;
                address_name: string;
            }[] | undefined;
        };
        buyer_info?: {
            id?: string | undefined;
            email?: string | undefined;
            username?: string | undefined;
        } | undefined;
        packages?: {
            id: string;
            items: {
                product_id: string;
                sku_id: string;
                quantity: number;
                order_item_id: string;
            }[];
            status?: string | undefined;
            shipping_provider_id?: string | undefined;
            shipping_provider_name?: string | undefined;
            tracking_number?: string | undefined;
            create_time?: number | undefined;
            update_time?: number | undefined;
        }[] | undefined;
        buyer_message?: string | undefined;
        seller_note?: string | undefined;
        shipping_type?: string | undefined;
        delivery_option_id?: string | undefined;
        delivery_option_name?: string | undefined;
        delivery_option_description?: string | undefined;
        is_cod?: boolean | undefined;
        warehouse_id?: string | undefined;
        fulfillment_type?: "FBT" | "FBS" | undefined;
        cancel_reason?: string | undefined;
        cancel_user?: string | undefined;
        rts_time?: number | undefined;
        rts_sla_time?: number | undefined;
        tts_time?: number | undefined;
        tts_sla_time?: number | undefined;
        collection_time?: number | undefined;
        paid_time?: number | undefined;
    };
}, {
    order: {
        status: TikTokOrderStatus;
        id: string;
        items: {
            id: string;
            product_id: string;
            product_name: string;
            sku_id: string;
            quantity: number;
            sale_price: number;
            variant_id?: string | undefined;
            variant_name?: string | undefined;
            sku_name?: string | undefined;
            sku_image?: string | undefined;
            seller_sku?: string | undefined;
            original_price?: number | undefined;
            platform_discount?: number | undefined;
            seller_discount?: number | undefined;
            tax?: number | undefined;
            small_order_fee?: number | undefined;
            shipping_fee?: number | undefined;
            sku_type?: "NORMAL" | "COMBO" | "VIRTUAL" | undefined;
            is_gift?: boolean | undefined;
            display_status?: string | undefined;
        }[];
        create_time: number;
        update_time: number;
        payment_info: {
            shipping_fee: number;
            currency: string;
            sub_total: number;
            total_amount: number;
            platform_discount?: number | undefined;
            seller_discount?: number | undefined;
            tax?: number | undefined;
            small_order_fee?: number | undefined;
            original_total_product_price?: number | undefined;
            original_shipping_fee?: number | undefined;
        };
        recipient_address: {
            recipient_name: string;
            phone_number: string;
            full_address: string;
            postal_code: string;
            region_code: string;
            address_line_1?: string | undefined;
            address_line_2?: string | undefined;
            address_line_3?: string | undefined;
            address_line_4?: string | undefined;
            city?: string | undefined;
            state?: string | undefined;
            district_info?: {
                address_level: string;
                address_level_name: string;
                address_name: string;
            }[] | undefined;
        };
        buyer_info?: {
            id?: string | undefined;
            email?: string | undefined;
            username?: string | undefined;
        } | undefined;
        packages?: {
            id: string;
            items: {
                product_id: string;
                sku_id: string;
                quantity: number;
                order_item_id: string;
            }[];
            status?: string | undefined;
            shipping_provider_id?: string | undefined;
            shipping_provider_name?: string | undefined;
            tracking_number?: string | undefined;
            create_time?: number | undefined;
            update_time?: number | undefined;
        }[] | undefined;
        buyer_message?: string | undefined;
        seller_note?: string | undefined;
        shipping_type?: string | undefined;
        delivery_option_id?: string | undefined;
        delivery_option_name?: string | undefined;
        delivery_option_description?: string | undefined;
        is_cod?: boolean | undefined;
        warehouse_id?: string | undefined;
        fulfillment_type?: "FBT" | "FBS" | undefined;
        cancel_reason?: string | undefined;
        cancel_user?: string | undefined;
        rts_time?: number | undefined;
        rts_sla_time?: number | undefined;
        tts_time?: number | undefined;
        tts_sla_time?: number | undefined;
        collection_time?: number | undefined;
        paid_time?: number | undefined;
    };
}>;
/**
 * TikTok tracking update request schema
 */
export declare const TikTokTrackingUpdateSchema: z.ZodObject<{
    order_id: z.ZodString;
    tracking_number: z.ZodString;
    shipping_provider_id: z.ZodOptional<z.ZodString>;
    shipping_provider_name: z.ZodOptional<z.ZodString>;
    upload_time: z.ZodOptional<z.ZodNumber>;
}, "strip", z.ZodTypeAny, {
    tracking_number: string;
    order_id: string;
    shipping_provider_id?: string | undefined;
    shipping_provider_name?: string | undefined;
    upload_time?: number | undefined;
}, {
    tracking_number: string;
    order_id: string;
    shipping_provider_id?: string | undefined;
    shipping_provider_name?: string | undefined;
    upload_time?: number | undefined;
}>;
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
    customer: {
        name: string;
        email?: string;
        phone: string;
    };
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
    items: Array<{
        id: string;
        productId: string;
        productName: string;
        sku: string;
        quantity: number;
        price: number;
        totalPrice: number;
    }>;
    payment: {
        currency: string;
        subtotal: number;
        shippingFee: number;
        tax: number;
        discounts: number;
        total: number;
    };
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
    buyerMessage?: string;
    sellerNote?: string;
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
//# sourceMappingURL=tiktok-order.d.ts.map