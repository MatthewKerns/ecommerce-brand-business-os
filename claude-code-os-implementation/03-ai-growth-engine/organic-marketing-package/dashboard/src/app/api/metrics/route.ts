/**
 * Metrics API Route
 *
 * GET /api/metrics - Returns aggregated metrics from all services
 */

import { NextRequest, NextResponse } from 'next/server'
import { fetchAllMetrics } from '@/lib/metrics-fetcher'
import { withErrorHandler, withLogging, withTimeout } from '@/lib/api/middleware'
import { serviceBreakers, CircuitOpenError } from '@/lib/resilience'

export const GET = withErrorHandler(
  withLogging(
    withTimeout(15000)(async (_request: NextRequest) => {
      const breaker = serviceBreakers.metrics()

      try {
        const metrics = await breaker.exec(() => fetchAllMetrics())

        return NextResponse.json(metrics, {
          status: 200,
          headers: {
            'Cache-Control': 'no-store, max-age=0',
          },
        })
      } catch (err) {
        if (err instanceof CircuitOpenError) {
          return NextResponse.json(
            {
              error: 'Service temporarily unavailable',
              message:
                'Metrics service is experiencing issues. Please try again later.',
              retryAfter: err.nextRetryAt.toISOString(),
            },
            {
              status: 503,
              headers: { 'Cache-Control': 'no-store, max-age=0' },
            }
          )
        }
        throw err
      }
    })
  )
)
