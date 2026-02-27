/**
 * HMAC Utilities - Cryptographic signing for email tracking
 *
 * Features:
 * - HMAC-SHA256 signing for tracking URLs
 * - Signature verification to prevent tampering
 * - Time-based expiration support
 * - URL-safe base64 encoding
 */

import { createHmac, timingSafeEqual } from 'crypto';

// ============================================================
// Types
// ============================================================

export interface SignedData {
  data: string;
  signature: string;
  timestamp?: number;
}

export interface VerificationResult {
  valid: boolean;
  expired: boolean;
  data?: any;
  error?: string;
}

export interface HmacConfig {
  secret: string;
  algorithm?: 'sha256' | 'sha512';
  expirationSeconds?: number;
}

// ============================================================
// Constants
// ============================================================

const DEFAULT_ALGORITHM = 'sha256';
const DEFAULT_EXPIRATION_SECONDS = 30 * 24 * 60 * 60; // 30 days

// ============================================================
// Helper Functions
// ============================================================

/**
 * Convert string to URL-safe base64
 */
function toBase64Url(str: string): string {
  return Buffer.from(str)
    .toString('base64')
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=+$/, '');
}

/**
 * Convert URL-safe base64 to string
 */
function fromBase64Url(base64Url: string): string {
  const base64 = base64Url
    .replace(/-/g, '+')
    .replace(/_/g, '/');
  return Buffer.from(base64, 'base64').toString('utf-8');
}

/**
 * Get current Unix timestamp in seconds
 */
function getCurrentTimestamp(): number {
  return Math.floor(Date.now() / 1000);
}

// ============================================================
// HMAC Service Class
// ============================================================

export class HmacService {
  private readonly config: Required<HmacConfig>;

  constructor(config: HmacConfig) {
    if (!config.secret) {
      throw new Error('HMAC secret is required');
    }
    this.config = {
      secret: config.secret,
      algorithm: config.algorithm || DEFAULT_ALGORITHM,
      expirationSeconds: config.expirationSeconds ?? DEFAULT_EXPIRATION_SECONDS,
    };
  }

  /**
   * Generate HMAC signature for data
   */
  private generateSignature(data: string): string {
    const hmac = createHmac(this.config.algorithm, this.config.secret);
    hmac.update(data);
    return hmac.digest('hex');
  }

  /**
   * Sign data with HMAC and optional timestamp
   */
  sign(data: Record<string, any>, includeTimestamp: boolean = true): SignedData {
    const payload = includeTimestamp
      ? { ...data, _ts: getCurrentTimestamp() }
      : data;

    const dataString = JSON.stringify(payload);
    const signature = this.generateSignature(dataString);

    return {
      data: toBase64Url(dataString),
      signature,
      timestamp: includeTimestamp ? payload._ts : undefined,
    };
  }

  /**
   * Verify HMAC signature and check expiration
   */
  verify(signedData: SignedData): VerificationResult {
    try {
      // Decode data
      const dataString = fromBase64Url(signedData.data);
      const payload = JSON.parse(dataString);

      // Verify signature
      const expectedSignature = this.generateSignature(dataString);
      const signatureBuffer = Buffer.from(signedData.signature, 'hex');
      const expectedBuffer = Buffer.from(expectedSignature, 'hex');

      if (signatureBuffer.length !== expectedBuffer.length) {
        return {
          valid: false,
          expired: false,
          error: 'Invalid signature length',
        };
      }

      const isValid = timingSafeEqual(signatureBuffer, expectedBuffer);

      if (!isValid) {
        return {
          valid: false,
          expired: false,
          error: 'Invalid signature',
        };
      }

      // Check expiration if timestamp exists
      let expired = false;
      if (payload._ts) {
        const currentTimestamp = getCurrentTimestamp();
        const age = currentTimestamp - payload._ts;
        expired = age > this.config.expirationSeconds;
      }

      // Remove internal timestamp from returned data
      if (payload._ts) {
        delete payload._ts;
      }

      return {
        valid: true,
        expired,
        data: payload,
      };
    } catch (error: any) {
      return {
        valid: false,
        expired: false,
        error: error.message || 'Verification failed',
      };
    }
  }

  /**
   * Create a signed token string (data and signature combined)
   */
  createToken(data: Record<string, any>, includeTimestamp: boolean = true): string {
    const signed = this.sign(data, includeTimestamp);
    return `${signed.data}.${signed.signature}`;
  }

  /**
   * Verify and parse a signed token string
   */
  verifyToken(token: string): VerificationResult {
    const parts = token.split('.');
    if (parts.length !== 2) {
      return {
        valid: false,
        expired: false,
        error: 'Invalid token format',
      };
    }

    return this.verify({
      data: parts[0],
      signature: parts[1],
    });
  }
}

// ============================================================
// Singleton Instance
// ============================================================

let defaultInstance: HmacService | null = null;

/**
 * Get or create the default HMAC service instance
 */
export function getHmacService(secret?: string): HmacService {
  if (!defaultInstance) {
    const hmacSecret = secret || process.env.WEBHOOK_SECRET;
    if (!hmacSecret) {
      throw new Error('HMAC secret not configured. Set WEBHOOK_SECRET environment variable.');
    }
    defaultInstance = new HmacService({ secret: hmacSecret });
  }
  return defaultInstance;
}

/**
 * Reset the default instance (mainly for testing)
 */
export function resetHmacService(): void {
  defaultInstance = null;
}
