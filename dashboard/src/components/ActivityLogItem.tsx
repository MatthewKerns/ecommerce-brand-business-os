"use client";

import { LucideIcon, CheckCircle2, XCircle, AlertCircle, Info } from "lucide-react";
import { cn } from "@/lib/utils";

/**
 * ActivityLogItem component displays a single activity log entry
 *
 * Features:
 * - Displays event type with color-coded icon
 * - Shows event description
 * - Displays timestamp with relative time formatting
 * - Color-coded based on event type (success/error/warning/info)
 * - Hover effects for better UX
 *
 * @example
 * ```tsx
 * <ActivityLogItem
 *   eventType="success"
 *   description="TikTok API connection established"
 *   timestamp={new Date()}
 * />
 * ```
 */

export type ActivityEventType = "success" | "error" | "warning" | "info";

export interface ActivityLogItemProps {
  /** Type of the event (determines icon and color) */
  eventType: ActivityEventType;
  /** Description of the event */
  description: string;
  /** When the event occurred */
  timestamp: Date | string;
  /** Optional service name */
  service?: string;
  /** Optional custom className for wrapper */
  className?: string;
}

export function ActivityLogItem({
  eventType,
  description,
  timestamp,
  service,
  className,
}: ActivityLogItemProps) {
  // Event type configuration
  const eventConfig = {
    success: {
      icon: CheckCircle2,
      iconColor: "text-green-600",
      bgColor: "bg-green-500",
    },
    error: {
      icon: XCircle,
      iconColor: "text-red-600",
      bgColor: "bg-red-500",
    },
    warning: {
      icon: AlertCircle,
      iconColor: "text-yellow-600",
      bgColor: "bg-yellow-500",
    },
    info: {
      icon: Info,
      iconColor: "text-blue-600",
      bgColor: "bg-blue-500",
    },
  };

  const config = eventConfig[eventType];
  const EventIcon = config.icon;

  // Format timestamp to relative time
  const formatTimestamp = (time: Date | string): string => {
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
        "flex items-start gap-4 border-b border-slate-100 pb-3 last:border-0 transition-colors hover:bg-slate-50 px-2 py-2 rounded",
        className
      )}
    >
      {/* Status indicator dot and icon */}
      <div className="flex items-center gap-2 pt-1">
        <div className={cn("h-2 w-2 rounded-full", config.bgColor)}></div>
        <EventIcon className={cn("h-4 w-4", config.iconColor)} />
      </div>

      {/* Event details */}
      <div className="flex-1 min-w-0">
        <p className="text-sm text-slate-900 font-medium">{description}</p>
        {service && (
          <p className="text-xs text-slate-500 mt-0.5">{service}</p>
        )}
      </div>

      {/* Timestamp */}
      <div className="flex-shrink-0 pt-0.5">
        <span className="text-xs text-slate-500 font-medium">
          {formatTimestamp(timestamp)}
        </span>
      </div>
    </div>
  );
}
