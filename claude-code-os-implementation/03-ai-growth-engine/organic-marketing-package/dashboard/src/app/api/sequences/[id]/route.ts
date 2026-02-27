/**
 * Individual Sequence API Route
 *
 * GET /api/sequences/[id] - Returns a specific email sequence
 * PUT /api/sequences/[id] - Updates an email sequence
 * DELETE /api/sequences/[id] - Deletes an email sequence
 *
 * This endpoint manages individual email sequences including:
 * - Retrieving sequence details
 * - Updating sequence configuration
 * - Deleting sequences
 *
 * @example
 * ```bash
 * # Get a sequence
 * curl -X GET http://localhost:3000/api/sequences/seq_welcome_001
 *
 * # Update a sequence
 * curl -X PUT http://localhost:3000/api/sequences/seq_welcome_001 \
 *   -H "Content-Type: application/json" \
 *   -d '{"status": "paused"}'
 *
 * # Delete a sequence
 * curl -X DELETE http://localhost:3000/api/sequences/seq_welcome_001
 * ```
 *
 * @returns {Sequence} JSON response with sequence
 */

import { NextRequest, NextResponse } from 'next/server'

/**
 * Email sequence interface matching the email automation service
 */
interface EmailSequence {
  id: string
  name: string
  description: string
  template?: string
  status: 'draft' | 'active' | 'paused' | 'archived'
  steps: SequenceStep[]
  trigger?: {
    type: 'lead_created' | 'tag_added' | 'manual' | 'form_submission'
    config?: Record<string, unknown>
  }
  metrics?: {
    subscribersEnrolled: number
    emailsSent: number
    openRate: number
    clickRate: number
    conversionRate: number
  }
  createdAt: string
  updatedAt: string
}

interface SequenceStep {
  id: string
  type: 'email' | 'delay' | 'condition'
  delayDays: number
  sendHour?: number
  templateId?: string
  subject?: string
  config?: Record<string, unknown>
}

/**
 * Mock sequence storage - In production, this would be in a database
 */
const MOCK_SEQUENCES: Record<string, EmailSequence> = {
  seq_welcome_001: {
    id: 'seq_welcome_001',
    name: 'Welcome Series',
    description: '4-email welcome sequence introducing new subscribers to the brand',
    template: 'welcome_series',
    status: 'active',
    steps: [
      {
        id: 'step_1',
        type: 'email',
        delayDays: 0,
        sendHour: 10,
        templateId: 'welcome_series_1',
        subject: "Welcome! Here's what to expect",
      },
      {
        id: 'step_2',
        type: 'email',
        delayDays: 2,
        sendHour: 10,
        templateId: 'welcome_series_2',
        subject: 'Your quick start guide',
      },
      {
        id: 'step_3',
        type: 'email',
        delayDays: 5,
        sendHour: 10,
        templateId: 'welcome_series_3',
        subject: 'See what others are achieving',
      },
      {
        id: 'step_4',
        type: 'email',
        delayDays: 7,
        sendHour: 10,
        templateId: 'welcome_series_4',
        subject: 'Special offer just for you',
      },
    ],
    trigger: {
      type: 'lead_created',
    },
    metrics: {
      subscribersEnrolled: 1247,
      emailsSent: 3891,
      openRate: 42.5,
      clickRate: 12.3,
      conversionRate: 3.8,
    },
    createdAt: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(),
    updatedAt: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
  },
  seq_nurture_001: {
    id: 'seq_nurture_001',
    name: 'Nurture Campaign',
    description: '4-email nurture sequence for non-buyers',
    template: 'nurture_series',
    status: 'active',
    steps: [
      {
        id: 'step_1',
        type: 'email',
        delayDays: 7,
        sendHour: 14,
        templateId: 'nurture_series_1',
        subject: 'Educational content: Getting started',
      },
      {
        id: 'step_2',
        type: 'email',
        delayDays: 14,
        sendHour: 14,
        templateId: 'nurture_series_2',
        subject: 'Success stories from our community',
      },
      {
        id: 'step_3',
        type: 'email',
        delayDays: 21,
        sendHour: 14,
        templateId: 'nurture_series_3',
        subject: 'Exclusive insights just for you',
      },
      {
        id: 'step_4',
        type: 'email',
        delayDays: 35,
        sendHour: 14,
        templateId: 'nurture_series_4',
        subject: 'Limited time offer',
      },
    ],
    trigger: {
      type: 'tag_added',
      config: {
        tag: 'non_buyer',
      },
    },
    metrics: {
      subscribersEnrolled: 892,
      emailsSent: 2456,
      openRate: 38.2,
      clickRate: 9.7,
      conversionRate: 2.1,
    },
    createdAt: new Date(Date.now() - 45 * 24 * 60 * 60 * 1000).toISOString(),
    updatedAt: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
  },
}

