/**
 * AI Content Generator - Provider-agnostic AI content generation
 *
 * Features:
 * - Multiple AI provider support (Gemini, OpenAI, Claude)
 * - Configurable prompts per niche
 * - Template-based generation
 * - Safety filters
 * - Personalization engine
 */

import { GoogleGenerativeAI } from '@google/generative-ai';
import OpenAI from 'openai';
import Anthropic from 'anthropic';
import type { Lead } from '@/types/lead';
import {
  PersonalizationRulesEngine,
  type PersonalizationRule,
  type PersonalizationContext,
} from '@/core/personalization/rules-engine';
import {
  InterestMatcher,
  type Interest,
  type InterestCategory,
  type InterestMatchResult,
} from '@/core/personalization/interest-matcher';

// ============================================================
// Types
// ============================================================

export type AIProvider = 'gemini' | 'openai' | 'claude';

export interface AIConfig {
  provider: AIProvider;
  apiKey: string;
  model?: string;
  temperature?: number;
  maxTokens?: number;
}

export interface ContentTemplate {
  id: string;
  name: string;
  description?: string;
  category: 'welcome' | 'nurture' | 'promotional' | 'transactional' | 'custom';
  systemPrompt: string;
  userPromptTemplate: string;
  variables: Array<{
    name: string;
    description: string;
    required?: boolean;
    defaultValue?: string;
  }>;
}

export interface GenerateContentRequest {
  templateId?: string;
  template?: ContentTemplate;
  variables: Record<string, any>;
  context?: Record<string, any>;
  tone?: 'professional' | 'casual' | 'friendly' | 'urgent' | 'educational';
  length?: 'short' | 'medium' | 'long';
  lead?: Lead; // Optional Lead for personalization
  applyPersonalization?: boolean; // Whether to apply personalization rules
}

export interface GeneratedContent {
  subject: string;
  body: string;
  preheader?: string;
  metadata?: {
    provider: AIProvider;
    model: string;
    templateId?: string;
    generatedAt: Date;
    tokensUsed?: number;
    personalizationApplied?: boolean;
    rulesApplied?: string[];
  };
}

// ============================================================
// Default Templates
// ============================================================

export const DEFAULT_TEMPLATES: ContentTemplate[] = [
  {
    id: 'welcome_email',
    name: 'Welcome Email',
    category: 'welcome',
    systemPrompt: `You are an expert email marketer. Create a warm, engaging welcome email that:
- Thanks the subscriber for joining
- Sets expectations for future emails
- Provides immediate value
- Includes a clear call-to-action
Keep the tone conversational and friendly.`,
    userPromptTemplate: `Write a welcome email for {{companyName}}.
Subscriber name: {{subscriberName}}
How they joined: {{source}}
Main value proposition: {{valueProp}}
First action to take: {{firstAction}}`,
    variables: [
      { name: 'companyName', description: 'Your company name', required: true },
      { name: 'subscriberName', description: 'Subscriber first name', required: true },
      { name: 'source', description: 'How they joined', defaultValue: 'website' },
      { name: 'valueProp', description: 'Main value proposition', required: true },
      { name: 'firstAction', description: 'First action for subscriber', required: true },
    ],
  },
  {
    id: 'nurture_educational',
    name: 'Educational Nurture',
    category: 'nurture',
    systemPrompt: `You are an expert content marketer. Create an educational email that:
- Provides valuable insights or tips
- Positions the company as an expert
- Builds trust without being salesy
- Includes subtle product/service mentions where relevant
Keep it informative and helpful.`,
    userPromptTemplate: `Write an educational email about {{topic}}.
Company: {{companyName}}
Target audience: {{audience}}
Key learning points: {{keyPoints}}
Related product/service: {{relatedOffering}}`,
    variables: [
      { name: 'topic', description: 'Educational topic', required: true },
      { name: 'companyName', description: 'Your company name', required: true },
      { name: 'audience', description: 'Target audience', required: true },
      { name: 'keyPoints', description: 'Key learning points', required: true },
      { name: 'relatedOffering', description: 'Related product/service' },
    ],
  },
  {
    id: 'promotional_offer',
    name: 'Promotional Offer',
    category: 'promotional',
    systemPrompt: `You are an expert copywriter. Create a compelling promotional email that:
- Highlights the offer clearly
- Creates urgency without being pushy
- Shows the value and benefits
- Has a strong call-to-action
Keep it persuasive but authentic.`,
    userPromptTemplate: `Write a promotional email for {{offerType}}.
Company: {{companyName}}
Discount/Offer: {{offer}}
Valid until: {{deadline}}
Key benefits: {{benefits}}
Call-to-action: {{cta}}`,
    variables: [
      { name: 'offerType', description: 'Type of offer', required: true },
      { name: 'companyName', description: 'Your company name', required: true },
      { name: 'offer', description: 'The offer details', required: true },
      { name: 'deadline', description: 'Offer deadline' },
      { name: 'benefits', description: 'Key benefits', required: true },
      { name: 'cta', description: 'Call-to-action text', required: true },
    ],
  },
];

