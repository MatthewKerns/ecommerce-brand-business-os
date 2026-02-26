"use client";

import { CheckCircle2, XCircle, AlertCircle, LucideIcon } from "lucide-react";
import { cn } from "@/lib/utils";

/**
 * ServiceStatusCard component displays the status of a service in the system health dashboard
 *
 * Features:
 * - Displays service name with optional icon
 * - Shows status badge (up/down/degraded) with color-coded indicator
 * - Displays uptime percentage
 * - Shows last check timestamp
 * - Optional last error message display
 * - Loading state with skeleton animation
 * - Responsive design with hover effects
 *
 * @example
 * ```tsx
 * <ServiceStatusCard
 *   name="TikTok API"
 *   status="up"
 *   uptime={99.9}
 *   lastCheck={new Date()}
 *   icon={Database}
 * />
 * ```
 */

export type ServiceStatus = "up" | "down" | "degraded";

export interface ServiceStatusCardProps {
  /** Name of the service */
  name: string;
  /** Current status of the service */
  status: ServiceStatus;
  /** Uptime percentage (0-100) */
  uptime?: number;
  /** Last check timestamp */
  lastCheck: Date | string;
  /** Optional last error message */
  lastError?: string;
  /** Optional icon component from lucide-react */
  icon?: LucideIcon;
  /** Loading state - shows skeleton when true */
  isLoading?: boolean;
  /** Optional custom className for card wrapper */
  className?: string;
}

export function ServiceStatusCard({
  name,
  status,
  uptime,
  lastCheck,
  lastError,
  icon: Icon,
  isLoading = false,
  className,
}: ServiceStatusCardProps) {
  // Loading state
  if (isLoading) {
    return (
      <div
        className={cn(
          "rounded-lg border border-slate-200 bg-white p-6",
          className
        )}
      >
        <div className="mb-4 flex items-center justify-between">
          <div className="h-5 w-32 animate-pulse rounded bg-slate-200"></div>
          <div className="h-3 w-3 animate-pulse rounded-full bg-slate-200"></div>
        </div>
        <div className="space-y-2">
          <div className="flex justify-between">
            <div className="h-4 w-16 animate-pulse rounded bg-slate-200"></div>
            <div className="h-4 w-20 animate-pulse rounded bg-slate-200"></div>
          </div>
          <div className="flex justify-between">
            <div className="h-4 w-16 animate-pulse rounded bg-slate-200"></div>
            <div className="h-4 w-16 animate-pulse rounded bg-slate-200"></div>
          </div>
          <div className="flex justify-between">
            <div className="h-4 w-20 animate-pulse rounded bg-slate-200"></div>
            <div className="h-4 w-24 animate-pulse rounded bg-slate-200"></div>
          </div>
        </div>
      </div>
    );
  }

  // Status configuration
  const statusConfig = {
    up: {
      label: "Operational",
      color: "text-green-700",
      bgColor: "bg-green-500",
      icon: CheckCircle2,
    },
    down: {
      label: "Down",
      color: "text-red-700",
      bgColor: "bg-red-500",
      icon: XCircle,
    },
    degraded: {
      label: "Degraded",
      color: "text-yellow-700",
      bgColor: "bg-yellow-500",
      icon: AlertCircle,
    },
  };

  const config = statusConfig[status];
  const StatusIcon = config.icon;

  // Format last check time
  const formatLastCheck = (time: Date | string): string => {
    const date = typeof time === "string" ? new Date(time) : time;
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);

    if (diffMins < 1) return "Just now";
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffMins < 1440) return `${Math.floor(diffMins / 60)}h ago`;
    return `${Math.floor(diffMins / 1440)}d ago`;
  };

  return (
    <div
      className={cn(
        "rounded-lg border border-slate-200 bg-white p-6 transition-shadow hover:shadow-md",
        className
      )}
    >
      {/* Header with service name and status indicator */}
      <div className="mb-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          {Icon && (
            <div className="rounded-md bg-slate-100 p-2">
              <Icon className="h-4 w-4 text-slate-600" />
            </div>
          )}
          <h3 className="font-semibold text-slate-900">{name}</h3>
        </div>
        <div className="flex items-center gap-2">
          <div className={cn("h-2 w-2 rounded-full", config.bgColor)}></div>
          <StatusIcon className={cn("h-4 w-4", config.color)} />
        </div>
      </div>

      {/* Status details */}
      <div className="space-y-2">
        {/* Status label */}
        <div className="flex justify-between text-sm">
          <span className="text-slate-600">Status</span>
          <span className={cn("font-medium", config.color)}>
            {config.label}
          </span>
        </div>

        {/* Uptime percentage */}
        {uptime !== undefined && (
          <div className="flex justify-between text-sm">
            <span className="text-slate-600">Uptime</span>
            <span className="font-medium text-slate-900">{uptime}%</span>
          </div>
        )}

        {/* Last check time */}
        <div className="flex justify-between text-sm">
          <span className="text-slate-600">Last Check</span>
          <span className="font-medium text-slate-900">
            {formatLastCheck(lastCheck)}
          </span>
        </div>

        {/* Last error (if present) */}
        {lastError && (
          <div className="mt-3 rounded-md bg-red-50 p-2">
            <p className="text-xs text-red-700">
              <span className="font-medium">Error:</span> {lastError}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
