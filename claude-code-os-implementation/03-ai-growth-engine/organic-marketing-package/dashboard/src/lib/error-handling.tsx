/**
 * Error Handling Utilities
 * Based on Software Development Best Practices Guide - ERROR_HANDLING.md
 *
 * Principles:
 * - Robustness: UI continues operating despite component failures
 * - Diagnosability: Clear information about what went wrong
 * - User Trust: Graceful failures with helpful guidance
 */

import { ComponentType } from 'react';
import { ApiError } from './errors/ApiError';
import { ValidationError } from './errors/ValidationError';
import { ServiceError } from './errors/ServiceError';
import { ErrorCategory, ErrorCode } from './errors/errorCodes';

/**
 * Error severity levels for UI components
 */
export enum ErrorSeverity {
  LOW = 'low',       // Component can degrade gracefully
  MEDIUM = 'medium', // Partial functionality available
  HIGH = 'high',     // Critical component failure
  CRITICAL = 'critical' // Page-level failure
}

/**
 * Component error with context
 */
export class ComponentError extends Error {
  constructor(
    message: string,
    public readonly componentName: string,
    public readonly severity: ErrorSeverity = ErrorSeverity.MEDIUM,
    public readonly fallbackAvailable: boolean = true,
    public readonly cause?: Error
  ) {
    super(message);
    this.name = 'ComponentError';
  }
}

/**
 * Dynamic import error handler
 * Returns a fallback component when dynamic import fails
 */
export function createDynamicImportHandler<T = any>(
  componentName: string,
  fallbackComponent: ComponentType<T>
) {
  return (error: Error) => {
    // Log error in development
    if (process.env.NODE_ENV === 'development') {
      console.error(`Failed to load component: ${componentName}`, error);
    }

    // Report to error tracking in production
    if (process.env.NODE_ENV === 'production') {
      // Here you would send to your error tracking service
      // e.g., Sentry, LogRocket, etc.
      console.error(`Component load failure: ${componentName}`);
    }

    // Return fallback component
    return { default: fallbackComponent };
  };
}

/**
 * Safe dynamic import with automatic fallback
 */
export async function safeDynamicImport<T = any>(
  importFn: () => Promise<any>,
  componentName: string,
  fallbackComponent: ComponentType<T>
): Promise<{ default: ComponentType<T> }> {
  try {
    const module = await importFn();

    // Validate the module has the expected export
    if (!module || typeof module !== 'object') {
      throw new ComponentError(
        `Invalid module structure for ${componentName}`,
        componentName,
        ErrorSeverity.HIGH
      );
    }

    // Check for the component export (handles both default and named exports)
    const component = module.default || module[componentName];

    if (!component) {
      console.warn(`Component ${componentName} not found in module, using fallback`);
      return { default: fallbackComponent };
    }

    return { default: component };
  } catch (error) {
    return createDynamicImportHandler(componentName, fallbackComponent)(error as Error);
  }
}

/**
 * Error logging utility
 */
export function logComponentError(
  error: Error,
  componentName: string,
  additionalContext?: Record<string, any>
) {
  const errorInfo = {
    timestamp: new Date().toISOString(),
    component: componentName,
    message: error.message,
    stack: error.stack,
    ...additionalContext
  };

  if (process.env.NODE_ENV === 'development') {
    console.group(`🚨 Component Error: ${componentName}`);
    console.error('Error:', error);
    console.table(additionalContext);
    console.groupEnd();
  }

  // In production, send to error tracking service
  if (process.env.NODE_ENV === 'production') {
    // e.g., Sentry.captureException(error, { extra: errorInfo });
  }
}

/**
 * Retry mechanism for transient failures
 */
