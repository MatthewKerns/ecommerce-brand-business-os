/**
 * TikTok Analytics Types - TikTok Content Creator Analytics Data Models
 *
 * Type definitions and Zod validation schemas for TikTok analytics/metrics.
 * Based on TikTok for Business API and Creator Marketplace API structure.
 *
 * Zod schemas provide runtime validation when receiving data from TikTok API.
 * TypeScript types are inferred from schemas for compile-time type safety.
 */

import { z } from 'zod';

// ============================================================
// Zod Schemas
// ============================================================

/**
 * TikTok video metrics schema
 */
export const TikTokVideoMetricsSchema = z.object({
  video_id: z.string(),
  video_url: z.string().optional(),
  posted_at: z.number(), // Unix timestamp

  // Engagement Metrics
  views: z.number().int().nonnegative(),
  likes: z.number().int().nonnegative(),
  comments: z.number().int().nonnegative(),
  shares: z.number().int().nonnegative(),
  saves: z.number().int().nonnegative().optional(),

  // Watch Metrics
  watch_time_avg_seconds: z.number().nonnegative().optional(),
  watch_time_total_hours: z.number().nonnegative().optional(),
  video_completion_rate: z.number().min(0).max(100).optional(), // Percentage

  // Commerce Metrics
  shop_clicks: z.number().int().nonnegative().optional(),
  product_views: z.number().int().nonnegative().optional(),

  // Calculated Metrics
  engagement_rate: z.number().min(0).max(100).optional(), // Percentage

  // Content Metadata
  caption: z.string().optional(),
  hashtags: z.array(z.string()).optional(),

  // Demographics & Traffic
  source_location: z.string().optional(),
  traffic_source: z.string().optional(),

  // Metadata
  recorded_at: z.number().optional(), // Unix timestamp when metrics were fetched
});

/**
 * TikTok video list response schema
 */
export const TikTokVideoListResponseSchema = z.object({
  videos: z.array(TikTokVideoMetricsSchema),
  total: z.number().int().nonnegative(),
  cursor: z.string().optional(),
  has_more: z.boolean(),
});

/**
 * TikTok account analytics summary schema
 */
export const TikTokAccountAnalyticsSchema = z.object({
  account_id: z.string(),
  date_range_start: z.number(), // Unix timestamp
  date_range_end: z.number(), // Unix timestamp

  // Overview Metrics
  total_followers: z.number().int().nonnegative(),
  follower_growth: z.number().int(),
  total_videos: z.number().int().nonnegative(),

  // Aggregate Engagement
  total_views: z.number().int().nonnegative(),
  total_likes: z.number().int().nonnegative(),
  total_comments: z.number().int().nonnegative(),
  total_shares: z.number().int().nonnegative(),
  total_saves: z.number().int().nonnegative().optional(),

  // Aggregate Commerce
  total_shop_clicks: z.number().int().nonnegative().optional(),
  total_product_views: z.number().int().nonnegative().optional(),

  // Average Performance
  avg_engagement_rate: z.number().min(0).max(100).optional(),
  avg_completion_rate: z.number().min(0).max(100).optional(),

  // Metadata
  recorded_at: z.number(), // Unix timestamp when metrics were fetched
});

/**
 * TikTok product analytics schema (for TikTok Shop)
 */
export const TikTokProductAnalyticsSchema = z.object({
  product_id: z.string(),
  product_name: z.string(),
  date_range_start: z.number(), // Unix timestamp
  date_range_end: z.number(), // Unix timestamp

  // Product Performance
  product_views: z.number().int().nonnegative(),
  product_clicks: z.number().int().nonnegative(),
  add_to_cart: z.number().int().nonnegative().optional(),
  purchases: z.number().int().nonnegative().optional(),

  // Revenue Metrics
  gross_sales: z.number().nonnegative().optional(),
  units_sold: z.number().int().nonnegative().optional(),

  // Conversion Metrics
  conversion_rate: z.number().min(0).max(100).optional(),

  // Metadata
  recorded_at: z.number(), // Unix timestamp when metrics were fetched
});

// ============================================================
// TypeScript Types (Inferred from Zod Schemas)
// ============================================================

/**
 * TikTok video metrics
 */
export type TikTokVideoMetrics = z.infer<typeof TikTokVideoMetricsSchema>;

/**
 * TikTok video list response
 */
export type TikTokVideoListResponse = z.infer<typeof TikTokVideoListResponseSchema>;

/**
 * TikTok account analytics summary
 */
export type TikTokAccountAnalytics = z.infer<typeof TikTokAccountAnalyticsSchema>;

/**
 * TikTok product analytics
 */
export type TikTokProductAnalytics = z.infer<typeof TikTokProductAnalyticsSchema>;

// ============================================================
// Helper Types
// ============================================================

/**
 * TikTok video metrics filter parameters
 */
export interface TikTokVideoMetricsParams {
  posted_from?: number; // Unix timestamp
  posted_to?: number; // Unix timestamp
  video_ids?: string[];
  cursor?: string;
  page_size?: number;
}

/**
 * TikTok account analytics parameters
 */
export interface TikTokAccountAnalyticsParams {
  date_from: number; // Unix timestamp
  date_to: number; // Unix timestamp
}

/**
 * TikTok product analytics parameters
 */
export interface TikTokProductAnalyticsParams {
  date_from: number; // Unix timestamp
  date_to: number; // Unix timestamp
  product_ids?: string[];
}
