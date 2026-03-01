/**
 * Service Error Class
 *
 * Specialized error for external service failures (e.g. Clerk, Klaviyo,
 * TikTok API, content agents backend). Carries service identification,
 * fallback options, and circuit breaker metadata.
 */

import { ErrorCode, ErrorCategory } from './errorCodes'

export interface FallbackOption {
  /** Description of the fallback strategy */
  description: string
  /** Type of fallback */
  type: 'cache' | 'default_value' | 'alternative_service' | 'degraded_mode' | 'queue'
}

export class ServiceError extends Error {
  readonly code: ErrorCode
  readonly category = ErrorCategory.SERVICE as const
  readonly serviceName: string
  readonly endpoint: string
  readonly fallbackOptions: FallbackOption[]
  readonly retryable: boolean
  readonly timestamp: string
  readonly originalError?: Error

  constructor(params: {
    message: string
    serviceName: string
    endpoint?: string
    code?: ErrorCode
    retryable?: boolean
    fallbackOptions?: FallbackOption[]
    originalError?: Error
  }) {
    super(`[${params.serviceName}] ${params.message}`)
    this.name = 'ServiceError'
    this.serviceName = params.serviceName
    this.endpoint = params.endpoint ?? ''
    this.code = params.code ?? ErrorCode.SERVICE_UNAVAILABLE
    this.retryable = params.retryable ?? true
    this.fallbackOptions = params.fallbackOptions ?? []
    this.originalError = params.originalError
    this.timestamp = new Date().toISOString()
  }

  /** Whether any fallback strategy is available. */
  get hasFallback(): boolean {
    return this.fallbackOptions.length > 0
  }

  /** User-facing message. */
  get userMessage(): string {
    const base = `The ${this.serviceName} service is experiencing issues.`
    if (this.hasFallback) {
      return `${base} Some features may be temporarily limited.`
    }
    return `${base} Please try again later.`
  }

  /** Serialize to a plain object for logging / monitoring. */
  toJSON() {
    return {
      name: this.name,
      message: this.message,
      code: this.code,
      category: this.category,
      serviceName: this.serviceName,
      endpoint: this.endpoint,
      retryable: this.retryable,
      fallbackOptions: this.fallbackOptions,
      timestamp: this.timestamp,
      originalError: this.originalError
        ? { name: this.originalError.name, message: this.originalError.message }
        : undefined,
    }
  }
}
