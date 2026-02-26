import { Activity } from "lucide-react";

/**
 * System Health Monitoring Page
 *
 * Displays real-time status of all organic marketing services and components.
 *
 * Features (to be implemented):
 * - Service status cards (TikTok API, Blog engine, Email automation, etc.)
 * - Overall system health indicator
 * - Recent activity log
 * - Uptime metrics and performance indicators
 * - Real-time status updates via polling
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

      {/* Overall Status Card */}
      <div className="rounded-lg border border-slate-200 bg-white p-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-slate-900">
              Overall Status
            </h2>
            <p className="text-sm text-slate-600">
              All systems operational
            </p>
          </div>
          <div className="flex items-center gap-2">
            <div className="h-3 w-3 rounded-full bg-green-500"></div>
            <span className="text-sm font-medium text-green-700">Healthy</span>
          </div>
        </div>
      </div>

      {/* Service Status Grid */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {["TikTok API", "Blog Engine", "Email Automation", "Python Agents", "Database", "Cache"].map(
          (service) => (
            <div
              key={service}
              className="rounded-lg border border-slate-200 bg-white p-6"
            >
              <div className="mb-4 flex items-center justify-between">
                <h3 className="font-semibold text-slate-900">{service}</h3>
                <div className="h-2 w-2 rounded-full bg-green-500"></div>
              </div>
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-slate-600">Status</span>
                  <span className="font-medium text-green-700">Operational</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-slate-600">Uptime</span>
                  <span className="font-medium text-slate-900">99.9%</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-slate-600">Last Check</span>
                  <span className="font-medium text-slate-900">Just now</span>
                </div>
              </div>
            </div>
          )
        )}
      </div>

      {/* Activity Log Placeholder */}
      <div className="rounded-lg border border-slate-200 bg-white p-6">
        <h2 className="mb-4 text-lg font-semibold text-slate-900">
          Recent Activity
        </h2>
        <div className="space-y-3">
          {[1, 2, 3, 4].map((i) => (
            <div
              key={i}
              className="flex items-center gap-4 border-b border-slate-100 pb-3 last:border-0"
            >
              <div className="h-2 w-2 rounded-full bg-slate-400"></div>
              <div className="flex-1">
                <div className="mb-1 h-3 w-48 animate-pulse rounded bg-slate-200"></div>
                <div className="h-2 w-32 animate-pulse rounded bg-slate-200"></div>
              </div>
              <div className="h-3 w-16 animate-pulse rounded bg-slate-200"></div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
