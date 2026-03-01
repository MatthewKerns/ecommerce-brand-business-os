export {
  OfflineManager,
  getOfflineManager,
  resetOfflineManager,
} from './offline-manager';

export type {
  ConnectionStatus,
  HttpMethod,
  OfflineManagerOptions,
  QueuedAction,
  SyncResult,
} from './offline-manager';

export { useOffline } from './use-offline';
export type { UseOfflineReturn } from './use-offline';

export { OfflineIndicator } from './OfflineIndicator';

export { CacheManager, getCacheManager, resetCacheManager } from './cache-manager';
export type {
  CacheEntry,
  CacheLayer,
  CacheManagerOptions,
  CacheStats,
  EvictionPolicy,
  InvalidationStrategy,
} from './cache-manager';

export { useCache } from './use-cache';
export type { UseCacheReturn } from './use-cache';

export {
  CircuitBreaker,
  CircuitOpenError,
  CircuitState,
  getCircuitBreaker,
  serviceBreakers,
} from './circuit-breaker';
export type { CircuitBreakerOptions } from './circuit-breaker';

export {
  withRetry,
  calculateBackoff,
  isRetryableError,
  RetryBudget,
  generateIdempotencyKey,
  deduplicateRequest,
  retryPolicies,
} from './retry-strategy';
export type { RetryPolicy, RetryOptions } from './retry-strategy';
