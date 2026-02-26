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

import axios, { type AxiosInstance, type AxiosError } from 'axios';
import crypto from 'crypto';
import type { AmazonMCFConfig, RetryConfig } from '../types/config';
import type {
  MCFFulfillmentOrderRequest,
  MCFCreateFulfillmentOrderResponse,
  MCFGetFulfillmentOrderResponse,
  MCFPackageTrackingDetails,
  CreateMCFOrderParams,
  GetMCFOrderParams,
} from '../types/mcf-order';
import {
  MCFCreateFulfillmentOrderResponseSchema,
  MCFGetFulfillmentOrderResponseSchema,
  MCFPackageTrackingDetailsSchema,
} from '../types/mcf-order';
import { ErrorCode } from '../types/common';

// ============================================================
// Types
// ============================================================

export interface AmazonMCFClientConfig extends AmazonMCFConfig {}

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

// ============================================================
// Constants
// ============================================================

const DEFAULT_RETRY_CONFIG: Required<RetryConfig> = {
  maxRetries: 3,
  initialDelay: 1000,
  backoffMultiplier: 2,
  maxDelay: 30000,
};

// LWA (Login with Amazon) OAuth endpoints
const LWA_TOKEN_URL = 'https://api.amazon.com/auth/o2/token';

// SP-API endpoints (US region)
const SP_API_ENDPOINTS = {
  'na': 'https://sellingpartnerapi-na.amazon.com',
  'eu': 'https://sellingpartnerapi-eu.amazon.com',
  'fe': 'https://sellingpartnerapi-fe.amazon.com',
} as const;

// API paths
const CREATE_FULFILLMENT_ORDER_PATH = '/fba/outbound/2020-07-01/fulfillmentOrders';
const GET_FULFILLMENT_ORDER_PATH = '/fba/outbound/2020-07-01/fulfillmentOrders';
const GET_PACKAGE_TRACKING_PATH = '/fba/outbound/2020-07-01/tracking';

// AWS service name for SP-API
const AWS_SERVICE = 'execute-api';

// Retryable HTTP status codes
const RETRYABLE_STATUS_CODES = [429, 500, 502, 503, 504];

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
 * Generate AWS Signature Version 4
 *
 * AWS Signature v4 signing process:
 * 1. Create canonical request
 * 2. Create string to sign
 * 3. Calculate signing key
 * 4. Calculate signature
 */
function generateAWSSignature(
  params: AWSSignatureParams,
  credentials: {
    accessKeyId: string;
    secretAccessKey: string;
    region: string;
  }
): string {
  const { method, path, queryString, headers, body, timestamp } = params;
  const date = timestamp.split('T')[0];

  // Step 1: Create canonical request
  const canonicalHeaders = Object.keys(headers)
    .sort()
    .map(key => `${key.toLowerCase()}:${headers[key].trim()}`)
    .join('\n');

  const signedHeaders = Object.keys(headers)
    .sort()
    .map(key => key.toLowerCase())
    .join(';');

  const payloadHash = crypto.createHash('sha256').update(body).digest('hex');

  const canonicalRequest = [
    method,
    path,
    queryString,
    canonicalHeaders + '\n',
    signedHeaders,
    payloadHash,
  ].join('\n');

  // Step 2: Create string to sign
  const credentialScope = `${date}/${credentials.region}/${AWS_SERVICE}/aws4_request`;
  const canonicalRequestHash = crypto.createHash('sha256').update(canonicalRequest).digest('hex');

  const stringToSign = [
    'AWS4-HMAC-SHA256',
    timestamp,
    credentialScope,
    canonicalRequestHash,
  ].join('\n');

  // Step 3: Calculate signing key
  const kDate = crypto.createHmac('sha256', `AWS4${credentials.secretAccessKey}`).update(date).digest();
  const kRegion = crypto.createHmac('sha256', kDate).update(credentials.region).digest();
  const kService = crypto.createHmac('sha256', kRegion).update(AWS_SERVICE).digest();
  const kSigning = crypto.createHmac('sha256', kService).update('aws4_request').digest();

  // Step 4: Calculate signature
  const signature = crypto.createHmac('sha256', kSigning).update(stringToSign).digest('hex');

  return signature;
}

/**
 * Build AWS authorization header
 */
function buildAuthorizationHeader(
  params: AWSSignatureParams,
  credentials: {
    accessKeyId: string;
    secretAccessKey: string;
    region: string;
  }
): string {
  const signature = generateAWSSignature(params, credentials);
  const date = params.timestamp.split('T')[0];
  const credentialScope = `${date}/${credentials.region}/${AWS_SERVICE}/aws4_request`;

  const signedHeaders = Object.keys(params.headers)
    .sort()
    .map(key => key.toLowerCase())
    .join(';');

  return `AWS4-HMAC-SHA256 Credential=${credentials.accessKeyId}/${credentialScope}, SignedHeaders=${signedHeaders}, Signature=${signature}`;
}

/**
 * Check if error is retryable
 */
