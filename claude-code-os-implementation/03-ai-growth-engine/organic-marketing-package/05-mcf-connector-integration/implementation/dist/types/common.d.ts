/**
 * Common Types and Enums for MCF Connector
 *
 * Shared type definitions used across the connector:
 * - Order status enums
 * - Error types
 * - Result/response types
 * - Utility types
 */
/**
 * TikTok Shop order status
 */
export declare enum TikTokOrderStatus {
    UNPAID = "UNPAID",
    AWAITING_SHIPMENT = "AWAITING_SHIPMENT",
    AWAITING_COLLECTION = "AWAITING_COLLECTION",
    IN_TRANSIT = "IN_TRANSIT",
    DELIVERED = "DELIVERED",
    CANCELLED = "CANCELLED",
    COMPLETED = "COMPLETED"
}
/**
 * Amazon MCF fulfillment order status
 */
export declare enum MCFFulfillmentStatus {
    RECEIVED = "RECEIVED",
    INVALID = "INVALID",
    PLANNING = "PLANNING",
    PROCESSING = "PROCESSING",
    CANCELLED = "CANCELLED",
    COMPLETE = "COMPLETE",
    COMPLETE_PARTIALLED = "COMPLETE_PARTIALLED",
    UNFULFILLABLE = "UNFULFILLABLE"
}
/**
 * Internal connector processing status
 */
export declare enum ProcessingStatus {
    PENDING = "PENDING",
    VALIDATING = "VALIDATING",
    VALIDATED = "VALIDATED",
    TRANSFORMING = "TRANSFORMING",
    CREATING_MCF_ORDER = "CREATING_MCF_ORDER",
    MCF_ORDER_CREATED = "MCF_ORDER_CREATED",
    SYNCING_TRACKING = "SYNCING_TRACKING",
    COMPLETED = "COMPLETED",
    FAILED = "FAILED"
}
/**
 * Shipment carrier types
 */
export declare enum ShipmentCarrier {
    UPS = "UPS",
    USPS = "USPS",
    FEDEX = "FEDEX",
    DHL = "DHL",
    AMAZON_LOGISTICS = "AMAZON_LOGISTICS",
    OTHER = "OTHER"
}
/**
 * Error codes for MCF Connector operations
 */
export declare enum ErrorCode {
    INVALID_ORDER_DATA = "INVALID_ORDER_DATA",
    INVALID_ADDRESS = "INVALID_ADDRESS",
    INVALID_PRODUCT_SKU = "INVALID_PRODUCT_SKU",
    INSUFFICIENT_INVENTORY = "INSUFFICIENT_INVENTORY",
    INVENTORY_CHECK_FAILED = "INVENTORY_CHECK_FAILED",
    TIKTOK_API_ERROR = "TIKTOK_API_ERROR",
    AMAZON_API_ERROR = "AMAZON_API_ERROR",
    AUTHENTICATION_FAILED = "AUTHENTICATION_FAILED",
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED",
    TRANSFORMATION_FAILED = "TRANSFORMATION_FAILED",
    ORDER_CREATION_FAILED = "ORDER_CREATION_FAILED",
    TRACKING_SYNC_FAILED = "TRACKING_SYNC_FAILED",
    NETWORK_ERROR = "NETWORK_ERROR",
    TIMEOUT_ERROR = "TIMEOUT_ERROR",
    UNKNOWN_ERROR = "UNKNOWN_ERROR"
}
/**
 * Base error interface for connector errors
 */
export interface ConnectorError {
    code: ErrorCode;
    message: string;
    details?: Record<string, unknown>;
    timestamp: Date;
    retryable: boolean;
}
/**
 * Generic success result
 */
export interface SuccessResult<T> {
    success: true;
    data: T;
    timestamp: Date;
}
/**
 * Generic error result
 */
export interface ErrorResult {
    success: false;
    error: ConnectorError;
    timestamp: Date;
}
/**
 * Generic result type (success or error)
 */
export type Result<T> = SuccessResult<T> | ErrorResult;
/**
 * Normalized address structure
 */
export interface Address {
    name: string;
    addressLine1: string;
    addressLine2?: string;
    city: string;
    stateOrRegion: string;
    postalCode: string;
    countryCode: string;
    phoneNumber?: string;
}
/**
 * Product item in an order
 */
export interface OrderItem {
    sku: string;
    productName: string;
    quantity: number;
    price: number;
    currency: string;
}
/**
 * Tracking information
 */
export interface TrackingInfo {
    trackingNumber: string;
    carrier: ShipmentCarrier;
    carrierCode?: string;
    shippedAt?: Date;
    estimatedDeliveryAt?: Date;
    deliveredAt?: Date;
}
/**
 * Pagination parameters for list operations
 */
export interface PaginationParams {
    pageSize?: number;
    pageToken?: string;
}
/**
 * Paginated response wrapper
 */
export interface PaginatedResponse<T> {
    items: T[];
    nextPageToken?: string;
    totalCount?: number;
}
/**
 * Webhook event types
 */
export declare enum WebhookEventType {
    ORDER_RECEIVED = "ORDER_RECEIVED",
    ORDER_VALIDATED = "ORDER_VALIDATED",
    ORDER_VALIDATION_FAILED = "ORDER_VALIDATION_FAILED",
    MCF_ORDER_CREATED = "MCF_ORDER_CREATED",
    MCF_ORDER_FAILED = "MCF_ORDER_FAILED",
    TRACKING_SYNCED = "TRACKING_SYNCED",
    TRACKING_SYNC_FAILED = "TRACKING_SYNC_FAILED",
    INVENTORY_LOW = "INVENTORY_LOW"
}
/**
 * Webhook event payload
 */
export interface WebhookEvent {
    eventType: WebhookEventType;
    orderId: string;
    timestamp: Date;
    data: Record<string, unknown>;
    error?: ConnectorError;
}
/**
 * Make specific properties optional
 */
export type PartialBy<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>;
/**
 * Make specific properties required
 */
export type RequiredBy<T, K extends keyof T> = Omit<T, K> & Required<Pick<T, K>>;
/**
 * Extract non-nullable type
 */
export type NonNullable<T> = T extends null | undefined ? never : T;
/**
 * Async function type
 */
export type AsyncFunction<T = void> = () => Promise<T>;
//# sourceMappingURL=common.d.ts.map