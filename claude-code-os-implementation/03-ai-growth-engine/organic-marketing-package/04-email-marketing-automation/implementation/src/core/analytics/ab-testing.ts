/**
 * A/B Testing System - Variant management and traffic splitting
 *
 * Features:
 * - Create and manage A/B tests
 * - Traffic splitting with configurable weights
 * - Variant assignment with consistent hashing
 * - Test status tracking (draft, running, completed, archived)
 * - Statistical significance calculation integration
 * - Performance comparison between variants
 */

import type { IAnalyticsStorage } from './storage';
import type { VariantMetrics, EmailEventFilter } from './models';

// ============================================================
// Types
// ============================================================

export type ABTestStatus = 'draft' | 'running' | 'paused' | 'completed' | 'archived';

export type ABTestType = 'subject_line' | 'content' | 'send_time' | 'from_name' | 'full_email';

export interface ABVariant {
  id: string;
  name: string;
  description?: string;
  weight: number; // 0-100 (percentage of traffic)

  // Variant configuration
  config: {
    subject?: string;
    fromName?: string;
    content?: string;
    templateId?: string;
    sendTime?: {
      hour: number;
      timezone?: string;
    };
  };

  // Tracking
  isControl?: boolean;
  metadata?: Record<string, any>;
}

export interface ABTest {
  id: string;
  name: string;
  description?: string;
  type: ABTestType;
  status: ABTestStatus;

  // Test configuration
  variants: ABVariant[];
  trafficAllocation: number; // 0-100 (percentage of total traffic to include in test)

  // Context
  sequenceId?: string;
  campaignId?: string;
  templateId?: string;

  // Timing
  startDate?: Date;
  endDate?: Date;
  createdAt: Date;
  updatedAt: Date;

  // Goals and metrics
  primaryMetric: 'open_rate' | 'click_rate' | 'conversion_rate' | 'revenue';
  minimumSampleSize?: number;
  confidenceLevel?: number; // 90, 95, 99

  // Results
  winner?: string; // variant ID
  winnerDeclaredAt?: Date;
  completionReason?: 'manual' | 'sample_size_reached' | 'time_limit' | 'significance_reached';

  // Metadata
  createdBy?: string;
  tags?: string[];
  metadata?: Record<string, any>;
}

export interface ABTestAssignment {
  testId: string;
  variantId: string;
  userId: string; // leadId or unique identifier
  assignedAt: Date;
  context?: {
    sequenceId?: string;
    campaignId?: string;
    messageId?: string;
  };
}

export interface ABTestFilter {
  status?: ABTestStatus | ABTestStatus[];
  type?: ABTestType;
  sequenceId?: string;
  campaignId?: string;
  tags?: string[];
}

export interface ABTestResults {
  testId: string;
  testName: string;
  status: ABTestStatus;
  primaryMetric: string;

  variants: Array<{
    variantId: string;
    variantName: string;
    isControl: boolean;
    metrics: VariantMetrics;
    isWinner?: boolean;
  }>;

  winner?: {
    variantId: string;
    variantName: string;
    improvement: number; // percentage improvement over control
    confidence?: number;
  };

  sampleSizeReached: boolean;
  statisticalSignificance?: number;
  recommendedAction?: 'continue' | 'declare_winner' | 'stop_test';
}

// ============================================================
// ABTestManager Class
// ============================================================

export class ABTestManager {
  private tests: Map<string, ABTest> = new Map();
  private assignments: Map<string, ABTestAssignment> = new Map(); // userId -> assignment
  private userTestAssignments: Map<string, Map<string, string>> = new Map(); // userId -> testId -> variantId
  private analyticsStorage?: IAnalyticsStorage;

  constructor(analyticsStorage?: IAnalyticsStorage) {
    this.analyticsStorage = analyticsStorage;
  }

  /**
   * Set analytics storage (can be called after construction)
   */
  setAnalyticsStorage(storage: IAnalyticsStorage): void {
    this.analyticsStorage = storage;
  }

  // ============================================================
  // Test Management
  // ============================================================

