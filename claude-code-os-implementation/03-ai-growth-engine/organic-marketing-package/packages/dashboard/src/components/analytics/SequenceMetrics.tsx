"use client";

import {
  Mail,
  MousePointer,
  TrendingUp,
  Users,
  Send,
  MailOpen,
  ArrowRight,
  Clock,
} from "lucide-react";
import { MetricCard } from "@/components/MetricCard";

/**
 * Sequence performance metrics
 */
export interface SequencePerformanceMetrics {
  /** Total subscribers enrolled in sequence */
  totalEnrolled: number;
  /** Total emails sent */
  totalSent: number;
  /** Total emails opened */
  totalOpens: number;
  /** Total clicks */
  totalClicks: number;
  /** Total conversions */
  totalConversions: number;
  /** Open rate percentage */
  openRate: number;
  /** Click rate percentage */
  clickRate: number;
  /** Conversion rate percentage */
  conversionRate: number;
  /** Click-to-open rate percentage */
  clickToOpenRate: number;
  /** Average time to open (in hours) */
  avgTimeToOpen: number;
  /** Change in open rate vs previous period */
  openRateChange?: number;
  /** Change in click rate vs previous period */
  clickRateChange?: number;
  /** Change in conversion rate vs previous period */
  conversionRateChange?: number;
  /** Change in enrolled subscribers vs previous period */
  enrolledChange?: number;
}

/**
 * SequenceMetrics Props
 */
