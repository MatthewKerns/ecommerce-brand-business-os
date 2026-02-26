"use client";

import {
  Video,
  FileText,
  Mail,
  Bot,
  Database,
  Server,
  LucideIcon,
} from "lucide-react";
import { ServiceStatusCard, ServiceStatus } from "@/components/ServiceStatusCard";

/**
 * SystemHealthDashboard component displays comprehensive system health monitoring
 *
 * Features:
 * - Overall system health indicator with color-coded status
 * - Grid of service status cards showing individual service health
 * - Recent activity log with loading states
 * - Automatic health calculation based on service statuses
 * - Responsive grid layout (1 col mobile, 2 col tablet, 3 col desktop)
 * - Loading state support with skeleton animations
 *
 * @example
 * ```tsx
 * <SystemHealthDashboard isLoading={false} />
 * ```
 */

export interface ServiceData {
  /** Name of the service */
  name: string;
  /** Current status of the service */
  status: ServiceStatus;
  /** Uptime percentage (0-100) */
  uptime: number;
  /** Last check timestamp */
  lastCheck: Date;
  /** Optional last error message */
  lastError?: string;
  /** Icon component from lucide-react */
  icon: LucideIcon;
}

export interface SystemHealthDashboardProps {
  /** Loading state - shows skeleton when true */
  isLoading?: boolean;
  /** Optional custom services data - defaults to example data */
  services?: ServiceData[];
  /** Optional custom className for wrapper */
  className?: string;
}

// Default services data for demonstration
const DEFAULT_SERVICES: ServiceData[] = [
  {
    name: "TikTok API",
    status: "up",
    uptime: 99.9,
    lastCheck: new Date(Date.now() - 30000), // 30 seconds ago
    icon: Video,
  },
  {
    name: "Blog Engine",
    status: "up",
    uptime: 99.8,
    lastCheck: new Date(Date.now() - 120000), // 2 minutes ago
    icon: FileText,
  },
  {
    name: "Email Automation",
    status: "degraded",
    uptime: 98.5,
    lastCheck: new Date(Date.now() - 60000), // 1 minute ago
    lastError: "High response time detected",
    icon: Mail,
  },
  {
    name: "Python Agents",
    status: "up",
    uptime: 99.95,
    lastCheck: new Date(Date.now() - 45000), // 45 seconds ago
    icon: Bot,
  },
  {
    name: "Database",
    status: "up",
    uptime: 99.99,
    lastCheck: new Date(Date.now() - 15000), // 15 seconds ago
    icon: Database,
  },
  {
    name: "Cache",
    status: "up",
    uptime: 99.7,
    lastCheck: new Date(Date.now() - 90000), // 1.5 minutes ago
    icon: Server,
  },
];

export function SystemHealthDashboard({
  isLoading = false,
  services = DEFAULT_SERVICES,
  className = "",
}: SystemHealthDashboardProps) {
  // Calculate overall health
  const allOperational = services.every((s) => s.status === "up");
  const hasWarnings = services.some((s) => s.status === "degraded");

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
