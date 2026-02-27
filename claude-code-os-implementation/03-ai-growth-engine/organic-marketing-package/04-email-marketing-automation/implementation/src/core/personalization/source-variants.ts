/**
 * Source-Based Content Variants
 *
 * Provides email content variations based on signup source (website, social media, partner, etc.)
 * to create more personalized and contextually relevant messaging.
 *
 * Each source variant includes:
 * - Custom subject lines
 * - Adjusted tone and messaging
 * - Source-specific context references
 */

import type { LeadSource } from '@/types/lead';

// ============================================================
// Types
// ============================================================

export interface ContentVariant {
  subject: string;
  preheader?: string;
  openingLine?: string;
  tone?: 'professional' | 'casual' | 'friendly' | 'urgent' | 'educational';
  contextualNote?: string; // Reference to how they joined
}

export interface SourceVariantConfig {
  templateId: string;
  source: LeadSource;
  variant: ContentVariant;
}

// ============================================================
// Source Variants Registry
// ============================================================

/**
 * Pre-configured content variants for different signup sources
 * Organized by template ID and then by source
 */
const SOURCE_VARIANTS: Record<string, Record<LeadSource, ContentVariant>> = {
  // Welcome Series Email 1 - Warm Welcome
  welcome_series_1: {
    website: {
      subject: 'Welcome! Here\'s what to expect next',
      preheader: 'Thanks for joining us from our website',
      openingLine: 'Thanks for signing up on our website!',
      tone: 'friendly',
      contextualNote: 'We noticed you joined us from our website',
    },
    landing_page: {
      subject: 'Welcome! Your special offer is inside',
      preheader: 'Thanks for taking the next step',
      openingLine: 'We\'re excited to have you here!',
      tone: 'friendly',
      contextualNote: 'Thanks for responding to our offer',
    },
    social_media: {
      subject: '👋 Hey! Welcome to the community',
      preheader: 'Great to connect with you from social media',
      openingLine: 'So glad you found us on social media!',
      tone: 'casual',
      contextualNote: 'We\'re excited to connect with you from social media',
    },
    email_referral: {
      subject: 'Welcome! Your friend thought you\'d love this',
      preheader: 'Thanks to a friend who knows you well',
      openingLine: 'A friend thought you\'d be interested in what we do!',
      tone: 'friendly',
      contextualNote: 'Thanks for joining us through a friend\'s recommendation',
    },
    partner: {
      subject: 'Welcome from our partner network',
      preheader: 'Exclusive access through our partnership',
      openingLine: 'We\'re thrilled to welcome you through our partner network!',
      tone: 'professional',
      contextualNote: 'You\'re receiving this through our trusted partnership',
    },
    event: {
      subject: 'Great meeting you! Here\'s what\'s next',
      preheader: 'Following up from our recent event',
      openingLine: 'It was great connecting with you at the event!',
      tone: 'professional',
      contextualNote: 'Thanks for your interest at our recent event',
    },
    manual: {
      subject: 'Welcome! We\'re glad to have you',
      preheader: 'Excited to start this journey together',
      openingLine: 'Welcome! We\'re excited to have you with us.',
      tone: 'friendly',
      contextualNote: 'We personally added you to our list',
    },
    import: {
      subject: 'Welcome! Here\'s what you need to know',
      preheader: 'Getting you up to speed',
      openingLine: 'Welcome! Let us bring you up to speed.',
      tone: 'friendly',
      contextualNote: 'We\'ve recently updated our systems',
    },
    api: {
      subject: 'Welcome! Your account is ready',
      preheader: 'You\'re all set to get started',
      openingLine: 'Your account has been created and you\'re ready to go!',
      tone: 'professional',
      contextualNote: 'Your account was created through our integration',
    },
    other: {
      subject: 'Welcome! Great to have you here',
      preheader: 'Let\'s get started',
      openingLine: 'Welcome! We\'re excited to have you with us.',
      tone: 'friendly',
      contextualNote: 'Thanks for joining us',
    },
  },

  // Welcome Series Email 2 - Educational Value
  welcome_series_2: {
    website: {
      subject: 'The #1 thing you need to know about {{topic}}',
      preheader: 'Building on your interest from our website',
      openingLine: 'Since you found us on our website, we thought you\'d find this valuable...',
      tone: 'educational',
    },
    landing_page: {
      subject: 'Here\'s the insider guide we promised',
      preheader: 'Exclusive insights for new members',
      openingLine: 'As promised, here\'s the valuable content we mentioned...',
      tone: 'educational',
    },
    social_media: {
      subject: '🎓 Quick lesson: Everything about {{topic}}',
      preheader: 'The good stuff you won\'t find on social',
      openingLine: 'Here\'s something you won\'t find in your social feed...',
      tone: 'casual',
    },
    email_referral: {
      subject: 'Why your friend recommended us (the real story)',
      preheader: 'The value they discovered first-hand',
      openingLine: 'Here\'s what your friend discovered that made them think of you...',
      tone: 'friendly',
    },
    partner: {
      subject: 'Professional insights: {{topic}} best practices',
      preheader: 'Expert knowledge through our partnership',
      openingLine: 'We\'re sharing our most valuable insights with you...',
      tone: 'professional',
    },
    event: {
      subject: 'Following up: Key takeaways about {{topic}}',
      preheader: 'Continuing our conversation',
      openingLine: 'Building on what we discussed at the event...',
      tone: 'professional',
    },
    manual: {
      subject: 'Here\'s what makes us different',
      preheader: 'The backstory you should know',
      openingLine: 'Let us share what makes our approach unique...',
      tone: 'friendly',
    },
    import: {
      subject: 'New here? Start with this essential guide',
      preheader: 'Getting you up to speed quickly',
      openingLine: 'Here\'s the essential guide to get you started...',
      tone: 'educational',
    },
    api: {
      subject: 'Getting started: {{topic}} fundamentals',
      preheader: 'Technical insights for your integration',
      openingLine: 'Here are the key concepts to maximize your integration...',
      tone: 'professional',
    },
    other: {
      subject: 'The essential guide to {{topic}}',
      preheader: 'Knowledge you can use today',
      openingLine: 'Here\'s valuable information to help you get started...',
      tone: 'educational',
    },
  },

  // Welcome Series Email 3 - Social Proof
  welcome_series_3: {
    website: {
      subject: 'How {{customerName}} achieved {{result}} (their story)',
      preheader: 'Real results from someone like you',
      openingLine: 'We wanted to share a story from someone who found us just like you did...',
      tone: 'friendly',
    },
    landing_page: {
      subject: 'This customer saw results in just {{timeframe}}',
      preheader: 'See what\'s possible for you',
      openingLine: 'Here\'s proof of what we can help you achieve...',
      tone: 'friendly',
    },
    social_media: {
      subject: '🌟 Real story: From skeptic to success',
      preheader: 'They were in your shoes 6 months ago',
      openingLine: 'This customer found us on social media, just like you. Here\'s their journey...',
      tone: 'casual',
    },
    email_referral: {
      subject: 'The success story your friend wanted you to see',
      preheader: 'Why they made the recommendation',
      openingLine: 'This is the kind of result that inspired your friend to recommend us...',
      tone: 'friendly',
    },
    partner: {
      subject: 'Case study: {{customerName}}\'s measurable results',
      preheader: 'Verified success through our partnership',
      openingLine: 'Here\'s a detailed case study from our partner network...',
      tone: 'professional',
    },
    event: {
      subject: 'Success stories from people you might have met',
      preheader: 'Results from our community',
      openingLine: 'Many attendees like yourself have achieved great results...',
      tone: 'professional',
    },
    manual: {
      subject: 'Why we handpicked you for this opportunity',
      preheader: 'Others in your position have thrived',
      openingLine: 'Here\'s why we think you\'re a perfect fit...',
      tone: 'friendly',
    },
    import: {
      subject: 'Join thousands who are already seeing results',
      preheader: 'You\'re in good company',
      openingLine: 'You\'re joining a community of successful users...',
      tone: 'friendly',
    },
    api: {
      subject: 'Integration success: {{customerName}}\'s ROI story',
      preheader: 'Technical implementation that delivered',
      openingLine: 'Here\'s how another integration partner achieved measurable ROI...',
      tone: 'professional',
    },
    other: {
      subject: 'Real customers, real results',
      preheader: 'Success stories you can relate to',
      openingLine: 'Here are some inspiring stories from our community...',
      tone: 'friendly',
    },
  },

  // Welcome Series Email 4 - First Purchase Incentive
  welcome_series_4: {
    website: {
      subject: '🎁 Your exclusive welcome offer expires soon',
      preheader: 'Save {{discount}} on your first order',
      openingLine: 'As a thank you for joining us from our website...',
      tone: 'friendly',
    },
    landing_page: {
      subject: 'Last chance: Your {{discount}} offer ends {{deadline}}',
      preheader: 'Don\'t miss this special opportunity',
      openingLine: 'This is the special offer you signed up for...',
      tone: 'urgent',
    },
    social_media: {
      subject: '⏰ Social media exclusive: {{discount}} off ends soon',
      preheader: 'For our social community only',
      openingLine: 'Here\'s an exclusive offer just for our social media community...',
      tone: 'casual',
    },
    email_referral: {
      subject: 'Double reward: {{discount}} off + thank your friend',
      preheader: 'Both of you benefit',
      openingLine: 'As a thank you for being referred by a friend...',
      tone: 'friendly',
    },
    partner: {
      subject: 'Partner exclusive: Premium access with {{discount}} off',
      preheader: 'Special offer through our partnership',
      openingLine: 'Through our partnership, you have access to this exclusive offer...',
      tone: 'professional',
    },
    event: {
      subject: 'Event attendee special: {{discount}} off expires {{deadline}}',
      preheader: 'Exclusive offer for event participants',
      openingLine: 'As an event attendee, you qualify for this special offer...',
      tone: 'professional',
    },
    manual: {
      subject: 'Your personalized offer: {{discount}} off',
      preheader: 'Handpicked just for you',
      openingLine: 'We\'ve created a special offer just for you...',
      tone: 'friendly',
    },
    import: {
      subject: 'Welcome back: {{discount}} off your next order',
      preheader: 'We\'ve missed you',
      openingLine: 'As a valued member, here\'s a special welcome back offer...',
      tone: 'friendly',
    },
    api: {
      subject: 'Your integration bonus: {{discount}} off premium features',
      preheader: 'Upgrade offer for your account',
      openingLine: 'To maximize your integration, here\'s an exclusive upgrade offer...',
      tone: 'professional',
    },
    other: {
      subject: 'Special offer: Save {{discount}} on your first order',
      preheader: 'Limited time opportunity',
      openingLine: 'Here\'s a special offer to get you started...',
      tone: 'friendly',
    },
  },
};

