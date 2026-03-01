/**
 * Sentry Initialization and Configuration
 *
 * Centralized Sentry setup that integrates with our enhanced error classes.
 * Provides helper functions for capturing errors with proper context,
 * user identification (without PII), and environment tagging.
 */

import * as Sentry from '@sentry/nextjs'
import type { ApiError } from '@/lib/errors/ApiError'
import type { ValidationError } from '@/lib/errors/ValidationError'
import type { ServiceError } from '@/lib/errors/ServiceError'
import { getErrorCategory } from '@/lib/error-handling'
import { ErrorCategory } from '@/lib/errors/errorCodes'

// ---------------------------------------------------------------------------
// Initialization
// ---------------------------------------------------------------------------

const SENTRY_DSN = process.env.NEXT_PUBLIC_SENTRY_DSN

export function isSentryEnabled(): boolean {
  return Boolean(SENTRY_DSN)
}

export interface SentryInitOptions {
  /** Override the DSN (defaults to NEXT_PUBLIC_SENTRY_DSN) */
  dsn?: string
  /** Override the environment tag */
  environment?: string
  /** Traces sample rate (0-1). Defaults to 0.1 in prod, 1.0 in dev */
  tracesSampleRate?: number
  /** Replay sample rate (0-1). Defaults to 0.1 */
  replaysSessionSampleRate?: number
  /** Error replay sample rate (0-1). Defaults to 1.0 */
  replaysOnErrorSampleRate?: number
}

export function initSentry(options: SentryInitOptions = {}) {
  const dsn = options.dsn ?? SENTRY_DSN
  if (!dsn) return

  const environment = options.environment ?? process.env.NODE_ENV ?? 'development'
  const isDev = environment === 'development'

  Sentry.init({
    dsn,
    environment,
    release: process.env.NEXT_PUBLIC_APP_VERSION ?? 'unknown',

    // Performance monitoring
    tracesSampleRate: options.tracesSampleRate ?? (isDev ? 1.0 : 0.1),

    // Session replay
    replaysSessionSampleRate: options.replaysSessionSampleRate ?? 0.1,
    replaysOnErrorSampleRate: options.replaysOnErrorSampleRate ?? 1.0,

    // Only send errors in production; in dev, log to console
    enabled: !isDev,

    // Filter out noisy or irrelevant errors
    beforeSend(event, hint) {
      const error = hint.originalException

      // Skip validation errors - they are expected user input issues
      if (isValidationError(error)) {
        return null
      }

      // Enrich the event with our error metadata
      if (isApiError(error)) {
        event.tags = {
          ...event.tags,
          error_code: error.code,
          error_category: error.category,
          http_status: String(error.status),
          api_method: error.method,
        }
        event.extra = {
          ...event.extra,
          api_url: error.url,
          request_id: error.requestId,
          retry_metadata: error.retryMetadata,
        }
      }

      if (isServiceError(error)) {
        event.tags = {
          ...event.tags,
          error_code: error.code,
          error_category: error.category,
          service_name: error.serviceName,
        }
        event.extra = {
          ...event.extra,
          service_endpoint: error.endpoint,
          fallback_options: error.fallbackOptions,
        }
      }

      return event
    },

    // Ignore common non-actionable errors
    ignoreErrors: [
      'ResizeObserver loop',
      'ResizeObserver loop completed with undelivered notifications',
      'Non-Error promise rejection',
      /Loading chunk \d+ failed/,
    ],
  })
}

// ---------------------------------------------------------------------------
// Error Capture Helpers
// ---------------------------------------------------------------------------

/**
 * Capture an error with full context from our enhanced error classes.
 */
export function captureError(error: unknown, context?: Record<string, unknown>) {
  if (!isSentryEnabled()) return

  const category = getErrorCategory(error)

  Sentry.withScope((scope) => {
    scope.setTag('error_category', category)

    if (context) {
      scope.setExtras(context)
    }

    if (isApiError(error)) {
      scope.setTag('error_code', error.code)
      scope.setTag('http_status', String(error.status))
      scope.setFingerprint(['api-error', error.code, String(error.status)])
    } else if (isServiceError(error)) {
      scope.setTag('service_name', error.serviceName)
      scope.setFingerprint(['service-error', error.serviceName, error.code])
    }

    if (error instanceof Error) {
      Sentry.captureException(error)
    } else {
      Sentry.captureMessage(String(error), 'error')
    }
  })
}

/**
 * Set user context for Sentry (without PII).
 * Uses opaque IDs from Clerk rather than names/emails.
 */
export function setUser(params: { id: string; workspaceId?: string | null }) {
  if (!isSentryEnabled()) return

  Sentry.setUser({
    id: params.id,
    ...(params.workspaceId ? { segment: params.workspaceId } : {}),
  })
}

/**
 * Clear user context (e.g., on sign out).
 */
export function clearUser() {
  if (!isSentryEnabled()) return
  Sentry.setUser(null)
}

/**
 * Add a breadcrumb for tracing user actions that led to an error.
 */
export function addBreadcrumb(params: {
  category: string
  message: string
  level?: Sentry.SeverityLevel
  data?: Record<string, unknown>
}) {
  if (!isSentryEnabled()) return

  Sentry.addBreadcrumb({
    category: params.category,
    message: params.message,
    level: params.level ?? 'info',
    data: params.data,
  })
}

/**
 * Track a performance transaction for critical flows.
 */
export function startTransaction(name: string, op: string) {
  if (!isSentryEnabled()) return undefined
  return Sentry.startInactiveSpan({ name, op })
}

// ---------------------------------------------------------------------------
// Type guards for error classes
// ---------------------------------------------------------------------------

function isApiError(error: unknown): error is ApiError {
  return error instanceof Error && error.name === 'ApiError' && 'status' in error && 'code' in error
}

function isValidationError(error: unknown): error is ValidationError {
  return error instanceof Error && error.name === 'ValidationError' && 'fieldErrors' in error
}

function isServiceError(error: unknown): error is ServiceError {
  return error instanceof Error && error.name === 'ServiceError' && 'serviceName' in error
}

// Re-export Sentry for direct access when needed
export { Sentry }

// Re-export ErrorCategory for convenience
export { ErrorCategory }
