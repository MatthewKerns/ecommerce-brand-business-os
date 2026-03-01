/**
 * Interest Matcher Tests
 */

import { describe, it, expect, beforeEach } from '@jest/globals';
import {
  InterestMatcher,
  getTopInterests,
  hasInterestInCategory,
  getInterestBasedPersonalization,
  DEFAULT_INTEREST_CATEGORIES,
  type Interest,
  type InterestCategory,
} from '../interest-matcher';
import type { Lead, LeadCustomField } from '@/types/lead';

describe('Interest Matcher', () => {
  let matcher: InterestMatcher;
  let sampleLead: Lead;

  beforeEach(() => {
    matcher = new InterestMatcher();
    sampleLead = {
      id: 'test-lead-1',
      email: 'test@example.com',
      status: 'engaged',
      source: 'website',
      createdAt: new Date(),
      updatedAt: new Date(),
      tags: ['email-marketing', 'automation', 'ecommerce'],
      segments: ['high-value', 'tech-savvy'],
      customFields: [
        {
          key: 'interests',
          value: ['content-creation', 'analytics'],
          type: 'multiselect',
        },
        {
          key: 'primary_goal',
          value: 'growth',
          type: 'text',
        },
      ],
      engagement: {
        emailsSent: 5,
        emailsOpened: 3,
        emailsClicked: 2,
        emailsReplied: 1,
      },
      consentGiven: true,
    };
  });

  describe('interest matching - extraction', () => {
    it('should extract interests from tags', () => {
      const interests = matcher.extractInterests(sampleLead);
      const tagInterests = interests.filter(i => i.source === 'tag');

      expect(tagInterests.length).toBeGreaterThan(0);
      expect(tagInterests.some(i => i.name === 'email-marketing')).toBe(true);
      expect(tagInterests.some(i => i.name === 'automation')).toBe(true);
      expect(tagInterests.some(i => i.name === 'ecommerce')).toBe(true);
    });

    it('should extract interests from segments', () => {
      const interests = matcher.extractInterests(sampleLead);
      const segmentInterests = interests.filter(i => i.source === 'segment');

      expect(segmentInterests.length).toBeGreaterThan(0);
      expect(segmentInterests.some(i => i.name === 'high-value')).toBe(true);
      expect(segmentInterests.some(i => i.name === 'tech-savvy')).toBe(true);
    });

    it('should extract interests from custom fields for interest matching', () => {
      const interests = matcher.extractInterests(sampleLead);
      const customFieldInterests = interests.filter(i => i.source === 'customField');

      expect(customFieldInterests.length).toBeGreaterThan(0);
      expect(customFieldInterests.some(i => i.name === 'content-creation')).toBe(true);
      expect(customFieldInterests.some(i => i.name === 'analytics')).toBe(true);
    });
  });

  describe('interest matching - scoring', () => {
    it('should assign scores to interests for matching', () => {
      const interests = matcher.extractInterests(sampleLead);

      interests.forEach(interest => {
        expect(interest.score).toBeGreaterThan(0);
        expect(interest.score).toBeLessThanOrEqual(100);
      });
    });
  });

  describe('interest matching - matching results', () => {
    it('should perform interest matching and return results', () => {
      const result = matcher.matchInterests(sampleLead);

      expect(result.lead).toBe(sampleLead);
      expect(result.interests.length).toBeGreaterThan(0);
      expect(result.topInterests.length).toBeGreaterThan(0);
      expect(result.metadata.totalInterests).toBe(result.interests.length);
    });

    it('should generate personalization rules from interest matching', () => {
      const result = matcher.matchInterests(sampleLead);

      expect(result.personalizationRules.length).toBeGreaterThan(0);
      result.personalizationRules.forEach(rule => {
        expect(rule.id).toBeDefined();
        expect(rule.name).toBeDefined();
        expect(rule.conditions.length).toBeGreaterThan(0);
        expect(rule.transformations.length).toBeGreaterThan(0);
      });
    });
  });
});
