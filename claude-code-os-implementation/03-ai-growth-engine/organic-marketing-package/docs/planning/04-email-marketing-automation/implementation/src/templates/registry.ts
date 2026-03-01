/**
 * Template Registry - Central management for all email templates
 *
 * Features:
 * - Load and manage welcome series templates
 * - Load and manage nurture series templates
 * - Template lookup by ID
 * - Template filtering by category
 * - Template metadata and scheduling
 */

import { ContentTemplate } from '../core/ai/content-generator';
import { WELCOME_SERIES_TEMPLATES, getWelcomeSendSchedule } from './welcome-series';
import { NURTURE_SERIES_TEMPLATES, getNurtureSendSchedule } from './nurture-series';
import type { ABTest, ABVariant, ABTestManager } from '../core/analytics/ab-testing';

// ============================================================
// Types
// ============================================================

export interface TemplateMetadata {
  templateId: string;
  name: string;
  description?: string;
  category: string;
  sendDelay?: number;
  sendDelayUnit?: 'days' | 'weeks';
  sequencePosition?: number;
  abTestId?: string;
}

export type TemplateCategory = 'welcome' | 'nurture' | 'promotional' | 'transactional' | 'custom';

export interface TemplateVariant {
  variantId: string;
  templateId: string;
  template: ContentTemplate;
  weight: number;
  isControl?: boolean;
}

export interface TemplateABTest {
  testId: string;
  baseTemplateId: string;
  variants: TemplateVariant[];
  status: 'draft' | 'running' | 'paused' | 'completed';
}

// ============================================================
// Template Registry Class
// ============================================================

export class TemplateRegistry {
  private templates: Map<string, ContentTemplate>;
  private abTestManager?: ABTestManager;
  private templateTests: Map<string, string> = new Map(); // templateId -> testId

  constructor(customTemplates?: ContentTemplate[], abTestManager?: ABTestManager) {
    this.templates = new Map();
    this.abTestManager = abTestManager;

    // Load welcome series templates
    WELCOME_SERIES_TEMPLATES.forEach(template => {
      this.templates.set(template.id, template);
    });

    // Load nurture series templates
    NURTURE_SERIES_TEMPLATES.forEach(template => {
      this.templates.set(template.id, template);
    });

    // Add custom templates if provided
    customTemplates?.forEach(template => {
      this.templates.set(template.id, template);
    });
  }

  /**
   * Set A/B test manager (can be called after construction)
   */
  setABTestManager(manager: ABTestManager): void {
    this.abTestManager = manager;
  }

  /**
   * Get A/B test manager instance
   */
  getABTestManager(): ABTestManager | undefined {
    return this.abTestManager;
  }

  /**
   * Get a template by ID
   */
  getTemplate(id: string): ContentTemplate | undefined {
    return this.templates.get(id);
  }

  /**
   * Get all templates
   */
  listTemplates(): ContentTemplate[] {
    return Array.from(this.templates.values());
  }

  /**
   * Get templates by category
   */
  getTemplatesByCategory(category: TemplateCategory): ContentTemplate[] {
    return this.listTemplates().filter(template => template.category === category);
  }

  /**
   * Get all welcome series templates
   */
  getWelcomeTemplates(): ContentTemplate[] {
    return this.getTemplatesByCategory('welcome');
  }

  /**
   * Get all nurture series templates
   */
  getNurtureTemplates(): ContentTemplate[] {
    return this.getTemplatesByCategory('nurture');
  }

  /**
   * Add a custom template to the registry
   */
  addTemplate(template: ContentTemplate): void {
    this.templates.set(template.id, template);
  }

  /**
   * Remove a template from the registry
   */
  removeTemplate(id: string): boolean {
    return this.templates.delete(id);
  }

  /**
   * Check if a template exists
   */
  hasTemplate(id: string): boolean {
    return this.templates.has(id);
  }

  /**
   * Get total template count
   */
  getTemplateCount(): number {
    return this.templates.size;
  }

  /**
   * Get template metadata with scheduling information
   */
  getTemplateMetadata(id: string): TemplateMetadata | undefined {
    const template = this.getTemplate(id);
    if (!template) {
      return undefined;
    }

    // Get scheduling info from welcome or nurture series
    const welcomeSchedule = getWelcomeSendSchedule().find(s => s.templateId === id);
    const nurtureSchedule = getNurtureSendSchedule().find(s => s.templateId === id);

    const metadata: TemplateMetadata = {
      templateId: template.id,
      name: template.name,
      description: template.description,
      category: template.category,
    };

    if (welcomeSchedule) {
      metadata.sendDelay = welcomeSchedule.delayDays;
      metadata.sendDelayUnit = 'days';
      metadata.sequencePosition = getWelcomeSendSchedule().findIndex(s => s.templateId === id) + 1;
    } else if (nurtureSchedule) {
      metadata.sendDelay = nurtureSchedule.delayWeeks;
      metadata.sendDelayUnit = 'weeks';
      metadata.sequencePosition = getNurtureSendSchedule().findIndex(s => s.templateId === id) + 1;
    }

    return metadata;
  }

  /**
   * Get all template metadata
   */
  listTemplateMetadata(): TemplateMetadata[] {
    return this.listTemplates()
      .map(template => this.getTemplateMetadata(template.id))
      .filter((metadata): metadata is TemplateMetadata => metadata !== undefined);
  }

