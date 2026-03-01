"use client";

import {
  Eye,
  Heart,
  Share2,
  ShoppingCart,
  Users,
  MousePointerClick,
  Mail,
  DollarSign,
  TrendingUp,
  Package,
  BarChart3,
  Globe,
  Zap,
  LucideIcon,
} from "lucide-react";
import { MetricCard } from "@/components/MetricCard";
import { useAsyncState } from "@/hooks/useAsyncState";
import { apiClient } from "@/lib/api-client";
import type { AggregatedMetrics } from "@/lib/metrics-fetcher";
import { useCallback, useMemo, useState } from "react";
import { cn } from "@/lib/utils";

/**
 * MetricsOverview component displays comprehensive analytics metrics overview
 *
 * Features:
 * - Comprehensive metrics dashboard across all channels
 * - Categorized metric groups (Engagement, Traffic, Revenue, Email)
 * - Time period filtering support
 * - Responsive grid layout (1-4 columns based on screen size)
 * - Real-time data fetching with loading states
 * - Error handling with user-friendly messages
 * - Category filtering to focus on specific metric groups
 * - Automatic data refresh support
 * - Summary statistics footer
 *
 * @example
 * ```tsx
 * <MetricsOverview pollingInterval={60000} />
 * ```
 */

export interface MetricItem {
  /** Name of the metric */
  name: string;
  /** Current value to display */
  value: string;
  /** Percentage change (positive or negative) */
  change: number;
  /** Icon component from lucide-react */
  icon: LucideIcon;
  /** Optional description or subtitle */
  description?: string;
}

export interface MetricCategory {
  /** Category identifier */
  id: string;
  /** Display name */
  name: string;
  /** Category icon */
  icon: LucideIcon;
  /** Category metrics */
  metrics: MetricItem[];
  /** Category color for visual distinction */
  color: string;
  /** Optional description */
  description?: string;
}