// ============================================================
// Content Generator Class
// ============================================================

export class ContentGenerator {
  private config: AIConfig;
  private templates: Map<string, ContentTemplate>;
  private geminiClient?: GoogleGenerativeAI;
  private openaiClient?: OpenAI;
  private claudeClient?: Anthropic;
  private personalizationEngine?: PersonalizationRulesEngine;
  private interestMatcher?: InterestMatcher;

  constructor(
    config: AIConfig,
    customTemplates?: ContentTemplate[],
    personalizationRules?: PersonalizationRule[]
  ) {
    this.config = config;
    this.templates = new Map();

    // Load default templates
    DEFAULT_TEMPLATES.forEach(t => this.templates.set(t.id, t));

    // Add custom templates
    customTemplates?.forEach(t => this.templates.set(t.id, t));

    // Initialize appropriate client
    this.initializeClient();

    // Initialize personalization engine if rules provided
    if (personalizationRules && personalizationRules.length > 0) {
      this.personalizationEngine = new PersonalizationRulesEngine(personalizationRules);
    }
  }

  /**
   * Initialize AI client based on provider
   */
  private initializeClient(): void {
    switch (this.config.provider) {
      case 'gemini':
        this.geminiClient = new GoogleGenerativeAI(this.config.apiKey);
        break;
      case 'openai':
        this.openaiClient = new OpenAI({ apiKey: this.config.apiKey });
        break;
      case 'claude':
        this.claudeClient = new Anthropic({ apiKey: this.config.apiKey });
        break;
    }
  }

  /**
   * Generate email content using AI
   */
  async generateContent(request: GenerateContentRequest): Promise<GeneratedContent> {
    // Get template
    const template = request.templateId
      ? this.templates.get(request.templateId)
      : request.template;

    if (!template) {
      throw new Error(`Template not found: ${request.templateId}`);
    }

    // Apply personalization if requested and available
    let variables = { ...request.variables };
    let rulesApplied: string[] = [];
    let personalizationApplied = false;

    if (request.applyPersonalization !== false && request.lead && this.personalizationEngine) {
      const personalizationContext: PersonalizationContext = {
        lead: request.lead,
        variables: { ...variables },
        metadata: request.context,
      };

      const personalizationResult = this.personalizationEngine.evaluateRules(
        personalizationContext
      );

      if (personalizationResult.matched) {
        variables = personalizationResult.transformedVariables;
        rulesApplied = personalizationResult.rulesApplied;
        personalizationApplied = true;

        // Apply tone and length overrides if set by personalization
        if (variables._tone && !request.tone) {
          request.tone = variables._tone;
        }
        if (variables._length && !request.length) {
          request.length = variables._length;
        }
      }
    }

    // Validate required variables
    for (const variable of template.variables) {
      if (variable.required && !variables[variable.name]) {
        throw new Error(`Required variable missing: ${variable.name}`);
      }
    }

    // Build prompt
    const systemPrompt = this.enhanceSystemPrompt(template.systemPrompt, request);
    const userPrompt = this.substituteVariables(template.userPromptTemplate, {
      ...variables,
      ...request.context,
    });

    // Generate content based on provider
    const content = await this.callAIProvider(systemPrompt, userPrompt);

    // Parse and structure the response
    const generatedContent = this.parseAIResponse(content, template.id);

    // Add personalization metadata
    if (personalizationApplied) {
      generatedContent.metadata = {
        ...generatedContent.metadata,
        personalizationApplied: true,
        rulesApplied,
      };
    }

    return generatedContent;
  }

  /**
   * Generate content without a template
   */
  async generateCustomContent(
    systemPrompt: string,
    userPrompt: string
  ): Promise<GeneratedContent> {
    const content = await this.callAIProvider(systemPrompt, userPrompt);
    return this.parseAIResponse(content);
  }

  /**
   * Add a custom template
   */
  addTemplate(template: ContentTemplate): void {
    this.templates.set(template.id, template);
  }

