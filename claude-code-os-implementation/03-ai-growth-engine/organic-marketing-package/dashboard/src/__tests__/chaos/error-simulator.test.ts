/* eslint-disable @typescript-eslint/no-explicit-any */
/**
 * Tests for the Error Simulation & Chaos Engineering Toolkit.
 *
 * Validates that failure injection, network condition simulation,
 * and the fetch interceptor work correctly for testing error handling paths.
 */

// Polyfill Response for jsdom environment (not available by default)
if (typeof globalThis.Response === 'undefined') {
  ;(globalThis as any).Response = class MockResponse {
    private _body: string
    status: number
    ok: boolean

    constructor(
      body?: string | null,
      init?: { status?: number; headers?: Record<string, string> }
    ) {
      this._body = body ?? ''
      this.status = init?.status ?? 200
      this.ok = this.status >= 200 && this.status < 300
    }

    async json() {
      return JSON.parse(this._body)
    }

    async text() {
      return this._body
    }
  }
}

// We need to mock next/server since error-simulator imports it
jest.mock('next/server', () => ({
  NextRequest: jest.fn(),
  NextResponse: {
    json: jest.fn((body: unknown, init?: { status?: number }) => ({
      body,
      status: init?.status ?? 200,
    })),
  },
}))

import {
  ErrorSimulator,
  scenarios,
  networkConditions,
  injectServerFailure,
  clearServerFailures,
  withFailureInjection,
} from '../../../tests/utils/error-simulator'
import type { FailureScenario } from '../../../tests/utils/error-simulator'

// Simple passthrough mock for when no scenario matches
function createPassthroughMock() {
  return jest.fn().mockResolvedValue({
    ok: true,
    status: 200,
    json: async () => ({ ok: true }),
    text: async () => '{"ok":true}',
  })
}

