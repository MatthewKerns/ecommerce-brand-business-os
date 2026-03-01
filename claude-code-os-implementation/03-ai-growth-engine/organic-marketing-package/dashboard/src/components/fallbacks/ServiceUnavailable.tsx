"use client";

import { useState, useEffect } from "react";
import { ServerCrash, RefreshCw, ExternalLink, MailOpen } from "lucide-react";
import { cn } from "@/lib/utils";

interface ServiceUnavailableProps {
  serviceName: string;
  estimatedRecovery?: string;
  statusPageUrl?: string;
  onRetry?: () => void;
  onContactSupport?: () => void;
  className?: string;
}

/**
 * Displayed when an external service is down.
 * Shows the service name, optional status page link, and estimated recovery time.
 */
export function ServiceUnavailable({
  serviceName,
  estimatedRecovery,
  statusPageUrl,
  onRetry,
  onContactSupport,
  className,
}: ServiceUnavailableProps) {
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
        "flex min-h-[300px] items-center justify-center p-6",
        className,
      )}
    >
      <div className="w-full max-w-md text-center">
        <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-orange-100">
          <ServerCrash className="h-7 w-7 text-orange-600" />
        </div>

        <h3 className="mb-1 text-lg font-semibold text-slate-900">
          {serviceName} is Unavailable
        </h3>
        <p className="mb-4 text-sm text-slate-600">
          We&apos;re having trouble connecting to {serviceName}. This is usually
          temporary.
        </p>

        {estimatedRecovery && (
          <div className="mb-4 inline-flex items-center gap-2 rounded-full bg-slate-100 px-3 py-1.5 text-xs font-medium text-slate-700">
            Estimated recovery: {estimatedRecovery}
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

          {statusPageUrl && (
            <a
              href={statusPageUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 rounded-md border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 transition-colors hover:bg-slate-50"
            >
              <ExternalLink className="h-4 w-4" />
              Status Page
            </a>
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
