"use client";

import { useParams, useRouter } from "next/navigation";
import { ArrowLeft, Download, Filter, Calendar } from "lucide-react";
import Link from "next/link";
import { useState } from "react";
import { SequenceMetrics, SequencePerformanceMetrics } from "@/components/analytics/SequenceMetrics";
import { EmailEventChart, EmailEventDataPoint } from "@/components/analytics/EmailEventChart";

/**
 * Generate mock performance metrics for demonstration
 * In production, this would fetch from API
 */
function generateMockMetrics(sequenceId: string): SequencePerformanceMetrics {
  // Different metrics based on sequence ID for variety
  const seed = sequenceId.length;
  const baseEnrolled = 1000 + seed * 100;
  const baseSent = baseEnrolled * 3.5; // Average emails per subscriber

  return {
    totalEnrolled: baseEnrolled,
    totalSent: Math.floor(baseSent),
    totalOpens: Math.floor(baseSent * 0.42),
    totalClicks: Math.floor(baseSent * 0.12),
    totalConversions: Math.floor(baseSent * 0.038),
    openRate: 42.0,
    clickRate: 12.0,
    conversionRate: 3.8,
    clickToOpenRate: 28.6,
    avgTimeToOpen: 4.5,
    openRateChange: 5.2,
    clickRateChange: 2.3,
    conversionRateChange: 0.8,
    enrolledChange: 12.5,
  };
}

/**
 * Generate mock time-series data for chart
 * In production, this would fetch from API
 */
function generateMockTimeSeriesData(days: number = 7): EmailEventDataPoint[] {
  const data: EmailEventDataPoint[] = [];
  const labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];

  for (let i = 0; i < days; i++) {
    const sent = Math.floor(Math.random() * 200) + 300;
    const opens = Math.floor(sent * (0.35 + Math.random() * 0.15));
    const clicks = Math.floor(sent * (0.08 + Math.random() * 0.08));
    const conversions = Math.floor(sent * (0.02 + Math.random() * 0.04));

    data.push({
      label: labels[i] || `Day ${i + 1}`,
      sent,
      opens,
      clicks,
      conversions,
    });
  }

  return data;
}

/**
 * Get sequence name from ID
 * In production, this would fetch from API
 */
function getSequenceName(sequenceId: string): string {
  const names: Record<string, string> = {
    "seq-1": "Welcome Series",
    "seq-2": "Nurture Campaign",
    "seq-3": "Product Launch Sequence",
    "seq-4": "Re-engagement Series",
    "test-seq": "Test Sequence",
  };
  return names[sequenceId] || "Email Sequence";
}

/**
 * Sequence Analytics Page
 *
 * Display comprehensive analytics for a specific email sequence.
 *
 * Features:
 * - Sequence performance metrics (enrollment, open rate, click rate, conversion)
 * - Time-series chart showing email events over time
 * - Conversion funnel visualization
 * - Advanced metrics (click-to-open rate, avg time to open)
 * - Time range selector (7 days, 30 days, 90 days, all time)
 * - Export functionality
 * - Filter options
 * - Navigation back to sequence list
 *
 * Route: /sequences/[id]/analytics
 *
 * @example
 * Navigate to: http://localhost:3000/sequences/test-seq/analytics
 */
