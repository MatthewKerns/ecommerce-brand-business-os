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
 * Initial service configurations - used as baseline data
 */
const INITIAL_SERVICES: Omit<ServiceData, "lastCheck">[] = [
  {
    name: "TikTok API",
    status: "up",
    uptime: 99.9,
    icon: Video,
  },
  {
    name: "Blog Engine",
    status: "up",
    uptime: 99.8,
    icon: FileText,
  },
  {
    name: "Email Automation",
    status: "up",
    uptime: 98.5,
    icon: Mail,
  },
  {
    name: "Python Agents",
    status: "up",
    uptime: 99.95,
    icon: Bot,
  },
  {
    name: "Database",
    status: "up",
    uptime: 99.99,
    icon: Database,
  },
  {
    name: "Cache",
    status: "up",
    uptime: 99.7,
    icon: Server,
  },
];

/**
 * Simulates a health check API call
 * In production, this would fetch from /api/health endpoint
 *
 * @returns Promise resolving to updated service data
 */
async function fetchHealthData(): Promise<ServiceData[]> {
  // Simulate API latency (200-500ms)
  await new Promise((resolve) =>
    setTimeout(resolve, 200 + Math.random() * 300)
  );

  // Simulate health check with occasional status changes
  return INITIAL_SERVICES.map((service) => {
    // 5% chance of status change to demonstrate real-time updates
    const random = Math.random();
    let status: ServiceStatus = service.status;
    let lastError: string | undefined;

    // Occasionally simulate status changes
    if (random < 0.05) {
      status = "degraded";
      lastError = "High response time detected";
    } else if (random < 0.02) {
      status = "down";
      lastError = "Connection timeout";
    } else {
      status = "up";
      lastError = undefined;
    }

    // Simulate slight uptime fluctuations
    const uptimeDelta = (Math.random() - 0.5) * 0.1; // ±0.05%
    const uptime = Math.max(
      95,
      Math.min(100, service.uptime + uptimeDelta)
    );

    return {
      ...service,
      status,
      uptime: parseFloat(uptime.toFixed(2)),
      lastCheck: new Date(),
      lastError,
    };
  });
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
