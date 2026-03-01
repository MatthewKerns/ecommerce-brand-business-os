/**
 * Tests for Personalization Rules Engine
 */

import {
  PersonalizationRulesEngine,
  createSourceRule,
  createInterestRule,
  createCustomFieldRule,
  createSegmentRule,
  type PersonalizationRule,
  type PersonalizationCondition,
  type PersonalizationTransformation,
} from '../rules-engine';
import type { Lead, LeadSource } from '@/types/lead';

// ============================================================
// Test Helper Functions
// ============================================================

function createMockLead(overrides?: Partial<Lead>): Lead {
  return {
    id: 'lead_123',
    email: 'test@example.com',
    status: 'new',
    source: 'website' as LeadSource,
    createdAt: new Date(),
    updatedAt: new Date(),
    tags: [],
    segments: [],
    customFields: [],
    engagement: {
      emailsSent: 0,
      emailsOpened: 0,
      emailsClicked: 0,
      emailsReplied: 0,
    },
    consentGiven: true,
    ...overrides,
  };
}

// ============================================================
// Tests
// ============================================================

describe('PersonalizationRulesEngine', () => {
  describe('Rule Management', () => {
    it('should add and retrieve rules', () => {
      const engine = new PersonalizationRulesEngine();
      const rule: PersonalizationRule = {
        id: 'test_rule',
        name: 'Test Rule',
        conditions: [],
        transformations: [],
        active: true,
      };

      engine.addRule(rule);
      const retrieved = engine.getRule('test_rule');

      expect(retrieved).toEqual(rule);
    });

    it('should remove rules', () => {
      const engine = new PersonalizationRulesEngine();
      const rule: PersonalizationRule = {
        id: 'test_rule',
        name: 'Test Rule',
        conditions: [],
        transformations: [],
        active: true,
      };

      engine.addRule(rule);
      const removed = engine.removeRule('test_rule');
      const retrieved = engine.getRule('test_rule');

      expect(removed).toBe(true);
      expect(retrieved).toBeUndefined();
    });

    it('should list active rules only', () => {
      const engine = new PersonalizationRulesEngine();

      engine.addRule({
        id: 'active_rule',
        name: 'Active',
        conditions: [],
        transformations: [],
        active: true,
      });

      engine.addRule({
        id: 'inactive_rule',
        name: 'Inactive',
        conditions: [],
        transformations: [],
        active: false,
      });

      const activeRules = engine.listRules({ active: true });

      expect(activeRules).toHaveLength(1);
      expect(activeRules[0].id).toBe('active_rule');
    });

    it('should sort rules by priority', () => {
      const engine = new PersonalizationRulesEngine();

      engine.addRule({
        id: 'low_priority',
        name: 'Low',
        conditions: [],
        transformations: [],
        priority: 10,
        active: true,
      });

      engine.addRule({
        id: 'high_priority',
        name: 'High',
        conditions: [],
        transformations: [],
        priority: 100,
        active: true,
      });

      const rules = engine.listRules();

      expect(rules[0].id).toBe('high_priority');
      expect(rules[1].id).toBe('low_priority');
    });
  });

  describe('Condition Evaluation', () => {
    it('should evaluate equals operator', () => {
      const engine = new PersonalizationRulesEngine();
      const lead = createMockLead({ source: 'social_media' });

      const conditions: PersonalizationCondition[] = [
        { field: 'source', operator: 'equals', value: 'social_media' },
      ];

      const result = engine.evaluateConditions(lead, conditions);
      expect(result).toBe(true);
    });

    it('should evaluate not_equals operator', () => {
      const engine = new PersonalizationRulesEngine();
      const lead = createMockLead({ source: 'website' });

      const conditions: PersonalizationCondition[] = [
        { field: 'source', operator: 'not_equals', value: 'social_media' },
      ];

      const result = engine.evaluateConditions(lead, conditions);
      expect(result).toBe(true);
    });

    it('should evaluate contains operator for strings', () => {
      const engine = new PersonalizationRulesEngine();
      const lead = createMockLead({ email: 'john@company.com' });

      const conditions: PersonalizationCondition[] = [
        { field: 'email', operator: 'contains', value: 'company' },
      ];

      const result = engine.evaluateConditions(lead, conditions);
      expect(result).toBe(true);
    });

    it('should evaluate contains operator for arrays', () => {
      const engine = new PersonalizationRulesEngine();
      const lead = createMockLead({ tags: ['premium', 'engaged'] });

      const conditions: PersonalizationCondition[] = [
        { field: 'tags', operator: 'contains', value: 'premium' },
      ];

      const result = engine.evaluateConditions(lead, conditions);
      expect(result).toBe(true);
    });

    it('should evaluate greater_than operator', () => {
      const engine = new PersonalizationRulesEngine();
      const lead = createMockLead({ score: 85 });

      const conditions: PersonalizationCondition[] = [
        { field: 'score', operator: 'greater_than', value: 50 },
      ];

      const result = engine.evaluateConditions(lead, conditions);
      expect(result).toBe(true);
    });

    it('should evaluate less_than operator', () => {
      const engine = new PersonalizationRulesEngine();
      const lead = createMockLead({ score: 25 });

      const conditions: PersonalizationCondition[] = [
        { field: 'score', operator: 'less_than', value: 50 },
      ];

      const result = engine.evaluateConditions(lead, conditions);
      expect(result).toBe(true);
    });

    it('should evaluate exists operator', () => {
      const engine = new PersonalizationRulesEngine();
      const lead = createMockLead({ firstName: 'John' });

      const conditions: PersonalizationCondition[] = [
        { field: 'firstName', operator: 'exists' },
      ];

      const result = engine.evaluateConditions(lead, conditions);
      expect(result).toBe(true);
    });

    it('should evaluate not_exists operator', () => {
      const engine = new PersonalizationRulesEngine();
      const lead = createMockLead();

      const conditions: PersonalizationCondition[] = [
        { field: 'company', operator: 'not_exists' },
      ];

      const result = engine.evaluateConditions(lead, conditions);
      expect(result).toBe(true);
    });

    it('should evaluate in operator', () => {
      const engine = new PersonalizationRulesEngine();
      const lead = createMockLead({ source: 'social_media' });

      const conditions: PersonalizationCondition[] = [
        { field: 'source', operator: 'in', value: ['social_media', 'partner'] },
      ];

      const result = engine.evaluateConditions(lead, conditions);
      expect(result).toBe(true);
    });

    it('should evaluate custom fields', () => {
      const engine = new PersonalizationRulesEngine();
      const lead = createMockLead({
        customFields: [
          { key: 'industry', value: 'technology', type: 'text' },
        ],
      });

      const conditions: PersonalizationCondition[] = [
        { field: 'customFields.industry', operator: 'equals', value: 'technology' },
      ];

      const result = engine.evaluateConditions(lead, conditions);
      expect(result).toBe(true);
    });

    it('should handle AND logic', () => {
      const engine = new PersonalizationRulesEngine();
      const lead = createMockLead({
        source: 'social_media',
        tags: ['premium'],
      });

      const conditions: PersonalizationCondition[] = [
        { field: 'source', operator: 'equals', value: 'social_media', logic: 'and' },
        { field: 'tags', operator: 'contains', value: 'premium' },
      ];

      const result = engine.evaluateConditions(lead, conditions);
      expect(result).toBe(true);
    });

    it('should handle OR logic', () => {
      const engine = new PersonalizationRulesEngine();
      const lead = createMockLead({ source: 'website' });

      const conditions: PersonalizationCondition[] = [
        { field: 'source', operator: 'equals', value: 'social_media', logic: 'or' },
        { field: 'source', operator: 'equals', value: 'website' },
      ];

      const result = engine.evaluateConditions(lead, conditions);
      expect(result).toBe(true);
    });
  });

  describe('Transformations', () => {
    it('should apply set_variable transformation', () => {
      const engine = new PersonalizationRulesEngine([
        {
          id: 'set_greeting',
          name: 'Set Greeting',
          conditions: [{ field: 'source', operator: 'equals', value: 'social_media' }],
          transformations: [
            { type: 'set_variable', target: 'greeting', value: 'Hey there!' },
          ],
          active: true,
        },
      ]);

      const lead = createMockLead({ source: 'social_media' });
      const result = engine.evaluateRules({ lead, variables: {} });

      expect(result.matched).toBe(true);
      expect(result.transformedVariables.greeting).toBe('Hey there!');
    });

    it('should apply append transformation', () => {
      const engine = new PersonalizationRulesEngine([
        {
          id: 'append_suffix',
          name: 'Append Suffix',
          conditions: [{ field: 'source', operator: 'equals', value: 'partner' }],
          transformations: [
            { type: 'append', target: 'message', value: ' (Partner Exclusive)' },
          ],
          active: true,
        },
      ]);

      const lead = createMockLead({ source: 'partner' });
      const result = engine.evaluateRules({
        lead,
        variables: { message: 'Welcome' },
      });

      expect(result.transformedVariables.message).toBe('Welcome (Partner Exclusive)');
    });

    it('should apply prepend transformation', () => {
      const engine = new PersonalizationRulesEngine([
        {
          id: 'prepend_prefix',
          name: 'Prepend Prefix',
          conditions: [{ field: 'tags', operator: 'contains', value: 'vip' }],
          transformations: [
            { type: 'prepend', target: 'subject', value: '\u2B50 VIP: ' },
          ],
          active: true,
        },
      ]);

      const lead = createMockLead({ tags: ['vip'] });
      const result = engine.evaluateRules({
        lead,
        variables: { subject: 'Special Offer' },
      });

      expect(result.transformedVariables.subject).toBe('\u2B50 VIP: Special Offer');
    });

    it('should apply modify_tone transformation', () => {
      const engine = new PersonalizationRulesEngine([
        {
          id: 'casual_tone',
          name: 'Casual Tone',
          conditions: [{ field: 'source', operator: 'equals', value: 'social_media' }],
          transformations: [
            { type: 'modify_tone', target: 'tone', value: 'casual' },
          ],
          active: true,
        },
      ]);

      const lead = createMockLead({ source: 'social_media' });
      const result = engine.evaluateRules({ lead, variables: {} });

      expect(result.transformedVariables._tone).toBe('casual');
    });

    it('should apply multiple transformations', () => {
      const engine = new PersonalizationRulesEngine([
        {
          id: 'multi_transform',
          name: 'Multiple Transformations',
          conditions: [{ field: 'source', operator: 'equals', value: 'social_media' }],
          transformations: [
            { type: 'set_variable', target: 'greeting', value: 'Hey!' },
            { type: 'modify_tone', target: 'tone', value: 'friendly' },
            { type: 'set_variable', target: 'cta', value: 'Check it out' },
          ],
          active: true,
        },
      ]);

      const lead = createMockLead({ source: 'social_media' });
      const result = engine.evaluateRules({ lead, variables: {} });

      expect(result.transformedVariables.greeting).toBe('Hey!');
      expect(result.transformedVariables._tone).toBe('friendly');
      expect(result.transformedVariables.cta).toBe('Check it out');
    });
  });

  describe('Helper Functions', () => {
    it('should create source-based rule', () => {
      const rule = createSourceRule('social_media', [
        { type: 'set_variable', target: 'greeting', value: 'Hey!' },
      ]);

      expect(rule.id).toBe('source_social_media');
      expect(rule.conditions[0].field).toBe('source');
      expect(rule.conditions[0].value).toBe('social_media');
    });

    it('should create interest-based rule', () => {
      const rule = createInterestRule('tech', [
        { type: 'set_variable', target: 'topic', value: 'technology' },
      ]);

      expect(rule.id).toBe('interest_tech');
      expect(rule.conditions[0].field).toBe('tags');
      expect(rule.conditions[0].value).toBe('tech');
    });

    it('should create custom field rule', () => {
      const rule = createCustomFieldRule('industry', 'equals', 'healthcare', [
        { type: 'set_variable', target: 'industry_specific', value: true },
      ]);

      expect(rule.id).toBe('custom_industry_equals');
      expect(rule.conditions[0].field).toBe('customFields.industry');
    });

    it('should create segment-based rule', () => {
      const rule = createSegmentRule('high-value', [
        { type: 'set_variable', target: 'offer_type', value: 'premium' },
      ]);

      expect(rule.id).toBe('segment_high-value');
      expect(rule.conditions[0].field).toBe('segments');
      expect(rule.conditions[0].value).toBe('high-value');
    });
  });

  describe('Integration Tests', () => {
    it('should evaluate and apply rules for social media lead', () => {
      const engine = new PersonalizationRulesEngine([
        createSourceRule('social_media', [
          { type: 'set_variable', target: 'greeting', value: 'Hey there!' },
          { type: 'modify_tone', target: 'tone', value: 'casual' },
        ]),
      ]);

      const lead = createMockLead({ source: 'social_media' });
      const result = engine.evaluateRules({ lead, variables: {} });

      expect(result.matched).toBe(true);
      expect(result.rulesApplied).toContain('source_social_media');
      expect(result.transformedVariables.greeting).toBe('Hey there!');
      expect(result.transformedVariables._tone).toBe('casual');
    });

    it('should get personalization suggestions for a lead', () => {
      const engine = new PersonalizationRulesEngine([
        createSourceRule('social_media', []),
        createInterestRule('tech', []),
      ]);

      const lead = createMockLead({
        source: 'social_media',
        tags: ['tech', 'engaged'],
      });

      const suggestions = engine.getPersonalizationSuggestions(lead);

      expect(suggestions).toHaveLength(2);
      expect(suggestions.map(s => s.ruleId)).toContain('source_social_media');
      expect(suggestions.map(s => s.ruleId)).toContain('interest_tech');
    });

    it('should test a rule against sample data', () => {
      const engine = new PersonalizationRulesEngine([
        {
          id: 'test_rule',
          name: 'Test Rule',
          conditions: [
            { field: 'source', operator: 'equals', value: 'social_media' },
            { field: 'score', operator: 'greater_than', value: 50 },
          ],
          transformations: [],
          active: true,
        },
      ]);

      const lead = createMockLead({
        source: 'social_media',
        score: 75,
      });

      const testResult = engine.testRule('test_rule', lead);

      expect(testResult.matched).toBe(true);
      expect(testResult.conditionsResults).toHaveLength(2);
      expect(testResult.conditionsResults[0].passed).toBe(true);
      expect(testResult.conditionsResults[1].passed).toBe(true);
    });
  });
});
