"use client";

import { useState, useEffect } from "react";
import {
  Video,
  FileText,
  Mail,
  Bot,
  Database,
  Server,
  LucideIcon,
} from "lucide-react";
import { ServiceStatus } from "@/components/ServiceStatusCard";
import { apiClient } from "@/lib/api-client";
import type { SystemHealth, HealthStatus } from "@/lib/health-checker";

/**
 * Service data structure for health monitoring
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

/**
 * Return type for useHealthMonitor hook
 */
export interface UseHealthMonitorReturn {
  /** Array of service health data */
  services: ServiceData[];
  /** Loading state - true during initial load and polls */
  isLoading: boolean;
  /** Error state if health check fails */
  error: Error | null;
  /** Manually trigger a health check */
  refetch: () => Promise<void>;
}

/**
 * Icon mapping for service names
 */
const SERVICE_ICONS: Record<string, LucideIcon> = {
  "TikTok API": Video,
  "Blog Engine": FileText,
  "Email Automation": Mail,
  "Python Agents": Bot,
  Database: Database,
  Cache: Server,
  Environment: Server,
};

/**
 * Map health status from API to ServiceStatus
 */
function mapHealthStatus(status: HealthStatus): ServiceStatus {
  switch (status) {
    case "healthy":
      return "up";
    case "degraded":
      return "degraded";
    case "unhealthy":
      return "down";
    default:
      return "down";
  }
}

/**
 * Fetch health data from /api/health endpoint
 *
 * @returns Promise resolving to service health data
 */
async function fetchHealthData(): Promise<ServiceData[]> {
  const health = await apiClient.get<SystemHealth>("/api/health");

  return health.services.map((service) => ({
    name: service.name,
    status: mapHealthStatus(service.status),
    uptime: service.uptime || 0,
    lastCheck: new Date(service.lastCheck),
    lastError: service.status === "unhealthy" ? service.message : undefined,
    icon: SERVICE_ICONS[service.name] || Server,
  }));
}

/**
 * Custom hook for monitoring system health with real-time polling
 *
 * Features:
 * - Automatically polls health status every 30 seconds
 * - Updates service status, uptime, and last check timestamps
 * - Provides loading and error states
 * - Cleans up polling interval on unmount
 * - Manual refetch capability
 *
 * @param options - Configuration options
 * @param options.pollingInterval - Polling interval in milliseconds (default: 30000)
 * @param options.enabled - Whether polling is enabled (default: true)
 *
 * @returns Object containing services data, loading state, error, and refetch function
 *
 * @example
 * ```tsx
 * function HealthDashboard() {
 *   const { services, isLoading, error, refetch } = useHealthMonitor();
 *
 *   if (error) return <div>Error: {error.message}</div>;
 *
 *   return (
 *     <div>
 *       {services.map(service => (
 *         <ServiceCard key={service.name} {...service} />
 *       ))}
 *       <button onClick={refetch}>Refresh</button>
 *     </div>
 *   );
 * }
 * ```
 */
export function useHealthMonitor(options: {
  pollingInterval?: number;
  enabled?: boolean;
} = {}): UseHealthMonitorReturn {
  const { pollingInterval = 30000, enabled = true } = options;

  const [services, setServices] = useState<ServiceData[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  /**
   * Fetches health data and updates state
   */
  const refetch = async () => {
    try {
      setError(null);
      const data = await fetchHealthData();
      setServices(data);
    } catch (err) {
      setError(
        err instanceof Error ? err : new Error("Failed to fetch health data")
      );
    } finally {
      setIsLoading(false);
    }
  };

  // Initial fetch and polling setup
  useEffect(() => {
    if (!enabled) {
      setIsLoading(false);
      return;
    }

    // Initial fetch
    refetch();

    // Set up polling interval
    const intervalId = setInterval(() => {
      refetch();
    }, pollingInterval);

    // Cleanup on unmount
    return () => {
      clearInterval(intervalId);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pollingInterval, enabled]);

  return {
    services,
    isLoading,
    error,
    refetch,
  };
}
