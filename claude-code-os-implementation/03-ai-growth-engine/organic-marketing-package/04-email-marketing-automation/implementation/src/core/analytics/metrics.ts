/**
 * Metrics Aggregation Engine - Performance reports and analytics
 *
 * Features:
 * - Aggregate metrics across sequences and campaigns
 * - Time-series analytics with configurable intervals
 * - Funnel analytics for email engagement
 * - Cohort analysis for user behavior
 * - Device and location breakdowns
 * - Top performing links analysis
 * - Performance report generation
 */

import type { IAnalyticsStorage } from './storage';
import type {
  EmailEvent,
  EmailEventFilter,
  EmailMetrics,
  SequenceMetrics,
  CampaignMetrics,
  VariantMetrics,
  TimeInterval,
  TimeSeriesMetrics,
  TimeSeriesDataPoint,
  EmailFunnel,
  FunnelStep,
  CohortMetrics,
  DeviceBreakdown,
  LocationBreakdown,
  TopLink,
  EmailEventType,
} from './models';

// ============================================================
// Types
// ============================================================

export interface PerformanceReportOptions {
  sequenceId?: string;
  campaignId?: string;
  variantId?: string;
  startDate?: Date;
  endDate?: Date;
  includeTimeSeries?: boolean;
  timeInterval?: TimeInterval;
  includeFunnel?: boolean;
  includeCohorts?: boolean;
  includeDeviceBreakdown?: boolean;
  includeLocationBreakdown?: boolean;
  includeTopLinks?: boolean;
  topLinksLimit?: number;
}

export interface PerformanceReport {
  summary: EmailMetrics;
  timeSeries?: TimeSeriesMetrics;
  funnel?: EmailFunnel;
  cohorts?: CohortMetrics[];
  deviceBreakdown?: DeviceBreakdown[];
  locationBreakdown?: LocationBreakdown[];
  topLinks?: TopLink[];
  generatedAt: Date;
  filter: EmailEventFilter;
}

export interface ComparisonReport {
  baseline: EmailMetrics;
  comparison: EmailMetrics;
  differences: {
    deliveryRate: number;
    openRate: number;
    clickRate: number;
    conversionRate: number;
    bounceRate: number;
    unsubscribeRate: number;
  };
  winner?: 'baseline' | 'comparison' | 'tie';
  confidence?: number;
}

export interface SequencePerformanceReport extends PerformanceReport {
  sequenceId: string;
  sequenceName?: string;
  stepMetrics: Array<{
    step: number;
    templateId?: string;
    templateName?: string;
    metrics: EmailMetrics;
  }>;
}

// ============================================================
// Metrics Aggregation Engine Class
// ============================================================

export class MetricsAggregationEngine {
  constructor(private storage: IAnalyticsStorage) {}

  /**
   * Generate comprehensive performance report
   */
  async generatePerformanceReport(options: PerformanceReportOptions = {}): Promise<PerformanceReport> {
    const filter = this.buildFilter(options);

    // Get base metrics
    const summary = await this.storage.getMetrics(filter);

    // Build report
    const report: PerformanceReport = {
      summary,
      generatedAt: new Date(),
      filter,
    };

    // Add time series if requested
    if (options.includeTimeSeries) {
      report.timeSeries = await this.getTimeSeries(
        filter,
        options.timeInterval || 'day'
      );
    }

    // Add funnel if requested
    if (options.includeFunnel) {
      report.funnel = await this.getFunnel(filter);
    }

    // Add cohorts if requested
    if (options.includeCohorts) {
      report.cohorts = await this.getCohortAnalysis(filter);
    }

    // Add device breakdown if requested
    if (options.includeDeviceBreakdown) {
      report.deviceBreakdown = await this.getDeviceBreakdown(filter);
    }

    // Add location breakdown if requested
    if (options.includeLocationBreakdown) {
      report.locationBreakdown = await this.getLocationBreakdown(filter);
    }

    // Add top links if requested
    if (options.includeTopLinks) {
      report.topLinks = await this.getTopLinks(filter, options.topLinksLimit || 10);
    }

    return report;
  }

