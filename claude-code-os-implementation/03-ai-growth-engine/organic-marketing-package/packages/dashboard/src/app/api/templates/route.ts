/**
 * Templates API Route
 *
 * GET /api/templates - Returns all available email templates
 *
 * This endpoint provides access to:
 * - Welcome series templates (4 emails over 7 days)
 * - Nurture series templates (4 emails over 5 weeks)
 * - Custom email templates
 *
 * @example
 * ```bash
 * # Get all templates
 * curl -X GET http://localhost:3000/api/templates
 *
 * # Get templates by category
 * curl -X GET http://localhost:3000/api/templates?category=welcome
 * ```
 *
 * @returns {Template[]} JSON response with templates
 */

import { NextRequest, NextResponse } from 'next/server'

/**
 * Template interface matching the email automation service
 */
interface EmailTemplate {
  id: string
  name: string
  description: string
  category: 'welcome' | 'nurture' | 'promotional' | 'transactional' | 'custom'
  subject: string
  previewText: string
  sendSchedule?: {
    delayDays: number
    sendHour: number
  }
  variables: string[]
  metadata?: {
    tags?: string[]
    author?: string
    version?: string
  }
  createdAt: string
  updatedAt: string
}

/**
 * Mock template data - In production, this would fetch from the email automation service
 */
const MOCK_TEMPLATES: EmailTemplate[] = [
  // Welcome Series Templates
  {
    id: 'welcome_series_1',
    name: 'Welcome Email - Day 0',
    description: 'Initial welcome email sent immediately upon signup',
    category: 'welcome',
    subject: "Welcome! Here's what to expect",
    previewText: 'Thanks for joining us. Here\'s how to get started...',
    sendSchedule: {
      delayDays: 0,
      sendHour: 10,
    },
    variables: [
      'firstName',
      'email',
      'signupSource',
      'brandName',
      'brandMission',
    ],
    metadata: {
      tags: ['onboarding', 'welcome', 'automation'],
      version: '1.0',
    },
    createdAt: new Date(Date.now() - 60 * 24 * 60 * 60 * 1000).toISOString(),
    updatedAt: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(),
  },
  {
    id: 'welcome_series_2',
    name: 'Welcome Email - Day 2',
    description: 'Educational value and quick start guide',
    category: 'welcome',
    subject: 'Your quick start guide',
    previewText: 'Get up to speed quickly with these essential tips...',
    sendSchedule: {
      delayDays: 2,
      sendHour: 10,
    },
    variables: [
      'firstName',
      'email',
      'primaryBenefit',
      'quickWins',
      'resourceLinks',
    ],
    metadata: {
      tags: ['onboarding', 'education', 'automation'],
      version: '1.0',
    },
    createdAt: new Date(Date.now() - 60 * 24 * 60 * 60 * 1000).toISOString(),
    updatedAt: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(),
  },
  {
    id: 'welcome_series_3',
    name: 'Welcome Email - Day 5',
    description: 'Social proof and success stories',
    category: 'welcome',
    subject: 'See what others are achieving',
    previewText: 'Real results from people just like you...',
    sendSchedule: {
      delayDays: 5,
      sendHour: 10,
    },
    variables: [
      'firstName',
      'email',
      'testimonials',
      'caseStudies',
      'communitySize',
    ],
    metadata: {
      tags: ['social-proof', 'testimonials', 'automation'],
      version: '1.0',
    },
    createdAt: new Date(Date.now() - 60 * 24 * 60 * 60 * 1000).toISOString(),
    updatedAt: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(),
  },
  {
    id: 'welcome_series_4',
    name: 'Welcome Email - Day 7',
    description: 'First purchase incentive',
    category: 'welcome',
    subject: 'Special offer just for you',
    previewText: 'Exclusive discount for new subscribers...',
    sendSchedule: {
      delayDays: 7,
      sendHour: 10,
    },
    variables: [
      'firstName',
      'email',
      'discountCode',
      'discountAmount',
      'expiryDate',
    ],
    metadata: {
      tags: ['conversion', 'offer', 'automation'],
      version: '1.0',
    },
    createdAt: new Date(Date.now() - 60 * 24 * 60 * 60 * 1000).toISOString(),
    updatedAt: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(),
  },
  // Nurture Series Templates
  {
    id: 'nurture_series_1',
    name: 'Nurture Email - Week 1',
    description: 'Educational foundation for non-buyers',
    category: 'nurture',
    subject: 'Educational content: Getting started',
    previewText: 'Learn the fundamentals to achieve your goals...',
    sendSchedule: {
      delayDays: 7,
      sendHour: 14,
    },
    variables: [
      'firstName',
      'email',
      'educationalContent',
      'topicArea',
      'resources',
    ],
    metadata: {
      tags: ['nurture', 'education', 'automation'],
      version: '1.0',
    },
    createdAt: new Date(Date.now() - 60 * 24 * 60 * 60 * 1000).toISOString(),
    updatedAt: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(),
  },
  {
    id: 'nurture_series_2',
    name: 'Nurture Email - Week 2',
    description: 'Success stories and social proof',
    category: 'nurture',
    subject: 'Success stories from our community',
    previewText: 'See how others transformed their results...',
    sendSchedule: {
      delayDays: 14,
      sendHour: 14,
    },
    variables: [
      'firstName',
      'email',
      'successStories',
      'beforeAfter',
      'communityHighlights',
    ],
    metadata: {
      tags: ['nurture', 'social-proof', 'automation'],
      version: '1.0',
    },
    createdAt: new Date(Date.now() - 60 * 24 * 60 * 60 * 1000).toISOString(),
    updatedAt: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(),
  },
  {
    id: 'nurture_series_3',
    name: 'Nurture Email - Week 3',
    description: 'Exclusive value and insights',
    category: 'nurture',
    subject: 'Exclusive insights just for you',
    previewText: 'Insider knowledge to accelerate your progress...',
    sendSchedule: {
      delayDays: 21,
      sendHour: 14,
    },
    variables: [
      'firstName',
      'email',
      'exclusiveContent',
      'insights',
      'expertTips',
    ],
    metadata: {
      tags: ['nurture', 'value', 'automation'],
      version: '1.0',
    },
    createdAt: new Date(Date.now() - 60 * 24 * 60 * 60 * 1000).toISOString(),
    updatedAt: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(),
  },
  {
    id: 'nurture_series_4',
    name: 'Nurture Email - Week 5',
    description: 'Special offer and conversion push',
    category: 'nurture',
    subject: 'Limited time offer',
    previewText: 'Don\'t miss this exclusive opportunity...',
    sendSchedule: {
      delayDays: 35,
      sendHour: 14,
    },
    variables: [
      'firstName',
      'email',
      'offerDetails',
      'urgency',
      'benefitsSummary',
    ],
    metadata: {
      tags: ['nurture', 'conversion', 'offer', 'automation'],
      version: '1.0',
    },
    createdAt: new Date(Date.now() - 60 * 24 * 60 * 60 * 1000).toISOString(),
    updatedAt: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(),
  },
]

