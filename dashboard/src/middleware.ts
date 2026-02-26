import { authMiddleware } from "@clerk/nextjs";

// This middleware protects all routes except the ones specified in publicRoutes
// See https://clerk.com/docs/references/nextjs/auth-middleware for more information
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
});

export const config = {
  matcher: [
    // Skip Next.js internals and all static files, unless found in search params
    "/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)",
    // Always run for API routes
    "/(api|trpc)(.*)",
  ],
};
