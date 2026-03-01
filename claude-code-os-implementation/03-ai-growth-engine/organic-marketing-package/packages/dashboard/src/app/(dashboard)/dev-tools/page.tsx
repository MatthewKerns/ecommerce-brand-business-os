'use client'

/**
 * Dev Tools - Error Simulation & Chaos Engineering Dashboard
 *
 * Development-only page providing controls for:
 * - Error/failure scenario injection (interactive fetch interceptor)
 * - Network condition simulation
 * - Circuit breaker state inspection and control
 * - Endpoint testing
 * - Cache manipulation (stats, clear)
 * - Offline manager queue inspection
 *
 * @route /dev-tools
 */

import { useCallback, useEffect, useState } from 'react'
import { Wrench, Zap, Wifi, Shield, RotateCcw, Database, WifiOff, Bug } from 'lucide-react'
import {
  CircuitState,
  getCircuitBreaker,
  serviceBreakers,
} from '@/lib/resilience'
import { getCacheManager, type CacheStats } from '@/lib/resilience/cache-manager'
import { getOfflineManager, type QueuedAction } from '@/lib/resilience/offline-manager'
import {
  ErrorSimulator,
  scenarios,
  networkConditions,
  type FailureScenario,
  type NetworkCondition,
} from '../../../../tests/utils/error-simulator'

// Only render in development
const IS_DEV = process.env.NODE_ENV === 'development'

