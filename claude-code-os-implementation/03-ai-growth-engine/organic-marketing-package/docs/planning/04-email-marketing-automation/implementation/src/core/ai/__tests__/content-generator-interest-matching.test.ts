/**
 * Content Generator Interest Matching Integration Tests
 */

import { describe, it, expect, beforeEach } from '@jest/globals';
import { ContentGenerator } from '../content-generator';
import { InterestMatcher } from '@/core/personalization/interest-matcher';
import type { Lead } from '@/types/lead';

describe('ContentGenerator - Interest Matching Integration', () => {
  let generator: ContentGenerator;
  let sampleLead: Lead;

  beforeEach(() => {
    generator = new ContentGenerator({
      provider: 'gemini',
      apiKey: 'test-api-key',
    });

    sampleLead = {
      id: 'test-lead-1',
      email: 'test@example.com',
      status: 'engaged',
      source: 'website',
      createdAt: new Date(),
      updatedAt: new Date(),
      tags: ['email-marketing', 'automation', 'growth'],
      segments: ['enterprise', 'tech-savvy'],
      customFields: [
        {
          key: 'interests',
          value: ['analytics', 'conversion-optimization'],
          type: 'multiselect',
        },
        {
          key: 'industry',
          value: 'ecommerce',
          type: 'text',
        },
      ],
      engagement: {
        emailsSent: 10,
        emailsOpened: 8,
        emailsClicked: 5,
        emailsReplied: 2,
      },
      consentGiven: true,
    };
  });

  describe('interest matching - initialization', () => {
    it('should enable interest matching personalization', () => {
      generator.enableInterestPersonalization();
      const matcher = generator.getInterestMatcher();

      expect(matcher).toBeDefined();
      expect(matcher).toBeInstanceOf(InterestMatcher);
    });

    it('should set custom interest matcher for matching', () => {
      const customMatcher = new InterestMatcher();
      generator.setInterestMatcher(customMatcher);

      const matcher = generator.getInterestMatcher();
      expect(matcher).toBe(customMatcher);
    });
  });

  describe('interest matching - extraction', () => {
    it('should extract lead interests through interest matching', () => {
      const interests = generator.getLeadInterests(sampleLead);

      expect(interests.length).toBeGreaterThan(0);
      expect(interests.some(i => i.name === 'email-marketing')).toBe(true);
      expect(interests.some(i => i.name === 'automation')).toBe(true);
    });

    it('should match lead interests with full interest matching results', () => {
      const result = generator.matchLeadInterests(sampleLead);

      expect(result.lead).toBe(sampleLead);
      expect(result.interests.length).toBeGreaterThan(0);
      expect(result.topInterests.length).toBeGreaterThan(0);
      expect(result.recommendedVariants.length).toBeGreaterThan(0);
      expect(result.personalizationRules.length).toBeGreaterThan(0);
    });
  });

  describe('interest matching - personalization rules', () => {
    it('should apply interest-based personalization rules via interest matching', () => {
      generator.applyInterestBasedPersonalization(sampleLead);

      const engine = generator.getPersonalizationEngine();
      expect(engine).toBeDefined();

      const rules = engine!.listRules({ active: true });
      expect(rules.length).toBeGreaterThan(0);
    });

    it('should generate rules for tag-based interests through interest matching', () => {
      generator.applyInterestBasedPersonalization(sampleLead);

      const engine = generator.getPersonalizationEngine();
      const rules = engine!.listRules({ active: true });

      const tagRules = rules.filter(r => r.id.startsWith('interest_'));
      expect(tagRules.length).toBeGreaterThan(0);
    });
  });

  describe('interest matching - integration flow', () => {
    it('should complete full interest-based matching personalization flow', () => {
      // Enable interest matching personalization
      generator.enableInterestPersonalization();

      // Extract interests through matching
      const interests = generator.getLeadInterests(sampleLead);
      expect(interests.length).toBeGreaterThan(0);

      // Match interests
      const matchResult = generator.matchLeadInterests(sampleLead);
      expect(matchResult.topInterests.length).toBeGreaterThan(0);

      // Apply personalization via interest matching
      generator.applyInterestBasedPersonalization(sampleLead);

      // Verify rules were created through interest matching
      const engine = generator.getPersonalizationEngine();
      expect(engine).toBeDefined();

      const rules = engine!.listRules({ active: true });
      expect(rules.length).toBeGreaterThan(0);

      // Verify interest matcher is set for matching
      const matcher = generator.getInterestMatcher();
      expect(matcher).toBeDefined();
    });
  });
});
