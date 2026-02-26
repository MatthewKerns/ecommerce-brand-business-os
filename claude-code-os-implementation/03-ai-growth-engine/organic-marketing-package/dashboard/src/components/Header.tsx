"use client";

import { Menu } from "lucide-react";
import { WorkspaceSelector } from "./WorkspaceSelector";
import { UserMenu } from "./UserMenu";
import { cn } from "@/lib/utils";

interface HeaderProps {
  /**
   * Optional callback to toggle the mobile sidebar
   */
  onMenuClick?: () => void;
  /**
   * Whether to show the mobile menu button
   * @default true
   */
  showMenuButton?: boolean;
  /**
   * Additional CSS classes for the header
   */
  className?: string;
}

/**
 * Header component displays the top navigation bar with user controls
 *
 * Features:
 * - Mobile menu toggle button for responsive sidebar
 * - Workspace switcher for multi-tenant workspace management
 * - User menu with profile and sign-out options
 * - Responsive design with proper spacing and layout
 * - Fixed positioning with backdrop blur effect
 * - Integrates with Clerk authentication
 *
 * Layout:
 * - Left: Mobile menu button (on mobile/tablet)
 * - Center: Workspace selector (on mobile), empty (on desktop)
 * - Right: Workspace selector (on desktop) + User menu
 *
 * The header is designed to work alongside the Sidebar component,
 * providing consistent navigation across all viewport sizes.
 *
 * @example
 * ```tsx
 * <Header onMenuClick={() => setIsMobileOpen(true)} />
 * ```
 */
export function Header({
  onMenuClick,
  showMenuButton = true,
  className,
}: HeaderProps) {
  return (
    <header
      className={cn(
        "sticky top-0 z-30 border-b border-slate-200 bg-white/95 backdrop-blur supports-[backdrop-filter]:bg-white/60",
        className
      )}
    >
      <div className="flex h-16 items-center justify-between gap-4 px-4 lg:px-6">
        {/* Left section - Mobile menu button */}
        <div className="flex items-center gap-4">
          {showMenuButton && (
            <button
              onClick={onMenuClick}
              className="rounded-md p-2 text-slate-600 transition-colors hover:bg-slate-100 hover:text-slate-900 lg:hidden"
              aria-label="Open menu"
            >
              <Menu className="h-6 w-6" />
            </button>
          )}

          {/* Workspace selector - visible on mobile only */}
          <div className="lg:hidden">
            <WorkspaceSelector />
          </div>
        </div>

        {/* Center section - Empty on desktop, can be used for breadcrumbs or page title */}
        <div className="hidden flex-1 lg:block">{/* Future: Breadcrumbs */}</div>

        {/* Right section - Workspace selector (desktop) + User menu */}
        <div className="flex items-center gap-4">
          {/* Workspace selector - visible on desktop only */}
          <div className="hidden lg:block">
            <WorkspaceSelector />
          </div>

          {/* User menu */}
          <UserMenu />
        </div>
      </div>
    </header>
  );
}
