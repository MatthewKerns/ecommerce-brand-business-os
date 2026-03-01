"use client";

import { useState } from "react";
import {
  Search,
  Sparkles,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  ChevronDown,
  ChevronUp,
  ExternalLink,
  Zap,
} from "lucide-react";

type ScoreStatus = "excellent" | "good" | "needs-work" | "critical";

interface ContentItem {
  id: string;
  title: string;
  url: string;
  seoScore: number;
  aeoScore: number;
  overallScore: number;
  status: ScoreStatus;
  lastAnalyzed: string;
  optimizations: OptimizationItem[];
}

interface OptimizationItem {
  id: string;
  category: "structure" | "content" | "technical" | "keyword";
  title: string;
  description: string;
  impact: "high" | "medium" | "low";
  currentValue: string;
  suggestedValue: string;
  applied: boolean;
}

// Mock data - will be replaced with API calls when AEO Scoring Engine is ready
const mockContentItems: ContentItem[] = [
  {
    id: "1",
    title: "Ultimate Guide to Product Analytics",
    url: "/blog/product-analytics-guide",
    seoScore: 85,
    aeoScore: 72,
    overallScore: 79,
    status: "good",
    lastAnalyzed: "2 hours ago",
    optimizations: [
      {
        id: "o1",
        category: "structure",
        title: "Add FAQ Schema Markup",
        description: "Structured FAQ data helps AI assistants extract and cite your answers directly.",
        impact: "high",
        currentValue: "No FAQ schema detected",
        suggestedValue: "Add 5-8 FAQ items with concise answers",
        applied: false,
      },
      {
        id: "o2",
        category: "content",
        title: "Improve Answer Conciseness",
        description: "AI assistants prefer concise, directly answerable paragraphs.",
        impact: "medium",
        currentValue: "Average paragraph: 180 words",
        suggestedValue: "Target 80-120 words per paragraph",
        applied: false,
      },
      {
        id: "o3",
        category: "keyword",
        title: "Add Question-Based Headers",
        description: "Headers formatted as questions improve AI snippet extraction.",
        impact: "high",
        currentValue: "2/8 headers are questions",
        suggestedValue: "Convert 4+ headers to question format",
        applied: true,
      },
    ],
  },
  {
    id: "2",
    title: "How to Scale Your E-commerce Business",
    url: "/blog/scale-ecommerce",
    seoScore: 78,
    aeoScore: 55,
    overallScore: 67,
    status: "needs-work",
    lastAnalyzed: "1 day ago",
    optimizations: [
      {
        id: "o4",
        category: "technical",
        title: "Add Entity Relationships",
        description: "Define clear entity connections to help AI understand content context.",
        impact: "high",
        currentValue: "No entity schema",
        suggestedValue: "Add Organization, Product, HowTo schemas",
        applied: false,
      },
      {
        id: "o5",
        category: "content",
        title: "Include Statistical Evidence",
        description: "AI assistants favor content with cited statistics and data points.",
        impact: "medium",
        currentValue: "3 data points",
        suggestedValue: "Include 8-12 cited statistics",
        applied: false,
      },
    ],
  },
  {
    id: "3",
    title: "Customer Retention Strategies for 2026",
    url: "/blog/customer-retention",
    seoScore: 92,
    aeoScore: 88,
    overallScore: 90,
    status: "excellent",
    lastAnalyzed: "4 hours ago",
    optimizations: [
      {
        id: "o6",
        category: "keyword",
        title: "Add Comparison Table",
        description: "Structured comparison tables are frequently cited by AI assistants.",
        impact: "low",
        currentValue: "No comparison tables",
        suggestedValue: "Add strategy comparison table",
        applied: false,
      },
    ],
  },
  {
    id: "4",
    title: "Email Marketing Automation Best Practices",
    url: "/blog/email-automation",
    seoScore: 45,
    aeoScore: 32,
    overallScore: 39,
    status: "critical",
    lastAnalyzed: "3 days ago",
    optimizations: [
      {
        id: "o7",
        category: "structure",
        title: "Restructure Content Hierarchy",
        description: "Content lacks clear hierarchy for AI extraction.",
        impact: "high",
        currentValue: "Flat content structure",
        suggestedValue: "Implement H2/H3/H4 hierarchy with clear sections",
        applied: false,
      },
      {
        id: "o8",
        category: "content",
        title: "Add Definitive Statements",
        description: "AI assistants prefer authoritative, definitive answers over hedged language.",
        impact: "high",
        currentValue: "12 hedging phrases detected",
        suggestedValue: "Replace with confident, authoritative language",
        applied: false,
      },
      {
        id: "o9",
        category: "technical",
        title: "Add Breadcrumb Schema",
        description: "Breadcrumb schema helps AI understand content hierarchy and context.",
        impact: "medium",
        currentValue: "No breadcrumb markup",
        suggestedValue: "Add BreadcrumbList structured data",
        applied: false,
      },
    ],
  },
];