export interface SequenceMetricsProps {
  /** Sequence performance metrics */
  metrics: SequencePerformanceMetrics;
  /** Loading state */
  isLoading?: boolean;
  /** Optional custom className */
  className?: string;
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
 * Format hours to human-readable time
 */
function formatTime(hours: number): string {
  if (hours < 1) {
    return `${Math.round(hours * 60)}m`;
  }
  if (hours < 24) {
    return `${hours.toFixed(1)}h`;
  }
  const days = Math.floor(hours / 24);
  const remainingHours = Math.round(hours % 24);
  if (remainingHours === 0) {
    return `${days}d`;
  }
  return `${days}d ${remainingHours}h`;
}

/**
 * SequenceMetrics Component
 *
 * Display comprehensive sequence performance metrics in a grid layout.
 *
 * Features:
 * - Key metrics cards with icons and trend indicators
 * - Responsive grid layout (1 col mobile, 2 col tablet, 4 col desktop)
 * - Open rate, click rate, conversion rate, and engagement metrics
 * - Loading state support
 * - Color-coded trend indicators (green for positive, red for negative)
 * - Additional metrics like click-to-open rate and avg time to open
 * - MetricCard component integration for consistency
 *
 * @example
 * ```tsx
 * <SequenceMetrics
 *   metrics={performanceMetrics}
 *   isLoading={false}
 * />
 * ```
 */
export function SequenceMetrics({
  metrics,
  isLoading = false,
  className = "",
}: SequenceMetricsProps) {
  return (
    <div className={className}>
      {/* Primary Metrics */}
      <div className="mb-6">
        <h3 className="mb-4 text-lg font-semibold text-slate-900">
          Key Performance Metrics
        </h3>
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
          <MetricCard
            title="Subscribers Enrolled"
            value={formatNumber(metrics.totalEnrolled)}
            change={metrics.enrolledChange}
            icon={Users}
            description="Total subscribers in sequence"
            isLoading={isLoading}
          />
          <MetricCard
            title="Open Rate"
            value={`${metrics.openRate.toFixed(1)}%`}
            change={metrics.openRateChange}
            icon={MailOpen}
            description="Emails opened / sent"
            isLoading={isLoading}
          />
          <MetricCard
            title="Click Rate"
            value={`${metrics.clickRate.toFixed(1)}%`}
            change={metrics.clickRateChange}
            icon={MousePointer}
            description="Clicks / sent"
            isLoading={isLoading}
          />
          <MetricCard
            title="Conversion Rate"
            value={`${metrics.conversionRate.toFixed(1)}%`}
            change={metrics.conversionRateChange}
            icon={TrendingUp}
            description="Conversions / sent"
            isLoading={isLoading}
          />
        </div>
      </div>

      {/* Secondary Metrics */}
      <div className="mb-6">
        <h3 className="mb-4 text-lg font-semibold text-slate-900">
          Engagement Details
        </h3>
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
          <MetricCard
            title="Total Sent"
            value={formatNumber(metrics.totalSent)}
            icon={Send}
            description="Emails delivered"
            isLoading={isLoading}
          />
          <MetricCard
            title="Total Opens"
            value={formatNumber(metrics.totalOpens)}
            icon={Mail}
            description="Unique opens"
            isLoading={isLoading}
          />
          <MetricCard
            title="Total Clicks"
            value={formatNumber(metrics.totalClicks)}
            icon={ArrowRight}
            description="Link clicks"
            isLoading={isLoading}
          />
          <MetricCard
            title="Total Conversions"
            value={formatNumber(metrics.totalConversions)}
            icon={TrendingUp}
            description="Goal completions"
            isLoading={isLoading}
          />
        </div>
      </div>

      {/* Advanced Metrics */}
      <div>
        <h3 className="mb-4 text-lg font-semibold text-slate-900">
          Advanced Analytics
        </h3>
        <div className="grid gap-6 md:grid-cols-2">
          {/* Click-to-Open Rate Card */}
          <div className="rounded-lg border border-slate-200 bg-white p-6">
            <div className="mb-4 flex items-start justify-between">
              <div className="flex-1">
                <h3 className="text-sm font-medium text-slate-600">
                  Click-to-Open Rate
                </h3>
                <p className="mt-1 text-xs text-slate-500">
                  Clicks / opens (engagement quality)
                </p>
              </div>
              <div className="rounded-md bg-slate-100 p-2">
                <MousePointer className="h-5 w-5 text-slate-600" />
              </div>
            </div>

            <div className="mb-3">
              <p className="text-3xl font-bold text-slate-900">
                {metrics.clickToOpenRate.toFixed(1)}%
              </p>
            </div>

            {/* Visual bar */}
            <div className="mb-2 h-2 w-full overflow-hidden rounded-full bg-slate-100">
              <div
                className="h-full rounded-full bg-purple-600 transition-all"
                style={{
                  width: `${Math.min(metrics.clickToOpenRate, 100)}%`,
                }}
              ></div>
            </div>

            <div className="text-xs text-slate-500">
              {metrics.clickToOpenRate >= 20 ? (
                <span className="text-green-700">
                  ✓ Excellent engagement quality
                </span>
              ) : metrics.clickToOpenRate >= 10 ? (
                <span className="text-blue-700">Good engagement</span>
              ) : (
                <span className="text-yellow-700">Room for improvement</span>
              )}
            </div>
          </div>

          {/* Average Time to Open Card */}
          <div className="rounded-lg border border-slate-200 bg-white p-6">
            <div className="mb-4 flex items-start justify-between">
              <div className="flex-1">
                <h3 className="text-sm font-medium text-slate-600">
                  Avg. Time to Open
                </h3>
                <p className="mt-1 text-xs text-slate-500">
                  Average time between send and first open
                </p>
              </div>
              <div className="rounded-md bg-slate-100 p-2">
                <Clock className="h-5 w-5 text-slate-600" />
              </div>
            </div>

            <div className="mb-3">
              <p className="text-3xl font-bold text-slate-900">
                {formatTime(metrics.avgTimeToOpen)}
              </p>
            </div>

            {/* Benchmark indicator */}
            <div className="mb-2 flex items-center gap-2 text-xs text-slate-500">
              <div className="flex-1">
                <div className="h-1.5 rounded-full bg-slate-100">
                  <div
                    className="h-full rounded-full bg-blue-600"
                    style={{
                      width: `${Math.min((metrics.avgTimeToOpen / 48) * 100, 100)}%`,
                    }}
                  ></div>
                </div>
              </div>
              <span>48h</span>
            </div>

            <div className="text-xs text-slate-500">
              {metrics.avgTimeToOpen <= 2 ? (
                <span className="text-green-700">
                  ✓ Very fast response time
                </span>
              ) : metrics.avgTimeToOpen <= 12 ? (
                <span className="text-blue-700">Fast response time</span>
              ) : metrics.avgTimeToOpen <= 24 ? (
                <span className="text-yellow-700">Good response time</span>
              ) : (
                <span className="text-orange-700">Slower response time</span>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Conversion Funnel */}
      <div className="mt-6 rounded-lg border border-slate-200 bg-white p-6">
        <h3 className="mb-4 text-sm font-medium text-slate-700">
          Conversion Funnel
        </h3>
        <div className="space-y-3">
          {/* Sent */}
          <div>
            <div className="mb-1 flex items-center justify-between text-sm">
              <span className="text-slate-700">Sent</span>
              <span className="font-medium text-slate-900">
                {formatNumber(metrics.totalSent)} (100%)
              </span>
            </div>
            <div className="h-3 w-full overflow-hidden rounded-full bg-slate-100">
              <div className="h-full rounded-full bg-slate-400" style={{ width: "100%" }}></div>
            </div>
          </div>

          {/* Opened */}
          <div>
            <div className="mb-1 flex items-center justify-between text-sm">
              <span className="text-slate-700">Opened</span>
              <span className="font-medium text-blue-700">
                {formatNumber(metrics.totalOpens)} ({metrics.openRate.toFixed(1)}%)
              </span>
            </div>
            <div className="h-3 w-full overflow-hidden rounded-full bg-slate-100">
              <div
                className="h-full rounded-full bg-blue-500"
                style={{ width: `${metrics.openRate}%` }}
              ></div>
            </div>
          </div>

          {/* Clicked */}
          <div>
            <div className="mb-1 flex items-center justify-between text-sm">
              <span className="text-slate-700">Clicked</span>
              <span className="font-medium text-purple-700">
                {formatNumber(metrics.totalClicks)} ({metrics.clickRate.toFixed(1)}%)
              </span>
            </div>
            <div className="h-3 w-full overflow-hidden rounded-full bg-slate-100">
              <div
                className="h-full rounded-full bg-purple-500"
                style={{ width: `${metrics.clickRate}%` }}
              ></div>
            </div>
          </div>

          {/* Converted */}
          <div>
            <div className="mb-1 flex items-center justify-between text-sm">
              <span className="text-slate-700">Converted</span>
              <span className="font-medium text-green-700">
                {formatNumber(metrics.totalConversions)} ({metrics.conversionRate.toFixed(1)}%)
              </span>
            </div>
            <div className="h-3 w-full overflow-hidden rounded-full bg-slate-100">
              <div
                className="h-full rounded-full bg-green-500"
                style={{ width: `${metrics.conversionRate}%` }}
              ></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
