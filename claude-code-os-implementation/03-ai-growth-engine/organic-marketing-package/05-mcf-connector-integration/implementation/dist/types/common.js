"use strict";
/**
 * Common Types and Enums for MCF Connector
 *
 * Shared type definitions used across the connector:
 * - Order status enums
 * - Error types
 * - Result/response types
 * - Utility types
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.WebhookEventType = exports.ErrorCode = exports.ShipmentCarrier = exports.ProcessingStatus = exports.MCFFulfillmentStatus = exports.TikTokOrderStatus = void 0;
// ============================================================
// Order Status Enums
// ============================================================
/**
 * TikTok Shop order status
 */
var TikTokOrderStatus;
(function (TikTokOrderStatus) {
    TikTokOrderStatus["UNPAID"] = "UNPAID";
    TikTokOrderStatus["AWAITING_SHIPMENT"] = "AWAITING_SHIPMENT";
    TikTokOrderStatus["AWAITING_COLLECTION"] = "AWAITING_COLLECTION";
    TikTokOrderStatus["IN_TRANSIT"] = "IN_TRANSIT";
    TikTokOrderStatus["DELIVERED"] = "DELIVERED";
    TikTokOrderStatus["CANCELLED"] = "CANCELLED";
    TikTokOrderStatus["COMPLETED"] = "COMPLETED";
})(TikTokOrderStatus || (exports.TikTokOrderStatus = TikTokOrderStatus = {}));
/**
 * Amazon MCF fulfillment order status
 */
var MCFFulfillmentStatus;
(function (MCFFulfillmentStatus) {
    MCFFulfillmentStatus["RECEIVED"] = "RECEIVED";
    MCFFulfillmentStatus["INVALID"] = "INVALID";
    MCFFulfillmentStatus["PLANNING"] = "PLANNING";
    MCFFulfillmentStatus["PROCESSING"] = "PROCESSING";
    MCFFulfillmentStatus["CANCELLED"] = "CANCELLED";
    MCFFulfillmentStatus["COMPLETE"] = "COMPLETE";
    MCFFulfillmentStatus["COMPLETE_PARTIALLED"] = "COMPLETE_PARTIALLED";
    MCFFulfillmentStatus["UNFULFILLABLE"] = "UNFULFILLABLE";
})(MCFFulfillmentStatus || (exports.MCFFulfillmentStatus = MCFFulfillmentStatus = {}));
/**
 * Internal connector processing status
 */
var ProcessingStatus;
(function (ProcessingStatus) {
    ProcessingStatus["PENDING"] = "PENDING";
    ProcessingStatus["VALIDATING"] = "VALIDATING";
    ProcessingStatus["VALIDATED"] = "VALIDATED";
    ProcessingStatus["TRANSFORMING"] = "TRANSFORMING";
    ProcessingStatus["CREATING_MCF_ORDER"] = "CREATING_MCF_ORDER";
    ProcessingStatus["MCF_ORDER_CREATED"] = "MCF_ORDER_CREATED";
    ProcessingStatus["SYNCING_TRACKING"] = "SYNCING_TRACKING";
    ProcessingStatus["COMPLETED"] = "COMPLETED";
    ProcessingStatus["FAILED"] = "FAILED";
})(ProcessingStatus || (exports.ProcessingStatus = ProcessingStatus = {}));
/**
 * Shipment carrier types
 */
var ShipmentCarrier;
(function (ShipmentCarrier) {
    ShipmentCarrier["UPS"] = "UPS";
    ShipmentCarrier["USPS"] = "USPS";
    ShipmentCarrier["FEDEX"] = "FEDEX";
    ShipmentCarrier["DHL"] = "DHL";
    ShipmentCarrier["AMAZON_LOGISTICS"] = "AMAZON_LOGISTICS";
    ShipmentCarrier["OTHER"] = "OTHER";
})(ShipmentCarrier || (exports.ShipmentCarrier = ShipmentCarrier = {}));
// ============================================================
// Error Types
// ============================================================
/**
 * Error codes for MCF Connector operations
 */
var ErrorCode;
(function (ErrorCode) {
    // Validation Errors
    ErrorCode["INVALID_ORDER_DATA"] = "INVALID_ORDER_DATA";
    ErrorCode["INVALID_ADDRESS"] = "INVALID_ADDRESS";
    ErrorCode["INVALID_PRODUCT_SKU"] = "INVALID_PRODUCT_SKU";
    // Inventory Errors
    ErrorCode["INSUFFICIENT_INVENTORY"] = "INSUFFICIENT_INVENTORY";
    ErrorCode["INVENTORY_CHECK_FAILED"] = "INVENTORY_CHECK_FAILED";
    // API Errors
    ErrorCode["TIKTOK_API_ERROR"] = "TIKTOK_API_ERROR";
    ErrorCode["AMAZON_API_ERROR"] = "AMAZON_API_ERROR";
    ErrorCode["AUTHENTICATION_FAILED"] = "AUTHENTICATION_FAILED";
    ErrorCode["RATE_LIMIT_EXCEEDED"] = "RATE_LIMIT_EXCEEDED";
    // Processing Errors
    ErrorCode["TRANSFORMATION_FAILED"] = "TRANSFORMATION_FAILED";
    ErrorCode["ORDER_CREATION_FAILED"] = "ORDER_CREATION_FAILED";
    ErrorCode["TRACKING_SYNC_FAILED"] = "TRACKING_SYNC_FAILED";
    // System Errors
    ErrorCode["NETWORK_ERROR"] = "NETWORK_ERROR";
    ErrorCode["TIMEOUT_ERROR"] = "TIMEOUT_ERROR";
    ErrorCode["UNKNOWN_ERROR"] = "UNKNOWN_ERROR";
})(ErrorCode || (exports.ErrorCode = ErrorCode = {}));
// ============================================================
// Webhook Types
// ============================================================
/**
 * Webhook event types
 */
var WebhookEventType;
(function (WebhookEventType) {
    WebhookEventType["ORDER_RECEIVED"] = "ORDER_RECEIVED";
    WebhookEventType["ORDER_VALIDATED"] = "ORDER_VALIDATED";
    WebhookEventType["ORDER_VALIDATION_FAILED"] = "ORDER_VALIDATION_FAILED";
    WebhookEventType["MCF_ORDER_CREATED"] = "MCF_ORDER_CREATED";
    WebhookEventType["MCF_ORDER_FAILED"] = "MCF_ORDER_FAILED";
    WebhookEventType["TRACKING_SYNCED"] = "TRACKING_SYNCED";
    WebhookEventType["TRACKING_SYNC_FAILED"] = "TRACKING_SYNC_FAILED";
    WebhookEventType["INVENTORY_LOW"] = "INVENTORY_LOW";
})(WebhookEventType || (exports.WebhookEventType = WebhookEventType = {}));
//# sourceMappingURL=common.js.map