/**
 * Analytics API Route
 *
 * GET /api/analytics - Returns email sequence analytics and performance metrics
 *
 * This endpoint provides:
 * - Sequence performance metrics (open rate, click rate, conversion rate)
 * - Email event data (opens, clicks, conversions)
 * - Time-series analytics
 * - Funnel analysis
 * - Device and location breakdowns
 *
 * @example
 * ```bash
 * # Get all analytics
 * curl -X GET http://localhost:3000/api/analytics
 *
 * # Get analytics for a specific sequence
 * curl -X GET http://localhost:3000/api/analytics?sequenceId=seq_welcome_001
 *
 * # Get analytics for a time range
 * curl -X GET "http://localhost:3000/api/analytics?startDate=2024-01-01&endDate=2024-01-31"
 * ```
 *
 * @returns {Analytics} JSON response with analytics data
 */

import { NextRequest, NextResponse } from 'next/server'

/**
 * Analytics interfaces matching the email automation service
 */
interface SequenceMetrics {
  sequenceId: string
  sequenceName: string
  period: {
    startDate: string
    endDate: string
  }
  summary: {
    subscribersEnrolled: number
    emailsSent: number
    opens: number
    clicks: number
    conversions: number
    bounces: number
    unsubscribes: number
  }
  rates: {
    openRate: number
    clickRate: number
    clickToOpenRate: number
    conversionRate: number
    bounceRate: number
    unsubscribeRate: number
  }
  stepMetrics: StepMetrics[]
  timeSeries?: TimeSeriesDataPoint[]
  funnel?: FunnelStep[]
  deviceBreakdown?: DeviceBreakdown
  topLinks?: TopLink[]
}

interface StepMetrics {
  stepId: string
  stepName: string
  position: number
  sent: number
  opens: number
  clicks: number
  conversions: number
  openRate: number
  clickRate: number
  conversionRate: number
}

interface TimeSeriesDataPoint {
  date: string
  sent: number
  opens: number
  clicks: number
  conversions: number
}

interface FunnelStep {
  name: string
  count: number
  rate: number
  dropoff?: number
}

interface DeviceBreakdown {
  desktop: number
  mobile: number
  tablet: number
  unknown: number
}

interface TopLink {
  url: string
  clicks: number
  uniqueClicks: number
  clickRate: number
}

/**
 * Mock analytics data - In production, this would fetch from the email automation service
 */