  /**
   * Generate sequence-specific performance report
   */
  async generateSequenceReport(
    sequenceId: string,
    options: Omit<PerformanceReportOptions, 'sequenceId'> = {}
  ): Promise<SequencePerformanceReport> {
    const baseReport = await this.generatePerformanceReport({
      ...options,
      sequenceId,
    });

    // Get sequence metrics with step breakdown
    const sequenceMetrics = await this.storage.getSequenceMetrics(
      sequenceId,
      this.buildFilter(options)
    );

    return {
      ...baseReport,
      sequenceId,
      sequenceName: sequenceMetrics.sequenceName,
      stepMetrics: sequenceMetrics.stepMetrics.map(step => ({
        step: step.step,
        templateId: step.templateId,
        templateName: step.templateName,
        metrics: {
          totalSent: step.totalSent,
          totalDelivered: step.totalDelivered,
          totalBounced: step.totalBounced,
          totalOpened: step.totalOpened,
          totalClicked: step.totalClicked,
          totalConverted: step.totalConverted,
          totalUnsubscribed: step.totalUnsubscribed,
          totalComplaints: step.totalComplaints,
          deliveryRate: step.deliveryRate,
          openRate: step.openRate,
          clickRate: step.clickRate,
          clickToOpenRate: step.clickToOpenRate,
          conversionRate: step.conversionRate,
          bounceRate: step.bounceRate,
          unsubscribeRate: step.unsubscribeRate,
          complaintRate: step.complaintRate,
          uniqueOpens: step.uniqueOpens,
          uniqueClicks: step.uniqueClicks,
          totalConversionValue: step.totalConversionValue,
          averageConversionValue: step.averageConversionValue,
          averageTimeToConversion: step.averageTimeToConversion,
          startDate: step.startDate,
          endDate: step.endDate,
        },
      })),
    };
  }

  /**
   * Compare two variants or time periods
   */
  async comparePerformance(
    baselineFilter: EmailEventFilter,
    comparisonFilter: EmailEventFilter
  ): Promise<ComparisonReport> {
    const [baseline, comparison] = await Promise.all([
      this.storage.getMetrics(baselineFilter),
      this.storage.getMetrics(comparisonFilter),
    ]);

    const differences = {
      deliveryRate: comparison.deliveryRate - baseline.deliveryRate,
      openRate: comparison.openRate - baseline.openRate,
      clickRate: comparison.clickRate - baseline.clickRate,
      conversionRate: comparison.conversionRate - baseline.conversionRate,
      bounceRate: comparison.bounceRate - baseline.bounceRate,
      unsubscribeRate: comparison.unsubscribeRate - baseline.unsubscribeRate,
    };

    // Determine winner based on key metrics
    const winner = this.determineWinner(baseline, comparison);

    return {
      baseline,
      comparison,
      differences,
      winner,
    };
  }

