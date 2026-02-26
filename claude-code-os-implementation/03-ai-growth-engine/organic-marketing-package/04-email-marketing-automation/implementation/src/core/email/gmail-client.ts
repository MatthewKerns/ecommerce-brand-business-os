/**
 * Gmail Client - Core email sending functionality via Gmail API
 *
 * Features:
 * - OAuth2 authentication with refresh tokens
 * - MIME message building with proper encoding
 * - Template variable substitution
 * - Exponential backoff retry logic
 * - Thread management for replies
 */

import { google } from 'googleapis';
import type { gmail_v1 } from 'googleapis';

// ============================================================
// Types
// ============================================================

export interface GmailConfig {
  clientId: string;
  clientSecret: string;
  refreshToken: string;
  redirectUri: string;
  senderEmail: string;
  senderName?: string;
}

export interface SendEmailRequest {
  to: string | string[];
  subject: string;
  body: string;
  cc?: string | string[];
  bcc?: string | string[];
  variables?: Record<string, string>;
  replyTo?: string;
  threading?: {
    threadId?: string;
    messageId?: string;
    references?: string;
  };
  attachments?: Array<{
    filename: string;
    content: Buffer;
    contentType: string;
  }>;
}

export interface SendEmailResponse {
  messageId: string;
  threadId: string;
  status: 'sent' | 'failed';
  timestamp: Date;
}

export interface RetryConfig {
  maxRetries?: number;
  initialDelay?: number;
  backoffMultiplier?: number;
  maxDelay?: number;
}

// ============================================================
// Constants
// ============================================================

const DEFAULT_RETRY_CONFIG: Required<RetryConfig> = {
  maxRetries: 3,
  initialDelay: 1000,
  backoffMultiplier: 2,
  maxDelay: 30000,
};

// ============================================================
// Helper Functions
// ============================================================

/**
 * Convert Buffer to base64url format required by Gmail API
 */
function toBase64Url(buffer: Buffer): string {
  return buffer
    .toString('base64')
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=+$/, '');
}

/**
 * Sleep for specified milliseconds
 */
function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Substitute template variables in text
 */
function substituteVariables(
  text: string,
  variables: Record<string, string>
): string {
  let result = text;
  for (const [key, value] of Object.entries(variables)) {
    const pattern = new RegExp(`{{\\s*${key}\\s*}}`, 'gi');
    result = result.replace(pattern, value);
  }
  return result;
}

/**
 * Build MIME message for email
 */
