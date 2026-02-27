/**
 * Email Templates - Central export point for all email templates
 *
 * This module provides:
 * - Welcome series templates (4 emails over 7 days)
 * - Nurture series templates (4 emails over 5 weeks)
 * - Template registry for managing all templates
 * - Helper functions for template lookup and scheduling
 */

// Export welcome series
export {
  WELCOME_SERIES_TEMPLATES,
  getWelcomeTemplate,
  getWelcomeSequenceIds,
  getWelcomeSendSchedule,
} from './welcome-series';

// Export nurture series
export {
  NURTURE_SERIES_TEMPLATES,
  getNurtureTemplate,
  getNurtureSequenceIds,
  getNurtureSendSchedule,
} from './nurture-series';

// Export template registry
export {
  TemplateRegistry,
  defaultTemplateRegistry,
  type TemplateMetadata,
  type TemplateCategory,
} from './registry';

// Re-export ContentTemplate type for convenience
export type { ContentTemplate } from '../core/ai/content-generator';
