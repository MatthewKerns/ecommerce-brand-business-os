"use client";

import { useState, useEffect, useCallback } from "react";
import { Clock, RefreshCw, MailOpen } from "lucide-react";
import { cn } from "@/lib/utils";

interface RateLimitErrorProps {
  retryAfterSeconds?: number;
  onRetry?: () => void;
  onContactSupport?: () => void;
  className?: string;
}

/**
 * Displayed when a rate limit is hit. Shows a countdown timer
 * and automatically enables the retry button once the limit period expires.
 */
export function RateLimitError({
  retryAfterSeconds = 60,
  onRetry,
  onContactSupport,
  className,
}: RateLimitErrorProps) {
  const [remaining, setRemaining] = useState(retryAfterSeconds);
  const [isRetrying, setIsRetrying] = useState(false);
  const canRetry = remaining <= 0;

  useEffect(() => {
    if (remaining <= 0) return;

    const timer = setInterval(() => {
      setRemaining((prev) => Math.max(0, prev - 1));
    }, 1000);

    return () => clearInterval(timer);
  }, [remaining]);

  const handleRetry = useCallback(async () => {
    if (!onRetry || !canRetry) return;
    setIsRetrying(true);
    try {
      await onRetry();
    } finally {
      setIsRetrying(false);
    }
  }, [onRetry, canRetry]);

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    if (mins > 0) {
      return `${mins}m ${secs.toString().padStart(2, "0")}s`;
    }
    return `${secs}s`;
  };

  const progress = Math.max(
    0,
    ((retryAfterSeconds - remaining) / retryAfterSeconds) * 100,
  );

  return (
    <div
      className={cn(
        "flex min-h-[300px] items-center justify-center p-6",
        className,
      )}
    >
      <div className="w-full max-w-md text-center">
        <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-amber-100">
          <Clock className="h-7 w-7 text-amber-600" />
        </div>

        <h3 className="mb-1 text-lg font-semibold text-slate-900">
          Rate Limit Reached
        </h3>
        <p className="mb-4 text-sm text-slate-600">
          Too many requests. Please wait before trying again.
        </p>

        {!canRetry && (
          <div className="mb-4">
            <div className="mb-2 text-2xl font-bold tabular-nums text-slate-900">
              {formatTime(remaining)}
            </div>
            <div className="mx-auto h-2 w-48 overflow-hidden rounded-full bg-slate-200">
              <div
                className="h-full rounded-full bg-amber-500 transition-all duration-1000"
                style={{ width: `${progress}%` }}
              />
            </div>
          </div>
        )}

        {canRetry && (
          <p className="mb-4 text-sm font-medium text-green-600">
            Ready to retry
          </p>
        )}

        <div className="flex flex-col items-center gap-2 sm:flex-row sm:justify-center">
          {onRetry && (
            <button
              onClick={handleRetry}
              disabled={!canRetry || isRetrying}
              className="inline-flex items-center gap-2 rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-50"
            >
              <RefreshCw
                className={cn("h-4 w-4", isRetrying && "animate-spin")}
              />
              {isRetrying
                ? "Retrying..."
                : canRetry
                  ? "Retry Now"
                  : "Wait..."}
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