// ============================================================
// Helper Functions
// ============================================================

/**
 * Get content variant for a specific source and template
 */
export function getSourceVariant(source: LeadSource, templateId: string): ContentVariant {
  const templateVariants = SOURCE_VARIANTS[templateId];

  if (!templateVariants) {
    throw new Error(`No source variants found for template: ${templateId}`);
  }

  const variant = templateVariants[source];

  if (!variant) {
    // Fallback to 'other' source if specific source not found
    return templateVariants.other || {
      subject: 'Welcome!',
      tone: 'friendly',
    };
  }

  return variant;
}

/**
 * Get all available sources for a template
 */
export function getAvailableSources(templateId: string): LeadSource[] {
  const templateVariants = SOURCE_VARIANTS[templateId];

  if (!templateVariants) {
    return [];
  }

  return Object.keys(templateVariants) as LeadSource[];
}

/**
 * Check if a template has source variants configured
 */
export function hasSourceVariants(templateId: string): boolean {
  return templateId in SOURCE_VARIANTS;
}

/**
 * Get all templates that have source variants
 */
export function getTemplatesWithSourceVariants(): string[] {
  return Object.keys(SOURCE_VARIANTS);
}

/**
 * Create a custom source variant
 */
export function createSourceVariant(
  templateId: string,
  source: LeadSource,
  variant: ContentVariant
): void {
  if (!SOURCE_VARIANTS[templateId]) {
    SOURCE_VARIANTS[templateId] = {} as Record<LeadSource, ContentVariant>;
  }

  SOURCE_VARIANTS[templateId][source] = variant;
}

