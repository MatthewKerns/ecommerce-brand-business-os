"use strict";
/**
 * Configuration Loader
 *
 * Loads MCF Connector configuration from environment variables
 */
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.loadConfig = loadConfig;
const dotenv = __importStar(require("dotenv"));
dotenv.config();
/**
 * Load MCF Connector configuration from environment variables
 */
function loadConfig() {
    // TikTok Shop Configuration
    const tiktokAppKey = process.env.TIKTOK_APP_KEY;
    const tiktokAppSecret = process.env.TIKTOK_APP_SECRET;
    const tiktokShopId = process.env.TIKTOK_SHOP_ID;
    const tiktokAccessToken = process.env.TIKTOK_ACCESS_TOKEN;
    const tiktokRefreshToken = process.env.TIKTOK_REFRESH_TOKEN;
    if (!tiktokAppKey)
        throw new Error('Missing required env var: TIKTOK_APP_KEY');
    if (!tiktokAppSecret)
        throw new Error('Missing required env var: TIKTOK_APP_SECRET');
    if (!tiktokShopId)
        throw new Error('Missing required env var: TIKTOK_SHOP_ID');
    if (!tiktokAccessToken)
        throw new Error('Missing required env var: TIKTOK_ACCESS_TOKEN');
    if (!tiktokRefreshToken)
        throw new Error('Missing required env var: TIKTOK_REFRESH_TOKEN');
    // Amazon MCF Configuration
    const amazonClientId = process.env.AMAZON_CLIENT_ID;
    const amazonClientSecret = process.env.AMAZON_CLIENT_SECRET;
    const amazonRefreshToken = process.env.AMAZON_REFRESH_TOKEN;
    const amazonMarketplaceId = process.env.AMAZON_MARKETPLACE_ID;
    const amazonSellerId = process.env.AMAZON_SELLER_ID;
    const amazonAwsAccessKey = process.env.AMAZON_AWS_ACCESS_KEY;
    const amazonAwsSecretKey = process.env.AMAZON_AWS_SECRET_KEY;
    if (!amazonClientId)
        throw new Error('Missing required env var: AMAZON_CLIENT_ID');
    if (!amazonClientSecret)
        throw new Error('Missing required env var: AMAZON_CLIENT_SECRET');
    if (!amazonRefreshToken)
        throw new Error('Missing required env var: AMAZON_REFRESH_TOKEN');
    if (!amazonMarketplaceId)
        throw new Error('Missing required env var: AMAZON_MARKETPLACE_ID');
    if (!amazonSellerId)
        throw new Error('Missing required env var: AMAZON_SELLER_ID');
    if (!amazonAwsAccessKey)
        throw new Error('Missing required env var: AMAZON_AWS_ACCESS_KEY');
    if (!amazonAwsSecretKey)
        throw new Error('Missing required env var: AMAZON_AWS_SECRET_KEY');
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
            logLevel: process.env.LOG_LEVEL || 'info',
        },
        database: {
            url: process.env.DATABASE_URL,
            enabled: !!process.env.DATABASE_URL,
        },
        environment: process.env.NODE_ENV || 'development',
    };
}
//# sourceMappingURL=config.js.map