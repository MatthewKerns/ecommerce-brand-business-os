/**
 * Email Tracking System - HMAC-signed tracking pixels and click URLs
 *
 * Features:
 * - Tracking pixel generation for email opens
 * - Click URL wrapping with redirect tracking
 * - HMAC signatures to prevent tampering
 * - Campaign and message-level tracking
 * - URL parameter preservation
 */

import { getHmacService } from './hmac';

// ============================================================
// Types
// ============================================================

export interface TrackingPixelParams {
  leadId: string;
  messageId: string;
  campaignId?: string;
  sequenceId?: string;
  templateId?: string;
  metadata?: Record<string, any>;
}

export interface ClickTrackingParams {
  leadId: string;
  messageId: string;
  targetUrl: string;
  linkId?: string;
  campaignId?: string;
  sequenceId?: string;
  metadata?: Record<string, any>;
}

export interface TrackingConfig {
  baseUrl: string;
  pixelEndpoint?: string;
  clickEndpoint?: string;
  includeMetadata?: boolean;
}

export interface ParsedTrackingData {
  leadId: string;
  messageId: string;
  campaignId?: string;
  sequenceId?: string;
  templateId?: string;
  linkId?: string;
  targetUrl?: string;
  metadata?: Record<string, any>;
  valid: boolean;
  expired: boolean;
  error?: string;
}

// ============================================================
// Constants
// ============================================================

const DEFAULT_PIXEL_ENDPOINT = '/track/open';
const DEFAULT_CLICK_ENDPOINT = '/track/click';
const PIXEL_GIF_BASE64 = 'R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7'; // 1x1 transparent GIF

// ============================================================
// Helper Functions
// ============================================================

/**
 * Build URL with query parameters
 */
function buildUrl(baseUrl: string, endpoint: string, params: Record<string, string>): string {
  const url = new URL(endpoint, baseUrl);
  for (const [key, value] of Object.entries(params)) {
    url.searchParams.set(key, value);
  }
  return url.toString();
}

/**
 * Validate required tracking parameters
 */
function validateTrackingParams(params: TrackingPixelParams | ClickTrackingParams): void {
  if (!params.leadId) {
    throw new Error('leadId is required for tracking');
  }
  if (!params.messageId) {
    throw new Error('messageId is required for tracking');
  }
  if ('targetUrl' in params && !params.targetUrl) {
    throw new Error('targetUrl is required for click tracking');
  }
}

// ============================================================
// Tracking Service Class
// ============================================================

export class TrackingService {
  private readonly config: Required<TrackingConfig>;

  constructor(config: TrackingConfig) {
    if (!config.baseUrl) {
      throw new Error('baseUrl is required for tracking');
    }
    this.config = {
      baseUrl: config.baseUrl.replace(/\/$/, ''), // Remove trailing slash
      pixelEndpoint: config.pixelEndpoint || DEFAULT_PIXEL_ENDPOINT,
      clickEndpoint: config.clickEndpoint || DEFAULT_CLICK_ENDPOINT,
      includeMetadata: config.includeMetadata ?? true,
    };
  }

  /**
   * Generate tracking pixel URL for email opens
   */
  generateTrackingPixel(params: TrackingPixelParams): string {
    validateTrackingParams(params);

    const hmacService = getHmacService();
    const trackingData: Record<string, any> = {
      lid: params.leadId,
      mid: params.messageId,
    };

    // Add optional parameters
    if (params.campaignId) trackingData.cid = params.campaignId;
    if (params.sequenceId) trackingData.sid = params.sequenceId;
    if (params.templateId) trackingData.tid = params.templateId;
    if (this.config.includeMetadata && params.metadata) {
      trackingData.meta = params.metadata;
    }

    // Create signed token
    const token = hmacService.createToken(trackingData);

    // Build pixel URL
    return buildUrl(this.config.baseUrl, this.config.pixelEndpoint, { t: token });
  }

  /**
   * Generate tracking pixel HTML tag
   */
  generateTrackingPixelTag(params: TrackingPixelParams): string {
    const url = this.generateTrackingPixel(params);
    return `<img src="${url}" width="1" height="1" border="0" alt="" style="display:block;border:0;outline:none;text-decoration:none;" />`;
  }

  /**
   * Generate wrapped click tracking URL
   */
  generateClickTrackingUrl(params: ClickTrackingParams): string {
    validateTrackingParams(params);

    const hmacService = getHmacService();
    const trackingData: Record<string, any> = {
      lid: params.leadId,
      mid: params.messageId,
      url: params.targetUrl,
    };

    // Add optional parameters
    if (params.linkId) trackingData.link = params.linkId;
    if (params.campaignId) trackingData.cid = params.campaignId;
    if (params.sequenceId) trackingData.sid = params.sequenceId;
    if (this.config.includeMetadata && params.metadata) {
      trackingData.meta = params.metadata;
    }

    // Create signed token
    const token = hmacService.createToken(trackingData);

    // Build click tracking URL
    return buildUrl(this.config.baseUrl, this.config.clickEndpoint, { t: token });
  }

