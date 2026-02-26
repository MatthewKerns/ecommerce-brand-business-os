/**
 * Configuration Module
 *
 * Centralized configuration management with validation
 * Loads from environment variables with zod schema validation
 *
 * Features:
 * - Environment-specific configuration
 * - Runtime validation with zod
 * - Type-safe config access
 * - Secure credential management
 */

import { config as loadDotenv } from 'dotenv';
import { z } from 'zod';
import type { GmailConfig } from '../core/email/gmail-client';
import type { AIConfig, AIProvider } from '../core/ai/content-generator';
import type { GoogleSheetsConfig } from '../core/leads/google-sheets-storage';

// ============================================================
// Environment Detection
// ============================================================

export type Environment = 'development' | 'staging' | 'production' | 'test';

/**
 * Get current environment
 */
export function getEnvironment(): Environment {
  const env = process.env.NODE_ENV || process.env.ENVIRONMENT || 'development';
  if (['development', 'staging', 'production', 'test'].includes(env)) {
    return env as Environment;
  }
  return 'development';
}

/**
 * Load environment-specific .env file
 */
export function loadEnvironmentConfig(): void {
  const environment = getEnvironment();

  // Load .env file based on environment
  if (environment !== 'production') {
    loadDotenv({ path: `.env.${environment}` });
  }

  // Also load base .env as fallback
  loadDotenv();
}

// ============================================================
// Zod Schemas
// ============================================================

/**
 * Gmail configuration schema
 */
const gmailConfigSchema = z.object({
  clientId: z.string().min(1, 'Gmail client ID is required'),
  clientSecret: z.string().min(1, 'Gmail client secret is required'),
  refreshToken: z.string().min(1, 'Gmail refresh token is required'),
  redirectUri: z.string().url('Gmail redirect URI must be a valid URL'),
  senderEmail: z.string().email('Sender email must be valid'),
  senderName: z.string().optional(),
});

/**
 * AI provider configuration schema
 */
const aiConfigSchema = z.object({
  provider: z.enum(['gemini', 'openai', 'claude'], {
    errorMap: () => ({ message: 'AI provider must be gemini, openai, or claude' }),
  }),
  apiKey: z.string().min(1, 'AI API key is required'),
  model: z.string().optional(),
  temperature: z.number().min(0).max(2).optional(),
  maxTokens: z.number().positive().optional(),
});

/**
 * Google Sheets credentials schema
 */
const googleSheetsCredentialsSchema = z.object({
  clientEmail: z.string().email('Google Sheets client email must be valid'),
  privateKey: z.string().min(1, 'Google Sheets private key is required'),
});

/**
 * Google Sheets configuration schema
 */
const googleSheetsConfigSchema = z.object({
  spreadsheetId: z.string().min(1, 'Spreadsheet ID is required'),
  sheetName: z.string().optional(),
  credentials: googleSheetsCredentialsSchema,
});

/**
 * Storage configuration schema
 */
const storageConfigSchema = z.object({
  type: z.enum(['google-sheets', 'database']),
  config: z.union([googleSheetsConfigSchema, z.any()]),
});

/**
 * Complete application configuration schema
 */
const appConfigSchema = z.object({
  environment: z.enum(['development', 'staging', 'production', 'test']),
  gmail: gmailConfigSchema,
  ai: aiConfigSchema,
  storage: storageConfigSchema,
});

// ============================================================
// Configuration Types
// ============================================================

export type AppConfig = z.infer<typeof appConfigSchema>;

// ============================================================
// Configuration Loading
// ============================================================

/**
 * Load and validate Gmail configuration from environment
 */
export function loadGmailConfig(): GmailConfig {
  const config = {
    clientId: process.env.GMAIL_CLIENT_ID || '',
    clientSecret: process.env.GMAIL_CLIENT_SECRET || '',
    refreshToken: process.env.GMAIL_REFRESH_TOKEN || '',
    redirectUri: process.env.GMAIL_REDIRECT_URI || 'http://localhost:3000/oauth/callback',
    senderEmail: process.env.GMAIL_SENDER_EMAIL || '',
    senderName: process.env.GMAIL_SENDER_NAME,
  };

  try {
    return gmailConfigSchema.parse(config);
  } catch (error) {
    if (error instanceof z.ZodError) {
      const messages = error.errors.map(e => `${e.path.join('.')}: ${e.message}`).join(', ');
      throw new Error(`Gmail configuration validation failed: ${messages}`);
    }
    throw error;
  }
}

/**
 * Load and validate AI configuration from environment
 */
