/**
 * Multi-Layer Cache Manager
 *
 * Provides a tiered caching system:
 *   1. Memory (LRU) -- fastest, limited capacity
 *   2. localStorage  -- survives page reload, ~5 MB limit
 *   3. IndexedDB     -- large datasets, async access
 *
 * Supports stale-while-revalidate, TTL expiration, manual/event-based
 * invalidation, size limits, and cache versioning for migrations.
 */

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export type CacheLayer = 'memory' | 'localStorage' | 'indexedDB';
export type EvictionPolicy = 'lru' | 'fifo';
export type InvalidationStrategy = 'ttl' | 'manual' | 'event';

export interface CacheEntry<T = unknown> {
  key: string;
  value: T;
  /** When this entry was written (epoch ms) */
  createdAt: number;
  /** When this entry was last accessed (epoch ms) */
  accessedAt: number;
  /** Time-to-live in ms; 0 = no expiration */
  ttl: number;
  /** Cache version for migration support */
  version: number;
}

export interface CacheStats {
  memorySize: number;
  memoryMaxSize: number;
  localStorageKeys: number;
  hits: number;
  misses: number;
  staleHits: number;
}

export interface CacheManagerOptions {
  /** Prefix for all storage keys (default: 'cache') */
  prefix?: string;
  /** Maximum entries in memory cache (default: 200) */
  memoryMaxSize?: number;
  /** Eviction policy for memory cache (default: 'lru') */
  evictionPolicy?: EvictionPolicy;
  /** Default TTL in ms (default: 300_000 = 5 min) */
  defaultTtl?: number;
  /** Cache version; bump to invalidate all entries (default: 1) */
  version?: number;
  /** IndexedDB database name (default: 'app-cache') */
  dbName?: string;
  /** IndexedDB store name (default: 'cache-store') */
  storeName?: string;
}

// ---------------------------------------------------------------------------
// LRU Memory Cache
// ---------------------------------------------------------------------------

class MemoryCache {
  private map = new Map<string, CacheEntry>();
  private readonly maxSize: number;
  private readonly policy: EvictionPolicy;

  constructor(maxSize: number, policy: EvictionPolicy) {
    this.maxSize = maxSize;
    this.policy = policy;
  }

  get<T>(key: string): CacheEntry<T> | undefined {
    const entry = this.map.get(key) as CacheEntry<T> | undefined;
    if (!entry) return undefined;

    // LRU: move to end (most recently used)
    if (this.policy === 'lru') {
      this.map.delete(key);
      entry.accessedAt = Date.now();
      this.map.set(key, entry as CacheEntry);
    }

    return entry;
  }

  set<T>(key: string, entry: CacheEntry<T>): void {
    // If key exists, delete first so insertion is at the end
    if (this.map.has(key)) {
      this.map.delete(key);
    }

    // Evict if over capacity
    while (this.map.size >= this.maxSize) {
      // Both LRU and FIFO remove the first (oldest) entry
      const firstKey = this.map.keys().next().value;
      if (firstKey !== undefined) {
        this.map.delete(firstKey);
      }
    }

    this.map.set(key, entry as CacheEntry);
  }

  delete(key: string): boolean {
    return this.map.delete(key);
  }

  clear(): void {
    this.map.clear();
  }

  get size(): number {
    return this.map.size;
  }

  get capacity(): number {
    return this.maxSize;
  }

  keys(): string[] {
    return Array.from(this.map.keys());
  }
}

// ---------------------------------------------------------------------------
// IndexedDB helpers
// ---------------------------------------------------------------------------

