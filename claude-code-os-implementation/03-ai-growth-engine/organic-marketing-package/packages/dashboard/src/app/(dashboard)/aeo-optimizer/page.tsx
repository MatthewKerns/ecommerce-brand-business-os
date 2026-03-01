"use client";

import { useState } from "react";
import {
  Target,
  TrendingUp,
  Search,
  Brain,
  Sparkles,
  CheckCircle,
  AlertCircle,
  Eye,
  FileText,
  Settings,
} from "lucide-react";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { MetricsErrorBoundary } from "@/components/error-boundaries";
import { CitationTracker } from "@/components/aeo/CitationTracker";
import { ContentOptimizationPanel } from "@/components/aeo/ContentOptimizationPanel";
import { BlogContentGenerator } from "@/components/aeo/BlogContentGenerator";

/**
 * AEO (Answer Engine Optimization) Dashboard Page
 *
 * Optimizes content for AI-powered search engines and answer engines like:
 * - Google's AI Overviews
 * - ChatGPT, Claude, and other LLMs
 * - Perplexity AI
 * - Bing Chat
 *
 * Features:
 * - Citation Tracking Dashboard: Real-time monitoring, trend graphs, competitor comparison
 * - Content Optimization Panel: Dual SEO/AEO scores, optimization previews
 * - Blog Content Generator: Generate citation-optimized posts
 * - AI Platform Coverage overview
 *
 * @route /aeo-optimizer
 */

