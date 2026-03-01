/**
 * Enhanced Error Classes - Barrel Export
 *
 * Centralized exports for the error classification system.
 *
 * @example
 * ```ts
 * import { ApiError, ValidationError, ServiceError, ErrorCode } from '@/lib/errors'
 * ```
 */

export { ErrorCategory, ErrorCode, errorCodeFromStatus, categoryFromCode } from './errorCodes'
export { ApiError } from './ApiError'
export type { RetryMetadata, RecoveryHint } from './ApiError'
export { ValidationError } from './ValidationError'
export type { FieldError } from './ValidationError'
export { ServiceError } from './ServiceError'
export type { FallbackOption } from './ServiceError'