  /**
   * Create a new A/B test
   */
  async createTest(test: Omit<ABTest, 'id' | 'createdAt' | 'updatedAt'>): Promise<ABTest> {
    // Validate variants
    this.validateVariants(test.variants);

    const newTest: ABTest = {
      ...test,
      id: this.generateId('test'),
      createdAt: new Date(),
      updatedAt: new Date(),
    };

    this.tests.set(newTest.id, newTest);
    return newTest;
  }

  /**
   * Update an existing test
   */
  async updateTest(
    testId: string,
    updates: Partial<Omit<ABTest, 'id' | 'createdAt'>>
  ): Promise<ABTest | null> {
    const test = this.tests.get(testId);
    if (!test) return null;

    // Validate variants if being updated
    if (updates.variants) {
      this.validateVariants(updates.variants);
    }

    // Don't allow certain updates if test is running
    if (test.status === 'running' && updates.variants) {
      throw new Error('Cannot modify variants while test is running');
    }

    const updatedTest = {
      ...test,
      ...updates,
      updatedAt: new Date(),
    };

    this.tests.set(testId, updatedTest);
    return updatedTest;
  }

  /**
   * Get test by ID
   */
  async getTest(testId: string): Promise<ABTest | null> {
    return this.tests.get(testId) || null;
  }

  /**
   * List all tests
   */
  async listTests(filter?: ABTestFilter): Promise<ABTest[]> {
    let tests = Array.from(this.tests.values());

    if (filter?.status) {
      const statuses = Array.isArray(filter.status) ? filter.status : [filter.status];
      tests = tests.filter(t => statuses.includes(t.status));
    }

    if (filter?.type) {
      tests = tests.filter(t => t.type === filter.type);
    }

    if (filter?.sequenceId) {
      tests = tests.filter(t => t.sequenceId === filter.sequenceId);
    }

    if (filter?.campaignId) {
      tests = tests.filter(t => t.campaignId === filter.campaignId);
    }

    if (filter?.tags && filter.tags.length > 0) {
      tests = tests.filter(t =>
        t.tags?.some(tag => filter.tags!.includes(tag))
      );
    }

    return tests;
  }

  /**
   * Start a test
   */
  async startTest(testId: string): Promise<boolean> {
    const test = this.tests.get(testId);
    if (!test || test.status !== 'draft') {
      return false;
    }

    test.status = 'running';
    test.startDate = new Date();
    test.updatedAt = new Date();
    this.tests.set(testId, test);

    return true;
  }

  /**
   * Pause a test
   */
  async pauseTest(testId: string): Promise<boolean> {
    const test = this.tests.get(testId);
    if (!test || test.status !== 'running') {
      return false;
    }

    test.status = 'paused';
    test.updatedAt = new Date();
    this.tests.set(testId, test);

    return true;
  }

  /**
   * Complete a test
   */
  async completeTest(
    testId: string,
    winnerId?: string,
    reason?: ABTest['completionReason']
  ): Promise<boolean> {
    const test = this.tests.get(testId);
    if (!test) return false;

    if (winnerId) {
      const variant = test.variants.find(v => v.id === winnerId);
      if (!variant) {
        throw new Error(`Variant ${winnerId} not found in test ${testId}`);
      }
    }

    test.status = 'completed';
    test.endDate = new Date();
    test.winner = winnerId;
    test.winnerDeclaredAt = winnerId ? new Date() : undefined;
    test.completionReason = reason || 'manual';
    test.updatedAt = new Date();
    this.tests.set(testId, test);

    return true;
  }

  /**
   * Archive a test
   */
  async archiveTest(testId: string): Promise<boolean> {
    const test = this.tests.get(testId);
    if (!test) return false;

    test.status = 'archived';
    test.updatedAt = new Date();
    this.tests.set(testId, test);

    return true;
  }

  // ============================================================
  // Variant Assignment & Traffic Splitting
  // ============================================================