  /**
   * Get all templates
   */
  getTemplates(): ContentTemplate[] {
    return Array.from(this.templates.values());
  }

  /**
   * Get template by ID
   */
  getTemplate(id: string): ContentTemplate | undefined {
    return this.templates.get(id);
  }

  /**
   * Set personalization engine
   */
  setPersonalizationEngine(engine: PersonalizationRulesEngine): void {
    this.personalizationEngine = engine;
  }

  /**
   * Get personalization engine
   */
  getPersonalizationEngine(): PersonalizationRulesEngine | undefined {
    return this.personalizationEngine;
  }

  /**
   * Add personalization rule
   */
  addPersonalizationRule(rule: PersonalizationRule): void {
    if (!this.personalizationEngine) {
      this.personalizationEngine = new PersonalizationRulesEngine([rule]);
    } else {
      this.personalizationEngine.addRule(rule);
    }
  }

  /**
   * Remove personalization rule
   */
  removePersonalizationRule(ruleId: string): boolean {
    return this.personalizationEngine?.removeRule(ruleId) || false;
  }

  /**
   * Get personalization suggestions for a lead
   */
  getPersonalizationSuggestions(lead: Lead): {
    ruleId: string;
    ruleName: string;
    description?: string;
  }[] {
    if (!this.personalizationEngine) {
      return [];
    }
    return this.personalizationEngine.getPersonalizationSuggestions(lead);
  }

  /**
   * Set interest matcher
   */
  setInterestMatcher(matcher: InterestMatcher): void {
    this.interestMatcher = matcher;
  }

  /**
   * Get interest matcher
   */
  getInterestMatcher(): InterestMatcher | undefined {
    return this.interestMatcher;
  }

  /**
   * Enable interest-based personalization (creates matcher if not exists)
   */
  enableInterestPersonalization(customCategories?: InterestCategory[]): void {
    if (!this.interestMatcher) {
      this.interestMatcher = new InterestMatcher(customCategories);
    }
  }

  /**
   * Get lead interests
   */
  getLeadInterests(lead: Lead): Interest[] {
    if (!this.interestMatcher) {
      this.interestMatcher = new InterestMatcher();
    }
    return this.interestMatcher.extractInterests(lead);
  }

  /**
   * Match lead interests and get recommendations
   */
  matchLeadInterests(lead: Lead): InterestMatchResult {
    if (!this.interestMatcher) {
      this.interestMatcher = new InterestMatcher();
    }
    return this.interestMatcher.matchInterests(lead);
  }

  /**
   * Apply interest-based personalization to content generation
   * This automatically adds interest-based rules to the personalization engine
   */
  applyInterestBasedPersonalization(lead: Lead): void {
    if (!this.interestMatcher) {
      this.interestMatcher = new InterestMatcher();
    }

    // Get interest-based personalization rules
    const interestRules = this.interestMatcher.getPersonalizationRules(lead);

    // Add rules to personalization engine
    for (const rule of interestRules) {
      this.addPersonalizationRule(rule);
    }
  }

  /**
   * Generate content with automatic interest-based personalization
   */
  async generateWithInterests(
    request: GenerateContentRequest
  ): Promise<GeneratedContent> {
    // If lead is provided and interest personalization is not explicitly disabled
    if (request.lead && request.applyPersonalization !== false) {
      // Ensure interest matcher exists
      if (!this.interestMatcher) {
        this.interestMatcher = new InterestMatcher();
      }

      // Apply interest-based personalization rules
      this.applyInterestBasedPersonalization(request.lead);

      // Get interest match results for metadata
      const interestMatch = this.interestMatcher.matchInterests(request.lead);

      // Generate content with standard personalization (which now includes interest rules)
      const content = await this.generateContent(request);

      // Add interest metadata
      if (content.metadata) {
        content.metadata = {
          ...content.metadata,
          interestsDetected: interestMatch.topInterests.length,
          topInterests: interestMatch.topInterests.map(i => i.name),
          primaryCategory: interestMatch.metadata.primaryCategory,
        };
      }

      return content;
    }

    // Fall back to standard generation if no lead or personalization disabled
    return this.generateContent(request);
  }

  // ============================================================
  // Private Methods
  // ============================================================