  /**
   * Get time-series metrics
   */
  async getTimeSeries(
    filter: EmailEventFilter,
    interval: TimeInterval = 'day'
  ): Promise<TimeSeriesMetrics> {
    const { events } = await this.storage.listEvents(
      filter,
      { field: 'timestamp', direction: 'asc' },
      1,
      Number.MAX_SAFE_INTEGER
    );

    if (events.length === 0) {
      return {
        interval,
        dataPoints: [],
        summary: await this.storage.getMetrics(filter),
      };
    }

    // Group events by time interval
    const groupedEvents = this.groupEventsByInterval(events, interval);

    // Calculate metrics for each interval
    const dataPoints: TimeSeriesDataPoint[] = [];
    for (const [timestamp, intervalEvents] of groupedEvents) {
      const sent = intervalEvents.filter(e => e.type === 'sent');
      const delivered = intervalEvents.filter(e => e.type === 'delivered');
      const opened = intervalEvents.filter(e => e.type === 'open');
      const clicked = intervalEvents.filter(e => e.type === 'click');
      const converted = intervalEvents.filter(e => e.type === 'conversion');
      const bounced = intervalEvents.filter(e => e.type === 'bounce');

      const uniqueOpens = new Set(opened.map(e => `${e.leadId}-${e.messageId}`)).size;
      const uniqueClicks = new Set(clicked.map(e => `${e.leadId}-${e.messageId}`)).size;

      const totalSent = sent.length;
      const totalDelivered = delivered.length;

      dataPoints.push({
        timestamp,
        sent: totalSent,
        delivered: totalDelivered,
        opened: opened.length,
        clicked: clicked.length,
        converted: converted.length,
        bounced: bounced.length,
        openRate: totalDelivered > 0 ? (uniqueOpens / totalDelivered) * 100 : 0,
        clickRate: totalDelivered > 0 ? (uniqueClicks / totalDelivered) * 100 : 0,
        conversionRate: totalDelivered > 0 ? (converted.length / totalDelivered) * 100 : 0,
      });
    }

    return {
      interval,
      dataPoints,
      summary: await this.storage.getMetrics(filter),
    };
  }

  /**
   * Get email engagement funnel
   */
  async getFunnel(filter: EmailEventFilter): Promise<EmailFunnel> {
    const { events } = await this.storage.listEvents(
      filter,
      undefined,
      1,
      Number.MAX_SAFE_INTEGER
    );

    // Count unique leads at each stage
    const sentLeads = new Set(events.filter(e => e.type === 'sent').map(e => e.leadId));
    const deliveredLeads = new Set(events.filter(e => e.type === 'delivered').map(e => e.leadId));
    const openedLeads = new Set(events.filter(e => e.type === 'open').map(e => e.leadId));
    const clickedLeads = new Set(events.filter(e => e.type === 'click').map(e => e.leadId));
    const convertedLeads = new Set(events.filter(e => e.type === 'conversion').map(e => e.leadId));

    const totalEntered = sentLeads.size;

    const steps: FunnelStep[] = [
      {
        name: 'Sent',
        eventType: 'sent',
        count: sentLeads.size,
        percentage: 100,
      },
      {
        name: 'Delivered',
        eventType: 'delivered',
        count: deliveredLeads.size,
        percentage: totalEntered > 0 ? (deliveredLeads.size / totalEntered) * 100 : 0,
        dropoff: sentLeads.size - deliveredLeads.size,
        dropoffPercentage: totalEntered > 0 ? ((sentLeads.size - deliveredLeads.size) / totalEntered) * 100 : 0,
      },
      {
        name: 'Opened',
        eventType: 'open',
        count: openedLeads.size,
        percentage: totalEntered > 0 ? (openedLeads.size / totalEntered) * 100 : 0,
        dropoff: deliveredLeads.size - openedLeads.size,
        dropoffPercentage: totalEntered > 0 ? ((deliveredLeads.size - openedLeads.size) / totalEntered) * 100 : 0,
      },
      {
        name: 'Clicked',
        eventType: 'click',
        count: clickedLeads.size,
        percentage: totalEntered > 0 ? (clickedLeads.size / totalEntered) * 100 : 0,
        dropoff: openedLeads.size - clickedLeads.size,
        dropoffPercentage: totalEntered > 0 ? ((openedLeads.size - clickedLeads.size) / totalEntered) * 100 : 0,
      },
      {
        name: 'Converted',
        eventType: 'conversion',
        count: convertedLeads.size,
        percentage: totalEntered > 0 ? (convertedLeads.size / totalEntered) * 100 : 0,
        dropoff: clickedLeads.size - convertedLeads.size,
        dropoffPercentage: totalEntered > 0 ? ((clickedLeads.size - convertedLeads.size) / totalEntered) * 100 : 0,
      },
    ];

    // Calculate average time to complete
    const conversionEvents = events.filter(e => e.type === 'conversion');
    const conversionTimes = conversionEvents
      .map(e => e.eventData?.conversionData?.timeToConversion)
      .filter((t): t is number => t !== undefined);

    const averageTimeToComplete =
      conversionTimes.length > 0
        ? conversionTimes.reduce((sum, t) => sum + t, 0) / conversionTimes.length
        : undefined;

    return {
      steps,
      totalEntered,
      totalCompleted: convertedLeads.size,
      completionRate: totalEntered > 0 ? (convertedLeads.size / totalEntered) * 100 : 0,
      averageTimeToComplete,
    };
  }