function isRetryableError(error: AxiosError | AmazonApiError): boolean {
  if ('retryable' in error) {
    return error.retryable;
  }

  if (axios.isAxiosError(error)) {
    // Network errors are retryable
    if (!error.response) {
      return true;
    }

    // Check for retryable status codes
    if (error.response.status && RETRYABLE_STATUS_CODES.includes(error.response.status)) {
      return true;
    }
  }

  return false;
}

/**
 * Handle Amazon API errors
 */
function handleAmazonError(error: AxiosError): AmazonApiError {
  if (!error.response) {
    return {
      code: ErrorCode.NETWORK_ERROR,
      message: 'Network error occurred',
      details: error.message,
      retryable: true,
    };
  }

  const status = error.response.status;
  const data = error.response.data as { errors?: Array<{ code: string; message: string }> };

  if (status === 429) {
    return {
      code: ErrorCode.RATE_LIMIT_EXCEEDED,
      message: 'Rate limit exceeded',
      details: data,
      retryable: true,
    };
  }

  if (status === 401 || status === 403) {
    return {
      code: ErrorCode.AUTHENTICATION_FAILED,
      message: 'Authentication failed',
      details: data,
      retryable: false,
    };
  }

  if (RETRYABLE_STATUS_CODES.includes(status)) {
    return {
      code: ErrorCode.AMAZON_API_ERROR,
      message: data.errors?.[0]?.message || 'Amazon API error',
      details: data,
      retryable: true,
    };
  }

  return {
    code: ErrorCode.AMAZON_API_ERROR,
    message: data.errors?.[0]?.message || 'Amazon API error',
    details: data,
    retryable: false,
  };
}

// ============================================================
// Amazon MCF Client Class
// ============================================================

export class AmazonMCFClient {
  private readonly config: AmazonMCFClientConfig;
  private readonly retryConfig: Required<RetryConfig>;
  private readonly httpClient: AxiosInstance;
  private readonly endpoint: string;
  private accessToken: string | null = null;
  private tokenExpiresAt: number = 0;

  constructor(config: AmazonMCFClientConfig, retryConfig: RetryConfig = {}) {
    this.config = config;
    this.retryConfig = { ...DEFAULT_RETRY_CONFIG, ...retryConfig };
    this.endpoint = SP_API_ENDPOINTS[config.region] || SP_API_ENDPOINTS['na'];

    this.httpClient = axios.create({
      baseURL: this.endpoint,
      timeout: 30000,
    });

    // Add request interceptor for authentication and signing
    this.httpClient.interceptors.request.use(async config => {
      // Ensure we have a valid access token
      await this.ensureValidToken();

      // Add LWA access token
      config.headers['x-amz-access-token'] = this.accessToken!;

      // Prepare for AWS signing
      const timestamp = new Date().toISOString().replace(/\.\d{3}Z$/, 'Z');
      const host = new URL(this.endpoint).host;

      config.headers['host'] = host;
      config.headers['x-amz-date'] = timestamp;
      config.headers['content-type'] = 'application/json';

      // Build signing parameters
      const method = (config.method || 'GET').toUpperCase();
      const path = config.url || '/';
      const queryString = config.params
        ? Object.entries(config.params)
            .sort(([keyA], [keyB]) => keyA.localeCompare(keyB))
            .map(([key, value]) => `${encodeURIComponent(key)}=${encodeURIComponent(String(value))}`)
            .join('&')
        : '';
      const body = config.data ? JSON.stringify(config.data) : '';

      const signatureParams: AWSSignatureParams = {
        method,
        path,
        queryString,
        headers: config.headers as Record<string, string>,
        body,
        timestamp,
      };

      // Generate and add authorization header
      const authHeader = buildAuthorizationHeader(signatureParams, {
        accessKeyId: this.config.awsAccessKey,
        secretAccessKey: this.config.awsSecretKey,
        region: this.config.region,
      });

      config.headers['Authorization'] = authHeader;

      return config;
    });
  }

  /**
   * Ensure we have a valid LWA access token
   */
  private async ensureValidToken(): Promise<void> {
    const now = Date.now();

    // Refresh if token doesn't exist or expires in less than 5 minutes
    if (!this.accessToken || now >= this.tokenExpiresAt - 5 * 60 * 1000) {
      await this.refreshAccessToken();
    }
  }

