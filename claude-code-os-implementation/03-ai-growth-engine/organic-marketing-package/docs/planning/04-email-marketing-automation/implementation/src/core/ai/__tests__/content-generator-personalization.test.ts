/**
 * Tests for ContentGenerator Personalization Integration
 */

import { ContentGenerator, type AIConfig, type ContentTemplate } from '../content-generator';
import {
  PersonalizationRulesEngine,
  createSourceRule,
  createInterestRule,
  type PersonalizationRule,
} from '@/core/personalization/rules-engine';
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

// Mock AI provider
const mockAIConfig: AIConfig = {
  provider: 'gemini',
  apiKey: 'test-key',
  model: 'gemini-1.5-flash',
};

// Mock template
const mockTemplate: ContentTemplate = {
  id: 'test_template',
  name: 'Test Template',
  category: 'welcome',
  systemPrompt: 'You are a helpful assistant.',
  userPromptTemplate: 'Write an email with greeting: {{greeting}} and message: {{message}}',
  variables: [
    { name: 'greeting', description: 'Greeting text', required: true },
    { name: 'message', description: 'Main message', required: true },
  ],
};

// ============================================================
// Tests
// ============================================================

describe('ContentGenerator Personalization', () => {
  describe('Initialization', () => {
    it('should initialize without personalization rules', () => {
      const generator = new ContentGenerator(mockAIConfig);
      const engine = generator.getPersonalizationEngine();

      expect(engine).toBeUndefined();
    });

    it('should initialize with personalization rules', () => {
      const rules: PersonalizationRule[] = [
        createSourceRule('social_media', [
          { type: 'set_variable', target: 'greeting', value: 'Hey!' },
        ]),
      ];

      const generator = new ContentGenerator(mockAIConfig, undefined, rules);
      const engine = generator.getPersonalizationEngine();

      expect(engine).toBeDefined();
      expect(engine?.listRules()).toHaveLength(1);
    });

    it('should set personalization engine after initialization', () => {
      const generator = new ContentGenerator(mockAIConfig);
      const engine = new PersonalizationRulesEngine([
        createSourceRule('social_media', []),
      ]);

      generator.setPersonalizationEngine(engine);

      expect(generator.getPersonalizationEngine()).toBe(engine);
    });
  });

  describe('Rule Management', () => {
    it('should add personalization rules', () => {
      const generator = new ContentGenerator(mockAIConfig);

      const rule = createSourceRule('social_media', [
        { type: 'set_variable', target: 'greeting', value: 'Hey!' },
      ]);

      generator.addPersonalizationRule(rule);

      const engine = generator.getPersonalizationEngine();
      expect(engine).toBeDefined();
      expect(engine?.getRule('source_social_media')).toBeDefined();
    });

    it('should remove personalization rules', () => {
      const rules: PersonalizationRule[] = [
        createSourceRule('social_media', []),
      ];

      const generator = new ContentGenerator(mockAIConfig, undefined, rules);
      const removed = generator.removePersonalizationRule('source_social_media');
      const engine = generator.getPersonalizationEngine();

      expect(removed).toBe(true);
      expect(engine?.getRule('source_social_media')).toBeUndefined();
    });

    it('should get personalization suggestions for a lead', () => {
      const rules: PersonalizationRule[] = [
        createSourceRule('social_media', []),
        createInterestRule('tech', []),
      ];

      const generator = new ContentGenerator(mockAIConfig, undefined, rules);
      const lead = createMockLead({
        source: 'social_media',
        tags: ['tech'],
      });

      const suggestions = generator.getPersonalizationSuggestions(lead);

      expect(suggestions).toHaveLength(2);
      expect(suggestions.map(s => s.ruleId)).toContain('source_social_media');
      expect(suggestions.map(s => s.ruleId)).toContain('interest_tech');
    });
  });

  describe('Content Generation with Personalization', () => {
    it('should apply personalization when lead is provided', async () => {
      const rules: PersonalizationRule[] = [
        createSourceRule('social_media', [
          { type: 'set_variable', target: 'greeting', value: 'Hey there!' },
          { type: 'set_variable', target: 'message', value: 'Welcome to our community!' },
        ]),
      ];

      const generator = new ContentGenerator(mockAIConfig, [mockTemplate], rules);

      // Mock the AI provider call
      const mockResponse = JSON.stringify({
        subject: 'Welcome!',
        body: 'Email body content',
      });

      // Spy on the private method
      jest.spyOn(generator as any, 'callAIProvider').mockResolvedValue(mockResponse);

      const lead = createMockLead({ source: 'social_media' });

      const result = await generator.generateContent({
        templateId: 'test_template',
        variables: {
          greeting: 'Hello',
          message: 'Default message',
        },
        lead,
        applyPersonalization: true,
      });

      expect(result.metadata?.personalizationApplied).toBe(true);
      expect(result.metadata?.rulesApplied).toContain('source_social_media');

      // Verify that the AI was called with personalized variables
      const callAIProvider = (generator as any).callAIProvider;
      expect(callAIProvider).toHaveBeenCalled();

      const userPromptCall = callAIProvider.mock.calls[0][1];
      expect(userPromptCall).toContain('Hey there!');
      expect(userPromptCall).toContain('Welcome to our community!');
    });

    it('should not apply personalization when applyPersonalization is false', async () => {
      const rules: PersonalizationRule[] = [
        createSourceRule('social_media', [
          { type: 'set_variable', target: 'greeting', value: 'Hey there!' },
        ]),
      ];

      const generator = new ContentGenerator(mockAIConfig, [mockTemplate], rules);

      const mockResponse = JSON.stringify({
        subject: 'Welcome!',
        body: 'Email body content',
      });

      jest.spyOn(generator as any, 'callAIProvider').mockResolvedValue(mockResponse);

      const lead = createMockLead({ source: 'social_media' });

      const result = await generator.generateContent({
        templateId: 'test_template',
        variables: {
          greeting: 'Hello',
          message: 'Default message',
        },
        lead,
        applyPersonalization: false,
      });

      expect(result.metadata?.personalizationApplied).toBeUndefined();
    });

    it('should not apply personalization when no lead is provided', async () => {
      const rules: PersonalizationRule[] = [
        createSourceRule('social_media', [
          { type: 'set_variable', target: 'greeting', value: 'Hey there!' },
        ]),
      ];

      const generator = new ContentGenerator(mockAIConfig, [mockTemplate], rules);

      const mockResponse = JSON.stringify({
        subject: 'Welcome!',
        body: 'Email body content',
      });

      jest.spyOn(generator as any, 'callAIProvider').mockResolvedValue(mockResponse);

      const result = await generator.generateContent({
        templateId: 'test_template',
        variables: {
          greeting: 'Hello',
          message: 'Default message',
        },
      });

      expect(result.metadata?.personalizationApplied).toBeUndefined();
    });

    it('should apply tone overrides from personalization', async () => {
      const rules: PersonalizationRule[] = [
        createSourceRule('social_media', [
          { type: 'modify_tone', target: 'tone', value: 'casual' },
          { type: 'set_variable', target: 'greeting', value: 'Hey!' },
          { type: 'set_variable', target: 'message', value: 'Casual message' },
        ]),
      ];

      const generator = new ContentGenerator(mockAIConfig, [mockTemplate], rules);

      const mockResponse = JSON.stringify({
        subject: 'Welcome!',
        body: 'Email body content',
      });

      jest.spyOn(generator as any, 'callAIProvider').mockResolvedValue(mockResponse);

      const lead = createMockLead({ source: 'social_media' });

      await generator.generateContent({
        templateId: 'test_template',
        variables: {
          greeting: 'Hello',
          message: 'Default message',
        },
        lead,
      });

      // Check that tone was applied in system prompt
      const callAIProvider = (generator as any).callAIProvider;
      const systemPromptCall = callAIProvider.mock.calls[0][0];
      expect(systemPromptCall).toContain('casual');
    });

    it('should handle multiple matching rules with priority', async () => {
      const rules: PersonalizationRule[] = [
        {
          id: 'low_priority_rule',
          name: 'Low Priority',
          conditions: [{ field: 'source', operator: 'equals', value: 'social_media' }],
          transformations: [
            { type: 'set_variable', target: 'greeting', value: 'Low priority greeting' },
          ],
          priority: 10,
          active: true,
        },
        {
          id: 'high_priority_rule',
          name: 'High Priority',
          conditions: [{ field: 'source', operator: 'equals', value: 'social_media' }],
          transformations: [
            { type: 'set_variable', target: 'message', value: 'High priority message' },
          ],
          priority: 100,
          active: true,
        },
      ];

      const generator = new ContentGenerator(mockAIConfig, [mockTemplate], rules);

      const mockResponse = JSON.stringify({
        subject: 'Welcome!',
        body: 'Email body content',
      });

      jest.spyOn(generator as any, 'callAIProvider').mockResolvedValue(mockResponse);

      const lead = createMockLead({ source: 'social_media' });

      const result = await generator.generateContent({
        templateId: 'test_template',
        variables: {
          greeting: 'Hello',
          message: 'Default message',
        },
        lead,
      });

      expect(result.metadata?.personalizationApplied).toBe(true);
      expect(result.metadata?.rulesApplied).toHaveLength(2);
    });

    it('should handle custom field-based personalization', async () => {
      const rules: PersonalizationRule[] = [
        {
          id: 'industry_tech',
          name: 'Tech Industry',
          conditions: [
            { field: 'customFields.industry', operator: 'equals', value: 'technology' },
          ],
          transformations: [
            { type: 'set_variable', target: 'message', value: 'Tech-specific message' },
          ],
          active: true,
        },
      ];

      const generator = new ContentGenerator(mockAIConfig, [mockTemplate], rules);

      const mockResponse = JSON.stringify({
        subject: 'Welcome!',
        body: 'Email body content',
      });

      jest.spyOn(generator as any, 'callAIProvider').mockResolvedValue(mockResponse);

      const lead = createMockLead({
        customFields: [
          { key: 'industry', value: 'technology', type: 'text' },
        ],
      });

      const result = await generator.generateContent({
        templateId: 'test_template',
        variables: {
          greeting: 'Hello',
          message: 'Default message',
        },
        lead,
      });

      expect(result.metadata?.personalizationApplied).toBe(true);
      expect(result.metadata?.rulesApplied).toContain('industry_tech');
    });
  });

  describe('Error Handling', () => {
    it('should throw error when required variables are missing after personalization', async () => {
      const rules: PersonalizationRule[] = [
        createSourceRule('social_media', [
          // Rule doesn't set required variables
        ]),
      ];

      const generator = new ContentGenerator(mockAIConfig, [mockTemplate], rules);

      const lead = createMockLead({ source: 'social_media' });

      await expect(
        generator.generateContent({
          templateId: 'test_template',
          variables: {},
          lead,
        })
      ).rejects.toThrow('Required variable missing');
    });
  });
});
