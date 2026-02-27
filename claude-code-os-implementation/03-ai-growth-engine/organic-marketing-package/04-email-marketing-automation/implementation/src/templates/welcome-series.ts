/**
 * Welcome Series Email Templates
 *
 * Pre-built 4-email welcome series delivered over 7 days.
 * Designed to:
 * - Welcome new subscribers warmly
 * - Educate about brand/product value
 * - Build trust through social proof
 * - Guide toward first purchase
 */

import { ContentTemplate } from '../core/ai/content-generator';

// ============================================================
// Welcome Series Templates (4 emails over 7 days)
// ============================================================

export const WELCOME_SERIES_TEMPLATES: ContentTemplate[] = [
  {
    id: 'welcome_series_1',
    name: 'Welcome Series - Email 1: Warm Welcome',
    description: 'Immediate welcome email sent upon subscription. Sets expectations and delivers instant value.',
    category: 'welcome',
    systemPrompt: `You are an expert email marketer creating the first email in a welcome series.

This email should:
- Thank the subscriber warmly for joining
- Set clear expectations for future emails (frequency, content type)
- Provide immediate value (quick tip, resource, or discount code)
- Establish a friendly, authentic brand voice
- Include a simple, non-intimidating call-to-action
- Keep it brief and scannable (under 200 words)

Tone: Warm, welcoming, and genuine. Avoid being overly salesy.`,
    userPromptTemplate: `Write the first welcome email for {{brandName}}.

Brand Info:
- Brand: {{brandName}}
- Industry: {{industry}}
- What we do: {{valueProposition}}

Subscriber Info:
- Name: {{firstName}}
- Signed up via: {{signupSource}}

Welcome Offer:
{{welcomeOffer}}

Expected Email Frequency: {{emailFrequency}}`,
    variables: [
      { name: 'brandName', description: 'Brand or company name', required: true },
      { name: 'industry', description: 'Industry or niche', required: true },
      { name: 'valueProposition', description: 'What the brand does/offers', required: true },
      { name: 'firstName', description: 'Subscriber first name', required: true },
      { name: 'signupSource', description: 'How they signed up', defaultValue: 'website' },
      { name: 'welcomeOffer', description: 'Welcome gift, discount, or resource', required: true },
      { name: 'emailFrequency', description: 'How often emails are sent', defaultValue: '2-3 times per week' },
    ],
  },

  {
    id: 'welcome_series_2',
    name: 'Welcome Series - Email 2: Educational Value',
    description: 'Sent 2 days after welcome. Delivers educational content that helps subscriber understand the brand better.',
    category: 'welcome',
    systemPrompt: `You are an expert email marketer creating the second email in a welcome series.

This email should:
- Deliver genuine educational value (tips, insights, how-to content)
- Position the brand as a helpful expert, not just a seller
- Reference their recent signup to maintain continuity
- Include subtle product/service mentions where naturally relevant
- Build trust through helpful, actionable information
- Keep it informative but not overwhelming (200-300 words)

Tone: Helpful, knowledgeable, and approachable.`,
    userPromptTemplate: `Write the second welcome email (Day 2) for {{brandName}}.

Brand Info:
- Brand: {{brandName}}
- Industry: {{industry}}
- Expertise area: {{expertiseArea}}

Educational Focus:
{{educationalTopic}}

Subscriber Context:
- Name: {{firstName}}
- Interests: {{subscriberInterests}}

Product/Service to subtly mention:
{{productMention}}`,
    variables: [
      { name: 'brandName', description: 'Brand or company name', required: true },
      { name: 'industry', description: 'Industry or niche', required: true },
      { name: 'expertiseArea', description: 'What the brand is expert in', required: true },
      { name: 'educationalTopic', description: 'Educational topic or tips to share', required: true },
      { name: 'firstName', description: 'Subscriber first name', required: true },
      { name: 'subscriberInterests', description: 'Known or inferred subscriber interests', defaultValue: 'general interest' },
      { name: 'productMention', description: 'Product or service to mention naturally', required: true },
    ],
  },

  {
    id: 'welcome_series_3',
    name: 'Welcome Series - Email 3: Social Proof',
    description: 'Sent 5 days after welcome. Builds credibility through customer success stories and testimonials.',
    category: 'welcome',
    systemPrompt: `You are an expert email marketer creating the third email in a welcome series.

This email should:
- Share compelling social proof (customer story, testimonial, case study)
- Make success stories relatable and specific
- Highlight real results and transformations
- Address common objections or hesitations
- Build confidence in the brand's ability to deliver
- Include a soft call-to-action to explore products/services
- Keep it story-focused and authentic (250-350 words)

Tone: Inspiring, credible, and relatable. Use specific details, not vague claims.`,
    userPromptTemplate: `Write the third welcome email (Day 5) for {{brandName}}.

Brand Info:
- Brand: {{brandName}}
- Industry: {{industry}}

Customer Success Story:
{{customerStory}}

Results Achieved:
{{results}}

Subscriber Info:
- Name: {{firstName}}
- Similar challenges: {{subscriberChallenges}}

Call-to-Action:
{{cta}}`,
    variables: [
      { name: 'brandName', description: 'Brand or company name', required: true },
      { name: 'industry', description: 'Industry or niche', required: true },
      { name: 'customerStory', description: 'Customer success story or testimonial', required: true },
      { name: 'results', description: 'Specific results the customer achieved', required: true },
      { name: 'firstName', description: 'Subscriber first name', required: true },
      { name: 'subscriberChallenges', description: 'Challenges the subscriber likely faces', required: true },
      { name: 'cta', description: 'Call-to-action (e.g., "Browse our products")', required: true },
    ],
  },

  {
    id: 'welcome_series_4',
    name: 'Welcome Series - Email 4: First Purchase Incentive',
    description: 'Sent 7 days after welcome. Encourages first purchase with time-sensitive offer.',
    category: 'welcome',
    systemPrompt: `You are an expert email marketer creating the fourth and final email in a welcome series.

This email should:
- Recap the value provided over the welcome series
- Present a compelling, time-sensitive offer for first purchase
- Create gentle urgency without being pushy
- Make the offer feel exclusive to new subscribers
- Address any last objections clearly
- Include a strong, clear call-to-action
- Make it easy to take the next step (link, button, simple instructions)
- Keep it persuasive but authentic (200-300 words)

Tone: Encouraging, slightly urgent, but not desperate. Focus on value and opportunity.`,
    userPromptTemplate: `Write the fourth welcome email (Day 7) for {{brandName}}.

Brand Info:
- Brand: {{brandName}}
- Industry: {{industry}}

Special Offer:
{{specialOffer}}

Offer Details:
- Discount: {{discountAmount}}
- Expires: {{expirationDate}}
- Code: {{promoCode}}

Value Recap:
{{valueRecap}}

Subscriber Info:
- Name: {{firstName}}
- Interests: {{subscriberInterests}}

Primary CTA:
{{primaryCTA}}`,
    variables: [
      { name: 'brandName', description: 'Brand or company name', required: true },
      { name: 'industry', description: 'Industry or niche', required: true },
      { name: 'specialOffer', description: 'Description of the special offer', required: true },
      { name: 'discountAmount', description: 'Discount percentage or amount', required: true },
      { name: 'expirationDate', description: 'When the offer expires', required: true },
      { name: 'promoCode', description: 'Promotional code to use', required: true },
      { name: 'valueRecap', description: 'Brief recap of value provided in series', required: true },
      { name: 'firstName', description: 'Subscriber first name', required: true },
      { name: 'subscriberInterests', description: 'Known or inferred subscriber interests', defaultValue: 'general interest' },
      { name: 'primaryCTA', description: 'Primary call-to-action text', required: true },
    ],
  },
];

// ============================================================
// Helper Functions
// ============================================================

/**
 * Get template by ID
 */
export function getWelcomeTemplate(templateId: string): ContentTemplate | undefined {
  return WELCOME_SERIES_TEMPLATES.find(t => t.id === templateId);
}

/**
 * Get all welcome series template IDs in sequence order
 */
export function getWelcomeSequenceIds(): string[] {
  return WELCOME_SERIES_TEMPLATES.map(t => t.id);
}

/**
 * Get recommended send delays for welcome series (in days)
 */
export function getWelcomeSendSchedule(): Array<{ templateId: string; delayDays: number; description: string }> {
  return [
    {
      templateId: 'welcome_series_1',
      delayDays: 0,
      description: 'Immediate welcome - sent upon subscription',
    },
    {
      templateId: 'welcome_series_2',
      delayDays: 2,
      description: 'Educational value - sent 2 days after welcome',
    },
    {
      templateId: 'welcome_series_3',
      delayDays: 5,
      description: 'Social proof - sent 5 days after welcome',
    },
    {
      templateId: 'welcome_series_4',
      delayDays: 7,
      description: 'First purchase incentive - sent 7 days after welcome',
    },
  ];
}
