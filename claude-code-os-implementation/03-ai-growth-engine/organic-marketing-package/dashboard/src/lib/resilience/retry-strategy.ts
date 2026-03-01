/**
 * Retry Strategy with Exponential Backoff and Jitter
 *
 * Provides configurable retry policies per service with smart retry
 * decisions based on error type, retry budgets to prevent storms,
 * and idempotency key generation for non-idempotent operations.
 */

// ---- Retry Policy Configuration ----

export interface RetryPolicy {
  /** Maximum number of retry attempts. */
  maxRetries: number
  /** Base delay in ms before the first retry. */
  baseDelayMs: number
  /** Maximum delay cap in ms. */
  maxDelayMs: number
  /** Jitter factor (0 = no jitter, 1 = full jitter). Default 1. */
  jitterFactor?: number
}

const DEFAULT_POLICY: RetryPolicy = {
  maxRetries: 3,
  baseDelayMs: 500,
  maxDelayMs: 15_000,
  jitterFactor: 1,
}

/**
 * Pre-defined retry policies for different operation types.
 */
export const retryPolicies = {
  /** Fast retries for read operations (GET). */
  read: {
    maxRetries: 3,
    baseDelayMs: 300,
    maxDelayMs: 5_000,
    jitterFactor: 1,
  } satisfies RetryPolicy,

  /** Conservative retries for write operations (POST/PUT/DELETE). */
  write: {
    maxRetries: 2,
    baseDelayMs: 1_000,
    maxDelayMs: 10_000,
    jitterFactor: 1,
  } satisfies RetryPolicy,

  /** Aggressive retries for critical operations. */
  critical: {
    maxRetries: 5,
    baseDelayMs: 500,
    maxDelayMs: 30_000,
    jitterFactor: 0.5,
  } satisfies RetryPolicy,

  /** No retries — fail immediately. */
  none: {
    maxRetries: 0,
    baseDelayMs: 0,
    maxDelayMs: 0,
    jitterFactor: 0,
  } satisfies RetryPolicy,
}

// ---- Backoff Calculation ----

/**
 * Calculate delay with exponential backoff and jitter.
 *
 * Uses the "full jitter" approach recommended by AWS:
 *   delay = random_between(0, min(cap, base * 2^attempt))
 */
export function calculateBackoff(
  attempt: number,
  policy: RetryPolicy
): number {
  const { baseDelayMs, maxDelayMs, jitterFactor = 1 } = policy
  const exponentialDelay = Math.min(maxDelayMs, baseDelayMs * Math.pow(2, attempt))

  if (jitterFactor <= 0) return exponentialDelay

  // Full jitter: uniform random between 0 and exponentialDelay
  const jitter = Math.random() * exponentialDelay * jitterFactor
  const deterministic = exponentialDelay * (1 - jitterFactor)
  return Math.round(deterministic + jitter)
}

// ---- Retryability Decisions ----

/**
 * Determine whether an error is retryable.
 *
 * Client errors (4xx) are generally NOT retried because the request
 * itself is faulty. Server errors (5xx) and network errors ARE retried.
 * Rate-limit errors (429) are retried.
 */
export function isRetryableError(err: unknown): boolean {
  if (!err || typeof err !== 'object') return false

  // Check for HTTP status on the error object
  if ('status' in err && typeof (err as { status: unknown }).status === 'number') {
    const status = (err as { status: number }).status
    // 429 (rate limit) is retryable
    if (status === 429) return true
    // Other 4xx errors are NOT retryable
    if (status >= 400 && status < 500) return false
    // 5xx errors are retryable
    if (status >= 500) return true
  }

  // Network / abort / timeout errors are retryable
  if (err instanceof Error) {
    const msg = err.message.toLowerCase()
    if (
      msg.includes('fetch') ||
      msg.includes('network') ||
      msg.includes('econnrefused') ||
      msg.includes('econnreset') ||
      msg.includes('timeout') ||
      msg.includes('aborted') ||
      err.name === 'AbortError' ||
      err.name === 'TimeoutError'
    ) {
      return true
    }
  }

  return false
}

