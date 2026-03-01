/**
 * API Middleware — composable wrappers for Next.js API route handlers.
 *
 * These middleware functions can be nested to build a resilient pipeline:
 *
 * @example
 * ```ts
 * import {
 *   withErrorHandler,
 *   withLogging,
 *   withTimeout,
 *   withValidation,
 *   validators,
 * } from '@/lib/api/middleware'
 *
 * const bodySchema = {
 *   topic: validators.nonEmptyString('topic'),
 *   channel: validators.nonEmptyString('channel'),
 * }
 *
 * export const POST = withErrorHandler(
 *   withLogging(
 *     withTimeout(30000)(
 *       withValidation(bodySchema)(async (req) => {
 *         const body = await req.json()
 *         return NextResponse.json({ ok: true })
 *       })
 *     )
 *   )
 * )
 * ```
 */

export { withErrorHandler } from './errorHandler'
export { withLogging, generateCorrelationId } from './logging'
export { withTimeout, TimeoutError } from './timeout'
export { withValidation, validators } from './validation'
export type { ValidationSchema } from './validation'
export type { RouteHandler, ApiErrorResponse } from './types'
export { CORRELATION_ID_HEADER } from './types'