  /**
   * Get cohort analysis
   */
  async getCohortAnalysis(filter: EmailEventFilter): Promise<CohortMetrics[]> {
    const { events } = await this.storage.listEvents(
      filter,
      { field: 'timestamp', direction: 'asc' },
      1,
      Number.MAX_SAFE_INTEGER
    );

    // Group events by cohort (date of first sent event per lead)
    const leadCohorts = new Map<string, Date>();
    const sentEvents = events.filter(e => e.type === 'sent');

    for (const event of sentEvents) {
      if (!leadCohorts.has(event.leadId)) {
        const cohortDate = new Date(event.timestamp);
        cohortDate.setHours(0, 0, 0, 0);
        leadCohorts.set(event.leadId, cohortDate);
      }
    }

    // Group by cohort date
    const cohortGroups = new Map<string, Set<string>>();
    for (const [leadId, cohortDate] of leadCohorts) {
      const dateKey = cohortDate.toISOString().split('T')[0];
      if (!cohortGroups.has(dateKey)) {
        cohortGroups.set(dateKey, new Set());
      }
      cohortGroups.get(dateKey)!.add(leadId);
    }

    // Calculate metrics for each cohort
    const cohorts: CohortMetrics[] = [];
    const sortedCohortDates = Array.from(cohortGroups.keys()).sort();

    for (const dateKey of sortedCohortDates) {
      const cohortDate = new Date(dateKey);
      const cohortLeadIds = cohortGroups.get(dateKey)!;

      const cohort: CohortMetrics = {
        cohortDate,
        cohortSize: cohortLeadIds.size,
        metrics: {},
      };

      // Calculate metrics for different time periods
      const periods = [
        { key: 'day0', days: 0 },
        { key: 'day1', days: 1 },
        { key: 'day3', days: 3 },
        { key: 'day7', days: 7 },
        { key: 'day14', days: 14 },
        { key: 'day30', days: 30 },
      ];

      for (const period of periods) {
        const periodEnd = new Date(cohortDate.getTime() + period.days * 24 * 60 * 60 * 1000);
        const periodFilter: EmailEventFilter = {
          ...filter,
          leadIds: Array.from(cohortLeadIds),
          timestampAfter: cohortDate,
          timestampBefore: periodEnd,
        };

        const periodMetrics = await this.storage.getMetrics(periodFilter);
        (cohort.metrics as any)[period.key] = periodMetrics;
      }

      cohorts.push(cohort);
    }

    return cohorts;
  }

  /**
   * Get device breakdown
   */
  async getDeviceBreakdown(filter: EmailEventFilter): Promise<DeviceBreakdown[]> {
    const { events } = await this.storage.listEvents(
      filter,
      undefined,
      1,
      Number.MAX_SAFE_INTEGER
    );

    const deviceTypes: Array<'desktop' | 'mobile' | 'tablet' | 'unknown'> = [
      'desktop',
      'mobile',
      'tablet',
      'unknown',
    ];

    const total = events.length;
    const breakdowns: DeviceBreakdown[] = [];

    for (const deviceType of deviceTypes) {
      const deviceEvents = events.filter(e => e.deviceType === deviceType);
      const count = deviceEvents.length;

      if (count === 0) continue;

      const deviceFilter: EmailEventFilter = {
        ...filter,
        deviceType,
      };

      const metrics = await this.storage.getMetrics(deviceFilter);

      breakdowns.push({
        deviceType,
        count,
        percentage: total > 0 ? (count / total) * 100 : 0,
        openRate: metrics.openRate,
        clickRate: metrics.clickRate,
        conversionRate: metrics.conversionRate,
      });
    }

    return breakdowns.sort((a, b) => b.count - a.count);
  }

