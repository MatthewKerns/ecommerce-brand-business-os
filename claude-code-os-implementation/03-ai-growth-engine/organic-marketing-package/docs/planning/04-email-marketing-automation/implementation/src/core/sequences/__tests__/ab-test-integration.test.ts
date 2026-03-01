/**
 * A/B Test Integration Tests
 *
 * Tests integration between:
 * - TemplateRegistry and ABTestManager
 * - SequenceEngine and TemplateRegistry
 * - End-to-end A/B testing flow
 */

import { describe, it, expect, beforeEach } from '@jest/globals';
import { SequenceEngine } from '../sequence-engine';
import { TemplateRegistry } from '@/templates/registry';
import { ABTestManager } from '@/core/analytics/ab-testing';
import { MemoryAnalyticsStorage } from '@/core/analytics/storage';
import type { ContentTemplate } from '@/core/ai/content-generator';
import type { Lead } from '@/types/lead';

// ============================================================
// Test Setup
// ============================================================

describe('A/B Test Integration', () => {
  let sequenceEngine: SequenceEngine;
  let templateRegistry: TemplateRegistry;
  let abTestManager: ABTestManager;
  let analyticsStorage: MemoryAnalyticsStorage;

  beforeEach(() => {
    analyticsStorage = new MemoryAnalyticsStorage();
    abTestManager = new ABTestManager(analyticsStorage);
    templateRegistry = new TemplateRegistry([], abTestManager);
    sequenceEngine = new SequenceEngine(analyticsStorage, templateRegistry);
  });

  // ============================================================
  // Template Registry A/B Test Integration
  // ============================================================

  describe('Template Registry A/B Test Integration', () => {
    it('should link ABTestManager to TemplateRegistry', () => {
      const registry = new TemplateRegistry();
      const manager = new ABTestManager(analyticsStorage);

      registry.setABTestManager(manager);
      expect(registry.getABTestManager()).toBe(manager);
    });

    it('should create ab test for template with variants', async () => {
      // Create base template
      const baseTemplate: ContentTemplate = {
        id: 'welcome_1',
        name: 'Welcome Email',
        description: 'Welcome new subscribers',
        category: 'welcome',
        systemPrompt: 'Write a welcome email',
        userPromptTemplate: 'Welcome {{name}}',
        outputFormat: 'html',
        requiredVariables: ['name'],
        tags: ['welcome'],
      };

      templateRegistry.addTemplate(baseTemplate);

      // Create variant templates
      const variantA: ContentTemplate = {
        ...baseTemplate,
        id: 'welcome_1_variant_a',
        name: 'Welcome Email - Variant A',
      };

      const variantB: ContentTemplate = {
        ...baseTemplate,
        id: 'welcome_1_variant_b',
        name: 'Welcome Email - Variant B',
      };

      // Create A/B test
      const test = await templateRegistry.createTemplateTest(
        'welcome_1',
        [
          {
            id: 'control',
            name: 'Control',
            template: baseTemplate,
            weight: 50,
            isControl: true,
          },
          {
            id: 'variant_a',
            name: 'Variant A',
            template: variantA,
            weight: 50,
          },
        ],
        {
          name: 'Welcome Email Test',
          trafficAllocation: 100,
          primaryMetric: 'open_rate',
        }
      );

      expect(test).toBeDefined();
      expect(test?.name).toBe('Welcome Email Test');
      expect(test?.variants).toHaveLength(2);
      expect(test?.templateId).toBe('welcome_1');
    });

    it('should get template for user with ab test integration', async () => {
      const baseTemplate: ContentTemplate = {
        id: 'welcome_1',
        name: 'Welcome Email',
        description: 'Welcome new subscribers',
        category: 'welcome',
        systemPrompt: 'Write a welcome email',
        userPromptTemplate: 'Welcome {{name}}',
        outputFormat: 'html',
        requiredVariables: ['name'],
        tags: ['welcome'],
      };

      templateRegistry.addTemplate(baseTemplate);

      const variantA: ContentTemplate = {
        ...baseTemplate,
        id: 'welcome_1_variant_a',
        name: 'Welcome Email - Variant A',
      };

      // Create and start A/B test
      const test = await templateRegistry.createTemplateTest(
        'welcome_1',
        [
          {
            id: 'control',
            name: 'Control',
            template: baseTemplate,
            weight: 50,
            isControl: true,
          },
          {
            id: 'variant_a',
            name: 'Variant A',
            template: variantA,
            weight: 50,
          },
        ]
      );

      expect(test).toBeDefined();
      await abTestManager.startTest(test!.id);

      // Get template for user (should return variant based on assignment)
      const template = await templateRegistry.getTemplateForUser(
        'welcome_1',
        'user123',
        { sequenceId: 'seq_1' }
      );

      expect(template).toBeDefined();
      expect(['welcome_1', 'welcome_1_variant_a']).toContain(template?.id);
    });

    it('should handle ab test integration for template variants', async () => {
      const baseTemplate: ContentTemplate = {
        id: 'nurture_1',
        name: 'Nurture Email',
        category: 'nurture',
        systemPrompt: 'Write a nurture email',
        userPromptTemplate: 'Nurture {{name}}',
        outputFormat: 'html',
        requiredVariables: ['name'],
        tags: ['nurture'],
      };

      templateRegistry.addTemplate(baseTemplate);

      const variantA: ContentTemplate = {
        ...baseTemplate,
        id: 'nurture_1_variant_a',
      };

      const variantB: ContentTemplate = {
        ...baseTemplate,
        id: 'nurture_1_variant_b',
      };

      // Create test
      const test = await templateRegistry.createTemplateTest(
        'nurture_1',
        [
          { id: 'control', name: 'Control', template: baseTemplate, weight: 34, isControl: true },
          { id: 'variant_a', name: 'Variant A', template: variantA, weight: 33 },
          { id: 'variant_b', name: 'Variant B', template: variantB, weight: 33 },
        ]
      );

      expect(test).toBeDefined();
      await abTestManager.startTest(test!.id);

      // Get variants
      const variants = await templateRegistry.getTemplateVariants('nurture_1');
      expect(variants).toHaveLength(3);
      expect(variants.find(v => v.isControl)).toBeDefined();
    });

    it('should check if template has active ab test integration', async () => {
      const template: ContentTemplate = {
        id: 'test_1',
        name: 'Test Template',
        category: 'welcome',
        systemPrompt: 'Test',
        userPromptTemplate: 'Test',
        outputFormat: 'html',
        requiredVariables: [],
      };

      templateRegistry.addTemplate(template);

      expect(templateRegistry.hasActiveTest('test_1')).toBe(false);

      await templateRegistry.createTemplateTest(
        'test_1',
        [
          { id: 'control', name: 'Control', template, weight: 50, isControl: true },
          { id: 'variant', name: 'Variant', template, weight: 50 },
        ]
      );

      expect(templateRegistry.hasActiveTest('test_1')).toBe(true);
    });
  });

  // ============================================================
  // Sequence Engine A/B Test Integration
  // ============================================================

  describe('Sequence Engine A/B Test Integration', () => {
    it('should integrate ab test manager with sequence engine', () => {
      const engine = new SequenceEngine(analyticsStorage);
      expect(engine.getABTestManager()).toBeDefined();
    });

    it('should integrate template registry with sequence engine for ab testing', () => {
      const registry = new TemplateRegistry();
      const engine = new SequenceEngine(analyticsStorage, registry);

      expect(engine.getTemplateRegistry()).toBe(registry);
      expect(registry.getABTestManager()).toBeDefined();
    });

    it('should get template for step with ab test integration', async () => {
      // Create template
      const template: ContentTemplate = {
        id: 'welcome_1',
        name: 'Welcome Email',
        category: 'welcome',
        systemPrompt: 'Write a welcome email',
        userPromptTemplate: 'Welcome {{name}}',
        outputFormat: 'html',
        requiredVariables: ['name'],
      };

      templateRegistry.addTemplate(template);

      // Create sequence with template step
      const sequence = await sequenceEngine.createSequence({
        name: 'Welcome Sequence',
        status: 'active',
        triggerType: 'immediate',
        steps: [
          {
            id: 'step_1',
            type: 'email',
            name: 'Welcome Email',
            config: {
              templateId: 'welcome_1',
            },
          },
        ],
        firstStepId: 'step_1',
        settings: {},
      });

      // Create lead and enroll
      const lead: Lead = {
        id: 'lead_123',
        email: 'test@example.com',
        status: 'active',
        source: 'website',
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      const enrollment = await sequenceEngine.enrollLead(lead, sequence.id);
      expect(enrollment).toBeDefined();

      // Get template for step
      const stepTemplate = await sequenceEngine.getTemplateForStep(
        enrollment!.id,
        'step_1'
      );

      expect(stepTemplate).toBeDefined();
      expect(stepTemplate?.id).toBe('welcome_1');
    });

    it('should create ab test for sequence step template integration', async () => {
      // Create base template
      const baseTemplate: ContentTemplate = {
        id: 'welcome_1',
        name: 'Welcome Email',
        category: 'welcome',
        systemPrompt: 'Write a welcome email',
        userPromptTemplate: 'Welcome {{name}}',
        outputFormat: 'html',
        requiredVariables: ['name'],
      };

      templateRegistry.addTemplate(baseTemplate);

      // Create sequence
      const sequence = await sequenceEngine.createSequence({
        name: 'Welcome Sequence',
        status: 'active',
        triggerType: 'immediate',
        steps: [
          {
            id: 'step_1',
            type: 'email',
            name: 'Welcome Email',
            config: {
              templateId: 'welcome_1',
            },
          },
        ],
        firstStepId: 'step_1',
        settings: {},
      });

      // Create variant
      const variant: ContentTemplate = {
        ...baseTemplate,
        id: 'welcome_1_variant',
      };

      // Create A/B test for step
      const test = await sequenceEngine.createStepTemplateTest(
        sequence.id,
        'step_1',
        [
          {
            id: 'control',
            name: 'Control',
            template: baseTemplate,
            weight: 50,
            isControl: true,
          },
          {
            id: 'variant',
            name: 'Variant',
            template: variant,
            weight: 50,
          },
        ],
        {
          primaryMetric: 'open_rate',
        }
      );

      expect(test).toBeDefined();
      expect(test?.sequenceId).toBe(sequence.id);
      expect(test?.variants).toHaveLength(2);
    });

    it('should get ab test results for sequence step integration', async () => {
      // Create template
      const template: ContentTemplate = {
        id: 'welcome_1',
        name: 'Welcome Email',
        category: 'welcome',
        systemPrompt: 'Write a welcome email',
        userPromptTemplate: 'Welcome {{name}}',
        outputFormat: 'html',
        requiredVariables: ['name'],
      };

      templateRegistry.addTemplate(template);

      // Create sequence
      const sequence = await sequenceEngine.createSequence({
        name: 'Welcome Sequence',
        status: 'active',
        triggerType: 'immediate',
        steps: [
          {
            id: 'step_1',
            type: 'email',
            name: 'Welcome Email',
            config: {
              templateId: 'welcome_1',
            },
          },
        ],
        firstStepId: 'step_1',
        settings: {},
      });

      // Create variant
      const variant: ContentTemplate = {
        ...template,
        id: 'welcome_1_variant',
      };

      // Create and start test
      const test = await sequenceEngine.createStepTemplateTest(
        sequence.id,
        'step_1',
        [
          { id: 'control', name: 'Control', template, weight: 50, isControl: true },
          { id: 'variant', name: 'Variant', template: variant, weight: 50 },
        ]
      );

      expect(test).toBeDefined();
      await sequenceEngine.startStepTest(sequence.id, 'step_1');

      // Get test results
      const results = await sequenceEngine.getStepTestResults(sequence.id, 'step_1');

      expect(results).toBeDefined();
      expect(results?.testId).toBe(test?.id);
      expect(results?.variants).toHaveLength(2);
    });

    it('should handle ab test integration across entire sequence', async () => {
      // Create templates
      const template1: ContentTemplate = {
        id: 'welcome_1',
        name: 'Welcome Email 1',
        category: 'welcome',
        systemPrompt: 'Write first welcome email',
        userPromptTemplate: 'Welcome {{name}}',
        outputFormat: 'html',
        requiredVariables: ['name'],
      };

      const template2: ContentTemplate = {
        id: 'welcome_2',
        name: 'Welcome Email 2',
        category: 'welcome',
        systemPrompt: 'Write second welcome email',
        userPromptTemplate: 'Follow up {{name}}',
        outputFormat: 'html',
        requiredVariables: ['name'],
      };

      templateRegistry.addTemplate(template1);
      templateRegistry.addTemplate(template2);

      // Create sequence with multiple steps
      const sequence = await sequenceEngine.createSequence({
        name: 'Welcome Sequence',
        status: 'active',
        triggerType: 'immediate',
        steps: [
          {
            id: 'step_1',
            type: 'email',
            name: 'Welcome Email 1',
            config: { templateId: 'welcome_1' },
            nextSteps: ['step_2'],
          },
          {
            id: 'step_2',
            type: 'email',
            name: 'Welcome Email 2',
            config: { templateId: 'welcome_2' },
          },
        ],
        firstStepId: 'step_1',
        settings: {},
      });

      // Create A/B tests for both steps
      const variant1: ContentTemplate = { ...template1, id: 'welcome_1_variant' };
      const variant2: ContentTemplate = { ...template2, id: 'welcome_2_variant' };

      const test1 = await sequenceEngine.createStepTemplateTest(
        sequence.id,
        'step_1',
        [
          { id: 'control_1', name: 'Control 1', template: template1, weight: 50, isControl: true },
          { id: 'variant_1', name: 'Variant 1', template: variant1, weight: 50 },
        ]
      );

      const test2 = await sequenceEngine.createStepTemplateTest(
        sequence.id,
        'step_2',
        [
          { id: 'control_2', name: 'Control 2', template: template2, weight: 50, isControl: true },
          { id: 'variant_2', name: 'Variant 2', template: variant2, weight: 50 },
        ]
      );

      expect(test1).toBeDefined();
      expect(test2).toBeDefined();

      // Get all sequence tests
      const tests = await sequenceEngine.getSequenceTests(sequence.id);
      expect(tests).toHaveLength(2);
    });
  });

  // ============================================================
  // End-to-End A/B Test Integration Flow
  // ============================================================

  describe('End-to-End A/B Test Integration Flow', () => {
    it('should handle complete ab test integration workflow', async () => {
      // 1. Setup templates
      const baseTemplate: ContentTemplate = {
        id: 'welcome_1',
        name: 'Welcome Email',
        category: 'welcome',
        systemPrompt: 'Write a welcome email',
        userPromptTemplate: 'Welcome {{name}}',
        outputFormat: 'html',
        requiredVariables: ['name'],
      };

      const variantTemplate: ContentTemplate = {
        ...baseTemplate,
        id: 'welcome_1_variant',
        name: 'Welcome Email - Variant',
      };

      templateRegistry.addTemplate(baseTemplate);
      templateRegistry.addTemplate(variantTemplate);

      // 2. Create sequence
      const sequence = await sequenceEngine.createSequence({
        name: 'Welcome Sequence',
        status: 'active',
        triggerType: 'immediate',
        steps: [
          {
            id: 'step_1',
            type: 'email',
            name: 'Welcome Email',
            config: { templateId: 'welcome_1' },
          },
        ],
        firstStepId: 'step_1',
        settings: {},
      });

      // 3. Create A/B test
      const test = await sequenceEngine.createStepTemplateTest(
        sequence.id,
        'step_1',
        [
          {
            id: 'control',
            name: 'Control',
            template: baseTemplate,
            weight: 50,
            isControl: true,
          },
          {
            id: 'variant',
            name: 'Variant',
            template: variantTemplate,
            weight: 50,
          },
        ],
        { primaryMetric: 'open_rate' }
      );

      expect(test).toBeDefined();

      // 4. Start test
      const started = await sequenceEngine.startStepTest(sequence.id, 'step_1');
      expect(started).toBe(true);

      // 5. Enroll lead
      const lead: Lead = {
        id: 'lead_123',
        email: 'test@example.com',
        status: 'active',
        source: 'website',
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      const enrollment = await sequenceEngine.enrollLead(lead, sequence.id);
      expect(enrollment).toBeDefined();

      // 6. Get template for step (should be variant based on A/B test)
      const template = await sequenceEngine.getTemplateForStep(
        enrollment!.id,
        'step_1'
      );

      expect(template).toBeDefined();
      expect(['welcome_1', 'welcome_1_variant']).toContain(template?.id);

      // 7. Get test results
      const results = await sequenceEngine.getStepTestResults(sequence.id, 'step_1');
      expect(results).toBeDefined();
      expect(results?.status).toBe('running');
    });
  });
});