  private enhanceSystemPrompt(basePrompt: string, request: GenerateContentRequest): string {
    let enhanced = basePrompt;

    // Add tone guidance
    if (request.tone) {
      enhanced += `\n\nTone: Keep the tone ${request.tone}.`;
    }

    // Add length guidance
    if (request.length) {
      const lengthGuide = {
        short: 'Keep it brief - 50-100 words.',
        medium: 'Aim for 150-250 words.',
        long: 'Write a comprehensive email - 300-500 words.',
      };
      enhanced += `\n\nLength: ${lengthGuide[request.length]}`;
    }

    // Add format guidance
    enhanced += `\n\nFormat the response as JSON with the following structure:
{
  "subject": "Email subject line",
  "preheader": "Preview text (optional)",
  "body": "Email body content (use \\n\\n for paragraphs)"
}`;

    return enhanced;
  }

  private substituteVariables(template: string, variables: Record<string, any>): string {
    let result = template;

    for (const [key, value] of Object.entries(variables)) {
      const pattern = new RegExp(`{{\\s*${key}\\s*}}`, 'gi');
      result = result.replace(pattern, String(value));
    }

    return result;
  }

  private async callAIProvider(systemPrompt: string, userPrompt: string): Promise<string> {
    switch (this.config.provider) {
      case 'gemini':
        return this.callGemini(systemPrompt, userPrompt);
      case 'openai':
        return this.callOpenAI(systemPrompt, userPrompt);
      case 'claude':
        return this.callClaude(systemPrompt, userPrompt);
      default:
        throw new Error(`Unsupported AI provider: ${this.config.provider}`);
    }
  }

  private async callGemini(systemPrompt: string, userPrompt: string): Promise<string> {
    if (!this.geminiClient) {
      throw new Error('Gemini client not initialized');
    }

    const model = this.geminiClient.getGenerativeModel({
      model: this.config.model || 'gemini-1.5-flash',
      generationConfig: {
        temperature: this.config.temperature || 0.7,
        maxOutputTokens: this.config.maxTokens || 1000,
      },
    });

    const prompt = `${systemPrompt}\n\n${userPrompt}`;
    const result = await model.generateContent(prompt);
    const response = await result.response;
    return response.text();
  }

  private async callOpenAI(systemPrompt: string, userPrompt: string): Promise<string> {
    if (!this.openaiClient) {
      throw new Error('OpenAI client not initialized');
    }

    const completion = await this.openaiClient.chat.completions.create({
      model: this.config.model || 'gpt-4-turbo-preview',
      messages: [
        { role: 'system', content: systemPrompt },
        { role: 'user', content: userPrompt },
      ],
      temperature: this.config.temperature || 0.7,
      max_tokens: this.config.maxTokens || 1000,
    });

    return completion.choices[0]?.message?.content || '';
  }

  private async callClaude(systemPrompt: string, userPrompt: string): Promise<string> {
    if (!this.claudeClient) {
      throw new Error('Claude client not initialized');
    }

    const message = await this.claudeClient.messages.create({
      model: this.config.model || 'claude-3-opus-20240229',
      messages: [{ role: 'user', content: userPrompt }],
      system: systemPrompt,
      max_tokens: this.config.maxTokens || 1000,
      temperature: this.config.temperature || 0.7,
    });

    return message.content[0]?.type === 'text' ? message.content[0].text : '';
  }

  private parseAIResponse(content: string, templateId?: string): GeneratedContent {
    try {
      // Try to parse as JSON first
      const parsed = JSON.parse(content);
      return {
        subject: parsed.subject || 'No subject',
        body: parsed.body || content,
        preheader: parsed.preheader,
        metadata: {
          provider: this.config.provider,
          model: this.config.model || this.getDefaultModel(),
          templateId,
          generatedAt: new Date(),
        },
      };
    } catch {
      // If not JSON, treat as plain text
      // Extract subject from first line if it looks like a subject
      const lines = content.split('\n');
      const firstLine = lines[0].trim();
      const isSubjectLine = firstLine.length < 100 && !firstLine.endsWith('.');

      return {
        subject: isSubjectLine ? firstLine : 'Email Update',
        body: isSubjectLine ? lines.slice(1).join('\n').trim() : content,
        metadata: {
          provider: this.config.provider,
          model: this.config.model || this.getDefaultModel(),
          templateId,
          generatedAt: new Date(),
        },
      };
    }
  }

  private getDefaultModel(): string {
    switch (this.config.provider) {
      case 'gemini':
        return 'gemini-1.5-flash';
      case 'openai':
        return 'gpt-4-turbo-preview';
      case 'claude':
        return 'claude-3-opus-20240229';
      default:
        return 'unknown';
    }
  }
}