const MOCK_ANALYTICS: Record<string, SequenceMetrics> = {
  seq_welcome_001: {
    sequenceId: 'seq_welcome_001',
    sequenceName: 'Welcome Series',
    period: {
      startDate: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(),
      endDate: new Date().toISOString(),
    },
    summary: {
      subscribersEnrolled: 1247,
      emailsSent: 3891,
      opens: 1654,
      clicks: 479,
      conversions: 148,
      bounces: 23,
      unsubscribes: 12,
    },
    rates: {
      openRate: 42.5,
      clickRate: 12.3,
      clickToOpenRate: 29.0,
      conversionRate: 3.8,
      bounceRate: 0.6,
      unsubscribeRate: 0.3,
    },
    stepMetrics: [
      {
        stepId: 'step_1',
        stepName: 'Welcome Email - Day 0',
        position: 1,
        sent: 1247,
        opens: 623,
        clicks: 187,
        conversions: 31,
        openRate: 50.0,
        clickRate: 15.0,
        conversionRate: 2.5,
      },
      {
        stepId: 'step_2',
        stepName: 'Quick Start Guide - Day 2',
        position: 2,
        sent: 1235,
        opens: 519,
        clicks: 148,
        conversions: 37,
        openRate: 42.0,
        clickRate: 12.0,
        conversionRate: 3.0,
      },
      {
        stepId: 'step_3',
        stepName: 'Social Proof - Day 5',
        position: 3,
        sent: 1223,
        opens: 367,
        clicks: 98,
        conversions: 43,
        openRate: 30.0,
        clickRate: 8.0,
        conversionRate: 3.5,
      },
      {
        stepId: 'step_4',
        stepName: 'Special Offer - Day 7',
        position: 4,
        sent: 1186,
        opens: 145,
        clicks: 46,
        conversions: 37,
        openRate: 12.2,
        clickRate: 3.9,
        conversionRate: 3.1,
      },
    ],
    timeSeries: [
      {
        date: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000)
          .toISOString()
          .split('T')[0],
        sent: 542,
        opens: 230,
        clicks: 67,
        conversions: 21,
      },
      {
        date: new Date(Date.now() - 6 * 24 * 60 * 60 * 1000)
          .toISOString()
          .split('T')[0],
        sent: 498,
        opens: 211,
        clicks: 61,
        conversions: 19,
      },
      {
        date: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000)
          .toISOString()
          .split('T')[0],
        sent: 587,
        opens: 249,
        clicks: 72,
        conversions: 22,
      },
      {
        date: new Date(Date.now() - 4 * 24 * 60 * 60 * 1000)
          .toISOString()
          .split('T')[0],
        sent: 623,
        opens: 265,
        clicks: 77,
        conversions: 24,
      },
      {
        date: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000)
          .toISOString()
          .split('T')[0],
        sent: 612,
        opens: 260,
        clicks: 75,
        conversions: 23,
      },
      {
        date: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000)
          .toISOString()
          .split('T')[0],
        sent: 534,
        opens: 227,
        clicks: 66,
        conversions: 20,
      },
      {
        date: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000)
          .toISOString()
          .split('T')[0],
        sent: 495,
        opens: 210,
        clicks: 61,
        conversions: 19,
      },
    ],
    funnel: [
      { name: 'Emails Sent', count: 3891, rate: 100.0 },
      { name: 'Emails Opened', count: 1654, rate: 42.5, dropoff: 57.5 },
      { name: 'Links Clicked', count: 479, rate: 12.3, dropoff: 71.0 },
      { name: 'Conversions', count: 148, rate: 3.8, dropoff: 69.1 },
    ],
    deviceBreakdown: {
      desktop: 1142,
      mobile: 423,
      tablet: 67,
      unknown: 22,
    },
    topLinks: [
      {
        url: 'https://example.com/getting-started',
        clicks: 187,
        uniqueClicks: 165,
        clickRate: 39.0,
      },
      {
        url: 'https://example.com/case-studies',
        clicks: 98,
        uniqueClicks: 87,
        clickRate: 20.5,
      },
      {
        url: 'https://example.com/special-offer',
        clicks: 46,
        uniqueClicks: 42,
        clickRate: 9.6,
      },
      {
        url: 'https://example.com/blog',
        clicks: 148,
        uniqueClicks: 123,
        clickRate: 30.9,
      },
    ],
  },
  seq_nurture_001: {
    sequenceId: 'seq_nurture_001',
    sequenceName: 'Nurture Campaign',
    period: {
      startDate: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(),
      endDate: new Date().toISOString(),
    },
    summary: {
      subscribersEnrolled: 892,
      emailsSent: 2456,
      opens: 938,
      clicks: 238,
      conversions: 52,
      bounces: 15,
      unsubscribes: 8,
    },
    rates: {
      openRate: 38.2,
      clickRate: 9.7,
      clickToOpenRate: 25.4,
      conversionRate: 2.1,
      bounceRate: 0.6,
      unsubscribeRate: 0.3,
    },
    stepMetrics: [
      {
        stepId: 'step_1',
        stepName: 'Educational Foundation - Week 1',
        position: 1,
        sent: 892,
        opens: 356,
        clicks: 89,
        conversions: 14,
        openRate: 39.9,
        clickRate: 10.0,
        conversionRate: 1.6,
      },
      {
        stepId: 'step_2',
        stepName: 'Success Stories - Week 2',
        position: 2,
        sent: 878,
        opens: 334,
        clicks: 83,
        conversions: 18,
        openRate: 38.0,
        clickRate: 9.5,
        conversionRate: 2.0,
      },
      {
        stepId: 'step_3',
        stepName: 'Exclusive Value - Week 3',
        position: 3,
        sent: 860,
        opens: 318,
        clicks: 79,
        conversions: 16,
        openRate: 37.0,
        clickRate: 9.2,
        conversionRate: 1.9,
      },
      {
        stepId: 'step_4',
        stepName: 'Special Offer - Week 5',
        position: 4,
        sent: 826,
        opens: 230,
        clicks: 37,
        conversions: 4,
        openRate: 27.8,
        clickRate: 4.5,
        conversionRate: 0.5,
      },
    ],
    timeSeries: [
      {
        date: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000)
          .toISOString()
          .split('T')[0],
        sent: 342,
        opens: 131,
        clicks: 33,
        conversions: 7,
      },
      {
        date: new Date(Date.now() - 6 * 24 * 60 * 60 * 1000)
          .toISOString()
          .split('T')[0],
        sent: 318,
        opens: 121,
        clicks: 30,
        conversions: 6,
      },
      {
        date: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000)
          .toISOString()
          .split('T')[0],
        sent: 367,
        opens: 140,
        clicks: 35,
        conversions: 8,
      },
      {
        date: new Date(Date.now() - 4 * 24 * 60 * 60 * 1000)
          .toISOString()
          .split('T')[0],
        sent: 389,
        opens: 149,
        clicks: 37,
        conversions: 8,
      },
      {
        date: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000)
          .toISOString()
          .split('T')[0],
        sent: 398,
        opens: 152,
        clicks: 38,
        conversions: 8,
      },
      {
        date: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000)
          .toISOString()
          .split('T')[0],
        sent: 356,
        opens: 136,
        clicks: 34,
        conversions: 7,
      },
      {
        date: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000)
          .toISOString()
          .split('T')[0],
        sent: 286,
        opens: 109,
        clicks: 31,
        conversions: 8,
      },
    ],
    funnel: [
      { name: 'Emails Sent', count: 2456, rate: 100.0 },
      { name: 'Emails Opened', count: 938, rate: 38.2, dropoff: 61.8 },
      { name: 'Links Clicked', count: 238, rate: 9.7, dropoff: 74.6 },
      { name: 'Conversions', count: 52, rate: 2.1, dropoff: 78.2 },
    ],
    deviceBreakdown: {
      desktop: 612,
      mobile: 267,
      tablet: 45,
      unknown: 14,
    },
    topLinks: [
      {
        url: 'https://example.com/education',
        clicks: 89,
        uniqueClicks: 78,
        clickRate: 37.4,
      },
      {
        url: 'https://example.com/success-stories',
        clicks: 83,
        uniqueClicks: 72,
        clickRate: 34.9,
      },
      {
        url: 'https://example.com/insights',
        clicks: 79,
        uniqueClicks: 68,
        clickRate: 33.2,
      },
      {
        url: 'https://example.com/offer',
        clicks: 37,
        uniqueClicks: 34,
        clickRate: 15.5,
      },
    ],
  },
}