export default function SequenceAnalyticsPage() {
  const params = useParams();
  const router = useRouter();
  const sequenceId = params.id as string;
  const sequenceName = getSequenceName(sequenceId);

  // State for time range filter
  const [timeRange, setTimeRange] = useState<"7d" | "30d" | "90d" | "all">("7d");

  // Generate mock data (in production, fetch from API based on sequenceId and timeRange)
  const metrics = generateMockMetrics(sequenceId);
  const chartData = generateMockTimeSeriesData(timeRange === "7d" ? 7 : timeRange === "30d" ? 30 : 90);

  // Time range options
  const timeRangeOptions = [
    { value: "7d" as const, label: "Last 7 days" },
    { value: "30d" as const, label: "Last 30 days" },
    { value: "90d" as const, label: "Last 90 days" },
    { value: "all" as const, label: "All time" },
  ];

  // Get chart period label
  const chartPeriod = timeRange === "7d" ? "Daily" : "Daily";
  const chartTitle = timeRange === "7d" ? "Last 7 Days" : timeRange === "30d" ? "Last 30 Days" : timeRange === "90d" ? "Last 90 Days" : "All Time";

  return (
    <div className="min-h-screen bg-slate-50">
      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          {/* Back button */}
          <Link
            href="/sequences"
            className="mb-4 inline-flex items-center gap-2 text-sm text-slate-600 transition-colors hover:text-slate-900"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to Sequences
          </Link>

          {/* Title and actions */}
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h1 className="text-3xl font-bold text-slate-900">
                {sequenceName} Analytics
              </h1>
              <p className="mt-2 text-sm text-slate-600">
                Comprehensive performance metrics and insights
              </p>
            </div>

            <div className="flex flex-wrap gap-3">
              {/* Time range selector */}
              <div className="relative">
                <select
                  value={timeRange}
                  onChange={(e) => setTimeRange(e.target.value as typeof timeRange)}
                  className="appearance-none rounded-lg border border-slate-300 bg-white px-4 py-2 pr-10 text-sm font-medium text-slate-700 shadow-sm transition-colors hover:border-slate-400 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
                >
                  {timeRangeOptions.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
                <Calendar className="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
              </div>

              {/* Filter button */}
              <button className="inline-flex items-center gap-2 rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 shadow-sm transition-colors hover:bg-slate-50">
                <Filter className="h-4 w-4" />
                Filters
              </button>

              {/* Export button */}
              <button className="inline-flex items-center gap-2 rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white shadow-sm transition-colors hover:bg-slate-800">
                <Download className="h-4 w-4" />
                Export
              </button>
            </div>
          </div>
        </div>

        {/* Metrics Section */}
        <div className="mb-8">
          <SequenceMetrics metrics={metrics} isLoading={false} />
        </div>

        {/* Chart Section */}
        <div className="mb-8">
          <EmailEventChart
            data={chartData}
            title={chartTitle}
            period={chartPeriod}
          />
        </div>

        {/* Additional Insights */}
        <div className="grid gap-6 md:grid-cols-2">
          {/* Top Performing Emails */}
          <div className="rounded-lg border border-slate-200 bg-white p-6">
            <h3 className="mb-4 text-lg font-semibold text-slate-900">
              Top Performing Emails
            </h3>
            <div className="space-y-3">
              {[
                { name: "Email 1: Welcome & Brand Story", openRate: 52.3, clicks: 156 },
                { name: "Email 3: Social Proof & Testimonials", openRate: 48.7, clicks: 143 },
                { name: "Email 4: First Purchase Offer", openRate: 41.2, clicks: 187 },
              ].map((email, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between rounded-lg bg-slate-50 p-3"
                >
                  <div className="flex-1">
                    <div className="text-sm font-medium text-slate-900">
                      {email.name}
                    </div>
                    <div className="mt-1 text-xs text-slate-600">
                      {email.clicks} clicks
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-semibold text-slate-900">
                      {email.openRate}%
                    </div>
                    <div className="text-xs text-slate-600">open rate</div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Best Send Times */}
          <div className="rounded-lg border border-slate-200 bg-white p-6">
            <h3 className="mb-4 text-lg font-semibold text-slate-900">
              Best Send Times
            </h3>
            <div className="space-y-3">
              {[
                { time: "Tuesday, 10:00 AM", openRate: 45.8, description: "Highest open rate" },
                { time: "Thursday, 2:00 PM", openRate: 43.2, description: "Highest click rate" },
                { time: "Wednesday, 9:00 AM", openRate: 42.1, description: "Best engagement" },
              ].map((timeSlot, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between rounded-lg bg-slate-50 p-3"
                >
                  <div className="flex-1">
                    <div className="text-sm font-medium text-slate-900">
                      {timeSlot.time}
                    </div>
                    <div className="mt-1 text-xs text-slate-600">
                      {timeSlot.description}
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-semibold text-slate-900">
                      {timeSlot.openRate}%
                    </div>
                    <div className="text-xs text-slate-600">open rate</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
