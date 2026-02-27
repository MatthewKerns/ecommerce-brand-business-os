/**
 * Sequence Engine - Manages email sequences and automation workflows
 *
 * Features:
 * - Configurable sequence patterns
 * - Scheduling and timing logic
 * - Conditional branching
 * - A/B testing support
 * - Pause/resume functionality
 * - Performance metrics and reporting
 */

import type { Lead } from '@/types/lead';
import type { IAnalyticsStorage } from '@/core/analytics/storage';
import { MetricsAggregationEngine } from '@/core/analytics/metrics';
import type {
  SequencePerformanceReport,
  PerformanceReportOptions,
} from '@/core/analytics/metrics';

// ============================================================
// Types
// ============================================================

export type SequenceStatus = 'draft' | 'active' | 'paused' | 'completed' | 'archived';

export type EmailTrigger =
  | 'immediate'
  | 'delay'
  | 'time_based'
  | 'action_based'
  | 'condition_based';

export type SequenceStepType =
  | 'email'
  | 'wait'
  | 'condition'
  | 'action'
  | 'ab_test'
  | 'goal';

export interface SequenceStep {
  id: string;
  type: SequenceStepType;
  name: string;
  config: SequenceStepConfig;
  nextSteps?: string[]; // IDs of possible next steps
}

export interface SequenceStepConfig {
  // For 'email' type
  templateId?: string;
  subject?: string;
  body?: string;
  fromName?: string;
  replyTo?: string;

  // For 'wait' type
  duration?: number; // in hours
  skipWeekends?: boolean;
  skipHolidays?: boolean;
  timezone?: string;

  // For 'condition' type
  conditions?: SequenceCondition[];
  trueStep?: string;
  falseStep?: string;

  // For 'ab_test' type
  variants?: Array<{
    id: string;
    weight: number; // 0-100
    stepId: string;
  }>;

  // For 'action' type
  actionType?: 'update_field' | 'add_tag' | 'remove_tag' | 'change_status' | 'webhook';
  actionConfig?: Record<string, any>;

  // For 'goal' type
  goalType?: 'conversion' | 'engagement' | 'custom';
  goalConfig?: Record<string, any>;
}

export interface SequenceCondition {
  field: string;
  operator: 'equals' | 'not_equals' | 'contains' | 'greater_than' | 'less_than' | 'exists' | 'not_exists';
  value?: any;
  logic?: 'and' | 'or'; // How to combine with other conditions
}

export interface EmailSequence {
  id: string;
  name: string;
  description?: string;
  status: SequenceStatus;

  // Sequence configuration
  triggerType: EmailTrigger;
  entryConditions?: SequenceCondition[];
  exitConditions?: SequenceCondition[];

  // Steps
  steps: SequenceStep[];
  firstStepId: string;

  // Settings
  settings: {
    sendingDays?: number[]; // 0=Sunday, 6=Saturday
    sendingHours?: { start: number; end: number }; // 24-hour format
    timezone?: string;
    maxEmailsPerDay?: number;
    stopOnReply?: boolean;
    stopOnConversion?: boolean;
    allowReEntry?: boolean;
    reEntryDelay?: number; // hours
  };

  // Metadata
  createdAt: Date;
  updatedAt: Date;
  createdBy?: string;
  tags?: string[];

  // Performance metrics
  metrics?: {
    totalEnrolled: number;
    currentlyActive: number;
    completed: number;
    converted: number;
    unsubscribed: number;
    avgCompletionTime?: number; // hours
    conversionRate?: number; // percentage
  };
}

export interface SequenceEnrollment {
  id: string;
  leadId: string;
  sequenceId: string;
  status: 'active' | 'paused' | 'completed' | 'exited';

  currentStepId?: string;
  currentStepIndex: number;
  stepsCompleted: string[];

  enrolledAt: Date;
  lastActivityAt?: Date;
  completedAt?: Date;
  exitedAt?: Date;
  exitReason?: 'completed' | 'manual' | 'condition_met' | 'unsubscribed' | 'bounced' | 'replied';

  // Step execution history
  history: Array<{
    stepId: string;
    executedAt: Date;
    result: 'success' | 'skipped' | 'failed';
    details?: Record<string, any>;
  }>;

