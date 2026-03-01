"use client";

import {
  LayoutDashboard,
  TrendingUp,
  Users,
  Video,
  FileText,
  Activity,
  ArrowUpRight,
  ArrowDownRight,
  Clock
} from "lucide-react";
import { KPIOverview } from "@/components/KPIOverview";
import Link from "next/link";

/**
 * Main Dashboard Page
 *
 * Central hub displaying overview of all organic marketing components.
 *
 * Features:
 * - KPI overview cards showing key metrics
 * - Quick access to content tools
 * - System health overview
 * - Recent activity summary
 *
 * @route /
 */
export default function DashboardPage() {
  // Sample data - in production, this would come from your API
  const recentMetrics = {
    contentGenerated: 24,
    videosCreated: 8,
    emailsSent: 156,
    engagementRate: 4.2,
  };

  const quickStats = [
    {
      label: "Content Generated",
      value: "24",
      change: "+12%",
      trend: "up",
      period: "this week"
    },
    {
      label: "Videos Created",
      value: "8",
      change: "+5%",
      trend: "up",
      period: "this week"
    },
    {
      label: "Engagement Rate",
      value: "4.2%",
      change: "-0.3%",
      trend: "down",
      period: "vs last week"
    },
    {
      label: "Active Campaigns",
      value: "12",
      change: "+2",
      trend: "up",
      period: "running"
    },
  ];

  const contentTools = [
    {
      title: "TikTok Content Studio",
      description: "Create viral scripts and manage video content",
      icon: Video,
      href: "/tiktok",
      color: "bg-purple-100 text-purple-700",
      stats: "8 videos this week"
    },
    {
      title: "Blog Engine",
      description: "Generate SEO-optimized blog posts",
      icon: FileText,
      href: "/blog",
      color: "bg-blue-100 text-blue-700",
      stats: "16 posts published"
    },
    {
      title: "Email Automation",
      description: "Manage email campaigns and sequences",
      icon: Users,
      href: "/email",
      color: "bg-green-100 text-green-700",
      stats: "156 emails sent"
    },
    {
      title: "Analytics",
      description: "Track performance across all channels",
      icon: Activity,
      href: "/analytics",
      color: "bg-orange-100 text-orange-700",
      stats: "Real-time metrics"
    },
  ];

  return (
    <div className="space-y-8">
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

      {/* Quick Stats */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {quickStats.map((stat, index) => (
          <div key={index} className="rounded-lg border border-slate-200 bg-white p-6">
            <div className="flex items-center justify-between">
              <p className="text-sm font-medium text-slate-600">{stat.label}</p>
              <span className="text-xs text-slate-500">{stat.period}</span>
            </div>
            <div className="mt-2 flex items-baseline gap-2">
              <p className="text-2xl font-bold text-slate-900">{stat.value}</p>
              <span className={`flex items-center text-sm font-medium ${
                stat.trend === 'up' ? 'text-green-600' : 'text-red-600'
              }`}>
                {stat.trend === 'up' ? <ArrowUpRight className="h-3 w-3" /> : <ArrowDownRight className="h-3 w-3" />}
                {stat.change}
              </span>
            </div>
          </div>
        ))}
      </div>

      {/* KPI Overview */}
      <KPIOverview />

      {/* Content Tools */}
      <div className="space-y-4">
        <div>
          <h2 className="text-lg font-semibold text-slate-900">Content Tools</h2>
          <p className="text-sm text-slate-600">Quick access to your marketing tools</p>
        </div>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {contentTools.map((tool, index) => (
            <Link
              key={index}
              href={tool.href}
              className="group relative rounded-lg border border-slate-200 bg-white p-6 transition-all hover:border-slate-300 hover:shadow-md"
            >
              <div className={`inline-flex rounded-lg p-3 ${tool.color}`}>
                <tool.icon className="h-6 w-6" />
              </div>
              <h3 className="mt-4 font-semibold text-slate-900 group-hover:text-slate-700">
                {tool.title}
              </h3>
              <p className="mt-1 text-sm text-slate-600">{tool.description}</p>
              <div className="mt-3 flex items-center gap-1 text-xs text-slate-500">
                <Clock className="h-3 w-3" />
                {tool.stats}
              </div>
            </Link>
          ))}
        </div>
      </div>

      {/* System Status */}
      <div className="rounded-lg border border-slate-200 bg-white p-6">
        <div className="mb-4 flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-slate-900">System Status</h2>
            <p className="text-sm text-slate-600">All services operational</p>
          </div>
          <Link
            href="/monitoring"
            className="text-sm font-medium text-blue-600 hover:text-blue-700"
          >
            View Details →
          </Link>
        </div>
        <div className="grid gap-2 md:grid-cols-3">
          <div className="flex items-center gap-2">
            <div className="h-2 w-2 rounded-full bg-green-500"></div>
            <span className="text-sm text-slate-700">TikTok API</span>
            <span className="text-xs text-slate-500">Operational</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="h-2 w-2 rounded-full bg-green-500"></div>
            <span className="text-sm text-slate-700">Python Agents</span>
            <span className="text-xs text-slate-500">Running</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="h-2 w-2 rounded-full bg-green-500"></div>
            <span className="text-sm text-slate-700">Database</span>
            <span className="text-xs text-slate-500">Connected</span>
          </div>
        </div>
      </div>
    </div>
  );
}
