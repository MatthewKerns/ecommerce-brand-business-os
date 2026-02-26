/**
 * API Client Library
 *
 * Centralized HTTP client for making API requests to Next.js API routes.
 * Provides type-safe wrappers with error handling and retry logic.
 *
 * @example
 * ```ts
 * import { apiClient } from '@/lib/api-client'
 *
 * const data = await apiClient.get('/api/metrics')
 * ```
 */

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
  /** Number of retry attempts (default: 0) */
  retries?: number
  /** Retry delay in milliseconds (default: 1000) */
  retryDelay?: number
  /** Custom headers */
  headers?: Record<string, string>
}

/**
 * Generic HTTP GET request
 *
 * @param {string} url - API endpoint URL
 * @param {ApiClientOptions} options - Request options
 * @returns {Promise<T>} Parsed JSON response
 * @throws {ApiError} If request fails or response is not ok
 */
export async function get<T>(
  url: string,
  options: ApiClientOptions = {}
): Promise<T> {
  const { timeout = 10000, retries = 0, retryDelay = 1000, headers = {} } = options

  let lastError: Error | null = null
  let attempts = 0

  while (attempts <= retries) {
    try {
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), timeout)

      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          ...headers,
        },
        signal: controller.signal,
      })

      clearTimeout(timeoutId)

      if (!response.ok) {
        const errorData = await response.json().catch(() => null)
        throw new ApiError(
          errorData?.message || `HTTP error ${response.status}`,
          response.status,
          errorData
        )
      }

      return await response.json()
    } catch (error) {
      lastError = error instanceof Error ? error : new Error('Unknown error')

      // Don't retry on client errors (4xx)
      if (error instanceof ApiError && error.status >= 400 && error.status < 500) {
        throw error
      }

      // Retry on network errors or server errors (5xx)
      if (attempts < retries) {
        attempts++
        await new Promise((resolve) => setTimeout(resolve, retryDelay))
        continue
      }

      throw lastError
    }
  }

  throw lastError || new Error('Request failed')
}

/**
 * Generic HTTP POST request
 *
 * @param {string} url - API endpoint URL
 * @param {unknown} body - Request body (will be JSON stringified)
 * @param {ApiClientOptions} options - Request options
 * @returns {Promise<T>} Parsed JSON response
 * @throws {ApiError} If request fails or response is not ok
 */
export async function post<T>(
  url: string,
  body: unknown,
  options: ApiClientOptions = {}
): Promise<T> {
  const { timeout = 10000, headers = {} } = options

  try {
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), timeout)

    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...headers,
      },
      body: JSON.stringify(body),
      signal: controller.signal,
    })

    clearTimeout(timeoutId)

    if (!response.ok) {
      const errorData = await response.json().catch(() => null)
      throw new ApiError(
        errorData?.message || `HTTP error ${response.status}`,
        response.status,
        errorData
      )
    }

    return await response.json()
  } catch (error) {
    if (error instanceof ApiError) {
      throw error
    }
    throw new Error(error instanceof Error ? error.message : 'POST request failed')
  }
}

/**
 * Generic HTTP PUT request
 *
 * @param {string} url - API endpoint URL
 * @param {unknown} body - Request body (will be JSON stringified)
 * @param {ApiClientOptions} options - Request options
 * @returns {Promise<T>} Parsed JSON response
 * @throws {ApiError} If request fails or response is not ok
 */
export async function put<T>(
  url: string,
  body: unknown,
  options: ApiClientOptions = {}
): Promise<T> {
  const { timeout = 10000, headers = {} } = options

  try {
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), timeout)

    const response = await fetch(url, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        ...headers,
      },
      body: JSON.stringify(body),
      signal: controller.signal,
    })

    clearTimeout(timeoutId)

    if (!response.ok) {
      const errorData = await response.json().catch(() => null)
      throw new ApiError(
        errorData?.message || `HTTP error ${response.status}`,
        response.status,
        errorData
      )
    }

    return await response.json()
  } catch (error) {
    if (error instanceof ApiError) {
      throw error
    }
    throw new Error(error instanceof Error ? error.message : 'PUT request failed')
  }
}

/**
 * Generic HTTP DELETE request
 *
 * @param {string} url - API endpoint URL
 * @param {ApiClientOptions} options - Request options
 * @returns {Promise<T>} Parsed JSON response
 * @throws {ApiError} If request fails or response is not ok
 */
export async function del<T>(
  url: string,
  options: ApiClientOptions = {}
): Promise<T> {
  const { timeout = 10000, headers = {} } = options

  try {
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), timeout)

    const response = await fetch(url, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
        ...headers,
      },
      signal: controller.signal,
    })

    clearTimeout(timeoutId)

    if (!response.ok) {
      const errorData = await response.json().catch(() => null)
      throw new ApiError(
        errorData?.message || `HTTP error ${response.status}`,
        response.status,
        errorData
      )
    }

    return await response.json()
  } catch (error) {
    if (error instanceof ApiError) {
      throw error
    }
    throw new Error(error instanceof Error ? error.message : 'DELETE request failed')
  }
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
