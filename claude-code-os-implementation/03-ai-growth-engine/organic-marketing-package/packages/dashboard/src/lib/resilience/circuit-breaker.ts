/**
 * Circuit Breaker Pattern
 *
 * Prevents cascading failures by short-circuiting requests to an
 * external service that is currently failing. The breaker transitions
 * through three states:
 *
 *   CLOSED  ->  OPEN  ->  HALF_OPEN  ->  CLOSED (on success) | OPEN (on failure)
 *
 * When the circuit is OPEN, calls are immediately rejected with a
 * CircuitOpenError so the caller can return a fallback response.
 */

export enum CircuitState {
  CLOSED = 'CLOSED',
  OPEN = 'OPEN',
  HALF_OPEN = 'HALF_OPEN',
}

export interface CircuitBreakerOptions {
  /** Number of consecutive failures before opening the circuit. Default 5. */
  failureThreshold?: number
  /** How long (ms) the circuit stays open before trying half-open. Default 30 000. */
  resetTimeout?: number
  /** Number of successful calls in HALF_OPEN needed to close. Default 2. */
  halfOpenSuccessThreshold?: number
  /** Optional name for logging. */
  name?: string
}

export class CircuitOpenError extends Error {
  constructor(
    public readonly serviceName: string,
    public readonly nextRetryAt: Date
  ) {
    super(
      `Circuit breaker open for "${serviceName}". Retry after ${nextRetryAt.toISOString()}`
    )
    this.name = 'CircuitOpenError'
  }
}

export class CircuitBreaker {
  private state: CircuitState = CircuitState.CLOSED
  private failures = 0
  private successes = 0
  private lastFailureTime = 0

  private readonly failureThreshold: number
  private readonly resetTimeout: number
  private readonly halfOpenSuccessThreshold: number
  readonly name: string

  constructor(options: CircuitBreakerOptions = {}) {
    this.failureThreshold = options.failureThreshold ?? 5
    this.resetTimeout = options.resetTimeout ?? 30_000
    this.halfOpenSuccessThreshold = options.halfOpenSuccessThreshold ?? 2
    this.name = options.name ?? 'default'
  }

  /**
   * Execute `fn` through the circuit breaker.
   *
   * @throws {CircuitOpenError} when the circuit is open
   * @throws Re-throws the original error from `fn` in CLOSED/HALF_OPEN states
   */
  async exec<T>(fn: () => Promise<T>): Promise<T> {
    // Check if the circuit should transition from OPEN -> HALF_OPEN
    if (this.state === CircuitState.OPEN) {
      if (Date.now() - this.lastFailureTime >= this.resetTimeout) {
        this.transitionTo(CircuitState.HALF_OPEN)
      } else {
        throw new CircuitOpenError(
          this.name,
          new Date(this.lastFailureTime + this.resetTimeout)
        )
      }
    }

    try {
      const result = await fn()
      this.onSuccess()
      return result
    } catch (err) {
      this.onFailure()
      throw err
    }
  }

  /** Current circuit state (useful for health checks / dashboards). */
  getState(): CircuitState {
    return this.state
  }

  /** Manually reset the circuit to CLOSED. */
  reset(): void {
    this.transitionTo(CircuitState.CLOSED)
  }

  // ---- internal ----

  private onSuccess(): void {
    if (this.state === CircuitState.HALF_OPEN) {
      this.successes++
      if (this.successes >= this.halfOpenSuccessThreshold) {
        this.transitionTo(CircuitState.CLOSED)
      }
    }
    // In CLOSED state, a success resets the failure counter
    if (this.state === CircuitState.CLOSED) {
      this.failures = 0
    }
  }

  private onFailure(): void {
    this.lastFailureTime = Date.now()

    if (this.state === CircuitState.HALF_OPEN) {
      // Any failure in HALF_OPEN re-opens the circuit
      this.transitionTo(CircuitState.OPEN)
      return
    }

    this.failures++
    if (this.failures >= this.failureThreshold) {
      this.transitionTo(CircuitState.OPEN)
    }
  }

  private transitionTo(newState: CircuitState): void {
    if (newState === this.state) return
    const prev = this.state
    this.state = newState
    this.failures = 0
    this.successes = 0

    if (process.env.NODE_ENV === 'development') {
      // eslint-disable-next-line no-console
      console.log(
        `[CircuitBreaker:${this.name}] ${prev} -> ${newState}`
      )
    }
  }
}

// ---- Pre-configured breakers for known services ----

const breakers = new Map<string, CircuitBreaker>()

/**
 * Get or create a named circuit breaker singleton.
 * Ensures a single breaker instance is shared across the application
 * for each service.
 */
export function getCircuitBreaker(
  name: string,
  options?: Omit<CircuitBreakerOptions, 'name'>
): CircuitBreaker {
  let breaker = breakers.get(name)
  if (!breaker) {
    breaker = new CircuitBreaker({ ...options, name })
    breakers.set(name, breaker)
  }
  return breaker
}

/** Pre-configured breakers with service-appropriate settings. */
export const serviceBreakers = {
  tiktok: () =>
    getCircuitBreaker('tiktok-api', {
      failureThreshold: 3,
      resetTimeout: 60_000,
      halfOpenSuccessThreshold: 2,
    }),
  videoGeneration: () =>
    getCircuitBreaker('video-generation', {
      failureThreshold: 2,
      resetTimeout: 120_000, // video gen is slow, give it more time
      halfOpenSuccessThreshold: 1,
    }),
  metrics: () =>
    getCircuitBreaker('metrics-api', {
      failureThreshold: 5,
      resetTimeout: 30_000,
      halfOpenSuccessThreshold: 2,
    }),
  email: () =>
    getCircuitBreaker('email-service', {
      failureThreshold: 4,
      resetTimeout: 45_000,
      halfOpenSuccessThreshold: 2,
    }),
  blog: () =>
    getCircuitBreaker('blog-api', {
      failureThreshold: 5,
      resetTimeout: 30_000,
      halfOpenSuccessThreshold: 2,
    }),
}
