"use client";

import { UserButton } from "@clerk/nextjs";

/**
 * UserMenu component displays user profile and account actions
 *
 * Features:
 * - Uses Clerk's <UserButton /> component for built-in functionality
 * - Displays user avatar with profile picture
 * - Dropdown menu with user info and sign-out option
 * - Manages account settings and preferences
 * - Consistent styling with dashboard theme
 *
 * The UserButton component from Clerk automatically handles:
 * - User profile display
 * - Account management options
 * - Sign out functionality
 * - Profile picture updates
 * - Security settings
 *
 * @example
 * ```tsx
 * <UserMenu />
 * ```
 */
export function UserMenu() {
  return (
    <div className="flex items-center gap-2">
      <UserButton
        afterSignOutUrl="/sign-in"
        appearance={{
          elements: {
            avatarBox: "h-9 w-9",
            userButtonPopoverCard: "shadow-lg border border-slate-200",
            userButtonPopoverActionButton:
              "hover:bg-slate-50 text-slate-700 rounded-md",
            userButtonPopoverActionButtonText: "text-sm",
            userButtonPopoverActionButtonIcon: "text-slate-500",
            userButtonPopoverFooter: "hidden",
          },
        }}
      />
    </div>
  );
}
