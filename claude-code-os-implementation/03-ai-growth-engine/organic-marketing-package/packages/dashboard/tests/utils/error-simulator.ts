/**
 * Error Simulation & Chaos Engineering Toolkit
 *
 * Provides controlled failure injection for testing error handling,
 * circuit breakers, and retry strategies in development/test environments.
 */

// ---- Types ----

export type FailureType =
  | 'network-error'
  | 'timeout'
  | 'server-error'
  | 'rate-limit'
  | 'bad-request'
  | 'not-found'
  | 'forbidden'
  | 'service-unavailable'

export interface FailureScenario {
  name: string
  description: string
  failureType: FailureType
  /** Probability of failure (0-1). Default 1 (always fails). */
  probability?: number
  /** Simulated latency in ms added before the response. */
  latencyMs?: number
  /** HTTP status code for the simulated error. */
  statusCode?: number
  /** Custom error message. */
  errorMessage?: string
  /** Number of consecutive failures before auto-recovery. -1 = never recover. */
  failureCount?: number
}

export interface NetworkCondition {
  /** Simulated latency in ms. */
  latencyMs: number
  /** Packet loss probability (0-1). */
  packetLoss: number
  /** Whether to simulate offline mode. */
  offline: boolean
  /** Bandwidth throttle in KB/s. 0 = no throttle. */
  bandwidthKbps: number
}

// ---- Default scenarios ----

export const scenarios: Record<string, FailureScenario> = {
  networkFailure: {
    name: 'Network Failure',
    description: 'Simulates a complete network outage',
    failureType: 'network-error',
    errorMessage: 'Failed to fetch: Network request failed',
  },
  slowResponse: {
    name: 'Slow Response',
    description: 'Simulates high latency (5s) responses',
    failureType: 'timeout',
    latencyMs: 5000,
  },
  serverCrash: {
    name: 'Server Crash (500)',
    description: 'Returns 500 Internal Server Error',
    failureType: 'server-error',
    statusCode: 500,
    errorMessage: 'Internal server error',
  },
  rateLimited: {
    name: 'Rate Limited (429)',
    description: 'Returns 429 Too Many Requests',
    failureType: 'rate-limit',
    statusCode: 429,
    errorMessage: 'Rate limit exceeded. Retry after 60 seconds.',
  },
  intermittentFailure: {
    name: 'Intermittent Failure',
    description: '50% chance of server error',
    failureType: 'server-error',
    probability: 0.5,
    statusCode: 500,
  },
  circuitBreakerTrip: {
    name: 'Circuit Breaker Trip',
    description: 'Fails 5 times to trip a circuit breaker, then recovers',
    failureType: 'server-error',
    statusCode: 503,
    failureCount: 5,
  },
  serviceUnavailable: {
    name: 'Service Unavailable',
    description: 'Returns 503 Service Unavailable',
    failureType: 'service-unavailable',
    statusCode: 503,
    errorMessage: 'Service temporarily unavailable',
  },
}

export const networkConditions: Record<string, NetworkCondition> = {
  good: { latencyMs: 50, packetLoss: 0, offline: false, bandwidthKbps: 0 },
  slow3G: { latencyMs: 2000, packetLoss: 0.02, offline: false, bandwidthKbps: 50 },
  fastLoss: { latencyMs: 100, packetLoss: 0.1, offline: false, bandwidthKbps: 0 },
  offline: { latencyMs: 0, packetLoss: 1, offline: true, bandwidthKbps: 0 },
}

// ---- Error Simulator ----

type FetchFn = typeof globalThis.fetch

export class ErrorSimulator {
  private activeScenarios = new Map<string, {
    scenario: FailureScenario
    remainingFailures: number
  }>()
  private networkCondition: NetworkCondition = networkConditions.good!
  private originalFetch: FetchFn | null = null
  private isIntercepting = false

  /**
   * Inject a failure scenario for a URL pattern.
   * The pattern is matched against the request URL using `String.includes`.
   */
  injectFailure(urlPattern: string, scenario: FailureScenario): void {
    this.activeScenarios.set(urlPattern, {
      scenario,
      remainingFailures: scenario.failureCount ?? -1,
    })
  }

  /** Remove a previously injected failure scenario. */
  removeFailure(urlPattern: string): void {
    this.activeScenarios.delete(urlPattern)
  }

  /** Remove all failure scenarios. */
  clearAll(): void {
    this.activeScenarios.clear()
    this.networkCondition = networkConditions.good!
  }

  /** Set simulated network conditions. */
  setNetworkCondition(condition: NetworkCondition): void {
    this.networkCondition = condition
  }

  /** Get current active scenarios (for UI display). */
  getActiveScenarios(): Array<{ pattern: string; scenario: FailureScenario; remaining: number }> {
    return Array.from(this.activeScenarios.entries()).map(([pattern, entry]) => ({
      pattern,
      scenario: entry.scenario,
      remaining: entry.remainingFailures,
    }))
  }

