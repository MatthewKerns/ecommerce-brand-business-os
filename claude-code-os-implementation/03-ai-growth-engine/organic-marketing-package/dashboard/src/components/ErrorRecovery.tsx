"use client";

import { useState, useCallback } from "react";
import {
  AlertCircle,
  RefreshCw,
  RotateCcw,
  Copy,
  Check,
  ChevronDown,
  ChevronUp,
  ExternalLink,
  MailOpen,
  Loader2,
} from "lucide-react";
import { cn } from "@/lib/utils";

type ErrorCategory =
  | "network"
  | "auth"
  | "validation"
  | "rate_limit"
  | "server"
  | "unknown";

interface RecoveryAction {
  label: string;
  description?: string;
  action: () => void | Promise<void>;
  variant?: "primary" | "secondary";
}

interface ErrorHistoryEntry {
  message: string;
  category: ErrorCategory;
  timestamp: Date;
}

interface ErrorRecoveryProps {
  error: Error;
  category?: ErrorCategory;
  onRetry?: () => void | Promise<void>;
  onRefresh?: () => void;
  onContactSupport?: () => void;
  alternativeActions?: RecoveryAction[];
  documentationUrl?: string;
  className?: string;
}

const CATEGORY_CONFIG: Record<
  ErrorCategory,
  {
    title: string;
    description: string;
    steps: string[];
    suggestedAction: string;
  }
> = {
  network: {
    title: "Connection Issue",
    description:
      "We're having trouble reaching our servers. This is usually temporary.",
    steps: [
      "Check your internet connection",
      "Try refreshing the page",
      "If the problem persists, try again in a few minutes",
    ],
    suggestedAction: "Retry",
  },
  auth: {
    title: "Authentication Error",
    description: "Your session may have expired or permissions have changed.",
    steps: [
      "Try signing out and signing back in",
      "Check that your account has the required permissions",
      "Contact your workspace admin if the issue persists",
    ],
    suggestedAction: "Sign In Again",
  },
  validation: {
    title: "Invalid Input",
    description: "Some of the data provided doesn't match what we expected.",
    steps: [
      "Review the form fields for errors",
      "Make sure all required fields are filled in",
      "Check that values are in the correct format",
    ],
    suggestedAction: "Review Input",
  },
  rate_limit: {
    title: "Too Many Requests",
    description:
      "You've made too many requests in a short period. Please wait before trying again.",
    steps: [
      "Wait a moment before retrying",
      "Reduce the frequency of your requests",
      "Contact support if you need higher limits",
    ],
    suggestedAction: "Wait & Retry",
  },
  server: {
    title: "Server Error",
    description:
      "Something went wrong on our end. Our team has been notified.",
    steps: [
      "Try again in a few moments",
      "If the problem persists, check our status page",
      "Contact support with the error details below",
    ],
    suggestedAction: "Retry",
  },
  unknown: {
    title: "Something Went Wrong",
    description: "An unexpected error occurred.",
    steps: [
      "Try the action again",
      "Refresh the page",
      "If the problem persists, contact support with the error details",
    ],
    suggestedAction: "Retry",
  },
};

function detectCategory(error: Error): ErrorCategory {
  const msg = error.message.toLowerCase();
  const name = error.name.toLowerCase();

  if (
    msg.includes("fetch") ||
    msg.includes("network") ||
    msg.includes("timeout") ||
    msg.includes("econnrefused")
  )
    return "network";
  if (
    msg.includes("unauthorized") ||
    msg.includes("forbidden") ||
    msg.includes("401") ||
    msg.includes("403") ||
    name.includes("auth")
  )
    return "auth";
  if (
    msg.includes("validation") ||
    msg.includes("invalid") ||
    msg.includes("required field")
  )
    return "validation";
  if (msg.includes("rate limit") || msg.includes("429") || msg.includes("too many"))
    return "rate_limit";
  if (msg.includes("500") || msg.includes("server error") || msg.includes("internal"))
    return "server";

  return "unknown";
}

/**
 * ErrorRecovery provides contextual error messages, step-by-step recovery instructions,
 * actionable buttons, error history tracking, and support escalation.
 */
