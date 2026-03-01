import { NextRequest, NextResponse } from 'next/server'
import { CORRELATION_ID_HEADER, type ApiErrorResponse, type RouteHandler } from './types'

/**
 * A simple schema descriptor for request validation.
 *
 * Each key maps a field name to a validator. The validator receives
 * the raw value and returns either `true` (valid) or a string
 * describing the validation failure.
 */
export interface ValidationSchema {
  [field: string]: (value: unknown) => true | string
}

/**
 * Built-in validators for common cases.
 */
export const validators = {
  required: (label: string) => (value: unknown): true | string =>
    value !== undefined && value !== null && value !== ''
      ? true
      : `${label} is required`,

  string: (label: string) => (value: unknown): true | string =>
    typeof value === 'string' ? true : `${label} must be a string`,

  nonEmptyString: (label: string) => (value: unknown): true | string =>
    typeof value === 'string' && value.trim().length > 0
      ? true
      : `${label} must be a non-empty string`,

  number: (label: string) => (value: unknown): true | string =>
    typeof value === 'number' && !isNaN(value)
      ? true
      : `${label} must be a number`,

  boolean: (label: string) => (value: unknown): true | string =>
    typeof value === 'boolean' ? true : `${label} must be a boolean`,

  oneOf:
    (label: string, allowed: readonly string[]) =>
    (value: unknown): true | string =>
      typeof value === 'string' && allowed.includes(value)
        ? true
        : `${label} must be one of: ${allowed.join(', ')}`,

  optional:
    (inner: (value: unknown) => true | string) =>
    (value: unknown): true | string =>
      value === undefined || value === null ? true : inner(value),
}

/**
 * Validate a body object against a schema.
 * Returns an array of error messages (empty if valid).
 */
function validate(
  body: Record<string, unknown>,
  schema: ValidationSchema
): string[] {
  const errors: string[] = []
  for (const [field, check] of Object.entries(schema)) {
    const result = check(body[field])
    if (result !== true) {
      errors.push(result)
    }
  }
  return errors
}

/**
 * Middleware that validates the JSON request body against a schema.
 *
 * Returns a 400 response with details if validation fails.
 * The parsed body is available at the same `req.json()` call inside
 * the wrapped handler (Next.js caches the parsed body).
 *
 * @example
 * ```ts
 * const schema: ValidationSchema = {
 *   channel_element: validators.nonEmptyString('channel_element'),
 *   topic: validators.nonEmptyString('topic'),
 * }
 *
 * export const POST = withValidation(schema)(async (req) => {
 *   const body = await req.json()
 *   // body is guaranteed to have valid channel_element and topic
 *   return NextResponse.json({ ok: true })
 * })
 * ```
 */
export function withValidation(schema: ValidationSchema) {
  return function wrapper(handler: RouteHandler): RouteHandler {
    return async (req: NextRequest, context) => {
      let body: Record<string, unknown>
      try {
        body = await req.json()
      } catch {
        const correlationId = req.headers.get(CORRELATION_ID_HEADER) || ''
        const errorBody: ApiErrorResponse = {
          error: 'Bad Request',
          message: 'Invalid JSON body',
          correlationId: correlationId || undefined,
          timestamp: new Date().toISOString(),
        }
        return NextResponse.json(errorBody, { status: 400 })
      }

      const errors = validate(body, schema)
      if (errors.length > 0) {
        const correlationId = req.headers.get(CORRELATION_ID_HEADER) || ''
        const errorBody: ApiErrorResponse = {
          error: 'Validation Error',
          message: errors.join('; '),
          correlationId: correlationId || undefined,
          timestamp: new Date().toISOString(),
          details: errors,
        }
        return NextResponse.json(errorBody, { status: 400 })
      }

      return handler(req, context)
    }
  }
}
