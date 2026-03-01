"use client";

import { BarChart3 } from "lucide-react";
import { MetricsErrorBoundary } from "@/components/error-boundaries";

/**
 * Analytics Dashboard Page
 *
 * Displays detailed performance metrics and analytics for organic marketing channels.
 *
 * Features (to be implemented):
 * - Performance charts and visualizations
 * - Channel-specific metrics (TikTok, Blog, Email)
 * - Trend analysis and comparisons
 * - Exportable reports
 * - Date range filtering
 *
 * @route /analytics
 */
function AnalyticsContent() {
  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center gap-3">
        <div className="rounded-lg bg-purple-100 p-3">
          <BarChart3 className="h-6 w-6 text-purple-700" />
        </div>
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Analytics</h1>
          <p className="text-sm text-slate-600">
            Detailed performance metrics and insights
          </p>
        </div>
      </div>

      {/* Date Range Selector Placeholder */}
      <div className="flex items-center justify-between rounded-lg border border-slate-200 bg-white p-4">
        <div className="flex gap-2">
          {["7 Days", "30 Days", "90 Days", "All Time"].map((range, index) => (
            <button
              key={range}
              className={`rounded-lg px-4 py-2 text-sm font-medium transition-colors ${
                index === 1
                  ? "bg-purple-600 text-white"
                  : "bg-slate-100 text-slate-700 hover:bg-slate-200"
              }`}
            >
              {range}
            </button>
          ))}
        </div>
        <button className="rounded-lg border border-slate-200 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50">
          Export Report
        </button>
      </div>

      {/* Key Metrics Grid */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        {[
          { label: "Total Views", value: "125.4K", change: "+12.5%" },
          { label: "Engagement Rate", value: "8.3%", change: "+2.1%" },
          { label: "New Subscribers", value: "3,421", change: "+18.7%" },
          { label: "Conversion Rate", value: "4.2%", change: "+0.8%" },
        ].map((metric) => (
          <div
            key={metric.label}
            className="rounded-lg border border-slate-200 bg-white p-6"
          >
            <div className="mb-2 text-sm font-medium text-slate-600">
              {metric.label}
            </div>
            <div className="mb-2 text-3xl font-bold text-slate-900">
              {metric.value}
            </div>
            <div className="text-sm font-medium text-green-600">
              {metric.change}
            </div>
          </div>
        ))}
      </div>

      {/* Chart Placeholder */}
      <div className="rounded-lg border border-slate-200 bg-white p-6">
        <h2 className="mb-4 text-lg font-semibold text-slate-900">
          Performance Over Time
        </h2>
        <div className="flex h-64 items-end justify-center gap-2">
          {[40, 65, 45, 80, 55, 90, 70, 85, 60, 95, 75, 88].map((height, i) => (
            <div key={i} className="flex flex-1 flex-col justify-end">
              <div
                className="w-full rounded-t-sm bg-purple-600 transition-all hover:bg-purple-700"
                style={{ height: `${height}%` }}
              ></div>
            </div>
          ))}
        </div>
        <div className="mt-4 flex justify-between text-xs text-slate-600">
          {["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"].map(
            (month) => (
              <span key={month}>{month}</span>
            )
          )}
        </div>
      </div>

      {/* Channel Breakdown */}
      <div className="grid gap-6 md:grid-cols-3">
        {[
          { channel: "TikTok", value: "45.2K", percentage: 36 },
          { channel: "Blog", value: "38.1K", percentage: 30 },
          { channel: "Email", value: "42.1K", percentage: 34 },
        ].map((channel) => (
          <div
            key={channel.channel}
            className="rounded-lg border border-slate-200 bg-white p-6"
          >
            <h3 className="mb-2 font-semibold text-slate-900">
              {channel.channel}
            </h3>
            <div className="mb-2 text-2xl font-bold text-slate-900">
              {channel.value}
            </div>
            <div className="h-2 w-full overflow-hidden rounded-full bg-slate-200">
              <div
                className="h-full rounded-full bg-purple-600"
                style={{ width: `${channel.percentage}%` }}
              ></div>
            </div>
            <div className="mt-2 text-sm text-slate-600">
              {channel.percentage}% of total traffic
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default function AnalyticsPage() {
  return (
    <MetricsErrorBoundary>
      <AnalyticsContent />
    </MetricsErrorBoundary>
  );
}
