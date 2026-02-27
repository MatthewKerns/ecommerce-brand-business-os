/**
 * Interest Matcher - Match lead interests to content customization
 *
 * Features:
 * - Extract interests from Lead tags, segments, and customFields
 * - Match interests to content variants
 * - Score and rank interests for prioritization
 * - Generate personalized content suggestions based on interests
 */

import type { Lead, LeadCustomField } from '@/types/lead';
import {
  PersonalizationRulesEngine,
  type PersonalizationRule,
  type PersonalizationTransformation,
  createInterestRule,
  createCustomFieldRule,
} from '@/core/personalization/rules-engine';

// ============================================================
// Types
// ============================================================

export interface Interest {
  id: string;
  name: string;
  source: 'tag' | 'segment' | 'customField' | 'inferred';
  value?: any;
  score: number; // 0-100, higher = more relevant
  extractedAt?: Date;
  metadata?: Record<string, any>;
}

export interface InterestCategory {
  id: string;
  name: string;
  keywords: string[];
  relatedInterests?: string[];
  priority?: number;
}

export interface ContentVariant {
  id: string;
  interestId: string;
  variantType: 'subject' | 'body' | 'cta' | 'tone' | 'length';
  content: string | Record<string, any>;
  score?: number;
}

export interface InterestMatchResult {
  lead: Lead;
  interests: Interest[];
  topInterests: Interest[];
  recommendedVariants: ContentVariant[];
  personalizationRules: PersonalizationRule[];
  metadata: {
    totalInterests: number;
    averageScore: number;
    primaryCategory?: string;
  };
}

// ============================================================
// Predefined Interest Categories
// ============================================================

export const DEFAULT_INTEREST_CATEGORIES: InterestCategory[] = [
  {
    id: 'ecommerce',
    name: 'E-commerce',
    keywords: ['shopping', 'product', 'store', 'cart', 'purchase', 'buy'],
    priority: 80,
  },
  {
    id: 'content',
    name: 'Content Creation',
    keywords: ['blog', 'writing', 'content', 'article', 'publish'],
    priority: 70,
  },
  {
    id: 'marketing',
    name: 'Marketing',
    keywords: ['marketing', 'email', 'campaign', 'ads', 'promotion', 'seo'],
    priority: 75,
  },
  {
    id: 'tech',
    name: 'Technology',
    keywords: ['tech', 'software', 'development', 'code', 'api', 'integration'],
    priority: 65,
  },
  {
    id: 'analytics',
    name: 'Analytics',
    keywords: ['analytics', 'data', 'metrics', 'tracking', 'insights', 'reporting'],
    priority: 60,
  },
  {
    id: 'automation',
    name: 'Automation',
    keywords: ['automation', 'workflow', 'automated', 'trigger', 'sequence'],
    priority: 70,
  },
  {
    id: 'growth',
    name: 'Growth',
    keywords: ['growth', 'scaling', 'conversion', 'optimization', 'testing'],
    priority: 75,
  },
];

// ============================================================
// Interest Matcher Class
// ============================================================

export class InterestMatcher {
  private categories: Map<string, InterestCategory>;
  private customInterestExtractors: Array<(lead: Lead) => Interest[]> = [];

  constructor(categories?: InterestCategory[]) {
    this.categories = new Map();

    // Load default categories
    DEFAULT_INTEREST_CATEGORIES.forEach(cat => this.categories.set(cat.id, cat));

    // Add custom categories
    categories?.forEach(cat => this.categories.set(cat.id, cat));
  }

  /**
   * Extract all interests from a lead
   */
  extractInterests(lead: Lead): Interest[] {
    const interests: Interest[] = [];

    // Extract from tags
    interests.push(...this.extractFromTags(lead.tags));

    // Extract from segments
    interests.push(...this.extractFromSegments(lead.segments));

    // Extract from custom fields
    interests.push(...this.extractFromCustomFields(lead.customFields));

    // Run custom extractors
    for (const extractor of this.customInterestExtractors) {
      interests.push(...extractor(lead));
    }

    // Deduplicate and score
    return this.deduplicateAndScore(interests);
  }