  /**
   * Get templates by sequence
   */
  getSequenceTemplates(sequenceType: 'welcome' | 'nurture'): ContentTemplate[] {
    if (sequenceType === 'welcome') {
      return WELCOME_SERIES_TEMPLATES;
    } else if (sequenceType === 'nurture') {
      return NURTURE_SERIES_TEMPLATES;
    }
    return [];
  }

  /**
   * Get send schedule for a sequence
   */
  getSequenceSchedule(sequenceType: 'welcome' | 'nurture'): Array<{ templateId: string; delay: number; unit: string; description: string }> {
    if (sequenceType === 'welcome') {
      return getWelcomeSendSchedule().map(schedule => ({
        templateId: schedule.templateId,
        delay: schedule.delayDays,
        unit: 'days',
        description: schedule.description,
      }));
    } else if (sequenceType === 'nurture') {
      return getNurtureSendSchedule().map(schedule => ({
        templateId: schedule.templateId,
        delay: schedule.delayWeeks,
        unit: 'weeks',
        description: schedule.description,
      }));
    }
    return [];
  }

  // ============================================================
  // A/B Testing Integration
  // ============================================================

  /**
   * Create an A/B test for a template with variants
   */
  async createTemplateTest(
    baseTemplateId: string,
    variants: Array<{
      id: string;
      name: string;
      template: ContentTemplate;
      weight: number;
      isControl?: boolean;
    }>,
    testOptions?: {
      name?: string;
      description?: string;
      trafficAllocation?: number;
      primaryMetric?: 'open_rate' | 'click_rate' | 'conversion_rate';
    }
  ): Promise<ABTest | null> {
    if (!this.abTestManager) {
      throw new Error('ABTestManager not configured. Call setABTestManager() first.');
    }

    const baseTemplate = this.getTemplate(baseTemplateId);
    if (!baseTemplate) {
      throw new Error(`Base template ${baseTemplateId} not found`);
    }

    // Validate and add variant templates to registry
    for (const variant of variants) {
      this.addTemplate(variant.template);
    }

    // Create A/B test with ABTestManager
    const abVariants: ABVariant[] = variants.map(v => ({
      id: v.id,
      name: v.name,
      weight: v.weight,
      isControl: v.isControl,
      config: {
        templateId: v.template.id,
      },
    }));

    const test = await this.abTestManager.createTest({
      name: testOptions?.name || `${baseTemplate.name} A/B Test`,
      description: testOptions?.description || `A/B test for template ${baseTemplateId}`,
      type: 'full_email',
      status: 'draft',
      variants: abVariants,
      trafficAllocation: testOptions?.trafficAllocation || 100,
      primaryMetric: testOptions?.primaryMetric || 'open_rate',
      templateId: baseTemplateId,
    });

    // Track template -> test mapping
    this.templateTests.set(baseTemplateId, test.id);

    return test;
  }

  /**
   * Get template for a user based on A/B test assignment
   */
  async getTemplateForUser(
    templateId: string,
    userId: string,
    context?: {
      sequenceId?: string;
      campaignId?: string;
      messageId?: string;
    }
  ): Promise<ContentTemplate | null> {
    // Check if template has an active A/B test
    const testId = this.templateTests.get(templateId);
    if (!testId || !this.abTestManager) {
      // No test - return base template
      return this.getTemplate(templateId) || null;
    }

    // Get test details
    const test = await this.abTestManager.getTest(testId);
    if (!test || test.status !== 'running') {
      // Test not running - return base template
      return this.getTemplate(templateId) || null;
    }

    // Assign variant to user
    const assignedVariant = await this.abTestManager.assignVariant(testId, userId, {
      sequenceId: context?.sequenceId,
      campaignId: context?.campaignId,
      messageId: context?.messageId,
    });

    if (!assignedVariant || !assignedVariant.config.templateId) {
      // Fallback to base template
      return this.getTemplate(templateId) || null;
    }

    // Return variant template
    return this.getTemplate(assignedVariant.config.templateId) || null;
  }

  /**
   * Check if a template has an active A/B test
   */
  hasActiveTest(templateId: string): boolean {
    const testId = this.templateTests.get(templateId);
    return testId !== undefined;
  }

  /**
   * Get A/B test for a template
   */
  async getTemplateTest(templateId: string): Promise<ABTest | null> {
    const testId = this.templateTests.get(templateId);
    if (!testId || !this.abTestManager) {
      return null;
    }

    return this.abTestManager.getTest(testId);
  }

  /**
   * Associate a template with an existing A/B test
   */
  linkTemplateToTest(templateId: string, testId: string): void {
    this.templateTests.set(templateId, testId);
  }

  /**
   * Remove A/B test association from a template
   */
  unlinkTemplateFromTest(templateId: string): boolean {
    return this.templateTests.delete(templateId);
  }

  /**
   * Get all templates that have A/B tests
   */
  getTemplatesWithTests(): string[] {
    return Array.from(this.templateTests.keys());
  }

  /**
   * Get template variants from an A/B test
   */
  async getTemplateVariants(templateId: string): Promise<TemplateVariant[]> {
    const test = await this.getTemplateTest(templateId);
    if (!test) {
      return [];
    }

    return test.variants.map(v => ({
      variantId: v.id,
      templateId: v.config.templateId || templateId,
      template: this.getTemplate(v.config.templateId || templateId)!,
      weight: v.weight,
      isControl: v.isControl,
    })).filter(v => v.template !== undefined);
  }
}

// ============================================================
// Singleton Instance
// ============================================================

/**
 * Default template registry instance
 */
export const defaultTemplateRegistry = new TemplateRegistry();
