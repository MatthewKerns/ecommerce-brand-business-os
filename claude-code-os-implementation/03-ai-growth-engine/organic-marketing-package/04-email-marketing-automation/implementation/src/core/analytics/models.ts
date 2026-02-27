/**
 * Analytics Data Models - Email event tracking data structures
 *
 * Defines types for storing and querying email events (opens, clicks, conversions)
 * with support for sequences, campaigns, and A/B testing.
 */

// ============================================================
// Event Types
// ============================================================

export type EmailEventType =
  | 'sent'          // Email was sent
  | 'delivered'     // Email was delivered successfully
  | 'open'          // Email was opened
  | 'click'         // Link in email was clicked
  | 'conversion'    // Conversion/goal completed
  | 'bounce'        // Email bounced
  | 'complaint'     // Spam complaint
  | 'unsubscribe';  // User unsubscribed

export type ConversionType =
  | 'purchase'      // Made a purchase
  | 'signup'        // Signed up for something
  | 'download'      // Downloaded resource
  | 'booking'       // Booked appointment/call
  | 'form_submit'   // Submitted form
  | 'custom';       // Custom conversion

export type BounceType =
  | 'hard'          // Permanent delivery failure
  | 'soft'          // Temporary delivery failure
  | 'block';        // Blocked by recipient's server

// ============================================================
// Core Event Interface
// ============================================================

export interface EmailEvent {
  // Event identification
  id: string;
  type: EmailEventType;
  timestamp: Date;

  // Email tracking
  leadId: string;
  messageId: string;
  emailAddress: string;

  // Campaign/Sequence context
  campaignId?: string;
  sequenceId?: string;
  templateId?: string;
  sequenceStep?: number;

  // A/B Testing context
  variantId?: string;
  testId?: string;

  // Event-specific data
  eventData?: EmailEventData;

  // Device/Client information
  userAgent?: string;
  ipAddress?: string;
  deviceType?: 'desktop' | 'mobile' | 'tablet' | 'unknown';
  emailClient?: string;
  operatingSystem?: string;

  // Location
  country?: string;
  region?: string;
  city?: string;

  // Metadata
  metadata?: Record<string, any>;
}

// ============================================================
// Event-Specific Data Types
// ============================================================

export interface EmailEventData {
  // Click event data
  clickData?: ClickEventData;

  // Conversion event data
  conversionData?: ConversionEventData;

  // Bounce event data
  bounceData?: BounceEventData;

  // Open event data
  openData?: OpenEventData;
}

export interface ClickEventData {
  linkId: string;
  targetUrl: string;
  linkText?: string;
  linkPosition?: number;
  isFirstClick?: boolean;
}

export interface ConversionEventData {
  conversionType: ConversionType;
  conversionValue?: number;
  currency?: string;
  conversionMetadata?: Record<string, any>;
  timeToConversion?: number; // milliseconds from email send to conversion
}

export interface BounceEventData {
  bounceType: BounceType;
  bounceReason?: string;
  diagnosticCode?: string;
}

export interface OpenEventData {
  isFirstOpen?: boolean;
  openCount?: number;
}

// ============================================================
// Event Creation Inputs
// ============================================================

export interface EmailEventCreateInput {
  type: EmailEventType;
  leadId: string;
  messageId: string;
  emailAddress: string;
  campaignId?: string;
  sequenceId?: string;
  templateId?: string;
  sequenceStep?: number;
  variantId?: string;
  testId?: string;
  eventData?: EmailEventData;
  userAgent?: string;
  ipAddress?: string;
  metadata?: Record<string, any>;
}

export interface ClickEventInput {
  leadId: string;
  messageId: string;
  emailAddress: string;
  linkId: string;
  targetUrl: string;
  linkText?: string;
  campaignId?: string;
  sequenceId?: string;
  templateId?: string;
  variantId?: string;
  userAgent?: string;
  ipAddress?: string;
  metadata?: Record<string, any>;
}

export interface ConversionEventInput {
  leadId: string;
  messageId: string;
  emailAddress: string;
  conversionType: ConversionType;
  conversionValue?: number;
  currency?: string;
  campaignId?: string;
  sequenceId?: string;
  templateId?: string;
  variantId?: string;
  conversionMetadata?: Record<string, any>;
  metadata?: Record<string, any>;
}

export interface OpenEventInput {
  leadId: string;
  messageId: string;
  emailAddress: string;
  campaignId?: string;
  sequenceId?: string;
  templateId?: string;
  variantId?: string;
  userAgent?: string;
  ipAddress?: string;
  metadata?: Record<string, any>;
}

// ============================================================
// Event Query/Filter Types
// ============================================================

export interface EmailEventFilter {
  // Event filters
  type?: EmailEventType | EmailEventType[];
  leadId?: string;
  leadIds?: string[];
  messageId?: string;
  messageIds?: string[];
  emailAddress?: string;

