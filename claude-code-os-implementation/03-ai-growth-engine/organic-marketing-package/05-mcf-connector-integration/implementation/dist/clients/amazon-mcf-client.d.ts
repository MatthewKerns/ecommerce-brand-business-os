/**
 * Amazon MCF Client - Core API client for Amazon Multi-Channel Fulfillment
 *
 * Features:
 * - LWA (Login with Amazon) OAuth2 authentication
 * - AWS Signature Version 4 request signing
 * - Exponential backoff retry logic
 * - Fulfillment order creation and retrieval
 * - Package tracking information
 */
import type { AmazonMCFConfig, RetryConfig } from '../types/config';
import type { MCFCreateFulfillmentOrderResponse, MCFGetFulfillmentOrderResponse, MCFPackageTrackingDetails, CreateMCFOrderParams, GetMCFOrderParams } from '../types/mcf-order';
import { ErrorCode } from '../types/common';
export interface AmazonMCFClientConfig extends AmazonMCFConfig {
}
export interface LWATokenResponse {
    access_token: string;
    refresh_token: string;
    token_type: string;
    expires_in: number;
}
export interface AmazonApiError {
    code: ErrorCode;
    message: string;
    details?: unknown;
    retryable: boolean;
}
export interface AWSSignatureParams {
    method: string;
    path: string;
    queryString: string;
    headers: Record<string, string>;
    body: string;
    timestamp: string;
}
export declare class AmazonMCFClient {
    private readonly config;
    private readonly retryConfig;
    private readonly httpClient;
    private readonly endpoint;
    private accessToken;
    private tokenExpiresAt;
    constructor(config: AmazonMCFClientConfig, retryConfig?: RetryConfig);
    /**
     * Ensure we have a valid LWA access token
     */
    private ensureValidToken;
    /**
     * Refresh LWA access token
     */
    refreshAccessToken(): Promise<void>;
    /**
     * Execute API call with exponential backoff retry logic
     */
    private executeWithRetry;
    /**
     * Create MCF fulfillment order
     *
     * @param params Order creation parameters
     * @returns Created fulfillment order response
     */
    createFulfillmentOrder(params: CreateMCFOrderParams): Promise<MCFCreateFulfillmentOrderResponse>;
    /**
     * Get MCF fulfillment order details
     *
     * @param params Order retrieval parameters
     * @returns Fulfillment order details with shipments
     */
    getFulfillmentOrder(params: GetMCFOrderParams): Promise<MCFGetFulfillmentOrderResponse>;
    /**
     * Get package tracking details
     *
     * @param packageNumber Package number to track
     * @returns Package tracking details
     */
    getPackageTracking(packageNumber: number): Promise<MCFPackageTrackingDetails>;
    /**
     * Test connection to Amazon SP-API
     *
     * Useful for validating credentials and connectivity.
     */
    testConnection(): Promise<boolean>;
}
//# sourceMappingURL=amazon-mcf-client.d.ts.map