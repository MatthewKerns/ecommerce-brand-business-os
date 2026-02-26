import { LayoutDashboard } from "lucide-react";

/**
 * Main Dashboard Page
 *
 * Central hub displaying overview of all organic marketing components.
 *
 * Features (to be implemented):
 * - KPI overview cards showing key metrics
 * - Recent activity feed
 * - Quick access to system health
 * - Performance charts and visualizations
 *
 * @route /
 */
export default function DashboardPage() {
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

      {/* Placeholder Content */}
      <div className="rounded-lg border border-slate-200 bg-white p-8">
        <div className="text-center">
          <h2 className="mb-2 text-xl font-semibold text-slate-900">
            Welcome to Marketing OS
          </h2>
          <p className="text-slate-600">
            Your central management interface for organic marketing components.
            KPI cards and metrics will be displayed here.
          </p>
        </div>
      </div>

      {/* Placeholder Grid */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {[1, 2, 3, 4, 5, 6].map((i) => (
          <div
            key={i}
            className="rounded-lg border border-slate-200 bg-white p-6"
          >
            <div className="mb-2 h-4 w-24 animate-pulse rounded bg-slate-200"></div>
            <div className="mb-4 h-8 w-32 animate-pulse rounded bg-slate-200"></div>
            <div className="h-3 w-20 animate-pulse rounded bg-slate-200"></div>
          </div>
        ))}
      </div>
    </div>
  );
}