  /**
   * Match lead interests and generate content customization
   */
  matchInterests(lead: Lead): InterestMatchResult {
    const interests = this.extractInterests(lead);

    // Sort by score (highest first)
    const sortedInterests = interests.sort((a, b) => b.score - a.score);

    // Get top interests (top 3)
    const topInterests = sortedInterests.slice(0, 3);

    // Generate content variants based on top interests
    const recommendedVariants = this.generateContentVariants(topInterests);

    // Generate personalization rules
    const personalizationRules = this.generatePersonalizationRules(topInterests);

    // Calculate metadata
    const totalInterests = interests.length;
    const averageScore =
      interests.length > 0
        ? interests.reduce((sum, i) => sum + i.score, 0) / interests.length
        : 0;
    const primaryCategory = this.identifyPrimaryCategory(interests);

    return {
      lead,
      interests,
      topInterests,
      recommendedVariants,
      personalizationRules,
      metadata: {
        totalInterests,
        averageScore,
        primaryCategory,
      },
    };
  }

  /**
   * Get personalization rules for a lead based on their interests
   */
  getPersonalizationRules(lead: Lead): PersonalizationRule[] {
    const interests = this.extractInterests(lead);
    const topInterests = interests.sort((a, b) => b.score - a.score).slice(0, 3);
    return this.generatePersonalizationRules(topInterests);
  }

  /**
   * Check if lead has specific interest
   */
  hasInterest(lead: Lead, interestId: string): boolean {
    const interests = this.extractInterests(lead);
    return interests.some(i => i.id === interestId);
  }

  /**
   * Get interest score for a lead
   */
  getInterestScore(lead: Lead, interestId: string): number {
    const interests = this.extractInterests(lead);
    const interest = interests.find(i => i.id === interestId);
    return interest?.score || 0;
  }

  /**
   * Add custom interest extractor
   */
  addInterestExtractor(extractor: (lead: Lead) => Interest[]): void {
    this.customInterestExtractors.push(extractor);
  }

  /**
   * Add interest category
   */
  addCategory(category: InterestCategory): void {
    this.categories.set(category.id, category);
  }

  /**
   * Get category by ID
   */
  getCategory(categoryId: string): InterestCategory | undefined {
    return this.categories.get(categoryId);
  }

  /**
   * List all categories
   */
  listCategories(): InterestCategory[] {
    return Array.from(this.categories.values()).sort(
      (a, b) => (b.priority || 0) - (a.priority || 0)
    );
  }

  // ============================================================
  // Private Methods
  // ============================================================

  /**
   * Extract interests from tags
   */
  private extractFromTags(tags: string[]): Interest[] {
    return tags.map(tag => ({
      id: `tag_${tag}`,
      name: tag,
      source: 'tag' as const,
      score: this.scoreTag(tag),
      extractedAt: new Date(),
    }));
  }

  /**
   * Extract interests from segments
   */
  private extractFromSegments(segments: string[]): Interest[] {
    return segments.map(segment => ({
      id: `segment_${segment}`,
      name: segment,
      source: 'segment' as const,
      score: this.scoreSegment(segment),
      extractedAt: new Date(),
    }));
  }

  /**
   * Extract interests from custom fields
   */
  private extractFromCustomFields(customFields: LeadCustomField[]): Interest[] {
    const interests: Interest[] = [];

    for (const field of customFields) {
      // Check if field key suggests interest
      if (this.isInterestField(field.key)) {
        if (field.type === 'multiselect' && Array.isArray(field.value)) {
          // Multiple interests
          field.value.forEach(value => {
            interests.push({
              id: `custom_${field.key}_${value}`,
              name: String(value),
              source: 'customField',
              value: value,
              score: this.scoreCustomField(field.key, value),
              extractedAt: new Date(),
              metadata: { fieldKey: field.key },
            });
          });
        } else if (field.type === 'boolean' && field.value === true) {
          // Boolean interest
          interests.push({
            id: `custom_${field.key}`,
            name: field.key,
            source: 'customField',
            value: field.value,
            score: 70,
            extractedAt: new Date(),
            metadata: { fieldKey: field.key },
          });
        } else {
          // Single interest
          interests.push({
            id: `custom_${field.key}_${field.value}`,
            name: String(field.value),
            source: 'customField',
            value: field.value,
            score: this.scoreCustomField(field.key, field.value),
            extractedAt: new Date(),
            metadata: { fieldKey: field.key },
          });
        }
      }
    }

    return interests;
  }