describe('ErrorSimulator', () => {
  let simulator: ErrorSimulator
  let realFetch: typeof globalThis.fetch

  beforeEach(() => {
    simulator = new ErrorSimulator()
    realFetch = globalThis.fetch
    globalThis.fetch = createPassthroughMock()
  })

  afterEach(() => {
    simulator.uninstall()
    globalThis.fetch = realFetch
  })

  describe('install/uninstall', () => {
    it('replaces and restores global fetch', () => {
      const fetchBeforeInstall = globalThis.fetch
      simulator.install()
      expect(globalThis.fetch).not.toBe(fetchBeforeInstall)
      simulator.uninstall()
      expect(globalThis.fetch).toBe(fetchBeforeInstall)
    })

    it('is idempotent on double install', () => {
      simulator.install()
      const interceptedFetch = globalThis.fetch
      simulator.install()
      expect(globalThis.fetch).toBe(interceptedFetch)
    })

    it('is safe to uninstall without install', () => {
      expect(() => simulator.uninstall()).not.toThrow()
    })
  })

  describe('failure injection', () => {
    it('throws TypeError for network-error scenario', async () => {
      simulator.install()
      simulator.injectFailure('/api/test', scenarios['networkFailure']!)
      await expect(fetch('/api/test')).rejects.toThrow(TypeError)
    })

    it('returns HTTP error for server-error scenario', async () => {
      simulator.install()
      simulator.injectFailure('/api/metrics', scenarios['serverCrash']!)
      const response = await fetch('/api/metrics')
      expect(response.status).toBe(500)
      const body = await response.json()
      expect(body.simulated).toBe(true)
      expect(body.error).toBe('server-error')
    })

    it('returns 429 for rate-limit scenario', async () => {
      simulator.install()
      simulator.injectFailure('/api/data', scenarios['rateLimited']!)
      const response = await fetch('/api/data')
      expect(response.status).toBe(429)
    })

    it('returns 503 for service-unavailable scenario', async () => {
      simulator.install()
      simulator.injectFailure('/api/service', scenarios['serviceUnavailable']!)
      const response = await fetch('/api/service')
      expect(response.status).toBe(503)
    })

    it('passes through to real fetch when no scenario matches', async () => {
      const mockFetch = globalThis.fetch as jest.Mock
      simulator.install()
      simulator.injectFailure('/api/failing', scenarios['serverCrash']!)
      await fetch('/api/healthy')
      expect(mockFetch).toHaveBeenCalledWith('/api/healthy', undefined)
    })

    it('matches URL patterns using includes', async () => {
      simulator.install()
      simulator.injectFailure('/api/tiktok', scenarios['serverCrash']!)
      const response = await fetch('/api/tiktok/generate')
      expect(response.status).toBe(500)
    })

    it('removes failure with removeFailure', async () => {
      const mockFetch = globalThis.fetch as jest.Mock
      simulator.install()
      simulator.injectFailure('/api/test', scenarios['serverCrash']!)
      const response1 = await fetch('/api/test')
      expect(response1.status).toBe(500)
      simulator.removeFailure('/api/test')
      await fetch('/api/test')
      expect(mockFetch).toHaveBeenCalledWith('/api/test', undefined)
    })

    it('clears all failures with clearAll', () => {
      simulator.injectFailure('/api/a', scenarios['serverCrash']!)
      simulator.injectFailure('/api/b', scenarios['rateLimited']!)
      expect(simulator.getActiveScenarios()).toHaveLength(2)
      simulator.clearAll()
      expect(simulator.getActiveScenarios()).toHaveLength(0)
    })
  })

  describe('failure count', () => {
    it('auto-recovers after specified failure count', async () => {
      const mockFetch = globalThis.fetch as jest.Mock
      simulator.install()
      const limitedFailure: FailureScenario = {
        name: 'Limited',
        description: 'Fails 2 times then recovers',
        failureType: 'server-error',
        statusCode: 500,
        failureCount: 2,
      }
      simulator.injectFailure('/api/limited', limitedFailure)
      const r1 = await fetch('/api/limited')
      expect(r1.status).toBe(500)
      const r2 = await fetch('/api/limited')
      expect(r2.status).toBe(500)
      await fetch('/api/limited')
      expect(mockFetch).toHaveBeenLastCalledWith('/api/limited', undefined)
    })

    it('continues indefinitely with failureCount=-1', async () => {
      simulator.install()
      const permanentFailure: FailureScenario = {
        name: 'Permanent',
        description: 'Never recovers',
        failureType: 'server-error',
        statusCode: 500,
        failureCount: -1,
      }
      simulator.injectFailure('/api/permanent', permanentFailure)
      for (let i = 0; i < 10; i++) {
        const response = await fetch('/api/permanent')
        expect(response.status).toBe(500)
      }
    })
  })

  describe('probability-based failures', () => {
    it('always fails with probability=1', async () => {
      simulator.install()
      const alwaysFail: FailureScenario = {
        name: 'Always Fail',
        description: 'Always fails',
        failureType: 'server-error',
        statusCode: 500,
        probability: 1,
      }
      simulator.injectFailure('/api/flaky', alwaysFail)
      const response = await fetch('/api/flaky')
      expect(response.status).toBe(500)
    })

    it('skips failure when random exceeds probability', async () => {
      simulator.install()
      const originalRandom = Math.random
      Math.random = () => 0.99
      const lowProbScenario: FailureScenario = {
        name: 'Unlikely',
        description: 'Very low probability',
        failureType: 'server-error',
        statusCode: 500,
        probability: 0.01,
      }
      simulator.injectFailure('/api/flaky', lowProbScenario)
      const response = await fetch('/api/flaky')
      expect(response.status).toBe(200)
      Math.random = originalRandom
    })
  })

  describe('network conditions', () => {
    it('simulates offline mode', async () => {
      simulator.install()
      simulator.setNetworkCondition(networkConditions['offline']!)
      await expect(fetch('/api/test')).rejects.toThrow(TypeError)
    })

    it('good network passes through normally', async () => {
      const mockFetch = globalThis.fetch as jest.Mock
      simulator.install()
      simulator.setNetworkCondition(networkConditions['good']!)
      await fetch('/api/test')
      expect(mockFetch).toHaveBeenCalledWith('/api/test', undefined)
    })

    it('resets network condition on clearAll', () => {
      simulator.setNetworkCondition(networkConditions['offline']!)
      simulator.clearAll()
      expect(simulator.getActiveScenarios()).toHaveLength(0)
    })
  })

  describe('getActiveScenarios', () => {
    it('returns all active scenario info', () => {
      simulator.injectFailure('/api/a', scenarios['serverCrash']!)
      simulator.injectFailure('/api/b', scenarios['rateLimited']!)
      const active = simulator.getActiveScenarios()
      expect(active).toHaveLength(2)
      expect(active[0]).toMatchObject({
        pattern: '/api/a',
        scenario: scenarios['serverCrash'],
      })
      expect(active[1]).toMatchObject({
        pattern: '/api/b',
        scenario: scenarios['rateLimited'],
      })
    })

    it('tracks remaining failure count', async () => {
      simulator.install()
      const limitedScenario: FailureScenario = {
        name: 'Limited',
        description: 'Fails 3 times',
        failureType: 'server-error',
        statusCode: 500,
        failureCount: 3,
      }
      simulator.injectFailure('/api/test', limitedScenario)
      expect(simulator.getActiveScenarios()[0]?.remaining).toBe(3)
      await fetch('/api/test')
      expect(simulator.getActiveScenarios()[0]?.remaining).toBe(2)
      await fetch('/api/test')
      expect(simulator.getActiveScenarios()[0]?.remaining).toBe(1)
    })
  })
})