  // A/B test assignments
  abTestAssignments?: Record<string, string>; // stepId -> variantId

  // Custom data
  customData?: Record<string, any>;
}

// ============================================================
// Sequence Engine Class
// ============================================================

export class SequenceEngine {
  private sequences: Map<string, EmailSequence> = new Map();
  private enrollments: Map<string, SequenceEnrollment> = new Map();
  private leadEnrollments: Map<string, Set<string>> = new Map(); // leadId -> enrollmentIds
  private metricsEngine?: MetricsAggregationEngine;

  constructor(analyticsStorage?: IAnalyticsStorage) {
    if (analyticsStorage) {
      this.metricsEngine = new MetricsAggregationEngine(analyticsStorage);
    }
  }

  /**
   * Set analytics storage (can be called after construction)
   */
  setAnalyticsStorage(storage: IAnalyticsStorage): void {
    this.metricsEngine = new MetricsAggregationEngine(storage);
  }

  /**
   * Create a new sequence
   */
  async createSequence(sequence: Omit<EmailSequence, 'id' | 'createdAt' | 'updatedAt'>): Promise<EmailSequence> {
    const newSequence: EmailSequence = {
      ...sequence,
      id: this.generateId('seq'),
      createdAt: new Date(),
      updatedAt: new Date(),
      metrics: {
        totalEnrolled: 0,
        currentlyActive: 0,
        completed: 0,
        converted: 0,
        unsubscribed: 0,
      },
    };

    this.sequences.set(newSequence.id, newSequence);
    return newSequence;
  }

  /**
   * Update a sequence
   */
  async updateSequence(
    id: string,
    updates: Partial<Omit<EmailSequence, 'id' | 'createdAt'>>
  ): Promise<EmailSequence | null> {
    const sequence = this.sequences.get(id);
    if (!sequence) return null;

    const updatedSequence = {
      ...sequence,
      ...updates,
      updatedAt: new Date(),
    };

    this.sequences.set(id, updatedSequence);
    return updatedSequence;
  }

  /**
   * Get sequence by ID
   */
  async getSequence(id: string): Promise<EmailSequence | null> {
    return this.sequences.get(id) || null;
  }

  /**
   * List all sequences
   */
  async listSequences(filter?: {
    status?: SequenceStatus;
    tags?: string[];
  }): Promise<EmailSequence[]> {
    let sequences = Array.from(this.sequences.values());

    if (filter?.status) {
      sequences = sequences.filter(s => s.status === filter.status);
    }

    if (filter?.tags && filter.tags.length > 0) {
      sequences = sequences.filter(s =>
        s.tags?.some(tag => filter.tags!.includes(tag))
      );
    }

    return sequences;
  }

  /**
   * Enroll a lead in a sequence
   */
  async enrollLead(
    lead: Lead,
    sequenceId: string,
    options?: {
      startAtStep?: string;
      customData?: Record<string, any>;
      skipEntryConditions?: boolean;
    }
  ): Promise<SequenceEnrollment | null> {
    const sequence = this.sequences.get(sequenceId);
    if (!sequence || sequence.status !== 'active') {
      return null;
    }

    // Check if already enrolled
    const existingEnrollments = this.leadEnrollments.get(lead.id) || new Set();
    for (const enrollmentId of existingEnrollments) {
      const enrollment = this.enrollments.get(enrollmentId);
      if (enrollment?.sequenceId === sequenceId && enrollment.status === 'active') {
        // Already actively enrolled in this sequence
        if (!sequence.settings.allowReEntry) {
          return null;
        }

        // Check re-entry delay
        if (sequence.settings.reEntryDelay && enrollment.exitedAt) {
          const hoursSinceExit = (Date.now() - enrollment.exitedAt.getTime()) / (1000 * 60 * 60);
          if (hoursSinceExit < sequence.settings.reEntryDelay) {
            return null;
          }
        }
      }
    }

    // Check entry conditions
    if (!options?.skipEntryConditions && sequence.entryConditions) {
      if (!this.evaluateConditions(lead, sequence.entryConditions)) {
        return null;
      }
    }

    // Create enrollment
    const enrollment: SequenceEnrollment = {
      id: this.generateId('enr'),
      leadId: lead.id,
      sequenceId,
      status: 'active',
      currentStepId: options?.startAtStep || sequence.firstStepId,
      currentStepIndex: 0,
      stepsCompleted: [],
      enrolledAt: new Date(),
      history: [],
      customData: options?.customData,
    };

    // Store enrollment
    this.enrollments.set(enrollment.id, enrollment);

    // Track lead enrollment
    if (!this.leadEnrollments.has(lead.id)) {
      this.leadEnrollments.set(lead.id, new Set());
    }
    this.leadEnrollments.get(lead.id)!.add(enrollment.id);

    // Update sequence metrics
    if (sequence.metrics) {
      sequence.metrics.totalEnrolled++;
      sequence.metrics.currentlyActive++;
    }

    return enrollment;
  }

