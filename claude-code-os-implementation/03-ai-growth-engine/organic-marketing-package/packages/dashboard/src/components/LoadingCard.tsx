"use client";

import { cn } from "@/lib/utils";

/**
 * LoadingCard component displays a skeleton placeholder for card content
 *
 * Features:
 * - Animated pulse effect for loading state
 * - Customizable layout (default, metric, status)
 * - Responsive design
 * - Matches card styling from MetricCard and other components
 * - Configurable height and padding
 *
 * @example
 * ```tsx
 * <LoadingCard variant="metric" />
 * <LoadingCard variant="status" className="h-32" />
 * ```
 */

export interface LoadingCardProps {
  /** Variant determines the skeleton layout */
  variant?: "default" | "metric" | "status";
  /** Optional custom className for card wrapper */
  className?: string;
}

export function LoadingCard({
  variant = "default",
  className,
}: LoadingCardProps) {
  // Metric variant - matches MetricCard layout
  if (variant === "metric") {
    return (
      <div
        className={cn(
          "rounded-lg border border-slate-200 bg-white p-6",
          className
        )}
      >
        {/* Header area */}
        <div className="mb-4 flex items-start justify-between">
          <div className="h-4 w-24 animate-pulse rounded bg-slate-200"></div>
          <div className="h-9 w-9 animate-pulse rounded-md bg-slate-200"></div>
        </div>
        {/* Value area */}
        <div className="mb-3 h-9 w-32 animate-pulse rounded bg-slate-200"></div>
        {/* Change indicator area */}
        <div className="h-6 w-28 animate-pulse rounded-full bg-slate-200"></div>
      </div>
    );
  }

  // Status variant - for service status cards
  if (variant === "status") {
    return (
      <div
        className={cn(
          "rounded-lg border border-slate-200 bg-white p-6",
          className
        )}
      >
        {/* Header with icon and title */}
        <div className="mb-4 flex items-center gap-3">
          <div className="h-10 w-10 animate-pulse rounded-md bg-slate-200"></div>
          <div className="flex-1">
            <div className="mb-2 h-5 w-32 animate-pulse rounded bg-slate-200"></div>
            <div className="h-3 w-20 animate-pulse rounded bg-slate-200"></div>
          </div>
        </div>
        {/* Status details */}
        <div className="space-y-2">
          <div className="h-4 w-full animate-pulse rounded bg-slate-200"></div>
          <div className="h-4 w-3/4 animate-pulse rounded bg-slate-200"></div>
        </div>
      </div>
    );
  }

  // Default variant - generic card skeleton
  return (
    <div
      className={cn(
        "rounded-lg border border-slate-200 bg-white p-6",
        className
      )}
    >
      {/* Title */}
      <div className="mb-4 h-6 w-48 animate-pulse rounded bg-slate-200"></div>
      {/* Content lines */}
      <div className="space-y-3">
        <div className="h-4 w-full animate-pulse rounded bg-slate-200"></div>
        <div className="h-4 w-full animate-pulse rounded bg-slate-200"></div>
        <div className="h-4 w-2/3 animate-pulse rounded bg-slate-200"></div>
      </div>
    </div>
  );
}