function openDB(dbName: string, storeName: string): Promise<IDBDatabase> {
  return new Promise((resolve, reject) => {
    if (typeof indexedDB === 'undefined') {
      reject(new Error('IndexedDB is not available'));
      return;
    }

    const request = indexedDB.open(dbName, 1);

    request.onupgradeneeded = () => {
      const db = request.result;
      if (!db.objectStoreNames.contains(storeName)) {
        db.createObjectStore(storeName, { keyPath: 'key' });
      }
    };

    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
}

// ---------------------------------------------------------------------------
// CacheManager
// ---------------------------------------------------------------------------

export class CacheManager {
  private memory: MemoryCache;
  private db: IDBDatabase | null = null;
  private dbReady: Promise<void> | null = null;
  private stats = { hits: 0, misses: 0, staleHits: 0 };

  private readonly prefix: string;
  private readonly defaultTtl: number;
  private readonly version: number;
  private readonly dbName: string;
  private readonly storeName: string;

  /** Listeners for event-based invalidation */
  private invalidationListeners = new Map<string, Set<() => void>>();

  constructor(options: CacheManagerOptions = {}) {
    this.prefix = options.prefix ?? 'cache';
    this.defaultTtl = options.defaultTtl ?? 300_000;
    this.version = options.version ?? 1;
    this.dbName = options.dbName ?? 'app-cache';
    this.storeName = options.storeName ?? 'cache-store';

    this.memory = new MemoryCache(
      options.memoryMaxSize ?? 200,
      options.evictionPolicy ?? 'lru'
    );

    // Open IndexedDB lazily
    this.dbReady = this.initDB();
  }

  // -------------------------------------------------------------------------
  // Public API
  // -------------------------------------------------------------------------

  /**
   * Get a value from cache, checking layers in order:
   *   memory -> localStorage -> IndexedDB
   *
   * If `revalidate` is provided and the entry is stale, the stale value
   * is returned immediately and the revalidation function is called in
   * the background (stale-while-revalidate).
   */
  async get<T>(
    key: string,
    revalidate?: () => Promise<T>
  ): Promise<T | undefined> {
    const fullKey = this.fullKey(key);

    // Layer 1: Memory
    const memEntry = this.memory.get<T>(fullKey);
    if (memEntry) {
      if (!this.isExpired(memEntry) && memEntry.version === this.version) {
        this.stats.hits++;
        return memEntry.value;
      }
      // Stale in memory -- try stale-while-revalidate
      if (revalidate) {
        this.stats.staleHits++;
        this.revalidateInBackground(key, revalidate);
        return memEntry.value;
      }
      // Expired without revalidator
      this.memory.delete(fullKey);
    }

    // Layer 2: localStorage
    const lsEntry = this.getFromLocalStorage<T>(fullKey);
    if (lsEntry) {
      if (!this.isExpired(lsEntry) && lsEntry.version === this.version) {
        this.stats.hits++;
        // Promote to memory
        this.memory.set(fullKey, lsEntry);
        return lsEntry.value;
      }
      if (revalidate) {
        this.stats.staleHits++;
        this.memory.set(fullKey, lsEntry);
        this.revalidateInBackground(key, revalidate);
        return lsEntry.value;
      }
      this.removeFromLocalStorage(fullKey);
    }

    // Layer 3: IndexedDB
    const idbEntry = await this.getFromIndexedDB<T>(fullKey);
    if (idbEntry) {
      if (!this.isExpired(idbEntry) && idbEntry.version === this.version) {
        this.stats.hits++;
        // Promote to memory + localStorage
        this.memory.set(fullKey, idbEntry);
        this.setInLocalStorage(fullKey, idbEntry);
        return idbEntry.value;
      }
      if (revalidate) {
        this.stats.staleHits++;
        this.memory.set(fullKey, idbEntry);
        this.revalidateInBackground(key, revalidate);
        return idbEntry.value;
      }
      await this.removeFromIndexedDB(fullKey);
    }

    this.stats.misses++;
    return undefined;
  }

  /**
   * Set a value in cache. Writes to all layers that apply:
   *   - Always memory
   *   - localStorage if layer includes it
   *   - IndexedDB if layer includes it
   */
  async set<T>(
    key: string,
    value: T,
    options?: { ttl?: number; layers?: CacheLayer[] }
  ): Promise<void> {
    const fullKey = this.fullKey(key);
    const ttl = options?.ttl ?? this.defaultTtl;
    const layers = options?.layers ?? ['memory', 'localStorage'];

    const entry: CacheEntry<T> = {
      key: fullKey,
      value,
      createdAt: Date.now(),
      accessedAt: Date.now(),
      ttl,
      version: this.version,
    };

    if (layers.includes('memory')) {
      this.memory.set(fullKey, entry);
    }

    if (layers.includes('localStorage')) {
      this.setInLocalStorage(fullKey, entry);
    }

    if (layers.includes('indexedDB')) {
      await this.setInIndexedDB(fullKey, entry);
    }
  }

  /** Invalidate a single key across all layers */
  async invalidate(key: string): Promise<void> {
    const fullKey = this.fullKey(key);
    this.memory.delete(fullKey);
    this.removeFromLocalStorage(fullKey);
    await this.removeFromIndexedDB(fullKey);
  }

  /** Invalidate all keys matching a prefix */
  async invalidateByPrefix(prefix: string): Promise<void> {
    const fullPrefix = this.fullKey(prefix);

    // Memory
    for (const k of this.memory.keys()) {
      if (k.startsWith(fullPrefix)) {
        this.memory.delete(k);
      }
    }

    // localStorage
    if (typeof localStorage !== 'undefined') {
      const keysToRemove: string[] = [];
      for (let i = 0; i < localStorage.length; i++) {
        const k = localStorage.key(i);
        if (k && k.startsWith(fullPrefix)) {
          keysToRemove.push(k);
        }
      }
      for (const k of keysToRemove) {
        localStorage.removeItem(k);
      }
    }

    // IndexedDB
    await this.clearIndexedDBByPrefix(fullPrefix);
  }

  /** Clear all cache entries across all layers */
  async clear(): Promise<void> {
    this.memory.clear();

    // Clear only our prefixed keys from localStorage
    if (typeof localStorage !== 'undefined') {
      const keysToRemove: string[] = [];
      for (let i = 0; i < localStorage.length; i++) {
        const k = localStorage.key(i);
        if (k && k.startsWith(`${this.prefix}:`)) {
          keysToRemove.push(k);
        }
      }
      for (const k of keysToRemove) {
        localStorage.removeItem(k);
      }
    }

    await this.clearIndexedDB();
  }

  /**
   * Subscribe to event-based invalidation.
   * When `emitInvalidation(eventKey)` is called, all subscribers are notified.
   */
  onInvalidation(eventKey: string, callback: () => void): () => void {
    if (!this.invalidationListeners.has(eventKey)) {
      this.invalidationListeners.set(eventKey, new Set());
    }
    this.invalidationListeners.get(eventKey)!.add(callback);
    return () => {
      this.invalidationListeners.get(eventKey)?.delete(callback);
    };
  }

  /** Emit an invalidation event, notifying all subscribers */
  emitInvalidation(eventKey: string): void {
    const listeners = this.invalidationListeners.get(eventKey);
    if (!listeners) return;
    Array.from(listeners).forEach((cb) => {
      try {
        cb();
      } catch {
        // listener errors should not break the cache
      }
    });
  }

  /** Warm the cache with multiple entries at once */
  async warmup<T>(entries: Array<{ key: string; fetcher: () => Promise<T>; ttl?: number }>): Promise<void> {
    await Promise.allSettled(
      entries.map(async ({ key, fetcher, ttl }) => {
        const value = await fetcher();
        await this.set(key, value, { ttl });
      })
    );
  }

  /** Get cache statistics */
  getStats(): CacheStats {
    let localStorageKeys = 0;
    if (typeof localStorage !== 'undefined') {
      for (let i = 0; i < localStorage.length; i++) {
        const k = localStorage.key(i);
        if (k && k.startsWith(`${this.prefix}:`)) {
          localStorageKeys++;
        }
      }
    }

    return {
      memorySize: this.memory.size,
      memoryMaxSize: this.memory.capacity,
      localStorageKeys,
      hits: this.stats.hits,
      misses: this.stats.misses,
      staleHits: this.stats.staleHits,
    };
  }

  // -------------------------------------------------------------------------
  // Internals
  // -------------------------------------------------------------------------

  private fullKey(key: string): string {
    return `${this.prefix}:${key}`;
  }

  private isExpired(entry: CacheEntry): boolean {
    if (entry.ttl === 0) return false;
    return Date.now() - entry.createdAt > entry.ttl;
  }

  private revalidateInBackground<T>(key: string, fetcher: () => Promise<T>): void {
    fetcher()
      .then((value) => this.set(key, value))
      .catch(() => {
        // Background revalidation failure is non-critical
      });
  }

  // --- localStorage layer ---

  private getFromLocalStorage<T>(fullKey: string): CacheEntry<T> | undefined {
    if (typeof localStorage === 'undefined') return undefined;
    try {
      const raw = localStorage.getItem(fullKey);
      if (!raw) return undefined;
      return JSON.parse(raw) as CacheEntry<T>;
    } catch {
      return undefined;
    }
  }

  private setInLocalStorage<T>(fullKey: string, entry: CacheEntry<T>): void {
    if (typeof localStorage === 'undefined') return;
    try {
      localStorage.setItem(fullKey, JSON.stringify(entry));
    } catch {
      // localStorage may be full; silently fail
    }
  }

  private removeFromLocalStorage(fullKey: string): void {
    if (typeof localStorage === 'undefined') return;
    try {
      localStorage.removeItem(fullKey);
    } catch {
      // ignore
    }
  }

  // --- IndexedDB layer ---

  private async initDB(): Promise<void> {
    try {
      this.db = await openDB(this.dbName, this.storeName);
    } catch {
      // IndexedDB unavailable (SSR, private browsing, etc.)
      this.db = null;
    }
  }

  private async ensureDB(): Promise<IDBDatabase | null> {
    if (this.dbReady) {
      await this.dbReady;
      this.dbReady = null;
    }
    return this.db;
  }

  private async getFromIndexedDB<T>(fullKey: string): Promise<CacheEntry<T> | undefined> {
    const db = await this.ensureDB();
    if (!db) return undefined;

    return new Promise((resolve) => {
      try {
        const tx = db.transaction(this.storeName, 'readonly');
        const store = tx.objectStore(this.storeName);
        const request = store.get(fullKey);

        request.onsuccess = () => resolve(request.result as CacheEntry<T> | undefined);
        request.onerror = () => resolve(undefined);
      } catch {
        resolve(undefined);
      }
    });
  }

  private async setInIndexedDB<T>(_fullKey: string, entry: CacheEntry<T>): Promise<void> {
    const db = await this.ensureDB();
    if (!db) return;

    return new Promise((resolve) => {
      try {
        const tx = db.transaction(this.storeName, 'readwrite');
        const store = tx.objectStore(this.storeName);
        store.put(entry);

        tx.oncomplete = () => resolve();
        tx.onerror = () => resolve();
      } catch {
        resolve();
      }
    });
  }

  private async removeFromIndexedDB(fullKey: string): Promise<void> {
    const db = await this.ensureDB();
    if (!db) return;

    return new Promise((resolve) => {
      try {
        const tx = db.transaction(this.storeName, 'readwrite');
        const store = tx.objectStore(this.storeName);
        store.delete(fullKey);

        tx.oncomplete = () => resolve();
        tx.onerror = () => resolve();
      } catch {
        resolve();
      }
    });
  }

  private async clearIndexedDB(): Promise<void> {
    const db = await this.ensureDB();
    if (!db) return;

    return new Promise((resolve) => {
      try {
        const tx = db.transaction(this.storeName, 'readwrite');
        const store = tx.objectStore(this.storeName);
        store.clear();

        tx.oncomplete = () => resolve();
        tx.onerror = () => resolve();
      } catch {
        resolve();
      }
    });
  }

  private async clearIndexedDBByPrefix(prefix: string): Promise<void> {
    const db = await this.ensureDB();
    if (!db) return;

    return new Promise((resolve) => {
      try {
        const tx = db.transaction(this.storeName, 'readwrite');
        const store = tx.objectStore(this.storeName);
        const request = store.openCursor();

        request.onsuccess = () => {
          const cursor = request.result;
          if (cursor) {
            if (typeof cursor.key === 'string' && cursor.key.startsWith(prefix)) {
              cursor.delete();
            }
            cursor.continue();
          }
        };

        tx.oncomplete = () => resolve();
        tx.onerror = () => resolve();
      } catch {
        resolve();
      }
    });
  }
}

// ---------------------------------------------------------------------------
// Singleton
// ---------------------------------------------------------------------------

let instance: CacheManager | null = null;

/** Get or create the global CacheManager instance */
export function getCacheManager(options?: CacheManagerOptions): CacheManager {
  if (!instance) {
    instance = new CacheManager(options);
  }
  return instance;
}

/** Reset the singleton (useful for tests) */
export function resetCacheManager(): void {
  instance = null;
}
