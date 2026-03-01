"use client";

import { useState } from "react";
import {
  TrendingUp,
  TrendingDown,
  Eye,
  BarChart3,
  ArrowUpRight,
  ArrowDownRight,
  RefreshCw,
} from "lucide-react";

type TimeRange = "7d" | "30d" | "90d";

interface CitationEntry {
  id: string;
  query: string;
  aiPlatform: "chatgpt" | "claude" | "perplexity" | "gemini" | "copilot";
  brandMentioned: boolean;
  brandRecommended: boolean;
  citationPosition: number | null;
  queryCategory: string;
  testDate: string;
}

interface CompetitorData {
  name: string;
  mentionRate: number;
  trend: number;
}

interface PlatformMetric {
  platform: string;
  citationRate: number;
  totalQueries: number;
  mentions: number;
  trend: number;
}

// Mock data - will be replaced with API calls when endpoints are ready
const mockCitations: CitationEntry[] = [
  { id: "1", query: "best ecommerce analytics tools", aiPlatform: "chatgpt", brandMentioned: true, brandRecommended: true, citationPosition: 2, queryCategory: "product_discovery", testDate: "2026-02-27" },
  { id: "2", query: "how to improve customer retention", aiPlatform: "claude", brandMentioned: true, brandRecommended: false, citationPosition: 4, queryCategory: "problem_solving", testDate: "2026-02-27" },
  { id: "3", query: "ecommerce tools comparison 2026", aiPlatform: "perplexity", brandMentioned: false, brandRecommended: false, citationPosition: null, queryCategory: "comparison", testDate: "2026-02-26" },
  { id: "4", query: "top marketing automation platforms", aiPlatform: "gemini", brandMentioned: true, brandRecommended: true, citationPosition: 1, queryCategory: "product_discovery", testDate: "2026-02-26" },
  { id: "5", query: "how to scale email marketing", aiPlatform: "chatgpt", brandMentioned: false, brandRecommended: false, citationPosition: null, queryCategory: "educational", testDate: "2026-02-25" },
  { id: "6", query: "best shopify analytics apps", aiPlatform: "perplexity", brandMentioned: true, brandRecommended: true, citationPosition: 3, queryCategory: "purchase_intent", testDate: "2026-02-25" },
];

const mockPlatformMetrics: PlatformMetric[] = [
  { platform: "ChatGPT", citationRate: 42, totalQueries: 120, mentions: 50, trend: 5.2 },
  { platform: "Claude", citationRate: 38, totalQueries: 85, mentions: 32, trend: 8.1 },
  { platform: "Perplexity", citationRate: 55, totalQueries: 60, mentions: 33, trend: -2.3 },
  { platform: "Gemini", citationRate: 31, totalQueries: 45, mentions: 14, trend: 12.4 },
  { platform: "Copilot", citationRate: 28, totalQueries: 30, mentions: 8, trend: 3.7 },
];

const mockCompetitors: CompetitorData[] = [
  { name: "Competitor A", mentionRate: 62, trend: -3.1 },
  { name: "Competitor B", mentionRate: 45, trend: 2.4 },
  { name: "Competitor C", mentionRate: 38, trend: 7.8 },
  { name: "Competitor D", mentionRate: 22, trend: -1.5 },
];

const platformColors: Record<string, string> = {
  ChatGPT: "bg-green-500",
  Claude: "bg-orange-500",
  Perplexity: "bg-blue-500",
  Gemini: "bg-purple-500",
  Copilot: "bg-cyan-500",
};