  /**
   * Get location breakdown
   */
  async getLocationBreakdown(filter: EmailEventFilter): Promise<LocationBreakdown[]> {
    const { events } = await this.storage.listEvents(
      filter,
      undefined,
      1,
      Number.MAX_SAFE_INTEGER
    );

    // Group by country
    const countries = new Map<string, number>();
    for (const event of events) {
      if (event.country) {
        countries.set(event.country, (countries.get(event.country) || 0) + 1);
      }
    }

    const total = events.length;
    const breakdowns: LocationBreakdown[] = [];

    for (const [country, count] of countries) {
      const countryFilter: EmailEventFilter = {
        ...filter,
        country,
      };

      const metrics = await this.storage.getMetrics(countryFilter);

      breakdowns.push({
        country,
        count,
        percentage: total > 0 ? (count / total) * 100 : 0,
        openRate: metrics.openRate,
        clickRate: metrics.clickRate,
        conversionRate: metrics.conversionRate,
      });
    }

    return breakdowns.sort((a, b) => b.count - a.count);
  }

  /**
   * Get top performing links
   */
  async getTopLinks(filter: EmailEventFilter, limit: number = 10): Promise<TopLink[]> {
    const { events } = await this.storage.listEvents(
      { ...filter, type: 'click' },
      undefined,
      1,
      Number.MAX_SAFE_INTEGER
    );

    // Group by link
    const links = new Map<string, {
      targetUrl: string;
      clicks: number;
      uniqueClicks: Set<string>;
    }>();

    for (const event of events) {
      const linkId = event.eventData?.clickData?.linkId;
      const targetUrl = event.eventData?.clickData?.targetUrl;

      if (linkId && targetUrl) {
        if (!links.has(linkId)) {
          links.set(linkId, {
            targetUrl,
            clicks: 0,
            uniqueClicks: new Set(),
          });
        }

        const link = links.get(linkId)!;
        link.clicks++;
        link.uniqueClicks.add(`${event.leadId}-${event.messageId}`);
      }
    }

    // Get total delivered for click rate calculation
    const metrics = await this.storage.getMetrics(filter);
    const totalDelivered = metrics.totalDelivered;

    // Convert to TopLink array
    const topLinks: TopLink[] = Array.from(links.entries()).map(([linkId, data]) => ({
      linkId,
      targetUrl: data.targetUrl,
      clicks: data.clicks,
      uniqueClicks: data.uniqueClicks.size,
      clickRate: totalDelivered > 0 ? (data.uniqueClicks.size / totalDelivered) * 100 : 0,
    }));

    // Sort by unique clicks and limit
    return topLinks
      .sort((a, b) => b.uniqueClicks - a.uniqueClicks)
      .slice(0, limit);
  }

  /**
   * Get variant metrics for A/B testing
   */
  async getVariantMetrics(
    testId: string,
    filter?: Omit<EmailEventFilter, 'testId'>
  ): Promise<VariantMetrics[]> {
    const testFilter: EmailEventFilter = {
      ...filter,
      testId,
    };

    // Get all events for this test
    const { events } = await this.storage.listEvents(
      testFilter,
      undefined,
      1,
      Number.MAX_SAFE_INTEGER
    );

    // Get unique variant IDs
    const variantIds = new Set(
      events.filter(e => e.variantId).map(e => e.variantId!)
    );

    // Calculate metrics for each variant
    const variantMetrics: VariantMetrics[] = [];

    for (const variantId of variantIds) {
      const variantFilter: EmailEventFilter = {
        ...testFilter,
        variantId,
      };

      const metrics = await this.storage.getMetrics(variantFilter);

      // Calculate traffic percentage
      const variantEvents = events.filter(e => e.variantId === variantId);
      const trafficPercentage = events.length > 0 ? (variantEvents.length / events.length) * 100 : 0;

      variantMetrics.push({
        variantId,
        testId,
        trafficPercentage,
        ...metrics,
      });
    }

    return variantMetrics;
  }

