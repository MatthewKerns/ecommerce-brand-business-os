"use client";

/**
 * Mock UserButton for development without Clerk
 */
function MockUserButton({ afterSignOutUrl }: { afterSignOutUrl?: string }) {
  return (
    <div className="flex items-center gap-2">
      <button
        className="h-9 w-9 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 text-white flex items-center justify-center font-semibold"
        title="Dev User"
      >
        DU
      </button>
    </div>
  );
}

/**
 * UserMenu component displays user profile and account actions
 *
 * Features:
 * - Uses Clerk's <UserButton /> component when available
 * - Falls back to mock component in development mode
 * - Displays user avatar with profile picture
 * - Dropdown menu with user info and sign-out option
 * - Manages account settings and preferences
 *
 * @example
 * ```tsx
 * <UserMenu />
 * ```
 */
export function UserMenu() {
  // Check if we're in skip-auth mode
  const skipAuth = process.env.NEXT_PUBLIC_SKIP_AUTH === 'true';
  const hasClerkKey = process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY &&
                      !process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY.includes('PLACEHOLDER');

  // Use mock button in development or when Clerk isn't configured
  if (skipAuth || !hasClerkKey) {
    return <MockUserButton afterSignOutUrl="/sign-in" />;
  }

  // Try to use Clerk UserButton
  try {
    const { UserButton } = require("@clerk/nextjs");

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
  } catch (error) {
    // Fallback to mock if Clerk isn't available
    return <MockUserButton afterSignOutUrl="/sign-in" />;
  }
}