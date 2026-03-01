import { NextRequest, NextResponse } from 'next/server'
import { CORRELATION_ID_HEADER, type RouteHandler } from './types'

/**
 * Generate a short correlation ID for request tracing.
 */
function generateCorrelationId(): string {
  const timestamp = Date.now().toString(36)
  const random = Math.random().toString(36).substring(2, 8)
  return `${timestamp}-${random}`
}

interface LogEntry {
  correlationId: string
  method: string
  path: string
  status?: number
  durationMs?: number
  error?: string
}

function log(level: 'info' | 'warn' | 'error', entry: LogEntry): void {
  const payload = {
    level,
    ...entry,
    timestamp: new Date().toISOString(),
  }
  if (level === 'error') {
    // eslint-disable-next-line no-console
    console.error(JSON.stringify(payload))
  } else {
    // eslint-disable-next-line no-console
    console.log(JSON.stringify(payload))
  }
}

/**
 * Middleware that adds structured logging with correlation IDs.
 *
 * Attaches a correlation ID to the request (via header) and logs
 * the request/response lifecycle with timing information.
 *
 * @example
 * ```ts
 * export const GET = withLogging(async (req) => {
 *   return NextResponse.json({ ok: true })
 * })
 * ```
 */
export function withLogging(handler: RouteHandler): RouteHandler {
  return async (req, context) => {
    const correlationId =
      req.headers.get(CORRELATION_ID_HEADER) || generateCorrelationId()
    const method = req.method
    const path = new URL(req.url).pathname
    const start = performance.now()

    log('info', { correlationId, method, path })

    try {
      const response = await handler(req, context)

      const durationMs = Math.round(performance.now() - start)
      log('info', {
        correlationId,
        method,
        path,
        status: response.status,
        durationMs,
      })

      // Attach correlation ID to the response so clients can reference it
      response.headers.set(CORRELATION_ID_HEADER, correlationId)
      return response
    } catch (err) {
      const durationMs = Math.round(performance.now() - start)
      const message = err instanceof Error ? err.message : 'Unknown error'
      log('error', { correlationId, method, path, durationMs, error: message })
      throw err
    }
  }
}

export { generateCorrelationId }
