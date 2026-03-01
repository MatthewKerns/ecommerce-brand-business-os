"use client";

import {
  TrendingUp,
  Eye,
  Heart,
  Share2,
  ShoppingCart,
  Users,
  Mail,
  MousePointerClick,
  DollarSign,
  Package,
  BarChart3,
  Globe,
  LucideIcon,
} from "lucide-react";
import { MetricCard } from "@/components/MetricCard";
import { useMetrics } from "@/hooks/useMetrics";
import { useMemo, useState } from "react";
import { cn } from "@/lib/utils";

/**
 * ChannelDashboard component displays performance metrics across all marketing channels
 *
 * Features:
 * - Multi-channel analytics view (TikTok, Website, Email, Sales)
 * - Channel-specific KPIs with icons and trends
 * - Responsive grid layout (1-4 columns based on screen size)
 * - Real-time data fetching with loading states
 * - Error handling with user-friendly messages
 * - Channel filtering to focus on specific channels
 * - Automatic data refresh support
 * - Color-coded trend indicators
 *
 * @example
 * ```tsx
 * <ChannelDashboard pollingInterval={60000} />
 * ```
 */

export interface ChannelMetric {
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

export interface Channel {
  /** Channel identifier */
  id: string;
  /** Display name */
  name: string;
  /** Channel icon */
  icon: LucideIcon;
  /** Channel metrics */
  metrics: ChannelMetric[];
  /** Channel color for visual distinction */
  color: string;
}

export interface ChannelDashboardProps {
  /** Optional custom className for wrapper */
  className?: string;
  /** Optional polling interval in milliseconds (default: disabled) */
  pollingInterval?: number;
  /** Optional initial channels to display (default: all) */
  defaultChannels?: string[];
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

export function ChannelDashboard({
  className = "",
  pollingInterval,
  defaultChannels = ["tiktok", "website", "email", "sales"],
}: ChannelDashboardProps) {
  // Fetch metrics from API with optional polling
  const { metrics, isLoading, error } = useMetrics({ pollingInterval });

  // State for channel filtering
  const [selectedChannels, setSelectedChannels] =
    useState<string[]>(defaultChannels);

  // Transform API metrics to channel format
  const channels = useMemo<Channel[]>(() => {
    if (!metrics) {
      return [];
    }

    // Find service metrics
    const tiktokService = metrics.services.find((s) => s.service === "tiktok");
    const websiteService = metrics.services.find(
      (s) => s.service === "website"
    );
    const emailService = metrics.services.find((s) => s.service === "email");

    // Extract metrics with fallbacks
    const tiktokMetrics = tiktokService?.metrics || {};
    const websiteMetrics = websiteService?.metrics || {};
    const emailMetrics = emailService?.metrics || {};
    const summaryMetrics = metrics.summary || {};

    return [
      {
        id: "tiktok",
        name: "TikTok",
        icon: BarChart3,
        color: "purple",
        metrics: [
          {
            name: "Total Views",
            value: formatNumber(tiktokMetrics.views?.value || 0),
            change: tiktokMetrics.views?.change || 0,
            icon: Eye,
            description: "Video views",
          },
          {
            name: "Likes",
            value: formatNumber(tiktokMetrics.likes?.value || 0),
            change: tiktokMetrics.likes?.change || 0,
            icon: Heart,
            description: "Total likes",
          },
          {
            name: "Shares",
            value: formatNumber(tiktokMetrics.shares?.value || 0),
            change: tiktokMetrics.shares?.change || 0,
            icon: Share2,
            description: "Content shares",
          },
          {
            name: "Shop Clicks",
            value: formatNumber(tiktokMetrics.shopClicks?.value || 0),
            change: tiktokMetrics.shopClicks?.change || 0,
            icon: ShoppingCart,
            description: "TikTok Shop clicks",
          },
        ],
      },
      {
        id: "website",
        name: "Website",
        icon: Globe,
        color: "blue",
        metrics: [
          {
            name: "Page Views",
            value: formatNumber(websiteMetrics.pageViews?.value || 0),
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
            name: "Conversions",
            value: formatNumber(websiteMetrics.conversions?.value || 0),
            change: websiteMetrics.conversions?.change || 0,
            icon: ShoppingCart,
            description: "Website conversions",
          },
        ],
      },
      {
        id: "email",
        name: "Email",
        icon: Mail,
        color: "green",
        metrics: [
          {
            name: "Subscribers",
            value: formatNumber(emailMetrics.subscribers?.value || 0),
            change: emailMetrics.subscribers?.change || 0,
            icon: Users,
            description: "Active subscribers",
          },
          {
            name: "Open Rate",
            value: formatPercentage(emailMetrics.openRate?.value || 0),
            change: emailMetrics.openRate?.change || 0,
            icon: Eye,
            description: "Email open rate",
          },
          {
            name: "Click Rate",
            value: formatPercentage(emailMetrics.clickRate?.value || 0),
            change: emailMetrics.clickRate?.change || 0,
            icon: MousePointerClick,
            description: "Email click rate",
          },
          {
            name: "Conversions",
            value: formatNumber(emailMetrics.conversions?.value || 0),
            change: emailMetrics.conversions?.change || 0,
            icon: ShoppingCart,
            description: "Email conversions",
          },
        ],
      },
      {
        id: "sales",
        name: "Sales",
        icon: DollarSign,
        color: "orange",
        metrics: [
          {
            name: "Total Revenue",
            value: formatCurrency(summaryMetrics.totalRevenue?.value || 0),
            change: summaryMetrics.totalRevenue?.change || 0,
            icon: DollarSign,
            description: "Last 30 days",
          },
          {
            name: "Orders",
            value: formatNumber(summaryMetrics.totalOrders?.value || 0),
            change: summaryMetrics.totalOrders?.change || 0,
            icon: Package,
            description: "Total orders",
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
        ],
      },
    ];
  }, [metrics]);

  // Filter channels based on selection
  const filteredChannels = useMemo(
    () => channels.filter((channel) => selectedChannels.includes(channel.id)),
    [channels, selectedChannels]
  );

  // Toggle channel selection
  const toggleChannel = (channelId: string) => {
    setSelectedChannels((prev) =>
      prev.includes(channelId)
        ? prev.filter((id) => id !== channelId)
        : [...prev, channelId]
    );
  };

  // Get color classes for channel
  const getChannelColorClass = (color: string, type: "bg" | "text") => {
    const colorMap: Record<string, Record<string, string>> = {
      purple: { bg: "bg-purple-100", text: "text-purple-700" },
      blue: { bg: "bg-blue-100", text: "text-blue-700" },
      green: { bg: "bg-green-100", text: "text-green-700" },
      orange: { bg: "bg-orange-100", text: "text-orange-700" },
    };
    return colorMap[color]?.[type] || colorMap.purple[type];
  };

  // Show error state if metrics fetch fails
  if (error) {
    return (
      <div className={className}>
        <h2 className="mb-4 text-2xl font-bold text-slate-900">
          Channel Performance
        </h2>
        <div className="rounded-lg border border-red-200 bg-red-50 p-6">
          <p className="text-sm text-red-600">
            Failed to load channel metrics: {error.message}
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
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-2xl font-bold text-slate-900">
            Channel Performance
          </h2>
          <p className="text-sm text-slate-600">
            Performance metrics across all marketing channels
          </p>
        </div>

        {/* Channel Filter Buttons */}
        <div className="flex flex-wrap gap-2">
          {channels.map((channel) => {
            const isSelected = selectedChannels.includes(channel.id);
            const Icon = channel.icon;
            return (
              <button
                key={channel.id}
                onClick={() => toggleChannel(channel.id)}
                className={cn(
                  "flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                  isSelected
                    ? `${getChannelColorClass(channel.color, "bg")} ${getChannelColorClass(channel.color, "text")}`
                    : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                )}
              >
                <Icon className="h-4 w-4" />
                {channel.name}
              </button>
            );
          })}
        </div>
      </div>

      {/* Channel Sections */}
      {filteredChannels.length === 0 ? (
        <div className="rounded-lg border border-slate-200 bg-slate-50 p-8 text-center">
          <p className="text-sm text-slate-600">
            No channels selected. Please select at least one channel to view
            metrics.
          </p>
        </div>
      ) : (
        <div className="space-y-8">
          {filteredChannels.map((channel) => {
            const Icon = channel.icon;
            return (
              <div
                key={channel.id}
                className="rounded-lg border border-slate-200 bg-white p-6"
              >
                {/* Channel Header */}
                <div className="mb-6 flex items-center gap-3">
                  <div
                    className={cn(
                      "rounded-lg p-3",
                      getChannelColorClass(channel.color, "bg")
                    )}
                  >
                    <Icon
                      className={cn(
                        "h-6 w-6",
                        getChannelColorClass(channel.color, "text")
                      )}
                    />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-slate-900">
                      {channel.name} Analytics
                    </h3>
                    <p className="text-sm text-slate-600">
                      {channel.metrics.length} key metrics
                    </p>
                  </div>
                </div>

                {/* Channel Metrics Grid */}
                <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
                  {channel.metrics.map((metric, index) => (
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

      {/* Summary Stats Footer */}
      {!isLoading && filteredChannels.length > 0 && metrics && (
        <div className="rounded-lg border border-slate-200 bg-slate-50 p-6">
          <h3 className="mb-4 text-sm font-semibold text-slate-700">
            Cross-Channel Summary
          </h3>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <div className="text-center">
              <p className="text-2xl font-bold text-slate-900">
                {formatNumber(metrics.summary.totalReach?.value || 0)}
              </p>
              <p className="text-xs text-slate-600">Total Reach</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-slate-900">
                {formatCurrency(metrics.summary.totalRevenue?.value || 0)}
              </p>
              <p className="text-xs text-slate-600">Total Revenue</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-slate-900">
                {formatPercentage(metrics.summary.conversionRate?.value || 0)}
              </p>
              <p className="text-xs text-slate-600">Avg Conversion Rate</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-slate-900">
                {selectedChannels.length}
              </p>
              <p className="text-xs text-slate-600">Active Channels</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
