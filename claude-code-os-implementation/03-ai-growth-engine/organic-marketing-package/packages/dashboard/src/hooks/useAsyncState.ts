"use client";

import { useState, useEffect, useCallback, useRef } from "react";

/**
 * Configuration options for useAsyncState
 */
export interface UseAsyncStateOptions<T> {
  /** Async function that fetches or produces the data */
  asyncFn: (signal: AbortSignal) => Promise<T>;
  /** Fallback data to use when the async operation fails */
  fallbackData?: T;
  /** Number of retry attempts on failure (default: 0) */
  retryCount?: number;
  /** Base delay in ms between retries, doubled each attempt (default: 1000) */
  retryDelay?: number;
  /** Whether to execute the async function immediately (default: true) */
  immediate?: boolean;
  /** Dependency array that triggers re-execution when values change */
  deps?: unknown[];
}

/**
 * State representing an in-progress optimistic update that can be rolled back
 */
interface OptimisticState<T> {
  previousData: T | null;
  pending: boolean;
}

/**
 * Return type for useAsyncState
 */
export interface UseAsyncStateReturn<T> {
  /** The current data value */
  data: T | null;
  /** Whether an async operation is in progress */
  isLoading: boolean;
  /** The error if the last operation failed */
  error: Error | null;
  /** Whether fallback data is currently being used */
  isFallback: boolean;
  /** Re-execute the async function */
  refetch: () => Promise<void>;
  /** Apply an optimistic update; returns a rollback function */
  optimisticUpdate: (updater: (current: T | null) => T) => () => void;
  /** Directly set data (e.g., from a form submission result) */
  setData: (data: T | null) => void;
}

/**
 * Unified async state management hook.
 *
 * Manages loading, error, and data states for async operations with built-in
 * retry logic, fallback data support, optimistic updates with rollback, and
 * automatic request cancellation on unmount.
 *
 * @example
 * ```tsx
 * const { data, isLoading, error, refetch } = useAsyncState({
 *   asyncFn: (signal) => fetch("/api/data", { signal }).then(r => r.json()),
 *   fallbackData: cachedData,
 *   retryCount: 2,
 * });
 * ```
 */
export function useAsyncState<T>(
  options: UseAsyncStateOptions<T>
): UseAsyncStateReturn<T> {
  const {
    asyncFn,
    fallbackData,
    retryCount = 0,
    retryDelay = 1000,
    immediate = true,
    deps = [],
  } = options;

  const [data, setData] = useState<T | null>(null);
  const [isLoading, setIsLoading] = useState(immediate);
  const [error, setError] = useState<Error | null>(null);
  const [isFallback, setIsFallback] = useState(false);

  const optimisticRef = useRef<OptimisticState<T>>({
    previousData: null,
    pending: false,
  });
  const abortControllerRef = useRef<AbortController | null>(null);
  const mountedRef = useRef(true);

  /**
   * Execute the async function with retry logic
   */
  const execute = useCallback(async () => {
    // Cancel any in-flight request
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    const controller = new AbortController();
    abortControllerRef.current = controller;

    setIsLoading(true);
    setError(null);
    setIsFallback(false);

    let lastError: Error | null = null;

    for (let attempt = 0; attempt <= retryCount; attempt++) {
      // Don't proceed if unmounted or aborted
      if (!mountedRef.current || controller.signal.aborted) return;

      try {
        const result = await asyncFn(controller.signal);

        if (!mountedRef.current || controller.signal.aborted) return;

        setData(result);
        setIsLoading(false);
        setError(null);
        setIsFallback(false);
        return;
      } catch (err) {
        // Ignore abort errors
        if (err instanceof DOMException && err.name === "AbortError") return;

        lastError =
          err instanceof Error ? err : new Error(String(err));

        // Wait before retrying (skip wait on last attempt)
        if (attempt < retryCount) {
          const delay = retryDelay * Math.pow(2, attempt);
          await new Promise((resolve) => setTimeout(resolve, delay));
        }
      }
    }

    // All attempts failed
    if (!mountedRef.current) return;

    setError(lastError);
    setIsLoading(false);

    // Use fallback data if available
    if (fallbackData !== undefined) {
      setData(fallbackData);
      setIsFallback(true);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [asyncFn, retryCount, retryDelay, fallbackData]);

  /**
   * Apply an optimistic update. Returns a function to rollback.
   */
  const optimisticUpdate = useCallback(
    (updater: (current: T | null) => T): (() => void) => {
      const previousData = data;
      optimisticRef.current = { previousData, pending: true };

      const newData = updater(data);
      setData(newData);

      return () => {
        if (optimisticRef.current.pending) {
          setData(optimisticRef.current.previousData);
          optimisticRef.current = { previousData: null, pending: false };
        }
      };
    },
    [data]
  );

  /**
   * Refetch wrapper
   */
  const refetch = useCallback(async () => {
    // Clear any pending optimistic update
    optimisticRef.current = { previousData: null, pending: false };
    await execute();
  }, [execute]);

  // Execute on mount and when deps change
  useEffect(() => {
    if (immediate) {
      execute();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [immediate, ...deps]);

  // Cleanup on unmount
  useEffect(() => {
    mountedRef.current = true;
    return () => {
      mountedRef.current = false;
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);

  return {
    data,
    isLoading,
    error,
    isFallback,
    refetch,
    optimisticUpdate,
    setData,
  };
}
