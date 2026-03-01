/**
 * Validation Error Class
 *
 * Specialized error for form and data validation failures.
 * Carries field-level error details so UI components can
 * highlight individual fields with appropriate messages.
 */

import { ErrorCode, ErrorCategory } from './errorCodes'

export interface FieldError {
  /** The field name / path (e.g. "email", "address.zip") */
  field: string
  /** User-facing error message for this field */
  message: string
  /** The validation rule that failed */
  rule: 'required' | 'format' | 'range' | 'type' | 'unique' | 'custom'
  /** The invalid value (omitted for sensitive fields) */
  value?: unknown
}

export class ValidationError extends Error {
  readonly code: ErrorCode
  readonly category = ErrorCategory.VALIDATION as const
  readonly fieldErrors: FieldError[]
  readonly timestamp: string

  constructor(params: {
    message?: string
    fieldErrors: FieldError[]
    code?: ErrorCode
  }) {
    const message =
      params.message ??
      `Validation failed for ${params.fieldErrors.length} field(s): ${params.fieldErrors.map((e) => e.field).join(', ')}`
    super(message)
    this.name = 'ValidationError'
    this.code = params.code ?? ErrorCode.VALIDATION_CONSTRAINT
    this.fieldErrors = params.fieldErrors
    this.timestamp = new Date().toISOString()
  }

  /** Get the error message for a specific field, or undefined if valid. */
  getFieldError(field: string): string | undefined {
    return this.fieldErrors.find((e) => e.field === field)?.message
  }

  /** Check whether a specific field has validation errors. */
  hasFieldError(field: string): boolean {
    return this.fieldErrors.some((e) => e.field === field)
  }

  /** Get all field names that have errors. */
  get errorFields(): string[] {
    return this.fieldErrors.map((e) => e.field)
  }

  /** Convert to a Record<fieldName, message> for easy form integration. */
  toFieldMap(): Record<string, string> {
    const map: Record<string, string> = {}
    for (const err of this.fieldErrors) {
      map[err.field] = err.message
    }
    return map
  }

  /** Serialize to a plain object for logging / monitoring. */
  toJSON() {
    return {
      name: this.name,
      message: this.message,
      code: this.code,
      category: this.category,
      fieldErrors: this.fieldErrors,
      timestamp: this.timestamp,
    }
  }
}
