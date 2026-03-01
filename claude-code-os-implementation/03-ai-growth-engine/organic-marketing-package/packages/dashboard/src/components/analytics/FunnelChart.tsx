"use client";

import { LucideIcon, TrendingDown, Users, Eye, ShoppingCart, DollarSign } from "lucide-react";
import { cn } from "@/lib/utils";
import { useMetrics } from "@/hooks/useMetrics";
import { useMemo } from "react";

/**
 * FunnelChart component displays customer journey funnel visualization
 *
 * Features:
 * - Visual funnel representation of conversion stages
 * - Stage-by-stage metrics with conversion rates
 * - Drop-off percentages between stages
 * - Responsive SVG-based funnel visualization
 * - Color-coded stages for visual clarity
 * - Loading state support
 * - Error handling with user-friendly messages
 * - Tooltips showing detailed metrics
 *
 * @example
 * ```tsx
 * <FunnelChart pollingInterval={60000} />
 * ```
 */

export interface FunnelStage {
  /** Stage identifier */
  id: string;
  /** Stage name/label */
  name: string;
  /** Number of users at this stage */
  value: number;
  /** Icon component from lucide-react */
  icon: LucideIcon;
  /** Stage color for visual distinction */
  color: string;
  /** Conversion rate from previous stage (percentage) */
  conversionRate?: number;
  /** Drop-off rate from previous stage (percentage) */
  dropOffRate?: number;
}

export interface FunnelChartProps {
  /** Optional custom className for wrapper */
  className?: string;
  /** Optional polling interval in milliseconds (default: disabled) */
  pollingInterval?: number;
  /** Optional custom stages data (overrides default) */
  stages?: FunnelStage[];
  /** Show detailed metrics for each stage */
  showDetails?: boolean;
}

/**
 * Format number to display-friendly string
 */
function formatNumber(num: number): string {
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + "M";
  }
  if (num >= 1000) {
    return (num / 1000).toFixed(1) + "K";
  }
  return num.toLocaleString();
}

/**
 * Calculate conversion rate between two values
 */
function calculateConversionRate(current: number, previous: number): number {
  if (previous === 0) return 0;
  return (current / previous) * 100;
}

/**
 * Calculate drop-off rate between two values
 */
function calculateDropOffRate(current: number, previous: number): number {
  if (previous === 0) return 0;
  return ((previous - current) / previous) * 100;
}

/**
 * Get color classes for stage
 */
function getStageColorClasses(color: string) {
  const colorMap: Record<string, { fill: string; text: string; bg: string }> = {
    blue: {
      fill: "fill-blue-500",
      text: "text-blue-700",
      bg: "bg-blue-50",
    },
    indigo: {
      fill: "fill-indigo-500",
      text: "text-indigo-700",
      bg: "bg-indigo-50",
    },
    purple: {
      fill: "fill-purple-500",
      text: "text-purple-700",
      bg: "bg-purple-50",
    },
    green: {
      fill: "fill-green-500",
      text: "text-green-700",
      bg: "bg-green-50",
    },
  };
  return colorMap[color] || colorMap.blue;
}

