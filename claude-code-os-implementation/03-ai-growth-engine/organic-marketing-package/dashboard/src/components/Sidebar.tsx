"use client";

import { useState } from "react";
import {
  LayoutDashboard,
  Activity,
  Settings,
  BarChart3,
  Menu,
  X,
} from "lucide-react";
import { SidebarItem } from "./SidebarItem";
import { WorkspaceSelector } from "./WorkspaceSelector";
import { cn } from "@/lib/utils";

/**
 * Sidebar navigation component with responsive design
 *
 * Features:
 * - Responsive design: full sidebar on desktop, collapsible on mobile
 * - Navigation sections: Dashboard, System Health, Configuration, Analytics
 * - Workspace selector integration
 * - Mobile menu toggle
 * - Active route highlighting
 * - Smooth transitions
 *
 * Navigation Structure:
 * - Dashboard (/) - Main overview page
 * - System Health (/health) - Service monitoring
 * - Configuration (/config) - Settings and API keys
 * - Analytics (/analytics) - Performance metrics
 *
 * @example
 * ```tsx
 * <Sidebar />
 * ```
 */
export function Sidebar() {
  const [isMobileOpen, setIsMobileOpen] = useState(false);

  const navigationItems = [
    {
      href: "/",
      icon: LayoutDashboard,
      label: "Dashboard",
    },
    {
      href: "/health",
      icon: Activity,
      label: "System Health",
    },
    {
      href: "/config",
      icon: Settings,
      label: "Configuration",
    },
    {
      href: "/analytics",
      icon: BarChart3,
      label: "Analytics",
    },
  ];

  return (
    <>
      {/* Mobile menu toggle button */}
      <button
        onClick={() => setIsMobileOpen(!isMobileOpen)}
        className="fixed left-4 top-4 z-50 rounded-md bg-white p-2 shadow-md lg:hidden"
        aria-label={isMobileOpen ? "Close menu" : "Open menu"}
      >
        {isMobileOpen ? (
          <X className="h-6 w-6 text-slate-900" />
        ) : (
          <Menu className="h-6 w-6 text-slate-900" />
        )}
      </button>

      {/* Mobile backdrop */}
      {isMobileOpen && (
        <div
          className="fixed inset-0 z-30 bg-slate-900/50 lg:hidden"
          onClick={() => setIsMobileOpen(false)}
          aria-hidden="true"
        />
      )}

      {/* Sidebar */}
      <aside
        className={cn(
          "fixed inset-y-0 left-0 z-40 w-64 transform border-r border-slate-200 bg-white transition-transform duration-200 ease-in-out lg:translate-x-0",
          isMobileOpen ? "translate-x-0" : "-translate-x-full"
        )}
      >
        <div className="flex h-full flex-col">
          {/* Header */}
          <div className="border-b border-slate-200 p-4">
            <div className="mb-4">
              <h1 className="text-xl font-bold text-slate-900">
                Marketing OS
              </h1>
              <p className="text-sm text-slate-500">Organic Growth Dashboard</p>
            </div>

            {/* Workspace Selector */}
            <WorkspaceSelector />
          </div>

          {/* Navigation */}
          <nav className="flex-1 overflow-y-auto p-4">
            <div className="space-y-1">
              {navigationItems.map((item) => (
                <SidebarItem
                  key={item.href}
                  href={item.href}
                  icon={item.icon}
                  label={item.label}
                />
              ))}
            </div>
          </nav>

          {/* Footer */}
          <div className="border-t border-slate-200 p-4">
            <p className="text-xs text-slate-500">
              &copy; {new Date().getFullYear()} Marketing OS
            </p>
          </div>
        </div>
      </aside>

      {/* Spacer for desktop layout */}
      <div className="hidden lg:block lg:w-64" aria-hidden="true" />
    </>
  );
}