  /**
   * Assign a variant to a user based on traffic splitting logic
   */
  async assignVariant(
    testId: string,
    userId: string,
    context?: ABTestAssignment['context']
  ): Promise<ABVariant | null> {
    const test = this.tests.get(testId);
    if (!test || test.status !== 'running') {
      return null;
    }

    // Check if user is already assigned to this test
    const existingAssignment = this.getUserAssignment(userId, testId);
    if (existingAssignment) {
      const variant = test.variants.find(v => v.id === existingAssignment);
      return variant || null;
    }

    // Check if user should be included in test based on traffic allocation
    if (!this.shouldIncludeInTest(userId, test.trafficAllocation)) {
      return null;
    }

    // Assign variant using consistent hashing
    const variant = this.selectVariant(userId, test.variants);
    if (!variant) return null;

    // Store assignment
    const assignment: ABTestAssignment = {
      testId,
      variantId: variant.id,
      userId,
      assignedAt: new Date(),
      context,
    };

    const assignmentKey = this.getAssignmentKey(userId, testId);
    this.assignments.set(assignmentKey, assignment);

    // Track user assignment
    if (!this.userTestAssignments.has(userId)) {
      this.userTestAssignments.set(userId, new Map());
    }
    this.userTestAssignments.get(userId)!.set(testId, variant.id);

    return variant;
  }

  /**
   * Get user's variant assignment for a test
   */
  getUserAssignment(userId: string, testId: string): string | null {
    return this.userTestAssignments.get(userId)?.get(testId) || null;
  }

  /**
   * Get all assignments for a user
   */
  getUserAssignments(userId: string): Map<string, string> {
    return this.userTestAssignments.get(userId) || new Map();
  }

  /**
   * Get all assignments for a test
   */
  getTestAssignments(testId: string): ABTestAssignment[] {
    const assignments: ABTestAssignment[] = [];

    for (const assignment of this.assignments.values()) {
      if (assignment.testId === testId) {
        assignments.push(assignment);
      }
    }

    return assignments;
  }

  // ============================================================
  // Results & Analytics
  // ============================================================

  /**
   * Get test results with variant performance
   */
  async getTestResults(testId: string, filter?: Omit<EmailEventFilter, 'testId'>): Promise<ABTestResults | null> {
    if (!this.analyticsStorage) {
      throw new Error('Analytics storage not configured. Call setAnalyticsStorage() first.');
    }

    const test = this.tests.get(testId);
    if (!test) return null;

    // Get metrics for each variant
    const variantResults = [];

    for (const variant of test.variants) {
      const variantFilter: EmailEventFilter = {
        ...filter,
        testId,
        variantId: variant.id,
      };

      const metrics = await this.analyticsStorage.getMetrics(variantFilter);

      variantResults.push({
        variantId: variant.id,
        variantName: variant.name,
        isControl: variant.isControl || false,
        metrics: {
          ...metrics,
          variantId: variant.id,
          testId,
          trafficPercentage: variant.weight,
        },
        isWinner: test.winner === variant.id,
      });
    }

    // Determine sample size status
    const totalSent = variantResults.reduce((sum, v) => sum + v.metrics.totalSent, 0);
    const sampleSizeReached = test.minimumSampleSize
      ? totalSent >= test.minimumSampleSize
      : false;

    // Find control and winner
    const control = variantResults.find(v => v.isControl);
    const winner = test.winner
      ? variantResults.find(v => v.variantId === test.winner)
      : undefined;

    // Calculate improvement if winner exists
    let improvement: number | undefined;
    if (winner && control) {
      const controlValue = this.getMetricValue(control.metrics, test.primaryMetric);
      const winnerValue = this.getMetricValue(winner.metrics, test.primaryMetric);
      if (controlValue > 0) {
        improvement = ((winnerValue - controlValue) / controlValue) * 100;
      }
    }

    // Determine recommended action
    let recommendedAction: ABTestResults['recommendedAction'] = 'continue';
    if (test.status === 'completed') {
      recommendedAction = test.winner ? 'declare_winner' : 'stop_test';
    } else if (sampleSizeReached) {
      recommendedAction = 'declare_winner';
    }

    return {
      testId,
      testName: test.name,
      status: test.status,
      primaryMetric: test.primaryMetric,
      variants: variantResults,
      winner: winner && improvement !== undefined ? {
        variantId: winner.variantId,
        variantName: winner.variantName,
        improvement,
      } : undefined,
      sampleSizeReached,
      recommendedAction,
    };
  }

