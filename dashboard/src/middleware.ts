import { authMiddleware } from "@clerk/nextjs";
import { NextResponse } from "next/server";

/**
 * Protected route middleware with workspace (organization) verification
 *
 * This middleware:
 * 1. Protects all routes except authentication pages and public assets
 * 2. Verifies authenticated users have an active workspace (Clerk organization)
 * 3. Redirects to workspace selection if user is authenticated but has no workspace
 * 4. Redirects to sign-in if user is unauthenticated
 *
 * Multi-tenancy: Uses Clerk Organizations as workspaces
 * See https://clerk.com/docs/references/nextjs/auth-middleware
 */
export default authMiddleware({
  // Routes that don't require authentication
  publicRoutes: [
    "/sign-in(.*)",
    "/sign-up(.*)",
    "/api/webhook(.*)",
  ],
  // Routes that are always accessible even when signed out
  ignoredRoutes: [
    "/api/health",
    "/_next(.*)",
    "/favicon.ico",
    "/public(.*)",
  ],

  /**
   * afterAuth callback runs after authentication is verified
   * Used to enforce workspace requirement for all protected routes
   */
  afterAuth(auth, req) {
    // If user is not authenticated, redirect to sign-in
    if (!auth.userId && !auth.isPublicRoute) {
      const signInUrl = new URL("/sign-in", req.url);
      signInUrl.searchParams.set("redirect_url", req.url);
      return NextResponse.redirect(signInUrl);
    }

    // If user is authenticated but has no organization (workspace),
    // redirect to workspace selection (handled by Clerk's organization switcher)
    // Skip this check for API routes and public routes
    if (
      auth.userId &&
      !auth.orgId &&
      !auth.isPublicRoute &&
      !req.nextUrl.pathname.startsWith("/api")
    ) {
      // Create organization URL - Clerk will show org creation/selection UI
      const orgSelectionUrl = new URL("/sign-in", req.url);
      orgSelectionUrl.searchParams.set("redirect_url", req.url);
      return NextResponse.redirect(orgSelectionUrl);
    }

    // Allow the request to proceed
    return NextResponse.next();
  },
});

export const config = {
  matcher: [
    // Skip Next.js internals and all static files, unless found in search params
    "/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)",
    // Always run for API routes
    "/(api|trpc)(.*)",
  ],
};
