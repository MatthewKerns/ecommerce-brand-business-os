"use client";

import { useEffect } from "react";
import { AlertCircle, RefreshCw, Home } from "lucide-react";
import { cn } from "@/lib/utils";

/**
 * Error page component for Next.js App Router
 *
 * Features:
 * - Catches errors at the route level
 * - User-friendly error message with retry option
 * - Navigate back to dashboard option
 * - Logs error details to console (development)
 * - Responsive centered layout
 * - Error boundary for route segments
 *
 * This file is a Next.js App Router convention:
 * - Must be a Client Component ("use client")
 * - Receives error and reset props automatically
 * - Catches errors in the current route segment
 *
 * @see https://nextjs.org/docs/app/api-reference/file-conventions/error
 */

export interface ErrorPageProps {
  /** Error object thrown in the route */
  error: Error & { digest?: string };
  /** Function to reset the error boundary and retry */
  reset: () => void;
}

export default function ErrorPage({ error, reset }: ErrorPageProps) {
  // Log error to console in development
  useEffect(() => {
    // eslint-disable-next-line no-console
    console.error("Route error caught:", error);
  }, [error]);

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-50 p-4">
      <div className="w-full max-w-md">
        <div className="rounded-lg border border-red-200 bg-white p-8 shadow-sm">
          {/* Error icon */}
          <div className="mb-6 flex justify-center">
            <div className="rounded-full bg-red-100 p-4">
              <AlertCircle className="h-10 w-10 text-red-600" />
            </div>
          </div>

          {/* Error message */}
          <div className="mb-8 text-center">
            <h1 className="mb-3 text-2xl font-bold text-slate-900">
              Something went wrong
            </h1>
            <p className="mb-2 text-base text-slate-600">
              We encountered an unexpected error while loading this page.
            </p>
            <p className="text-sm text-slate-500">
              Please try again or return to the dashboard. If the problem
              persists, contact support.
            </p>

            {/* Show error message in development */}
            {process.env.NODE_ENV === "development" && (
              <div className="mt-6 rounded-md bg-slate-50 p-4 text-left">
                <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-700">
                  Error Details (Development Only):
                </p>
                <p className="mb-1 text-sm font-medium text-red-600">
                  {error.message}
                </p>
                {error.digest && (
                  <p className="text-xs text-slate-500">
                    Error ID: {error.digest}
                  </p>
                )}
                {error.stack && (
                  <details className="mt-3">
                    <summary className="cursor-pointer text-xs font-medium text-slate-700 hover:text-slate-900">
                      Stack Trace
                    </summary>
                    <pre className="mt-2 max-h-48 overflow-auto rounded bg-slate-100 p-2 text-xs text-slate-800">
                      {error.stack}
                    </pre>
                  </details>
                )}
              </div>
            )}
          </div>

          {/* Action buttons */}
          <div className="flex flex-col gap-3">
            {/* Retry button */}
            <button
              onClick={reset}
              className={cn(
                "inline-flex items-center justify-center gap-2 rounded-md px-5 py-2.5",
                "bg-slate-900 text-sm font-semibold text-white",
                "transition-colors hover:bg-slate-800",
                "focus:outline-none focus:ring-2 focus:ring-slate-500 focus:ring-offset-2"
              )}
            >
              <RefreshCw className="h-4 w-4" />
              Try Again
            </button>

            {/* Go to dashboard button */}
            <button
              onClick={() => (window.location.href = "/")}
              className={cn(
                "inline-flex items-center justify-center gap-2 rounded-md px-5 py-2.5",
                "border border-slate-300 bg-white text-sm font-medium text-slate-700",
                "transition-colors hover:bg-slate-50",
                "focus:outline-none focus:ring-2 focus:ring-slate-500 focus:ring-offset-2"
              )}
            >
              <Home className="h-4 w-4" />
              Go to Dashboard
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
