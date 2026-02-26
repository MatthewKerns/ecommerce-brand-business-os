/**
 * Secrets Management Utilities
 *
 * Secure handling of sensitive credentials and tokens
 *
 * Features:
 * - OAuth token management and validation
 * - Secure credential loading from environment
 * - API key validation and masking
 * - Token refresh utilities
 * - Credential encryption/decryption helpers
 */

import { createCipheriv, createDecipheriv, randomBytes, pbkdf2Sync } from 'crypto';

// ============================================================
// Types
// ============================================================

export interface OAuthCredentials {
  clientId: string;
  clientSecret: string;
  refreshToken: string;
  accessToken?: string;
  expiresAt?: Date;
}

export interface APICredentials {
  apiKey: string;
  endpoint?: string;
  timeout?: number;
}

export interface EncryptionOptions {
  algorithm?: string;
  keyLength?: number;
  iterations?: number;
  salt?: Buffer;
}

export interface SecretValidationResult {
  isValid: boolean;
  errors: string[];
}

// ============================================================
// Constants
// ============================================================

const DEFAULT_ENCRYPTION_ALGORITHM = 'aes-256-gcm';
const DEFAULT_KEY_LENGTH = 32;
const DEFAULT_ITERATIONS = 100000;
const MIN_API_KEY_LENGTH = 20;
const MIN_TOKEN_LENGTH = 40;

// ============================================================
// OAuth Token Management
// ============================================================

/**
 * Load OAuth credentials from environment variables
 */
export function loadOAuthCredentials(prefix: string = 'GMAIL'): OAuthCredentials {
  const clientId = process.env[`${prefix}_CLIENT_ID`] || '';
  const clientSecret = process.env[`${prefix}_CLIENT_SECRET`] || '';
  const refreshToken = process.env[`${prefix}_REFRESH_TOKEN`] || '';
  const accessToken = process.env[`${prefix}_ACCESS_TOKEN`];

  return {
    clientId,
    clientSecret,
    refreshToken,
    accessToken,
    expiresAt: accessToken ? new Date(Date.now() + 3600 * 1000) : undefined,
  };
}

/**
 * Validate OAuth credentials
 */
export function validateOAuthCredentials(credentials: OAuthCredentials): SecretValidationResult {
  const errors: string[] = [];

  if (!credentials.clientId || credentials.clientId.length < 10) {
    errors.push('Client ID is missing or invalid');
  }

  if (!credentials.clientSecret || credentials.clientSecret.length < 10) {
    errors.push('Client secret is missing or invalid');
  }

  if (!credentials.refreshToken || credentials.refreshToken.length < MIN_TOKEN_LENGTH) {
    errors.push('Refresh token is missing or invalid');
  }

  return {
    isValid: errors.length === 0,
    errors,
  };
}

/**
 * Check if OAuth access token is expired
 */
export function isTokenExpired(credentials: OAuthCredentials): boolean {
  if (!credentials.expiresAt) {
    return true;
  }
  // Add 5-minute buffer to account for clock skew
  const bufferMs = 5 * 60 * 1000;
  return credentials.expiresAt.getTime() - bufferMs < Date.now();
}

/**
 * Mask sensitive token for logging
 */
export function maskToken(token: string, visibleChars: number = 4): string {
  if (token.length <= visibleChars * 2) {
    return '*'.repeat(token.length);
  }
  const start = token.substring(0, visibleChars);
  const end = token.substring(token.length - visibleChars);
  const masked = '*'.repeat(Math.max(8, token.length - visibleChars * 2));
  return `${start}${masked}${end}`;
}

// ============================================================
// API Key Management
// ============================================================

/**
 * Load API credentials from environment variables
 */
export function loadAPICredentials(prefix: string): APICredentials {
  const apiKey = process.env[`${prefix}_API_KEY`] || '';
  const endpoint = process.env[`${prefix}_ENDPOINT`];
  const timeoutStr = process.env[`${prefix}_TIMEOUT`];
  const timeout = timeoutStr ? parseInt(timeoutStr, 10) : undefined;

  return {
    apiKey,
    endpoint,
    timeout,
  };
}

/**
 * Validate API key format
 */
export function validateAPIKey(apiKey: string, minLength: number = MIN_API_KEY_LENGTH): SecretValidationResult {
  const errors: string[] = [];

  if (!apiKey) {
    errors.push('API key is missing');
  } else if (apiKey.length < minLength) {
    errors.push(`API key must be at least ${minLength} characters`);
  } else if (apiKey.includes(' ')) {
    errors.push('API key contains invalid whitespace');
  }

  return {
    isValid: errors.length === 0,
    errors,
  };
}

/**
 * Mask API key for logging
 */
export function maskAPIKey(apiKey: string): string {
  return maskToken(apiKey, 4);
}

// ============================================================
// Credential Encryption
// ============================================================

/**
 * Derive encryption key from password using PBKDF2
 */