function AEOOptimizerContent() {
  const [activeTab, setActiveTab] = useState("overview");

  // Overview metrics (aggregated from sub-components)
  const overviewMetrics = {
    aeoScore: 73.5,
    aeoScoreTrend: 5.2,
    citationRate: 42,
    citationRateTrend: 4.2,
    optimizedPages: { done: 42, total: 58 },
    pendingOptimizations: 23,
  };

  const aiPlatformCoverage = [
    { name: "Google AI", coverage: 85, queries: 180, trend: 3.1 },
    { name: "ChatGPT", coverage: 78, queries: 120, trend: 5.2 },
    { name: "Perplexity", coverage: 72, queries: 60, trend: -2.3 },
    { name: "Claude", coverage: 69, queries: 85, trend: 8.1 },
  ];

  const optimizationFactors = [
    { name: "Structured Data", status: "good" as const, score: 90, description: "Schema markup is properly implemented" },
    { name: "Entity Coverage", status: "warning" as const, score: 65, description: "Missing key entity relationships" },
    { name: "Answer Snippets", status: "good" as const, score: 85, description: "Clear, concise answers to user queries" },
    { name: "Topic Authority", status: "critical" as const, score: 40, description: "Low topical authority signals" },
    { name: "FAQ Schema", status: "good" as const, score: 88, description: "Comprehensive FAQ coverage" },
    { name: "Citation Quality", status: "warning" as const, score: 72, description: "Needs more authoritative sources" },
  ];

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 p-3">
            <Target className="h-6 w-6 text-white" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-slate-900">AEO Optimizer</h1>
            <p className="text-sm text-slate-600">
              Optimize content for AI-powered answer engines
            </p>
          </div>
        </div>
        <div className="flex gap-3">
          <button className="flex items-center gap-2 rounded-lg border border-slate-200 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50">
            <Brain className="h-4 w-4" />
            AI Analysis
          </button>
          <button className="flex items-center gap-2 rounded-lg bg-purple-600 px-4 py-2 text-sm font-medium text-white hover:bg-purple-700">
            <Sparkles className="h-4 w-4" />
            Bulk Optimize
          </button>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <div className="rounded-lg border border-slate-200 bg-white p-6">
          <div className="mb-2 flex items-center justify-between">
            <span className="text-sm font-medium text-slate-600">AEO Score</span>
            <TrendingUp className="h-4 w-4 text-green-600" />
          </div>
          <div className="mb-2 text-3xl font-bold text-slate-900">{overviewMetrics.aeoScore}</div>
          <div className="text-sm text-green-600">+{overviewMetrics.aeoScoreTrend} from last week</div>
        </div>
        <div className="rounded-lg border border-slate-200 bg-white p-6">
          <div className="mb-2 flex items-center justify-between">
            <span className="text-sm font-medium text-slate-600">Citation Rate</span>
            <Eye className="h-4 w-4 text-purple-600" />
          </div>
          <div className="mb-2 text-3xl font-bold text-slate-900">{overviewMetrics.citationRate}%</div>
          <div className="text-sm text-green-600">+{overviewMetrics.citationRateTrend}% from last period</div>
        </div>
        <div className="rounded-lg border border-slate-200 bg-white p-6">
          <div className="mb-2 flex items-center justify-between">
            <span className="text-sm font-medium text-slate-600">Optimized Pages</span>
            <CheckCircle className="h-4 w-4 text-green-600" />
          </div>
          <div className="mb-2 text-3xl font-bold text-slate-900">
            {overviewMetrics.optimizedPages.done}/{overviewMetrics.optimizedPages.total}
          </div>
          <div className="text-sm text-slate-600">
            {Math.round((overviewMetrics.optimizedPages.done / overviewMetrics.optimizedPages.total) * 100)}% completion
          </div>
        </div>
        <div className="rounded-lg border border-slate-200 bg-white p-6">
          <div className="mb-2 flex items-center justify-between">
            <span className="text-sm font-medium text-slate-600">Opportunities</span>
            <AlertCircle className="h-4 w-4 text-amber-600" />
          </div>
          <div className="mb-2 text-3xl font-bold text-slate-900">{overviewMetrics.pendingOptimizations}</div>
          <div className="text-sm text-amber-600">High-impact fixes</div>
        </div>
      </div>

      {/* Tabbed Content */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="w-full justify-start gap-1 bg-slate-100 p-1">
          <TabsTrigger value="overview" className="flex items-center gap-2">
            <Search className="h-4 w-4" />
            Overview
          </TabsTrigger>
          <TabsTrigger value="citations" className="flex items-center gap-2">
            <Eye className="h-4 w-4" />
            Citation Tracking
          </TabsTrigger>
          <TabsTrigger value="optimization" className="flex items-center gap-2">
            <Settings className="h-4 w-4" />
            Content Optimization
          </TabsTrigger>
          <TabsTrigger value="generator" className="flex items-center gap-2">
            <FileText className="h-4 w-4" />
            Blog Generator
          </TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview">
          <div className="space-y-6 pt-4">
            {/* AI Platform Coverage */}
            <div className="rounded-lg border border-slate-200 bg-white p-6">
              <h2 className="mb-4 text-lg font-semibold text-slate-900">
                AI Platform Coverage
              </h2>
              <div className="grid gap-6 md:grid-cols-4">
                {aiPlatformCoverage.map((platform) => (
                  <div key={platform.name} className="rounded-lg border border-slate-100 p-4 text-center">
                    <div className="mb-2 text-sm font-medium text-slate-700">
                      {platform.name}
                    </div>
                    <div className="mb-1 text-3xl font-bold text-slate-900">
                      {platform.coverage}%
                    </div>
                    <div className="mb-2 text-xs text-slate-500">
                      {platform.queries} queries tracked
                    </div>
                    <div className={`text-xs font-medium ${
                      platform.trend >= 0 ? "text-green-600" : "text-red-600"
                    }`}>
                      {platform.trend >= 0 ? "+" : ""}{platform.trend}% trend
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Optimization Factors */}
            <div className="rounded-lg border border-slate-200 bg-white p-6">
              <h2 className="mb-4 text-lg font-semibold text-slate-900">
                AEO Optimization Factors
              </h2>
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {optimizationFactors.map((factor) => (
                  <div key={factor.name} className="rounded-lg border border-slate-200 p-4">
                    <div className="mb-2 flex items-center justify-between">
                      <span className="font-medium text-slate-900">{factor.name}</span>
                      <div
                        className={`h-2 w-2 rounded-full ${
                          factor.status === "good" ? "bg-green-500" :
                          factor.status === "warning" ? "bg-amber-500" :
                          "bg-red-500"
                        }`}
                      />
                    </div>
                    <div className="mb-2">
                      <div className="flex items-baseline gap-1">
                        <span className="text-2xl font-bold text-slate-900">{factor.score}</span>
                        <span className="text-sm text-slate-600">/100</span>
                      </div>
                    </div>
                    <p className="text-xs text-slate-600">{factor.description}</p>
                    <div className="mt-3 h-2 w-full overflow-hidden rounded-full bg-slate-200">
                      <div
                        className={`h-full rounded-full ${
                          factor.status === "good" ? "bg-green-500" :
                          factor.status === "warning" ? "bg-amber-500" :
                          "bg-red-500"
                        }`}
                        style={{ width: `${factor.score}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </TabsContent>

        {/* Citation Tracking Tab */}
        <TabsContent value="citations">
          <div className="pt-4">
            <CitationTracker />
          </div>
        </TabsContent>

        {/* Content Optimization Tab */}
        <TabsContent value="optimization">
          <div className="pt-4">
            <ContentOptimizationPanel />
          </div>
        </TabsContent>

        {/* Blog Generator Tab */}
        <TabsContent value="generator">
          <div className="pt-4">
            <BlogContentGenerator />
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}

export default function AEOOptimizerPage() {
  return (
    <MetricsErrorBoundary>
      <AEOOptimizerContent />
    </MetricsErrorBoundary>
  );
}
