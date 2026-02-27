/**
 * Sequences API Route
 *
 * GET /api/sequences - Returns all email sequences with metrics
 * POST /api/sequences - Creates a new email sequence
 *
 * This endpoint manages email sequences for:
 * - Welcome series
 * - Nurture campaigns
 * - Custom automated sequences
 *
 * @example
 * ```bash
 * # Get all sequences
 * curl -X GET http://localhost:3000/api/sequences
 *
 * # Create a new sequence
 * curl -X POST http://localhost:3000/api/sequences \
 *   -H "Content-Type: application/json" \
 *   -d '{"name": "Welcome Series", "template": "welcome_series", "status": "draft"}'
 * ```
 *
 * @returns {Sequence[]} JSON response with sequences
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

interface SequenceListFilter {
  status?: 'draft' | 'active' | 'paused' | 'archived'
  template?: string
  search?: string
}

/**
 * Mock sequence data - In production, this would fetch from the email automation service
 */
const MOCK_SEQUENCES: EmailSequence[] = [
  {
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
        subject: 'Welcome! Here\'s what to expect',
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
  {
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
  {
    id: 'seq_custom_001',
    name: 'Product Launch',
    description: 'Custom sequence for new product announcements',
    status: 'draft',
    steps: [
      {
        id: 'step_1',
        type: 'email',
        delayDays: 0,
        sendHour: 9,
        subject: 'Coming soon: Something exciting',
      },
    ],
    trigger: {
      type: 'manual',
    },
    metrics: {
      subscribersEnrolled: 0,
      emailsSent: 0,
      openRate: 0,
      clickRate: 0,
      conversionRate: 0,
    },
    createdAt: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
    updatedAt: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
  },
]

/**
 * GET /api/sequences
 *
 * Returns all email sequences with optional filtering.
 *
 * @param {NextRequest} request - Next.js request object with optional query params
 * @returns {Promise<NextResponse>} JSON response with sequences
 */
export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams
    const statusFilter = searchParams.get('status') as SequenceListFilter['status']
    const templateFilter = searchParams.get('template')
    const searchQuery = searchParams.get('search')

    // Filter sequences based on query parameters
    let sequences = [...MOCK_SEQUENCES]

    if (statusFilter) {
      sequences = sequences.filter((seq) => seq.status === statusFilter)
    }

    if (templateFilter) {
      sequences = sequences.filter((seq) => seq.template === templateFilter)
    }

    if (searchQuery) {
      const query = searchQuery.toLowerCase()
      sequences = sequences.filter(
        (seq) =>
          seq.name.toLowerCase().includes(query) ||
          seq.description.toLowerCase().includes(query)
      )
    }

    // Sort by most recently updated
    sequences.sort(
      (a, b) =>
        new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime()
    )

    return NextResponse.json(
      {
        sequences,
        total: sequences.length,
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
      console.error('Sequences fetch error:', error.message)
    }

    return NextResponse.json(
      {
        error: 'Failed to fetch sequences',
        message: error instanceof Error ? error.message : 'Unknown error',
        timestamp: new Date().toISOString(),
      },
      { status: 500 }
    )
  }
}

/**
 * POST /api/sequences
 *
 * Creates a new email sequence.
 * Validates the sequence configuration before creating.
 *
 * @param {NextRequest} request - Next.js request object with sequence data
 * @returns {Promise<NextResponse>} JSON response with created sequence
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { name, description, template, status, steps, trigger } = body

    // Validate request body
    if (!name || typeof name !== 'string') {
      return NextResponse.json(
        {
          error: 'Name is required',
          message: 'Please provide a valid sequence name',
        },
        { status: 400 }
      )
    }

    if (status && !['draft', 'active', 'paused', 'archived'].includes(status)) {
      return NextResponse.json(
        {
          error: 'Invalid status',
          message: 'Status must be one of: draft, active, paused, archived',
        },
        { status: 400 }
      )
    }

    // Create new sequence
    const newSequence: EmailSequence = {
      id: `seq_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      name,
      description: description || '',
      template,
      status: status || 'draft',
      steps: steps || [],
      trigger,
      metrics: {
        subscribersEnrolled: 0,
        emailsSent: 0,
        openRate: 0,
        clickRate: 0,
        conversionRate: 0,
      },
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    }

    // In production, this would save to the email automation service
    // For now, we'll just return the created sequence
    MOCK_SEQUENCES.push(newSequence)

    return NextResponse.json(
      {
        sequence: newSequence,
        message: 'Sequence created successfully',
        timestamp: new Date().toISOString(),
      },
      {
        status: 201,
        headers: {
          'Cache-Control': 'no-store, max-age=0',
        },
      }
    )
  } catch (error) {
    if (error instanceof Error) {
      // eslint-disable-next-line no-console
      console.error('Sequence creation error:', error.message)
    }

    return NextResponse.json(
      {
        error: 'Failed to create sequence',
        message: error instanceof Error ? error.message : 'Unknown error',
        timestamp: new Date().toISOString(),
      },
      { status: 500 }
    )
  }
}