  /**
   * Refresh LWA access token
   */
  public async refreshAccessToken(): Promise<void> {
    try {
      const response = await axios.post<LWATokenResponse>(
        LWA_TOKEN_URL,
        new URLSearchParams({
          grant_type: 'refresh_token',
          refresh_token: this.config.refreshToken,
          client_id: this.config.clientId,
          client_secret: this.config.clientSecret,
        }),
        {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
        }
      );

      this.accessToken = response.data.access_token;
      this.tokenExpiresAt = Date.now() + response.data.expires_in * 1000;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw new Error(`Failed to refresh LWA token: ${error.message}`);
      }
      throw error;
    }
  }

  /**
   * Execute API call with exponential backoff retry logic
   */
  private async executeWithRetry<T>(
    operation: () => Promise<T>,
    operationName: string
  ): Promise<T> {
    let lastError: Error | null = null;
    let delay = this.retryConfig.initialDelay;

    for (let attempt = 0; attempt <= this.retryConfig.maxRetries; attempt++) {
      try {
        return await operation();
      } catch (error) {
        lastError = error as Error;

        // Check if we should retry
        const shouldRetry =
          attempt < this.retryConfig.maxRetries &&
          (axios.isAxiosError(error) ? isRetryableError(error) : false);

        if (!shouldRetry) {
          // Convert to AmazonApiError if it's an Axios error
          if (axios.isAxiosError(error)) {
            const apiError = handleAmazonError(error);
            throw new Error(`${operationName} failed: ${apiError.message}`);
          }
          throw error;
        }

        // Wait before retrying
        await sleep(delay);

        // Increase delay for next retry
        delay = Math.min(delay * this.retryConfig.backoffMultiplier, this.retryConfig.maxDelay);
      }
    }

    throw new Error(`${operationName} failed after ${this.retryConfig.maxRetries} retries: ${lastError?.message}`);
  }

  /**
   * Create MCF fulfillment order
   *
   * @param params Order creation parameters
   * @returns Created fulfillment order response
   */
  public async createFulfillmentOrder(
    params: CreateMCFOrderParams
  ): Promise<MCFCreateFulfillmentOrderResponse> {
    return this.executeWithRetry(async () => {
      // Transform params to MCF API format
      const request: MCFFulfillmentOrderRequest = {
        marketplaceId: this.config.marketplaceId,
        sellerFulfillmentOrderId: params.orderId,
        displayableOrderId: params.displayableOrderId,
        displayableOrderDate: params.orderDate.toISOString(),
        displayableOrderComment: params.orderComment,
        shippingSpeedCategory: params.shippingSpeed,
        destinationAddress: params.destinationAddress,
        fulfillmentPolicy: params.fulfillmentPolicy,
        deliveryWindow: params.deliveryWindow
          ? {
              startDate: params.deliveryWindow.startDate.toISOString(),
              endDate: params.deliveryWindow.endDate.toISOString(),
            }
          : undefined,
        notificationEmails: params.notificationEmails,
        items: params.items.map(item => ({
          sellerSku: item.sku,
          sellerFulfillmentOrderItemId: item.itemId,
          quantity: item.quantity,
          perUnitDeclaredValue: item.declaredValue
            ? {
                currencyCode: item.declaredValue.currency,
                value: item.declaredValue.amount,
              }
            : undefined,
          perUnitPrice: item.price
            ? {
                currencyCode: item.price.currency,
                value: item.price.amount,
              }
            : undefined,
          perUnitTax: item.tax
            ? {
                currencyCode: item.tax.currency,
                value: item.tax.amount,
              }
            : undefined,
        })),
        fulfillmentAction: undefined,
        codSettings: undefined,
      };

      const response = await this.httpClient.post<MCFCreateFulfillmentOrderResponse>(
        CREATE_FULFILLMENT_ORDER_PATH,
        request
      );

      // Validate response with Zod schema
      const validatedResponse = MCFCreateFulfillmentOrderResponseSchema.parse(response.data);

      return validatedResponse;
    }, 'createFulfillmentOrder');
  }

  /**
   * Get MCF fulfillment order details
   *
   * @param params Order retrieval parameters
   * @returns Fulfillment order details with shipments
   */
  public async getFulfillmentOrder(
    params: GetMCFOrderParams
  ): Promise<MCFGetFulfillmentOrderResponse> {
    return this.executeWithRetry(async () => {
      const path = `${GET_FULFILLMENT_ORDER_PATH}/${params.sellerFulfillmentOrderId}`;

      const response = await this.httpClient.get<MCFGetFulfillmentOrderResponse>(path);

      // Validate response with Zod schema
      const validatedResponse = MCFGetFulfillmentOrderResponseSchema.parse(response.data);

      return validatedResponse;
    }, 'getFulfillmentOrder');
  }

  /**
   * Get package tracking details
   *
   * @param packageNumber Package number to track
   * @returns Package tracking details
   */
  public async getPackageTracking(packageNumber: number): Promise<MCFPackageTrackingDetails> {
    return this.executeWithRetry(async () => {
      const response = await this.httpClient.get<MCFPackageTrackingDetails>(
        GET_PACKAGE_TRACKING_PATH,
        {
          params: {
            packageNumber,
          },
        }
      );

      // Validate response with Zod schema
      const validatedResponse = MCFPackageTrackingDetailsSchema.parse(response.data);

      return validatedResponse;
    }, 'getPackageTracking');
  }

  /**
   * Test connection to Amazon SP-API
   *
   * Useful for validating credentials and connectivity.
   */
  public async testConnection(): Promise<boolean> {
    try {
      await this.refreshAccessToken();
      return true;
    } catch (error) {
      return false;
    }
  }
}
