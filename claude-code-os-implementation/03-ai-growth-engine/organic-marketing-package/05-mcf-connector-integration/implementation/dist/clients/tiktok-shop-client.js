"use strict";
/**
 * TikTok Shop Client - Core API client for TikTok Shop integration
 *
 * Features:
 * - OAuth2 authentication with refresh tokens
 * - API signature generation (HMAC-SHA256)
 * - Exponential backoff retry logic
 * - Order retrieval and pagination
 * - Tracking number updates
 */
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.TikTokShopClient = void 0;
const axios_1 = __importDefault(require("axios"));
const crypto_1 = __importDefault(require("crypto"));
const tiktok_order_1 = require("../types/tiktok-order");
const common_1 = require("../types/common");
// ============================================================
// Constants
// ============================================================
const DEFAULT_RETRY_CONFIG = {
    maxRetries: 3,
    initialDelay: 1000,
    backoffMultiplier: 2,
    maxDelay: 30000,
};
const API_VERSION = '202309';
const TOKEN_REFRESH_ENDPOINT = '/api/token/refresh';
const ORDERS_LIST_ENDPOINT = '/order/202309/orders/search';
const ORDER_DETAIL_ENDPOINT = '/order/202309/orders/{order_id}';
const UPDATE_TRACKING_ENDPOINT = '/fulfillment/202309/packages/{package_id}/tracking';
// TikTok API error codes that are retryable
const RETRYABLE_ERROR_CODES = [
    1000002, // Rate limit exceeded
    1000004, // Service temporarily unavailable
    1000005, // Internal server error
];
// ============================================================
// Helper Functions
// ============================================================
/**
 * Sleep for specified milliseconds
 */
function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}
/**
 * Generate TikTok Shop API signature
 *
 * TikTok uses HMAC-SHA256 for request signing:
 * 1. Concatenate: app_key + timestamp + path + query_string + body
 * 2. Generate HMAC-SHA256 with app_secret
 */
function generateSignature(appSecret, appKey, timestamp, path, queryString, body) {
    const input = `${appKey}${timestamp}${path}${queryString}${body}`;
    const hmac = crypto_1.default.createHmac('sha256', appSecret);
    hmac.update(input);
    return hmac.digest('hex');
}
/**
 * Build query string from parameters
 */
function buildQueryString(params) {
    const entries = Object.entries(params)
        .filter(([_, value]) => value !== undefined && value !== null)
        .sort(([keyA], [keyB]) => keyA.localeCompare(keyB))
        .map(([key, value]) => {
        if (Array.isArray(value)) {
            return value.map(v => `${key}=${encodeURIComponent(String(v))}`).join('&');
        }
        return `${key}=${encodeURIComponent(String(value))}`;
    });
    return entries.join('&');
}
/**
 * Check if error is retryable
 */
function isRetryableError(error) {
    if ('retryable' in error) {
        return error.retryable;
    }
    if (axios_1.default.isAxiosError(error)) {
        // Network errors are retryable
        if (!error.response) {
            return true;
        }
        // 5xx errors are retryable
        if (error.response.status >= 500) {
            return true;
        }
        // Check TikTok-specific error codes
        const data = error.response.data;
        if (data?.code && RETRYABLE_ERROR_CODES.includes(data.code)) {
            return true;
        }
        // 429 (rate limit) is retryable
        if (error.response.status === 429) {
            return true;
        }
    }
    return false;
}
/**
 * Convert TikTok API error to ConnectorError
 */
