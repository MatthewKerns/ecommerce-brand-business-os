/**
 * Google Sheets Storage - Lead storage adapter using Google Sheets
 *
 * Features:
 * - Full CRUD operations for leads
 * - Bidirectional sync with sheets
 * - Batch operations for performance
 * - Custom field mapping
 * - Data validation
 */

import { google } from 'googleapis';
import type { sheets_v4 } from 'googleapis';
import type {
  Lead,
  LeadCreateInput,
  LeadUpdateInput,
  LeadFilter,
  LeadSort,
  LeadListResponse,
  LeadCustomField,
} from '@/types/lead';

// ============================================================
// Types
// ============================================================

export interface GoogleSheetsConfig {
  spreadsheetId: string;
  sheetName?: string;
  credentials: {
    clientEmail: string;
    privateKey: string;
  };
}

export interface SheetColumn {
  name: string;
  field: string;
  type: 'string' | 'number' | 'boolean' | 'date' | 'json';
  required?: boolean;
}

// ============================================================
// Constants
// ============================================================

const DEFAULT_COLUMNS: SheetColumn[] = [
  { name: 'ID', field: 'id', type: 'string', required: true },
  { name: 'Email', field: 'email', type: 'string', required: true },
  { name: 'Status', field: 'status', type: 'string', required: true },
  { name: 'Source', field: 'source', type: 'string', required: true },
  { name: 'First Name', field: 'firstName', type: 'string' },
  { name: 'Last Name', field: 'lastName', type: 'string' },
  { name: 'Company', field: 'company', type: 'string' },
  { name: 'Job Title', field: 'jobTitle', type: 'string' },
  { name: 'Phone', field: 'phone', type: 'string' },
  { name: 'Website', field: 'website', type: 'string' },
  { name: 'Tags', field: 'tags', type: 'json' },
  { name: 'Segments', field: 'segments', type: 'json' },
  { name: 'Score', field: 'score', type: 'number' },
  { name: 'Priority', field: 'priority', type: 'string' },
  { name: 'Current Sequence', field: 'currentSequence', type: 'string' },
  { name: 'Sequence Step', field: 'sequenceStep', type: 'number' },
  { name: 'Custom Fields', field: 'customFields', type: 'json' },
  { name: 'Consent Given', field: 'consentGiven', type: 'boolean' },
  { name: 'Consent Date', field: 'consentDate', type: 'date' },
  { name: 'Notes', field: 'notes', type: 'string' },
  { name: 'Created At', field: 'createdAt', type: 'date', required: true },
  { name: 'Updated At', field: 'updatedAt', type: 'date', required: true },
  { name: 'Last Contacted', field: 'lastContactedAt', type: 'date' },
  { name: 'Emails Sent', field: 'engagement.emailsSent', type: 'number' },
  { name: 'Emails Opened', field: 'engagement.emailsOpened', type: 'number' },
  { name: 'Emails Clicked', field: 'engagement.emailsClicked', type: 'number' },
  { name: 'Emails Replied', field: 'engagement.emailsReplied', type: 'number' },
];

// ============================================================
// Helper Functions
// ============================================================

