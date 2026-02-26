/**
 * Configuration Types for MCF Connector
 *
 * Defines all configuration interfaces for:
 * - TikTok Shop API integration
 * - Amazon MCF (Multi-Channel Fulfillment) API integration
 * - Connector behavior and retry logic
 */
export interface TikTokShopConfig {
    /**
     * TikTok App Key (from TikTok Developer Portal)
     */
    appKey: string;
    /**
     * TikTok App Secret (from TikTok Developer Portal)
     */
    appSecret: string;
    /**
     * TikTok Shop ID
     */
    shopId: string;
    /**
     * TikTok API base URL
     * @default 'https://open-api.tiktokglobalshop.com'
     */
    apiBaseUrl: string;
    /**
     * OAuth2 Access Token for API authentication
     */
    accessToken: string;
    /**
     * OAuth2 Refresh Token for token renewal
     */
    refreshToken: string;
}
export interface AmazonMCFConfig {
    /**
     * Amazon LWA (Login with Amazon) Client ID
     */
    clientId: string;
    /**
     * Amazon LWA Client Secret
     */
    clientSecret: string;
    /**
     * OAuth2 Refresh Token for SP-API access
     */
    refreshToken: string;
    /**
     * Amazon Marketplace ID (e.g., ATVPDKIKX0DER for US)
     */
    marketplaceId: string;
    /**
     * Amazon Seller ID
     */
    sellerId: string;
    /**
     * AWS Access Key for AWS Signature v4 signing
     */
    awsAccessKey: string;
    /**
     * AWS Secret Key for AWS Signature v4 signing
     */
    awsSecretKey: string;
    /**
     * AWS Region for API endpoints
     * @default 'us-east-1'
     */
    region: string;
    /**
     * Amazon SP-API base URL
     * @default 'https://sellingpartnerapi-na.amazon.com'
     */
    apiBaseUrl: string;
}
export interface RetryConfig {
    /**
     * Maximum number of retry attempts
     * @default 3
     */
    maxRetries?: number;
    /**
     * Initial delay in milliseconds before first retry
     * @default 1000
     */
    initialDelay?: number;
    /**
     * Backoff multiplier for exponential backoff
     * @default 2
     */
    backoffMultiplier?: number;
    /**
     * Maximum delay in milliseconds between retries
     * @default 30000
     */
    maxDelay?: number;
}
export interface ConnectorConfig {
    /**
     * Interval in minutes to poll TikTok Shop for new orders
     * @default 5
     */
    orderPollIntervalMinutes: number;
    /**
     * Interval in minutes to sync tracking numbers from MCF to TikTok
     * @default 30
     */
    trackingSyncIntervalMinutes: number;
    /**
     * Interval in minutes to sync inventory from Amazon
     * @default 60
     */
    inventorySyncIntervalMinutes: number;
    /**
     * Retry configuration for API calls
     */
    retry: RetryConfig;
    /**
     * Enable webhook notifications for order events
     * @default false
     */
    enableWebhookNotifications?: boolean;
    /**
     * Webhook URL for order event notifications
     */
    webhookUrl?: string;
    /**
     * Log level (debug, info, warn, error)
     * @default 'info'
     */
    logLevel?: 'debug' | 'info' | 'warn' | 'error';
}
export interface DatabaseConfig {
    /**
     * Database connection URL
     * Format: postgresql://user:pass@host:port/database
     */
    url?: string;
    /**
     * Enable database persistence for order state tracking
     * @default false
     */
    enabled: boolean;
}
export interface MCFConnectorConfig {
    /**
     * TikTok Shop API configuration
     */
    tiktok: TikTokShopConfig;
    /**
     * Amazon MCF API configuration
     */
    amazon: AmazonMCFConfig;
    /**
     * Connector behavior configuration
     */
    connector: ConnectorConfig;
    /**
     * Database configuration (optional)
     */
    database?: DatabaseConfig;
    /**
     * Environment (development, staging, production)
     * @default 'development'
     */
    environment?: 'development' | 'staging' | 'production';
}
//# sourceMappingURL=config.d.ts.map