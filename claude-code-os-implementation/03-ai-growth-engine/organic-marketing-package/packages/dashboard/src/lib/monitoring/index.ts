/**
 * Monitoring Module - Barrel Export
 *
 * @example
 * ```ts
 * import { captureError, setUser, getErrorMetricsStore } from '@/lib/monitoring'
 * ```
 */

export {
  initSentry,
  isSentryEnabled,
  captureError,
  setUser,
  clearUser,
  addBreadcrumb,
  startTransaction,
  Sentry,
} from './sentry'
export type { SentryInitOptions } from './sentry'

export { getErrorMetricsStore } from './error-metrics'
export type {
  ErrorMetric,
  ErrorRateBucket,
  CircuitBreakerState,
  MonitoringSnapshot,
  ServiceHealthMetric,
  CacheMetrics,
  RecoveryMetrics,
} from './error-metrics'

export { evaluateAlerts, DEFAULT_ALERT_RULES } from './alerts'
export type {
  AlertSeverity,
  AlertChannel,
  AlertRule,
  AlertCondition,
  AlertEvent,
  ChannelConfig,
} from './alerts'
