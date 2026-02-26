/**
 * Service-Specific Metrics API Route
 *
 * GET /api/metrics/[service] - Returns metrics for a specific service
 *
 * Supported services:
 * - tiktok: TikTok marketing metrics
 * - blog: Blog Engine metrics
 * - email: Email Automation metrics
 *
 * @example
 * ```bash
 * curl -X GET http://localhost:3000/api/metrics/tiktok
 * curl -X GET http://localhost:3000/api/metrics/blog
 * curl -X GET http://localhost:3000/api/metrics/email
 * ```
 *
 * @returns {ServiceMetrics} JSON response with service-specific metrics
 */

import { NextRequest, NextResponse } from 'next/server'
import { fetchServiceMetrics } from '@/lib/metrics-fetcher'

/**
 * GET /api/metrics/[service]
 *
 * Returns metrics for a specific marketing service.
 *
 * @param {NextRequest} _request - Next.js request object (unused)
 * @param {Object} params - Route parameters
 * @param {string} params.service - Service name (tiktok, blog, email)
 * @returns {Promise<NextResponse>} JSON response with service metrics
 */
export async function GET(
  _request: NextRequest,
  { params }: { params: { service: string } }
) {
  try {
    const { service } = params

    if (!service) {
      return NextResponse.json(
        {
          error: 'Service name is required',
          message: 'Please specify a service: tiktok, blog, or email',
        },
        { status: 400 }
      )
    }

    const metrics = await fetchServiceMetrics(service)

    // Return 404 if service is unknown (status will be 'error')
    if (metrics.status === 'error' && Object.keys(metrics.metrics).length === 0) {
      return NextResponse.json(
        {
          error: 'Service not found',
          message: `Unknown service: ${service}. Available services: tiktok, blog, email`,
          service,
        },
        { status: 404 }
      )
    }

    return NextResponse.json(
      {
        ...metrics,
        timestamp: new Date().toISOString(),
      },
      {
        status: 200,
        headers: {
          'Cache-Control': 'no-store, max-age=0',
        },
      }
    )
  } catch (error) {
    // Log error but don't expose internal details
    if (error instanceof Error) {
      // eslint-disable-next-line no-console
      console.error('Service metrics fetch error:', error.message)
    }

    return NextResponse.json(
      {
        error: 'Failed to fetch service metrics',
        message: error instanceof Error ? error.message : 'Unknown error',
        timestamp: new Date().toISOString(),
      },
      { status: 500 }
    )
  }
}