  /**
   * Check if custom field key suggests it's an interest field
   */
  private isInterestField(key: string): boolean {
    const interestKeywords = [
      'interest',
      'preference',
      'topic',
      'category',
      'focus',
      'area',
      'goal',
    ];
    const lowerKey = key.toLowerCase();
    return interestKeywords.some(keyword => lowerKey.includes(keyword));
  }

  /**
   * Score a tag based on category matching
   */
  private scoreTag(tag: string): number {
    const lowerTag = tag.toLowerCase();
    let maxScore = 50; // Default score

    // Check if tag matches any category keywords
    for (const category of this.categories.values()) {
      for (const keyword of category.keywords) {
        if (lowerTag.includes(keyword) || keyword.includes(lowerTag)) {
          const categoryScore = category.priority || 50;
          maxScore = Math.max(maxScore, categoryScore);
        }
      }
    }

    return maxScore;
  }

  /**
   * Score a segment (segments are generally more important than tags)
   */
  private scoreSegment(segment: string): number {
    const tagScore = this.scoreTag(segment);
    return Math.min(100, tagScore + 20); // Segments get +20 bonus
  }

  /**
   * Score a custom field value
   */
  private scoreCustomField(key: string, value: any): number {
    // Custom fields with "interest" in the key get higher scores
    const baseScore = key.toLowerCase().includes('interest') ? 80 : 60;

    // Check if value matches category keywords
    const valueStr = String(value).toLowerCase();
    let maxScore = baseScore;

    for (const category of this.categories.values()) {
      for (const keyword of category.keywords) {
        if (valueStr.includes(keyword) || keyword.includes(valueStr)) {
          const categoryScore = category.priority || 50;
          maxScore = Math.max(maxScore, categoryScore);
        }
      }
    }

    return maxScore;
  }

  /**
   * Deduplicate and normalize scores
   */
  private deduplicateAndScore(interests: Interest[]): Interest[] {
    const seen = new Map<string, Interest>();

    for (const interest of interests) {
      const existing = seen.get(interest.id);
      if (existing) {
        // Keep higher score
        if (interest.score > existing.score) {
          seen.set(interest.id, interest);
        }
      } else {
        seen.set(interest.id, interest);
      }
    }

    return Array.from(seen.values());
  }

  /**
   * Identify primary category from interests
   */
  private identifyPrimaryCategory(interests: Interest[]): string | undefined {
    const categoryCounts = new Map<string, number>();

    for (const interest of interests) {
      const name = interest.name.toLowerCase();

      for (const category of this.categories.values()) {
        for (const keyword of category.keywords) {
          if (name.includes(keyword) || keyword.includes(name)) {
            categoryCounts.set(
              category.id,
              (categoryCounts.get(category.id) || 0) + interest.score
            );
          }
        }
      }
    }

    if (categoryCounts.size === 0) {
      return undefined;
    }

    // Return category with highest weighted score
    const sorted = Array.from(categoryCounts.entries()).sort((a, b) => b[1] - a[1]);
    return sorted[0][0];
  }

  /**
   * Generate content variants based on interests
   */
  private generateContentVariants(interests: Interest[]): ContentVariant[] {
    const variants: ContentVariant[] = [];

    for (const interest of interests) {
      // Generate subject line variant
      variants.push({
        id: `subject_${interest.id}`,
        interestId: interest.id,
        variantType: 'subject',
        content: this.generateSubjectVariant(interest),
        score: interest.score,
      });

      // Generate CTA variant
      variants.push({
        id: `cta_${interest.id}`,
        interestId: interest.id,
        variantType: 'cta',
        content: this.generateCTAVariant(interest),
        score: interest.score,
      });

      // Generate tone suggestion
      variants.push({
        id: `tone_${interest.id}`,
        interestId: interest.id,
        variantType: 'tone',
        content: this.suggestTone(interest),
        score: interest.score,
      });
    }

    return variants;
  }

  /**
   * Generate subject line variant for interest
   */
  private generateSubjectVariant(interest: Interest): string {
    const templates = [
      `{{interestName}}: {{value}}`,
      `Your {{interestName}} guide is here`,
      `Everything you need for {{interestName}}`,
      `{{interestName}} tips inside`,
    ];

    const template = templates[Math.floor(Math.random() * templates.length)];
    return template
      .replace(/{{interestName}}/g, interest.name)
      .replace(/{{value}}/g, String(interest.value || 'resources'));
  }

