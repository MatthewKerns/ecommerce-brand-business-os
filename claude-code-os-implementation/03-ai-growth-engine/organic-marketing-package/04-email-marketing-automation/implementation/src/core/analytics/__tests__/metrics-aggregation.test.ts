/**
 * Metrics Aggregation Engine Tests
 *
 * Tests for performance reporting, time-series analytics, funnel analysis,
 * cohort analysis, and device/location breakdowns.
 */

import { describe, it, expect, beforeEach } from '@jest/globals';
import { MetricsAggregationEngine } from '../metrics';
import { MemoryAnalyticsStorage } from '../storage';
import type {
  EmailEventCreateInput,
  ClickEventInput,
  ConversionEventInput,
  OpenEventInput,
} from '../models';

describe('MetricsAggregationEngine', () => {
  let storage: MemoryAnalyticsStorage;
  let engine: MetricsAggregationEngine;

  beforeEach(() => {
    storage = new MemoryAnalyticsStorage();
    engine = new MetricsAggregationEngine(storage);
  });

  describe('metrics aggregation', () => {
    it('should generate performance report with summary metrics', async () => {
      // Create sample events
      await storage.recordEvent({
        type: 'sent',
        leadId: 'lead1',
        messageId: 'msg1',
        emailAddress: 'test@example.com',
        sequenceId: 'seq1',
      });

      await storage.recordEvent({
        type: 'delivered',
        leadId: 'lead1',
        messageId: 'msg1',
        emailAddress: 'test@example.com',
        sequenceId: 'seq1',
      });

      await storage.recordOpen({
        leadId: 'lead1',
        messageId: 'msg1',
        emailAddress: 'test@example.com',
        sequenceId: 'seq1',
      });

      const report = await engine.generatePerformanceReport({
        sequenceId: 'seq1',
      });

      expect(report).toBeDefined();
      expect(report.summary).toBeDefined();
      expect(report.summary.totalSent).toBe(1);
      expect(report.summary.totalDelivered).toBe(1);
      expect(report.summary.totalOpened).toBe(1);
      expect(report.summary.openRate).toBeGreaterThan(0);
    });

    it('should include time series data when requested', async () => {
      await storage.recordEvent({
        type: 'sent',
        leadId: 'lead1',
        messageId: 'msg1',
        emailAddress: 'test@example.com',
      });

      const report = await engine.generatePerformanceReport({
        includeTimeSeries: true,
        timeInterval: 'day',
      });

      expect(report.timeSeries).toBeDefined();
      expect(report.timeSeries?.dataPoints).toBeDefined();
      expect(report.timeSeries?.interval).toBe('day');
    });

    it('should include funnel analysis when requested', async () => {
      // Create full funnel
      await storage.recordEvent({
        type: 'sent',
        leadId: 'lead1',
        messageId: 'msg1',
        emailAddress: 'test@example.com',
      });

      await storage.recordEvent({
        type: 'delivered',
        leadId: 'lead1',
        messageId: 'msg1',
        emailAddress: 'test@example.com',
      });

      await storage.recordOpen({
        leadId: 'lead1',
        messageId: 'msg1',
        emailAddress: 'test@example.com',
      });

      await storage.recordClick({
        leadId: 'lead1',
        messageId: 'msg1',
        emailAddress: 'test@example.com',
        linkId: 'link1',
        targetUrl: 'https://example.com',
      });

      await storage.recordConversion({
        leadId: 'lead1',
        messageId: 'msg1',
        emailAddress: 'test@example.com',
        conversionType: 'purchase',
        conversionValue: 100,
      });

      const report = await engine.generatePerformanceReport({
        includeFunnel: true,
      });

      expect(report.funnel).toBeDefined();
      expect(report.funnel?.steps).toHaveLength(5);
      expect(report.funnel?.steps[0].name).toBe('Sent');
      expect(report.funnel?.steps[4].name).toBe('Converted');
      expect(report.funnel?.totalEntered).toBe(1);
      expect(report.funnel?.totalCompleted).toBe(1);
    });

    it('should aggregate metrics for sequences', async () => {
      // Add events for sequence
      await storage.recordEvent({
        type: 'sent',
        leadId: 'lead1',
        messageId: 'msg1',
        emailAddress: 'test@example.com',
        sequenceId: 'seq1',
        sequenceStep: 1,
      });

      await storage.recordEvent({
        type: 'delivered',
        leadId: 'lead1',
        messageId: 'msg1',
        emailAddress: 'test@example.com',
        sequenceId: 'seq1',
        sequenceStep: 1,
      });

      await storage.recordOpen({
        leadId: 'lead1',
        messageId: 'msg1',
        emailAddress: 'test@example.com',
        sequenceId: 'seq1',
        sequenceStep: 1,
      });

      const report = await engine.generateSequenceReport('seq1');

      expect(report).toBeDefined();
      expect(report.sequenceId).toBe('seq1');
      expect(report.stepMetrics).toBeDefined();
      expect(report.stepMetrics.length).toBeGreaterThan(0);
      expect(report.stepMetrics[0].step).toBe(1);
    });
  });

  describe('time series aggregation', () => {
    it('should group events by day', async () => {
      const now = new Date();

      await storage.recordEvent({
        type: 'sent',
        leadId: 'lead1',
        messageId: 'msg1',
        emailAddress: 'test@example.com',
      });

      const timeSeries = await engine.getTimeSeries({}, 'day');

      expect(timeSeries).toBeDefined();
      expect(timeSeries.interval).toBe('day');
      expect(timeSeries.dataPoints).toBeDefined();
    });

    it('should calculate metrics for each time interval', async () => {
      await storage.recordEvent({
        type: 'sent',
        leadId: 'lead1',
        messageId: 'msg1',
        emailAddress: 'test@example.com',
      });

      await storage.recordEvent({
        type: 'delivered',
        leadId: 'lead1',
        messageId: 'msg1',
        emailAddress: 'test@example.com',
      });

      const timeSeries = await engine.getTimeSeries({}, 'hour');

      expect(timeSeries.dataPoints.length).toBeGreaterThan(0);
      expect(timeSeries.dataPoints[0]).toHaveProperty('timestamp');
      expect(timeSeries.dataPoints[0]).toHaveProperty('sent');
      expect(timeSeries.dataPoints[0]).toHaveProperty('delivered');
      expect(timeSeries.dataPoints[0]).toHaveProperty('openRate');
    });
  });

  describe('funnel aggregation', () => {
    it('should calculate funnel steps with dropoff', async () => {
      // Send to 2 leads
      await storage.recordEvent({
        type: 'sent',
        leadId: 'lead1',
        messageId: 'msg1',
        emailAddress: 'test1@example.com',
      });

      await storage.recordEvent({
        type: 'sent',
        leadId: 'lead2',
        messageId: 'msg2',
        emailAddress: 'test2@example.com',
      });

      // Only 1 opens
      await storage.recordEvent({
        type: 'delivered',
        leadId: 'lead1',
        messageId: 'msg1',
        emailAddress: 'test1@example.com',
      });

      await storage.recordOpen({
        leadId: 'lead1',
        messageId: 'msg1',
        emailAddress: 'test1@example.com',
      });

      const funnel = await engine.getFunnel({});

      expect(funnel.steps).toBeDefined();
      expect(funnel.totalEntered).toBe(2);

      const openedStep = funnel.steps.find(s => s.name === 'Opened');
      expect(openedStep).toBeDefined();
      expect(openedStep?.percentage).toBeLessThan(100);
    });
  });

  describe('device and location aggregation', () => {
    it('should aggregate metrics by device type', async () => {
      await storage.recordEvent({
        type: 'open',
        leadId: 'lead1',
        messageId: 'msg1',
        emailAddress: 'test@example.com',
        userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)',
      });

      await storage.recordEvent({
        type: 'open',
        leadId: 'lead2',
        messageId: 'msg2',
        emailAddress: 'test2@example.com',
        userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
      });

      const breakdown = await engine.getDeviceBreakdown({});

      expect(breakdown).toBeDefined();
      expect(breakdown.length).toBeGreaterThan(0);
      expect(breakdown[0]).toHaveProperty('deviceType');
      expect(breakdown[0]).toHaveProperty('count');
      expect(breakdown[0]).toHaveProperty('percentage');
    });

    it('should aggregate top performing links', async () => {
      await storage.recordClick({
        leadId: 'lead1',
        messageId: 'msg1',
        emailAddress: 'test@example.com',
        linkId: 'link1',
        targetUrl: 'https://example.com/product1',
      });

      await storage.recordClick({
        leadId: 'lead2',
        messageId: 'msg2',
        emailAddress: 'test2@example.com',
        linkId: 'link1',
        targetUrl: 'https://example.com/product1',
      });

      await storage.recordClick({
        leadId: 'lead3',
        messageId: 'msg3',
        emailAddress: 'test3@example.com',
        linkId: 'link2',
        targetUrl: 'https://example.com/product2',
      });

      const topLinks = await engine.getTopLinks({}, 5);

      expect(topLinks).toBeDefined();
      expect(topLinks.length).toBeGreaterThan(0);
      expect(topLinks[0]).toHaveProperty('linkId');
      expect(topLinks[0]).toHaveProperty('targetUrl');
      expect(topLinks[0]).toHaveProperty('clicks');
      expect(topLinks[0]).toHaveProperty('uniqueClicks');
      expect(topLinks[0].uniqueClicks).toBe(2);
    });
  });

  describe('comparison and variant aggregation', () => {
    it('should compare performance between two filters', async () => {
      // Baseline variant
      await storage.recordEvent({
        type: 'sent',
        leadId: 'lead1',
        messageId: 'msg1',
        emailAddress: 'test@example.com',
        variantId: 'variant-a',
      });

      await storage.recordEvent({
        type: 'delivered',
        leadId: 'lead1',
        messageId: 'msg1',
        emailAddress: 'test@example.com',
        variantId: 'variant-a',
      });

      // Comparison variant
      await storage.recordEvent({
        type: 'sent',
        leadId: 'lead2',
        messageId: 'msg2',
        emailAddress: 'test2@example.com',
        variantId: 'variant-b',
      });

      await storage.recordEvent({
        type: 'delivered',
        leadId: 'lead2',
        messageId: 'msg2',
        emailAddress: 'test2@example.com',
        variantId: 'variant-b',
      });

      await storage.recordOpen({
        leadId: 'lead2',
        messageId: 'msg2',
        emailAddress: 'test2@example.com',
        variantId: 'variant-b',
      });

      const comparison = await engine.comparePerformance(
        { variantId: 'variant-a' },
        { variantId: 'variant-b' }
      );

      expect(comparison).toBeDefined();
      expect(comparison.baseline).toBeDefined();
      expect(comparison.comparison).toBeDefined();
      expect(comparison.differences).toBeDefined();
      expect(comparison.differences.openRate).toBeGreaterThan(0);
    });

    it('should aggregate metrics for A/B test variants', async () => {
      await storage.recordEvent({
        type: 'sent',
        leadId: 'lead1',
        messageId: 'msg1',
        emailAddress: 'test@example.com',
        testId: 'test1',
        variantId: 'variant-a',
      });

      await storage.recordEvent({
        type: 'sent',
        leadId: 'lead2',
        messageId: 'msg2',
        emailAddress: 'test2@example.com',
        testId: 'test1',
        variantId: 'variant-b',
      });

      const variantMetrics = await engine.getVariantMetrics('test1');

      expect(variantMetrics).toBeDefined();
      expect(variantMetrics.length).toBe(2);
      expect(variantMetrics[0]).toHaveProperty('variantId');
      expect(variantMetrics[0]).toHaveProperty('testId');
      expect(variantMetrics[0]).toHaveProperty('trafficPercentage');
    });
  });

  describe('cohort aggregation', () => {
    it('should group leads by cohort date', async () => {
      const today = new Date();
      today.setHours(0, 0, 0, 0);

      await storage.recordEvent({
        type: 'sent',
        leadId: 'lead1',
        messageId: 'msg1',
        emailAddress: 'test@example.com',
      });

      const cohorts = await engine.getCohortAnalysis({});

      expect(cohorts).toBeDefined();
      expect(cohorts.length).toBeGreaterThan(0);
      expect(cohorts[0]).toHaveProperty('cohortDate');
      expect(cohorts[0]).toHaveProperty('cohortSize');
      expect(cohorts[0]).toHaveProperty('metrics');
    });
  });
});
