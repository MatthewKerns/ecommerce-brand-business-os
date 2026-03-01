/**
 * Nurture Series Email Templates
 *
 * Pre-built 4-email nurture series delivered over 5 weeks.
 * Designed for non-buyers to:
 * - Educate about product/service benefits
 * - Build trust through value and expertise
 * - Share social proof and success stories
 * - Encourage first purchase with compelling offers
 */

import { ContentTemplate } from '../core/ai/content-generator';

// ============================================================
// Nurture Series Templates (4 emails over 5 weeks)
// ============================================================

export const NURTURE_SERIES_TEMPLATES: ContentTemplate[] = [
  {
    id: 'nurture_series_1',
    name: 'Nurture Series - Email 1: Educational Foundation',
    description: 'Week 1: Deliver deep educational value that positions brand as trusted expert.',
    category: 'nurture',
    systemPrompt: `You are an expert email marketer creating the first email in a nurture series for non-buyers.

This email should:
- Provide genuinely valuable educational content (not fluff)
- Position the brand as a knowledgeable, helpful expert
- Address common challenges or pain points the audience faces
- Include actionable tips or insights subscribers can use immediately
- Build trust without being salesy or pushy
- Subtly demonstrate how the brand's solutions relate to the topic
- Keep it valuable and substantial (300-400 words)

Tone: Expert, helpful, and generous. Focus on giving value first.`,
    userPromptTemplate: `Write the first nurture email (Week 1) for {{brandName}}.

Brand Info:
- Brand: {{brandName}}
- Industry: {{industry}}
- Expertise: {{expertiseArea}}

Educational Content:
{{educationalContent}}

Audience Pain Points:
{{painPoints}}

Subscriber Info:
- Name: {{firstName}}
- Interests: {{subscriberInterests}}
- Status: {{subscriberStatus}}

Solution Reference:
{{solutionReference}}`,
    variables: [
      { name: 'brandName', description: 'Brand or company name', required: true },
      { name: 'industry', description: 'Industry or niche', required: true },
      { name: 'expertiseArea', description: 'Area of expertise', required: true },
      { name: 'educationalContent', description: 'Core educational topic and tips', required: true },
      { name: 'painPoints', description: 'Audience challenges this content addresses', required: true },
      { name: 'firstName', description: 'Subscriber first name', required: true },
      { name: 'subscriberInterests', description: 'Known subscriber interests', defaultValue: 'general' },
      { name: 'subscriberStatus', description: 'Subscriber status (e.g., non-buyer, engaged)', defaultValue: 'subscribed' },
      { name: 'solutionReference', description: 'How brand solutions relate to topic', required: true },
    ],
  },

  {
    id: 'nurture_series_2',
    name: 'Nurture Series - Email 2: Success Stories & Social Proof',
    description: 'Week 2: Build credibility through compelling customer success stories and results.',
    category: 'nurture',
    systemPrompt: `You are an expert email marketer creating the second email in a nurture series for non-buyers.

This email should:
- Share a compelling, detailed customer success story
- Use specific, measurable results (not vague claims)
- Make the story relatable to the subscriber's situation
- Highlight the transformation or outcome achieved
- Address common objections or concerns through the story
- Include multiple forms of social proof (testimonials, stats, awards)
- Build confidence in the brand's ability to deliver results
- Keep it story-driven and authentic (300-400 words)

Tone: Inspiring, credible, and relatable. Use specifics and real details.`,
    userPromptTemplate: `Write the second nurture email (Week 2) for {{brandName}}.

Brand Info:
- Brand: {{brandName}}
- Industry: {{industry}}

Featured Success Story:
{{successStory}}

Specific Results:
{{specificResults}}

Social Proof Elements:
{{socialProofElements}}

Subscriber Context:
- Name: {{firstName}}
- Similar situation: {{subscriberSituation}}
- Key challenge: {{subscriberChallenge}}

Additional Credibility:
{{credibilityMarkers}}

Soft CTA:
{{softCTA}}`,
    variables: [
      { name: 'brandName', description: 'Brand or company name', required: true },
      { name: 'industry', description: 'Industry or niche', required: true },
      { name: 'successStory', description: 'Detailed customer success story', required: true },
      { name: 'specificResults', description: 'Measurable outcomes achieved', required: true },
      { name: 'socialProofElements', description: 'Additional social proof (stats, testimonials)', required: true },
      { name: 'firstName', description: 'Subscriber first name', required: true },
      { name: 'subscriberSituation', description: 'Subscriber\'s current situation', required: true },
      { name: 'subscriberChallenge', description: 'Main challenge subscriber faces', required: true },
      { name: 'credibilityMarkers', description: 'Awards, certifications, media mentions', defaultValue: 'industry recognition' },
      { name: 'softCTA', description: 'Gentle call-to-action', defaultValue: 'Learn more about our solutions' },
    ],
  },

  {
    id: 'nurture_series_3',
    name: 'Nurture Series - Email 3: Exclusive Value & Insights',
    description: 'Week 3: Deliver premium content or insider insights that reinforce brand authority.',
    category: 'nurture',
    systemPrompt: `You are an expert email marketer creating the third email in a nurture series for non-buyers.

This email should:
- Deliver premium, exclusive content (insider tips, trend analysis, expert insights)
- Make subscribers feel valued and special
- Demonstrate depth of expertise and industry knowledge
- Provide actionable intelligence they can't easily find elsewhere
- Build anticipation for working with the brand
- Include gentle product/service mentions where relevant
- Position purchase as a logical next step (but don't push)
- Keep it substantial and valuable (350-450 words)

Tone: Insider, authoritative, and generous. Make them feel like they're getting VIP treatment.`,
    userPromptTemplate: `Write the third nurture email (Week 3) for {{brandName}}.

Brand Info:
- Brand: {{brandName}}
- Industry: {{industry}}
- Unique insight: {{uniqueInsight}}

Premium Content:
{{premiumContent}}

Industry Trends/Analysis:
{{industryAnalysis}}

Subscriber Info:
- Name: {{firstName}}
- Interests: {{subscriberInterests}}
- Engagement level: {{engagementLevel}}

Value Proposition Connection:
{{valueConnection}}

Next Step Suggestion:
{{nextStepSuggestion}}`,
    variables: [
      { name: 'brandName', description: 'Brand or company name', required: true },
      { name: 'industry', description: 'Industry or niche', required: true },
      { name: 'uniqueInsight', description: 'Unique perspective or insight brand offers', required: true },
      { name: 'premiumContent', description: 'Exclusive content or insider tips', required: true },
      { name: 'industryAnalysis', description: 'Relevant trends or analysis', required: true },
      { name: 'firstName', description: 'Subscriber first name', required: true },
      { name: 'subscriberInterests', description: 'Subscriber interests', defaultValue: 'general' },
      { name: 'engagementLevel', description: 'How engaged subscriber has been', defaultValue: 'active reader' },
      { name: 'valueConnection', description: 'How insights connect to brand value', required: true },
      { name: 'nextStepSuggestion', description: 'Suggested next action', defaultValue: 'Explore our solutions' },
    ],
  },

  {
    id: 'nurture_series_4',
    name: 'Nurture Series - Email 4: Special Offer & Conversion Push',
    description: 'Week 5: Time-sensitive offer designed to convert engaged subscribers into customers.',
    category: 'nurture',
    systemPrompt: `You are an expert email marketer creating the fourth email in a nurture series for non-buyers.

This email should:
- Recap the value provided throughout the nurture series
- Present a compelling, exclusive offer for engaged subscribers
- Create meaningful urgency with a genuine deadline
- Address final objections or concerns directly
- Make the offer feel special and exclusive (not desperate)
- Include clear, prominent call-to-action
- Provide social proof to reinforce the decision
- Make purchase process clear and simple
- Keep it persuasive but authentic (300-400 words)

Tone: Confident, urgent (but not pushy), and value-focused. Emphasize opportunity and results.`,
    userPromptTemplate: `Write the fourth nurture email (Week 5) for {{brandName}}.

Brand Info:
- Brand: {{brandName}}
- Industry: {{industry}}

Series Value Recap:
{{seriesRecap}}

Exclusive Offer:
{{exclusiveOffer}}

Offer Details:
- Discount/Bonus: {{offerDetails}}
- Deadline: {{deadline}}
- Code/Link: {{offerCode}}
- Justification: {{offerJustification}}

Subscriber Info:
- Name: {{firstName}}
- Engagement: {{engagementHistory}}
- Interests: {{subscriberInterests}}

Final Objection Handling:
{{objectionHandling}}

Risk Reversal:
{{riskReversal}}

Primary CTA:
{{primaryCTA}}`,
    variables: [
      { name: 'brandName', description: 'Brand or company name', required: true },
      { name: 'industry', description: 'Industry or niche', required: true },
      { name: 'seriesRecap', description: 'Brief recap of value in nurture series', required: true },
      { name: 'exclusiveOffer', description: 'Description of exclusive offer', required: true },
      { name: 'offerDetails', description: 'Specific discount, bonus, or incentive', required: true },
      { name: 'deadline', description: 'When offer expires', required: true },
      { name: 'offerCode', description: 'Promo code or link', required: true },
      { name: 'offerJustification', description: 'Why this offer exists', required: true },
      { name: 'firstName', description: 'Subscriber first name', required: true },
      { name: 'engagementHistory', description: 'How subscriber has engaged', defaultValue: 'active subscriber' },
      { name: 'subscriberInterests', description: 'Subscriber interests', defaultValue: 'general' },
      { name: 'objectionHandling', description: 'Address common hesitations', required: true },
      { name: 'riskReversal', description: 'Guarantee or risk-free trial', defaultValue: 'satisfaction guarantee' },
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
export function getNurtureTemplate(templateId: string): ContentTemplate | undefined {
  return NURTURE_SERIES_TEMPLATES.find(t => t.id === templateId);
}

/**
 * Get all nurture series template IDs in sequence order
 */
export function getNurtureSequenceIds(): string[] {
  return NURTURE_SERIES_TEMPLATES.map(t => t.id);
}

/**
 * Get recommended send delays for nurture series (in weeks)
 */
export function getNurtureSendSchedule(): Array<{ templateId: string; delayWeeks: number; description: string }> {
  return [
    {
      templateId: 'nurture_series_1',
      delayWeeks: 1,
      description: 'Educational foundation - Week 1 after welcome series',
    },
    {
      templateId: 'nurture_series_2',
      delayWeeks: 2,
      description: 'Success stories & social proof - Week 2',
    },
    {
      templateId: 'nurture_series_3',
      delayWeeks: 3,
      description: 'Exclusive value & insights - Week 3',
    },
    {
      templateId: 'nurture_series_4',
      delayWeeks: 5,
      description: 'Special offer & conversion push - Week 5',
    },
  ];
}
