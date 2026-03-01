"use client";

import { useState } from "react";
import { AlertTriangle, RefreshCw, Database, MailOpen } from "lucide-react";
import { cn } from "@/lib/utils";

interface DataLoadErrorProps {
  title?: string;
  message?: string;
  hasCachedData?: boolean;
  cachedDataAge?: string;
  onRetry?: () => void;
  onUseCachedData?: () => void;
  onContactSupport?: () => void;
  className?: string;
}

/**
 * Displayed when a data fetch fails. Can optionally offer cached data as a fallback.
 */
export function DataLoadError({
  title = "Failed to Load Data",
  message = "We couldn't retrieve the latest data. Please try again.",
  hasCachedData = false,
  cachedDataAge,
  onRetry,
  onUseCachedData,
  onContactSupport,
  className,
}: DataLoadErrorProps) {
  const [isRetrying, setIsRetrying] = useState(false);

  const handleRetry = async () => {
    if (!onRetry) return;
    setIsRetrying(true);
    try {
      await onRetry();
    } finally {
      setIsRetrying(false);
    }
  };

  return (
    <div
      className={cn(
        "flex min-h-[250px] items-center justify-center p-6",
        className,
      )}
    >
      <div className="w-full max-w-md text-center">
        <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-red-100">
          <AlertTriangle className="h-7 w-7 text-red-600" />
        </div>

        <h3 className="mb-1 text-lg font-semibold text-slate-900">{title}</h3>
        <p className="mb-4 text-sm text-slate-600">{message}</p>

        {hasCachedData && (
          <div className="mb-4 rounded-lg border border-blue-200 bg-blue-50 p-3">
            <div className="flex items-center justify-center gap-2 text-sm text-blue-800">
              <Database className="h-4 w-4" />
              <span>
                Cached data available
                {cachedDataAge ? ` (${cachedDataAge} old)` : ""}
              </span>
            </div>
            {onUseCachedData && (
              <button
                onClick={onUseCachedData}
                className="mt-2 text-sm font-medium text-blue-700 hover:text-blue-600"
              >
                Use cached data instead
              </button>
            )}
          </div>
        )}

        <div className="flex flex-col items-center gap-2 sm:flex-row sm:justify-center">
          {onRetry && (
            <button
              onClick={handleRetry}
              disabled={isRetrying}
              className="inline-flex items-center gap-2 rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-slate-800 disabled:opacity-50"
            >
              <RefreshCw
                className={cn("h-4 w-4", isRetrying && "animate-spin")}
              />
              {isRetrying ? "Retrying..." : "Try Again"}
            </button>
          )}

          {onContactSupport && (
            <button
              onClick={onContactSupport}
              className="inline-flex items-center gap-2 rounded-md border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 transition-colors hover:bg-slate-50"
            >
              <MailOpen className="h-4 w-4" />
              Contact Support
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
