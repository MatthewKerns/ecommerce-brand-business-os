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

import axios, { type AxiosInstance, type AxiosError } from 'axios';
import crypto from 'crypto';
import type { TikTokShopConfig, RetryConfig } from '../types/config';
import type {
  TikTokOrder,
  TikTokOrderListParams,
  TikTokOrderListResponse,
  TikTokOrderDetailResponse,
  TikTokTrackingUpdate,
} from '../types/tiktok-order';
import {
  TikTokOrderListResponseSchema,
  TikTokOrderDetailResponseSchema,
} from '../types/tiktok-order';
import type {
  TikTokVideoMetrics,
  TikTokVideoListResponse,
  TikTokVideoMetricsParams,
  TikTokAccountAnalytics,
  TikTokAccountAnalyticsParams,
  TikTokProductAnalytics,
  TikTokProductAnalyticsParams,
} from '../types/tiktok-analytics';
import {
  TikTokVideoMetricsSchema,
  TikTokVideoListResponseSchema,
  TikTokAccountAnalyticsSchema,
  TikTokProductAnalyticsSchema,
} from '../types/tiktok-analytics';
import { ErrorCode } from '../types/common';

// ============================================================
// Types
// ============================================================

export interface TikTokShopClientConfig extends TikTokShopConfig {}

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

// ============================================================
// Constants
// ============================================================

