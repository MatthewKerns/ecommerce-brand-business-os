/**
 * Template Registry - Central management for all email templates
 *
 * Features:
 * - Load and manage welcome series templates
 * - Load and manage nurture series templates
 * - Template lookup by ID
 * - Template filtering by category
 * - Template metadata and scheduling
 */

import { ContentTemplate } from '../core/ai/content-generator';
import { WELCOME_SERIES_TEMPLATES, getWelcomeSendSchedule } from './welcome-series';
import { NURTURE_SERIES_TEMPLATES, getNurtureSendSchedule } from './nurture-series';

// ============================================================
// Types
// ============================================================

export interface TemplateMetadata {
  templateId: string;
  name: string;
  description?: string;
  category: string;
  sendDelay?: number;
  sendDelayUnit?: 'days' | 'weeks';
  sequencePosition?: number;
}

export type TemplateCategory = 'welcome' | 'nurture' | 'promotional' | 'transactional' | 'custom';

// ============================================================
// Template Registry Class
// ============================================================

export class TemplateRegistry {
  private templates: Map<string, ContentTemplate>;

  constructor(customTemplates?: ContentTemplate[]) {
    this.templates = new Map();

    // Load welcome series templates
    WELCOME_SERIES_TEMPLATES.forEach(template => {
      this.templates.set(template.id, template);
    });

    // Load nurture series templates
    NURTURE_SERIES_TEMPLATES.forEach(template => {
      this.templates.set(template.id, template);
    });

    // Add custom templates if provided
    customTemplates?.forEach(template => {
      this.templates.set(template.id, template);
    });
  }

  /**
   * Get a template by ID
   */
  getTemplate(id: string): ContentTemplate | undefined {
    return this.templates.get(id);
  }

  /**
   * Get all templates
   */
  listTemplates(): ContentTemplate[] {
    return Array.from(this.templates.values());
  }

  /**
   * Get templates by category
   */
  getTemplatesByCategory(category: TemplateCategory): ContentTemplate[] {
    return this.listTemplates().filter(template => template.category === category);
  }

  /**
   * Get all welcome series templates
   */
  getWelcomeTemplates(): ContentTemplate[] {
    return this.getTemplatesByCategory('welcome');
  }

  /**
   * Get all nurture series templates
   */
  getNurtureTemplates(): ContentTemplate[] {
    return this.getTemplatesByCategory('nurture');
  }

  /**
   * Add a custom template to the registry
   */
  addTemplate(template: ContentTemplate): void {
    this.templates.set(template.id, template);
  }

  /**
   * Remove a template from the registry
   */
  removeTemplate(id: string): boolean {
    return this.templates.delete(id);
  }

  /**
   * Check if a template exists
   */
  hasTemplate(id: string): boolean {
    return this.templates.has(id);
  }

  /**
   * Get total template count
   */
  getTemplateCount(): number {
    return this.templates.size;
  }

  /**
   * Get template metadata with scheduling information
   */
  getTemplateMetadata(id: string): TemplateMetadata | undefined {
    const template = this.getTemplate(id);
    if (!template) {
      return undefined;
    }

    // Get scheduling info from welcome or nurture series
    const welcomeSchedule = getWelcomeSendSchedule().find(s => s.templateId === id);
    const nurtureSchedule = getNurtureSendSchedule().find(s => s.templateId === id);

    const metadata: TemplateMetadata = {
      templateId: template.id,
      name: template.name,
      description: template.description,
      category: template.category,
    };

    if (welcomeSchedule) {
      metadata.sendDelay = welcomeSchedule.delayDays;
      metadata.sendDelayUnit = 'days';
      metadata.sequencePosition = getWelcomeSendSchedule().findIndex(s => s.templateId === id) + 1;
    } else if (nurtureSchedule) {
      metadata.sendDelay = nurtureSchedule.delayWeeks;
      metadata.sendDelayUnit = 'weeks';
      metadata.sequencePosition = getNurtureSendSchedule().findIndex(s => s.templateId === id) + 1;
    }

    return metadata;
  }

  /**
   * Get all template metadata
   */
  listTemplateMetadata(): TemplateMetadata[] {
    return this.listTemplates()
      .map(template => this.getTemplateMetadata(template.id))
      .filter((metadata): metadata is TemplateMetadata => metadata !== undefined);
  }

  /**
   * Get templates by sequence
   */
  getSequenceTemplates(sequenceType: 'welcome' | 'nurture'): ContentTemplate[] {
    if (sequenceType === 'welcome') {
      return WELCOME_SERIES_TEMPLATES;
    } else if (sequenceType === 'nurture') {
      return NURTURE_SERIES_TEMPLATES;
    }
    return [];
  }

  /**
   * Get send schedule for a sequence
   */
  getSequenceSchedule(sequenceType: 'welcome' | 'nurture'): Array<{ templateId: string; delay: number; unit: string; description: string }> {
    if (sequenceType === 'welcome') {
      return getWelcomeSendSchedule().map(schedule => ({
        templateId: schedule.templateId,
        delay: schedule.delayDays,
        unit: 'days',
        description: schedule.description,
      }));
    } else if (sequenceType === 'nurture') {
      return getNurtureSendSchedule().map(schedule => ({
        templateId: schedule.templateId,
        delay: schedule.delayWeeks,
        unit: 'weeks',
        description: schedule.description,
      }));
    }
    return [];
  }
}

// ============================================================
// Singleton Instance
// ============================================================

/**
 * Default template registry instance
 */
export const defaultTemplateRegistry = new TemplateRegistry();