  /**
   * Generate CTA variant for interest
   */
  private generateCTAVariant(interest: Interest): string {
    const templates = [
      `Explore ${interest.name}`,
      `Get ${interest.name} resources`,
      `Learn more about ${interest.name}`,
      `See ${interest.name} in action`,
    ];

    return templates[Math.floor(Math.random() * templates.length)];
  }

  /**
   * Suggest tone based on interest
   */
  private suggestTone(interest: Interest): string {
    const category = this.identifyInterestCategory(interest);

    switch (category) {
      case 'tech':
      case 'analytics':
        return 'professional';
      case 'marketing':
      case 'growth':
        return 'friendly';
      case 'ecommerce':
        return 'urgent';
      default:
        return 'educational';
    }
  }

  /**
   * Identify which category an interest belongs to
   */
  private identifyInterestCategory(interest: Interest): string | undefined {
    const name = interest.name.toLowerCase();

    for (const category of this.categories.values()) {
      for (const keyword of category.keywords) {
        if (name.includes(keyword) || keyword.includes(name)) {
          return category.id;
        }
      }
    }

    return undefined;
  }

  /**
   * Generate personalization rules from interests
   */
  private generatePersonalizationRules(interests: Interest[]): PersonalizationRule[] {
    const rules: PersonalizationRule[] = [];

    for (const interest of interests) {
      if (interest.source === 'tag') {
        // Create rule for tag-based interest
        const transformations: PersonalizationTransformation[] = [
          {
            type: 'set_variable',
            target: 'interest_topic',
            value: interest.name,
          },
          {
            type: 'set_variable',
            target: 'interest_score',
            value: interest.score,
          },
        ];

        // Add tone modification if applicable
        const tone = this.suggestTone(interest);
        transformations.push({
          type: 'modify_tone',
          target: 'tone',
          value: tone,
        });

        rules.push(
          createInterestRule(interest.name, transformations)
        );
      } else if (interest.source === 'customField' && interest.metadata?.fieldKey) {
        // Create rule for custom field interest
        const transformations: PersonalizationTransformation[] = [
          {
            type: 'set_variable',
            target: 'custom_interest',
            value: interest.value,
          },
          {
            type: 'set_variable',
            target: 'interest_field',
            value: interest.metadata.fieldKey,
          },
        ];

        rules.push(
          createCustomFieldRule(
            interest.metadata.fieldKey,
            'equals',
            interest.value,
            transformations
          )
        );
      }
    }

    return rules;
  }
}

// ============================================================
// Helper Functions
// ============================================================

/**
 * Create an interest matcher with default configuration
 */
export function createInterestMatcher(
  customCategories?: InterestCategory[]
): InterestMatcher {
  return new InterestMatcher(customCategories);
}

/**
 * Extract top interests from a lead
 */
export function getTopInterests(lead: Lead, limit: number = 3): Interest[] {
  const matcher = new InterestMatcher();
  const interests = matcher.extractInterests(lead);
  return interests.sort((a, b) => b.score - a.score).slice(0, limit);
}

/**
 * Check if lead has any interests in a category
 */
export function hasInterestInCategory(
  lead: Lead,
  categoryId: string
): boolean {
  const matcher = new InterestMatcher();
  const category = matcher.getCategory(categoryId);

  if (!category) {
    return false;
  }

  const interests = matcher.extractInterests(lead);

  for (const interest of interests) {
    const name = interest.name.toLowerCase();
    for (const keyword of category.keywords) {
      if (name.includes(keyword) || keyword.includes(name)) {
        return true;
      }
    }
  }

  return false;
}

/**
 * Get personalization suggestions for a lead based on interests
 */
export function getInterestBasedPersonalization(lead: Lead): {
  interests: Interest[];
  rules: PersonalizationRule[];
  variants: ContentVariant[];
} {
  const matcher = new InterestMatcher();
  const result = matcher.matchInterests(lead);

  return {
    interests: result.topInterests,
    rules: result.personalizationRules,
    variants: result.recommendedVariants,
  };
}
