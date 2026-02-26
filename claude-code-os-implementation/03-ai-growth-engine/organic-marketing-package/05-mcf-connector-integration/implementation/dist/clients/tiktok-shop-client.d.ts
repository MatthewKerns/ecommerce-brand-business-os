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
import type { TikTokShopConfig, RetryConfig } from '../types/config';
import type { TikTokOrder, TikTokOrderListParams, TikTokOrderListResponse, TikTokTrackingUpdate } from '../types/tiktok-order';
import { ErrorCode } from '../types/common';
export interface TikTokShopClientConfig extends TikTokShopConfig {
}
export interface TikTokApiResponse<T> {
    code: number;
    message: string;
    data: T;
    request_id: string;
}
export interface TikTokTokenResponse {
    access_token: string;
    access_token_expire_in: number;
    refresh_token: string;
    refresh_token_expire_in: number;
    open_id: string;
    seller_name: string;
    seller_base_region: string;
    user_type: number;
}
export interface UpdateTrackingResponse {
    order_id: string;
    updated: boolean;
}
export interface TikTokShopError {
    code: ErrorCode;
    message: string;
    details?: unknown;
    retryable: boolean;
}
export declare class TikTokShopClient {
    private readonly config;
    private readonly retryConfig;
    private readonly httpClient;
    private accessToken;
    constructor(config: TikTokShopClientConfig, retryConfig?: RetryConfig);
    /**
     * Execute API call with retry logic
     */
    private executeWithRetry;
    /**
     * Refresh OAuth2 access token
     */
    refreshAccessToken(): Promise<void>;
    /**
     * Get list of orders with optional filters
     */
    getOrders(params?: TikTokOrderListParams): Promise<TikTokOrderListResponse>;
    /**
     * Get detailed information for a specific order
     */
    getOrderDetail(orderId: string): Promise<TikTokOrder>;
    /**
     * Update tracking information for an order package
     */
    updateTrackingInfo(packageId: string, trackingInfo: TikTokTrackingUpdate): Promise<UpdateTrackingResponse>;
    /**
     * Test API connection and authentication
     */
    testConnection(): Promise<boolean>;
}
//# sourceMappingURL=tiktok-shop-client.d.ts.map