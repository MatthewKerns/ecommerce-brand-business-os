"use client";

import { ReactNode } from "react";
import { Sidebar } from "./Sidebar";
import { Header } from "./Header";

interface DashboardLayoutProps {
  /**
   * Main content to be displayed in the dashboard
   */
  children: ReactNode;
}

/**
 * DashboardLayout wraps the entire dashboard with sidebar and header navigation
 *
 * Features:
 * - Two-column layout: fixed sidebar (left) + scrollable main content (right)
 * - Responsive design: collapsible sidebar on mobile, fixed on desktop
 * - Header displays user menu and workspace switcher
 * - Sidebar contains navigation items, workspace selector, and mobile toggle
 * - Main content area with proper spacing and overflow handling
 * - Consistent slate color scheme throughout
 *
 * Layout Structure:
 * ```
 * ┌──────────────┬────────────────────┐
 * │              │      Header        │
 * │   Sidebar    ├────────────────────┤
 * │  (fixed)     │   Main Content     │
 * │              │   (scrollable)     │
 * └──────────────┴────────────────────┘
 * ```
 *
 * Responsive Behavior:
 * - Desktop (lg+): Sidebar always visible, takes 256px width (w-64)
 * - Mobile/Tablet: Sidebar hidden by default, slides in from left when toggled
 * - Sidebar manages its own mobile menu state and toggle button
 * - Main content area adjusts with lg:pl-64 padding on desktop
 *
 * @example
 * ```tsx
 * <DashboardLayout>
 *   <YourPageContent />
 * </DashboardLayout>
 * ```
 */
export function DashboardLayout({ children }: DashboardLayoutProps) {
  return (
    <div className="min-h-screen bg-slate-50">
      {/* Sidebar - handles its own mobile state and positioning */}
      <Sidebar />

      {/* Main content area - offset by sidebar width on desktop */}
      <div className="lg:pl-64">
        {/* Header - sticky at top of main content area */}
        <Header showMenuButton={false} />

        {/* Main content - scrollable area */}
        <main className="min-h-[calc(100vh-4rem)] p-4 lg:p-6">
          {children}
        </main>
      </div>
    </div>
  );
}