  /**
   * Compare two variants
   */
  async compareVariants(
    testId: string,
    variantIdA: string,
    variantIdB: string,
    filter?: Omit<EmailEventFilter, 'testId' | 'variantId'>
  ): Promise<{
    variantA: VariantMetrics;
    variantB: VariantMetrics;
    differences: Record<string, number>;
  } | null> {
    if (!this.analyticsStorage) {
      throw new Error('Analytics storage not configured. Call setAnalyticsStorage() first.');
    }

    const test = this.tests.get(testId);
    if (!test) return null;

    const [metricsA, metricsB] = await Promise.all([
      this.analyticsStorage.getMetrics({
        ...filter,
        testId,
        variantId: variantIdA,
      }),
      this.analyticsStorage.getMetrics({
        ...filter,
        testId,
        variantId: variantIdB,
      }),
    ]);

    const differences = {
      openRate: metricsB.openRate - metricsA.openRate,
      clickRate: metricsB.clickRate - metricsA.clickRate,
      conversionRate: metricsB.conversionRate - metricsA.conversionRate,
      clickToOpenRate: metricsB.clickToOpenRate - metricsA.clickToOpenRate,
      bounceRate: metricsB.bounceRate - metricsA.bounceRate,
      unsubscribeRate: metricsB.unsubscribeRate - metricsA.unsubscribeRate,
    };

    return {
      variantA: {
        ...metricsA,
        variantId: variantIdA,
        testId,
      },
      variantB: {
        ...metricsB,
        variantId: variantIdB,
        testId,
      },
      differences,
    };
  }

  // ============================================================
  // Private Helper Methods
  // ============================================================

  private generateId(prefix: string): string {
    return `${prefix}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private validateVariants(variants: ABVariant[]): void {
    if (variants.length < 2) {
      throw new Error('A/B test must have at least 2 variants');
    }

    // Check total weight equals 100
    const totalWeight = variants.reduce((sum, v) => sum + v.weight, 0);
    if (Math.abs(totalWeight - 100) > 0.01) {
      throw new Error(`Variant weights must sum to 100 (got ${totalWeight})`);
    }

    // Check for duplicate variant IDs
    const ids = new Set(variants.map(v => v.id));
    if (ids.size !== variants.length) {
      throw new Error('Duplicate variant IDs found');
    }

    // Ensure exactly one control
    const controlCount = variants.filter(v => v.isControl).length;
    if (controlCount === 0) {
      throw new Error('A/B test must have exactly one control variant');
    }
    if (controlCount > 1) {
      throw new Error('A/B test can only have one control variant');
    }
  }

  private shouldIncludeInTest(userId: string, trafficAllocation: number): boolean {
    if (trafficAllocation >= 100) return true;
    if (trafficAllocation <= 0) return false;

    // Use consistent hashing to determine if user should be included
    const hash = this.hashString(userId);
    const percentage = (hash % 100) + 1; // 1-100

    return percentage <= trafficAllocation;
  }

  private selectVariant(userId: string, variants: ABVariant[]): ABVariant | null {
    if (variants.length === 0) return null;

    // Use consistent hashing to assign variant
    const hash = this.hashString(`${userId}-variant`);
    const random = (hash % 10000) / 100; // 0-100 with 2 decimal precision

    // Select variant based on cumulative weights
    let cumulative = 0;
    for (const variant of variants) {
      cumulative += variant.weight;
      if (random < cumulative) {
        return variant;
      }
    }

    // Fallback to last variant (handles floating point precision issues)
    return variants[variants.length - 1];
  }

  private hashString(str: string): number {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      const char = str.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // Convert to 32-bit integer
    }
    return Math.abs(hash);
  }

  private getAssignmentKey(userId: string, testId: string): string {
    return `${userId}:${testId}`;
  }

  private getMetricValue(metrics: VariantMetrics, metricName: string): number {
    switch (metricName) {
      case 'open_rate':
        return metrics.openRate;
      case 'click_rate':
        return metrics.clickRate;
      case 'conversion_rate':
        return metrics.conversionRate;
      case 'revenue':
        return metrics.totalConversionValue;
      default:
        return 0;
    }
  }
}

// ============================================================
// Singleton Instance
// ============================================================

let defaultManager: ABTestManager | null = null;

export function getABTestManager(analyticsStorage?: IAnalyticsStorage): ABTestManager {
  if (!defaultManager) {
    defaultManager = new ABTestManager(analyticsStorage);
  }
  return defaultManager;
}

export function resetABTestManager(): void {
  defaultManager = null;
}
