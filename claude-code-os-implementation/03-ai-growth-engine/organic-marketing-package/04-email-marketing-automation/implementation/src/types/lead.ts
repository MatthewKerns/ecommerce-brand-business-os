/**
 * Lead Types - Niche-agnostic lead data model
 *
 * Core fields are standard across all niches.
 * Custom fields allow niche-specific data.
 */

export type LeadStatus =
  | 'new'                 // Just added, not contacted
  | 'contacted'           // Initial email sent
  | 'engaged'             // Opened or clicked email
  | 'replied'             // Responded to email
  | 'qualified'           // Meets criteria for conversion
  | 'converted'           // Completed desired action
  | 'nurturing'           // In long-term nurture sequence
  | 'paused'              // Temporarily paused
  | 'unsubscribed'        // Opted out
  | 'bounced'             // Email bounced
  | 'invalid';            // Invalid email or data

export type LeadSource =
  | 'website'             // Website form/widget
  | 'landing_page'        // Dedicated landing page
  | 'social_media'        // Social platform
  | 'email_referral'      // Referred by email
  | 'partner'             // Partner referral
  | 'event'               // Event/webinar
  | 'manual'              // Manually added
  | 'import'              // Bulk import
  | 'api'                 // API integration
  | 'other';              // Other source

export interface LeadEngagement {
  emailsSent: number;
  emailsOpened: number;
  emailsClicked: number;
  emailsReplied: number;
  lastEmailSent?: Date;
  lastEmailOpened?: Date;
  lastEmailClicked?: Date;
  lastEngagement?: Date;
}

export interface LeadCustomField {
  key: string;
  value: string | number | boolean | Date | string[];
  type: 'text' | 'number' | 'boolean' | 'date' | 'select' | 'multiselect';
}

export interface Lead {
  // Core fields (required)
  id: string;
  email: string;
  status: LeadStatus;
  source: LeadSource;
  createdAt: Date;
  updatedAt: Date;

  // Contact information (optional)
  firstName?: string;
  lastName?: string;
  fullName?: string;
  phone?: string;
  company?: string;
  jobTitle?: string;
  website?: string;
  timezone?: string;

  // Segmentation
  tags: string[];
  segments: string[];
  score?: number;            // Lead scoring value
  priority?: 'low' | 'medium' | 'high';

  // Engagement tracking
  engagement: LeadEngagement;

  // Sequences
  currentSequence?: string;
  sequenceStep?: number;
  sequenceStartedAt?: Date;
  sequenceCompletedAt?: Date;
  sequencePausedAt?: Date;

  // Custom fields (niche-specific)
  customFields: LeadCustomField[];

  // Consent & compliance
  consentGiven: boolean;
  consentDate?: Date;
  consentSource?: string;
  doNotEmail?: boolean;
  doNotCall?: boolean;

  // Notes & metadata
  notes?: string;
  lastContactedAt?: Date;
  nextFollowUpAt?: Date;
  assignedTo?: string;

  // External IDs for integrations
  externalIds?: {
    crm?: string;
    marketing?: string;
    custom?: Record<string, string>;
  };
}

export interface LeadCreateInput {
  email: string;
  source: LeadSource;
  firstName?: string;
  lastName?: string;
  company?: string;
  tags?: string[];
  customFields?: LeadCustomField[];
  consentGiven?: boolean;
  consentSource?: string;
}

export interface LeadUpdateInput {
  status?: LeadStatus;
  firstName?: string;
  lastName?: string;
  company?: string;
  jobTitle?: string;
  phone?: string;
  website?: string;
  tags?: string[];
  segments?: string[];
  score?: number;
  priority?: 'low' | 'medium' | 'high';
  customFields?: LeadCustomField[];
  notes?: string;
  doNotEmail?: boolean;
  assignedTo?: string;
}

export interface LeadFilter {
  status?: LeadStatus | LeadStatus[];
  source?: LeadSource | LeadSource[];
  tags?: string[];
  segments?: string[];
  priority?: 'low' | 'medium' | 'high';
  assignedTo?: string;
  createdAfter?: Date;
  createdBefore?: Date;
  lastContactedAfter?: Date;
  lastContactedBefore?: Date;
  hasEngagement?: boolean;
  inSequence?: string;
  customFilters?: Array<{
    field: string;
    operator: 'equals' | 'contains' | 'gt' | 'lt' | 'in' | 'not_in';
    value: any;
  }>;
}

export interface LeadSort {
  field: 'createdAt' | 'updatedAt' | 'lastContactedAt' | 'score' | 'email' | 'company';
  direction: 'asc' | 'desc';
}

export interface LeadPagination {
  page: number;
  limit: number;
  total?: number;
  totalPages?: number;
}

export interface LeadListResponse {
  leads: Lead[];
  pagination: LeadPagination;
  filters?: LeadFilter;
  sort?: LeadSort;
}