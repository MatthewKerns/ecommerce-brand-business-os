/**
 * Analytics Storage - Email event storage and retrieval
 *
 * Features:
 * - Store and retrieve email events (opens, clicks, conversions)
 * - Query events with filtering, sorting, pagination
 * - Aggregate metrics calculation
 * - Time-series analytics
 * - Multiple storage backends (Google Sheets, in-memory)
 */

import { google } from 'googleapis';
import type { sheets_v4 } from 'googleapis';
import type {
  EmailEvent,
  EmailEventType,
  EmailEventCreateInput,
  ClickEventInput,
  ConversionEventInput,
  OpenEventInput,
  EmailEventFilter,
  EmailEventSort,
  EmailEventListResponse,
  EmailMetrics,
  SequenceMetrics,
  CampaignMetrics,
  EmailEventData,
  ConversionType,
} from './models';

// ============================================================
// Types
// ============================================================

export interface AnalyticsStorageConfig {
  type: 'google-sheets' | 'memory';
  googleSheets?: {
    spreadsheetId: string;
    sheetName?: string;
    credentials: {
      clientEmail: string;
      privateKey: string;
    };
  };
}

export interface SheetColumn {
  name: string;
  field: string;
  type: 'string' | 'number' | 'boolean' | 'date' | 'json';
}

// ============================================================
// Constants
// ============================================================

const EVENT_COLUMNS: SheetColumn[] = [
  { name: 'ID', field: 'id', type: 'string' },
  { name: 'Type', field: 'type', type: 'string' },
  { name: 'Timestamp', field: 'timestamp', type: 'date' },
  { name: 'Lead ID', field: 'leadId', type: 'string' },
  { name: 'Message ID', field: 'messageId', type: 'string' },
  { name: 'Email Address', field: 'emailAddress', type: 'string' },
  { name: 'Campaign ID', field: 'campaignId', type: 'string' },
  { name: 'Sequence ID', field: 'sequenceId', type: 'string' },
  { name: 'Template ID', field: 'templateId', type: 'string' },
  { name: 'Sequence Step', field: 'sequenceStep', type: 'number' },
  { name: 'Variant ID', field: 'variantId', type: 'string' },
  { name: 'Test ID', field: 'testId', type: 'string' },
  { name: 'Event Data', field: 'eventData', type: 'json' },
  { name: 'User Agent', field: 'userAgent', type: 'string' },
  { name: 'IP Address', field: 'ipAddress', type: 'string' },
  { name: 'Device Type', field: 'deviceType', type: 'string' },
  { name: 'Email Client', field: 'emailClient', type: 'string' },
  { name: 'Operating System', field: 'operatingSystem', type: 'string' },
  { name: 'Country', field: 'country', type: 'string' },
  { name: 'Region', field: 'region', type: 'string' },
  { name: 'City', field: 'city', type: 'string' },
  { name: 'Metadata', field: 'metadata', type: 'json' },
];

// ============================================================
// Helper Functions
// ============================================================

