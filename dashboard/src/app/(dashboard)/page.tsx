"use client";

import { LayoutDashboard } from "lucide-react";
import { KPIOverview } from "@/components/KPIOverview";
import { LoadingCard } from "@/components/LoadingCard";
import {
  SkeletonLoader,
  SkeletonText,
  SkeletonAvatar,
  SkeletonCard,
} from "@/components/SkeletonLoader";
import { useState } from "react";

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
 * - Loading state demonstrations
 *
 * @route /
 */
export default function DashboardPage() {
  const [showLoadingDemo, setShowLoadingDemo] = useState(false);

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

      {/* KPI Overview */}
      <KPIOverview isLoading={showLoadingDemo} />

      {/* Loading States Demo Section */}
      <div className="mt-12 rounded-lg border border-slate-200 bg-slate-50 p-6">
        <div className="mb-4 flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-slate-900">
              Loading States Demo
            </h2>
            <p className="text-sm text-slate-600">
              Demonstration of skeleton screens and loading components
            </p>
          </div>
          <button
            onClick={() => setShowLoadingDemo(!showLoadingDemo)}
            className="rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-slate-800"
          >
            {showLoadingDemo ? "Show Data" : "Show Loading"}
          </button>
        </div>

        <div className="space-y-6">
          {/* LoadingCard Variants */}
          <div>
            <h3 className="mb-3 text-sm font-medium text-slate-700">
              LoadingCard Components
            </h3>
            <div className="grid gap-4 md:grid-cols-3">
              <div>
                <p className="mb-2 text-xs text-slate-600">Metric Variant</p>
                <LoadingCard variant="metric" />
              </div>
              <div>
                <p className="mb-2 text-xs text-slate-600">Status Variant</p>
                <LoadingCard variant="status" />
              </div>
              <div>
                <p className="mb-2 text-xs text-slate-600">Default Variant</p>
                <LoadingCard variant="default" />
              </div>
            </div>
          </div>

          {/* SkeletonLoader Components */}
          <div>
            <h3 className="mb-3 text-sm font-medium text-slate-700">
              Skeleton Loaders
            </h3>
            <div className="space-y-4 rounded-lg bg-white p-4">
              <div>
                <p className="mb-2 text-xs text-slate-600">Text Skeleton</p>
                <SkeletonText lines={3} />
              </div>
              <div className="flex items-center gap-4">
                <div>
                  <p className="mb-2 text-xs text-slate-600">Avatar - Small</p>
                  <SkeletonAvatar size="sm" />
                </div>
                <div>
                  <p className="mb-2 text-xs text-slate-600">Avatar - Medium</p>
                  <SkeletonAvatar size="md" />
                </div>
                <div>
                  <p className="mb-2 text-xs text-slate-600">Avatar - Large</p>
                  <SkeletonAvatar size="lg" />
                </div>
              </div>
              <div>
                <p className="mb-2 text-xs text-slate-600">
                  Rectangle Skeleton
                </p>
                <SkeletonLoader
                  variant="rectangle"
                  width="w-full"
                  height="h-32"
                />
              </div>
            </div>
          </div>

          {/* SkeletonCard Component */}
          <div>
            <h3 className="mb-3 text-sm font-medium text-slate-700">
              Skeleton Card
            </h3>
            <SkeletonCard />
          </div>
        </div>
      </div>
    </div>
  );
}