export function FunnelChart({
  className = "",
  pollingInterval,
  stages: customStages,
  showDetails = true,
}: FunnelChartProps) {
  // Fetch metrics from API with optional polling
  const { metrics, isLoading, error } = useMetrics({ pollingInterval });

  // Transform API metrics to funnel stages
  const funnelStages = useMemo<FunnelStage[]>(() => {
    // Use custom stages if provided
    if (customStages) {
      return customStages.map((stage, index) => {
        const previousStage = index > 0 ? customStages[index - 1] : null;
        return {
          ...stage,
          conversionRate: previousStage
            ? calculateConversionRate(stage.value, previousStage.value)
            : 100,
          dropOffRate: previousStage
            ? calculateDropOffRate(stage.value, previousStage.value)
            : 0,
        };
      });
    }

    // Default funnel stages from metrics
    if (!metrics) {
      return [];
    }

    // Extract metrics from API response
    const tiktok = metrics.services.find((s) => s.service === "tiktok");
    const website = metrics.services.find((s) => s.service === "website");
    const email = metrics.services.find((s) => s.service === "email");

    const totalReach = metrics.summary.totalReach?.value || 0;
    const websiteVisitors = website?.metrics.uniqueVisitors?.value || 0;
    const shopClicks = tiktok?.metrics.shopClicks?.value || 0;
    const emailConversions = email?.metrics.conversions?.value || 0;
    const totalRevenue = metrics.summary.totalRevenue?.value || 0;

    // Calculate total conversions (shop clicks + email conversions)
    const totalConversions = shopClicks + emailConversions;

    const stages: FunnelStage[] = [
      {
        id: "awareness",
        name: "Awareness",
        value: totalReach,
        icon: Eye,
        color: "blue",
      },
      {
        id: "interest",
        name: "Interest",
        value: websiteVisitors,
        icon: Users,
        color: "indigo",
      },
      {
        id: "consideration",
        name: "Consideration",
        value: totalConversions,
        icon: ShoppingCart,
        color: "purple",
      },
      {
        id: "purchase",
        name: "Purchase",
        value: totalRevenue > 0 ? Math.floor(totalRevenue / 50) : 0, // Estimate purchases
        icon: DollarSign,
        color: "green",
      },
    ];

    // Calculate conversion and drop-off rates
    return stages.map((stage, index) => {
      const previousStage = index > 0 ? stages[index - 1] : null;
      return {
        ...stage,
        conversionRate: previousStage
          ? calculateConversionRate(stage.value, previousStage.value)
          : 100,
        dropOffRate: previousStage
          ? calculateDropOffRate(stage.value, previousStage.value)
          : 0,
      };
    });
  }, [metrics, customStages]);

  // Calculate funnel dimensions
  const funnelWidth = 400;
  const funnelHeight = 400;
  const stageHeight = funnelHeight / Math.max(funnelStages.length, 1);

  // Show error state if metrics fetch fails
  if (error) {
    return (
      <div className={cn("rounded-lg border border-slate-200 bg-white p-6", className)}>
        <h2 className="mb-4 text-2xl font-bold text-slate-900">
          Conversion Funnel
        </h2>
        <div className="rounded-lg border border-red-200 bg-red-50 p-6">
          <p className="text-sm text-red-600">
            Failed to load funnel data: {error.message}
          </p>
          <p className="mt-2 text-xs text-red-500">
            Please check your connection and try again.
          </p>
        </div>
      </div>
    );
  }

  // Show loading state
  if (isLoading) {
    return (
      <div className={cn("rounded-lg border border-slate-200 bg-white p-6", className)}>
        <h2 className="mb-4 text-2xl font-bold text-slate-900">
          Conversion Funnel
        </h2>
        <div className="space-y-4">
          <div className="h-96 animate-pulse rounded-lg bg-slate-200"></div>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="space-y-2">
                <div className="h-4 w-24 animate-pulse rounded bg-slate-200"></div>
                <div className="h-8 w-32 animate-pulse rounded bg-slate-200"></div>
                <div className="h-3 w-20 animate-pulse rounded bg-slate-200"></div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  // Calculate max value for funnel width scaling
  const maxValue = Math.max(...funnelStages.map((s) => s.value), 1);

  return (
    <div className={cn("rounded-lg border border-slate-200 bg-white p-6", className)}>
      {/* Header */}
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-slate-900">Conversion Funnel</h2>
        <p className="text-sm text-slate-600">
          Customer journey from awareness to purchase
        </p>
      </div>

      {/* Funnel Visualization */}
      <div className="mb-8 flex justify-center overflow-x-auto">
        <svg
          viewBox={`0 0 ${funnelWidth} ${funnelHeight}`}
          className="h-auto w-full max-w-md"
        >
          {funnelStages.map((stage, index) => {
            // Calculate stage dimensions based on value
            const stageValue = stage.value;
            const widthRatio = stageValue / maxValue;
            const topWidth = funnelWidth * widthRatio;

            // Next stage width (for trapezoid bottom)
            const nextStage = funnelStages[index + 1];
            const nextWidthRatio = nextStage ? nextStage.value / maxValue : widthRatio * 0.8;
            const bottomWidth = funnelWidth * nextWidthRatio;

            // Positioning
            const y = index * stageHeight;
            const topX = (funnelWidth - topWidth) / 2;
            const bottomX = (funnelWidth - bottomWidth) / 2;

            // Create trapezoid path
            const path = `
              M ${topX} ${y}
              L ${topX + topWidth} ${y}
              L ${bottomX + bottomWidth} ${y + stageHeight}
              L ${bottomX} ${y + stageHeight}
              Z
            `;

            const colors = getStageColorClasses(stage.color);

            return (
              <g key={stage.id}>
                {/* Funnel segment */}
                <path
                  d={path}
                  className={cn(colors.fill, "opacity-80 transition-opacity hover:opacity-100")}
                  stroke="white"
                  strokeWidth="2"
                />

                {/* Stage label and value */}
                <text
                  x={funnelWidth / 2}
                  y={y + stageHeight / 2 - 10}
                  textAnchor="middle"
                  className="fill-white text-sm font-semibold"
                >
                  {stage.name}
                </text>
                <text
                  x={funnelWidth / 2}
                  y={y + stageHeight / 2 + 10}
                  textAnchor="middle"
                  className="fill-white text-xs font-medium"
                >
                  {formatNumber(stage.value)}
                </text>

                {/* Conversion rate (if not first stage) */}
                {index > 0 && stage.conversionRate !== undefined && (
                  <text
                    x={funnelWidth / 2}
                    y={y + stageHeight / 2 + 26}
                    textAnchor="middle"
                    className="fill-white text-xs opacity-90"
                  >
                    {stage.conversionRate.toFixed(1)}% conversion
                  </text>
                )}
              </g>
            );
          })}
        </svg>
      </div>

      {/* Detailed Metrics */}
      {showDetails && funnelStages.length > 0 && (
        <div>
          <h3 className="mb-4 text-sm font-semibold text-slate-700">
            Stage Details
          </h3>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {funnelStages.map((stage) => {
              const Icon = stage.icon;
              const colors = getStageColorClasses(stage.color);

              return (
                <div
                  key={stage.id}
                  className="rounded-lg border border-slate-200 bg-white p-4 transition-shadow hover:shadow-md"
                >
                  {/* Header */}
                  <div className="mb-3 flex items-center gap-2">
                    <div className={cn("rounded-md p-2", colors.bg)}>
                      <Icon className={cn("h-4 w-4", colors.text)} />
                    </div>
                    <h4 className="text-sm font-medium text-slate-700">
                      {stage.name}
                    </h4>
                  </div>

                  {/* Value */}
                  <div className="mb-2">
                    <p className="text-2xl font-bold text-slate-900">
                      {formatNumber(stage.value)}
                    </p>
                    <p className="text-xs text-slate-500">users</p>
                  </div>

                  {/* Conversion & Drop-off */}
                  <div className="space-y-1">
                    {stage.conversionRate !== undefined && stage.conversionRate < 100 && (
                      <div className="flex items-center justify-between text-xs">
                        <span className="text-slate-600">Conversion:</span>
                        <span className="font-medium text-green-600">
                          {stage.conversionRate.toFixed(1)}%
                        </span>
                      </div>
                    )}
                    {stage.dropOffRate !== undefined && stage.dropOffRate > 0 && (
                      <div className="flex items-center justify-between text-xs">
                        <span className="text-slate-600">Drop-off:</span>
                        <span className="flex items-center gap-1 font-medium text-red-600">
                          <TrendingDown className="h-3 w-3" />
                          {stage.dropOffRate.toFixed(1)}%
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Summary Stats */}
      {funnelStages.length > 1 && (
        <div className="mt-6 rounded-lg border border-slate-200 bg-slate-50 p-4">
          <h3 className="mb-3 text-sm font-semibold text-slate-700">
            Funnel Summary
          </h3>
          <div className="grid gap-4 sm:grid-cols-3">
            <div className="text-center">
              <p className="text-2xl font-bold text-slate-900">
                {formatNumber(funnelStages[0]?.value || 0)}
              </p>
              <p className="text-xs text-slate-600">Total Reach</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-slate-900">
                {formatNumber(funnelStages[funnelStages.length - 1]?.value || 0)}
              </p>
              <p className="text-xs text-slate-600">Final Conversions</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-slate-900">
                {funnelStages.length > 1
                  ? calculateConversionRate(
                      funnelStages[funnelStages.length - 1]?.value || 0,
                      funnelStages[0]?.value || 1
                    ).toFixed(2)
                  : "0.00"}
                %
              </p>
              <p className="text-xs text-slate-600">Overall Conversion Rate</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