function buildMimeMessage(
  from: string,
  to: string,
  subject: string,
  body: string,
  options?: {
    cc?: string;
    bcc?: string;
    replyTo?: string;
    threading?: SendEmailRequest['threading'];
    attachments?: SendEmailRequest['attachments'];
  }
): Buffer {
  const boundary = `----=_Part_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  const lines: string[] = [];

  // Headers
  lines.push(`From: ${from}`);
  lines.push(`To: ${to}`);
  if (options?.cc) lines.push(`Cc: ${options.cc}`);
  if (options?.bcc) lines.push(`Bcc: ${options.bcc}`);
  if (options?.replyTo) lines.push(`Reply-To: ${options.replyTo}`);
  lines.push(`Subject: ${subject}`);
  lines.push('MIME-Version: 1.0');

  // Threading headers
  if (options?.threading?.messageId) {
    lines.push(`In-Reply-To: ${options.threading.messageId}`);
  }
  if (options?.threading?.references) {
    lines.push(`References: ${options.threading.references}`);
  }

  // Content type
  if (options?.attachments && options.attachments.length > 0) {
    lines.push(`Content-Type: multipart/mixed; boundary="${boundary}"`);
    lines.push('');

    // Text part
    lines.push(`--${boundary}`);
    lines.push('Content-Type: text/plain; charset="UTF-8"');
    lines.push('Content-Transfer-Encoding: base64');
    lines.push('');
    lines.push(Buffer.from(body, 'utf-8').toString('base64'));

    // Attachments
    for (const attachment of options.attachments) {
      lines.push(`--${boundary}`);
      lines.push(`Content-Type: ${attachment.contentType}; name="${attachment.filename}"`);
      lines.push('Content-Transfer-Encoding: base64');
      lines.push(`Content-Disposition: attachment; filename="${attachment.filename}"`);
      lines.push('');
      lines.push(attachment.content.toString('base64'));
    }

    lines.push(`--${boundary}--`);
  } else {
    lines.push('Content-Type: text/plain; charset="UTF-8"');
    lines.push('');
    lines.push(body);
  }

  return Buffer.from(lines.join('\r\n'), 'utf-8');
}

// ============================================================
// Gmail Client Class
// ============================================================

export class GmailClient {
  private readonly gmail: gmail_v1.Gmail;
  private readonly config: GmailConfig;
  private readonly retryConfig: Required<RetryConfig>;

  constructor(config: GmailConfig, retryConfig: RetryConfig = {}) {
    const oauth2Client = new google.auth.OAuth2(
      config.clientId,
      config.clientSecret,
      config.redirectUri
    );
    oauth2Client.setCredentials({ refresh_token: config.refreshToken });

    this.gmail = google.gmail({ version: 'v1', auth: oauth2Client });
    this.config = config;
    this.retryConfig = { ...DEFAULT_RETRY_CONFIG, ...retryConfig };
  }

  /**
   * Send an email with automatic retries
   */
  async sendEmail(request: SendEmailRequest): Promise<SendEmailResponse> {
    // Prepare recipients
    const to = Array.isArray(request.to) ? request.to.join(', ') : request.to;
    const cc = request.cc
      ? Array.isArray(request.cc)
        ? request.cc.join(', ')
        : request.cc
      : undefined;
    const bcc = request.bcc
      ? Array.isArray(request.bcc)
        ? request.bcc.join(', ')
        : request.bcc
      : undefined;

    // Apply variable substitution
    let subject = request.subject;
    let body = request.body;
    if (request.variables) {
      subject = substituteVariables(subject, request.variables);
      body = substituteVariables(body, request.variables);
    }

    // Build sender
    const from = this.config.senderName
      ? `${this.config.senderName} <${this.config.senderEmail}>`
      : this.config.senderEmail;

    // Build MIME message
    const mimeMessage = buildMimeMessage(from, to, subject, body, {
      cc,
      bcc,
      replyTo: request.replyTo,
      threading: request.threading,
      attachments: request.attachments,
    });

    // Encode for Gmail API
    const encodedMessage = toBase64Url(mimeMessage);

    // Send with retries
    let lastError: Error | undefined;
    for (let attempt = 0; attempt <= this.retryConfig.maxRetries; attempt++) {
      try {
        const response = await this.gmail.users.messages.send({
          userId: 'me',
          requestBody: {
            raw: encodedMessage,
            threadId: request.threading?.threadId,
          },
        });

        if (!response.data.id || !response.data.threadId) {
          throw new Error('Invalid response from Gmail API');
        }

        return {
          messageId: response.data.id,
          threadId: response.data.threadId,
          status: 'sent',
          timestamp: new Date(),
        };
      } catch (error: any) {
        lastError = error;

        // Check if retryable
        const status = error.response?.status || error.status;
        const isRetryable = status === 429 || (status >= 500 && status < 600);

        if (!isRetryable || attempt === this.retryConfig.maxRetries) {
          break;
        }

        // Calculate delay
        const delay = Math.min(
          this.retryConfig.initialDelay * Math.pow(this.retryConfig.backoffMultiplier, attempt),
          this.retryConfig.maxDelay
        );

        // Check for Retry-After header
        const retryAfter = error.response?.headers?.['retry-after'];
        if (retryAfter) {
          const retryDelay = parseInt(retryAfter, 10) * 1000;
          if (!isNaN(retryDelay)) {
            await sleep(Math.max(delay, retryDelay));
            continue;
          }
        }

        await sleep(delay);
      }
    }

    // All retries exhausted
    throw lastError || new Error('Failed to send email');
  }

  /**
   * Get email thread by ID
   */
  async getThread(threadId: string): Promise<gmail_v1.Schema$Thread> {
    const response = await this.gmail.users.threads.get({
      userId: 'me',
      id: threadId,
    });
    return response.data;
  }

  /**
   * Get email message by ID
   */
  async getMessage(messageId: string): Promise<gmail_v1.Schema$Message> {
    const response = await this.gmail.users.messages.get({
      userId: 'me',
      id: messageId,
    });
    return response.data;
  }

  /**
   * List messages matching query
   */
  async listMessages(
    query?: string,
    maxResults: number = 10
  ): Promise<gmail_v1.Schema$Message[]> {
    const response = await this.gmail.users.messages.list({
      userId: 'me',
      q: query,
      maxResults,
    });
    return response.data.messages || [];
  }
}