export async function retryOperation<T>(
  operation: () => Promise<T>,
  maxRetries: number = 3,
  delayMs: number = 1000,
  backoffMultiplier: number = 2
): Promise<T> {
  let lastError: Error;

  for (let i = 0; i < maxRetries; i++) {
    try {
      return await operation();
    } catch (error) {
      lastError = error as Error;

      if (i < maxRetries - 1) {
        const delay = delayMs * Math.pow(backoffMultiplier, i);
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }
  }

  throw lastError!;
}

/**
 * Check if error is recoverable
 */
export function isRecoverableError(error: Error): boolean {
  // Network errors are often recoverable
  if (error.message.includes('fetch') || error.message.includes('network')) {
    return true;
  }

  // Chunk load errors might be recoverable with a refresh
  if (error.message.includes('ChunkLoadError') || error.message.includes('Loading chunk')) {
    return true;
  }

  // Syntax errors and reference errors are not recoverable
  if (error instanceof SyntaxError || error instanceof ReferenceError) {
    return false;
  }

  return false;
}

/**
 * User-friendly error messages
 */
export function getUserFriendlyErrorMessage(error: Error): string {
  // Map technical errors to user-friendly messages
  const errorMap: Record<string, string> = {
    'ChunkLoadError': 'Some components failed to load. Please refresh the page.',
    'NetworkError': 'Connection issue detected. Please check your internet connection.',
    'TimeoutError': 'The operation took too long. Please try again.',
    'PermissionError': 'You don\'t have permission to perform this action.',
    'ValidationError': 'Please check your input and try again.',
  };

  // Check if error type matches any known patterns
  for (const [pattern, message] of Object.entries(errorMap)) {
    if (error.name.includes(pattern) || error.message.includes(pattern)) {
      return message;
    }
  }

  // Generic fallback message
  return 'Something went wrong. Please try again or contact support if the issue persists.';
}

/**
 * Create a fallback component with consistent styling
 */
export function createFallbackComponent(
  componentName: string,
  icon?: ComponentType<{ className?: string }>,
  message?: string
): ComponentType<any> {
  return function FallbackComponent(props: any) {
    const Icon = icon;

    return (
      <div className="flex flex-col items-center justify-center min-h-[200px] p-6 text-center">
        {Icon && <Icon className="h-12 w-12 text-gray-400 mb-3" />}
        <p className="text-sm font-medium text-gray-900 mb-1">
          {componentName}
        </p>
        <p className="text-sm text-gray-500">
          {message || 'This component is temporarily unavailable'}
        </p>
        {props.onRetry && (
          <button
            onClick={props.onRetry}
            className="mt-4 text-sm text-blue-600 hover:text-blue-500"
          >
            Try Again
          </button>
        )}
      </div>
    );
  };
}

// ---------------------------------------------------------------------------
// Enhanced error classification and recovery utilities
// ---------------------------------------------------------------------------

/**
 * Classify an error into a category for routing and display decisions.
 */
export function getErrorCategory(error: unknown): ErrorCategory {
  if (error instanceof ApiError) return error.category;
  if (error instanceof ValidationError) return ErrorCategory.VALIDATION;
  if (error instanceof ServiceError) return ErrorCategory.SERVICE;
  if (error instanceof ComponentError) return ErrorCategory.COMPONENT;

  if (error instanceof Error) {
    const msg = error.message.toLowerCase();
    if (msg.includes('network') || msg.includes('fetch') || msg.includes('timeout')) {
      return ErrorCategory.NETWORK;
    }
    if (msg.includes('unauthorized') || msg.includes('forbidden') || msg.includes('auth')) {
      return ErrorCategory.AUTH;
    }
    if (msg.includes('validation') || msg.includes('invalid')) {
      return ErrorCategory.VALIDATION;
    }
  }

  return ErrorCategory.UNKNOWN;
}

/**
 * Returns a user-actionable recovery message with a recommended action.
 * This is richer than getUserFriendlyErrorMessage: it tells the user
 * _what to do_ rather than just _what happened_.
 */
export function getUserActionableMessage(error: unknown): {
  title: string;
  description: string;
  action: string;
  actionType: 'retry' | 'redirect' | 'refresh' | 'contact_support' | 'dismiss';
  url?: string;
} {
  if (error instanceof ApiError) {
    return {
      title: 'Request Failed',
      description: error.recoveryHint.description,
      action: error.recoveryHint.action,
      actionType: error.recoveryHint.type,
      url: error.recoveryHint.url,
    };
  }

  if (error instanceof ValidationError) {
    return {
      title: 'Validation Error',
      description: `Please fix the following fields: ${error.errorFields.join(', ')}`,
      action: 'Fix Fields',
      actionType: 'dismiss',
    };
  }

  if (error instanceof ServiceError) {
    return {
      title: `${error.serviceName} Issue`,
      description: error.userMessage,
      action: error.retryable ? 'Retry' : 'Dismiss',
      actionType: error.retryable ? 'retry' : 'dismiss',
    };
  }

  const category = getErrorCategory(error);

  if (category === ErrorCategory.NETWORK) {
    return {
      title: 'Connection Problem',
      description: 'Please check your internet connection and try again.',
      action: 'Retry',
      actionType: 'retry',
    };
  }

  if (category === ErrorCategory.AUTH) {
    return {
      title: 'Authentication Required',
      description: 'Your session may have expired. Please sign in again.',
      action: 'Sign In',
      actionType: 'redirect',
      url: '/sign-in',
    };
  }

  return {
    title: 'Something Went Wrong',
    description: 'An unexpected error occurred. Please try again or contact support.',
    action: 'Retry',
    actionType: 'retry',
  };
}

/**
 * Determine whether an operation should be retried given its error and attempt count.
 *
 * Works with the enhanced error classes or falls back to heuristics
 * for generic Error instances.
 */
export function shouldRetry(error: unknown, attempt: number, maxAttempts: number = 3): boolean {
  if (attempt >= maxAttempts) return false;

  if (error instanceof ApiError) {
    return error.retryMetadata.retryable && attempt < error.retryMetadata.maxRetries;
  }

  if (error instanceof ServiceError) {
    return error.retryable;
  }

  // Validation errors are never retryable
  if (error instanceof ValidationError) {
    return false;
  }

  if (error instanceof Error) {
    const msg = error.message.toLowerCase();
    // Network / transient errors are retryable
    if (msg.includes('network') || msg.includes('fetch') || msg.includes('timeout')) {
      return true;
    }
    // Chunk load errors might be retryable once (e.g., after a deploy)
    if (msg.includes('chunkloaderror') || msg.includes('loading chunk')) {
      return attempt < 1;
    }
  }

  return false;
}

/**
 * Get the error code from any error instance.
 * Returns ErrorCode.UNKNOWN for generic errors.
 */
export function getErrorCode(error: unknown): ErrorCode {
  if (error instanceof ApiError) return error.code;
  if (error instanceof ValidationError) return error.code;
  if (error instanceof ServiceError) return error.code;
  return ErrorCode.UNKNOWN;
}