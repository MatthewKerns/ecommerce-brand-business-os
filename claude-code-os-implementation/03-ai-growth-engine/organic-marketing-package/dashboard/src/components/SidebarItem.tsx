"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { LucideIcon } from "lucide-react";
import { cn } from "@/lib/utils";

/**
 * SidebarItem represents a single navigation link in the sidebar
 *
 * Features:
 * - Active state highlighting based on current route
 * - Icon support via lucide-react
 * - Hover and active states
 * - Accessible navigation with proper aria labels
 * - Optional badge for notifications/counts
 *
 * @example
 * ```tsx
 * <SidebarItem
 *   href="/dashboard"
 *   icon={LayoutDashboard}
 *   label="Dashboard"
 * />
 * ```
 */
export interface SidebarItemProps {
  /** Navigation href path */
  href: string;
  /** Lucide icon component */
  icon: LucideIcon;
  /** Display label for the navigation item */
  label: string;
  /** Optional badge text (e.g., notification count) */
  badge?: string | number;
  /** Whether the sidebar is collapsed (mobile) */
  isCollapsed?: boolean;
}

export function SidebarItem({
  href,
  icon: Icon,
  label,
  badge,
  isCollapsed = false,
}: SidebarItemProps) {
  const pathname = usePathname();
  const isActive = pathname === href || pathname?.startsWith(`${href}/`);

  return (
    <Link
      href={href}
      className={cn(
        "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
        isActive
          ? "bg-slate-100 text-slate-900"
          : "text-slate-600 hover:bg-slate-50 hover:text-slate-900",
        isCollapsed && "justify-center"
      )}
      aria-current={isActive ? "page" : undefined}
    >
      <Icon className={cn("h-5 w-5 flex-shrink-0", isActive && "text-blue-600")} />

      {!isCollapsed && (
        <>
          <span className="flex-1 truncate">{label}</span>
          {badge !== undefined && (
            <span
              className={cn(
                "flex h-5 min-w-[20px] items-center justify-center rounded-full px-1.5 text-xs font-semibold",
                isActive
                  ? "bg-blue-600 text-white"
                  : "bg-slate-200 text-slate-700"
              )}
            >
              {badge}
            </span>
          )}
        </>
      )}
    </Link>
  );
}