  /**
   * Parse and verify tracking token from URL
   */
  parseTrackingToken(token: string): ParsedTrackingData {
    try {
      const hmacService = getHmacService();
      const result = hmacService.verifyToken(token);

      if (!result.valid) {
        return {
          leadId: '',
          messageId: '',
          valid: false,
          expired: false,
          error: result.error || 'Invalid token',
        };
      }

      const data = result.data as Record<string, any>;

      return {
        leadId: data.lid || '',
        messageId: data.mid || '',
        campaignId: data.cid,
        sequenceId: data.sid,
        templateId: data.tid,
        linkId: data.link,
        targetUrl: data.url,
        metadata: data.meta,
        valid: true,
        expired: result.expired || false,
      };
    } catch (error: any) {
      return {
        leadId: '',
        messageId: '',
        valid: false,
        expired: false,
        error: error.message || 'Failed to parse token',
      };
    }
  }

  /**
   * Wrap all links in email HTML with click tracking
   */
  wrapLinksWithTracking(
    html: string,
    leadId: string,
    messageId: string,
    options?: {
      campaignId?: string;
      sequenceId?: string;
      metadata?: Record<string, any>;
    }
  ): string {
    // Regular expression to match href attributes in anchor tags
    const hrefPattern = /<a\s+([^>]*?)href=["']([^"']+)["']([^>]*)>/gi;

    let linkIndex = 0;
    return html.replace(hrefPattern, (match, beforeHref, url, afterHref) => {
      // Skip tracking pixels and already tracked URLs
      if (
        url.includes(this.config.pixelEndpoint) ||
        url.includes(this.config.clickEndpoint) ||
        url.startsWith('#') ||
        url.startsWith('mailto:') ||
        url.startsWith('tel:')
      ) {
        return match;
      }

      // Generate tracking URL
      const trackingUrl = this.generateClickTrackingUrl({
        leadId,
        messageId,
        targetUrl: url,
        linkId: `link_${linkIndex++}`,
        campaignId: options?.campaignId,
        sequenceId: options?.sequenceId,
        metadata: options?.metadata,
      });

      return `<a ${beforeHref}href="${trackingUrl}"${afterHref}>`;
    });
  }

  /**
   * Insert tracking pixel at end of HTML body
   */
  insertTrackingPixel(
    html: string,
    params: TrackingPixelParams
  ): string {
    const pixelTag = this.generateTrackingPixelTag(params);

    // Try to insert before closing body tag
    if (html.toLowerCase().includes('</body>')) {
      return html.replace(/<\/body>/i, `${pixelTag}</body>`);
    }

    // Otherwise append to end
    return html + pixelTag;
  }

  /**
   * Apply complete tracking to email HTML (pixel + click tracking)
   */
  applyTracking(
    html: string,
    params: TrackingPixelParams
  ): string {
    // First wrap all links
    let trackedHtml = this.wrapLinksWithTracking(
      html,
      params.leadId,
      params.messageId,
      {
        campaignId: params.campaignId,
        sequenceId: params.sequenceId,
        metadata: params.metadata,
      }
    );

    // Then insert tracking pixel
    trackedHtml = this.insertTrackingPixel(trackedHtml, params);

    return trackedHtml;
  }
}

// ============================================================
// Singleton Instance & Convenience Functions
// ============================================================

let defaultInstance: TrackingService | null = null;

/**
 * Get or create the default tracking service instance
 */
export function getTrackingService(baseUrl?: string): TrackingService {
  if (!defaultInstance) {
    const trackingBaseUrl = baseUrl || process.env.TRACKING_BASE_URL || process.env.PUBLIC_URL;
    if (!trackingBaseUrl) {
      throw new Error(
        'Tracking base URL not configured. Set TRACKING_BASE_URL or PUBLIC_URL environment variable.'
      );
    }
    defaultInstance = new TrackingService({ baseUrl: trackingBaseUrl });
  }
  return defaultInstance;
}

/**
 * Reset the default instance (mainly for testing)
 */
export function resetTrackingService(): void {
  defaultInstance = null;
}

/**
 * Convenience function: Generate tracking pixel URL
 */
export function generateTrackingPixel(
  leadId: string,
  messageId: string,
  options?: {
    campaignId?: string;
    sequenceId?: string;
    templateId?: string;
    metadata?: Record<string, any>;
    baseUrl?: string;
  }
): string {
  const service = options?.baseUrl
    ? new TrackingService({ baseUrl: options.baseUrl })
    : getTrackingService();

  return service.generateTrackingPixel({
    leadId,
    messageId,
    campaignId: options?.campaignId,
    sequenceId: options?.sequenceId,
    templateId: options?.templateId,
    metadata: options?.metadata,
  });
}

/**
 * Convenience function: Generate click tracking URL
 */
export function generateClickTrackingUrl(
  leadId: string,
  messageId: string,
  targetUrl: string,
  options?: {
    linkId?: string;
    campaignId?: string;
    sequenceId?: string;
    metadata?: Record<string, any>;
    baseUrl?: string;
  }
): string {
  const service = options?.baseUrl
    ? new TrackingService({ baseUrl: options.baseUrl })
    : getTrackingService();

  return service.generateClickTrackingUrl({
    leadId,
    messageId,
    targetUrl,
    linkId: options?.linkId,
    campaignId: options?.campaignId,
    sequenceId: options?.sequenceId,
    metadata: options?.metadata,
  });
}

/**
 * Convenience function: Parse tracking token
 */
export function parseTrackingToken(token: string, baseUrl?: string): ParsedTrackingData {
  const service = baseUrl
    ? new TrackingService({ baseUrl })
    : getTrackingService();

  return service.parseTrackingToken(token);
}
