'use client'

import { useEffect, useState, useCallback } from 'react'
import {
  AlertTriangle,
  Activity,
  Shield,
  RefreshCw,
  CheckCircle,
  XCircle,
  Clock,
  Zap,
  Database,
  ArrowUpRight,
  ArrowDownRight,
} from 'lucide-react'
import type { MonitoringSnapshot, CircuitBreakerState, ServiceHealthMetric } from '@/lib/monitoring/error-metrics'

const REFRESH_INTERVAL_MS = 10_000

export default function MonitoringPage() {
  const [snapshot, setSnapshot] = useState<MonitoringSnapshot | null>(null)
  const [loading, setLoading] = useState(true)
  const [lastRefresh, setLastRefresh] = useState<Date | null>(null)

  const fetchSnapshot = useCallback(async () => {
    try {
      const res = await fetch('/api/monitoring')
      if (res.ok) {
        const data: MonitoringSnapshot = await res.json()
        setSnapshot(data)
        setLastRefresh(new Date())
      }
    } catch {
      // Silently fail - dashboard will show stale data
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchSnapshot()
    const interval = setInterval(fetchSnapshot, REFRESH_INTERVAL_MS)
    return () => clearInterval(interval)
  }, [fetchSnapshot])

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="rounded-lg bg-orange-100 p-3">
            <Activity className="h-6 w-6 text-orange-700" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-slate-900">Error Monitoring</h1>
            <p className="text-sm text-slate-600">
              Real-time error tracking, service health, and alert status
            </p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          {lastRefresh && (
            <span className="text-xs text-slate-500">
              Updated {lastRefresh.toLocaleTimeString()}
            </span>
          )}
          <button
            onClick={fetchSnapshot}
            className="flex items-center gap-1.5 rounded-md bg-slate-100 px-3 py-1.5 text-sm font-medium text-slate-700 transition-colors hover:bg-slate-200"
          >
            <RefreshCw className="h-3.5 w-3.5" />
            Refresh
          </button>
        </div>
      </div>

      {loading && !snapshot ? (
        <LoadingState />
      ) : snapshot ? (
        <>
          {/* Top-level KPIs */}
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <KPICard
              label="Error Rate"
              value={`${snapshot.errorRate.current}/min`}
              icon={AlertTriangle}
              trend={snapshot.errorRate.current > 5 ? 'up' : 'down'}
              trendLabel={snapshot.errorRate.current > 5 ? 'Elevated' : 'Normal'}
              color={snapshot.errorRate.current > 10 ? 'red' : snapshot.errorRate.current > 5 ? 'amber' : 'green'}
            />
            <KPICard
              label="Services Healthy"
              value={`${snapshot.serviceHealth.filter((s) => s.status === 'healthy').length}/${snapshot.serviceHealth.length}`}
              icon={Shield}
              trend={snapshot.serviceHealth.every((s) => s.status === 'healthy') ? 'down' : 'up'}
              trendLabel={snapshot.serviceHealth.every((s) => s.status === 'healthy') ? 'All Clear' : 'Issues'}
              color={snapshot.serviceHealth.every((s) => s.status === 'healthy') ? 'green' : 'amber'}
            />
            <KPICard
              label="Circuit Breakers"
              value={`${snapshot.circuitBreakers.filter((cb) => cb.state === 'open').length} Open`}
              icon={Zap}
              trend={snapshot.circuitBreakers.some((cb) => cb.state === 'open') ? 'up' : 'down'}
              trendLabel={snapshot.circuitBreakers.some((cb) => cb.state === 'open') ? 'Active' : 'All Closed'}
              color={snapshot.circuitBreakers.some((cb) => cb.state === 'open') ? 'red' : 'green'}
            />
            <KPICard
              label="Avg Recovery"
              value={snapshot.recoveryMetrics.avgRecoveryTimeMs > 0 ? `${snapshot.recoveryMetrics.avgRecoveryTimeMs}ms` : 'N/A'}
              icon={Clock}
              trend="down"
              trendLabel={`${snapshot.recoveryMetrics.successfulRetries} retries`}
              color="slate"
            />
          </div>

          {/* Error Rate Timeline */}
          <div className="rounded-lg border border-slate-200 bg-white p-6">
            <h2 className="mb-4 text-lg font-semibold text-slate-900">Error Rate Timeline</h2>
            <ErrorRateChart buckets={snapshot.errorRate.buckets} />
          </div>

          {/* Service Health + Circuit Breakers */}
          <div className="grid gap-6 lg:grid-cols-2">
            <div className="rounded-lg border border-slate-200 bg-white p-6">
              <h2 className="mb-4 text-lg font-semibold text-slate-900">Service Health</h2>
              <ServiceHealthList services={snapshot.serviceHealth} />
            </div>
            <div className="rounded-lg border border-slate-200 bg-white p-6">
              <h2 className="mb-4 text-lg font-semibold text-slate-900">Circuit Breakers</h2>
              <CircuitBreakerList breakers={snapshot.circuitBreakers} />
            </div>
          </div>

          {/* Top Errors + Cache Metrics */}
          <div className="grid gap-6 lg:grid-cols-2">
            <div className="rounded-lg border border-slate-200 bg-white p-6">
              <h2 className="mb-4 text-lg font-semibold text-slate-900">Top Errors</h2>
              {snapshot.topErrors.length === 0 ? (
                <p className="py-8 text-center text-sm text-slate-500">No errors recorded yet</p>
              ) : (
                <div className="space-y-2">
                  {snapshot.topErrors.map((err) => (
                    <div
                      key={`${err.code}:${err.serviceName ?? ''}`}
                      className="flex items-center justify-between rounded-md bg-slate-50 px-3 py-2"
                    >
                      <div>
                        <p className="text-sm font-medium text-slate-900">{err.code}</p>
                        <p className="text-xs text-slate-500">
                          {err.category}{err.serviceName ? ` - ${err.serviceName}` : ''}
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="text-sm font-semibold text-slate-900">{err.count}</p>
                        <p className="text-xs text-slate-500">
                          Last: {new Date(err.lastSeen).toLocaleTimeString()}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
            <div className="rounded-lg border border-slate-200 bg-white p-6">
              <h2 className="mb-4 text-lg font-semibold text-slate-900">Cache Metrics</h2>
              <div className="grid grid-cols-2 gap-4">
                <MetricTile label="Hit Rate" value={`${(snapshot.cacheMetrics.hitRate * 100).toFixed(1)}%`} icon={Database} />
                <MetricTile label="Miss Rate" value={`${(snapshot.cacheMetrics.missRate * 100).toFixed(1)}%`} icon={Database} />
                <MetricTile label="Total Requests" value={String(snapshot.cacheMetrics.totalRequests)} icon={Activity} />
                <MetricTile label="Evictions" value={String(snapshot.cacheMetrics.evictions)} icon={RefreshCw} />
              </div>
            </div>
          </div>

          {/* Recovery Metrics */}
          <div className="rounded-lg border border-slate-200 bg-white p-6">
            <h2 className="mb-4 text-lg font-semibold text-slate-900">Recovery Metrics</h2>
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
              <MetricTile label="Total Recoveries" value={String(snapshot.recoveryMetrics.totalRecoveries)} icon={RefreshCw} />
              <MetricTile label="Avg Recovery Time" value={`${snapshot.recoveryMetrics.avgRecoveryTimeMs}ms`} icon={Clock} />
              <MetricTile label="Successful Retries" value={String(snapshot.recoveryMetrics.successfulRetries)} icon={CheckCircle} />
              <MetricTile label="Failed Retries" value={String(snapshot.recoveryMetrics.failedRetries)} icon={XCircle} />
              <MetricTile label="User-Initiated" value={String(snapshot.recoveryMetrics.userInitiatedRecoveries)} icon={Zap} />
            </div>
          </div>
        </>
      ) : (
        <div className="py-12 text-center text-sm text-slate-500">
          Failed to load monitoring data. Click Refresh to try again.
        </div>
      )}
    </div>
  )
}

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

function LoadingState() {
  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      {[1, 2, 3, 4].map((i) => (
        <div key={i} className="h-28 animate-pulse rounded-lg bg-slate-100" />
      ))}
    </div>
  )
}

function KPICard(props: {
  label: string
  value: string
  icon: React.ComponentType<{ className?: string }>
  trend: 'up' | 'down'
  trendLabel: string
  color: 'green' | 'amber' | 'red' | 'slate'
}) {
  const Icon = props.icon
  const colorMap = {
    green: 'bg-green-100 text-green-700',
    amber: 'bg-amber-100 text-amber-700',
    red: 'bg-red-100 text-red-700',
    slate: 'bg-slate-100 text-slate-700',
  }

  return (
    <div className="rounded-lg border border-slate-200 bg-white p-4">
      <div className="flex items-center justify-between">
        <div className={`rounded-md p-2 ${colorMap[props.color]}`}>
          <Icon className="h-4 w-4" />
        </div>
        <div className="flex items-center gap-1 text-xs text-slate-500">
          {props.trend === 'up' ? (
            <ArrowUpRight className="h-3 w-3 text-red-500" />
          ) : (
            <ArrowDownRight className="h-3 w-3 text-green-500" />
          )}
          {props.trendLabel}
        </div>
      </div>
      <p className="mt-3 text-2xl font-bold text-slate-900">{props.value}</p>
      <p className="text-xs text-slate-500">{props.label}</p>
    </div>
  )
}

function MetricTile(props: {
  label: string
  value: string
  icon: React.ComponentType<{ className?: string }>
}) {
  const Icon = props.icon
  return (
    <div className="rounded-md bg-slate-50 p-3">
      <div className="flex items-center gap-2">
        <Icon className="h-4 w-4 text-slate-400" />
        <p className="text-xs text-slate-500">{props.label}</p>
      </div>
      <p className="mt-1 text-lg font-semibold text-slate-900">{props.value}</p>
    </div>
  )
}

function ServiceHealthList(props: { services: ServiceHealthMetric[] }) {
  const statusBadge = (status: string) => {
    switch (status) {
      case 'healthy':
        return <span className="inline-flex items-center gap-1 rounded-full bg-green-100 px-2 py-0.5 text-xs font-medium text-green-700"><CheckCircle className="h-3 w-3" /> Healthy</span>
      case 'degraded':
        return <span className="inline-flex items-center gap-1 rounded-full bg-amber-100 px-2 py-0.5 text-xs font-medium text-amber-700"><AlertTriangle className="h-3 w-3" /> Degraded</span>
      case 'unhealthy':
        return <span className="inline-flex items-center gap-1 rounded-full bg-red-100 px-2 py-0.5 text-xs font-medium text-red-700"><XCircle className="h-3 w-3" /> Unhealthy</span>
      default:
        return null
    }
  }

  return (
    <div className="space-y-2">
      {props.services.map((svc) => (
        <div key={svc.name} className="flex items-center justify-between rounded-md bg-slate-50 px-3 py-2">
          <div>
            <p className="text-sm font-medium text-slate-900">{svc.name}</p>
            <p className="text-xs text-slate-500">{svc.uptimePercent}% uptime</p>
          </div>
          {statusBadge(svc.status)}
        </div>
      ))}
    </div>
  )
}

function CircuitBreakerList(props: { breakers: CircuitBreakerState[] }) {
  const stateColor = (state: string) => {
    switch (state) {
      case 'closed': return 'bg-green-100 text-green-700'
      case 'half-open': return 'bg-amber-100 text-amber-700'
      case 'open': return 'bg-red-100 text-red-700'
      default: return 'bg-slate-100 text-slate-700'
    }
  }

  if (props.breakers.length === 0) {
    return <p className="py-8 text-center text-sm text-slate-500">No circuit breakers configured</p>
  }

  return (
    <div className="space-y-2">
      {props.breakers.map((cb) => (
        <div key={cb.service} className="flex items-center justify-between rounded-md bg-slate-50 px-3 py-2">
          <div>
            <p className="text-sm font-medium text-slate-900">{cb.service}</p>
            <p className="text-xs text-slate-500">
              {cb.failureCount} failures
              {cb.nextRetryAt ? ` - retry at ${new Date(cb.nextRetryAt).toLocaleTimeString()}` : ''}
            </p>
          </div>
          <span className={`rounded-full px-2 py-0.5 text-xs font-medium capitalize ${stateColor(cb.state)}`}>
            {cb.state}
          </span>
        </div>
      ))}
    </div>
  )
}

function ErrorRateChart(props: { buckets: Array<{ timestamp: string; count: number }> }) {
  if (props.buckets.length === 0) {
    return (
      <div className="flex h-40 items-center justify-center text-sm text-slate-500">
        No error data yet. Errors will appear here as they are recorded.
      </div>
    )
  }

  const maxCount = Math.max(...props.buckets.map((b) => b.count), 1)

  return (
    <div className="flex h-40 items-end gap-1">
      {props.buckets.map((bucket) => {
        const heightPercent = (bucket.count / maxCount) * 100
        const color = bucket.count > 10 ? 'bg-red-400' : bucket.count > 5 ? 'bg-amber-400' : 'bg-green-400'
        return (
          <div
            key={bucket.timestamp}
            className="group relative flex-1"
            title={`${new Date(bucket.timestamp).toLocaleTimeString()}: ${bucket.count} errors`}
          >
            <div
              className={`rounded-t ${color} transition-all`}
              style={{ height: `${Math.max(heightPercent, 2)}%` }}
            />
            <div className="pointer-events-none absolute -top-8 left-1/2 hidden -translate-x-1/2 rounded bg-slate-800 px-2 py-1 text-xs text-white group-hover:block">
              {bucket.count}
            </div>
          </div>
        )
      })}
    </div>
  )
}