function generateId(): string {
  return `lead_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
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

function getNestedValue(obj: any, path: string): any {
  return path.split('.').reduce((current, key) => current?.[key], obj);
}

function setNestedValue(obj: any, path: string, value: any): void {
  const keys = path.split('.');
  const lastKey = keys.pop()!;
  const target = keys.reduce((current, key) => {
    if (!current[key]) current[key] = {};
    return current[key];
  }, obj);
  target[lastKey] = value;
}

// ============================================================
// Google Sheets Storage Class
// ============================================================

export class GoogleSheetsStorage {
  private sheets: sheets_v4.Sheets;
  private config: GoogleSheetsConfig;
  private columns: SheetColumn[];
  private initialized: boolean = false;

  constructor(config: GoogleSheetsConfig, customColumns?: SheetColumn[]) {
    // Initialize Google Sheets API
    const auth = new google.auth.JWT({
      email: config.credentials.clientEmail,
      key: config.credentials.privateKey,
      scopes: ['https://www.googleapis.com/auth/spreadsheets'],
    });

    this.sheets = google.sheets({ version: 'v4', auth });
    this.config = config;
    this.columns = customColumns || DEFAULT_COLUMNS;
  }

  /**
   * Initialize the sheet with headers if needed
   */
  async initialize(): Promise<void> {
    if (this.initialized) return;

    const sheetName = this.config.sheetName || 'Leads';
    const range = `${sheetName}!A1:${this.getColumnLetter(this.columns.length)}1`;

    try {
      // Check if headers exist
      const response = await this.sheets.spreadsheets.values.get({
        spreadsheetId: this.config.spreadsheetId,
        range,
      });

      if (!response.data.values || response.data.values.length === 0) {
        // Create headers
        const headers = this.columns.map(col => col.name);
        await this.sheets.spreadsheets.values.update({
          spreadsheetId: this.config.spreadsheetId,
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
        throw new Error(`Spreadsheet not found: ${this.config.spreadsheetId}`);
      }
      throw error;
    }
  }

  /**
   * Create a new lead
   */
  async create(input: LeadCreateInput): Promise<Lead> {
    await this.initialize();

    const lead: Lead = {
      id: generateId(),
      email: input.email,
      status: 'new',
      source: input.source,
      firstName: input.firstName,
      lastName: input.lastName,
      company: input.company,
      tags: input.tags || [],
      segments: [],
      customFields: input.customFields || [],
      consentGiven: input.consentGiven || false,
      consentSource: input.consentSource,
      engagement: {
        emailsSent: 0,
        emailsOpened: 0,
        emailsClicked: 0,
        emailsReplied: 0,
      },
      createdAt: new Date(),
      updatedAt: new Date(),
    };

    // Convert to row values
    const row = this.leadToRow(lead);

    // Append to sheet
    const sheetName = this.config.sheetName || 'Leads';
    await this.sheets.spreadsheets.values.append({
      spreadsheetId: this.config.spreadsheetId,
      range: `${sheetName}!A:A`,
      valueInputOption: 'RAW',
      requestBody: {
        values: [row],
      },
    });

    return lead;
  }

  /**
   * Get lead by ID
   */
  async getById(id: string): Promise<Lead | null> {
    await this.initialize();

    const leads = await this.getAllLeads();
    return leads.find(lead => lead.id === id) || null;
  }

  /**
   * Get lead by email
   */
  async getByEmail(email: string): Promise<Lead | null> {
    await this.initialize();

    const leads = await this.getAllLeads();
    return leads.find(lead => lead.email.toLowerCase() === email.toLowerCase()) || null;
  }

  /**
   * Update a lead
   */
  async update(id: string, input: LeadUpdateInput): Promise<Lead | null> {
    await this.initialize();

    const { leads, rowIndex } = await this.getAllLeadsWithIndex();
    const leadIndex = leads.findIndex(lead => lead.id === id);

    if (leadIndex === -1) return null;

    const lead = leads[leadIndex];
    const updatedLead: Lead = {
      ...lead,
      ...input,
      updatedAt: new Date(),
    };

    // Update the specific row
    const row = this.leadToRow(updatedLead);
    const sheetName = this.config.sheetName || 'Leads';
    const range = `${sheetName}!A${rowIndex[leadIndex]}:${this.getColumnLetter(this.columns.length)}${rowIndex[leadIndex]}`;

    await this.sheets.spreadsheets.values.update({
      spreadsheetId: this.config.spreadsheetId,
      range,
      valueInputOption: 'RAW',
      requestBody: {
        values: [row],
      },
    });

    return updatedLead;
  }

  /**
   * Delete a lead
   */
  async delete(id: string): Promise<boolean> {
    await this.initialize();

    const { leads, rowIndex } = await this.getAllLeadsWithIndex();
    const leadIndex = leads.findIndex(lead => lead.id === id);

    if (leadIndex === -1) return false;

    // Delete the row
    const sheetName = this.config.sheetName || 'Leads';
    const sheetId = await this.getSheetId(sheetName);

    await this.sheets.spreadsheets.batchUpdate({
      spreadsheetId: this.config.spreadsheetId,
      requestBody: {
        requests: [
          {
            deleteDimension: {
              range: {
                sheetId,
                dimension: 'ROWS',
                startIndex: rowIndex[leadIndex] - 1,
                endIndex: rowIndex[leadIndex],
              },
            },
          },
        ],
      },
    });

    return true;
  }

  /**
   * List leads with filtering, sorting, and pagination
   */
  async list(
    filter?: LeadFilter,
    sort?: LeadSort,
    page: number = 1,
    limit: number = 100
  ): Promise<LeadListResponse> {
    await this.initialize();

    let leads = await this.getAllLeads();

    // Apply filters
    if (filter) {
      leads = this.applyFilters(leads, filter);
    }

    // Apply sorting
    if (sort) {
      leads = this.applySort(leads, sort);
    }

    // Apply pagination
    const total = leads.length;
    const totalPages = Math.ceil(total / limit);
    const start = (page - 1) * limit;
    const paginatedLeads = leads.slice(start, start + limit);

    return {
      leads: paginatedLeads,
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

  /**
   * Batch update multiple leads
   */
  async batchUpdate(updates: Array<{ id: string; data: LeadUpdateInput }>): Promise<Lead[]> {
    await this.initialize();

    const updatedLeads: Lead[] = [];

    for (const { id, data } of updates) {
      const updated = await this.update(id, data);
      if (updated) {
        updatedLeads.push(updated);
      }
    }

    return updatedLeads;
  }

  // ============================================================
  // Private Methods
  // ============================================================

  private async getAllLeads(): Promise<Lead[]> {
    const sheetName = this.config.sheetName || 'Leads';
    const response = await this.sheets.spreadsheets.values.get({
      spreadsheetId: this.config.spreadsheetId,
      range: `${sheetName}!A2:${this.getColumnLetter(this.columns.length)}`,
    });

    const rows = response.data.values || [];
    return rows.map(row => this.rowToLead(row));
  }

  private async getAllLeadsWithIndex(): Promise<{ leads: Lead[]; rowIndex: number[] }> {
    const sheetName = this.config.sheetName || 'Leads';
    const response = await this.sheets.spreadsheets.values.get({
      spreadsheetId: this.config.spreadsheetId,
      range: `${sheetName}!A2:${this.getColumnLetter(this.columns.length)}`,
    });

    const rows = response.data.values || [];
    const leads = rows.map(row => this.rowToLead(row));
    const rowIndex = rows.map((_, index) => index + 2); // +2 for header and 0-based index

    return { leads, rowIndex };
  }

  private leadToRow(lead: Lead): string[] {
    return this.columns.map(col => {
      const value = getNestedValue(lead, col.field);
      return formatValue(value, col.type);
    });
  }

  private rowToLead(row: string[]): Lead {
    const lead: any = {
      engagement: {},
    };

    this.columns.forEach((col, index) => {
      const value = parseValue(row[index], col.type);
      setNestedValue(lead, col.field, value);
    });

    return lead as Lead;
  }

  private applyFilters(leads: Lead[], filter: LeadFilter): Lead[] {
    return leads.filter(lead => {
      if (filter.status) {
        const statuses = Array.isArray(filter.status) ? filter.status : [filter.status];
        if (!statuses.includes(lead.status)) return false;
      }

      if (filter.source) {
        const sources = Array.isArray(filter.source) ? filter.source : [filter.source];
        if (!sources.includes(lead.source)) return false;
      }

      if (filter.tags && filter.tags.length > 0) {
        if (!filter.tags.some(tag => lead.tags.includes(tag))) return false;
      }

      if (filter.priority && lead.priority !== filter.priority) return false;

      if (filter.createdAfter && lead.createdAt < filter.createdAfter) return false;
      if (filter.createdBefore && lead.createdAt > filter.createdBefore) return false;

      return true;
    });
  }

  private applySort(leads: Lead[], sort: LeadSort): Lead[] {
    return [...leads].sort((a, b) => {
      const aValue = getNestedValue(a, sort.field);
      const bValue = getNestedValue(b, sort.field);

      if (aValue === bValue) return 0;
      if (aValue === null || aValue === undefined) return 1;
      if (bValue === null || bValue === undefined) return -1;

      const comparison = aValue < bValue ? -1 : 1;
      return sort.direction === 'asc' ? comparison : -comparison;
    });
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

  private async getSheetId(sheetName: string): Promise<number> {
    const response = await this.sheets.spreadsheets.get({
      spreadsheetId: this.config.spreadsheetId,
    });

    const sheet = response.data.sheets?.find(
      s => s.properties?.title === sheetName
    );

    if (!sheet?.properties?.sheetId) {
      throw new Error(`Sheet not found: ${sheetName}`);
    }

    return sheet.properties.sheetId;
  }
}