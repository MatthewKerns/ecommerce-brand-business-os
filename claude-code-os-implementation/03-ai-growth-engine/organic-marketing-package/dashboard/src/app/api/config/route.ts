/**
 * Configuration API Route
 *
 * GET /api/config - Returns all service configurations
 * POST /api/config - Updates configuration for a specific service
 *
 * This endpoint manages configuration for:
 * - TikTok (API keys, webhooks, auto-post settings)
 * - Blog Engine (base URL, publishing settings, SEO)
 * - Email Automation (provider, templates, auto-send)
 *
 * @example
 * ```bash
 * # Get all configurations
 * curl -X GET http://localhost:3000/api/config
 *
 * # Update a service configuration
 * curl -X POST http://localhost:3000/api/config \
 *   -H "Content-Type: application/json" \
 *   -d '{"service": "tiktok", "settings": {"autoPost": true}}'
 * ```
 *
 * @returns {AllConfigs | ServiceConfig} JSON response with configurations
 */

import { NextRequest, NextResponse } from 'next/server'
import {
  getAllConfigs,
  updateServiceConfig,
  validateServiceConfig,
} from '@/lib/config-manager'

/**
 * GET /api/config
 *
 * Returns all service configurations.
 *
 * @param {NextRequest} _request - Next.js request object (unused)
 * @returns {Promise<NextResponse>} JSON response with all configurations
 */
export async function GET(_request: NextRequest) {
  try {
    const configs = await getAllConfigs()

    return NextResponse.json(configs, {
      status: 200,
      headers: {
        'Cache-Control': 'no-store, max-age=0',
      },
    })
  } catch (error) {
    if (error instanceof Error) {
      // eslint-disable-next-line no-console
      console.error('Config fetch error:', error.message)
    }

    return NextResponse.json(
      {
        error: 'Failed to fetch configurations',
        message: error instanceof Error ? error.message : 'Unknown error',
        timestamp: new Date().toISOString(),
      },
      { status: 500 }
    )
  }
}

/**
 * POST /api/config
 *
 * Updates configuration for a specific service.
 * Validates the configuration before applying updates.
 *
 * @param {NextRequest} request - Next.js request object with service and settings
 * @returns {Promise<NextResponse>} JSON response with updated configuration
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { service, settings } = body

    // Validate request body
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
      console.error('Config update error:', error.message)
    }

    return NextResponse.json(
      {
        error: 'Failed to update configuration',
        message: error instanceof Error ? error.message : 'Unknown error',
        timestamp: new Date().toISOString(),
      },
      { status: 500 }
    )
  }
}