/**
 * Route params interface
 */
interface RouteParams {
  params: {
    id: string
  }
}

/**
 * GET /api/sequences/[id]
 *
 * Returns a specific email sequence by ID.
 *
 * @param {NextRequest} _request - Next.js request object (unused)
 * @param {RouteParams} context - Route context with sequence ID
 * @returns {Promise<NextResponse>} JSON response with sequence
 */
export async function GET(
  _request: NextRequest,
  { params }: RouteParams
): Promise<NextResponse> {
  try {
    const { id } = params

    // Find sequence
    const sequence = MOCK_SEQUENCES[id]

    if (!sequence) {
      return NextResponse.json(
        {
          error: 'Sequence not found',
          message: `No sequence found with ID: ${id}`,
          timestamp: new Date().toISOString(),
        },
        { status: 404 }
      )
    }

    return NextResponse.json(
      {
        sequence,
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
      console.error('Sequence fetch error:', error.message)
    }

    return NextResponse.json(
      {
        error: 'Failed to fetch sequence',
        message: error instanceof Error ? error.message : 'Unknown error',
        timestamp: new Date().toISOString(),
      },
      { status: 500 }
    )
  }
}

/**
 * PUT /api/sequences/[id]
 *
 * Updates an email sequence.
 * Validates the update before applying changes.
 *
 * @param {NextRequest} request - Next.js request object with update data
 * @param {RouteParams} context - Route context with sequence ID
 * @returns {Promise<NextResponse>} JSON response with updated sequence
 */
export async function PUT(
  request: NextRequest,
  { params }: RouteParams
): Promise<NextResponse> {
  try {
    const { id } = params
    const body = await request.json()

    // Find sequence
    const sequence = MOCK_SEQUENCES[id]

    if (!sequence) {
      return NextResponse.json(
        {
          error: 'Sequence not found',
          message: `No sequence found with ID: ${id}`,
          timestamp: new Date().toISOString(),
        },
        { status: 404 }
      )
    }

    // Validate status if provided
    if (
      body.status &&
      !['draft', 'active', 'paused', 'archived'].includes(body.status)
    ) {
      return NextResponse.json(
        {
          error: 'Invalid status',
          message: 'Status must be one of: draft, active, paused, archived',
        },
        { status: 400 }
      )
    }

    // Update sequence
    const updatedSequence: EmailSequence = {
      ...sequence,
      ...body,
      id, // Ensure ID cannot be changed
      updatedAt: new Date().toISOString(),
    }

    // Save updated sequence
    MOCK_SEQUENCES[id] = updatedSequence

    return NextResponse.json(
      {
        sequence: updatedSequence,
        message: 'Sequence updated successfully',
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
      console.error('Sequence update error:', error.message)
    }

    return NextResponse.json(
      {
        error: 'Failed to update sequence',
        message: error instanceof Error ? error.message : 'Unknown error',
        timestamp: new Date().toISOString(),
      },
      { status: 500 }
    )
  }
}

/**
 * DELETE /api/sequences/[id]
 *
 * Deletes an email sequence.
 * This is a soft delete - the sequence is archived, not permanently removed.
 *
 * @param {NextRequest} _request - Next.js request object (unused)
 * @param {RouteParams} context - Route context with sequence ID
 * @returns {Promise<NextResponse>} JSON response confirming deletion
 */
export async function DELETE(
  _request: NextRequest,
  { params }: RouteParams
): Promise<NextResponse> {
  try {
    const { id } = params

    // Find sequence
    const sequence = MOCK_SEQUENCES[id]

    if (!sequence) {
      return NextResponse.json(
        {
          error: 'Sequence not found',
          message: `No sequence found with ID: ${id}`,
          timestamp: new Date().toISOString(),
        },
        { status: 404 }
      )
    }

    // Check if sequence has active enrollments
    if (
      sequence.status === 'active' &&
      sequence.metrics &&
      sequence.metrics.subscribersEnrolled > 0
    ) {
      return NextResponse.json(
        {
          error: 'Cannot delete active sequence',
          message:
            'This sequence has active enrollments. Please pause it first or archive instead.',
          timestamp: new Date().toISOString(),
        },
        { status: 400 }
      )
    }

    // Soft delete - archive the sequence
    MOCK_SEQUENCES[id] = {
      ...sequence,
      status: 'archived',
      updatedAt: new Date().toISOString(),
    }

    return NextResponse.json(
      {
        message: 'Sequence deleted successfully',
        id,
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
      console.error('Sequence deletion error:', error.message)
    }

    return NextResponse.json(
      {
        error: 'Failed to delete sequence',
        message: error instanceof Error ? error.message : 'Unknown error',
        timestamp: new Date().toISOString(),
      },
      { status: 500 }
    )
  }
}
