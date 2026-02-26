/**
 * Configuration Loader
 *
 * Loads MCF Connector configuration from environment variables
 */

import * as dotenv from 'dotenv';
import type { MCFConnectorConfig } from './types/config';

dotenv.config();

/**
 * Load MCF Connector configuration from environment variables
 */
export function loadConfig(): MCFConnectorConfig {
  // TikTok Shop Configuration
  const tiktokAppKey = process.env.TIKTOK_APP_KEY;
  const tiktokAppSecret = process.env.TIKTOK_APP_SECRET;
  const tiktokShopId = process.env.TIKTOK_SHOP_ID;
  const tiktokAccessToken = process.env.TIKTOK_ACCESS_TOKEN;
  const tiktokRefreshToken = process.env.TIKTOK_REFRESH_TOKEN;

  if (!tiktokAppKey) throw new Error('Missing required env var: TIKTOK_APP_KEY');
  if (!tiktokAppSecret) throw new Error('Missing required env var: TIKTOK_APP_SECRET');
  if (!tiktokShopId) throw new Error('Missing required env var: TIKTOK_SHOP_ID');
  if (!tiktokAccessToken) throw new Error('Missing required env var: TIKTOK_ACCESS_TOKEN');
  if (!tiktokRefreshToken) throw new Error('Missing required env var: TIKTOK_REFRESH_TOKEN');

  // Amazon MCF Configuration
  const amazonClientId = process.env.AMAZON_CLIENT_ID;
  const amazonClientSecret = process.env.AMAZON_CLIENT_SECRET;
  const amazonRefreshToken = process.env.AMAZON_REFRESH_TOKEN;
  const amazonMarketplaceId = process.env.AMAZON_MARKETPLACE_ID;
  const amazonSellerId = process.env.AMAZON_SELLER_ID;
  const amazonAwsAccessKey = process.env.AMAZON_AWS_ACCESS_KEY;
  const amazonAwsSecretKey = process.env.AMAZON_AWS_SECRET_KEY;

  if (!amazonClientId) throw new Error('Missing required env var: AMAZON_CLIENT_ID');
  if (!amazonClientSecret) throw new Error('Missing required env var: AMAZON_CLIENT_SECRET');
  if (!amazonRefreshToken) throw new Error('Missing required env var: AMAZON_REFRESH_TOKEN');
  if (!amazonMarketplaceId) throw new Error('Missing required env var: AMAZON_MARKETPLACE_ID');
  if (!amazonSellerId) throw new Error('Missing required env var: AMAZON_SELLER_ID');
  if (!amazonAwsAccessKey) throw new Error('Missing required env var: AMAZON_AWS_ACCESS_KEY');
  if (!amazonAwsSecretKey) throw new Error('Missing required env var: AMAZON_AWS_SECRET_KEY');

  return {
    tiktok: {
      appKey: tiktokAppKey,
      appSecret: tiktokAppSecret,
      shopId: tiktokShopId,
      apiBaseUrl: process.env.TIKTOK_API_BASE_URL || 'https://open-api.tiktokglobalshop.com',
      accessToken: tiktokAccessToken,
      refreshToken: tiktokRefreshToken,
    },
    amazon: {
      clientId: amazonClientId,
      clientSecret: amazonClientSecret,
      refreshToken: amazonRefreshToken,
      marketplaceId: amazonMarketplaceId,
      sellerId: amazonSellerId,
      awsAccessKey: amazonAwsAccessKey,
      awsSecretKey: amazonAwsSecretKey,
      region: process.env.AMAZON_REGION || 'us-east-1',
      apiBaseUrl: process.env.AMAZON_API_BASE_URL || 'https://sellingpartnerapi-na.amazon.com',
    },
    connector: {
      orderPollIntervalMinutes: parseInt(process.env.ORDER_POLL_INTERVAL_MINUTES || '5', 10),
      trackingSyncIntervalMinutes: parseInt(process.env.TRACKING_SYNC_INTERVAL_MINUTES || '30', 10),
      inventorySyncIntervalMinutes: parseInt(process.env.INVENTORY_SYNC_INTERVAL_MINUTES || '60', 10),
      retry: {
        maxRetries: parseInt(process.env.MAX_RETRY_ATTEMPTS || '3', 10),
        initialDelay: parseInt(process.env.RETRY_BACKOFF_MS || '1000', 10),
        backoffMultiplier: 2,
        maxDelay: 30000,
      },
      enableWebhookNotifications: process.env.ENABLE_WEBHOOK_NOTIFICATIONS === 'true',
      webhookUrl: process.env.WEBHOOK_URL,
      logLevel: (process.env.LOG_LEVEL as 'debug' | 'info' | 'warn' | 'error') || 'info',
    },
    database: {
      url: process.env.DATABASE_URL,
      enabled: !!process.env.DATABASE_URL,
    },
    environment: (process.env.NODE_ENV as 'development' | 'staging' | 'production') || 'development',
  };
}