  /**
   * Get next step to execute for an enrollment
   */
  async getNextStep(enrollmentId: string): Promise<SequenceStep | null> {
    const enrollment = this.enrollments.get(enrollmentId);
    if (!enrollment || enrollment.status !== 'active') {
      return null;
    }

    const sequence = this.sequences.get(enrollment.sequenceId);
    if (!sequence) return null;

    // Get current step
    const currentStep = sequence.steps.find(s => s.id === enrollment.currentStepId);
    if (!currentStep) return null;

    // Check if should execute based on timing
    if (!this.shouldExecuteNow(sequence, enrollment)) {
      return null;
    }

    return currentStep;
  }

  /**
   * Execute a step for an enrollment
   */
  async executeStep(
    enrollmentId: string,
    stepId: string,
    result: 'success' | 'skipped' | 'failed',
    details?: Record<string, any>
  ): Promise<boolean> {
    const enrollment = this.enrollments.get(enrollmentId);
    if (!enrollment || enrollment.status !== 'active') {
      return false;
    }

    const sequence = this.sequences.get(enrollment.sequenceId);
    if (!sequence) return false;

    const step = sequence.steps.find(s => s.id === stepId);
    if (!step) return false;

    // Record execution
    enrollment.history.push({
      stepId,
      executedAt: new Date(),
      result,
      details,
    });

    enrollment.lastActivityAt = new Date();

    // Mark step as completed if successful
    if (result === 'success') {
      enrollment.stepsCompleted.push(stepId);
    }

    // Determine next step
    const nextStepId = await this.determineNextStep(enrollment, sequence, step, details);

    if (nextStepId) {
      enrollment.currentStepId = nextStepId;
      enrollment.currentStepIndex++;
    } else {
      // No more steps - complete enrollment
      enrollment.status = 'completed';
      enrollment.completedAt = new Date();
      enrollment.exitReason = 'completed';

      // Update metrics
      if (sequence.metrics) {
        sequence.metrics.currentlyActive--;
        sequence.metrics.completed++;
      }
    }

    this.enrollments.set(enrollmentId, enrollment);
    return true;
  }

  /**
   * Pause an enrollment
   */
  async pauseEnrollment(enrollmentId: string): Promise<boolean> {
    const enrollment = this.enrollments.get(enrollmentId);
    if (!enrollment || enrollment.status !== 'active') {
      return false;
    }

    enrollment.status = 'paused';
    this.enrollments.set(enrollmentId, enrollment);

    // Update metrics
    const sequence = this.sequences.get(enrollment.sequenceId);
    if (sequence?.metrics) {
      sequence.metrics.currentlyActive--;
    }

    return true;
  }

  /**
   * Resume an enrollment
   */
  async resumeEnrollment(enrollmentId: string): Promise<boolean> {
    const enrollment = this.enrollments.get(enrollmentId);
    if (!enrollment || enrollment.status !== 'paused') {
      return false;
    }

    enrollment.status = 'active';
    this.enrollments.set(enrollmentId, enrollment);

    // Update metrics
    const sequence = this.sequences.get(enrollment.sequenceId);
    if (sequence?.metrics) {
      sequence.metrics.currentlyActive++;
    }

    return true;
  }

