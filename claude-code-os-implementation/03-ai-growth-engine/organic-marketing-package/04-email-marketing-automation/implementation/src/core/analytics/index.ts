/**
 * Analytics Module - Email tracking and performance measurement
 *
 * Exports:
 * - HMAC signing utilities for secure tracking
 * - Tracking pixel generation for email opens
 * - Click URL wrapping for link tracking
 * - Token parsing and verification
 */

// HMAC Utilities
export {
  HmacService,
  getHmacService,
  resetHmacService,
  type SignedData,
  type VerificationResult,
  type HmacConfig,
} from './hmac';

// Tracking System
export {
  TrackingService,
  getTrackingService,
  resetTrackingService,
  generateTrackingPixel,
  generateClickTrackingUrl,
  parseTrackingToken,
  type TrackingPixelParams,
  type ClickTrackingParams,
  type TrackingConfig,
  type ParsedTrackingData,
} from './tracking';
