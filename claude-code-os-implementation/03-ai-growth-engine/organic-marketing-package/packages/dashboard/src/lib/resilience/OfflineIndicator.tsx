'use client';

/**
 * Offline Indicator Component
 *
 * Displays a banner when the app is offline, shows pending action count,
 * and provides manual sync / clear queue controls.
 */

import { useOffline } from './use-offline';

export function OfflineIndicator() {
  const { status, isOffline, isSyncing, pendingCount, syncNow, clearQueue } = useOffline();

  // Only render when offline or syncing or there are pending actions
  if (status === 'online' && pendingCount === 0) {
    return null;
  }

  return (
    <div
      role="status"
      aria-live="polite"
      className={`fixed bottom-4 left-1/2 z-50 flex -translate-x-1/2 items-center gap-3 rounded-lg px-4 py-2.5 text-sm font-medium shadow-lg transition-colors ${
        isOffline
          ? 'bg-amber-600 text-white'
          : isSyncing
            ? 'bg-blue-600 text-white'
            : 'bg-gray-800 text-gray-100'
      }`}
    >
      {/* Status dot */}
      <span
        className={`inline-block h-2 w-2 rounded-full ${
          isOffline
            ? 'bg-amber-300'
            : isSyncing
              ? 'animate-pulse bg-blue-300'
              : 'bg-green-400'
        }`}
      />

      {/* Message */}
      <span>
        {isOffline && 'You are offline'}
        {isSyncing && 'Syncing actions...'}
        {!isOffline && !isSyncing && pendingCount > 0 && 'Pending actions to sync'}
      </span>

      {/* Pending count badge */}
      {pendingCount > 0 && (
        <span className="rounded-full bg-white/20 px-2 py-0.5 text-xs">
          {pendingCount}
        </span>
      )}

      {/* Actions */}
      {!isOffline && pendingCount > 0 && !isSyncing && (
        <button
          onClick={() => syncNow()}
          className="ml-1 rounded bg-white/20 px-2.5 py-1 text-xs hover:bg-white/30"
        >
          Sync now
        </button>
      )}

      {pendingCount > 0 && !isSyncing && (
        <button
          onClick={clearQueue}
          className="rounded bg-white/10 px-2.5 py-1 text-xs hover:bg-white/20"
        >
          Clear
        </button>
      )}
    </div>
  );
}
