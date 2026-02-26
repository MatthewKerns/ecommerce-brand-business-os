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

/**
 * KPIOverview component displays key performance indicators grid
 *
 * Features:
 * - Displays 6 key metrics across all organic marketing channels
 * - Responsive grid layout (1 col mobile, 2 col tablet, 3 col desktop)
 * - TikTok views, email subscribers, blog traffic, revenue, conversion rate, total reach
 * - Loading state support for all metrics
 * - Color-coded trend indicators
 *
 * @example
 * ```tsx
 * <KPIOverview isLoading={false} />
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
  /** Loading state - shows skeleton when true */
  isLoading?: boolean;
  /** Optional custom metrics data - defaults to example data */
  metrics?: KPIMetric[];
  /** Optional custom className for grid wrapper */
  className?: string;
}

// Default metrics data
const DEFAULT_METRICS: KPIMetric[] = [
  {
    title: "TikTok Views",
    value: "124.5K",
    change: 12.5,
    icon: Eye,
    description: "Total video views",
  },
  {
    title: "Email Subscribers",
    value: "3,452",
    change: 8.2,
    icon: Mail,
    description: "Active subscribers",
  },
  {
    title: "Blog Traffic",
    value: "45.2K",
    change: -3.1,
    icon: FileText,
    description: "Monthly visitors",
  },
  {
    title: "Revenue",
    value: "$12,543",
    change: 15.8,
    icon: DollarSign,
    description: "Last 30 days",
  },
  {
    title: "Conversion Rate",
    value: "3.2%",
    change: 0.5,
    icon: TrendingUp,
    description: "Visitor to customer",
  },
  {
    title: "Total Reach",
    value: "89.3K",
    change: 22.1,
    icon: Users,
    description: "Across all channels",
  },
];

export function KPIOverview({
  isLoading = false,
  metrics = DEFAULT_METRICS,
  className = "",
}: KPIOverviewProps) {
  return (
    <div className={className}>
      <h2 className="mb-4 text-lg font-semibold text-slate-900">
        Key Performance Indicators
      </h2>
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {metrics.map((metric, index) => (
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
