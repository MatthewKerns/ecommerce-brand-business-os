import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

/**
 * Middleware that handles both Clerk authentication and skip-auth development mode
 *
 * In development with NEXT_PUBLIC_SKIP_AUTH=true:
 * - Allows all requests through without authentication
 *
 * In production or with Clerk configured:
 * - Protects routes and enforces workspace requirements
 */
export function middleware(request: NextRequest) {
  // Check if we're in skip-auth mode
  const skipAuth = process.env.NEXT_PUBLIC_SKIP_AUTH === 'true';

  if (skipAuth) {
    // In development mode with skip auth, allow all requests
    return NextResponse.next();
  }

  // Check if Clerk is properly configured
  const hasClerkKey = process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY &&
                     !process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY.includes('PLACEHOLDER');

  if (!hasClerkKey) {
    // No valid Clerk configuration, allow access to show setup screen
    return NextResponse.next();
  }

  // Try to use Clerk middleware if available
  try {
    const { authMiddleware } = require("@clerk/nextjs");

    // Use Clerk's authMiddleware with the original configuration
    const clerkMiddleware = authMiddleware({
      publicRoutes: [
        "/sign-in(.*)",
        "/sign-up(.*)",
        "/api/webhook(.*)",
      ],
      ignoredRoutes: [
        "/api/health",
        "/_next(.*)",
        "/favicon.ico",
        "/public(.*)",
      ],
      afterAuth(auth: any, req: NextRequest) {
        // If user is not authenticated, redirect to sign-in
        if (!auth.userId && !auth.isPublicRoute) {
          const signInUrl = new URL("/sign-in", req.url);
          signInUrl.searchParams.set("redirect_url", req.url);
          return NextResponse.redirect(signInUrl);
        }

        // If user is authenticated but has no organization (workspace),
        // redirect to workspace selection
        if (
          auth.userId &&
          !auth.orgId &&
          !auth.isPublicRoute &&
          !req.nextUrl.pathname.startsWith("/api")
        ) {
          const orgSelectionUrl = new URL("/sign-in", req.url);
          orgSelectionUrl.searchParams.set("redirect_url", req.url);
          return NextResponse.redirect(orgSelectionUrl);
        }

        return NextResponse.next();
      },
    });

    // Execute Clerk middleware
    return clerkMiddleware(request);
  } catch (error) {
    // Clerk not available or error, allow request to proceed
    console.warn("Clerk middleware not available, proceeding without authentication");
    return NextResponse.next();
  }
}

export const config = {
  matcher: [
    // Skip Next.js internals and all static files
    "/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)",
    // Always run for API routes
    "/(api|trpc)(.*)",
  ],
};