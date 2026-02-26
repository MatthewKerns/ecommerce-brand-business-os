"use client";

import { ActivityLogItem, ActivityEventType } from "@/components/ActivityLogItem";
import { cn } from "@/lib/utils";

/**
 * ActivityLog component displays a list of recent system events
 *
 * Features:
 * - Displays chronological list of system events
 * - Shows timestamp, event type, and description for each event
 * - Loading state with skeleton animations
 * - Empty state when no activities
 * - Auto-scrollable for long lists
 *
 * @example
 * ```tsx
 * <ActivityLog
 *   activities={[
 *     { id: "1", eventType: "success", description: "Service started", timestamp: new Date() }
 *   ]}
 *   isLoading={false}
 * />
 * ```
 */

export interface Activity {
  /** Unique identifier for the activity */
  id: string;
  /** Type of the event */
  eventType: ActivityEventType;
  /** Description of what happened */
  description: string;
  /** When it happened */
  timestamp: Date | string;
  /** Optional service name */
  service?: string;
}

export interface ActivityLogProps {
  /** Array of activities to display */
  activities?: Activity[];
  /** Loading state - shows skeleton when true */
  isLoading?: boolean;
  /** Maximum number of items to show */
  maxItems?: number;
  /** Optional custom className for wrapper */
  className?: string;
}

export function ActivityLog({
  activities = [],
  isLoading = false,
  maxItems = 10,
  className,
}: ActivityLogProps) {
  // Limit activities to maxItems
  const displayedActivities = activities.slice(0, maxItems);

  // Loading state
  if (isLoading) {
    return (
      <div className={cn("space-y-3", className)}>
        {[1, 2, 3, 4].map((i) => (
          <div
            key={i}
            className="flex items-center gap-4 border-b border-slate-100 pb-3 last:border-0"
          >
            <div className="h-2 w-2 rounded-full bg-slate-200 animate-pulse"></div>
            <div className="flex-1">
              <div className="mb-1 h-3 w-48 animate-pulse rounded bg-slate-200"></div>
              <div className="h-2 w-32 animate-pulse rounded bg-slate-200"></div>
            </div>
            <div className="h-3 w-16 animate-pulse rounded bg-slate-200"></div>
          </div>
        ))}
      </div>
    );
  }

  // Empty state
  if (displayedActivities.length === 0) {
    return (
      <div className={cn("text-center py-8", className)}>
        <p className="text-sm text-slate-500">No recent activity</p>
      </div>
    );
  }

  return (
    <div className={cn("space-y-2", className)}>
      {displayedActivities.map((activity) => (
        <ActivityLogItem
          key={activity.id}
          eventType={activity.eventType}
          description={activity.description}
          timestamp={activity.timestamp}
          service={activity.service}
        />
      ))}
    </div>
  );
}
