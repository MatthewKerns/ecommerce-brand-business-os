/**
 * Offline Manager with Action Queuing
 *
 * Provides offline detection, action queuing, and automatic sync
 * when connectivity is restored. Persists queued actions to localStorage
 * to survive page reloads.
 */

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export type HttpMethod = 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';

export interface QueuedAction {
  id: string;
  url: string;
  method: HttpMethod;
  body?: unknown;
  headers?: Record<string, string>;
  timestamp: number;
  retryCount: number;
  maxRetries: number;
  /** Optional version/etag for conflict detection */
  entityVersion?: string;
  /** Human-readable description for UI display */
  description?: string;
}

export type ConnectionStatus = 'online' | 'offline' | 'syncing';

export type SyncResult =
  | { status: 'success'; action: QueuedAction }
  | { status: 'conflict'; action: QueuedAction; serverVersion?: string }
  | { status: 'error'; action: QueuedAction; error: string };

export interface OfflineManagerOptions {
  /** localStorage key for persisting queue (default: 'offline-action-queue') */
  storageKey?: string;
  /** Maximum number of queued actions (default: 100) */
  maxQueueSize?: number;
  /** Base delay in ms for exponential backoff (default: 1000) */
  baseRetryDelay?: number;
  /** Maximum retry delay cap in ms (default: 30000) */
  maxRetryDelay?: number;
  /** Default max retries per action (default: 5) */
  defaultMaxRetries?: number;
  /** Whether to auto-sync when coming back online (default: true) */
  autoSync?: boolean;
}

type Listener<T> = (value: T) => void;

// ---------------------------------------------------------------------------
// OfflineManager
// ---------------------------------------------------------------------------

export class OfflineManager {
  private queue: QueuedAction[] = [];
  private status: ConnectionStatus = 'online';
  private statusListeners: Set<Listener<ConnectionStatus>> = new Set();
  private queueListeners: Set<Listener<QueuedAction[]>> = new Set();
  private syncResultListeners: Set<Listener<SyncResult[]>> = new Set();
  private isSyncing = false;
  private disposed = false;

  private readonly storageKey: string;
  private readonly maxQueueSize: number;
  private readonly defaultMaxRetries: number;
  private readonly autoSync: boolean;

  // Bound handlers for cleanup
  private readonly handleOnline: () => void;
  private readonly handleOffline: () => void;

  constructor(options: OfflineManagerOptions = {}) {
    this.storageKey = options.storageKey ?? 'offline-action-queue';
    this.maxQueueSize = options.maxQueueSize ?? 100;
    this.defaultMaxRetries = options.defaultMaxRetries ?? 5;
    this.autoSync = options.autoSync ?? true;

    this.handleOnline = this.onOnline.bind(this);
    this.handleOffline = this.onOffline.bind(this);

    this.restoreQueue();
    this.initNetworkListeners();
  }

  // -------------------------------------------------------------------------
  // Public API
  // -------------------------------------------------------------------------

  /** Current connection status */
  getStatus(): ConnectionStatus {
    return this.status;
  }

  /** Whether the browser reports being online */
  isOnline(): boolean {
    return typeof navigator !== 'undefined' ? navigator.onLine : true;
  }

  /** Current queued actions (read-only copy) */
  getQueue(): ReadonlyArray<QueuedAction> {
    return [...this.queue];
  }

  /** Number of pending actions */
  get pendingCount(): number {
    return this.queue.length;
  }

  /**
   * Enqueue an action to be executed when online.
   * If currently online, the action is executed immediately.
   * Returns the queued action id.
   */
  async enqueue(
    action: Omit<QueuedAction, 'id' | 'timestamp' | 'retryCount' | 'maxRetries'> & {
      maxRetries?: number;
    }
  ): Promise<string> {
    const id = this.generateId();
    const queuedAction: QueuedAction = {
      ...action,
      id,
      timestamp: Date.now(),
      retryCount: 0,
      maxRetries: action.maxRetries ?? this.defaultMaxRetries,
    };

    // If online, try to execute immediately
    if (this.isOnline() && !this.isSyncing) {
      const result = await this.executeAction(queuedAction);
      if (result.status === 'success') {
        return id;
      }
      // If immediate execution fails, fall through to queue it
    }

    this.addToQueue(queuedAction);
    return id;
  }

  /** Remove a specific action from the queue */
  removeFromQueue(actionId: string): boolean {
    const index = this.queue.findIndex((a) => a.id === actionId);
    if (index === -1) return false;
    this.queue.splice(index, 1);
    this.persistQueue();
    this.notifyQueueListeners();
    return true;
  }

  /** Clear the entire queue */
  clearQueue(): void {
    this.queue = [];
    this.persistQueue();
    this.notifyQueueListeners();
  }

  /** Manually trigger sync of all queued actions */
  async syncNow(): Promise<SyncResult[]> {
    if (this.isSyncing) return [];
    if (!this.isOnline()) return [];
    return this.processQueue();
  }

  // -------------------------------------------------------------------------
  // Subscriptions
  // -------------------------------------------------------------------------

  /** Subscribe to connection status changes */
  onStatusChange(listener: Listener<ConnectionStatus>): () => void {
    this.statusListeners.add(listener);
    return () => {
      this.statusListeners.delete(listener);
    };
  }

  /** Subscribe to queue changes */
  onQueueChange(listener: Listener<QueuedAction[]>): () => void {
    this.queueListeners.add(listener);
    return () => {
      this.queueListeners.delete(listener);
    };
  }