function getStatusConfig(status: ScoreStatus) {
  switch (status) {
    case "excellent":
      return { color: "text-green-700", bg: "bg-green-50", border: "border-green-200", icon: CheckCircle2, label: "Excellent" };
    case "good":
      return { color: "text-blue-700", bg: "bg-blue-50", border: "border-blue-200", icon: CheckCircle2, label: "Good" };
    case "needs-work":
      return { color: "text-amber-700", bg: "bg-amber-50", border: "border-amber-200", icon: AlertTriangle, label: "Needs Work" };
    case "critical":
      return { color: "text-red-700", bg: "bg-red-50", border: "border-red-200", icon: XCircle, label: "Critical" };
  }
}

function getImpactBadge(impact: "high" | "medium" | "low") {
  switch (impact) {
    case "high":
      return "bg-red-100 text-red-800";
    case "medium":
      return "bg-amber-100 text-amber-800";
    case "low":
      return "bg-slate-100 text-slate-700";
  }
}

function getScoreColor(score: number): string {
  if (score >= 80) return "text-green-600";
  if (score >= 60) return "text-blue-600";
  if (score >= 40) return "text-amber-600";
  return "text-red-600";
}

function getBarColor(score: number): string {
  if (score >= 80) return "bg-green-500";
  if (score >= 60) return "bg-blue-500";
  if (score >= 40) return "bg-amber-500";
  return "bg-red-500";
}

