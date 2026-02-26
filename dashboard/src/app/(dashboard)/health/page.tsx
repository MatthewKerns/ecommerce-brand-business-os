import { Activity } from "lucide-react";
import { SystemHealthDashboard } from "@/components/SystemHealthDashboard";

/**
 * System Health Monitoring Page
 *
 * Displays real-time status of all organic marketing services and components.
 *
 * Features:
 * - Service status cards with real-time status indicators
 * - Overall system health indicator
 * - Recent activity log
 * - Uptime metrics and performance indicators
 * - Different status states (up/down/degraded) demonstration
 *
 * @route /health
 */
export default function HealthPage() {
  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center gap-3">
        <div className="rounded-lg bg-green-100 p-3">
          <Activity className="h-6 w-6 text-green-700" />
        </div>
        <div>
          <h1 className="text-3xl font-bold text-slate-900">System Health</h1>
          <p className="text-sm text-slate-600">
            Monitor the status of all services and components
          </p>
        </div>
      </div>

      {/* System Health Dashboard */}
      <SystemHealthDashboard />
    </div>
  );
}
