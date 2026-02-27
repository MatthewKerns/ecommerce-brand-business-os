"use client";

import { Mail, MousePointer, TrendingUp, Calendar } from "lucide-react";
import { cn } from "@/lib/utils";

/**
 * Email event data point
 */
export interface EmailEventDataPoint {
  /** Date label (e.g., "Mon", "Jan 1", "Week 1") */
  label: string;
  /** Number of emails sent */
  sent: number;
  /** Number of emails opened */
  opens: number;
  /** Number of clicks */
  clicks: number;
  /** Number of conversions */
  conversions: number;
}

/**
 * EmailEventChart Props
 */
export interface EmailEventChartProps {
  /** Chart data points */
  data: EmailEventDataPoint[];
  /** Chart title */
  title?: string;
  /** Time period label */
  period?: string;
  /** Optional custom className */
  className?: string;
}

/**
 * Calculate maximum value across all metrics for chart scaling
 */
function getMaxValue(data: EmailEventDataPoint[]): number {
  const maxSent = Math.max(...data.map((d) => d.sent));
  const maxOpens = Math.max(...data.map((d) => d.opens));
  const maxClicks = Math.max(...data.map((d) => d.clicks));
  return Math.max(maxSent, maxOpens, maxClicks);
}

/**
 * Format number for tooltip display
 */
function formatNumber(num: number): string {
  return num.toLocaleString();
}

/**
 * EmailEventChart Component
 *
 * Display email event metrics over time with a visual chart.
 *
 * Features:
 * - Time-series visualization of email events (sent, opens, clicks, conversions)
 * - Bar chart representation with color-coded metrics
 * - Interactive hover states showing exact values
 * - Responsive design
 * - Legend showing what each color represents
 * - Percentage display for rates
 * - Empty state when no data available
 *
 * @example
 * ```tsx
 * <EmailEventChart
 *   data={eventData}
 *   title="Last 7 Days"
 *   period="Daily"
 * />
 * ```
 */