// ---- Retry Budget ----

/**
 * A sliding-window budget that limits total retries over a time window
 * to prevent retry storms across concurrent requests.
 */
export class RetryBudget {
  private timestamps: number[] = []

  constructor(
    /** Maximum retries allowed in the window. */
    private readonly maxRetries: number,
    /** Window duration in ms. Default 60_000 (1 minute). */
    private readonly windowMs: number = 60_000
  ) {}

  /** Check whether a retry is allowed. */
  tryAcquire(): boolean {
    const now = Date.now()
    this.timestamps = this.timestamps.filter((t) => now - t < this.windowMs)
    if (this.timestamps.length >= this.maxRetries) return false
    this.timestamps.push(now)
    return true
  }

  /** How many retries remain in the current window. */
  remaining(): number {
    const now = Date.now()
    this.timestamps = this.timestamps.filter((t) => now - t < this.windowMs)
    return Math.max(0, this.maxRetries - this.timestamps.length)
  }
}

// ---- Idempotency ----

/**
 * Generate a unique idempotency key for non-idempotent operations.
 * Combine the operation identifier with a timestamp and random component
 * so retries carry the same key.
 */
export function generateIdempotencyKey(operationId: string): string {
  const timestamp = Date.now().toString(36)
  const random = Math.random().toString(36).substring(2, 8)
  return `idem_${operationId}_${timestamp}_${random}`
}

// ---- Core Retry Function ----

export interface RetryOptions {
  policy?: RetryPolicy
  budget?: RetryBudget
  /** Called before each retry. Return false to abort. */
  onRetry?: (attempt: number, error: unknown, delayMs: number) => boolean | void
  /** Abort signal to cancel retries externally. */
  signal?: AbortSignal
}

/**
 * Execute `fn` with retries according to the given policy.
 *
 * @example
 * ```ts
 * const data = await withRetry(
 *   () => fetch('https://api.example.com/data').then(r => r.json()),
 *   { policy: retryPolicies.read }
 * )
 * ```
 */
export async function withRetry<T>(
  fn: () => Promise<T>,
  options: RetryOptions = {}
): Promise<T> {
  const policy = options.policy ?? DEFAULT_POLICY
  const { budget, onRetry, signal } = options
  let lastError: unknown

  for (let attempt = 0; attempt <= policy.maxRetries; attempt++) {
    try {
      return await fn()
    } catch (err) {
      lastError = err

      // If this was the last attempt or the error is not retryable, throw
      if (attempt >= policy.maxRetries || !isRetryableError(err)) {
        throw err
      }

      // Check abort signal
      if (signal?.aborted) throw err

      // Check retry budget
      if (budget && !budget.tryAcquire()) throw err

      const delayMs = calculateBackoff(attempt, policy)

      // Notify caller
      if (onRetry) {
        const shouldContinue = onRetry(attempt + 1, err, delayMs)
        if (shouldContinue === false) throw err
      }

      // Wait before retrying
      await new Promise<void>((resolve, reject) => {
        const timer = setTimeout(resolve, delayMs)
        if (signal) {
          const onAbort = () => {
            clearTimeout(timer)
            reject(err)
          }
          signal.addEventListener('abort', onAbort, { once: true })
        }
      })
    }
  }

  throw lastError
}

// ---- Request Deduplication ----

const inflightRequests = new Map<string, Promise<unknown>>()

/**
 * Deduplicate concurrent identical requests.
 *
 * If a request with the same `key` is already in-flight, the
 * existing promise is returned instead of initiating a new request.
 *
 * @example
 * ```ts
 * const data = await deduplicateRequest('metrics-fetch', () =>
 *   fetch('/api/metrics').then(r => r.json())
 * )
 * ```
 */
export async function deduplicateRequest<T>(
  key: string,
  fn: () => Promise<T>
): Promise<T> {
  const existing = inflightRequests.get(key)
  if (existing) return existing as Promise<T>

  const promise = fn().finally(() => {
    inflightRequests.delete(key)
  })

  inflightRequests.set(key, promise)
  return promise
}
