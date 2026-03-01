/**
 * Email Marketing Automation Package
 *
 * Main entry point for the niche-agnostic email marketing system
 */

// Core components
export { GmailClient } from './core/email/gmail-client';
export type {
  GmailConfig,
  SendEmailRequest,
  SendEmailResponse
} from './core/email/gmail-client';

export { GoogleSheetsStorage } from './core/leads/google-sheets-storage';
export type {
  GoogleSheetsConfig,
  SheetColumn
} from './core/leads/google-sheets-storage';

export { SequenceEngine } from './core/sequences/sequence-engine';
export type {
  EmailSequence,
  SequenceStep,
  SequenceEnrollment,
  SequenceStatus,
  EmailTrigger,
  SequenceStepType
} from './core/sequences/sequence-engine';

export { ContentGenerator, DEFAULT_TEMPLATES } from './core/ai/content-generator';
export type {
  AIConfig,
  AIProvider,
  ContentTemplate,
  GenerateContentRequest,
  GeneratedContent
} from './core/ai/content-generator';

// Lead types
export type {
  Lead,
  LeadStatus,
  LeadSource,
  LeadEngagement,
  LeadCustomField,
  LeadCreateInput,
  LeadUpdateInput,
  LeadFilter,
  LeadSort,
  LeadPagination,
  LeadListResponse
} from './types/lead';

// Main orchestrator class
import { GmailClient } from './core/email/gmail-client';
import { GoogleSheetsStorage } from './core/leads/google-sheets-storage';
import { SequenceEngine } from './core/sequences/sequence-engine';
import { ContentGenerator } from './core/ai/content-generator';
import type { GmailConfig } from './core/email/gmail-client';
import type { GoogleSheetsConfig } from './core/leads/google-sheets-storage';
import type { AIConfig } from './core/ai/content-generator';

export interface EmailAutomationConfig {
  gmail: GmailConfig;
  ai: AIConfig;
  storage: {
    type: 'google-sheets' | 'database';
    config: GoogleSheetsConfig | any; // Database config TBD
  };
}

export class EmailAutomation {
  public email: GmailClient;
  public leads: GoogleSheetsStorage;
  public sequences: SequenceEngine;
  public ai: ContentGenerator;

  constructor(config: EmailAutomationConfig) {
    // Initialize email client
    this.email = new GmailClient(config.gmail);

    // Initialize storage
    if (config.storage.type === 'google-sheets') {
      this.leads = new GoogleSheetsStorage(config.storage.config as GoogleSheetsConfig);
    } else {
      throw new Error('Database storage not yet implemented');
    }

    // Initialize sequence engine
    this.sequences = new SequenceEngine();

    // Initialize AI content generator
    this.ai = new ContentGenerator(config.ai);
  }

  /**
   * Quick method to enroll a lead in a welcome sequence
   */
  async enrollInWelcomeSequence(email: string, firstName?: string, source?: string) {
    // Create or get lead
    let lead = await this.leads.getByEmail(email);

    if (!lead) {
      lead = await this.leads.create({
        email,
        firstName,
        source: (source as any) || 'website',
        consentGiven: true,
      });
    }

    // Find welcome sequence
    const sequences = await this.sequences.listSequences({
      status: 'active'
    });
    const welcomeSequence = sequences.find(s =>
      s.name.toLowerCase().includes('welcome')
    );

    if (!welcomeSequence) {
      throw new Error('No active welcome sequence found');
    }

    // Enroll lead
    return await this.sequences.enrollLead(lead, welcomeSequence.id);
  }

  /**
   * Process next steps for all active enrollments
   * This would typically be called by a cron job
   */
  async processSequences() {
    // This is a simplified version - in production you'd want:
    // - Batch processing
    // - Error handling
    // - Rate limiting
    // - Logging

    const leads = await this.leads.list();

    for (const lead of leads.leads) {
      const enrollments = await this.sequences.getLeadEnrollments(lead.id, {
        status: 'active'
      });

      for (const enrollment of enrollments) {
        const nextStep = await this.sequences.getNextStep(enrollment.id);

        if (nextStep && nextStep.type === 'email') {
          // Generate content
          const content = await this.ai.generateContent({
            templateId: nextStep.config.templateId,
            variables: {
              firstName: lead.firstName,
              email: lead.email,
              company: lead.company,
            },
          });

          // Send email
          try {
            const result = await this.email.sendEmail({
              to: lead.email,
              subject: content.subject,
              body: content.body,
            });

            // Record execution
            await this.sequences.executeStep(
              enrollment.id,
              nextStep.id,
              'success',
              { messageId: result.messageId }
            );

            // Update lead engagement
            await this.leads.update(lead.id, {
              lastContactedAt: new Date(),
              'engagement.emailsSent': (lead.engagement.emailsSent || 0) + 1,
            });
          } catch (error) {
            // Record failure
            await this.sequences.executeStep(
              enrollment.id,
              nextStep.id,
              'failed',
              { error: (error as Error).message }
            );
          }
        }
      }
    }
  }
}