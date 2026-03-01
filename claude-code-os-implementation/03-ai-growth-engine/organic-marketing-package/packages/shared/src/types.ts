/**
 * Common types shared across Organic Marketing packages.
 */

export interface ContentMetrics {
  views: number;
  saves: number;
  shares: number;
  engagement_rate: number;
  timestamp: string;
}

export interface ServiceHealth {
  service: string;
  status: 'healthy' | 'degraded' | 'down';
  uptime_seconds: number;
  last_check: string;
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  timestamp: string;
}
