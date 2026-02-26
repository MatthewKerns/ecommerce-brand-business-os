import {
  LayoutDashboard,
  Eye,
  Mail,
  FileText,
  DollarSign,
  Users,
  TrendingUp,
} from "lucide-react";
import { MetricCard } from "@/components/MetricCard";

/**
 * Main Dashboard Page
 *
 * Central hub displaying overview of all organic marketing components.
 *
 * Features:
 * - KPI overview cards showing key metrics
 * - Recent activity feed
 * - Quick access to system health
 * - Performance charts and visualizations
 *
 * @route /
 */
export default function DashboardPage() {
  // Example metric data - in production, this would come from API
  const metrics = [
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

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center gap-3">
        <div className="rounded-lg bg-slate-100 p-3">
          <LayoutDashboard className="h-6 w-6 text-slate-700" />
        </div>
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Dashboard</h1>
          <p className="text-sm text-slate-600">
            Overview of your organic marketing performance
          </p>
        </div>
      </div>

      {/* KPI Overview */}
      <div>
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
            />
          ))}
        </div>
      </div>

      {/* Loading State Demo */}
      <div>
        <h2 className="mb-4 text-lg font-semibold text-slate-900">
          Loading State Demo
        </h2>
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          <MetricCard
            title="Loading Metric"
            value="0"
            isLoading={true}
          />
          <MetricCard
            title="Loading Metric"
            value="0"
            isLoading={true}
          />
          <MetricCard
            title="Loading Metric"
            value="0"
            isLoading={true}
          />
        </div>
      </div>
    </div>
  );
}