export function deriveKey(
  password: string,
  salt: Buffer,
  options: EncryptionOptions = {}
): Buffer {
  const keyLength = options.keyLength || DEFAULT_KEY_LENGTH;
  const iterations = options.iterations || DEFAULT_ITERATIONS;

  return pbkdf2Sync(password, salt, iterations, keyLength, 'sha256');
}

/**
 * Encrypt sensitive data
 */
export function encryptSecret(
  data: string,
  password: string,
  options: EncryptionOptions = {}
): string {
  const algorithm = options.algorithm || DEFAULT_ENCRYPTION_ALGORITHM;
  const salt = options.salt || randomBytes(16);
  const iv = randomBytes(16);
  const key = deriveKey(password, salt, options);

  const cipher = createCipheriv(algorithm, key, iv);
  let encrypted = cipher.update(data, 'utf8', 'hex');
  encrypted += cipher.final('hex');

  // Get auth tag for GCM mode
  const authTag = (cipher as any).getAuthTag();

  // Combine salt + iv + authTag + encrypted
  return Buffer.concat([
    salt,
    iv,
    authTag,
    Buffer.from(encrypted, 'hex'),
  ]).toString('base64');
}

/**
 * Decrypt sensitive data
 */
export function decryptSecret(
  encryptedData: string,
  password: string,
  options: EncryptionOptions = {}
): string {
  const algorithm = options.algorithm || DEFAULT_ENCRYPTION_ALGORITHM;
  const buffer = Buffer.from(encryptedData, 'base64');

  // Extract components
  const salt = buffer.subarray(0, 16);
  const iv = buffer.subarray(16, 32);
  const authTag = buffer.subarray(32, 48);
  const encrypted = buffer.subarray(48);

  const key = deriveKey(password, salt, options);

  const decipher = createDecipheriv(algorithm, key, iv);
  (decipher as any).setAuthTag(authTag);

  let decrypted = decipher.update(encrypted);
  decrypted = Buffer.concat([decrypted, decipher.final()]);

  return decrypted.toString('utf8');
}

// ============================================================
// Environment Variable Helpers
// ============================================================

/**
 * Get required environment variable or throw error
 */
export function getRequiredEnv(key: string): string {
  const value = process.env[key];
  if (!value) {
    throw new Error(`Required environment variable ${key} is not set`);
  }
  return value;
}

/**
 * Get optional environment variable with default
 */
export function getOptionalEnv(key: string, defaultValue: string = ''): string {
  return process.env[key] || defaultValue;
}

/**
 * Load secret from environment or file path
 */
export function loadSecret(key: string, isFilePath: boolean = false): string {
  const value = getRequiredEnv(key);

  if (isFilePath) {
    try {
      const fs = require('fs');
      return fs.readFileSync(value, 'utf8').trim();
    } catch (error: any) {
      throw new Error(`Failed to load secret from file ${value}: ${error.message}`);
    }
  }

  return value;
}

/**
 * Check if running in production environment
 */
export function isProduction(): boolean {
  const env = process.env.NODE_ENV || process.env.ENVIRONMENT || 'development';
  return env === 'production';
}

/**
 * Validate all required secrets are present
 */
export function validateRequiredSecrets(requiredKeys: string[]): SecretValidationResult {
  const errors: string[] = [];

  for (const key of requiredKeys) {
    if (!process.env[key]) {
      errors.push(`Missing required secret: ${key}`);
    }
  }

  return {
    isValid: errors.length === 0,
    errors,
  };
}

// ============================================================
// Utility Functions
// ============================================================

/**
 * Generate a random encryption key
 */
export function generateEncryptionKey(length: number = 32): string {
  return randomBytes(length).toString('hex');
}

/**
 * Securely compare two strings (timing-safe)
 */
export function secureCompare(a: string, b: string): boolean {
  if (a.length !== b.length) {
    return false;
  }

  let result = 0;
  for (let i = 0; i < a.length; i++) {
    result |= a.charCodeAt(i) ^ b.charCodeAt(i);
  }

  return result === 0;
}

/**
 * Sanitize secret for logging (removes sensitive data)
 */
export function sanitizeForLogging(obj: Record<string, any>): Record<string, any> {
  const sensitiveKeys = [
    'password',
    'secret',
    'token',
    'key',
    'apikey',
    'api_key',
    'clientsecret',
    'client_secret',
    'privatekey',
    'private_key',
  ];

  const sanitized: Record<string, any> = {};

  for (const [key, value] of Object.entries(obj)) {
    const lowerKey = key.toLowerCase();
    const isSensitive = sensitiveKeys.some(sensitive => lowerKey.includes(sensitive));

    if (isSensitive && typeof value === 'string') {
      sanitized[key] = maskToken(value);
    } else if (typeof value === 'object' && value !== null && !Array.isArray(value)) {
      sanitized[key] = sanitizeForLogging(value);
    } else {
      sanitized[key] = value;
    }
  }

  return sanitized;
}
