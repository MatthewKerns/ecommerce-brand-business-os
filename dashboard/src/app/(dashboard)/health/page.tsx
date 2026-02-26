import {
  Activity,
  Video,
  FileText,
  Mail,
  Bot,
  Database,
  Server,
} from "lucide-react";
import { ServiceStatusCard } from "@/components/ServiceStatusCard";

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
  // Mock data for demonstration - in production, this would come from API
  const services = [
    {
      name: "TikTok API",
      status: "up" as const,
      uptime: 99.9,
      lastCheck: new Date(Date.now() - 30000), // 30 seconds ago
      icon: Video,
    },
    {
      name: "Blog Engine",
      status: "up" as const,
      uptime: 99.8,
      lastCheck: new Date(Date.now() - 120000), // 2 minutes ago
      icon: FileText,
    },
    {
      name: "Email Automation",
      status: "degraded" as const,
      uptime: 98.5,
      lastCheck: new Date(Date.now() - 60000), // 1 minute ago
      lastError: "High response time detected",
      icon: Mail,
    },
    {
      name: "Python Agents",
      status: "up" as const,
      uptime: 99.95,
      lastCheck: new Date(Date.now() - 45000), // 45 seconds ago
      icon: Bot,
    },
    {
      name: "Database",
      status: "up" as const,
      uptime: 99.99,
      lastCheck: new Date(Date.now() - 15000), // 15 seconds ago
      icon: Database,
    },
    {
      name: "Cache",
      status: "up" as const,
      uptime: 99.7,
      lastCheck: new Date(Date.now() - 90000), // 1.5 minutes ago
      icon: Server,
    },
  ];

  // Calculate overall health
  const allOperational = services.every((s) => s.status === "up");
  const hasWarnings = services.some((s) => s.status === "degraded");

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
              {allOperational
                ? "All systems operational"
                : hasWarnings
                  ? "Some services degraded"
                  : "System issues detected"}
            </p>
          </div>
          <div className="flex items-center gap-2">
            <div
              className={`h-3 w-3 rounded-full ${
                allOperational
                  ? "bg-green-500"
                  : hasWarnings
                    ? "bg-yellow-500"
                    : "bg-red-500"
              }`}
            ></div>
            <span
              className={`text-sm font-medium ${
                allOperational
                  ? "text-green-700"
                  : hasWarnings
                    ? "text-yellow-700"
                    : "text-red-700"
              }`}
            >
              {allOperational ? "Healthy" : hasWarnings ? "Warning" : "Critical"}
            </span>
          </div>
        </div>
      </div>

      {/* Service Status Grid */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {services.map((service) => (
          <ServiceStatusCard
            key={service.name}
            name={service.name}
            status={service.status}
            uptime={service.uptime}
            lastCheck={service.lastCheck}
            lastError={service.lastError}
            icon={service.icon}
          />
        ))}
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
