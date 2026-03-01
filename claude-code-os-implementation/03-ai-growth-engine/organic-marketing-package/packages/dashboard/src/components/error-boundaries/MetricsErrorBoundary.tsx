"use client";

import React, { Component, ReactNode } from "react";
import { BarChart3, RefreshCw, AlertCircle, Database } from "lucide-react";
import { cn } from "@/lib/utils";
import {
  logComponentError,
  isRecoverableError,
  getUserFriendlyErrorMessage,
} from "@/lib/error-handling";

interface MetricsErrorBoundaryProps {
  children: ReactNode;
  cachedData?: Record<string, unknown> | null;
}

interface MetricsErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  showCachedData: boolean;
}

export class MetricsErrorBoundary extends Component<
  MetricsErrorBoundaryProps,
  MetricsErrorBoundaryState
> {
  constructor(props: MetricsErrorBoundaryProps) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      showCachedData: false,
    };
  }

  static getDerivedStateFromError(error: Error): Partial<MetricsErrorBoundaryState> {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    logComponentError(error, "MetricsDashboard", {
      componentStack: errorInfo.componentStack,
      hasCachedData: !!this.props.cachedData,
    });
  }

  handleRetry = () => {
    this.setState({ hasError: false, error: null, showCachedData: false });
  };

  handleShowCachedData = () => {
    this.setState({ showCachedData: true });
  };

  render() {
    if (!this.state.hasError) {
      return this.props.children;
    }

    const { error, showCachedData } = this.state;
    const { cachedData } = this.props;
    const recoverable = error ? isRecoverableError(error) : false;
    const friendlyMessage = error
      ? getUserFriendlyErrorMessage(error)
      : "Unable to load analytics data.";
    const hasCachedData = cachedData && Object.keys(cachedData).length > 0;

    // Show cached data view
    if (showCachedData && hasCachedData) {
      return (
        <div className="space-y-4">
          <div className="flex items-center gap-2 rounded-lg border border-amber-200 bg-amber-50 p-3">
            <Database className="h-4 w-4 flex-shrink-0 text-amber-600" />
            <p className="text-sm text-amber-700">
              Showing cached data. Live metrics are temporarily unavailable.
            </p>
            <button
              onClick={this.handleRetry}
              className="ml-auto text-sm font-medium text-amber-700 underline hover:text-amber-800"
            >
              Retry
            </button>
          </div>
          <div className="rounded-lg border border-slate-200 bg-white p-6">
            <h3 className="mb-4 text-lg font-semibold text-slate-900">
              Last Known Metrics
            </h3>
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
              {Object.entries(cachedData).map(([key, value]) => (
                <div
                  key={key}
                  className="rounded-md border border-slate-100 bg-slate-50 p-4"
                >
                  <p className="text-xs font-medium text-slate-500">
                    {key.replace(/([A-Z])/g, " $1").replace(/^./, (s) => s.toUpperCase())}
                  </p>
                  <p className="mt-1 text-lg font-semibold text-slate-900">
                    {String(value)}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>
      );
    }

    return (
      <div className="flex min-h-[400px] items-center justify-center p-4">
        <div className="w-full max-w-lg">
          <div className="rounded-lg border border-red-200 bg-white p-6 shadow-sm">
            {/* Icon */}
            <div className="mb-4 flex justify-center">
              <div className="rounded-full bg-red-100 p-3">
                <BarChart3 className="h-8 w-8 text-red-600" />
              </div>
            </div>

            {/* Error message */}
            <div className="mb-6 text-center">
              <h2 className="mb-2 text-xl font-semibold text-slate-900">
                Analytics Unavailable
              </h2>
              <p className="text-sm text-slate-600">{friendlyMessage}</p>

              {recoverable && (
                <div className="mt-3 rounded-md bg-blue-50 p-3">
                  <p className="text-sm text-blue-700">
                    This appears to be a temporary issue. Your data is safe.
                  </p>
                </div>
              )}

              {process.env.NODE_ENV === "development" && error && (
                <details className="mt-4 text-left">
                  <summary className="cursor-pointer text-xs text-slate-500">
                    Error Details
                  </summary>
                  <pre className="mt-2 max-h-40 overflow-auto whitespace-pre-wrap rounded-md bg-slate-50 p-3 text-xs text-red-600">
                    {error.message}
                  </pre>
                </details>
              )}
            </div>

            {/* Recovery actions */}
            <div className="flex flex-col gap-2 sm:flex-row sm:justify-center">
              <button
                onClick={this.handleRetry}
                className={cn(
                  "inline-flex items-center justify-center gap-2 rounded-md px-4 py-2",
                  "bg-purple-600 text-sm font-medium text-white",
                  "transition-colors hover:bg-purple-700",
                  "focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2"
                )}
              >
                <RefreshCw className="h-4 w-4" />
                Retry
              </button>

              {hasCachedData && (
                <button
                  onClick={this.handleShowCachedData}
                  className={cn(
                    "inline-flex items-center justify-center gap-2 rounded-md px-4 py-2",
                    "border border-slate-300 bg-white text-sm font-medium text-slate-700",
                    "transition-colors hover:bg-slate-50",
                    "focus:outline-none focus:ring-2 focus:ring-slate-500 focus:ring-offset-2"
                  )}
                >
                  <Database className="h-4 w-4" />
                  Show Cached Data
                </button>
              )}

              <button
                onClick={() => (window.location.href = "/")}
                className={cn(
                  "inline-flex items-center justify-center rounded-md px-4 py-2",
                  "border border-slate-300 bg-white text-sm font-medium text-slate-700",
                  "transition-colors hover:bg-slate-50",
                  "focus:outline-none focus:ring-2 focus:ring-slate-500 focus:ring-offset-2"
                )}
              >
                Go to Dashboard
              </button>
            </div>

            {/* Status indicator */}
            {hasCachedData && (
              <div className="mt-4 flex items-center justify-center gap-2">
                <AlertCircle className="h-3 w-3 text-slate-400" />
                <p className="text-xs text-slate-500">
                  Cached data available from your last session
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  }
}
