import { LayoutDashboard } from "lucide-react";
import { KPIOverview } from "@/components/KPIOverview";

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
      <KPIOverview />

      {/* Loading State Demo */}
      <KPIOverview isLoading={true} />
    </div>
  );
}