  // ============================================================
  // Private Helper Methods
  // ============================================================

  private buildFilter(options: PerformanceReportOptions): EmailEventFilter {
    const filter: EmailEventFilter = {};

    if (options.sequenceId) filter.sequenceId = options.sequenceId;
    if (options.campaignId) filter.campaignId = options.campaignId;
    if (options.variantId) filter.variantId = options.variantId;
    if (options.startDate) filter.startDate = options.startDate;
    if (options.endDate) filter.endDate = options.endDate;

    return filter;
  }

  private groupEventsByInterval(
    events: EmailEvent[],
    interval: TimeInterval
  ): Map<Date, EmailEvent[]> {
    const groups = new Map<string, EmailEvent[]>();

    for (const event of events) {
      const key = this.getIntervalKey(event.timestamp, interval);
      if (!groups.has(key)) {
        groups.set(key, []);
      }
      groups.get(key)!.push(event);
    }

    // Convert string keys to Date objects and sort
    const sortedGroups = new Map<Date, EmailEvent[]>();
    const sortedKeys = Array.from(groups.keys()).sort();

    for (const key of sortedKeys) {
      sortedGroups.set(new Date(key), groups.get(key)!);
    }

    return sortedGroups;
  }

  private getIntervalKey(date: Date, interval: TimeInterval): string {
    const d = new Date(date);

    switch (interval) {
      case 'hour':
        d.setMinutes(0, 0, 0);
        break;
      case 'day':
        d.setHours(0, 0, 0, 0);
        break;
      case 'week':
        const day = d.getDay();
        const diff = d.getDate() - day;
        d.setDate(diff);
        d.setHours(0, 0, 0, 0);
        break;
      case 'month':
        d.setDate(1);
        d.setHours(0, 0, 0, 0);
        break;
    }

    return d.toISOString();
  }

  private determineWinner(
    baseline: EmailMetrics,
    comparison: EmailMetrics
  ): 'baseline' | 'comparison' | 'tie' {
    // Weight different metrics
    const weights = {
      conversionRate: 0.4,
      clickRate: 0.3,
      openRate: 0.2,
      deliveryRate: 0.1,
    };

    let baselineScore = 0;
    let comparisonScore = 0;

    baselineScore +=
      baseline.conversionRate * weights.conversionRate +
      baseline.clickRate * weights.clickRate +
      baseline.openRate * weights.openRate +
      baseline.deliveryRate * weights.deliveryRate;

    comparisonScore +=
      comparison.conversionRate * weights.conversionRate +
      comparison.clickRate * weights.clickRate +
      comparison.openRate * weights.openRate +
      comparison.deliveryRate * weights.deliveryRate;

    const difference = Math.abs(baselineScore - comparisonScore);

    // Consider it a tie if difference is less than 1%
    if (difference < 1) {
      return 'tie';
    }

    return comparisonScore > baselineScore ? 'comparison' : 'baseline';
  }
}

// ============================================================
// Singleton Instance
// ============================================================

let defaultEngine: MetricsAggregationEngine | null = null;

export function getMetricsEngine(storage: IAnalyticsStorage): MetricsAggregationEngine {
  if (!defaultEngine) {
    defaultEngine = new MetricsAggregationEngine(storage);
  }
  return defaultEngine;
}

export function resetMetricsEngine(): void {
  defaultEngine = null;
}