function generateEventId(): string {
  return `evt_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

function parseValue(value: any, type: SheetColumn['type']): any {
  if (!value || value === '') return null;

  switch (type) {
    case 'string':
      return String(value);
    case 'number':
      const num = Number(value);
      return isNaN(num) ? null : num;
    case 'boolean':
      return value === 'true' || value === true;
    case 'date':
      const date = new Date(value);
      return isNaN(date.getTime()) ? null : date;
    case 'json':
      try {
        return typeof value === 'string' ? JSON.parse(value) : value;
      } catch {
        return null;
      }
  }
}

function formatValue(value: any, type: SheetColumn['type']): string {
  if (value === null || value === undefined) return '';

  switch (type) {
    case 'string':
      return String(value);
    case 'number':
      return String(value);
    case 'boolean':
      return value ? 'true' : 'false';
    case 'date':
      return value instanceof Date ? value.toISOString() : '';
    case 'json':
      return JSON.stringify(value);
  }
}

function parseUserAgent(userAgent?: string): {
  deviceType: 'desktop' | 'mobile' | 'tablet' | 'unknown';
  emailClient?: string;
  operatingSystem?: string;
} {
  if (!userAgent) {
    return { deviceType: 'unknown' };
  }

  const ua = userAgent.toLowerCase();

  const deviceType = ua.includes('mobile')
    ? 'mobile'
    : ua.includes('tablet') || ua.includes('ipad')
    ? 'tablet'
    : ua.includes('windows') || ua.includes('mac') || ua.includes('linux')
    ? 'desktop'
    : 'unknown';

  let emailClient: string | undefined;
  if (ua.includes('outlook')) emailClient = 'Outlook';
  else if (ua.includes('gmail')) emailClient = 'Gmail';
  else if (ua.includes('apple mail') || ua.includes('mail.app')) emailClient = 'Apple Mail';
  else if (ua.includes('thunderbird')) emailClient = 'Thunderbird';
  else if (ua.includes('yahoo')) emailClient = 'Yahoo Mail';

  let operatingSystem: string | undefined;
  if (ua.includes('windows')) operatingSystem = 'Windows';
  else if (ua.includes('mac os') || ua.includes('macos')) operatingSystem = 'macOS';
  else if (ua.includes('linux')) operatingSystem = 'Linux';
  else if (ua.includes('android')) operatingSystem = 'Android';
  else if (ua.includes('ios') || ua.includes('iphone') || ua.includes('ipad')) operatingSystem = 'iOS';

  return { deviceType, emailClient, operatingSystem };
}

// ============================================================
// Abstract Storage Interface
// ============================================================

export interface IAnalyticsStorage {
  recordEvent(input: EmailEventCreateInput): Promise<EmailEvent>;
  recordOpen(input: OpenEventInput): Promise<EmailEvent>;
  recordClick(input: ClickEventInput): Promise<EmailEvent>;
  recordConversion(input: ConversionEventInput): Promise<EmailEvent>;
  getEvent(id: string): Promise<EmailEvent | null>;
  listEvents(
    filter?: EmailEventFilter,
    sort?: EmailEventSort,
    page?: number,
    limit?: number
  ): Promise<EmailEventListResponse>;
  getMetrics(filter?: EmailEventFilter): Promise<EmailMetrics>;
  getSequenceMetrics(sequenceId: string, filter?: EmailEventFilter): Promise<SequenceMetrics>;
  getCampaignMetrics(campaignId: string, filter?: EmailEventFilter): Promise<CampaignMetrics>;
}

// ============================================================
// In-Memory Storage Implementation
// ============================================================

export class MemoryAnalyticsStorage implements IAnalyticsStorage {
  private events: Map<string, EmailEvent> = new Map();

  async recordEvent(input: EmailEventCreateInput): Promise<EmailEvent> {
    const { deviceType, emailClient, operatingSystem } = parseUserAgent(input.userAgent);

    const event: EmailEvent = {
      id: generateEventId(),
      type: input.type,
      timestamp: new Date(),
      leadId: input.leadId,
      messageId: input.messageId,
      emailAddress: input.emailAddress,
      campaignId: input.campaignId,
      sequenceId: input.sequenceId,
      templateId: input.templateId,
      sequenceStep: input.sequenceStep,
      variantId: input.variantId,
      testId: input.testId,
      eventData: input.eventData,
      userAgent: input.userAgent,
      ipAddress: input.ipAddress,
      deviceType,
      emailClient,
      operatingSystem,
      metadata: input.metadata,
    };

    this.events.set(event.id, event);
    return event;
  }

  async recordOpen(input: OpenEventInput): Promise<EmailEvent> {
    const existingOpens = Array.from(this.events.values()).filter(
      e => e.type === 'open' && e.leadId === input.leadId && e.messageId === input.messageId
    );

    const isFirstOpen = existingOpens.length === 0;

    return this.recordEvent({
      type: 'open',
      ...input,
      eventData: {
        openData: {
          isFirstOpen,
          openCount: existingOpens.length + 1,
        },
      },
    });
  }

  async recordClick(input: ClickEventInput): Promise<EmailEvent> {
    const existingClicks = Array.from(this.events.values()).filter(
      e =>
        e.type === 'click' &&
        e.leadId === input.leadId &&
        e.messageId === input.messageId &&
        e.eventData?.clickData?.linkId === input.linkId
    );

    const isFirstClick = existingClicks.length === 0;

    return this.recordEvent({
      type: 'click',
      leadId: input.leadId,
      messageId: input.messageId,
      emailAddress: input.emailAddress,
      campaignId: input.campaignId,
      sequenceId: input.sequenceId,
      templateId: input.templateId,
      variantId: input.variantId,
      userAgent: input.userAgent,
      ipAddress: input.ipAddress,
      metadata: input.metadata,
      eventData: {
        clickData: {
          linkId: input.linkId,
          targetUrl: input.targetUrl,
          linkText: input.linkText,
          isFirstClick,
        },
      },
    });
  }

  async recordConversion(input: ConversionEventInput): Promise<EmailEvent> {
    const sentEvent = Array.from(this.events.values()).find(
      e => e.type === 'sent' && e.messageId === input.messageId && e.leadId === input.leadId
    );

    const timeToConversion = sentEvent
      ? new Date().getTime() - sentEvent.timestamp.getTime()
      : undefined;

    return this.recordEvent({
      type: 'conversion',
      leadId: input.leadId,
      messageId: input.messageId,
      emailAddress: input.emailAddress,
      campaignId: input.campaignId,
      sequenceId: input.sequenceId,
      templateId: input.templateId,
      variantId: input.variantId,
      metadata: input.metadata,
      eventData: {
        conversionData: {
          conversionType: input.conversionType,
          conversionValue: input.conversionValue,
          currency: input.currency,
          conversionMetadata: input.conversionMetadata,
          timeToConversion,
        },
      },
    });
  }

  async getEvent(id: string): Promise<EmailEvent | null> {
    return this.events.get(id) || null;
  }

  async listEvents(
    filter?: EmailEventFilter,
    sort?: EmailEventSort,
    page: number = 1,
    limit: number = 100
  ): Promise<EmailEventListResponse> {
    let events = Array.from(this.events.values());

    if (filter) {
      events = this.applyFilters(events, filter);
    }

    if (sort) {
      events = this.applySort(events, sort);
    }

    const total = events.length;
    const totalPages = Math.ceil(total / limit);
    const start = (page - 1) * limit;
    const paginatedEvents = events.slice(start, start + limit);

    return {
      events: paginatedEvents,
      pagination: {
        page,
        limit,
        total,
        totalPages,
      },
      filters: filter,
      sort,
    };
  }

  async getMetrics(filter?: EmailEventFilter): Promise<EmailMetrics> {
    const { events } = await this.listEvents(filter, undefined, 1, Number.MAX_SAFE_INTEGER);
    return this.calculateMetrics(events, filter);
  }

  async getSequenceMetrics(
    sequenceId: string,
    filter?: EmailEventFilter
  ): Promise<SequenceMetrics> {
    const sequenceFilter = { ...filter, sequenceId };
    const baseMetrics = await this.getMetrics(sequenceFilter);

    const stepNumbers = new Set(
      Array.from(this.events.values())
        .filter(e => e.sequenceId === sequenceId && e.sequenceStep !== undefined)
        .map(e => e.sequenceStep!)
    );

    const stepMetrics = await Promise.all(
      Array.from(stepNumbers)
        .sort((a, b) => a - b)
        .map(async step => {
          const stepFilter = { ...sequenceFilter, sequenceStep: step };
          const { events } = await this.listEvents(stepFilter, undefined, 1, Number.MAX_SAFE_INTEGER);
          const metrics = this.calculateMetrics(events, stepFilter);

          const templateId = events.find(e => e.templateId)?.templateId;

          return {
            step,
            templateId,
            ...metrics,
          };
        })
    );

    return {
      sequenceId,
      ...baseMetrics,
      stepMetrics,
    };
  }

  async getCampaignMetrics(
    campaignId: string,
    filter?: EmailEventFilter
  ): Promise<CampaignMetrics> {
    const campaignFilter = { ...filter, campaignId };
    const metrics = await this.getMetrics(campaignFilter);

    return {
      campaignId,
      ...metrics,
    };
  }

  private applyFilters(events: EmailEvent[], filter: EmailEventFilter): EmailEvent[] {
    return events.filter(event => {
      if (filter.type) {
        const types = Array.isArray(filter.type) ? filter.type : [filter.type];
        if (!types.includes(event.type)) return false;
      }

      if (filter.leadId && event.leadId !== filter.leadId) return false;
      if (filter.leadIds && !filter.leadIds.includes(event.leadId)) return false;
      if (filter.messageId && event.messageId !== filter.messageId) return false;
      if (filter.messageIds && !filter.messageIds.includes(event.messageId)) return false;
      if (filter.emailAddress && event.emailAddress !== filter.emailAddress) return false;

      if (filter.campaignId && event.campaignId !== filter.campaignId) return false;
      if (filter.sequenceId && event.sequenceId !== filter.sequenceId) return false;
      if (filter.templateId && event.templateId !== filter.templateId) return false;
      if (filter.variantId && event.variantId !== filter.variantId) return false;
      if (filter.testId && event.testId !== filter.testId) return false;

      if (filter.startDate && event.timestamp < filter.startDate) return false;
      if (filter.endDate && event.timestamp > filter.endDate) return false;
      if (filter.timestampAfter && event.timestamp < filter.timestampAfter) return false;
      if (filter.timestampBefore && event.timestamp > filter.timestampBefore) return false;

      if (filter.deviceType && event.deviceType !== filter.deviceType) return false;
      if (filter.emailClient && event.emailClient !== filter.emailClient) return false;
      if (filter.country && event.country !== filter.country) return false;
      if (filter.region && event.region !== filter.region) return false;

      if (filter.conversionType && event.eventData?.conversionData?.conversionType !== filter.conversionType)
        return false;

      if (
        filter.minConversionValue !== undefined &&
        (event.eventData?.conversionData?.conversionValue || 0) < filter.minConversionValue
      )
        return false;

      if (
        filter.maxConversionValue !== undefined &&
        (event.eventData?.conversionData?.conversionValue || 0) > filter.maxConversionValue
      )
        return false;

      return true;
    });
  }

  private applySort(events: EmailEvent[], sort: EmailEventSort): EmailEvent[] {
    return [...events].sort((a, b) => {
      let aValue: any;
      let bValue: any;

      switch (sort.field) {
        case 'timestamp':
          aValue = a.timestamp.getTime();
          bValue = b.timestamp.getTime();
          break;
        case 'type':
          aValue = a.type;
          bValue = b.type;
          break;
        case 'leadId':
          aValue = a.leadId;
          bValue = b.leadId;
          break;
        case 'messageId':
          aValue = a.messageId;
          bValue = b.messageId;
          break;
        case 'campaignId':
          aValue = a.campaignId || '';
          bValue = b.campaignId || '';
          break;
        case 'sequenceId':
          aValue = a.sequenceId || '';
          bValue = b.sequenceId || '';
          break;
      }

      if (aValue === bValue) return 0;
      const comparison = aValue < bValue ? -1 : 1;
      return sort.direction === 'asc' ? comparison : -comparison;
    });
  }

  private calculateMetrics(events: EmailEvent[], filter?: EmailEventFilter): EmailMetrics {
    const sent = events.filter(e => e.type === 'sent');
    const delivered = events.filter(e => e.type === 'delivered');
    const bounced = events.filter(e => e.type === 'bounce');
    const opened = events.filter(e => e.type === 'open');
    const clicked = events.filter(e => e.type === 'click');
    const converted = events.filter(e => e.type === 'conversion');
    const unsubscribed = events.filter(e => e.type === 'unsubscribe');
    const complaints = events.filter(e => e.type === 'complaint');

    const uniqueOpens = new Set(opened.map(e => `${e.leadId}-${e.messageId}`)).size;
    const uniqueClicks = new Set(clicked.map(e => `${e.leadId}-${e.messageId}`)).size;

    const totalSent = sent.length;
    const totalDelivered = delivered.length;
    const totalBounced = bounced.length;

    const conversionValues = converted
      .map(e => e.eventData?.conversionData?.conversionValue || 0)
      .filter(v => v > 0);

    const conversionTimes = converted
      .map(e => e.eventData?.conversionData?.timeToConversion)
      .filter((t): t is number => t !== undefined);

    const timestamps = events.map(e => e.timestamp);
    const startDate = timestamps.length > 0 ? new Date(Math.min(...timestamps.map(t => t.getTime()))) : new Date();
    const endDate = timestamps.length > 0 ? new Date(Math.max(...timestamps.map(t => t.getTime()))) : new Date();

    return {
      totalSent,
      totalDelivered,
      totalBounced,
      totalOpened: opened.length,
      totalClicked: clicked.length,
      totalConverted: converted.length,
      totalUnsubscribed: unsubscribed.length,
      totalComplaints: complaints.length,
      deliveryRate: totalSent > 0 ? (totalDelivered / totalSent) * 100 : 0,
      openRate: totalDelivered > 0 ? (uniqueOpens / totalDelivered) * 100 : 0,
      clickRate: totalDelivered > 0 ? (uniqueClicks / totalDelivered) * 100 : 0,
      clickToOpenRate: uniqueOpens > 0 ? (uniqueClicks / uniqueOpens) * 100 : 0,
      conversionRate: totalDelivered > 0 ? (converted.length / totalDelivered) * 100 : 0,
      bounceRate: totalSent > 0 ? (totalBounced / totalSent) * 100 : 0,
      unsubscribeRate: totalDelivered > 0 ? (unsubscribed.length / totalDelivered) * 100 : 0,
      complaintRate: totalDelivered > 0 ? (complaints.length / totalDelivered) * 100 : 0,
      uniqueOpens,
      uniqueClicks,
      totalConversionValue: conversionValues.reduce((sum, v) => sum + v, 0),
      averageConversionValue:
        conversionValues.length > 0
          ? conversionValues.reduce((sum, v) => sum + v, 0) / conversionValues.length
          : 0,
      averageTimeToConversion:
        conversionTimes.length > 0
          ? conversionTimes.reduce((sum, t) => sum + t, 0) / conversionTimes.length
          : undefined,
      startDate,
      endDate,
    };
  }
}

// ============================================================
// Google Sheets Storage Implementation
// ============================================================

export class GoogleSheetsAnalyticsStorage implements IAnalyticsStorage {
  private sheets: sheets_v4.Sheets;
  private spreadsheetId: string;
  private sheetName: string;
  private initialized: boolean = false;

  constructor(config: {
    spreadsheetId: string;
    sheetName?: string;
    credentials: {
      clientEmail: string;
      privateKey: string;
    };
  }) {
    const auth = new google.auth.JWT({
      email: config.credentials.clientEmail,
      key: config.credentials.privateKey,
      scopes: ['https://www.googleapis.com/auth/spreadsheets'],
    });

    this.sheets = google.sheets({ version: 'v4', auth });
    this.spreadsheetId = config.spreadsheetId;
    this.sheetName = config.sheetName || 'Email Events';
  }

  async initialize(): Promise<void> {
    if (this.initialized) return;

    const range = `${this.sheetName}!A1:${this.getColumnLetter(EVENT_COLUMNS.length)}1`;

    try {
      const response = await this.sheets.spreadsheets.values.get({
        spreadsheetId: this.spreadsheetId,
        range,
      });

      if (!response.data.values || response.data.values.length === 0) {
        const headers = EVENT_COLUMNS.map(col => col.name);
        await this.sheets.spreadsheets.values.update({
          spreadsheetId: this.spreadsheetId,
          range,
          valueInputOption: 'RAW',
          requestBody: {
            values: [headers],
          },
        });
      }

      this.initialized = true;
    } catch (error: any) {
      if (error.code === 404) {
        throw new Error(`Spreadsheet not found: ${this.spreadsheetId}`);
      }
      throw error;
    }
  }

  async recordEvent(input: EmailEventCreateInput): Promise<EmailEvent> {
    await this.initialize();

    const { deviceType, emailClient, operatingSystem } = parseUserAgent(input.userAgent);

    const event: EmailEvent = {
      id: generateEventId(),
      type: input.type,
      timestamp: new Date(),
      leadId: input.leadId,
      messageId: input.messageId,
      emailAddress: input.emailAddress,
      campaignId: input.campaignId,
      sequenceId: input.sequenceId,
      templateId: input.templateId,
      sequenceStep: input.sequenceStep,
      variantId: input.variantId,
      testId: input.testId,
      eventData: input.eventData,
      userAgent: input.userAgent,
      ipAddress: input.ipAddress,
      deviceType,
      emailClient,
      operatingSystem,
      metadata: input.metadata,
    };

    const row = this.eventToRow(event);

    await this.sheets.spreadsheets.values.append({
      spreadsheetId: this.spreadsheetId,
      range: `${this.sheetName}!A:A`,
      valueInputOption: 'RAW',
      requestBody: {
        values: [row],
      },
    });

    return event;
  }

  async recordOpen(input: OpenEventInput): Promise<EmailEvent> {
    const events = await this.getAllEvents();
    const existingOpens = events.filter(
      e => e.type === 'open' && e.leadId === input.leadId && e.messageId === input.messageId
    );

    const isFirstOpen = existingOpens.length === 0;

    return this.recordEvent({
      type: 'open',
      ...input,
      eventData: {
        openData: {
          isFirstOpen,
          openCount: existingOpens.length + 1,
        },
      },
    });
  }

  async recordClick(input: ClickEventInput): Promise<EmailEvent> {
    const events = await this.getAllEvents();
    const existingClicks = events.filter(
      e =>
        e.type === 'click' &&
        e.leadId === input.leadId &&
        e.messageId === input.messageId &&
        e.eventData?.clickData?.linkId === input.linkId
    );

    const isFirstClick = existingClicks.length === 0;

    return this.recordEvent({
      type: 'click',
      leadId: input.leadId,
      messageId: input.messageId,
      emailAddress: input.emailAddress,
      campaignId: input.campaignId,
      sequenceId: input.sequenceId,
      templateId: input.templateId,
      variantId: input.variantId,
      userAgent: input.userAgent,
      ipAddress: input.ipAddress,
      metadata: input.metadata,
      eventData: {
        clickData: {
          linkId: input.linkId,
          targetUrl: input.targetUrl,
          linkText: input.linkText,
          isFirstClick,
        },
      },
    });
  }

  async recordConversion(input: ConversionEventInput): Promise<EmailEvent> {
    const events = await this.getAllEvents();
    const sentEvent = events.find(
      e => e.type === 'sent' && e.messageId === input.messageId && e.leadId === input.leadId
    );

    const timeToConversion = sentEvent
      ? new Date().getTime() - sentEvent.timestamp.getTime()
      : undefined;

    return this.recordEvent({
      type: 'conversion',
      leadId: input.leadId,
      messageId: input.messageId,
      emailAddress: input.emailAddress,
      campaignId: input.campaignId,
      sequenceId: input.sequenceId,
      templateId: input.templateId,
      variantId: input.variantId,
      metadata: input.metadata,
      eventData: {
        conversionData: {
          conversionType: input.conversionType,
          conversionValue: input.conversionValue,
          currency: input.currency,
          conversionMetadata: input.conversionMetadata,
          timeToConversion,
        },
      },
    });
  }

  async getEvent(id: string): Promise<EmailEvent | null> {
    const events = await this.getAllEvents();
    return events.find(e => e.id === id) || null;
  }

  async listEvents(
    filter?: EmailEventFilter,
    sort?: EmailEventSort,
    page: number = 1,
    limit: number = 100
  ): Promise<EmailEventListResponse> {
    const memoryStorage = new MemoryAnalyticsStorage();
    const allEvents = await this.getAllEvents();

    for (const event of allEvents) {
      await memoryStorage.recordEvent({
        type: event.type,
        leadId: event.leadId,
        messageId: event.messageId,
        emailAddress: event.emailAddress,
        campaignId: event.campaignId,
        sequenceId: event.sequenceId,
        templateId: event.templateId,
        sequenceStep: event.sequenceStep,
        variantId: event.variantId,
        testId: event.testId,
        eventData: event.eventData,
        userAgent: event.userAgent,
        ipAddress: event.ipAddress,
        metadata: event.metadata,
      });
    }

    return memoryStorage.listEvents(filter, sort, page, limit);
  }

  async getMetrics(filter?: EmailEventFilter): Promise<EmailMetrics> {
    const { events } = await this.listEvents(filter, undefined, 1, Number.MAX_SAFE_INTEGER);
    const memoryStorage = new MemoryAnalyticsStorage();
    return memoryStorage['calculateMetrics'](events, filter);
  }

  async getSequenceMetrics(
    sequenceId: string,
    filter?: EmailEventFilter
  ): Promise<SequenceMetrics> {
    const memoryStorage = new MemoryAnalyticsStorage();
    const allEvents = await this.getAllEvents();

    for (const event of allEvents) {
      await memoryStorage.recordEvent({
        type: event.type,
        leadId: event.leadId,
        messageId: event.messageId,
        emailAddress: event.emailAddress,
        campaignId: event.campaignId,
        sequenceId: event.sequenceId,
        templateId: event.templateId,
        sequenceStep: event.sequenceStep,
        variantId: event.variantId,
        testId: event.testId,
        eventData: event.eventData,
        userAgent: event.userAgent,
        ipAddress: event.ipAddress,
        metadata: event.metadata,
      });
    }

    return memoryStorage.getSequenceMetrics(sequenceId, filter);
  }

  async getCampaignMetrics(
    campaignId: string,
    filter?: EmailEventFilter
  ): Promise<CampaignMetrics> {
    const memoryStorage = new MemoryAnalyticsStorage();
    const allEvents = await this.getAllEvents();

    for (const event of allEvents) {
      await memoryStorage.recordEvent({
        type: event.type,
        leadId: event.leadId,
        messageId: event.messageId,
        emailAddress: event.emailAddress,
        campaignId: event.campaignId,
        sequenceId: event.sequenceId,
        templateId: event.templateId,
        sequenceStep: event.sequenceStep,
        variantId: event.variantId,
        testId: event.testId,
        eventData: event.eventData,
        userAgent: event.userAgent,
        ipAddress: event.ipAddress,
        metadata: event.metadata,
      });
    }

    return memoryStorage.getCampaignMetrics(campaignId, filter);
  }

  private async getAllEvents(): Promise<EmailEvent[]> {
    await this.initialize();

    const response = await this.sheets.spreadsheets.values.get({
      spreadsheetId: this.spreadsheetId,
      range: `${this.sheetName}!A2:${this.getColumnLetter(EVENT_COLUMNS.length)}`,
    });

    const rows = response.data.values || [];
    return rows.map(row => this.rowToEvent(row));
  }

  private eventToRow(event: EmailEvent): string[] {
    return EVENT_COLUMNS.map(col => {
      const value = (event as any)[col.field];
      return formatValue(value, col.type);
    });
  }

  private rowToEvent(row: string[]): EmailEvent {
    const event: any = {};

    EVENT_COLUMNS.forEach((col, index) => {
      const value = parseValue(row[index], col.type);
      event[col.field] = value;
    });

    return event as EmailEvent;
  }

  private getColumnLetter(columnNumber: number): string {
    let letter = '';
    while (columnNumber > 0) {
      const remainder = (columnNumber - 1) % 26;
      letter = String.fromCharCode(65 + remainder) + letter;
      columnNumber = Math.floor((columnNumber - 1) / 26);
    }
    return letter;
  }
}

// ============================================================
// Storage Factory
// ============================================================

export function createAnalyticsStorage(config: AnalyticsStorageConfig): IAnalyticsStorage {
  switch (config.type) {
    case 'google-sheets':
      if (!config.googleSheets) {
        throw new Error('Google Sheets configuration required for google-sheets storage type');
      }
      return new GoogleSheetsAnalyticsStorage(config.googleSheets);
    case 'memory':
      return new MemoryAnalyticsStorage();
    default:
      throw new Error(`Unknown storage type: ${config.type}`);
  }
}

// ============================================================
// Singleton Instance
// ============================================================

let defaultStorage: IAnalyticsStorage | null = null;

export function getAnalyticsStorage(config?: AnalyticsStorageConfig): IAnalyticsStorage {
  if (!defaultStorage) {
    if (!config) {
      defaultStorage = new MemoryAnalyticsStorage();
    } else {
      defaultStorage = createAnalyticsStorage(config);
    }
  }
  return defaultStorage;
}

export function resetAnalyticsStorage(): void {
  defaultStorage = null;
}
