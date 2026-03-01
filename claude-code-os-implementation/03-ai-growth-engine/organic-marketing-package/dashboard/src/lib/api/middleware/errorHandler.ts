import { NextResponse } from 'next/server'
import { CORRELATION_ID_HEADER, type ApiErrorResponse, type RouteHandler } from './types'
import { TimeoutError } from './timeout'

/**
 * Map of known error names/types to HTTP status codes.
 */
const ERROR_STATUS_MAP: Record<string, number> = {
  ValidationError: 400,
  BadRequestError: 400,
  UnauthorizedError: 401,
  ForbiddenError: 403,
  NotFoundError: 404,
  ConflictError: 409,
  TimeoutError: 504,
  CircuitOpenError: 503,
}

/**
 * Derive an HTTP status code from an error instance.
 */
function statusFromError(err: unknown): number {
  if (err && typeof err === 'object') {
    // Support errors that carry their own status
    if ('status' in err && typeof (err as { status: unknown }).status === 'number') {
      return (err as { status: number }).status
    }
    if ('name' in err && typeof (err as { name: unknown }).name === 'string') {
      const mapped = ERROR_STATUS_MAP[(err as { name: string }).name]
      if (mapped) return mapped
    }
  }
  return 500
}

/**
 * Centralized error handler middleware for Next.js API routes.
 *
 * Wraps a route handler and catches any thrown error, returning a
 * consistent JSON error response. In development, includes the
 * error stack trace; in production, only the sanitized message.
 *
 * @example
 * ```ts
 * export const GET = withErrorHandler(async (req) => {
 *   const data = await fetchData()
 *   return NextResponse.json(data)
 * })
 * ```
 */
export function withErrorHandler(handler: RouteHandler): RouteHandler {
  return async (req, context) => {
    try {
      return await handler(req, context)
    } catch (err) {
      const status = statusFromError(err)
      const correlationId = req.headers.get(CORRELATION_ID_HEADER) || ''
      const message =
        err instanceof Error ? err.message : 'An unexpected error occurred'

      // Log server-side errors
      if (status >= 500) {
        // eslint-disable-next-line no-console
        console.error(
          JSON.stringify({
            level: 'error',
            correlationId,
            status,
            error: message,
            stack:
              process.env.NODE_ENV === 'development' && err instanceof Error
                ? err.stack
                : undefined,
            timestamp: new Date().toISOString(),
          })
        )
      }

      const body: ApiErrorResponse = {
        error: errorLabel(status, err),
        message: status >= 500 && process.env.NODE_ENV === 'production'
          ? 'Internal server error'
          : message,
        correlationId: correlationId || undefined,
        timestamp: new Date().toISOString(),
      }

      return NextResponse.json(body, { status })
    }
  }
}

function errorLabel(status: number, err: unknown): string {
  if (err instanceof TimeoutError) return 'Gateway Timeout'
  switch (status) {
    case 400:
      return 'Bad Request'
    case 401:
      return 'Unauthorized'
    case 403:
      return 'Forbidden'
    case 404:
      return 'Not Found'
    case 409:
      return 'Conflict'
    case 503:
      return 'Service Unavailable'
    case 504:
      return 'Gateway Timeout'
    default:
      return 'Internal Server Error'
  }
}