  /** Subscribe to sync results (batch, after syncNow or auto-sync) */
  onSyncResults(listener: Listener<SyncResult[]>): () => void {
    this.syncResultListeners.add(listener);
    return () => {
      this.syncResultListeners.delete(listener);
    };
  }

  /** Clean up event listeners and subscriptions */
  dispose(): void {
    if (this.disposed) return;
    this.disposed = true;

    if (typeof window !== 'undefined') {
      window.removeEventListener('online', this.handleOnline);
      window.removeEventListener('offline', this.handleOffline);
    }

    this.statusListeners.clear();
    this.queueListeners.clear();
    this.syncResultListeners.clear();
  }

  // -------------------------------------------------------------------------
  // Internals
  // -------------------------------------------------------------------------

  private initNetworkListeners(): void {
    if (typeof window === 'undefined') return;

    // Set initial status
    this.status = navigator.onLine ? 'online' : 'offline';

    window.addEventListener('online', this.handleOnline);
    window.addEventListener('offline', this.handleOffline);
  }

  private onOnline(): void {
    this.setStatus('online');
    if (this.autoSync && this.queue.length > 0) {
      this.processQueue();
    }
  }

  private onOffline(): void {
    this.setStatus('offline');
  }

  private setStatus(status: ConnectionStatus): void {
    if (this.status === status) return;
    this.status = status;
    Array.from(this.statusListeners).forEach((listener) => {
      try {
        listener(status);
      } catch {
        // Listener errors should not break the manager
      }
    });
  }

  private addToQueue(action: QueuedAction): void {
    if (this.queue.length >= this.maxQueueSize) {
      // Remove the oldest action to make room
      this.queue.shift();
    }
    this.queue.push(action);
    this.persistQueue();
    this.notifyQueueListeners();
  }

  private async processQueue(): Promise<SyncResult[]> {
    if (this.isSyncing || this.queue.length === 0) return [];
    this.isSyncing = true;
    this.setStatus('syncing');

    const results: SyncResult[] = [];
    const actionsToRetry: QueuedAction[] = [];

    // Process actions in order (FIFO)
    for (const action of [...this.queue]) {
      if (!this.isOnline()) {
        // Went offline mid-sync; keep remaining actions
        actionsToRetry.push(action);
        continue;
      }

      const result = await this.executeAction(action);
      results.push(result);

      if (result.status === 'error') {
        const updatedAction = { ...action, retryCount: action.retryCount + 1 };
        if (updatedAction.retryCount < updatedAction.maxRetries) {
          actionsToRetry.push(updatedAction);
        }
        // If max retries exceeded, the action is dropped and the error result is returned
      }
      // 'conflict' actions are dropped from the queue; the caller is notified via results
    }

    this.queue = actionsToRetry;
    this.persistQueue();
    this.notifyQueueListeners();

    this.isSyncing = false;
    this.setStatus(this.isOnline() ? 'online' : 'offline');

    // Notify sync result listeners
    Array.from(this.syncResultListeners).forEach((listener) => {
      try {
        listener(results);
      } catch {
        // Listener errors should not break the manager
      }
    });

    return results;
  }

  private async executeAction(action: QueuedAction): Promise<SyncResult> {
    try {
      // Validate freshness: reject actions older than 24 hours
      const maxAge = 24 * 60 * 60 * 1000;
      if (Date.now() - action.timestamp > maxAge) {
        return {
          status: 'conflict',
          action,
          serverVersion: undefined,
        };
      }

      const fetchOptions: RequestInit = {
        method: action.method,
        headers: {
          'Content-Type': 'application/json',
          ...action.headers,
        },
      };

      if (action.body && action.method !== 'GET') {
        fetchOptions.body = JSON.stringify(action.body);
      }

      // Include entity version for conflict detection
      if (action.entityVersion) {
        (fetchOptions.headers as Record<string, string>)['If-Match'] = action.entityVersion;
      }

      const response = await fetch(action.url, fetchOptions);

      if (response.status === 409) {
        // Conflict detected
        const data = await response.json().catch(() => ({}));
        return {
          status: 'conflict',
          action,
          serverVersion: data.version ?? data.etag,
        };
      }

      if (!response.ok) {
        return {
          status: 'error',
          action,
          error: `HTTP ${response.status}: ${response.statusText}`,
        };
      }

      return { status: 'success', action };
    } catch (error) {
      return {
        status: 'error',
        action,
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  }

  private persistQueue(): void {
    if (typeof localStorage === 'undefined') return;
    try {
      localStorage.setItem(this.storageKey, JSON.stringify(this.queue));
    } catch {
      // localStorage might be full or unavailable
    }
  }

  private restoreQueue(): void {
    if (typeof localStorage === 'undefined') return;
    try {
      const stored = localStorage.getItem(this.storageKey);
      if (stored) {
        this.queue = JSON.parse(stored);
      }
    } catch {
      this.queue = [];
    }
  }

  private notifyQueueListeners(): void {
    const snapshot = [...this.queue];
    Array.from(this.queueListeners).forEach((listener) => {
      try {
        listener(snapshot);
      } catch {
        // Listener errors should not break the manager
      }
    });
  }

  private generateId(): string {
    return `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
  }
}

// ---------------------------------------------------------------------------
// Singleton
// ---------------------------------------------------------------------------

let instance: OfflineManager | null = null;

/** Get or create the global OfflineManager instance */
export function getOfflineManager(options?: OfflineManagerOptions): OfflineManager {
  if (!instance) {
    instance = new OfflineManager(options);
  }
  return instance;
}

/** Reset the singleton (useful for tests) */
export function resetOfflineManager(): void {
  if (instance) {
    instance.dispose();
    instance = null;
  }
}