/**
 * GET /api/analytics
 *
 * Returns email sequence analytics with optional filtering.
 *
 * @param {NextRequest} request - Next.js request object with optional query params
 * @returns {Promise<NextResponse>} JSON response with analytics
 */
export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams
    const sequenceId = searchParams.get('sequenceId')
    const startDate = searchParams.get('startDate')
    const endDate = searchParams.get('endDate')

    // If a specific sequence is requested
    if (sequenceId) {
      const analytics = MOCK_ANALYTICS[sequenceId]

      if (!analytics) {
        return NextResponse.json(
          {
            error: 'Analytics not found',
            message: `No analytics found for sequence: ${sequenceId}`,
            timestamp: new Date().toISOString(),
          },
          { status: 404 }
        )
      }

      // Filter time series data if date range is provided
      let filteredAnalytics = { ...analytics }
      if (startDate || endDate) {
        const start = startDate ? new Date(startDate) : null
        const end = endDate ? new Date(endDate) : null

        if (filteredAnalytics.timeSeries) {
          filteredAnalytics.timeSeries = filteredAnalytics.timeSeries.filter(
            (point) => {
              const pointDate = new Date(point.date)
              if (start && pointDate < start) return false
              if (end && pointDate > end) return false
              return true
            }
          )
        }
      }

      return NextResponse.json(
        {
          analytics: filteredAnalytics,
          timestamp: new Date().toISOString(),
        },
        {
          status: 200,
          headers: {
            'Cache-Control': 'no-store, max-age=0',
          },
        }
      )
    }

    // Return all analytics
    const allAnalytics = Object.values(MOCK_ANALYTICS)

    // Calculate aggregate metrics
    const aggregate = {
      totalEnrolled: allAnalytics.reduce(
        (sum, a) => sum + a.summary.subscribersEnrolled,
        0
      ),
      totalSent: allAnalytics.reduce((sum, a) => sum + a.summary.emailsSent, 0),
      totalOpens: allAnalytics.reduce((sum, a) => sum + a.summary.opens, 0),
      totalClicks: allAnalytics.reduce((sum, a) => sum + a.summary.clicks, 0),
      totalConversions: allAnalytics.reduce(
        (sum, a) => sum + a.summary.conversions,
        0
      ),
    }

    const aggregateRates = {
      openRate:
        aggregate.totalSent > 0
          ? (aggregate.totalOpens / aggregate.totalSent) * 100
          : 0,
      clickRate:
        aggregate.totalSent > 0
          ? (aggregate.totalClicks / aggregate.totalSent) * 100
          : 0,
      conversionRate:
        aggregate.totalSent > 0
          ? (aggregate.totalConversions / aggregate.totalSent) * 100
          : 0,
    }

    return NextResponse.json(
      {
        sequences: allAnalytics,
        aggregate: {
          ...aggregate,
          rates: aggregateRates,
        },
        total: allAnalytics.length,
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
      console.error('Analytics fetch error:', error.message)
    }

    return NextResponse.json(
      {
        error: 'Failed to fetch analytics',
        message: error instanceof Error ? error.message : 'Unknown error',
        timestamp: new Date().toISOString(),
      },
      { status: 500 }
    )
  }
}