export function CitationTracker() {
  const [timeRange, setTimeRange] = useState<TimeRange>("30d");
  const [isRefreshing, setIsRefreshing] = useState(false);

  const overallCitationRate = Math.round(
    mockCitations.filter((c) => c.brandMentioned).length / mockCitations.length * 100
  );

  const handleRefresh = () => {
    setIsRefreshing(true);
    // Simulated refresh - will call API when endpoints are ready
    setTimeout(() => setIsRefreshing(false), 1500);
  };

  return (
    <div className="space-y-6">
      {/* Header with time range selector */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold text-slate-900">Citation Tracking</h2>
          <p className="text-sm text-slate-600">
            Monitor brand mentions across AI platforms
          </p>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex rounded-lg border border-slate-200 bg-white p-1">
            {(["7d", "30d", "90d"] as TimeRange[]).map((range) => (
              <button
                key={range}
                onClick={() => setTimeRange(range)}
                className={`rounded-md px-3 py-1.5 text-sm font-medium transition-colors ${
                  timeRange === range
                    ? "bg-purple-100 text-purple-900"
                    : "text-slate-600 hover:text-slate-900"
                }`}
              >
                {range === "7d" ? "7 Days" : range === "30d" ? "30 Days" : "90 Days"}
              </button>
            ))}
          </div>
          <button
            onClick={handleRefresh}
            disabled={isRefreshing}
            className="flex items-center gap-2 rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-700 hover:bg-slate-50 disabled:opacity-50"
          >
            <RefreshCw className={`h-4 w-4 ${isRefreshing ? "animate-spin" : ""}`} />
            Refresh
          </button>
        </div>
      </div>

      {/* Overview Metrics */}
      <div className="grid gap-4 md:grid-cols-4">
        <div className="rounded-lg border border-slate-200 bg-white p-5">
          <div className="mb-1 flex items-center justify-between">
            <span className="text-sm font-medium text-slate-600">Citation Rate</span>
            <Eye className="h-4 w-4 text-purple-600" />
          </div>
          <div className="text-3xl font-bold text-slate-900">{overallCitationRate}%</div>
          <div className="mt-1 flex items-center gap-1 text-sm text-green-600">
            <ArrowUpRight className="h-3 w-3" />
            +4.2% from last period
          </div>
        </div>
        <div className="rounded-lg border border-slate-200 bg-white p-5">
          <div className="mb-1 flex items-center justify-between">
            <span className="text-sm font-medium text-slate-600">Total Queries Tracked</span>
            <BarChart3 className="h-4 w-4 text-blue-600" />
          </div>
          <div className="text-3xl font-bold text-slate-900">340</div>
          <div className="mt-1 text-sm text-slate-500">Across 5 platforms</div>
        </div>
        <div className="rounded-lg border border-slate-200 bg-white p-5">
          <div className="mb-1 flex items-center justify-between">
            <span className="text-sm font-medium text-slate-600">Avg Position</span>
            <TrendingUp className="h-4 w-4 text-green-600" />
          </div>
          <div className="text-3xl font-bold text-slate-900">2.4</div>
          <div className="mt-1 flex items-center gap-1 text-sm text-green-600">
            <ArrowUpRight className="h-3 w-3" />
            Improved by 0.6
          </div>
        </div>
        <div className="rounded-lg border border-slate-200 bg-white p-5">
          <div className="mb-1 flex items-center justify-between">
            <span className="text-sm font-medium text-slate-600">Recommendations</span>
            <TrendingDown className="h-4 w-4 text-amber-600" />
          </div>
          <div className="text-3xl font-bold text-slate-900">67%</div>
          <div className="mt-1 text-sm text-slate-500">Brand recommended rate</div>
        </div>
      </div>

      {/* Platform Breakdown + Competitor Comparison */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Platform Breakdown */}
        <div className="rounded-lg border border-slate-200 bg-white p-5">
          <h3 className="mb-4 font-semibold text-slate-900">Platform Citation Rates</h3>
          <div className="space-y-4">
            {mockPlatformMetrics.map((metric) => (
              <div key={metric.platform}>
                <div className="mb-1.5 flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className={`h-2.5 w-2.5 rounded-full ${platformColors[metric.platform]}`} />
                    <span className="text-sm font-medium text-slate-900">{metric.platform}</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="text-sm font-semibold text-slate-900">
                      {metric.citationRate}%
                    </span>
                    <span className={`flex items-center text-xs font-medium ${
                      metric.trend >= 0 ? "text-green-600" : "text-red-600"
                    }`}>
                      {metric.trend >= 0 ? (
                        <ArrowUpRight className="h-3 w-3" />
                      ) : (
                        <ArrowDownRight className="h-3 w-3" />
                      )}
                      {Math.abs(metric.trend)}%
                    </span>
                  </div>
                </div>
                <div className="h-2 w-full overflow-hidden rounded-full bg-slate-100">
                  <div
                    className={`h-full rounded-full ${platformColors[metric.platform]}`}
                    style={{ width: `${metric.citationRate}%` }}
                  />
                </div>
                <div className="mt-1 text-xs text-slate-500">
                  {metric.mentions} mentions / {metric.totalQueries} queries
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Competitor Comparison */}
        <div className="rounded-lg border border-slate-200 bg-white p-5">
          <h3 className="mb-4 font-semibold text-slate-900">Competitor Comparison</h3>
          <div className="space-y-3">
            {/* Your brand */}
            <div className="rounded-lg bg-purple-50 p-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="h-3 w-3 rounded-full bg-purple-600" />
                  <span className="text-sm font-semibold text-purple-900">Your Brand</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-lg font-bold text-purple-900">{overallCitationRate}%</span>
                  <span className="flex items-center text-xs font-medium text-green-600">
                    <ArrowUpRight className="h-3 w-3" />
                    4.2%
                  </span>
                </div>
              </div>
              <div className="mt-2 h-2 w-full overflow-hidden rounded-full bg-purple-200">
                <div
                  className="h-full rounded-full bg-purple-600"
                  style={{ width: `${overallCitationRate}%` }}
                />
              </div>
            </div>
            {/* Competitors */}
            {mockCompetitors.map((competitor) => (
              <div key={competitor.name} className="rounded-lg border border-slate-100 p-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className="h-3 w-3 rounded-full bg-slate-400" />
                    <span className="text-sm font-medium text-slate-700">{competitor.name}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-lg font-bold text-slate-900">{competitor.mentionRate}%</span>
                    <span className={`flex items-center text-xs font-medium ${
                      competitor.trend >= 0 ? "text-green-600" : "text-red-600"
                    }`}>
                      {competitor.trend >= 0 ? (
                        <ArrowUpRight className="h-3 w-3" />
                      ) : (
                        <ArrowDownRight className="h-3 w-3" />
                      )}
                      {Math.abs(competitor.trend)}%
                    </span>
                  </div>
                </div>
                <div className="mt-2 h-2 w-full overflow-hidden rounded-full bg-slate-100">
                  <div
                    className="h-full rounded-full bg-slate-400"
                    style={{ width: `${competitor.mentionRate}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Recent Citation Tests */}
      <div className="rounded-lg border border-slate-200 bg-white">
        <div className="border-b border-slate-200 p-4">
          <h3 className="font-semibold text-slate-900">Recent Citation Tests</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-100 text-left">
                <th className="px-4 py-3 text-xs font-medium uppercase text-slate-500">Query</th>
                <th className="px-4 py-3 text-xs font-medium uppercase text-slate-500">Platform</th>
                <th className="px-4 py-3 text-xs font-medium uppercase text-slate-500">Category</th>
                <th className="px-4 py-3 text-xs font-medium uppercase text-slate-500">Cited</th>
                <th className="px-4 py-3 text-xs font-medium uppercase text-slate-500">Position</th>
                <th className="px-4 py-3 text-xs font-medium uppercase text-slate-500">Date</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {mockCitations.map((citation) => (
                <tr key={citation.id} className="hover:bg-slate-50">
                  <td className="max-w-[300px] truncate px-4 py-3 text-sm text-slate-900">
                    {citation.query}
                  </td>
                  <td className="px-4 py-3">
                    <span className="inline-flex items-center gap-1.5 text-sm text-slate-700">
                      <span className={`h-2 w-2 rounded-full ${
                        platformColors[
                          citation.aiPlatform.charAt(0).toUpperCase() + citation.aiPlatform.slice(1)
                        ] || "bg-slate-400"
                      }`} />
                      {citation.aiPlatform.charAt(0).toUpperCase() + citation.aiPlatform.slice(1)}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <span className="rounded-full bg-slate-100 px-2.5 py-0.5 text-xs font-medium text-slate-700">
                      {citation.queryCategory.replace("_", " ")}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    {citation.brandMentioned ? (
                      <span className="inline-flex items-center rounded-full bg-green-50 px-2.5 py-0.5 text-xs font-medium text-green-700">
                        Yes
                        {citation.brandRecommended && " (Recommended)"}
                      </span>
                    ) : (
                      <span className="inline-flex items-center rounded-full bg-red-50 px-2.5 py-0.5 text-xs font-medium text-red-700">
                        No
                      </span>
                    )}
                  </td>
                  <td className="px-4 py-3 text-sm text-slate-900">
                    {citation.citationPosition ? `#${citation.citationPosition}` : "-"}
                  </td>
                  <td className="px-4 py-3 text-sm text-slate-500">{citation.testDate}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