export function ContentOptimizationPanel() {
  const [expandedItem, setExpandedItem] = useState<string | null>(null);
  const [filterStatus, setFilterStatus] = useState<ScoreStatus | "all">("all");
  const [searchQuery, setSearchQuery] = useState("");

  const filteredItems = mockContentItems.filter((item) => {
    if (filterStatus !== "all" && item.status !== filterStatus) return false;
    if (searchQuery && !item.title.toLowerCase().includes(searchQuery.toLowerCase())) return false;
    return true;
  });

  const avgSeoScore = Math.round(
    mockContentItems.reduce((sum, item) => sum + item.seoScore, 0) / mockContentItems.length
  );
  const avgAeoScore = Math.round(
    mockContentItems.reduce((sum, item) => sum + item.aeoScore, 0) / mockContentItems.length
  );
  const totalOptimizations = mockContentItems.reduce(
    (sum, item) => sum + item.optimizations.filter((o) => !o.applied).length,
    0
  );

  return (
    <div className="space-y-6">
      {/* Score Overview */}
      <div className="grid gap-4 md:grid-cols-3">
        <div className="rounded-lg border border-slate-200 bg-white p-5">
          <div className="mb-2 text-sm font-medium text-slate-600">Avg SEO Score</div>
          <div className="flex items-baseline gap-2">
            <span className={`text-3xl font-bold ${getScoreColor(avgSeoScore)}`}>{avgSeoScore}</span>
            <span className="text-sm text-slate-500">/100</span>
          </div>
          <div className="mt-3 h-2 w-full overflow-hidden rounded-full bg-slate-100">
            <div className={`h-full rounded-full ${getBarColor(avgSeoScore)}`} style={{ width: `${avgSeoScore}%` }} />
          </div>
        </div>
        <div className="rounded-lg border border-slate-200 bg-white p-5">
          <div className="mb-2 text-sm font-medium text-slate-600">Avg AEO Score</div>
          <div className="flex items-baseline gap-2">
            <span className={`text-3xl font-bold ${getScoreColor(avgAeoScore)}`}>{avgAeoScore}</span>
            <span className="text-sm text-slate-500">/100</span>
          </div>
          <div className="mt-3 h-2 w-full overflow-hidden rounded-full bg-slate-100">
            <div className={`h-full rounded-full ${getBarColor(avgAeoScore)}`} style={{ width: `${avgAeoScore}%` }} />
          </div>
        </div>
        <div className="rounded-lg border border-slate-200 bg-white p-5">
          <div className="mb-2 text-sm font-medium text-slate-600">Pending Optimizations</div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-bold text-amber-600">{totalOptimizations}</span>
            <span className="text-sm text-slate-500">improvements</span>
          </div>
          <div className="mt-2 text-sm text-slate-500">
            {mockContentItems.filter((i) => i.status === "critical").length} critical items
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap items-center gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            placeholder="Search content..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full rounded-lg border border-slate-200 py-2 pl-9 pr-4 text-sm text-slate-900 placeholder:text-slate-400 focus:border-purple-300 focus:outline-none focus:ring-2 focus:ring-purple-100"
          />
        </div>
        <div className="flex rounded-lg border border-slate-200 bg-white p-1">
          {(["all", "critical", "needs-work", "good", "excellent"] as const).map((status) => (
            <button
              key={status}
              onClick={() => setFilterStatus(status)}
              className={`rounded-md px-3 py-1.5 text-sm font-medium transition-colors ${
                filterStatus === status
                  ? "bg-purple-100 text-purple-900"
                  : "text-slate-600 hover:text-slate-900"
              }`}
            >
              {status === "all" ? "All" : status === "needs-work" ? "Needs Work" : status.charAt(0).toUpperCase() + status.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Content Items */}
      <div className="space-y-3">
        {filteredItems.map((item) => {
          const statusConfig = getStatusConfig(item.status);
          const StatusIcon = statusConfig.icon;
          const isExpanded = expandedItem === item.id;

          return (
            <div key={item.id} className="rounded-lg border border-slate-200 bg-white">
              {/* Content Header */}
              <button
                onClick={() => setExpandedItem(isExpanded ? null : item.id)}
                className="flex w-full items-center justify-between p-4 text-left"
              >
                <div className="flex-1">
                  <div className="flex items-center gap-3">
                    <h3 className="font-medium text-slate-900">{item.title}</h3>
                    <span className={`inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-medium ${statusConfig.bg} ${statusConfig.color}`}>
                      <StatusIcon className="h-3 w-3" />
                      {statusConfig.label}
                    </span>
                  </div>
                  <div className="mt-1 flex items-center gap-4 text-sm text-slate-500">
                    <span className="flex items-center gap-1">
                      <ExternalLink className="h-3 w-3" />
                      {item.url}
                    </span>
                    <span>Analyzed {item.lastAnalyzed}</span>
                  </div>
                </div>
                <div className="ml-6 flex items-center gap-6">
                  {/* Dual Score Display */}
                  <div className="flex items-center gap-4">
                    <div className="text-center">
                      <div className={`text-lg font-bold ${getScoreColor(item.seoScore)}`}>{item.seoScore}</div>
                      <div className="text-xs text-slate-500">SEO</div>
                    </div>
                    <div className="h-8 w-px bg-slate-200" />
                    <div className="text-center">
                      <div className={`text-lg font-bold ${getScoreColor(item.aeoScore)}`}>{item.aeoScore}</div>
                      <div className="text-xs text-slate-500">AEO</div>
                    </div>
                  </div>
                  {item.optimizations.filter((o) => !o.applied).length > 0 && (
                    <span className="rounded-full bg-amber-100 px-2 py-0.5 text-xs font-medium text-amber-800">
                      {item.optimizations.filter((o) => !o.applied).length} fixes
                    </span>
                  )}
                  {isExpanded ? (
                    <ChevronUp className="h-5 w-5 text-slate-400" />
                  ) : (
                    <ChevronDown className="h-5 w-5 text-slate-400" />
                  )}
                </div>
              </button>

              {/* Expanded Optimization Details */}
              {isExpanded && (
                <div className="border-t border-slate-200 p-4">
                  {/* Score Bars */}
                  <div className="mb-6 grid gap-4 md:grid-cols-2">
                    <div>
                      <div className="mb-1 flex items-center justify-between text-sm">
                        <span className="text-slate-600">SEO Score</span>
                        <span className={`font-semibold ${getScoreColor(item.seoScore)}`}>{item.seoScore}/100</span>
                      </div>
                      <div className="h-3 w-full overflow-hidden rounded-full bg-slate-100">
                        <div className={`h-full rounded-full ${getBarColor(item.seoScore)}`} style={{ width: `${item.seoScore}%` }} />
                      </div>
                    </div>
                    <div>
                      <div className="mb-1 flex items-center justify-between text-sm">
                        <span className="text-slate-600">AEO Score</span>
                        <span className={`font-semibold ${getScoreColor(item.aeoScore)}`}>{item.aeoScore}/100</span>
                      </div>
                      <div className="h-3 w-full overflow-hidden rounded-full bg-slate-100">
                        <div className={`h-full rounded-full ${getBarColor(item.aeoScore)}`} style={{ width: `${item.aeoScore}%` }} />
                      </div>
                    </div>
                  </div>

                  {/* Optimization Suggestions */}
                  <h4 className="mb-3 text-sm font-semibold text-slate-900">Optimization Suggestions</h4>
                  <div className="space-y-3">
                    {item.optimizations.map((opt) => (
                      <div
                        key={opt.id}
                        className={`rounded-lg border p-4 ${
                          opt.applied ? "border-green-200 bg-green-50" : "border-slate-200"
                        }`}
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center gap-2">
                              <h5 className="text-sm font-medium text-slate-900">{opt.title}</h5>
                              <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${getImpactBadge(opt.impact)}`}>
                                {opt.impact} impact
                              </span>
                              <span className="rounded-full bg-slate-100 px-2 py-0.5 text-xs font-medium text-slate-600">
                                {opt.category}
                              </span>
                            </div>
                            <p className="mt-1 text-sm text-slate-600">{opt.description}</p>
                            <div className="mt-2 grid gap-2 md:grid-cols-2">
                              <div className="text-xs">
                                <span className="text-slate-500">Current: </span>
                                <span className="text-slate-700">{opt.currentValue}</span>
                              </div>
                              <div className="text-xs">
                                <span className="text-slate-500">Suggested: </span>
                                <span className="font-medium text-purple-700">{opt.suggestedValue}</span>
                              </div>
                            </div>
                          </div>
                          {opt.applied ? (
                            <span className="flex items-center gap-1 rounded-full bg-green-100 px-3 py-1 text-xs font-medium text-green-700">
                              <CheckCircle2 className="h-3 w-3" />
                              Applied
                            </span>
                          ) : (
                            <button className="flex items-center gap-1 rounded-lg bg-purple-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-purple-700">
                              <Zap className="h-3 w-3" />
                              Apply Fix
                            </button>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>

                  {/* Quick Actions */}
                  <div className="mt-4 flex items-center gap-3">
                    <button className="flex items-center gap-2 rounded-lg bg-purple-600 px-4 py-2 text-sm font-medium text-white hover:bg-purple-700">
                      <Sparkles className="h-4 w-4" />
                      Apply All Fixes
                    </button>
                    <button className="flex items-center gap-2 rounded-lg border border-slate-200 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50">
                      Re-analyze Content
                    </button>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
