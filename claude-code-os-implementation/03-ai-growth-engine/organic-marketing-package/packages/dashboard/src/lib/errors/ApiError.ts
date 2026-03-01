/**
 * Enhanced API Error Class
 *
 * Extends the base Error with HTTP status codes, retry metadata,
 * recovery hints, and structured error data for API failures.
 */

import { ErrorCode, ErrorCategory, errorCodeFromStatus, categoryFromCode } from './errorCodes'

export interface RetryMetadata {
  /** Whether this error is retryable */
  retryable: boolean
  /** Suggested delay in ms before retrying */
  retryAfterMs?: number
  /** Maximum number of retry attempts */
  maxRetries: number
  /** Current attempt number (0-based) */
  attempt: number
}

export interface RecoveryHint {
  /** Short action label for UI buttons (e.g., "Retry", "Sign In") */
  action: string
  /** Longer description of what the user should do */
  description: string
  /** Type of recovery action */
  type: 'retry' | 'redirect' | 'refresh' | 'contact_support' | 'dismiss'
  /** Optional URL for redirect-type recovery */
  url?: string
}

export class ApiError extends Error {
  readonly code: ErrorCode
  readonly category: ErrorCategory
  readonly status: number
  readonly retryMetadata: RetryMetadata
  readonly recoveryHint: RecoveryHint
  readonly data: unknown
  readonly url: string
  readonly method: string
  readonly requestId?: string
  readonly timestamp: string

  constructor(params: {
    message: string
    status: number
    url?: string
    method?: string
    data?: unknown
    requestId?: string
    code?: ErrorCode
    attempt?: number
    retryAfterMs?: number
  }) {
    super(params.message)
    this.name = 'ApiError'
    this.status = params.status
    this.url = params.url ?? ''
    this.method = params.method ?? 'GET'
    this.data = params.data
    this.requestId = params.requestId
    this.timestamp = new Date().toISOString()
    this.code = params.code ?? errorCodeFromStatus(params.status)
    this.category = categoryFromCode(this.code)
    this.retryMetadata = buildRetryMetadata(this.status, params.attempt ?? 0, params.retryAfterMs)
    this.recoveryHint = buildRecoveryHint(this.code, this.status)
  }

  /** Returns a user-facing message suitable for display in a toast or alert. */
  get userMessage(): string {
    return USER_MESSAGES[this.code] ?? 'Something went wrong. Please try again.'
  }

  /** Whether the caller should attempt a retry. */
  get shouldRetry(): boolean {
    return this.retryMetadata.retryable && this.retryMetadata.attempt < this.retryMetadata.maxRetries
  }

  /** Serialize to a plain object for logging / monitoring. */
  toJSON() {
    return {
      name: this.name,
      message: this.message,
      code: this.code,
      category: this.category,
      status: this.status,
      url: this.url,
      method: this.method,
      requestId: this.requestId,
      timestamp: this.timestamp,
      retryMetadata: this.retryMetadata,
      recoveryHint: this.recoveryHint,
    }
  }
}

// ---------------------------------------------------------------------------
// Internal helpers
// ---------------------------------------------------------------------------

function buildRetryMetadata(
  status: number,
  attempt: number,
  retryAfterMs?: number,
): RetryMetadata {
  // 5xx and 429 are retryable
  const retryable = status >= 500 || status === 429
  const maxRetries = status === 429 ? 5 : 3

  return {
    retryable,
    retryAfterMs: retryAfterMs ?? (retryable ? 1000 * Math.pow(2, attempt) : undefined),
    maxRetries,
    attempt,
  }
}

function buildRecoveryHint(code: ErrorCode, status: number): RecoveryHint {
  const hints: Partial<Record<ErrorCode, RecoveryHint>> = {
    [ErrorCode.API_UNAUTHORIZED]: {
      action: 'Sign In',
      description: 'Your session has expired. Please sign in again.',
      type: 'redirect',
      url: '/sign-in',
    },
    [ErrorCode.API_FORBIDDEN]: {
      action: 'Contact Admin',
      description: 'You do not have permission to perform this action.',
      type: 'contact_support',
    },
    [ErrorCode.API_NOT_FOUND]: {
      action: 'Go Back',
      description: 'The requested resource could not be found.',
      type: 'dismiss',
    },
    [ErrorCode.API_RATE_LIMITED]: {
      action: 'Wait & Retry',
      description: 'Too many requests. Please wait a moment and try again.',
      type: 'retry',
    },
    [ErrorCode.API_SERVER_ERROR]: {
      action: 'Retry',
      description: 'A server error occurred. Retrying may resolve the issue.',
      type: 'retry',
    },
    [ErrorCode.API_SERVICE_UNAVAILABLE]: {
      action: 'Retry Later',
      description: 'The service is temporarily unavailable. Please try again later.',
      type: 'retry',
    },
    [ErrorCode.API_GATEWAY_TIMEOUT]: {
      action: 'Retry',
      description: 'The request timed out. Please try again.',
      type: 'retry',
    },
  }

  if (hints[code]) {
    return hints[code]
  }

  // Fallback based on status range
  if (status >= 500) {
    return { action: 'Retry', description: 'A server error occurred.', type: 'retry' }
  }

  return {
    action: 'Dismiss',
    description: 'An unexpected error occurred.',
    type: 'dismiss',
  }
}

const USER_MESSAGES: Partial<Record<ErrorCode, string>> = {
  [ErrorCode.API_BAD_REQUEST]: 'The request was invalid. Please check your input and try again.',
  [ErrorCode.API_UNAUTHORIZED]: 'Your session has expired. Please sign in again.',
  [ErrorCode.API_FORBIDDEN]: 'You do not have permission to perform this action.',
  [ErrorCode.API_NOT_FOUND]: 'The requested resource was not found.',
  [ErrorCode.API_RATE_LIMITED]: 'Too many requests. Please wait a moment before trying again.',
  [ErrorCode.API_CONFLICT]: 'A conflict occurred. Someone may have modified this resource.',
  [ErrorCode.API_UNPROCESSABLE]: 'The data could not be processed. Please check your input.',
  [ErrorCode.API_SERVER_ERROR]: 'A server error occurred. Please try again.',
  [ErrorCode.API_BAD_GATEWAY]: 'A gateway error occurred. Please try again.',
  [ErrorCode.API_SERVICE_UNAVAILABLE]: 'The service is temporarily unavailable.',
  [ErrorCode.API_GATEWAY_TIMEOUT]: 'The request timed out. Please try again.',
  [ErrorCode.NETWORK_TIMEOUT]: 'The request timed out. Please check your connection.',
  [ErrorCode.NETWORK_OFFLINE]: 'You appear to be offline. Please check your internet connection.',
}