/**
 * GET /api/templates
 *
 * Returns all available email templates with optional filtering.
 *
 * @param {NextRequest} request - Next.js request object with optional query params
 * @returns {Promise<NextResponse>} JSON response with templates
 */
export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams
    const categoryFilter = searchParams.get('category')
    const searchQuery = searchParams.get('search')
    const tagsFilter = searchParams.get('tags')

    // Filter templates based on query parameters
    let templates = [...MOCK_TEMPLATES]

    if (categoryFilter) {
      templates = templates.filter((tmpl) => tmpl.category === categoryFilter)
    }

    if (searchQuery) {
      const query = searchQuery.toLowerCase()
      templates = templates.filter(
        (tmpl) =>
          tmpl.name.toLowerCase().includes(query) ||
          tmpl.description.toLowerCase().includes(query) ||
          tmpl.subject.toLowerCase().includes(query)
      )
    }

    if (tagsFilter) {
      const tags = tagsFilter.split(',').map((t) => t.trim().toLowerCase())
      templates = templates.filter((tmpl) =>
        tmpl.metadata?.tags?.some((tag) =>
          tags.includes(tag.toLowerCase())
        )
      )
    }

    // Group templates by category for easier consumption
    const groupedTemplates = templates.reduce(
      (acc, template) => {
        const category = template.category
        if (!acc[category]) {
          acc[category] = []
        }
        acc[category].push(template)
        return acc
      },
      {} as Record<string, EmailTemplate[]>
    )

    return NextResponse.json(
      {
        templates,
        grouped: groupedTemplates,
        total: templates.length,
        categories: {
          welcome: templates.filter((t) => t.category === 'welcome').length,
          nurture: templates.filter((t) => t.category === 'nurture').length,
          promotional: templates.filter((t) => t.category === 'promotional')
            .length,
          transactional: templates.filter(
            (t) => t.category === 'transactional'
          ).length,
          custom: templates.filter((t) => t.category === 'custom').length,
        },
        timestamp: new Date().toISOString(),
      },
      {
        status: 200,
        headers: {
          'Cache-Control': 'public, max-age=3600', // Templates can be cached for 1 hour
        },
      }
    )
  } catch (error) {
    if (error instanceof Error) {
      // eslint-disable-next-line no-console
      console.error('Templates fetch error:', error.message)
    }

    return NextResponse.json(
      {
        error: 'Failed to fetch templates',
        message: error instanceof Error ? error.message : 'Unknown error',
        timestamp: new Date().toISOString(),
      },
      { status: 500 }
    )
  }
}