const DEFAULT_RETRY_CONFIG: Required<RetryConfig> = {
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
const VIDEO_METRICS_ENDPOINT = '/analytics/202309/videos/metrics';
const ACCOUNT_ANALYTICS_ENDPOINT = '/analytics/202309/account/summary';
const PRODUCT_ANALYTICS_ENDPOINT = '/analytics/202309/products/metrics';

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
function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Generate TikTok Shop API signature
 *
 * TikTok uses HMAC-SHA256 for request signing:
 * 1. Concatenate: app_key + timestamp + path + query_string + body
 * 2. Generate HMAC-SHA256 with app_secret
 */
function generateSignature(
  appSecret: string,
  appKey: string,
  timestamp: number,
  path: string,
  queryString: string,
  body: string
): string {
  const input = `${appKey}${timestamp}${path}${queryString}${body}`;
  const hmac = crypto.createHmac('sha256', appSecret);
  hmac.update(input);
  return hmac.digest('hex');
}

/**
 * Build query string from parameters
 */
function buildQueryString(params: Record<string, unknown>): string {
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
function isRetryableError(error: AxiosError | TikTokShopError): boolean {
  if ('retryable' in error) {
    return error.retryable;
  }

  if (axios.isAxiosError(error)) {
    // Network errors are retryable
    if (!error.response) {
      return true;
    }

    // 5xx errors are retryable
    if (error.response.status >= 500) {
      return true;
    }

    // Check TikTok-specific error codes
    const data = error.response.data as TikTokApiResponse<unknown>;
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
function handleTikTokError(error: unknown): TikTokShopError {
  if (axios.isAxiosError(error)) {
    const response = error.response?.data as TikTokApiResponse<unknown>;

    // Authentication errors
    if (error.response?.status === 401 || error.response?.status === 403) {
      return {
        code: ErrorCode.AUTHENTICATION_FAILED,
        message: response?.message || 'Authentication failed',
        details: response,
        retryable: false,
      };
    }

    // Rate limit errors
    if (error.response?.status === 429 || response?.code === 1000002) {
      return {
        code: ErrorCode.RATE_LIMIT_EXCEEDED,
        message: 'Rate limit exceeded',
        details: response,
        retryable: true,
      };
    }

    // Network errors
    if (!error.response) {
      return {
        code: ErrorCode.NETWORK_ERROR,
        message: error.message || 'Network error occurred',
        details: error,
        retryable: true,
      };
    }

    // TikTok API errors
    return {
      code: ErrorCode.TIKTOK_API_ERROR,
      message: response?.message || error.message || 'TikTok API error',
      details: response,
      retryable: isRetryableError(error),
    };
  }

  // Unknown errors
  return {
    code: ErrorCode.UNKNOWN_ERROR,
    message: error instanceof Error ? error.message : 'Unknown error occurred',
    details: error,
    retryable: false,
  };
}

// ============================================================
// TikTok Shop Client Class
// ============================================================

export class TikTokShopClient {
  private readonly config: TikTokShopClientConfig;
  private readonly retryConfig: Required<RetryConfig>;
  private readonly httpClient: AxiosInstance;
  private accessToken: string;

  constructor(config: TikTokShopClientConfig, retryConfig: RetryConfig = {}) {
    this.config = config;
    this.retryConfig = { ...DEFAULT_RETRY_CONFIG, ...retryConfig };
    this.accessToken = config.accessToken;

    // Create axios instance with base configuration
    this.httpClient = axios.create({
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

      const signature = generateSignature(
        this.config.appSecret,
        this.config.appKey,
        timestamp,
        path,
        queryString,
        body
      );

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
  private async executeWithRetry<T>(
    operation: () => Promise<T>,
    operationName: string
  ): Promise<T> {
    let lastError: TikTokShopError | undefined;
    let delay = this.retryConfig.initialDelay;

    for (let attempt = 0; attempt <= this.retryConfig.maxRetries; attempt++) {
      try {
        return await operation();
      } catch (error) {
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
        delay = Math.min(
          delay * this.retryConfig.backoffMultiplier,
          this.retryConfig.maxDelay
        );
      }
    }

    // This should never be reached, but TypeScript needs it
    throw lastError || new Error(`${operationName} failed after retries`);
  }

  /**
   * Refresh OAuth2 access token
   */
  async refreshAccessToken(): Promise<void> {
    try {
      const timestamp = Math.floor(Date.now() / 1000);
      const queryString = buildQueryString({
        app_key: this.config.appKey,
        grant_type: 'refresh_token',
        refresh_token: this.config.refreshToken,
      });

      const signature = generateSignature(
        this.config.appSecret,
        this.config.appKey,
        timestamp,
        TOKEN_REFRESH_ENDPOINT,
        queryString,
        ''
      );

      const response = await axios.post<TikTokApiResponse<TikTokTokenResponse>>(
        `${this.config.apiBaseUrl}${TOKEN_REFRESH_ENDPOINT}`,
        null,
        {
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
        }
      );

      if (response.data.code !== 0) {
        throw new Error(`Token refresh failed: ${response.data.message}`);
      }

      this.accessToken = response.data.data.access_token;
    } catch (error) {
      throw handleTikTokError(error);
    }
  }

  /**
   * Get list of orders with optional filters
   */
  async getOrders(params: TikTokOrderListParams = {}): Promise<TikTokOrderListResponse> {
    return this.executeWithRetry(async () => {
      const requestParams: Record<string, unknown> = {
        shop_cipher: this.config.shopId,
      };

      if (params.create_time_from) requestParams.create_time_from = params.create_time_from;
      if (params.create_time_to) requestParams.create_time_to = params.create_time_to;
      if (params.update_time_from) requestParams.update_time_from = params.update_time_from;
      if (params.update_time_to) requestParams.update_time_to = params.update_time_to;
      if (params.order_status) {
        requestParams.order_status = Array.isArray(params.order_status)
          ? params.order_status
          : [params.order_status];
      }
      if (params.page_size) requestParams.page_size = params.page_size;
      if (params.page_token) requestParams.cursor = params.page_token;
      if (params.sort_by) requestParams.sort_by = params.sort_by;
      if (params.sort_order) requestParams.sort_type = params.sort_order === 'ASC' ? 1 : 2;

      const response = await this.httpClient.post<TikTokApiResponse<TikTokOrderListResponse>>(
        ORDERS_LIST_ENDPOINT,
        requestParams
      );

      if (response.data.code !== 0) {
        throw new Error(`Get orders failed: ${response.data.message}`);
      }

      // Validate response with Zod schema
      const validated = TikTokOrderListResponseSchema.parse(response.data.data);
      return validated;
    }, 'getOrders');
  }

  /**
   * Get detailed information for a specific order
   */
  async getOrderDetail(orderId: string): Promise<TikTokOrder> {
    return this.executeWithRetry(async () => {
      const endpoint = ORDER_DETAIL_ENDPOINT.replace('{order_id}', orderId);

      const response = await this.httpClient.get<TikTokApiResponse<TikTokOrderDetailResponse>>(
        endpoint,
        {
          params: {
            shop_cipher: this.config.shopId,
          },
        }
      );

      if (response.data.code !== 0) {
        throw new Error(`Get order detail failed: ${response.data.message}`);
      }

      // Validate response with Zod schema
      const validated = TikTokOrderDetailResponseSchema.parse(response.data.data);
      return validated.order;
    }, 'getOrderDetail');
  }

  /**
   * Update tracking information for an order package
   */
  async updateTrackingInfo(
    packageId: string,
    trackingInfo: TikTokTrackingUpdate
  ): Promise<UpdateTrackingResponse> {
    return this.executeWithRetry(async () => {
      const endpoint = UPDATE_TRACKING_ENDPOINT.replace('{package_id}', packageId);

      const requestBody = {
        tracking_number: trackingInfo.tracking_number,
        shipping_provider_id: trackingInfo.shipping_provider_id,
        shipping_provider_name: trackingInfo.shipping_provider_name,
      };

      const response = await this.httpClient.post<TikTokApiResponse<unknown>>(
        endpoint,
        requestBody
      );

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
  async testConnection(): Promise<boolean> {
    try {
      // Try to fetch orders with minimal parameters
      await this.getOrders({ page_size: 1 });
      return true;
    } catch (error) {
      return false;
    }
  }

  // ============================================================
  // Analytics Methods
  // ============================================================

  /**
   * Get video metrics for content analytics
   *
   * Fetches performance metrics for TikTok videos including views, engagement,
   * and shop clicks for marketing attribution.
   */
  async getVideoMetrics(
    params: TikTokVideoMetricsParams = {}
  ): Promise<TikTokVideoListResponse> {
    return this.executeWithRetry(async () => {
      const requestParams: Record<string, unknown> = {
        shop_cipher: this.config.shopId,
      };

      if (params.posted_from) requestParams.posted_from = params.posted_from;
      if (params.posted_to) requestParams.posted_to = params.posted_to;
      if (params.video_ids && params.video_ids.length > 0) {
        requestParams.video_ids = params.video_ids;
      }
      if (params.page_size) requestParams.page_size = params.page_size;
      if (params.cursor) requestParams.cursor = params.cursor;

      const response = await this.httpClient.post<TikTokApiResponse<TikTokVideoListResponse>>(
        VIDEO_METRICS_ENDPOINT,
        requestParams
      );

      if (response.data.code !== 0) {
        throw new Error(`Get video metrics failed: ${response.data.message}`);
      }

      // Add recorded_at timestamp to each video metric
      const recordedAt = Math.floor(Date.now() / 1000);
      const videosWithTimestamp = response.data.data.videos.map(video => ({
        ...video,
        recorded_at: video.recorded_at || recordedAt,
      }));

      // Validate response with Zod schema
      const validated = TikTokVideoListResponseSchema.parse({
        ...response.data.data,
        videos: videosWithTimestamp,
      });
      return validated;
    }, 'getVideoMetrics');
  }

  /**
   * Get account-level analytics summary
   *
   * Fetches aggregate analytics for the TikTok account over a date range,
   * including follower growth, total engagement, and commerce metrics.
   */
  async getAccountAnalytics(
    params: TikTokAccountAnalyticsParams
  ): Promise<TikTokAccountAnalytics> {
    return this.executeWithRetry(async () => {
      const requestParams = {
        shop_cipher: this.config.shopId,
        date_from: params.date_from,
        date_to: params.date_to,
      };

      const response = await this.httpClient.post<TikTokApiResponse<TikTokAccountAnalytics>>(
        ACCOUNT_ANALYTICS_ENDPOINT,
        requestParams
      );

      if (response.data.code !== 0) {
        throw new Error(`Get account analytics failed: ${response.data.message}`);
      }

      // Add recorded_at timestamp if not present
      const dataWithTimestamp = {
        ...response.data.data,
        recorded_at: response.data.data.recorded_at || Math.floor(Date.now() / 1000),
      };

      // Validate response with Zod schema
      const validated = TikTokAccountAnalyticsSchema.parse(dataWithTimestamp);
      return validated;
    }, 'getAccountAnalytics');
  }

  /**
   * Get product analytics for TikTok Shop
   *
   * Fetches performance metrics for specific products including views,
   * clicks, conversions, and revenue data.
   */
  async getProductAnalytics(
    params: TikTokProductAnalyticsParams
  ): Promise<TikTokProductAnalytics[]> {
    return this.executeWithRetry(async () => {
      const requestParams: Record<string, unknown> = {
        shop_cipher: this.config.shopId,
        date_from: params.date_from,
        date_to: params.date_to,
      };

      if (params.product_ids && params.product_ids.length > 0) {
        requestParams.product_ids = params.product_ids;
      }

      const response = await this.httpClient.post<
        TikTokApiResponse<{ products: TikTokProductAnalytics[] }>
      >(PRODUCT_ANALYTICS_ENDPOINT, requestParams);

      if (response.data.code !== 0) {
        throw new Error(`Get product analytics failed: ${response.data.message}`);
      }

      // Add recorded_at timestamp to each product metric if not present
      const recordedAt = Math.floor(Date.now() / 1000);
      const productsWithTimestamp = response.data.data.products.map(product => ({
        ...product,
        recorded_at: product.recorded_at || recordedAt,
      }));

      // Validate each product with Zod schema
      const validated = productsWithTimestamp.map(product =>
        TikTokProductAnalyticsSchema.parse(product)
      );
      return validated;
    }, 'getProductAnalytics');
  }
}
