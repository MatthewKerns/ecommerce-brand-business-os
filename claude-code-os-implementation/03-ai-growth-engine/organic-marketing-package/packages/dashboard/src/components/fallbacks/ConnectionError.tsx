"use client";

import { useState, useEffect } from "react";
import { WifiOff, RefreshCw, MailOpen } from "lucide-react";
import { cn } from "@/lib/utils";

interface ConnectionErrorProps {
  onRetry?: () => void;
  onContactSupport?: () => void;
  autoRetry?: boolean;
  autoRetryInterval?: number;
  className?: string;
}

/**
 * Displayed when a network connectivity issue is detected.
 * Optionally auto-retries at a set interval.
 */
export function ConnectionError({
  onRetry,
  onContactSupport,
  autoRetry = false,
  autoRetryInterval = 10000,
  className,
}: ConnectionErrorProps) {
  const [isRetrying, setIsRetrying] = useState(false);
  const [countdown, setCountdown] = useState(
    autoRetry ? Math.ceil(autoRetryInterval / 1000) : 0,
  );

  useEffect(() => {
    if (!autoRetry || !onRetry) return;

    const interval = setInterval(() => {
      setCountdown((prev) => {
        if (prev <= 1) {
          onRetry();
          return Math.ceil(autoRetryInterval / 1000);
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(interval);
  }, [autoRetry, autoRetryInterval, onRetry]);

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
        "flex min-h-[300px] items-center justify-center p-6",
        className,
      )}
    >
      <div className="w-full max-w-md text-center">
        <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-slate-100">
          <WifiOff className="h-7 w-7 text-slate-500" />
        </div>

        <h3 className="mb-1 text-lg font-semibold text-slate-900">
          Connection Lost
        </h3>
        <p className="mb-4 text-sm text-slate-600">
          Please check your internet connection and try again.
        </p>

        {autoRetry && countdown > 0 && (
          <p className="mb-4 text-xs text-slate-500">
            Retrying automatically in {countdown}s
          </p>
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
              {isRetrying ? "Reconnecting..." : "Reconnect"}
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
