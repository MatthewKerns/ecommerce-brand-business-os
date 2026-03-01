/**
 * Error Metrics Collection
 *
 * Client-side error metric aggregation for the monitoring dashboard.
 * Collects error counts, rates, and timing data in-memory and
 * exposes it via an API endpoint for the dashboard to consume.
 */

import { ErrorCategory, ErrorCode } from '@/lib/errors/errorCodes'

export interface ErrorMetric {
  code: ErrorCode
  category: ErrorCategory
  count: number
  firstSeen: string
  lastSeen: string
  serviceName?: string
}

export interface ErrorRateBucket {
  timestamp: string
  count: number
  categories: Partial<Record<ErrorCategory, number>>
}

export interface CircuitBreakerState {
  service: string
  state: 'closed' | 'open' | 'half-open'
  failureCount: number
  lastFailure: string | null
  lastSuccess: string | null
  nextRetryAt: string | null
}

export interface MonitoringSnapshot {
  timestamp: string
  errorRate: {
    current: number
    buckets: ErrorRateBucket[]
  }
  topErrors: ErrorMetric[]
  serviceHealth: ServiceHealthMetric[]
  circuitBreakers: CircuitBreakerState[]
  cacheMetrics: CacheMetrics
  recoveryMetrics: RecoveryMetrics
}

export interface ServiceHealthMetric {
  name: string
  status: 'healthy' | 'degraded' | 'unhealthy'
  responseTimeMs: number
  uptimePercent: number
  errorRate: number
}

export interface CacheMetrics {
  hitRate: number
  missRate: number
  totalRequests: number
  evictions: number
  memoryUsageMb: number
}

export interface RecoveryMetrics {
  totalRecoveries: number
  avgRecoveryTimeMs: number
  successfulRetries: number
  failedRetries: number
  userInitiatedRecoveries: number
}

// ---------------------------------------------------------------------------
// In-memory error store (singleton)
// ---------------------------------------------------------------------------

const ERROR_BUCKET_DURATION_MS = 60_000 // 1 minute per bucket
const MAX_BUCKETS = 60 // Keep 60 minutes of history

class ErrorMetricsStore {
  private errorCounts = new Map<string, ErrorMetric>()
  private rateBuckets: ErrorRateBucket[] = []
  private circuitBreakers = new Map<string, CircuitBreakerState>()
  private recoveries = { total: 0, successRetries: 0, failedRetries: 0, userInitiated: 0, totalRecoveryTimeMs: 0 }

  recordError(code: ErrorCode, category: ErrorCategory, serviceName?: string) {
    const key = `${code}:${serviceName ?? ''}`
    const now = new Date().toISOString()
    const existing = this.errorCounts.get(key)

    if (existing) {
      existing.count++
      existing.lastSeen = now
    } else {
      this.errorCounts.set(key, {
        code,
        category,
        count: 1,
        firstSeen: now,
        lastSeen: now,
        serviceName,
      })
    }

    this.incrementBucket(category)
  }

  recordRecovery(successful: boolean, recoveryTimeMs: number, userInitiated: boolean) {
    this.recoveries.total++
    this.recoveries.totalRecoveryTimeMs += recoveryTimeMs
    if (successful) this.recoveries.successRetries++
    else this.recoveries.failedRetries++
    if (userInitiated) this.recoveries.userInitiated++
  }

  updateCircuitBreaker(service: string, state: CircuitBreakerState['state'], failureCount: number) {
    const now = new Date().toISOString()
    const existing = this.circuitBreakers.get(service)

    this.circuitBreakers.set(service, {
      service,
      state,
      failureCount,
      lastFailure: state !== 'closed' ? now : (existing?.lastFailure ?? null),
      lastSuccess: state === 'closed' ? now : (existing?.lastSuccess ?? null),
      nextRetryAt: state === 'open'
        ? new Date(Date.now() + 30_000).toISOString()
        : null,
    })
  }

  getSnapshot(): MonitoringSnapshot {
    const buckets = this.rateBuckets.slice(-MAX_BUCKETS)
    const recentBuckets = buckets.slice(-5)
    const recentCount = recentBuckets.reduce((sum, b) => sum + b.count, 0)
    const currentRate = recentBuckets.length > 0 ? recentCount / recentBuckets.length : 0

    const topErrors = Array.from(this.errorCounts.values())
      .sort((a, b) => b.count - a.count)
      .slice(0, 10)

    return {
      timestamp: new Date().toISOString(),
      errorRate: {
        current: Math.round(currentRate * 100) / 100,
        buckets,
      },
      topErrors,
      serviceHealth: this.getServiceHealth(),
      circuitBreakers: Array.from(this.circuitBreakers.values()),
      cacheMetrics: this.getCacheMetrics(),
      recoveryMetrics: this.getRecoveryMetrics(),
    }
  }

  private incrementBucket(category: ErrorCategory) {
    const now = new Date()
    const bucketTime = new Date(
      Math.floor(now.getTime() / ERROR_BUCKET_DURATION_MS) * ERROR_BUCKET_DURATION_MS
    ).toISOString()

    let bucket = this.rateBuckets.find((b) => b.timestamp === bucketTime)
    if (!bucket) {
      bucket = { timestamp: bucketTime, count: 0, categories: {} }
      this.rateBuckets.push(bucket)
      // Trim old buckets
      if (this.rateBuckets.length > MAX_BUCKETS) {
        this.rateBuckets = this.rateBuckets.slice(-MAX_BUCKETS)
      }
    }

    bucket.count++
    bucket.categories[category] = (bucket.categories[category] ?? 0) + 1
  }

  private getServiceHealth(): ServiceHealthMetric[] {
    // Default service list - will be populated by actual health checks
    const services = ['TikTok API', 'Blog Engine', 'Email Automation', 'Python Agents', 'Database', 'Cache']
    return services.map((name) => {
      const cb = this.circuitBreakers.get(name)
      const status = cb?.state === 'open' ? 'unhealthy' as const : cb?.state === 'half-open' ? 'degraded' as const : 'healthy' as const
      return {
        name,
        status,
        responseTimeMs: 0, // Populated by health checker
        uptimePercent: status === 'healthy' ? 99.9 : status === 'degraded' ? 95.0 : 0,
        errorRate: cb ? cb.failureCount : 0,
      }
    })
  }

  private getCacheMetrics(): CacheMetrics {
    // Placeholder - will be populated by cache layer integration
    return {
      hitRate: 0,
      missRate: 0,
      totalRequests: 0,
      evictions: 0,
      memoryUsageMb: 0,
    }
  }

  private getRecoveryMetrics(): RecoveryMetrics {
    const { total, successRetries, failedRetries, userInitiated, totalRecoveryTimeMs } = this.recoveries
    return {
      totalRecoveries: total,
      avgRecoveryTimeMs: total > 0 ? Math.round(totalRecoveryTimeMs / total) : 0,
      successfulRetries: successRetries,
      failedRetries,
      userInitiatedRecoveries: userInitiated,
    }
  }
}

// Singleton instance
let storeInstance: ErrorMetricsStore | null = null

export function getErrorMetricsStore(): ErrorMetricsStore {
  if (!storeInstance) {
    storeInstance = new ErrorMetricsStore()
  }
  return storeInstance
}
