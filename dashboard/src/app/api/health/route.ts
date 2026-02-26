/**
 * Health Check API Route
 *
 * GET /api/health - Returns system health status
 *
 * This endpoint checks the health of all system components including:
 * - Environment configuration
 * - External services (TikTok, Blog, Email)
 * - Internal services (Python Agents, Database, Cache)
 *
 * @example
 * ```bash
 * curl -X GET http://localhost:3000/api/health
 * ```
 *
 * @returns {SystemHealth} JSON response with system health status
 */

import { NextRequest, NextResponse } from 'next/server'
import { checkSystemHealth, checkServiceHealth } from '@/lib/health-checker'

/**
 * GET /api/health
 *
 * Returns comprehensive system health status.
 * Optionally filter by service using ?service=serviceName query parameter.
 *
 * @param {NextRequest} request - Next.js request object
 * @returns {Promise<NextResponse>} JSON response with health status
 */
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const serviceName = searchParams.get('service')

    // Check specific service if requested
    if (serviceName) {
      const serviceHealth = await checkServiceHealth(serviceName)

      return NextResponse.json(
        {
          service: serviceHealth,
          timestamp: new Date().toISOString(),
        },
        { status: serviceHealth.status === 'unhealthy' ? 503 : 200 }
      )
    }

    // Check all system health
    const health = await checkSystemHealth()

    // Return 503 if system is unhealthy, 200 otherwise
    const statusCode = health.status === 'unhealthy' ? 503 : 200

    return NextResponse.json(health, {
      status: statusCode,
      headers: {
        'Cache-Control': 'no-store, max-age=0',
      },
    })
  } catch (error) {
    // Log error but don't expose internal details
    if (error instanceof Error) {
      // eslint-disable-next-line no-console
      console.error('Health check error:', error.message)
    }

    return NextResponse.json(
      {
        status: 'unhealthy',
        timestamp: new Date().toISOString(),
        error: 'Health check failed',
        message: error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 503 }
    )
  }
}
