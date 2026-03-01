/**
 * API Client Library
 *
 * Centralized HTTP client for making API requests to Next.js API routes.
 * Provides type-safe wrappers with error handling, retry logic with
 * exponential backoff, and request deduplication.
 */

import {
  withRetry,
  retryPolicies,
  deduplicateRequest,
  generateIdempotencyKey,
} from '@/lib/resilience'
import type { RetryPolicy } from '@/lib/resilience'

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public data?: unknown
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

export interface ApiClientOptions {
  /** Request timeout in milliseconds (default: 10000) */
  timeout?: number
  /** Number of retry attempts (default: 0 for backwards compat) */
  retries?: number
  /** Retry delay in milliseconds (legacy, prefer retryPolicy) */
  retryDelay?: number
  /** Custom headers */
  headers?: Record<string, string>
  /** Retry policy (overrides retries/retryDelay) */
  retryPolicy?: RetryPolicy
  /** Deduplicate concurrent identical requests (GET only). Default false. */
  deduplicate?: boolean
  /** Abort signal for external cancellation */
  signal?: AbortSignal
}

/**
 * Internal helper that executes a single fetch and throws ApiError on failure.
 */
async function executeFetch<T>(
  url: string,
  init: RequestInit,
  timeout: number
): Promise<T> {
  const controller = new AbortController()
  const timeoutId = setTimeout(() => controller.abort(), timeout)

  // Combine external signal with timeout signal
  const existingSignal = init.signal
  if (existingSignal) {
    existingSignal.addEventListener('abort', () => controller.abort())
  }

  try {
    const response = await fetch(url, {
      ...init,
      signal: controller.signal,
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => null)
      throw new ApiError(
        errorData?.message || `HTTP error ${response.status}`,
        response.status,
        errorData
      )
    }

    return await response.json()
  } finally {
    clearTimeout(timeoutId)
  }
}

/**
 * Resolve the retry policy from options. If a RetryPolicy is provided
 * directly, use it. Otherwise, build one from the legacy retries/retryDelay
 * fields. If neither, return undefined (no retries).
 */
function resolveRetryPolicy(
  options: ApiClientOptions,
  defaultPolicy?: RetryPolicy
): RetryPolicy | undefined {
  if (options.retryPolicy) return options.retryPolicy
  if (options.retries && options.retries > 0) {
    return {
      maxRetries: options.retries,
      baseDelayMs: options.retryDelay ?? 1000,
      maxDelayMs: (options.retryDelay ?? 1000) * 8,
      jitterFactor: 1,
    }
  }
  return defaultPolicy
}

/**
 * Generic HTTP GET request
 */
export async function get<T>(
  url: string,
  options: ApiClientOptions = {}
): Promise<T> {
  const { timeout = 10000, headers = {}, deduplicate: dedup = false } = options
  const policy = resolveRetryPolicy(options, retryPolicies.read)

  const doFetch = () =>
    executeFetch<T>(url, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json', ...headers },
      signal: options.signal,
    }, timeout)

  const retryFetch = policy
    ? () => withRetry(doFetch, { policy, signal: options.signal })
    : doFetch

  if (dedup) {
    return deduplicateRequest(url, retryFetch)
  }

  return retryFetch()
}

/**
 * Generic HTTP POST request
 */
export async function post<T>(
  url: string,
  body: unknown,
  options: ApiClientOptions = {}
): Promise<T> {
  const { timeout = 10000, headers = {} } = options
  const policy = resolveRetryPolicy(options)
  const idempotencyKey = generateIdempotencyKey('post')

  const doFetch = () =>
    executeFetch<T>(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Idempotency-Key': idempotencyKey,
        ...headers,
      },
      body: JSON.stringify(body),
      signal: options.signal,
    }, timeout)

  if (policy) {
    return withRetry(doFetch, { policy, signal: options.signal })
  }

  return doFetch()
}

/**
 * Generic HTTP PUT request
 */
export async function put<T>(
  url: string,
  body: unknown,
  options: ApiClientOptions = {}
): Promise<T> {
  const { timeout = 10000, headers = {} } = options
  const policy = resolveRetryPolicy(options)
  const idempotencyKey = generateIdempotencyKey('put')

  const doFetch = () =>
    executeFetch<T>(url, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Idempotency-Key': idempotencyKey,
        ...headers,
      },
      body: JSON.stringify(body),
      signal: options.signal,
    }, timeout)

  if (policy) {
    return withRetry(doFetch, { policy, signal: options.signal })
  }

  return doFetch()
}

/**
 * Generic HTTP DELETE request
 */
export async function del<T>(
  url: string,
  options: ApiClientOptions = {}
): Promise<T> {
  const { timeout = 10000, headers = {} } = options
  const policy = resolveRetryPolicy(options)

  const doFetch = () =>
    executeFetch<T>(url, {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json', ...headers },
      signal: options.signal,
    }, timeout)

  if (policy) {
    return withRetry(doFetch, { policy, signal: options.signal })
  }

  return doFetch()
}

/**
 * Export apiClient object with all HTTP methods
 */
export const apiClient = {
  get,
  post,
  put,
  delete: del,
}
