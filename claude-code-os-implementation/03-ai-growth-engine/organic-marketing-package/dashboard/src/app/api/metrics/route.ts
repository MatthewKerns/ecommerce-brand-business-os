/**
 * Metrics API Route
 *
 * GET /api/metrics - Returns aggregated metrics from all services
 *
 * This endpoint fetches and aggregates metrics from:
 * - TikTok (views, engagement, followers, videos posted)
 * - Blog Engine (page views, unique visitors, posts, avg time on page)
 * - Email Automation (subscribers, emails sent, open rate, click rate)
 *
 * @example
 * ```bash
 * curl -X GET http://localhost:3000/api/metrics
 * ```
 *
 * @returns {AggregatedMetrics} JSON response with aggregated metrics
 */

import { NextRequest, NextResponse } from 'next/server'
import { fetchAllMetrics } from '@/lib/metrics-fetcher'

/**
 * GET /api/metrics
 *
 * Returns comprehensive metrics aggregated from all marketing services.
 * Includes summary metrics like total reach, engagement, revenue, and conversions.
 *
 * @param {NextRequest} _request - Next.js request object (unused)
 * @returns {Promise<NextResponse>} JSON response with aggregated metrics
 */
export async function GET(_request: NextRequest) {
  try {
    const metrics = await fetchAllMetrics()

    return NextResponse.json(metrics, {
      status: 200,
      headers: {
        'Cache-Control': 'no-store, max-age=0',
      },
    })
  } catch (error) {
    // Log error but don't expose internal details
    if (error instanceof Error) {
      // eslint-disable-next-line no-console
      console.error('Metrics fetch error:', error.message)
    }

    return NextResponse.json(
      {
        error: 'Failed to fetch metrics',
        message: error instanceof Error ? error.message : 'Unknown error',
        timestamp: new Date().toISOString(),
      },
      { status: 500 }
    )
  }
}
