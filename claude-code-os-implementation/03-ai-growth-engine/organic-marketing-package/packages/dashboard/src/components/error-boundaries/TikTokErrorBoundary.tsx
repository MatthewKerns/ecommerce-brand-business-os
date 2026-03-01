"use client";

import React, { Component, ReactNode } from "react";
import { Video, RefreshCw, AlertCircle, WifiOff } from "lucide-react";
import { cn } from "@/lib/utils";
import {
  logComponentError,
  isRecoverableError,
  getUserFriendlyErrorMessage,
} from "@/lib/error-handling";

interface TikTokErrorBoundaryProps {
  children: ReactNode;
}

interface TikTokErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  errorCount: number;
}

export class TikTokErrorBoundary extends Component<
  TikTokErrorBoundaryProps,
  TikTokErrorBoundaryState
> {
  constructor(props: TikTokErrorBoundaryProps) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorCount: 0,
    };
  }

  static getDerivedStateFromError(error: Error): Partial<TikTokErrorBoundaryState> {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    this.setState((prev) => ({ errorCount: prev.errorCount + 1 }));

    logComponentError(error, "TikTokContentStudio", {
      componentStack: errorInfo.componentStack,
      errorCount: this.state.errorCount + 1,
    });
  }

  handleRetry = () => {
    this.setState({ hasError: false, error: null });
  };

  handleRefreshPage = () => {
    window.location.reload();
  };

  render() {
    if (!this.state.hasError) {
      return this.props.children;
    }

    const { error, errorCount } = this.state;
    const recoverable = error ? isRecoverableError(error) : false;
    const friendlyMessage = error
      ? getUserFriendlyErrorMessage(error)
      : "An unexpected error occurred in TikTok Content Studio.";
    const tooManyRetries = errorCount >= 3;

    return (
      <div className="flex min-h-[400px] items-center justify-center p-4">
        <div className="w-full max-w-lg">
          <div className="rounded-lg border border-red-200 bg-white p-6 shadow-sm">
            {/* Icon */}
            <div className="mb-4 flex justify-center">
              <div className="rounded-full bg-red-100 p-3">
                {recoverable ? (
                  <WifiOff className="h-8 w-8 text-red-600" />
                ) : (
                  <Video className="h-8 w-8 text-red-600" />
                )}
              </div>
            </div>

            {/* Error message */}
            <div className="mb-6 text-center">
              <h2 className="mb-2 text-xl font-semibold text-slate-900">
                TikTok Studio Error
              </h2>
              <p className="text-sm text-slate-600">{friendlyMessage}</p>

              {tooManyRetries && (
                <div className="mt-3 rounded-md bg-amber-50 p-3">
                  <div className="flex items-start gap-2">
                    <AlertCircle className="mt-0.5 h-4 w-4 flex-shrink-0 text-amber-600" />
                    <p className="text-sm text-amber-700">
                      Multiple errors detected. Try refreshing the page or check
                      your TikTok API configuration.
                    </p>
                  </div>
                </div>
              )}

              {process.env.NODE_ENV === "development" && error && (
                <details className="mt-4 text-left">
                  <summary className="cursor-pointer text-xs text-slate-500">
                    Error Details
                  </summary>
                  <pre className="mt-2 max-h-40 overflow-auto whitespace-pre-wrap rounded-md bg-slate-50 p-3 text-xs text-red-600">
                    {error.message}
                    {error.stack && `\n\n${error.stack}`}
                  </pre>
                </details>
              )}
            </div>

            {/* Recovery actions */}
            <div className="flex flex-col gap-2 sm:flex-row sm:justify-center">
              {!tooManyRetries && (
                <button
                  onClick={this.handleRetry}
                  className={cn(
                    "inline-flex items-center justify-center gap-2 rounded-md px-4 py-2",
                    "bg-blue-600 text-sm font-medium text-white",
                    "transition-colors hover:bg-blue-700",
                    "focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                  )}
                >
                  <RefreshCw className="h-4 w-4" />
                  Retry
                </button>
              )}

              <button
                onClick={this.handleRefreshPage}
                className={cn(
                  "inline-flex items-center justify-center rounded-md px-4 py-2",
                  "border border-slate-300 bg-white text-sm font-medium text-slate-700",
                  "transition-colors hover:bg-slate-50",
                  "focus:outline-none focus:ring-2 focus:ring-slate-500 focus:ring-offset-2"
                )}
              >
                Refresh Page
              </button>

              <button
                onClick={() => (window.location.href = "/config")}
                className={cn(
                  "inline-flex items-center justify-center rounded-md px-4 py-2",
                  "border border-slate-300 bg-white text-sm font-medium text-slate-700",
                  "transition-colors hover:bg-slate-50",
                  "focus:outline-none focus:ring-2 focus:ring-slate-500 focus:ring-offset-2"
                )}
              >
                Check API Config
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }
}
