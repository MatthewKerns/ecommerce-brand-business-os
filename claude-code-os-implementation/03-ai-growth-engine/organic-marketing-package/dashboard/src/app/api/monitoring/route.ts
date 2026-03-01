/**
 * Monitoring API Endpoint
 *
 * GET /api/monitoring - Returns the current monitoring snapshot
 * including error rates, service health, circuit breaker states,
 * cache metrics, and recovery statistics.
 */

import { NextResponse } from 'next/server'
import { getErrorMetricsStore } from '@/lib/monitoring/error-metrics'

export async function GET() {
  const store = getErrorMetricsStore()
  const snapshot = store.getSnapshot()

  return NextResponse.json(snapshot, {
    headers: {
      'Cache-Control': 'no-store, max-age=0',
    },
  })
}