  /**
   * Exit a lead from a sequence
   */
  async exitEnrollment(
    enrollmentId: string,
    reason: SequenceEnrollment['exitReason']
  ): Promise<boolean> {
    const enrollment = this.enrollments.get(enrollmentId);
    if (!enrollment) return false;

    enrollment.status = 'exited';
    enrollment.exitedAt = new Date();
    enrollment.exitReason = reason;
    this.enrollments.set(enrollmentId, enrollment);

    // Update metrics
    const sequence = this.sequences.get(enrollment.sequenceId);
    if (sequence?.metrics && enrollment.status === 'active') {
      sequence.metrics.currentlyActive--;
      if (reason === 'unsubscribed') {
        sequence.metrics.unsubscribed++;
      }
    }

    return true;
  }

  /**
   * Get enrollments for a lead
   */
  async getLeadEnrollments(
    leadId: string,
    filter?: { status?: SequenceEnrollment['status'] }
  ): Promise<SequenceEnrollment[]> {
    const enrollmentIds = this.leadEnrollments.get(leadId) || new Set();
    let enrollments: SequenceEnrollment[] = [];

    for (const id of enrollmentIds) {
      const enrollment = this.enrollments.get(id);
      if (enrollment) {
        if (!filter?.status || enrollment.status === filter.status) {
          enrollments.push(enrollment);
        }
      }
    }

    return enrollments;
  }

  // ============================================================
  // Performance Metrics & Reporting
  // ============================================================

  /**
   * Get performance report for a sequence
   */
  async getSequencePerformanceReport(
    sequenceId: string,
    options: Omit<PerformanceReportOptions, 'sequenceId'> = {}
  ): Promise<SequencePerformanceReport | null> {
    if (!this.metricsEngine) {
      throw new Error('Analytics storage not configured. Call setAnalyticsStorage() first.');
    }

    const sequence = this.sequences.get(sequenceId);
    if (!sequence) {
      return null;
    }

    return this.metricsEngine.generateSequenceReport(sequenceId, options);
  }

  /**
   * Get performance reports for all active sequences
   */
  async getAllSequencePerformanceReports(
    options: Omit<PerformanceReportOptions, 'sequenceId'> = {}
  ): Promise<SequencePerformanceReport[]> {
    if (!this.metricsEngine) {
      throw new Error('Analytics storage not configured. Call setAnalyticsStorage() first.');
    }

    const activeSequences = Array.from(this.sequences.values()).filter(
      s => s.status === 'active'
    );

    const reports = await Promise.all(
      activeSequences.map(seq =>
        this.metricsEngine!.generateSequenceReport(seq.id, options)
      )
    );

    return reports;
  }

  /**
   * Update sequence metrics from analytics
   */
  async updateSequenceMetrics(sequenceId: string): Promise<boolean> {
    if (!this.metricsEngine) {
      throw new Error('Analytics storage not configured. Call setAnalyticsStorage() first.');
    }

    const sequence = this.sequences.get(sequenceId);
    if (!sequence) {
      return false;
    }

    try {
      const report = await this.metricsEngine.generateSequenceReport(sequenceId);

      // Update sequence metrics
      sequence.metrics = {
        totalEnrolled: sequence.metrics?.totalEnrolled || 0,
        currentlyActive: sequence.metrics?.currentlyActive || 0,
        completed: sequence.metrics?.completed || 0,
        converted: report.summary.totalConverted,
        unsubscribed: report.summary.totalUnsubscribed,
        avgCompletionTime: report.summary.averageTimeToConversion,
        conversionRate: report.summary.conversionRate,
      };

      sequence.updatedAt = new Date();
      this.sequences.set(sequenceId, sequence);

      return true;
    } catch (error) {
      return false;
    }
  }

  /**
   * Get sequence leaderboard by performance
   */
  async getSequenceLeaderboard(
    metric: 'conversionRate' | 'openRate' | 'clickRate' = 'conversionRate',
    limit: number = 10,
    options: Omit<PerformanceReportOptions, 'sequenceId'> = {}
  ): Promise<Array<{ sequence: EmailSequence; report: SequencePerformanceReport }>> {
    if (!this.metricsEngine) {
      throw new Error('Analytics storage not configured. Call setAnalyticsStorage() first.');
    }

    const sequences = Array.from(this.sequences.values());
    const reportsWithSequences = await Promise.all(
      sequences.map(async seq => ({
        sequence: seq,
        report: await this.metricsEngine!.generateSequenceReport(seq.id, options),
      }))
    );

    // Sort by metric
    reportsWithSequences.sort((a, b) => {
      const aValue = a.report.summary[metric];
      const bValue = b.report.summary[metric];
      return bValue - aValue;
    });

    return reportsWithSequences.slice(0, limit);
  }

