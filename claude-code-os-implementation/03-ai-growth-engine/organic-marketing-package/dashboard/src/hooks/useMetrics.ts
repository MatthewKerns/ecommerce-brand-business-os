"use client";

import { useState, useEffect } from "react";
import { apiClient } from "@/lib/api-client";
import type { AggregatedMetrics } from "@/lib/metrics-fetcher";

/**
 * Return type for useMetrics hook
 */
export interface UseMetricsReturn {
  /** Aggregated metrics data from all services */
  metrics: AggregatedMetrics | null;
  /** Loading state - true during initial load and polls */
  isLoading: boolean;
  /** Error state if metrics fetch fails */
  error: Error | null;
  /** Manually trigger a metrics fetch */
  refetch: () => Promise<void>;
}

/**
 * Custom hook for fetching metrics data with optional polling
 *
 * Features:
 * - Fetches aggregated metrics from /api/metrics endpoint
 * - Optional automatic polling at configurable intervals
 * - Provides loading and error states
 * - Cleans up polling interval on unmount
 * - Manual refetch capability
 * - Proper error handling with user-friendly messages
 *
 * @param options - Configuration options
 * @param options.pollingInterval - Polling interval in milliseconds (default: disabled)
 * @param options.enabled - Whether fetching is enabled (default: true)
 *
 * @returns Object containing metrics data, loading state, error, and refetch function
 *
 * @example
 * ```tsx
 * function Dashboard() {
 *   const { metrics, isLoading, error, refetch } = useMetrics({
 *     pollingInterval: 60000, // Poll every 60 seconds
 *   });
 *
 *   if (error) return <div>Error: {error.message}</div>;
 *   if (isLoading) return <div>Loading...</div>;
 *
 *   return (
 *     <div>
 *       <h1>Total Reach: {metrics?.summary.totalReach.value}</h1>
 *       <button onClick={refetch}>Refresh</button>
 *     </div>
 *   );
 * }
 * ```
 */
export function useMetrics(options: {
  pollingInterval?: number;
  enabled?: boolean;
} = {}): UseMetricsReturn {
  const { pollingInterval, enabled = true } = options;

  const [metrics, setMetrics] = useState<AggregatedMetrics | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  /**
   * Fetches metrics data and updates state
   */
  const refetch = async () => {
    try {
      setError(null);
      const data = await apiClient.get<AggregatedMetrics>("/api/metrics");
      setMetrics(data);
    } catch (err) {
      setError(
        err instanceof Error ? err : new Error("Failed to fetch metrics")
      );
    } finally {
      setIsLoading(false);
    }
  };

  // Initial fetch and polling setup
  useEffect(() => {
    if (!enabled) {
      setIsLoading(false);
      return;
    }

    // Initial fetch
    refetch();

    // Set up polling interval if specified
    if (pollingInterval && pollingInterval > 0) {
      const intervalId = setInterval(() => {
        refetch();
      }, pollingInterval);

      // Cleanup on unmount
      return () => {
        clearInterval(intervalId);
      };
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pollingInterval, enabled]);

  return {
    metrics,
    isLoading,
    error,
    refetch,
  };
}