// Shared simulator singleton for the page
const simulator = new ErrorSimulator()

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface BreakerInfo {
  name: string
  state: CircuitState
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function getServiceBreakerStates(): BreakerInfo[] {
  const names = ['tiktok-api', 'video-generation', 'metrics-api', 'email-service', 'blog-api']
  serviceBreakers.tiktok()
  serviceBreakers.videoGeneration()
  serviceBreakers.metrics()
  serviceBreakers.email()
  serviceBreakers.blog()

  return names.map((name) => ({
    name,
    state: getCircuitBreaker(name).getState(),
  }))
}

function stateColor(state: CircuitState): string {
  switch (state) {
    case CircuitState.CLOSED:
      return 'bg-green-100 text-green-800'
    case CircuitState.OPEN:
      return 'bg-red-100 text-red-800'
    case CircuitState.HALF_OPEN:
      return 'bg-yellow-100 text-yellow-800'
  }
}

function Badge({ label, variant }: { label: string; variant: 'green' | 'red' | 'amber' | 'blue' | 'slate' }) {
  const colors: Record<string, string> = {
    green: 'bg-green-100 text-green-700',
    red: 'bg-red-100 text-red-700',
    amber: 'bg-amber-100 text-amber-700',
    blue: 'bg-blue-100 text-blue-700',
    slate: 'bg-slate-100 text-slate-600',
  }
  return (
    <span className={`inline-block rounded-full px-2.5 py-0.5 text-xs font-medium ${colors[variant]}`}>
      {label}
    </span>
  )
}

function StatBox({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded border border-slate-100 bg-slate-50 px-3 py-2">
      <p className="text-xs text-slate-400">{label}</p>
      <p className="text-sm font-semibold text-slate-800">{value}</p>
    </div>
  )
}

// ---------------------------------------------------------------------------
// Error Injection Panel
// ---------------------------------------------------------------------------

function ErrorInjectionPanel() {
  const [urlPattern, setUrlPattern] = useState('/api/')
  const [selectedScenario, setSelectedScenario] = useState<string>('networkFailure')
  const [active, setActive] = useState<Array<{ pattern: string; scenario: FailureScenario; remaining: number }>>([])
  const [intercepting, setIntercepting] = useState(false)

  const refreshActive = useCallback(() => {
    setActive(simulator.getActiveScenarios())
  }, [])

  const handleInject = () => {
    const scenario = scenarios[selectedScenario]
    if (!scenario || !urlPattern.trim()) return
    simulator.injectFailure(urlPattern.trim(), scenario)
    refreshActive()
  }

  const handleRemove = (pattern: string) => {
    simulator.removeFailure(pattern)
    refreshActive()
  }

  const handleClearAll = () => {
    simulator.clearAll()
    refreshActive()
  }

  const toggleInterceptor = () => {
    if (intercepting) {
      simulator.uninstall()
      setIntercepting(false)
    } else {
      simulator.install()
      setIntercepting(true)
    }
  }

  return (
    <div className="rounded-lg border border-slate-200 bg-white p-6">
      <div className="mb-4 flex items-center gap-2">
        <Bug className="h-5 w-5 text-slate-600" />
        <h2 className="text-lg font-semibold text-slate-900">Failure Injection</h2>
      </div>
      <p className="mb-4 text-sm text-slate-600">
        Inject failure scenarios into fetch requests for testing error handling.
      </p>

      {/* Interceptor toggle */}
      <div className="mb-4 flex items-center gap-3">
        <button
          onClick={toggleInterceptor}
          className={`rounded-md px-3 py-1.5 text-sm font-medium ${
            intercepting
              ? 'bg-red-600 text-white hover:bg-red-700'
              : 'bg-blue-600 text-white hover:bg-blue-700'
          }`}
        >
          {intercepting ? 'Disable Interceptor' : 'Enable Interceptor'}
        </button>
        <Badge
          label={intercepting ? 'ACTIVE' : 'INACTIVE'}
          variant={intercepting ? 'red' : 'slate'}
        />
      </div>

      {/* Scenario selection */}
      <div className="mb-4 flex flex-wrap gap-2">
        <input
          type="text"
          value={urlPattern}
          onChange={(e) => setUrlPattern(e.target.value)}
          placeholder="URL pattern (e.g. /api/metrics)"
          className="w-56 rounded border border-slate-300 px-3 py-1.5 text-sm"
        />
        <select
          value={selectedScenario}
          onChange={(e) => setSelectedScenario(e.target.value)}
          className="rounded border border-slate-300 px-3 py-1.5 text-sm"
        >
          {Object.entries(scenarios).map(([key, s]) => (
            <option key={key} value={key}>
              {s.name}
            </option>
          ))}
        </select>
        <button
          onClick={handleInject}
          className="rounded-md bg-amber-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-amber-700"
        >
          Inject
        </button>
        <button
          onClick={handleClearAll}
          className="rounded-md border border-slate-300 px-3 py-1.5 text-sm text-slate-700 hover:bg-slate-50"
        >
          Clear All
        </button>
      </div>

      {/* Active scenarios list */}
      {active.length > 0 && (
        <div className="space-y-2">
          <p className="text-xs font-medium uppercase text-slate-400">Active Scenarios</p>
          {active.map((a) => (
            <div
              key={a.pattern}
              className="flex items-center justify-between rounded-md border border-slate-200 bg-slate-50 px-3 py-2 text-sm"
            >
              <div>
                <span className="font-medium">{a.scenario.name}</span>
                <span className="ml-2 text-slate-400">on {a.pattern}</span>
                {a.remaining >= 0 && (
                  <span className="ml-2 text-xs text-slate-400">
                    ({a.remaining} remaining)
                  </span>
                )}
              </div>
              <button
                onClick={() => handleRemove(a.pattern)}
                className="text-xs text-red-500 hover:text-red-700"
              >
                Remove
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

// ---------------------------------------------------------------------------
// Network Conditions Panel
// ---------------------------------------------------------------------------

function NetworkConditionsPanel() {
  const [activeCondition, setActiveCondition] = useState<string>('good')

  const handleSelect = (key: string) => {
    const condition = networkConditions[key] as NetworkCondition | undefined
    if (!condition) return
    simulator.setNetworkCondition(condition)
    setActiveCondition(key)
  }

  return (
    <div className="rounded-lg border border-slate-200 bg-white p-6">
      <div className="mb-4 flex items-center gap-2">
        <Wifi className="h-5 w-5 text-slate-600" />
        <h2 className="text-lg font-semibold text-slate-900">Network Simulation</h2>
      </div>
      <p className="mb-4 text-sm text-slate-600">
        Simulate different network environments. Requires the fetch interceptor to be active.
      </p>
      <div className="flex flex-wrap gap-2">
        {Object.entries(networkConditions).map(([key, cond]) => (
          <button
            key={key}
            onClick={() => handleSelect(key)}
            className={`rounded-md px-3 py-1.5 text-sm font-medium ${
              activeCondition === key
                ? 'bg-blue-600 text-white'
                : 'border border-slate-300 text-slate-700 hover:bg-slate-50'
            }`}
          >
            {key}
            <span className="ml-1 text-xs opacity-70">
              {cond.offline
                ? '(offline)'
                : cond.latencyMs > 0
                  ? `(${cond.latencyMs}ms)`
                  : ''}
            </span>
          </button>
        ))}
      </div>
    </div>
  )
}

// ---------------------------------------------------------------------------
// Circuit Breaker Panel
// ---------------------------------------------------------------------------

function CircuitBreakerPanel() {
  const [breakers, setBreakers] = useState<BreakerInfo[]>(getServiceBreakerStates)

  function refreshBreakers() {
    setBreakers(getServiceBreakerStates())
  }

  function resetBreaker(name: string) {
    getCircuitBreaker(name).reset()
    refreshBreakers()
  }

  function resetAllBreakers() {
    breakers.forEach((b) => getCircuitBreaker(b.name).reset())
    refreshBreakers()
  }

  function tripBreaker(name: string) {
    const breaker = getCircuitBreaker(name)
    const trip = async () => {
      for (let i = 0; i < 10; i++) {
        try {
          await breaker.exec(() => Promise.reject(new Error('Simulated failure')))
        } catch {
          // expected
        }
      }
    }
    trip().then(refreshBreakers)
  }

  useEffect(() => {
    const id = setInterval(refreshBreakers, 3000)
    return () => clearInterval(id)
  }, [])

  return (
    <div className="rounded-lg border border-slate-200 bg-white p-6">
      <div className="mb-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Shield className="h-5 w-5 text-slate-600" />
          <h2 className="text-lg font-semibold text-slate-900">Circuit Breakers</h2>
        </div>
        <div className="flex gap-2">
          <button
            onClick={refreshBreakers}
            className="rounded-md border border-slate-300 px-3 py-1.5 text-sm text-slate-700 hover:bg-slate-50"
          >
            Refresh
          </button>
          <button
            onClick={resetAllBreakers}
            className="rounded-md bg-slate-900 px-3 py-1.5 text-sm text-white hover:bg-slate-800"
          >
            Reset All
          </button>
        </div>
      </div>
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {breakers.map((b) => (
          <div
            key={b.name}
            className="flex items-center justify-between rounded-md border border-slate-200 p-3"
          >
            <div>
              <p className="text-sm font-medium text-slate-900">{b.name}</p>
              <span
                className={`mt-1 inline-block rounded-full px-2 py-0.5 text-xs font-medium ${stateColor(b.state)}`}
              >
                {b.state}
              </span>
            </div>
            <div className="flex gap-1">
              <button
                onClick={() => tripBreaker(b.name)}
                className="rounded p-1 text-red-400 hover:bg-red-50 hover:text-red-600"
                title="Force trip to OPEN"
              >
                <Zap className="h-4 w-4" />
              </button>
              {b.state !== CircuitState.CLOSED && (
                <button
                  onClick={() => resetBreaker(b.name)}
                  className="rounded p-1 text-slate-400 hover:bg-slate-100 hover:text-slate-600"
                  title="Reset to CLOSED"
                >
                  <RotateCcw className="h-4 w-4" />
                </button>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

// ---------------------------------------------------------------------------
// Endpoint Tester Panel
// ---------------------------------------------------------------------------

function EndpointTesterPanel() {
  const [testResult, setTestResult] = useState<string | null>(null)
  const [testLoading, setTestLoading] = useState(false)

  async function testEndpoint(url: string, method: string) {
    setTestLoading(true)
    setTestResult(null)
    const start = performance.now()
    try {
      const res = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        ...(method === 'POST' ? { body: JSON.stringify({}) } : {}),
      })
      const elapsed = Math.round(performance.now() - start)
      const body = await res.text()
      setTestResult(`${res.status} ${res.statusText} (${elapsed}ms)\n${body.substring(0, 500)}`)
    } catch (err) {
      const elapsed = Math.round(performance.now() - start)
      setTestResult(`ERROR (${elapsed}ms): ${err instanceof Error ? err.message : 'Unknown error'}`)
    } finally {
      setTestLoading(false)
    }
  }

  return (
    <div className="rounded-lg border border-slate-200 bg-white p-6">
      <div className="mb-4 flex items-center gap-2">
        <Zap className="h-5 w-5 text-slate-600" />
        <h2 className="text-lg font-semibold text-slate-900">Endpoint Tester</h2>
      </div>
      <p className="mb-4 text-sm text-slate-600">
        Fire requests to test error handling, timeouts, and circuit breaker behavior.
      </p>
      <div className="flex flex-wrap gap-2">
        <button
          onClick={() => testEndpoint('/api/metrics', 'GET')}
          disabled={testLoading}
          className="rounded-md border border-slate-300 px-3 py-1.5 text-sm text-slate-700 hover:bg-slate-50 disabled:opacity-50"
        >
          GET /api/metrics
        </button>
        <button
          onClick={() => testEndpoint('/api/health', 'GET')}
          disabled={testLoading}
          className="rounded-md border border-slate-300 px-3 py-1.5 text-sm text-slate-700 hover:bg-slate-50 disabled:opacity-50"
        >
          GET /api/health
        </button>
        <button
          onClick={() => testEndpoint('/api/tiktok/generate', 'POST')}
          disabled={testLoading}
          className="rounded-md border border-slate-300 px-3 py-1.5 text-sm text-slate-700 hover:bg-slate-50 disabled:opacity-50"
        >
          POST /api/tiktok/generate
        </button>
        <button
          onClick={() => testEndpoint('/api/tiktok/generate-video', 'POST')}
          disabled={testLoading}
          className="rounded-md border border-slate-300 px-3 py-1.5 text-sm text-slate-700 hover:bg-slate-50 disabled:opacity-50"
        >
          POST /api/tiktok/generate-video
        </button>
      </div>
      {testResult && (
        <pre className="mt-4 overflow-auto rounded-md bg-slate-50 p-4 text-xs text-slate-700">
          {testResult}
        </pre>
      )}
    </div>
  )
}

// ---------------------------------------------------------------------------
// Cache Panel
// ---------------------------------------------------------------------------

function CachePanel() {
  const [stats, setStats] = useState<CacheStats | null>(null)

  const refresh = useCallback(() => {
    setStats(getCacheManager().getStats())
  }, [])

  useEffect(() => {
    refresh()
  }, [refresh])

  const handleClear = async () => {
    await getCacheManager().clear()
    refresh()
  }

  return (
    <div className="rounded-lg border border-slate-200 bg-white p-6">
      <div className="mb-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Database className="h-5 w-5 text-slate-600" />
          <h2 className="text-lg font-semibold text-slate-900">Cache Management</h2>
        </div>
        <div className="flex gap-2">
          <button
            onClick={refresh}
            className="rounded-md border border-slate-300 px-3 py-1.5 text-sm text-slate-700 hover:bg-slate-50"
          >
            Refresh
          </button>
          <button
            onClick={handleClear}
            className="rounded-md bg-red-600 px-3 py-1.5 text-sm text-white hover:bg-red-700"
          >
            Clear All
          </button>
        </div>
      </div>
      {stats && (
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
          <StatBox label="Memory entries" value={`${stats.memorySize} / ${stats.memoryMaxSize}`} />
          <StatBox label="localStorage keys" value={String(stats.localStorageKeys)} />
          <StatBox label="Hits" value={String(stats.hits)} />
          <StatBox label="Misses" value={String(stats.misses)} />
          <StatBox label="Stale hits" value={String(stats.staleHits)} />
          <StatBox
            label="Hit rate"
            value={
              stats.hits + stats.misses > 0
                ? `${Math.round((stats.hits / (stats.hits + stats.misses)) * 100)}%`
                : 'N/A'
            }
          />
        </div>
      )}
    </div>
  )
}

// ---------------------------------------------------------------------------
// Offline Queue Panel
// ---------------------------------------------------------------------------

function OfflineQueuePanel() {
  const [queue, setQueue] = useState<ReadonlyArray<QueuedAction>>([])
  const [status, setStatus] = useState<string>('')

  const refresh = useCallback(() => {
    const mgr = getOfflineManager()
    setQueue(mgr.getQueue())
    setStatus(mgr.getStatus())
  }, [])

  useEffect(() => {
    refresh()
    const unsub = getOfflineManager().onQueueChange(() => refresh())
    const unsubStatus = getOfflineManager().onStatusChange(() => refresh())
    return () => {
      unsub()
      unsubStatus()
    }
  }, [refresh])

  const handleSync = async () => {
    await getOfflineManager().syncNow()
    refresh()
  }

  const handleClear = () => {
    getOfflineManager().clearQueue()
    refresh()
  }

  return (
    <div className="rounded-lg border border-slate-200 bg-white p-6">
      <div className="mb-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <WifiOff className="h-5 w-5 text-slate-600" />
          <h2 className="text-lg font-semibold text-slate-900">Offline Queue</h2>
        </div>
        <div className="flex items-center gap-3">
          <Badge
            label={status.toUpperCase() || 'UNKNOWN'}
            variant={status === 'online' ? 'green' : status === 'offline' ? 'red' : 'blue'}
          />
          <span className="text-sm text-slate-500">{queue.length} pending</span>
        </div>
      </div>
      <div className="mb-4 flex gap-2">
        <button
          onClick={handleSync}
          className="rounded-md bg-blue-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-blue-700"
        >
          Sync Now
        </button>
        <button
          onClick={handleClear}
          className="rounded-md bg-red-100 px-3 py-1.5 text-sm font-medium text-red-600 hover:bg-red-200"
        >
          Clear Queue
        </button>
        <button
          onClick={refresh}
          className="rounded-md border border-slate-300 px-3 py-1.5 text-sm text-slate-700 hover:bg-slate-50"
        >
          Refresh
        </button>
      </div>
      {queue.length > 0 ? (
        <div className="space-y-2">
          {queue.map((action) => (
            <div
              key={action.id}
              className="flex items-center justify-between rounded-md border border-slate-200 bg-slate-50 px-3 py-2 text-sm"
            >
              <div>
                <span className="font-mono text-xs font-bold text-blue-600">{action.method}</span>
                <span className="ml-2">{action.url}</span>
                {action.description && (
                  <span className="ml-2 text-slate-400">- {action.description}</span>
                )}
              </div>
              <div className="flex items-center gap-2 text-xs text-slate-400">
                <span>Retries: {action.retryCount}/{action.maxRetries}</span>
                <span>{new Date(action.timestamp).toLocaleTimeString()}</span>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <p className="text-sm text-slate-400">No pending actions in queue.</p>
      )}
    </div>
  )
}

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------

export default function DevToolsPage() {
  if (!IS_DEV) {
    return (
      <div className="flex items-center justify-center py-24">
        <p className="text-slate-500">Dev tools are only available in development mode.</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center gap-3">
        <div className="rounded-lg bg-amber-100 p-3">
          <Wrench className="h-6 w-6 text-amber-700" />
        </div>
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Dev Tools</h1>
          <p className="text-sm text-slate-600">
            Error simulation, chaos engineering, and resilience controls
          </p>
        </div>
      </div>

      {/* Top row: Failure Injection + Network */}
      <div className="grid gap-6 lg:grid-cols-2">
        <ErrorInjectionPanel />
        <NetworkConditionsPanel />
      </div>

      {/* Middle row: Circuit Breakers + Endpoint Tester */}
      <div className="grid gap-6 lg:grid-cols-2">
        <CircuitBreakerPanel />
        <EndpointTesterPanel />
      </div>

      {/* Bottom row: Cache + Offline Queue */}
      <div className="grid gap-6 lg:grid-cols-2">
        <CachePanel />
        <OfflineQueuePanel />
      </div>
    </div>
  )
}