export function loadAIConfig(): AIConfig {
  const provider = (process.env.AI_PROVIDER || 'gemini') as AIProvider;

  const config = {
    provider,
    apiKey: process.env.AI_API_KEY || '',
    model: process.env.AI_MODEL,
    temperature: process.env.AI_TEMPERATURE ? parseFloat(process.env.AI_TEMPERATURE) : undefined,
    maxTokens: process.env.AI_MAX_TOKENS ? parseInt(process.env.AI_MAX_TOKENS, 10) : undefined,
  };

  try {
    return aiConfigSchema.parse(config);
  } catch (error) {
    if (error instanceof z.ZodError) {
      const messages = error.errors.map(e => `${e.path.join('.')}: ${e.message}`).join(', ');
      throw new Error(`AI configuration validation failed: ${messages}`);
    }
    throw error;
  }
}

/**
 * Load and validate Google Sheets configuration from environment
 */
export function loadGoogleSheetsConfig(): GoogleSheetsConfig {
  // Private key may contain \n as literal string, need to convert to actual newlines
  const privateKey = (process.env.GOOGLE_SHEETS_PRIVATE_KEY || '')
    .replace(/\\n/g, '\n');

  const config = {
    spreadsheetId: process.env.GOOGLE_SHEETS_SPREADSHEET_ID || '',
    sheetName: process.env.GOOGLE_SHEETS_SHEET_NAME || 'Leads',
    credentials: {
      clientEmail: process.env.GOOGLE_SHEETS_CLIENT_EMAIL || '',
      privateKey,
    },
  };

  try {
    return googleSheetsConfigSchema.parse(config);
  } catch (error) {
    if (error instanceof z.ZodError) {
      const messages = error.errors.map(e => `${e.path.join('.')}: ${e.message}`).join(', ');
      throw new Error(`Google Sheets configuration validation failed: ${messages}`);
    }
    throw error;
  }
}

/**
 * Load and validate complete application configuration
 */
export function loadConfig(): AppConfig {
  // Load environment-specific config
  loadEnvironmentConfig();

  const environment = getEnvironment();
  const gmail = loadGmailConfig();
  const ai = loadAIConfig();
  const storage = {
    type: (process.env.STORAGE_TYPE || 'google-sheets') as 'google-sheets' | 'database',
    config: process.env.STORAGE_TYPE === 'database' ? {} : loadGoogleSheetsConfig(),
  };

  const config = {
    environment,
    gmail,
    ai,
    storage,
  };

  try {
    return appConfigSchema.parse(config);
  } catch (error) {
    if (error instanceof z.ZodError) {
      const messages = error.errors.map(e => `${e.path.join('.')}: ${e.message}`).join(', ');
      throw new Error(`Configuration validation failed: ${messages}`);
    }
    throw error;
  }
}

// ============================================================
// Validation Helpers
// ============================================================

/**
 * Validate Gmail configuration without throwing
 */
export function validateGmailConfig(config: unknown): config is GmailConfig {
  return gmailConfigSchema.safeParse(config).success;
}

/**
 * Validate AI configuration without throwing
 */
export function validateAIConfig(config: unknown): config is AIConfig {
  return aiConfigSchema.safeParse(config).success;
}

/**
 * Validate Google Sheets configuration without throwing
 */
export function validateGoogleSheetsConfig(config: unknown): config is GoogleSheetsConfig {
  return googleSheetsConfigSchema.safeParse(config).success;
}

/**
 * Check if all required environment variables are set
 */
export function checkRequiredEnvVars(): { missing: string[]; isValid: boolean } {
  const required = [
    'GMAIL_CLIENT_ID',
    'GMAIL_CLIENT_SECRET',
    'GMAIL_REFRESH_TOKEN',
    'GMAIL_SENDER_EMAIL',
    'AI_PROVIDER',
    'AI_API_KEY',
  ];

  // Add storage-specific requirements
  const storageType = process.env.STORAGE_TYPE || 'google-sheets';
  if (storageType === 'google-sheets') {
    required.push(
      'GOOGLE_SHEETS_SPREADSHEET_ID',
      'GOOGLE_SHEETS_CLIENT_EMAIL',
      'GOOGLE_SHEETS_PRIVATE_KEY'
    );
  }

  const missing = required.filter(key => !process.env[key]);

  return {
    missing,
    isValid: missing.length === 0,
  };
}

// ============================================================
// Default Export
// ============================================================

/**
 * Pre-loaded configuration instance
 * Use this for convenience in most cases
 */
let cachedConfig: AppConfig | null = null;

export function getConfig(): AppConfig {
  if (!cachedConfig) {
    cachedConfig = loadConfig();
  }
  return cachedConfig;
}

/**
 * Reset cached configuration (useful for testing)
 */
export function resetConfig(): void {
  cachedConfig = null;
}

// Named exports for individual configs
export {
  loadGmailConfig,
  loadAIConfig,
  loadGoogleSheetsConfig,
  loadConfig,
};