/**
 * Get source-specific variable overrides for template generation
 * Returns variables that should be merged into the template variables
 */
export function getSourceVariableOverrides(
  source: LeadSource,
  templateId: string
): Record<string, any> {
  const variant = getSourceVariant(source, templateId);

  return {
    _sourceSubject: variant.subject,
    _sourcePreheader: variant.preheader,
    _sourceOpeningLine: variant.openingLine,
    _sourceTone: variant.tone,
    _sourceContextualNote: variant.contextualNote,
  };
}

/**
 * Apply source variant to existing content
 * Useful for post-processing generated content
 */
export function applySourceVariant(
  content: { subject: string; body: string; preheader?: string },
  source: LeadSource,
  templateId: string
): { subject: string; body: string; preheader?: string } {
  const variant = getSourceVariant(source, templateId);

  return {
    subject: variant.subject || content.subject,
    body: content.body,
    preheader: variant.preheader || content.preheader,
  };
}

/**
 * Get recommended tone for a source (for use in AI generation)
 */
export function getSourceTone(source: LeadSource): 'professional' | 'casual' | 'friendly' | 'urgent' | 'educational' {
  const toneMap: Record<LeadSource, 'professional' | 'casual' | 'friendly' | 'urgent' | 'educational'> = {
    website: 'friendly',
    landing_page: 'friendly',
    social_media: 'casual',
    email_referral: 'friendly',
    partner: 'professional',
    event: 'professional',
    manual: 'friendly',
    import: 'friendly',
    api: 'professional',
    other: 'friendly',
  };

  return toneMap[source] || 'friendly';
}
