/**
 * Service-Specific Configuration API Route
 *
 * GET /api/config/[service] - Returns configuration for a specific service
 * PUT /api/config/[service] - Updates configuration for a specific service
 * DELETE /api/config/[service] - Resets configuration to defaults
 *
 * Supported services:
 * - tiktok: TikTok marketing configuration
 * - blog: Blog Engine configuration
 * - email: Email Automation configuration
 *
 * @example
 * ```bash
 * # Get TikTok configuration
 * curl -X GET http://localhost:3000/api/config/tiktok
 *
 * # Update TikTok configuration
 * curl -X PUT http://localhost:3000/api/config/tiktok \
 *   -H "Content-Type: application/json" \
 *   -d '{"autoPost": true, "refreshInterval": 7200}'
 *
 * # Reset TikTok configuration to defaults
 * curl -X DELETE http://localhost:3000/api/config/tiktok
 * ```
 *
 * @returns {ServiceConfig} JSON response with service configuration
 */

import { NextRequest, NextResponse } from 'next/server'
import {
  getServiceConfig,
  updateServiceConfig,
  resetServiceConfig,
  validateServiceConfig,
} from '@/lib/config-manager'

/**
 * GET /api/config/[service]
 *
 * Returns configuration for a specific service.
 *
 * @param {NextRequest} _request - Next.js request object (unused)
 * @param {Object} params - Route parameters
 * @param {string} params.service - Service name (tiktok, blog, email)
 * @returns {Promise<NextResponse>} JSON response with service configuration
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

    const config = await getServiceConfig(service)

    // Return 404 if service is unknown (status will be 'error')
    if (config.status === 'error' && Object.keys(config.settings).length === 0) {
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
        ...config,
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
    if (error instanceof Error) {
      // eslint-disable-next-line no-console
      console.error('Service config fetch error:', error.message)
    }

    return NextResponse.json(
      {
        error: 'Failed to fetch service configuration',
        message: error instanceof Error ? error.message : 'Unknown error',
        timestamp: new Date().toISOString(),
      },
      { status: 500 }
    )
  }
}

/**
 * PUT /api/config/[service]
 *
 * Updates configuration for a specific service.
 * Validates the configuration before applying updates.
 *
 * @param {NextRequest} request - Next.js request object with settings
 * @param {Object} params - Route parameters
 * @param {string} params.service - Service name (tiktok, blog, email)
 * @returns {Promise<NextResponse>} JSON response with updated configuration
 */
export async function PUT(
  request: NextRequest,
  { params }: { params: { service: string } }
) {
  try {
    const { service } = params
    const settings = await request.json()

    if (!service) {
      return NextResponse.json(
        {
          error: 'Service name is required',
          message: 'Please specify a service: tiktok, blog, or email',
        },
        { status: 400 }
      )
    }

    if (!settings || typeof settings !== 'object') {
      return NextResponse.json(
        {
          error: 'Settings object is required',
          message: 'Please provide a valid settings object',
        },
        { status: 400 }
      )
    }

    // Validate configuration settings
    try {
      validateServiceConfig(service, settings)
    } catch (validationError) {
      return NextResponse.json(
        {
          error: 'Invalid configuration',
          message:
            validationError instanceof Error
              ? validationError.message
              : 'Configuration validation failed',
        },
        { status: 400 }
      )
    }

    // Update configuration
    const updatedConfig = await updateServiceConfig(service, settings)

    return NextResponse.json(
      {
        ...updatedConfig,
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
    if (error instanceof Error) {
      // eslint-disable-next-line no-console
      console.error('Service config update error:', error.message)
    }

    return NextResponse.json(
      {
        error: 'Failed to update service configuration',
        message: error instanceof Error ? error.message : 'Unknown error',
        timestamp: new Date().toISOString(),
      },
      { status: 500 }
    )
  }
}

/**
 * DELETE /api/config/[service]
 *
 * Resets configuration for a specific service to defaults.
 *
 * @param {NextRequest} _request - Next.js request object (unused)
 * @param {Object} params - Route parameters
 * @param {string} params.service - Service name (tiktok, blog, email)
 * @returns {Promise<NextResponse>} JSON response with reset configuration
 */
export async function DELETE(
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

    const resetConfig = await resetServiceConfig(service)

    return NextResponse.json(
      {
        ...resetConfig,
        timestamp: new Date().toISOString(),
        message: `Configuration for ${service} has been reset to defaults`,
      },
      {
        status: 200,
        headers: {
          'Cache-Control': 'no-store, max-age=0',
        },
      }
    )
  } catch (error) {
    if (error instanceof Error) {
      // eslint-disable-next-line no-console
      console.error('Service config reset error:', error.message)
    }

    return NextResponse.json(
      {
        error: 'Failed to reset service configuration',
        message: error instanceof Error ? error.message : 'Unknown error',
        timestamp: new Date().toISOString(),
      },
      { status: 500 }
    )
  }
}