function handleTikTokError(error) {
    if (axios_1.default.isAxiosError(error)) {
        const response = error.response?.data;
        // Authentication errors
        if (error.response?.status === 401 || error.response?.status === 403) {
            return {
                code: common_1.ErrorCode.AUTHENTICATION_FAILED,
                message: response?.message || 'Authentication failed',
                details: response,
                retryable: false,
            };
        }
        // Rate limit errors
        if (error.response?.status === 429 || response?.code === 1000002) {
            return {
                code: common_1.ErrorCode.RATE_LIMIT_EXCEEDED,
                message: 'Rate limit exceeded',
                details: response,
                retryable: true,
            };
        }
        // Network errors
        if (!error.response) {
            return {
                code: common_1.ErrorCode.NETWORK_ERROR,
                message: error.message || 'Network error occurred',
                details: error,
                retryable: true,
            };
        }
        // TikTok API errors
        return {
            code: common_1.ErrorCode.TIKTOK_API_ERROR,
            message: response?.message || error.message || 'TikTok API error',
            details: response,
            retryable: isRetryableError(error),
        };
    }
    // Unknown errors
    return {
        code: common_1.ErrorCode.UNKNOWN_ERROR,
        message: error instanceof Error ? error.message : 'Unknown error occurred',
        details: error,
        retryable: false,
    };
}
// ============================================================
// TikTok Shop Client Class
// ============================================================
class TikTokShopClient {
    config;
    retryConfig;
    httpClient;
    accessToken;
    constructor(config, retryConfig = {}) {
        this.config = config;
        this.retryConfig = { ...DEFAULT_RETRY_CONFIG, ...retryConfig };
        this.accessToken = config.accessToken;
        // Create axios instance with base configuration
        this.httpClient = axios_1.default.create({
            baseURL: config.apiBaseUrl,
            timeout: 30000,
            headers: {
                'Content-Type': 'application/json',
            },
        });
        // Add request interceptor for authentication and signing
        this.httpClient.interceptors.request.use(config => {
            const timestamp = Math.floor(Date.now() / 1000);
            const path = config.url || '';
            const queryString = buildQueryString(config.params || {});
            const body = config.data ? JSON.stringify(config.data) : '';
            const signature = generateSignature(this.config.appSecret, this.config.appKey, timestamp, path, queryString, body);
            config.headers = config.headers || {};
            config.headers['x-tts-access-token'] = this.accessToken;
            config.headers['x-tts-app-key'] = this.config.appKey;
            config.headers['x-tts-timestamp'] = String(timestamp);
            config.headers['x-tts-sign'] = signature;
            return config;
        });
    }
    /**
     * Execute API call with retry logic
     */
    async executeWithRetry(operation, operationName) {
        let lastError;
        let delay = this.retryConfig.initialDelay;
        for (let attempt = 0; attempt <= this.retryConfig.maxRetries; attempt++) {
            try {
                return await operation();
            }
            catch (error) {
                lastError = handleTikTokError(error);
                // If error is not retryable, throw immediately
                if (!lastError.retryable) {
                    throw lastError;
                }
                // If this was the last attempt, throw
                if (attempt === this.retryConfig.maxRetries) {
                    throw lastError;
                }
                // Wait before retrying
                await sleep(delay);
                delay = Math.min(delay * this.retryConfig.backoffMultiplier, this.retryConfig.maxDelay);
            }
        }
        // This should never be reached, but TypeScript needs it
        throw lastError || new Error(`${operationName} failed after retries`);
    }
    /**
     * Refresh OAuth2 access token
     */
    async refreshAccessToken() {
        try {
            const timestamp = Math.floor(Date.now() / 1000);
            const queryString = buildQueryString({
                app_key: this.config.appKey,
                grant_type: 'refresh_token',
                refresh_token: this.config.refreshToken,
            });
            const signature = generateSignature(this.config.appSecret, this.config.appKey, timestamp, TOKEN_REFRESH_ENDPOINT, queryString, '');
            const response = await axios_1.default.post(`${this.config.apiBaseUrl}${TOKEN_REFRESH_ENDPOINT}`, null, {
                params: {
                    app_key: this.config.appKey,
                    grant_type: 'refresh_token',
                    refresh_token: this.config.refreshToken,
                },
                headers: {
                    'x-tts-app-key': this.config.appKey,
                    'x-tts-timestamp': String(timestamp),
                    'x-tts-sign': signature,
                },
            });
            if (response.data.code !== 0) {
                throw new Error(`Token refresh failed: ${response.data.message}`);
            }
            this.accessToken = response.data.data.access_token;
        }
        catch (error) {
            throw handleTikTokError(error);
        }
    }
    /**
     * Get list of orders with optional filters
     */
    async getOrders(params = {}) {
        return this.executeWithRetry(async () => {
            const requestParams = {
                shop_cipher: this.config.shopId,
            };
            if (params.create_time_from)
                requestParams.create_time_from = params.create_time_from;
            if (params.create_time_to)
                requestParams.create_time_to = params.create_time_to;
            if (params.update_time_from)
                requestParams.update_time_from = params.update_time_from;
            if (params.update_time_to)
                requestParams.update_time_to = params.update_time_to;
            if (params.order_status) {
                requestParams.order_status = Array.isArray(params.order_status)
                    ? params.order_status
                    : [params.order_status];
            }
            if (params.page_size)
                requestParams.page_size = params.page_size;
            if (params.page_token)
                requestParams.cursor = params.page_token;
            if (params.sort_by)
                requestParams.sort_by = params.sort_by;
            if (params.sort_order)
                requestParams.sort_type = params.sort_order === 'ASC' ? 1 : 2;
            const response = await this.httpClient.post(ORDERS_LIST_ENDPOINT, requestParams);
            if (response.data.code !== 0) {
                throw new Error(`Get orders failed: ${response.data.message}`);
            }
            // Validate response with Zod schema
            const validated = tiktok_order_1.TikTokOrderListResponseSchema.parse(response.data.data);
            return validated;
        }, 'getOrders');
    }
    /**
     * Get detailed information for a specific order
     */
    async getOrderDetail(orderId) {
        return this.executeWithRetry(async () => {
            const endpoint = ORDER_DETAIL_ENDPOINT.replace('{order_id}', orderId);
            const response = await this.httpClient.get(endpoint, {
                params: {
                    shop_cipher: this.config.shopId,
                },
            });
            if (response.data.code !== 0) {
                throw new Error(`Get order detail failed: ${response.data.message}`);
            }
            // Validate response with Zod schema
            const validated = tiktok_order_1.TikTokOrderDetailResponseSchema.parse(response.data.data);
            return validated.order;
        }, 'getOrderDetail');
    }
    /**
     * Update tracking information for an order package
     */
    async updateTrackingInfo(packageId, trackingInfo) {
        return this.executeWithRetry(async () => {
            const endpoint = UPDATE_TRACKING_ENDPOINT.replace('{package_id}', packageId);
            const requestBody = {
                tracking_number: trackingInfo.tracking_number,
                shipping_provider_id: trackingInfo.shipping_provider_id,
                shipping_provider_name: trackingInfo.shipping_provider_name,
            };
            const response = await this.httpClient.post(endpoint, requestBody);
            if (response.data.code !== 0) {
                throw new Error(`Update tracking failed: ${response.data.message}`);
            }
            return {
                order_id: trackingInfo.order_id,
                updated: true,
            };
        }, 'updateTrackingInfo');
    }
    /**
     * Test API connection and authentication
     */
    async testConnection() {
        try {
            // Try to fetch orders with minimal parameters
            await this.getOrders({ page_size: 1 });
            return true;
        }
        catch (error) {
            return false;
        }
    }
}
exports.TikTokShopClient = TikTokShopClient;
//# sourceMappingURL=tiktok-shop-client.js.map