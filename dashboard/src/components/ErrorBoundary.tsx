"use client";

import React, { Component, ReactNode } from "react";
import { AlertCircle, RefreshCw } from "lucide-react";
import { cn } from "@/lib/utils";

/**
 * ErrorBoundary component catches JavaScript errors anywhere in the child component tree
 *
 * Features:
 * - Catches and displays errors gracefully
 * - Prevents entire app crash when error occurs
 * - User-friendly error message with retry option
 * - Logs error details to console (development)
 * - Optional custom fallback UI
 * - Reset error state on retry
 * - Responsive design with centered layout
 *
 * @example
 * ```tsx
 * <ErrorBoundary>
 *   <YourComponent />
 * </ErrorBoundary>
 * ```
 *
 * @example With custom fallback
 * ```tsx
 * <ErrorBoundary fallback={<CustomErrorUI />}>
 *   <YourComponent />
 * </ErrorBoundary>
 * ```
 */

export interface ErrorBoundaryProps {
  /** Child components to wrap and protect */
  children: ReactNode;
  /** Optional custom fallback UI to display on error */
  fallback?: ReactNode;
  /** Optional callback when error is caught */
  onError?: (error: Error, errorInfo: React.ErrorInfo) => void;
}

export interface ErrorBoundaryState {
  /** Whether an error has been caught */
  hasError: boolean;
  /** The error object if caught */
  error: Error | null;
}

/**
 * ErrorBoundary class component - catches React errors in child components
 */
export class ErrorBoundary extends Component<
  ErrorBoundaryProps,
  ErrorBoundaryState
> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
    };
  }

  /**
   * Update state when error is caught
   */
  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return {
      hasError: true,
      error,
    };
  }

  /**
   * Log error details to console and call optional onError callback
   */
  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    // Log error details for debugging
    // eslint-disable-next-line no-console
    console.error("ErrorBoundary caught an error:", error, errorInfo);

    // Call optional error handler
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }
  }

  /**
   * Reset error state and retry rendering children
   */
  handleReset = () => {
    this.setState({
      hasError: false,
      error: null,
    });
  };

  render() {
    const { hasError, error } = this.state;
    const { children, fallback } = this.props;

    // If error occurred, show fallback UI
    if (hasError) {
      // Use custom fallback if provided
      if (fallback) {
        return fallback;
      }

      // Default error UI
      return (
        <div className="flex min-h-[400px] items-center justify-center p-4">
          <div className="w-full max-w-md">
            <div className="rounded-lg border border-red-200 bg-white p-6 shadow-sm">
              {/* Error icon */}
              <div className="mb-4 flex justify-center">
                <div className="rounded-full bg-red-100 p-3">
                  <AlertCircle className="h-8 w-8 text-red-600" />
                </div>
              </div>

              {/* Error message */}
              <div className="mb-6 text-center">
                <h2 className="mb-2 text-xl font-semibold text-slate-900">
                  Something went wrong
                </h2>
                <p className="text-sm text-slate-600">
                  We encountered an unexpected error. Please try again or
                  contact support if the problem persists.
                </p>

                {/* Show error message in development */}
                {process.env.NODE_ENV === "development" && error && (
                  <div className="mt-4 rounded-md bg-slate-50 p-3 text-left">
                    <p className="mb-1 text-xs font-medium text-slate-700">
                      Error Details:
                    </p>
                    <p className="text-xs text-red-600">{error.message}</p>
                  </div>
                )}
              </div>

              {/* Action buttons */}
              <div className="flex flex-col gap-2 sm:flex-row sm:justify-center">
                <button
                  onClick={this.handleReset}
                  className={cn(
                    "inline-flex items-center justify-center gap-2 rounded-md px-4 py-2",
                    "bg-slate-900 text-sm font-medium text-white",
                    "transition-colors hover:bg-slate-800",
                    "focus:outline-none focus:ring-2 focus:ring-slate-500 focus:ring-offset-2"
                  )}
                >
                  <RefreshCw className="h-4 w-4" />
                  Try Again
                </button>

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

    // No error, render children normally
    return children;
  }
}
