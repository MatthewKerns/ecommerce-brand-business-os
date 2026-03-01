import { NextResponse } from 'next/server'
import { CORRELATION_ID_HEADER, type ApiErrorResponse, type RouteHandler } from './types'

/**
 * Middleware that enforces a timeout on the wrapped handler.
 *
 * If the handler does not resolve within the given duration, the
 * request is aborted and a 504 Gateway Timeout response is returned.
 *
 * @param ms - Timeout in milliseconds (default 30000)
 *
 * @example
 * ```ts
 * export const GET = withTimeout(5000)(async (req) => {
 *   const data = await longRunningQuery()
 *   return NextResponse.json(data)
 * })
 * ```
 */
export function withTimeout(ms = 30000) {
  return function wrapper(handler: RouteHandler): RouteHandler {
    return async (req, context) => {
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), ms)

      try {
        const result = await Promise.race([
          handler(req, context),
          new Promise<never>((_resolve, reject) => {
            controller.signal.addEventListener('abort', () => {
              reject(new TimeoutError(`Request timed out after ${ms}ms`))
            })
          }),
        ])
        return result
      } catch (err) {
        if (err instanceof TimeoutError) {
          const correlationId = req.headers.get(CORRELATION_ID_HEADER) || ''
          const body: ApiErrorResponse = {
            error: 'Gateway Timeout',
            message: err.message,
            correlationId: correlationId || undefined,
            timestamp: new Date().toISOString(),
          }
          return NextResponse.json(body, { status: 504 })
        }
        throw err
      } finally {
        clearTimeout(timeoutId)
      }
    }
  }
}

class TimeoutError extends Error {
  constructor(message: string) {
    super(message)
    this.name = 'TimeoutError'
  }
}

export { TimeoutError }