export interface MetricsOverviewProps {
  /** Optional custom className for wrapper */
  className?: string;
  /** Optional polling interval in milliseconds (default: disabled) */
  pollingInterval?: number;
  /** Optional initial categories to display (default: all) */
  defaultCategories?: string[];
  /** Show category filters */
  showFilters?: boolean;
  /** Compact mode - smaller cards */
  compact?: boolean;
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

/**
 * Format percentage to display-friendly string
 */
function formatPercentage(num: number): string {
  return num.toFixed(1) + "%";
}

export function MetricsOverview({
  className = "",
  pollingInterval,
  defaultCategories = ["engagement", "traffic", "revenue", "email"],
  showFilters = true,
  compact = false,
}: MetricsOverviewProps) {
  // Fetch metrics from API using useAsyncState for unified state management
  const fetchMetrics = useCallback(
    async (_signal: AbortSignal) => apiClient.get<AggregatedMetrics>("/api/metrics"),
    []
  );

  const {
    data: metrics,
    isLoading,
    error,
    isFallback,
  } = useAsyncState<AggregatedMetrics>({
    asyncFn: fetchMetrics,
    retryCount: 2,
    retryDelay: 1000,
  });

  // State for category filtering
  const [selectedCategories, setSelectedCategories] =
    useState<string[]>(defaultCategories);

  // Transform API metrics to categorized format
  const categories = useMemo<MetricCategory[]>(() => {
    if (!metrics) {
      return [];
    }

    // Find service metrics
    const tiktokService = metrics.services.find((s) => s.service === "tiktok");
    const websiteService = metrics.services.find(
      (s) => s.service === "website"
    );
    const emailService = metrics.services.find((s) => s.service === "email");
    const blogService = metrics.services.find((s) => s.service === "blog");

    // Extract metrics with fallbacks
    const tiktokMetrics = tiktokService?.metrics || {};
    const websiteMetrics = websiteService?.metrics || {};
    const emailMetrics = emailService?.metrics || {};
    const blogMetrics = blogService?.metrics || {};
    const summaryMetrics = metrics.summary || {};

    return [
      {
        id: "engagement",
        name: "Engagement Metrics",
        icon: Heart,
        color: "rose",
        description: "Content engagement across channels",
        metrics: [
          {
            name: "TikTok Views",
            value: formatNumber(tiktokMetrics.views?.value || 0),
            change: tiktokMetrics.views?.change || 0,
            icon: Eye,
            description: "Total video views",
          },
          {
            name: "TikTok Likes",
            value: formatNumber(tiktokMetrics.likes?.value || 0),
            change: tiktokMetrics.likes?.change || 0,
            icon: Heart,
            description: "Video likes",
          },
          {
            name: "TikTok Shares",
            value: formatNumber(tiktokMetrics.shares?.value || 0),
            change: tiktokMetrics.shares?.change || 0,
            icon: Share2,
            description: "Content shares",
          },
          {
            name: "Engagement Rate",
            value: formatPercentage(tiktokMetrics.engagementRate?.value || 0),
            change: tiktokMetrics.engagementRate?.change || 0,
            icon: Zap,
            description: "Overall engagement",
          },
        ],
      },
      {
        id: "traffic",
        name: "Traffic Metrics",
        icon: Globe,
        color: "blue",
        description: "Website and blog traffic",
        metrics: [
          {
            name: "Page Views",
            value: formatNumber(
              (websiteMetrics.pageViews?.value || 0) +
                (blogMetrics.pageViews?.value || 0)
            ),
            change: websiteMetrics.pageViews?.change || 0,
            icon: Eye,
            description: "Total page views",
          },
          {
            name: "Unique Visitors",
            value: formatNumber(websiteMetrics.uniqueVisitors?.value || 0),
            change: websiteMetrics.uniqueVisitors?.change || 0,
            icon: Users,
            description: "Unique users",
          },
          {
            name: "Sessions",
            value: formatNumber(websiteMetrics.sessions?.value || 0),
            change: websiteMetrics.sessions?.change || 0,
            icon: MousePointerClick,
            description: "Total sessions",
          },
          {
            name: "Avg Session Duration",
            value:
              (websiteMetrics.avgSessionDuration?.value || 0).toFixed(1) + "m",
            change: websiteMetrics.avgSessionDuration?.change || 0,
            icon: BarChart3,
            description: "Average time on site",
          },
        ],
      },
      {
        id: "revenue",
        name: "Revenue Metrics",
        icon: DollarSign,
        color: "green",
        description: "Sales and conversion performance",
        metrics: [
          {
            name: "Total Revenue",
            value: formatCurrency(summaryMetrics.totalRevenue?.value || 0),
            change: summaryMetrics.totalRevenue?.change || 0,
            icon: DollarSign,
            description: "Last 30 days",
          },
          {
            name: "Total Orders",
            value: formatNumber(summaryMetrics.totalOrders?.value || 0),
            change: summaryMetrics.totalOrders?.change || 0,
            icon: Package,
            description: "All channels",
          },
          {
            name: "Avg Order Value",
            value: formatCurrency(summaryMetrics.avgOrderValue?.value || 0),
            change: summaryMetrics.avgOrderValue?.change || 0,
            icon: TrendingUp,
            description: "Per order",
          },
          {
            name: "Conversion Rate",
            value: formatPercentage(summaryMetrics.conversionRate?.value || 0),
            change: summaryMetrics.conversionRate?.change || 0,
            icon: TrendingUp,
            description: "Visitor to customer",
          },
          {
            name: "TikTok Shop Clicks",
            value: formatNumber(tiktokMetrics.shopClicks?.value || 0),
            change: tiktokMetrics.shopClicks?.change || 0,
            icon: ShoppingCart,
            description: "Shop engagement",
          },
          {
            name: "Website Conversions",
            value: formatNumber(websiteMetrics.conversions?.value || 0),
            change: websiteMetrics.conversions?.change || 0,
            icon: ShoppingCart,
            description: "Website sales",
          },
        ],
      },
      {
        id: "email",
        name: "Email Metrics",
        icon: Mail,
        color: "purple",
        description: "Email marketing performance",
        metrics: [
          {
            name: "Active Subscribers",
            value: formatNumber(emailMetrics.subscribers?.value || 0),
            change: emailMetrics.subscribers?.change || 0,
            icon: Users,
            description: "Email list size",
          },
          {
            name: "Open Rate",
            value: formatPercentage(emailMetrics.openRate?.value || 0),
            change: emailMetrics.openRate?.change || 0,
            icon: Eye,
            description: "Email opens",
          },
          {
            name: "Click Rate",
            value: formatPercentage(emailMetrics.clickRate?.value || 0),
            change: emailMetrics.clickRate?.change || 0,
            icon: MousePointerClick,
            description: "Email clicks",
          },
          {
            name: "Email Conversions",
            value: formatNumber(emailMetrics.conversions?.value || 0),
            change: emailMetrics.conversions?.change || 0,
            icon: ShoppingCart,
            description: "Sales from email",
          },
        ],
      },
    ];
  }, [metrics]);

  // Filter categories based on selection
  const filteredCategories = useMemo(
    () =>
      categories.filter((category) =>
        selectedCategories.includes(category.id)
      ),
    [categories, selectedCategories]
  );

  // Toggle category selection
  const toggleCategory = (categoryId: string) => {
    setSelectedCategories((prev) =>
      prev.includes(categoryId)
        ? prev.filter((id) => id !== categoryId)
        : [...prev, categoryId]
    );
  };

  // Get color classes for category
  const getCategoryColorClass = (color: string, type: "bg" | "text") => {
    const colorMap: Record<string, Record<string, string>> = {
      rose: { bg: "bg-rose-100", text: "text-rose-700" },
      blue: { bg: "bg-blue-100", text: "text-blue-700" },
      green: { bg: "bg-green-100", text: "text-green-700" },
      purple: { bg: "bg-purple-100", text: "text-purple-700" },
    };
    return colorMap[color]?.[type] || colorMap.blue[type];
  };

  // Calculate summary statistics
  const summaryStats = useMemo(() => {
    if (!metrics) {
      return {
        totalReach: 0,
        totalRevenue: 0,
        totalConversions: 0,
        avgConversionRate: 0,
      };
    }

    return {
      totalReach: metrics.summary.totalReach?.value || 0,
      totalRevenue: metrics.summary.totalRevenue?.value || 0,
      totalConversions: metrics.summary.totalOrders?.value || 0,
      avgConversionRate: metrics.summary.conversionRate?.value || 0,
    };
  }, [metrics]);

  // Show error state if metrics fetch fails and no fallback available
  if (error && !metrics) {
    return (
      <div className={className}>
        <h2 className="mb-4 text-2xl font-bold text-slate-900">
          Metrics Overview
        </h2>
        <div className="rounded-lg border border-red-200 bg-red-50 p-6">
          <p className="text-sm text-red-600">
            Failed to load metrics: {error.message}
          </p>
          <p className="mt-2 text-xs text-red-500">
            Please check your connection and try again.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className={cn("space-y-6", className)}>
      {/* Fallback data banner */}
      {isFallback && (
        <div className="flex items-center gap-2 rounded-lg border border-amber-200 bg-amber-50 p-3">
          <TrendingUp className="h-4 w-4 flex-shrink-0 text-amber-600" />
          <p className="text-sm text-amber-700">
            Showing cached data. Live metrics are temporarily unavailable.
          </p>
        </div>
      )}

      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-2xl font-bold text-slate-900">Metrics Overview</h2>
          <p className="text-sm text-slate-600">
            Comprehensive analytics across all channels
          </p>
        </div>

        {/* Category Filter Buttons */}
        {showFilters && (
          <div className="flex flex-wrap gap-2">
            {categories.map((category) => {
              const isSelected = selectedCategories.includes(category.id);
              const Icon = category.icon;
              return (
                <button
                  key={category.id}
                  onClick={() => toggleCategory(category.id)}
                  className={cn(
                    "flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                    isSelected
                      ? `${getCategoryColorClass(category.color, "bg")} ${getCategoryColorClass(category.color, "text")}`
                      : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                  )}
                >
                  <Icon className="h-4 w-4" />
                  {category.name.replace(" Metrics", "")}
                </button>
              );
            })}
          </div>
        )}
      </div>

      {/* Summary Stats Header */}
      {!isLoading && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <div className="rounded-lg border border-slate-200 bg-gradient-to-br from-blue-50 to-blue-100 p-4">
            <div className="flex items-center gap-2 text-blue-700">
              <Users className="h-5 w-5" />
              <p className="text-xs font-semibold uppercase tracking-wide">
                Total Reach
              </p>
            </div>
            <p className="mt-2 text-3xl font-bold text-blue-900">
              {formatNumber(summaryStats.totalReach)}
            </p>
          </div>
          <div className="rounded-lg border border-slate-200 bg-gradient-to-br from-green-50 to-green-100 p-4">
            <div className="flex items-center gap-2 text-green-700">
              <DollarSign className="h-5 w-5" />
              <p className="text-xs font-semibold uppercase tracking-wide">
                Total Revenue
              </p>
            </div>
            <p className="mt-2 text-3xl font-bold text-green-900">
              {formatCurrency(summaryStats.totalRevenue)}
            </p>
          </div>
          <div className="rounded-lg border border-slate-200 bg-gradient-to-br from-purple-50 to-purple-100 p-4">
            <div className="flex items-center gap-2 text-purple-700">
              <Package className="h-5 w-5" />
              <p className="text-xs font-semibold uppercase tracking-wide">
                Total Orders
              </p>
            </div>
            <p className="mt-2 text-3xl font-bold text-purple-900">
              {formatNumber(summaryStats.totalConversions)}
            </p>
          </div>
          <div className="rounded-lg border border-slate-200 bg-gradient-to-br from-rose-50 to-rose-100 p-4">
            <div className="flex items-center gap-2 text-rose-700">
              <TrendingUp className="h-5 w-5" />
              <p className="text-xs font-semibold uppercase tracking-wide">
                Conversion Rate
              </p>
            </div>
            <p className="mt-2 text-3xl font-bold text-rose-900">
              {formatPercentage(summaryStats.avgConversionRate)}
            </p>
          </div>
        </div>
      )}

      {/* Category Sections */}
      {filteredCategories.length === 0 ? (
        <div className="rounded-lg border border-slate-200 bg-slate-50 p-8 text-center">
          <p className="text-sm text-slate-600">
            No categories selected. Please select at least one category to view
            metrics.
          </p>
        </div>
      ) : (
        <div className="space-y-8">
          {filteredCategories.map((category) => {
            const Icon = category.icon;
            return (
              <div
                key={category.id}
                className="rounded-lg border border-slate-200 bg-white p-6"
              >
                {/* Category Header */}
                <div className="mb-6 flex items-center gap-3">
                  <div
                    className={cn(
                      "rounded-lg p-3",
                      getCategoryColorClass(category.color, "bg")
                    )}
                  >
                    <Icon
                      className={cn(
                        "h-6 w-6",
                        getCategoryColorClass(category.color, "text")
                      )}
                    />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-slate-900">
                      {category.name}
                    </h3>
                    {category.description && (
                      <p className="text-sm text-slate-600">
                        {category.description}
                      </p>
                    )}
                  </div>
                </div>

                {/* Category Metrics Grid */}
                <div
                  className={cn(
                    "grid gap-4",
                    compact
                      ? "sm:grid-cols-2 lg:grid-cols-4 xl:grid-cols-6"
                      : "sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4"
                  )}
                >
                  {category.metrics.map((metric, index) => (
                    <MetricCard
                      key={index}
                      title={metric.name}
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
          })}
        </div>
      )}

      {/* Performance Insights Footer */}
      {!isLoading && filteredCategories.length > 0 && metrics && (
        <div className="rounded-lg border border-slate-200 bg-slate-50 p-6">
          <h3 className="mb-4 text-sm font-semibold text-slate-700">
            Quick Insights
          </h3>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <div className="flex items-start gap-3 rounded-lg bg-white p-4">
              <div className="rounded-md bg-blue-100 p-2">
                <TrendingUp className="h-5 w-5 text-blue-700" />
              </div>
              <div>
                <p className="text-sm font-medium text-slate-900">
                  Best Performing Channel
                </p>
                <p className="text-xs text-slate-600">
                  {metrics.services.reduce((best, current) => {
                    const bestViews = best.metrics.views?.value || 0;
                    const currentViews = current.metrics.views?.value || 0;
                    return currentViews > bestViews ? current : best;
                  }).service}
                </p>
              </div>
            </div>
            <div className="flex items-start gap-3 rounded-lg bg-white p-4">
              <div className="rounded-md bg-green-100 p-2">
                <DollarSign className="h-5 w-5 text-green-700" />
              </div>
              <div>
                <p className="text-sm font-medium text-slate-900">
                  Revenue Growth
                </p>
                <p className="text-xs text-slate-600">
                  {summaryStats.totalRevenue > 0
                    ? `${(metrics.summary.totalRevenue?.change || 0).toFixed(1)}% vs last period`
                    : "No data yet"}
                </p>
              </div>
            </div>
            <div className="flex items-start gap-3 rounded-lg bg-white p-4">
              <div className="rounded-md bg-purple-100 p-2">
                <Users className="h-5 w-5 text-purple-700" />
              </div>
              <div>
                <p className="text-sm font-medium text-slate-900">
                  Active Categories
                </p>
                <p className="text-xs text-slate-600">
                  {selectedCategories.length} of {categories.length} selected
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
