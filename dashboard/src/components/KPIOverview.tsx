"use client";

import {
  Eye,
  Mail,
  FileText,
  DollarSign,
  Users,
  TrendingUp,
  LucideIcon,
} from "lucide-react";
import { MetricCard } from "@/components/MetricCard";
import { useMetrics } from "@/hooks/useMetrics";
import { useMemo } from "react";

/**
 * KPIOverview component displays key performance indicators grid
 *
 * Features:
 * - Displays 6 key metrics across all organic marketing channels
 * - Fetches real-time data from /api/metrics endpoint
 * - Responsive grid layout (1 col mobile, 2 col tablet, 3 col desktop)
 * - TikTok views, email subscribers, blog traffic, revenue, conversion rate, total reach
 * - Loading state support for all metrics
 * - Color-coded trend indicators
 * - Optional polling for real-time updates
 *
 * @example
 * ```tsx
 * <KPIOverview pollingInterval={60000} />
 * ```
 */

export interface KPIMetric {
  /** Title of the metric */
  title: string;
  /** Current value to display */
  value: string;
  /** Percentage change (positive or negative) */
  change: number;
  /** Icon component from lucide-react */
  icon: LucideIcon;
  /** Description or subtitle */
  description: string;
}

export interface KPIOverviewProps {
  /** Optional custom className for grid wrapper */
  className?: string;
  /** Optional polling interval in milliseconds (default: disabled) */
  pollingInterval?: number;
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
 * Format currency to display-friendly string
 */
function formatCurrency(num: number): string {
  return "$" + num.toLocaleString();
}

export function KPIOverview({
  className = "",
  pollingInterval,
}: KPIOverviewProps) {
  // Fetch metrics from API with optional polling
  const { metrics, isLoading, error } = useMetrics({ pollingInterval });

  // Transform API metrics to KPI format
  const kpiMetrics = useMemo<KPIMetric[]>(() => {
    if (!metrics) {
      return [];
    }

    const tiktok = metrics.services.find((s) => s.service === "tiktok");
    const blog = metrics.services.find((s) => s.service === "blog");
    const email = metrics.services.find((s) => s.service === "email");

    return [
      {
        title: "TikTok Views",
        value: formatNumber(tiktok?.metrics.views?.value || 0),
        change: tiktok?.metrics.views?.change || 0,
        icon: Eye,
        description: "Total video views",
      },
      {
        title: "Email Subscribers",
        value: (email?.metrics.subscribers?.value || 0).toLocaleString(),
        change: email?.metrics.subscribers?.change || 0,
        icon: Mail,
        description: "Active subscribers",
      },
      {
        title: "Blog Traffic",
        value: formatNumber(blog?.metrics.pageViews?.value || 0),
        change: blog?.metrics.pageViews?.change || 0,
        icon: FileText,
        description: "Monthly page views",
      },
      {
        title: "Revenue",
        value: formatCurrency(metrics.summary.totalRevenue?.value || 0),
        change: metrics.summary.totalRevenue?.change || 0,
        icon: DollarSign,
        description: "Last 30 days",
      },
      {
        title: "Conversion Rate",
        value: (metrics.summary.conversionRate?.value || 0).toFixed(2) + "%",
        change: metrics.summary.conversionRate?.change || 0,
        icon: TrendingUp,
        description: "Visitor to customer",
      },
      {
        title: "Total Reach",
        value: formatNumber(metrics.summary.totalReach?.value || 0),
        change: metrics.summary.totalReach?.change || 0,
        icon: Users,
        description: "Across all channels",
      },
    ];
  }, [metrics]);

  // Show error state if metrics fetch fails
  if (error) {
    return (
      <div className={className}>
        <h2 className="mb-4 text-lg font-semibold text-slate-900">
          Key Performance Indicators
        </h2>
        <div className="rounded-lg border border-red-200 bg-red-50 p-6">
          <p className="text-sm text-red-600">
            Failed to load metrics: {error.message}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className={className}>
      <h2 className="mb-4 text-lg font-semibold text-slate-900">
        Key Performance Indicators
      </h2>
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {kpiMetrics.map((metric, index) => (
          <MetricCard
            key={index}
            title={metric.title}
            value={metric.value}
            change={metric.change}
            icon={metric.icon}
            description={metric.description}
            isLoading={isLoading}
          />
        ))}
      </div>
    </div>
  );
}