export function ErrorRecovery({
  error,
  category: explicitCategory,
  onRetry,
  onRefresh,
  onContactSupport,
  alternativeActions = [],
  documentationUrl,
  className,
}: ErrorRecoveryProps) {
  const category = explicitCategory ?? detectCategory(error);
  const config = CATEGORY_CONFIG[category];

  const [isRetrying, setIsRetrying] = useState(false);
  const [retryCount, setRetryCount] = useState(0);
  const [showDetails, setShowDetails] = useState(false);
  const [copied, setCopied] = useState(false);
  const [history, setHistory] = useState<ErrorHistoryEntry[]>([
    { message: error.message, category, timestamp: new Date() },
  ]);

  const handleRetry = useCallback(async () => {
    if (!onRetry) return;
    setIsRetrying(true);
    setRetryCount((c) => c + 1);
    try {
      await onRetry();
    } catch (retryError) {
      const err = retryError instanceof Error ? retryError : new Error(String(retryError));
      setHistory((prev) => [
        ...prev,
        {
          message: err.message,
          category: detectCategory(err),
          timestamp: new Date(),
        },
      ]);
    } finally {
      setIsRetrying(false);
    }
  }, [onRetry]);

  const handleCopyDetails = useCallback(() => {
    const details = [
      `Error: ${error.message}`,
      `Category: ${category}`,
      `Time: ${new Date().toISOString()}`,
      `Retry attempts: ${retryCount}`,
      error.stack ? `\nStack:\n${error.stack}` : "",
    ].join("\n");

    navigator.clipboard.writeText(details).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  }, [error, category, retryCount]);

  const handleRefresh = () => {
    if (onRefresh) {
      onRefresh();
    } else {
      window.location.reload();
    }
  };

  return (
    <div
      className={cn(
        "w-full max-w-lg rounded-lg border border-red-200 bg-white p-6 shadow-sm",
        className,
      )}
    >
      {/* Header */}
      <div className="mb-4 flex items-start gap-3">
        <div className="flex-shrink-0 rounded-full bg-red-100 p-2">
          <AlertCircle className="h-5 w-5 text-red-600" />
        </div>
        <div>
          <h3 className="text-base font-semibold text-slate-900">
            {config.title}
          </h3>
          <p className="mt-0.5 text-sm text-slate-600">{config.description}</p>
        </div>
      </div>

      {/* Recovery Steps */}
      <div className="mb-5">
        <p className="mb-2 text-xs font-medium uppercase tracking-wide text-slate-500">
          Recovery Steps
        </p>
        <ol className="space-y-1.5">
          {config.steps.map((step, idx) => (
            <li key={idx} className="flex items-start gap-2 text-sm text-slate-700">
              <span className="flex h-5 w-5 flex-shrink-0 items-center justify-center rounded-full bg-slate-100 text-xs font-medium text-slate-600">
                {idx + 1}
              </span>
              {step}
            </li>
          ))}
        </ol>
      </div>

      {/* Progress indicator during retry */}
      {isRetrying && (
        <div className="mb-4 flex items-center gap-2 rounded-md bg-blue-50 p-3 text-sm text-blue-800">
          <Loader2 className="h-4 w-4 animate-spin" />
          Attempting recovery... (attempt {retryCount})
        </div>
      )}

      {/* Primary Actions */}
      <div className="mb-4 flex flex-wrap gap-2">
        {onRetry && (
          <button
            onClick={handleRetry}
            disabled={isRetrying}
            className="inline-flex items-center gap-2 rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-slate-800 disabled:opacity-50"
          >
            <RefreshCw
              className={cn("h-4 w-4", isRetrying && "animate-spin")}
            />
            {isRetrying ? "Retrying..." : config.suggestedAction}
          </button>
        )}

        <button
          onClick={handleRefresh}
          className="inline-flex items-center gap-2 rounded-md border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 transition-colors hover:bg-slate-50"
        >
          <RotateCcw className="h-4 w-4" />
          Refresh Page
        </button>

        {alternativeActions.map((action, idx) => (
          <button
            key={idx}
            onClick={() => action.action()}
            className={cn(
              "inline-flex items-center gap-2 rounded-md px-4 py-2 text-sm font-medium transition-colors",
              action.variant === "primary"
                ? "bg-blue-600 text-white hover:bg-blue-700"
                : "border border-slate-300 bg-white text-slate-700 hover:bg-slate-50",
            )}
          >
            {action.label}
          </button>
        ))}
      </div>

      {/* Support & Docs Row */}
      <div className="flex flex-wrap items-center gap-3 border-t border-slate-100 pt-4">
        {onContactSupport && (
          <button
            onClick={onContactSupport}
            className="inline-flex items-center gap-1.5 text-sm font-medium text-slate-600 hover:text-slate-900"
          >
            <MailOpen className="h-3.5 w-3.5" />
            Contact Support
          </button>
        )}

        {documentationUrl && (
          <a
            href={documentationUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1.5 text-sm font-medium text-slate-600 hover:text-slate-900"
          >
            <ExternalLink className="h-3.5 w-3.5" />
            Documentation
          </a>
        )}

        <button
          onClick={handleCopyDetails}
          className="inline-flex items-center gap-1.5 text-sm font-medium text-slate-600 hover:text-slate-900"
        >
          {copied ? (
            <>
              <Check className="h-3.5 w-3.5 text-green-600" />
              <span className="text-green-600">Copied</span>
            </>
          ) : (
            <>
              <Copy className="h-3.5 w-3.5" />
              Copy Error Details
            </>
          )}
        </button>
      </div>

      {/* Error Details (collapsible) */}
      <div className="mt-3 border-t border-slate-100 pt-3">
        <button
          onClick={() => setShowDetails(!showDetails)}
          className="flex w-full items-center justify-between text-xs font-medium text-slate-500 hover:text-slate-700"
        >
          Error Details
          {showDetails ? (
            <ChevronUp className="h-3.5 w-3.5" />
          ) : (
            <ChevronDown className="h-3.5 w-3.5" />
          )}
        </button>

        {showDetails && (
          <div className="mt-2 space-y-2">
            <div className="rounded-md bg-slate-50 p-3 text-xs">
              <p className="font-medium text-slate-700">
                {error.name}: {error.message}
              </p>
              {error.stack && (
                <pre className="mt-2 max-h-32 overflow-auto whitespace-pre-wrap text-slate-500">
                  {error.stack}
                </pre>
              )}
            </div>

            {/* Error History */}
            {history.length > 1 && (
              <div>
                <p className="mb-1 text-xs font-medium text-slate-500">
                  Error History ({history.length} occurrences)
                </p>
                <div className="space-y-1">
                  {history.map((entry, idx) => (
                    <div
                      key={idx}
                      className="flex items-center justify-between rounded bg-slate-50 px-2 py-1 text-xs"
                    >
                      <span className="text-slate-600 truncate mr-2">
                        {entry.message}
                      </span>
                      <span className="flex-shrink-0 text-slate-400">
                        {entry.timestamp.toLocaleTimeString()}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
