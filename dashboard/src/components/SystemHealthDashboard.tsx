"use client";

import { ServiceStatusCard } from "@/components/ServiceStatusCard";
import {
  useHealthMonitor,
  ServiceData,
} from "@/hooks/useHealthMonitor";
import { RefreshCw } from "lucide-react";

/**
 * SystemHealthDashboard component displays comprehensive system health monitoring
 *
 * Features:
 * - Real-time health monitoring with automatic 30-second polling
 * - Overall system health indicator with color-coded status
 * - Grid of service status cards showing individual service health
 * - Recent activity log with loading states
 * - Automatic health calculation based on service statuses
 * - Responsive grid layout (1 col mobile, 2 col tablet, 3 col desktop)
 * - Loading state support with skeleton animations
 * - Manual refresh capability
 *
 * @example
 * ```tsx
 * <SystemHealthDashboard />
 * ```
 */

// Re-export ServiceData for backwards compatibility
export type { ServiceData };

export interface SystemHealthDashboardProps {
  /** Optional custom className for wrapper */
  className?: string;
  /** Optional polling interval override in milliseconds (default: 30000) */
  pollingInterval?: number;
}

export function SystemHealthDashboard({
  className = "",
  pollingInterval = 30000,
}: SystemHealthDashboardProps) {
  // Use health monitor hook for real-time updates
  const { services, isLoading, error, refetch } = useHealthMonitor({
    pollingInterval,
  });
  // Calculate overall health
  const allOperational = services.every((s) => s.status === "up");
  const hasWarnings = services.some((s) => s.status === "degraded");

  // Show error state if health check fails
  if (error) {
    return (
      <div className={className}>
        <div className="rounded-lg border border-red-200 bg-red-50 p-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-lg font-semibold text-red-900">
                Health Check Failed
              </h2>
              <p className="text-sm text-red-600">{error.message}</p>
            </div>
            <button
              onClick={() => refetch()}
              className="rounded-md bg-red-100 px-3 py-2 text-sm font-medium text-red-700 hover:bg-red-200 transition-colors"
            >
              Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={className}>
      {/* Overall Status Card */}
      <div className="mb-6 rounded-lg border border-slate-200 bg-white p-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-slate-900">
              Overall Status
            </h2>
            <p className="text-sm text-slate-600">
              {isLoading
                ? "Checking system status..."
                : allOperational
                  ? "All systems operational"
                  : hasWarnings
                    ? "Some services degraded"
                    : "System issues detected"}
            </p>
          </div>
          <div className="flex items-center gap-3">
            {/* Manual refresh button */}
            <button
              onClick={() => refetch()}
              disabled={isLoading}
              className="rounded-md p-2 text-slate-600 hover:bg-slate-100 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              title="Refresh health status"
            >
              <RefreshCw
                className={`h-4 w-4 ${isLoading ? "animate-spin" : ""}`}
              />
            </button>
            {/* Status indicator */}
            <div className="flex items-center gap-2">
              <div
                className={`h-3 w-3 rounded-full ${
                  isLoading
                    ? "animate-pulse bg-slate-300"
                    : allOperational
                      ? "bg-green-500"
                      : hasWarnings
                        ? "bg-yellow-500"
                        : "bg-red-500"
                }`}
              ></div>
              <span
                className={`text-sm font-medium ${
                  isLoading
                    ? "text-slate-600"
                    : allOperational
                      ? "text-green-700"
                      : hasWarnings
                        ? "text-yellow-700"
                        : "text-red-700"
                }`}
              >
                {isLoading
                  ? "Loading..."
                  : allOperational
                    ? "Healthy"
                    : hasWarnings
                      ? "Warning"
                      : "Critical"}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Service Status Grid */}
      <div className="mb-6">
        <h2 className="mb-4 text-lg font-semibold text-slate-900">
          Service Status
        </h2>
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
              isLoading={isLoading}
            />
          ))}
        </div>
      </div>

      {/* Activity Log */}
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