  /**
   * Install a global fetch interceptor.
   * In test/dev, this replaces `globalThis.fetch` with a version
   * that applies failure scenarios and network conditions.
   */
  install(): void {
    if (this.isIntercepting) return
    this.originalFetch = globalThis.fetch
    this.isIntercepting = true

    const self = this
    globalThis.fetch = async function simulatedFetch(
      input: RequestInfo | URL,
      init?: RequestInit
    ): Promise<Response> {
      const url = typeof input === 'string'
        ? input
        : input instanceof URL
          ? input.toString()
          : input.url

      // Apply network condition: offline
      if (self.networkCondition.offline) {
        throw new TypeError('Failed to fetch: Network request failed')
      }

      // Apply network condition: packet loss
      if (
        self.networkCondition.packetLoss > 0 &&
        Math.random() < self.networkCondition.packetLoss
      ) {
        throw new TypeError('Failed to fetch: Network request failed')
      }

      // Apply network condition: latency
      if (self.networkCondition.latencyMs > 0) {
        await sleep(self.networkCondition.latencyMs)
      }

      // Check for matching failure scenario
      for (const [pattern, entry] of Array.from(self.activeScenarios.entries())) {
        if (!url.includes(pattern)) continue

        const { scenario } = entry

        // Check remaining failure count
        if (entry.remainingFailures === 0) {
          self.activeScenarios.delete(pattern)
          continue
        }
        if (entry.remainingFailures > 0) {
          entry.remainingFailures--
        }

        // Check probability
        if (
          scenario.probability !== undefined &&
          scenario.probability < 1 &&
          Math.random() > scenario.probability
        ) {
          continue // luck — no failure this time
        }

        // Add scenario latency
        if (scenario.latencyMs) {
          await sleep(scenario.latencyMs)
        }

        // Produce the failure
        if (scenario.failureType === 'network-error') {
          throw new TypeError(
            scenario.errorMessage || 'Failed to fetch: Network request failed'
          )
        }

        if (scenario.failureType === 'timeout') {
          // Simulate a timeout by waiting longer than typical AbortController timeout
          await sleep(scenario.latencyMs || 35000)
          throw new DOMException('The operation was aborted', 'AbortError')
        }

        // HTTP error responses
        const status = scenario.statusCode || statusForType(scenario.failureType)
        return new Response(
          JSON.stringify({
            error: scenario.failureType,
            message: scenario.errorMessage || `Simulated ${scenario.failureType}`,
            simulated: true,
          }),
          {
            status,
            headers: { 'Content-Type': 'application/json' },
          }
        )
      }

      // No matching scenario — pass through to real fetch
      return self.originalFetch!(input, init)
    }
  }

  /** Restore the original global fetch. */
  uninstall(): void {
    if (!this.isIntercepting || !this.originalFetch) return
    globalThis.fetch = this.originalFetch
    this.originalFetch = null
    this.isIntercepting = false
    this.clearAll()
  }
}

// ---- Failure injection middleware for API routes (server-side) ----

import { NextRequest, NextResponse } from 'next/server'

type RouteHandler = (
  req: NextRequest,
  context?: unknown
) => Promise<NextResponse> | NextResponse

/** In-memory registry of server-side failure injections (dev only). */
const serverFailures = new Map<string, FailureScenario>()

export function injectServerFailure(routePattern: string, scenario: FailureScenario): void {
  serverFailures.set(routePattern, scenario)
}

export function clearServerFailures(): void {
  serverFailures.clear()
}

/**
 * Middleware that checks for injected server failures before
 * executing the real handler. Only active when NODE_ENV !== 'production'.
 */
export function withFailureInjection(handler: RouteHandler): RouteHandler {
  return async (req: NextRequest, context) => {
    if (process.env.NODE_ENV === 'production') return handler(req, context)

    const path = new URL(req.url).pathname
    for (const [pattern, scenario] of Array.from(serverFailures.entries())) {
      if (!path.includes(pattern)) continue

      if (scenario.latencyMs) {
        await sleep(scenario.latencyMs)
      }

      if (scenario.probability !== undefined && Math.random() > scenario.probability) {
        continue
      }

      const status = scenario.statusCode || statusForType(scenario.failureType)
      return NextResponse.json(
        {
          error: scenario.failureType,
          message: scenario.errorMessage || `Injected failure: ${scenario.name}`,
          simulated: true,
        },
        { status }
      )
    }

    return handler(req, context)
  }
}

// ---- Helpers ----

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

function statusForType(type: FailureType): number {
  switch (type) {
    case 'bad-request': return 400
    case 'forbidden': return 403
    case 'not-found': return 404
    case 'rate-limit': return 429
    case 'server-error': return 500
    case 'service-unavailable': return 503
    case 'network-error': return 0
    case 'timeout': return 504
  }
}
