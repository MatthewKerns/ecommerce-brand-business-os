'use client';

/**
 * React hook for consuming CacheManager.
 *
 * Provides a simple API for cache reads with stale-while-revalidate,
 * manual invalidation, and cache stats.
 */

import { useCallback, useEffect, useRef, useState } from 'react';
import { CacheManager, CacheStats, getCacheManager, CacheLayer } from './cache-manager';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface UseCacheOptions<T> {
  /** Cache key */
  key: string;
  /** Function to fetch fresh data (used for stale-while-revalidate) */
  fetcher?: () => Promise<T>;
  /** Time-to-live in ms (overrides CacheManager default) */
  ttl?: number;
  /** Which cache layers to write to */
  layers?: CacheLayer[];
  /** Whether to fetch on mount (default: true) */
  fetchOnMount?: boolean;
}

export interface UseCacheReturn<T> {
  /** Cached data (or undefined if not yet loaded) */
  data: T | undefined;
  /** Whether a fetch is in progress */
  isLoading: boolean;
  /** Error from the latest fetch attempt */
  error: Error | undefined;
  /** Manually refresh the data */
  refresh: () => Promise<void>;
  /** Invalidate this key and re-fetch */
  invalidate: () => Promise<void>;
  /** Cache statistics */
  stats: CacheStats;
}

// ---------------------------------------------------------------------------
// Hook
// ---------------------------------------------------------------------------

export function useCache<T>(options: UseCacheOptions<T>): UseCacheReturn<T> {
  const { key, fetcher, ttl, layers, fetchOnMount = true } = options;

  const cacheRef = useRef<CacheManager>(getCacheManager());
  const [data, setData] = useState<T | undefined>(undefined);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | undefined>(undefined);
  const [stats, setStats] = useState<CacheStats>(() => cacheRef.current.getStats());

  // Stable reference for fetcher to avoid infinite effect loops
  const fetcherRef = useRef(fetcher);
  fetcherRef.current = fetcher;

  const load = useCallback(async () => {
    setIsLoading(true);
    setError(undefined);
    try {
      const cached = await cacheRef.current.get<T>(key, fetcherRef.current);
      if (cached !== undefined) {
        setData(cached);
      } else if (fetcherRef.current) {
        // Nothing cached, fetch fresh
        const freshValue = await fetcherRef.current();
        await cacheRef.current.set(key, freshValue, { ttl, layers });
        setData(freshValue);
      }
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Cache fetch failed'));
    } finally {
      setIsLoading(false);
      setStats(cacheRef.current.getStats());
    }
  }, [key, ttl, layers]);

  const refresh = useCallback(async () => {
    if (!fetcherRef.current) return;
    setIsLoading(true);
    setError(undefined);
    try {
      const freshValue = await fetcherRef.current();
      await cacheRef.current.set(key, freshValue, { ttl, layers });
      setData(freshValue);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Cache refresh failed'));
    } finally {
      setIsLoading(false);
      setStats(cacheRef.current.getStats());
    }
  }, [key, ttl, layers]);

  const invalidate = useCallback(async () => {
    await cacheRef.current.invalidate(key);
    setData(undefined);
    if (fetcherRef.current) {
      await load();
    }
    setStats(cacheRef.current.getStats());
  }, [key, load]);

  useEffect(() => {
    if (fetchOnMount) {
      load();
    }
  }, [fetchOnMount, load]);

  return { data, isLoading, error, refresh, invalidate, stats };
}
