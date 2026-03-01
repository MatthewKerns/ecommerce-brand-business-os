import { NextRequest, NextResponse } from 'next/server'

/**
 * A Next.js API route handler function.
 */
export type RouteHandler = (
  req: NextRequest,
  context?: { params: Record<string, string> }
) => Promise<NextResponse>

/**
 * Correlation ID header name used for request tracing.
 */
export const CORRELATION_ID_HEADER = 'x-correlation-id'

/**
 * Standard API error response shape.
 */
export interface ApiErrorResponse {
  error: string
  message: string
  correlationId?: string
  timestamp: string
  details?: unknown
}