describe('scenarios', () => {
  it('defines all expected scenario presets', () => {
    expect(scenarios['networkFailure']).toBeDefined()
    expect(scenarios['slowResponse']).toBeDefined()
    expect(scenarios['serverCrash']).toBeDefined()
    expect(scenarios['rateLimited']).toBeDefined()
    expect(scenarios['intermittentFailure']).toBeDefined()
    expect(scenarios['circuitBreakerTrip']).toBeDefined()
    expect(scenarios['serviceUnavailable']).toBeDefined()
  })

  it('serverCrash has status 500', () => {
    expect(scenarios['serverCrash']?.statusCode).toBe(500)
  })

  it('rateLimited has status 429', () => {
    expect(scenarios['rateLimited']?.statusCode).toBe(429)
  })

  it('intermittentFailure has 50% probability', () => {
    expect(scenarios['intermittentFailure']?.probability).toBe(0.5)
  })

  it('circuitBreakerTrip has failureCount of 5', () => {
    expect(scenarios['circuitBreakerTrip']?.failureCount).toBe(5)
  })
})

describe('networkConditions', () => {
  it('defines expected condition presets', () => {
    expect(networkConditions['good']).toBeDefined()
    expect(networkConditions['slow3G']).toBeDefined()
    expect(networkConditions['fastLoss']).toBeDefined()
    expect(networkConditions['offline']).toBeDefined()
  })

  it('good has minimal latency, no loss, not offline', () => {
    expect(networkConditions['good']?.latencyMs).toBe(50)
    expect(networkConditions['good']?.packetLoss).toBe(0)
    expect(networkConditions['good']?.offline).toBe(false)
  })

  it('offline is fully offline', () => {
    expect(networkConditions['offline']?.offline).toBe(true)
    expect(networkConditions['offline']?.packetLoss).toBe(1)
  })

  it('slow3G has high latency', () => {
    expect(networkConditions['slow3G']?.latencyMs).toBe(2000)
  })
})

describe('withFailureInjection (server-side)', () => {
  beforeEach(() => {
    clearServerFailures()
  })

  it('passes through when no failures injected', async () => {
    const handler = jest.fn().mockResolvedValue({ status: 200, body: 'ok' })
    const wrapped = withFailureInjection(handler)
    const mockReq = { url: 'http://localhost:3000/api/test' } as any
    await wrapped(mockReq)
    expect(handler).toHaveBeenCalledWith(mockReq, undefined)
  })

  it('returns error when failure matches route', async () => {
    const { NextResponse } = require('next/server')
    const handler = jest.fn()
    const wrapped = withFailureInjection(handler)
    injectServerFailure('/api/test', scenarios['serverCrash']!)
    const mockReq = { url: 'http://localhost:3000/api/test' } as any
    await wrapped(mockReq)
    expect(handler).not.toHaveBeenCalled()
    expect(NextResponse.json).toHaveBeenCalledWith(
      expect.objectContaining({
        error: 'server-error',
        simulated: true,
      }),
      { status: 500 }
    )
  })

  it('passes through in production', async () => {
    const originalEnv = process.env.NODE_ENV
    Object.defineProperty(process.env, 'NODE_ENV', {
      value: 'production',
      configurable: true,
    })
    const handler = jest.fn().mockResolvedValue({ status: 200 })
    const wrapped = withFailureInjection(handler)
    injectServerFailure('/api/test', scenarios['serverCrash']!)
    const mockReq = { url: 'http://localhost:3000/api/test' } as any
    await wrapped(mockReq)
    expect(handler).toHaveBeenCalled()
    Object.defineProperty(process.env, 'NODE_ENV', {
      value: originalEnv,
      configurable: true,
    })
  })
})
