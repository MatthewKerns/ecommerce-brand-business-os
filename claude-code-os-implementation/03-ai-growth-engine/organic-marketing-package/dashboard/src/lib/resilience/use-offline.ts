'use client';

/**
 * React hook for consuming OfflineManager state.
 *
 * Provides reactive connection status, pending queue, and
 * actions to enqueue / sync / clear offline actions.
 */

import { useCallback, useEffect, useRef, useSyncExternalStore } from 'react';
import {
  ConnectionStatus,
  getOfflineManager,
  OfflineManager,
  QueuedAction,
  SyncResult,
} from './offline-manager';

// ---------------------------------------------------------------------------
// Internal store snapshots for useSyncExternalStore
// ---------------------------------------------------------------------------

function subscribeStatus(callback: () => void): () => void {
  const mgr = getOfflineManager();
  return mgr.onStatusChange(() => callback());
}

function getStatusSnapshot(): ConnectionStatus {
  return getOfflineManager().getStatus();
}

function getServerStatusSnapshot(): ConnectionStatus {
  return 'online'; // SSR always assumes online
}

function subscribeQueue(callback: () => void): () => void {
  const mgr = getOfflineManager();
  return mgr.onQueueChange(() => callback());
}

function getQueueSnapshot(): ReadonlyArray<QueuedAction> {
  return getOfflineManager().getQueue();
}

function getServerQueueSnapshot(): ReadonlyArray<QueuedAction> {
  return [];
}

// ---------------------------------------------------------------------------
// Hook
// ---------------------------------------------------------------------------

export interface UseOfflineReturn {
  /** Current connection status ('online' | 'offline' | 'syncing') */
  status: ConnectionStatus;
  /** Whether the app is currently offline */
  isOffline: boolean;
  /** Whether a sync is currently in progress */
  isSyncing: boolean;
  /** Queued actions waiting to be synced */
  queue: ReadonlyArray<QueuedAction>;
  /** Number of pending actions */
  pendingCount: number;
  /** Enqueue an action (will attempt immediate execution if online) */
  enqueue: OfflineManager['enqueue'];
  /** Manually trigger sync of all queued actions */
  syncNow: () => Promise<SyncResult[]>;
  /** Remove a single action from the queue */
  removeFromQueue: (actionId: string) => boolean;
  /** Clear the entire queue */
  clearQueue: () => void;
}

export function useOffline(): UseOfflineReturn {
  const managerRef = useRef<OfflineManager>(getOfflineManager());

  const status = useSyncExternalStore(subscribeStatus, getStatusSnapshot, getServerStatusSnapshot);
  const queue = useSyncExternalStore(subscribeQueue, getQueueSnapshot, getServerQueueSnapshot);

  const enqueue = useCallback<OfflineManager['enqueue']>(
    (action) => managerRef.current.enqueue(action),
    []
  );

  const syncNow = useCallback(() => managerRef.current.syncNow(), []);

  const removeFromQueue = useCallback(
    (actionId: string) => managerRef.current.removeFromQueue(actionId),
    []
  );

  const clearQueue = useCallback(() => managerRef.current.clearQueue(), []);

  // Cleanup on unmount is not needed for the singleton, but we keep
  // a ref to avoid stale closure issues.
  useEffect(() => {
    managerRef.current = getOfflineManager();
  }, []);

  return {
    status,
    isOffline: status === 'offline',
    isSyncing: status === 'syncing',
    queue,
    pendingCount: queue.length,
    enqueue,
    syncNow,
    removeFromQueue,
    clearQueue,
  };
}