  // ============================================================
  // Private Methods
  // ============================================================

  private generateId(prefix: string): string {
    return `${prefix}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private evaluateConditions(lead: Lead, conditions: SequenceCondition[]): boolean {
    let result = true;
    let logic: 'and' | 'or' = 'and';

    for (const condition of conditions) {
      const conditionMet = this.evaluateCondition(lead, condition);

      if (logic === 'and') {
        result = result && conditionMet;
      } else {
        result = result || conditionMet;
      }

      logic = condition.logic || 'and';
    }

    return result;
  }

  private evaluateCondition(lead: Lead, condition: SequenceCondition): boolean {
    const value = this.getFieldValue(lead, condition.field);

    switch (condition.operator) {
      case 'equals':
        return value === condition.value;
      case 'not_equals':
        return value !== condition.value;
      case 'contains':
        return String(value).includes(String(condition.value));
      case 'greater_than':
        return Number(value) > Number(condition.value);
      case 'less_than':
        return Number(value) < Number(condition.value);
      case 'exists':
        return value !== null && value !== undefined;
      case 'not_exists':
        return value === null || value === undefined;
      default:
        return false;
    }
  }

  private getFieldValue(lead: Lead, field: string): any {
    // Handle nested fields
    const parts = field.split('.');
    let value: any = lead;

    for (const part of parts) {
      if (value === null || value === undefined) return null;
      value = value[part];
    }

    return value;
  }

  private shouldExecuteNow(sequence: EmailSequence, enrollment: SequenceEnrollment): boolean {
    const now = new Date();
    const settings = sequence.settings;

    // Check sending days
    if (settings.sendingDays && settings.sendingDays.length > 0) {
      const currentDay = now.getDay();
      if (!settings.sendingDays.includes(currentDay)) {
        return false;
      }
    }

    // Check sending hours
    if (settings.sendingHours) {
      const currentHour = now.getHours();
      if (currentHour < settings.sendingHours.start || currentHour >= settings.sendingHours.end) {
        return false;
      }
    }

    // Check max emails per day
    if (settings.maxEmailsPerDay) {
      const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
      const emailsSentToday = enrollment.history.filter(h => {
        const executedDate = new Date(h.executedAt);
        return executedDate >= today && h.result === 'success';
      }).length;

      if (emailsSentToday >= settings.maxEmailsPerDay) {
        return false;
      }
    }

    return true;
  }

  private async determineNextStep(
    enrollment: SequenceEnrollment,
    sequence: EmailSequence,
    currentStep: SequenceStep,
    executionDetails?: Record<string, any>
  ): Promise<string | null> {
    // Handle conditional branching
    if (currentStep.type === 'condition' && currentStep.config.conditions) {
      const lead = { id: enrollment.leadId } as Lead; // In real implementation, fetch lead
      const conditionsMet = this.evaluateConditions(lead, currentStep.config.conditions);
      return conditionsMet ? currentStep.config.trueStep! : currentStep.config.falseStep!;
    }

    // Handle A/B test
    if (currentStep.type === 'ab_test' && currentStep.config.variants) {
      // Check if already assigned
      const assignedVariant = enrollment.abTestAssignments?.[currentStep.id];
      if (assignedVariant) {
        return assignedVariant;
      }

      // Assign variant based on weights
      const random = Math.random() * 100;
      let cumulative = 0;
      for (const variant of currentStep.config.variants) {
        cumulative += variant.weight;
        if (random < cumulative) {
          // Store assignment
          if (!enrollment.abTestAssignments) {
            enrollment.abTestAssignments = {};
          }
          enrollment.abTestAssignments[currentStep.id] = variant.stepId;
          return variant.stepId;
        }
      }
    }

    // Default: use first next step
    return currentStep.nextSteps?.[0] || null;
  }
}