export function EmailEventChart({
  data,
  title = "Email Performance Over Time",
  period = "Daily",
  className,
}: EmailEventChartProps) {
  const maxValue = getMaxValue(data);

  // Empty state
  if (data.length === 0) {
    return (
      <div
        className={cn(
          "rounded-lg border border-slate-200 bg-white p-6",
          className
        )}
      >
        <h3 className="mb-4 text-lg font-semibold text-slate-900">{title}</h3>
        <div className="flex flex-col items-center justify-center rounded-lg border-2 border-dashed border-slate-200 bg-slate-50 p-12">
          <Calendar className="h-12 w-12 text-slate-400" />
          <p className="mt-4 text-sm text-slate-600">No data available yet</p>
        </div>
      </div>
    );
  }

  return (
    <div
      className={cn(
        "rounded-lg border border-slate-200 bg-white p-6",
        className
      )}
    >
      {/* Header */}
      <div className="mb-6 flex items-start justify-between">
        <div>
          <h3 className="text-lg font-semibold text-slate-900">{title}</h3>
          <p className="mt-1 text-sm text-slate-600">{period} performance</p>
        </div>
      </div>

      {/* Legend */}
      <div className="mb-6 flex flex-wrap gap-4">
        <div className="flex items-center gap-2">
          <div className="h-3 w-3 rounded-full bg-slate-400"></div>
          <span className="text-xs text-slate-700">Sent</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="h-3 w-3 rounded-full bg-blue-500"></div>
          <span className="text-xs text-slate-700">Opens</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="h-3 w-3 rounded-full bg-purple-500"></div>
          <span className="text-xs text-slate-700">Clicks</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="h-3 w-3 rounded-full bg-green-500"></div>
          <span className="text-xs text-slate-700">Conversions</span>
        </div>
      </div>

      {/* Chart */}
      <div className="relative">
        {/* Y-axis labels */}
        <div className="absolute -left-2 top-0 flex h-64 flex-col justify-between text-xs text-slate-500">
          <span>{formatNumber(maxValue)}</span>
          <span>{formatNumber(Math.floor(maxValue * 0.75))}</span>
          <span>{formatNumber(Math.floor(maxValue * 0.5))}</span>
          <span>{formatNumber(Math.floor(maxValue * 0.25))}</span>
          <span>0</span>
        </div>

        {/* Chart area */}
        <div className="ml-12 overflow-x-auto">
          <div
            className="flex h-64 items-end gap-2"
            style={{ minWidth: `${data.length * 80}px` }}
          >
            {data.map((point, index) => {
              const sentHeight = maxValue > 0 ? (point.sent / maxValue) * 100 : 0;
              const opensHeight = maxValue > 0 ? (point.opens / maxValue) * 100 : 0;
              const clicksHeight = maxValue > 0 ? (point.clicks / maxValue) * 100 : 0;
              const conversionsHeight = maxValue > 0 ? (point.conversions / maxValue) * 100 : 0;

              const openRate = point.sent > 0 ? (point.opens / point.sent) * 100 : 0;
              const clickRate = point.sent > 0 ? (point.clicks / point.sent) * 100 : 0;
              const conversionRate = point.sent > 0 ? (point.conversions / point.sent) * 100 : 0;

              return (
                <div key={index} className="group relative flex-1">
                  {/* Tooltip */}
                  <div className="absolute bottom-full left-1/2 z-10 mb-2 hidden w-48 -translate-x-1/2 rounded-lg border border-slate-200 bg-white p-3 shadow-lg group-hover:block">
                    <div className="mb-2 text-xs font-medium text-slate-900">
                      {point.label}
                    </div>
                    <div className="space-y-1.5 text-xs">
                      <div className="flex items-center justify-between">
                        <span className="text-slate-600">Sent:</span>
                        <span className="font-medium text-slate-900">
                          {formatNumber(point.sent)}
                        </span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-slate-600">Opens:</span>
                        <span className="font-medium text-blue-700">
                          {formatNumber(point.opens)} ({openRate.toFixed(1)}%)
                        </span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-slate-600">Clicks:</span>
                        <span className="font-medium text-purple-700">
                          {formatNumber(point.clicks)} ({clickRate.toFixed(1)}%)
                        </span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-slate-600">Conversions:</span>
                        <span className="font-medium text-green-700">
                          {formatNumber(point.conversions)} ({conversionRate.toFixed(1)}%)
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Bars */}
                  <div className="flex h-full flex-col items-center justify-end gap-1 pb-8">
                    {/* Sent bar (background) */}
                    <div className="relative w-full">
                      <div
                        className="w-full rounded-t bg-slate-200 transition-all group-hover:bg-slate-300"
                        style={{ height: `${sentHeight}%` }}
                      ></div>
                    </div>

                    {/* Layered bars */}
                    <div className="absolute bottom-8 flex w-full flex-col items-center">
                      {/* Opens bar */}
                      {point.opens > 0 && (
                        <div
                          className="w-3/4 rounded-t bg-blue-500 transition-all group-hover:bg-blue-600"
                          style={{ height: `${opensHeight * 2.56}px` }}
                        ></div>
                      )}
                      {/* Clicks bar */}
                      {point.clicks > 0 && (
                        <div
                          className="w-1/2 rounded-t bg-purple-500 transition-all group-hover:bg-purple-600"
                          style={{ height: `${clicksHeight * 2.56}px` }}
                        ></div>
                      )}
                      {/* Conversions bar */}
                      {point.conversions > 0 && (
                        <div
                          className="w-1/3 rounded-t bg-green-500 transition-all group-hover:bg-green-600"
                          style={{ height: `${conversionsHeight * 2.56}px` }}
                        ></div>
                      )}
                    </div>
                  </div>

                  {/* X-axis label */}
                  <div className="absolute bottom-0 left-1/2 -translate-x-1/2 text-xs text-slate-600">
                    {point.label}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* X-axis line */}
        <div className="ml-12 mt-2 border-t border-slate-200"></div>
      </div>

      {/* Summary Stats */}
      <div className="mt-6 grid grid-cols-2 gap-4 border-t border-slate-200 pt-6 md:grid-cols-4">
        <div>
          <div className="flex items-center gap-2 text-sm text-slate-600">
            <Mail className="h-4 w-4" />
            Total Sent
          </div>
          <div className="mt-1 text-2xl font-bold text-slate-900">
            {formatNumber(data.reduce((sum, d) => sum + d.sent, 0))}
          </div>
        </div>
        <div>
          <div className="flex items-center gap-2 text-sm text-slate-600">
            <Mail className="h-4 w-4 text-blue-600" />
            Total Opens
          </div>
          <div className="mt-1 text-2xl font-bold text-blue-700">
            {formatNumber(data.reduce((sum, d) => sum + d.opens, 0))}
          </div>
        </div>
        <div>
          <div className="flex items-center gap-2 text-sm text-slate-600">
            <MousePointer className="h-4 w-4 text-purple-600" />
            Total Clicks
          </div>
          <div className="mt-1 text-2xl font-bold text-purple-700">
            {formatNumber(data.reduce((sum, d) => sum + d.clicks, 0))}
          </div>
        </div>
        <div>
          <div className="flex items-center gap-2 text-sm text-slate-600">
            <TrendingUp className="h-4 w-4 text-green-600" />
            Total Conversions
          </div>
          <div className="mt-1 text-2xl font-bold text-green-700">
            {formatNumber(data.reduce((sum, d) => sum + d.conversions, 0))}
          </div>
        </div>
      </div>
    </div>
  );
}
