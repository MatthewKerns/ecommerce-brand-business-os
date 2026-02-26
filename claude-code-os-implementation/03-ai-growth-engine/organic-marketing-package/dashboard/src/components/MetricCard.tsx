"use client";

import { LucideIcon, TrendingUp, TrendingDown } from "lucide-react";
import { cn } from "@/lib/utils";

/**
 * MetricCard component displays a single metric with value and change indicator
 *
 * Features:
 * - Displays metric title and icon
 * - Shows current value with optional formatting
 * - Displays percentage change with trend indicator (up/down arrow)
 * - Color-coded trend: green for positive, red for negative
 * - Loading state with skeleton animation
 * - Responsive design
 *
 * @example
 * ```tsx
 * <MetricCard
 *   title="Total Views"
 *   value="12,543"
 *   change={12.5}
 *   icon={Eye}
 *   isLoading={false}
 * />
 * ```
 */

export interface MetricCardProps {
  /** Title of the metric */
  title: string;
  /** Current value to display (can be string or number) */
  value: string | number;
  /** Percentage change (positive or negative) */
  change?: number;
  /** Optional icon component from lucide-react */
  icon?: LucideIcon;
  /** Optional description or subtitle */
  description?: string;
  /** Loading state - shows skeleton when true */
  isLoading?: boolean;
  /** Optional custom className for card wrapper */
  className?: string;
}

export function MetricCard({
  title,
  value,
  change,
  icon: Icon,
  description,
  isLoading = false,
  className,
}: MetricCardProps) {
  // Loading state
  if (isLoading) {
    return (
      <div
        className={cn(
          "rounded-lg border border-slate-200 bg-white p-6",
          className
        )}
      >
        <div className="mb-2 h-4 w-24 animate-pulse rounded bg-slate-200"></div>
        <div className="mb-4 h-8 w-32 animate-pulse rounded bg-slate-200"></div>
        <div className="h-3 w-20 animate-pulse rounded bg-slate-200"></div>
      </div>
    );
  }

  // Determine trend direction and styling
  const isPositive = change !== undefined && change > 0;
  const isNegative = change !== undefined && change < 0;
  const isNeutral = change === 0;

  const trendColor = isPositive
    ? "text-green-600"
    : isNegative
      ? "text-red-600"
      : "text-slate-500";

  const trendBgColor = isPositive
    ? "bg-green-50"
    : isNegative
      ? "bg-red-50"
      : "bg-slate-50";

  return (
    <div
      className={cn(
        "rounded-lg border border-slate-200 bg-white p-6 transition-shadow hover:shadow-md",
        className
      )}
    >
      {/* Header with title and icon */}
      <div className="mb-4 flex items-start justify-between">
        <div className="flex-1">
          <h3 className="text-sm font-medium text-slate-600">{title}</h3>
          {description && (
            <p className="mt-1 text-xs text-slate-500">{description}</p>
          )}
        </div>
        {Icon && (
          <div className="rounded-md bg-slate-100 p-2">
            <Icon className="h-5 w-5 text-slate-600" />
          </div>
        )}
      </div>

      {/* Value */}
      <div className="mb-3">
        <p className="text-3xl font-bold text-slate-900">{value}</p>
      </div>

      {/* Change indicator */}
      {change !== undefined && (
        <div className="flex items-center gap-1">
          <div
            className={cn(
              "flex items-center gap-1 rounded-full px-2 py-0.5",
              trendBgColor
            )}
          >
            {!isNeutral && (
              <>
                {isPositive ? (
                  <TrendingUp className={cn("h-3 w-3", trendColor)} />
                ) : (
                  <TrendingDown className={cn("h-3 w-3", trendColor)} />
                )}
              </>
            )}
            <span className={cn("text-xs font-medium", trendColor)}>
              {isPositive && "+"}
              {change.toFixed(1)}%
            </span>
          </div>
          <span className="text-xs text-slate-500">vs last period</span>
        </div>
      )}
    </div>
  );
}
