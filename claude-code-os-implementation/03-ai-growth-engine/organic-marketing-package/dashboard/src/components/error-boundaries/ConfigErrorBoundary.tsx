"use client";

import React, { Component, ReactNode } from "react";
import { Settings, RefreshCw, AlertCircle, RotateCcw } from "lucide-react";
import { cn } from "@/lib/utils";
import {
  logComponentError,
  getUserFriendlyErrorMessage,
} from "@/lib/error-handling";

interface ConfigErrorBoundaryProps {
  children: ReactNode;
  onRollback?: () => void;
}

interface ConfigErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  rolledBack: boolean;
}

export class ConfigErrorBoundary extends Component<
  ConfigErrorBoundaryProps,
  ConfigErrorBoundaryState
> {
  constructor(props: ConfigErrorBoundaryProps) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      rolledBack: false,
    };
  }

  static getDerivedStateFromError(error: Error): Partial<ConfigErrorBoundaryState> {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    logComponentError(error, "ConfigurationDashboard", {
      componentStack: errorInfo.componentStack,
    });
  }

  handleRetry = () => {
    this.setState({ hasError: false, error: null, rolledBack: false });
  };

  handleRollback = () => {
    if (this.props.onRollback) {
      this.props.onRollback();
    }
    this.setState({ rolledBack: true, hasError: false, error: null });
  };

  render() {
    if (!this.state.hasError) {
      return this.props.children;
    }

    const { error } = this.state;
    const { onRollback } = this.props;
    const friendlyMessage = error
      ? getUserFriendlyErrorMessage(error)
      : "Unable to load configuration settings.";

    const isValidationError =
      error?.message.includes("Validation") ||
      error?.message.includes("validation") ||
      error?.message.includes("invalid");

    return (
      <div className="flex min-h-[400px] items-center justify-center p-4">
        <div className="w-full max-w-lg">
          <div className="rounded-lg border border-red-200 bg-white p-6 shadow-sm">
            {/* Icon */}
            <div className="mb-4 flex justify-center">
              <div className="rounded-full bg-red-100 p-3">
                <Settings className="h-8 w-8 text-red-600" />
              </div>
            </div>

            {/* Error message */}
            <div className="mb-6 text-center">
              <h2 className="mb-2 text-xl font-semibold text-slate-900">
                Configuration Error
              </h2>
              <p className="text-sm text-slate-600">{friendlyMessage}</p>

              {isValidationError && (
                <div className="mt-3 rounded-md bg-amber-50 p-3">
                  <div className="flex items-start gap-2">
                    <AlertCircle className="mt-0.5 h-4 w-4 flex-shrink-0 text-amber-600" />
                    <p className="text-left text-sm text-amber-700">
                      A configuration value appears to be invalid. You can
                      rollback to the previous working configuration.
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
                  "bg-blue-600 text-sm font-medium text-white",
                  "transition-colors hover:bg-blue-700",
                  "focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                )}
              >
                <RefreshCw className="h-4 w-4" />
                Retry
              </button>

              {onRollback && (
                <button
                  onClick={this.handleRollback}
                  className={cn(
                    "inline-flex items-center justify-center gap-2 rounded-md px-4 py-2",
                    "border border-amber-300 bg-amber-50 text-sm font-medium text-amber-700",
                    "transition-colors hover:bg-amber-100",
                    "focus:outline-none focus:ring-2 focus:ring-amber-500 focus:ring-offset-2"
                  )}
                >
                  <RotateCcw className="h-4 w-4" />
                  Rollback Configuration
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
          </div>
        </div>
      </div>
    );
  }
}