  // Context filters
  campaignId?: string;
  sequenceId?: string;
  templateId?: string;
  variantId?: string;
  testId?: string;

  // Time filters
  startDate?: Date;
  endDate?: Date;
  timestampAfter?: Date;
  timestampBefore?: Date;

  // Device filters
  deviceType?: 'desktop' | 'mobile' | 'tablet' | 'unknown';
  emailClient?: string;

  // Location filters
  country?: string;
  region?: string;

  // Conversion filters (for conversion events)
  conversionType?: ConversionType;
  minConversionValue?: number;
  maxConversionValue?: number;
}

export interface EmailEventSort {
  field: 'timestamp' | 'type' | 'leadId' | 'messageId' | 'campaignId' | 'sequenceId';
  direction: 'asc' | 'desc';
}

export interface EmailEventPagination {
  page: number;
  limit: number;
  total?: number;
  totalPages?: number;
}

export interface EmailEventListResponse {
  events: EmailEvent[];
  pagination: EmailEventPagination;
  filters?: EmailEventFilter;
  sort?: EmailEventSort;
}

// ============================================================
// Aggregated Metrics Types
// ============================================================

export interface EmailMetrics {
  // Volume metrics
  totalSent: number;
  totalDelivered: number;
  totalBounced: number;
  totalOpened: number;
  totalClicked: number;
  totalConverted: number;
  totalUnsubscribed: number;
  totalComplaints: number;

  // Rate metrics (percentages)
  deliveryRate: number;      // delivered / sent
  openRate: number;           // unique opens / delivered
  clickRate: number;          // unique clicks / delivered
  clickToOpenRate: number;    // unique clicks / unique opens
  conversionRate: number;     // conversions / delivered
  bounceRate: number;         // bounced / sent
  unsubscribeRate: number;    // unsubscribed / delivered
  complaintRate: number;      // complaints / delivered

  // Unique counts
  uniqueOpens: number;
  uniqueClicks: number;

  // Conversion metrics
  totalConversionValue: number;
  averageConversionValue: number;
  averageTimeToConversion?: number; // milliseconds

  // Time period
  startDate: Date;
  endDate: Date;
}

export interface SequenceMetrics extends EmailMetrics {
  sequenceId: string;
  sequenceName?: string;
  stepMetrics: StepMetrics[];
}

export interface StepMetrics extends EmailMetrics {
  step: number;
  templateId?: string;
  templateName?: string;
}

export interface CampaignMetrics extends EmailMetrics {
  campaignId: string;
  campaignName?: string;
}

export interface VariantMetrics extends EmailMetrics {
  variantId: string;
  variantName?: string;
  testId?: string;
  trafficPercentage?: number;
}

// ============================================================
// Time-Series Analytics Types
// ============================================================

export type TimeInterval = 'hour' | 'day' | 'week' | 'month';

export interface TimeSeriesDataPoint {
  timestamp: Date;
  sent: number;
  delivered: number;
  opened: number;
  clicked: number;
  converted: number;
  bounced: number;
  openRate: number;
  clickRate: number;
  conversionRate: number;
}

export interface TimeSeriesMetrics {
  interval: TimeInterval;
  dataPoints: TimeSeriesDataPoint[];
  summary: EmailMetrics;
}

// ============================================================
// Funnel Analytics Types
// ============================================================

export interface FunnelStep {
  name: string;
  eventType: EmailEventType;
  count: number;
  percentage: number;
  dropoff?: number;
  dropoffPercentage?: number;
}

export interface EmailFunnel {
  steps: FunnelStep[];
  totalEntered: number;
  totalCompleted: number;
  completionRate: number;
  averageTimeToComplete?: number; // milliseconds
}

// ============================================================
// Cohort Analysis Types
// ============================================================

export interface CohortMetrics {
  cohortDate: Date;
  cohortSize: number;
  metrics: {
    day0?: EmailMetrics;
    day1?: EmailMetrics;
    day3?: EmailMetrics;
    day7?: EmailMetrics;
    day14?: EmailMetrics;
    day30?: EmailMetrics;
  };
}

// ============================================================
// Helper Types
// ============================================================

export interface EmailEventCount {
  type: EmailEventType;
  count: number;
}

export interface TopLink {
  linkId: string;
  targetUrl: string;
  clicks: number;
  uniqueClicks: number;
  clickRate: number;
}

export interface DeviceBreakdown {
  deviceType: 'desktop' | 'mobile' | 'tablet' | 'unknown';
  count: number;
  percentage: number;
  openRate: number;
  clickRate: number;
  conversionRate: number;
}

export interface LocationBreakdown {
  country: string;
  count: number;
  percentage: number;
  openRate: number;
  clickRate: number;
  conversionRate: number;
}
