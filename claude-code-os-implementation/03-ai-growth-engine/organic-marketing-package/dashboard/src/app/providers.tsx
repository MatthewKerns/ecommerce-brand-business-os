"use client";

import { ClerkProvider } from "@clerk/nextjs";
import { ReactNode, useState, useEffect } from "react";
import { WorkspaceProvider } from "@/contexts/WorkspaceContext";
import { ClerkSetupGuard } from "@/components/auth/ClerkSetupGuard";
import { ToastProvider } from "@/components/toast/ToastProvider";

interface ProvidersProps {
  children: ReactNode;
}

/**
 * SafeClerkProvider wraps ClerkProvider and handles configuration errors gracefully
 */
function SafeClerkProvider({ children }: { children: ReactNode }) {
  // Check configuration at render time (env vars are replaced at build time)
  const skipAuth = process.env.NEXT_PUBLIC_SKIP_AUTH === 'true';
  const publishableKey = process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY || '';
  const hasValidKey = publishableKey &&
                      !publishableKey.includes('PLACEHOLDER') &&
                      publishableKey.startsWith('pk_');

  const shouldLoadClerk = !skipAuth && hasValidKey;

  // If we should load Clerk and have valid config, use ClerkProvider
  if (shouldLoadClerk) {
    return (
      <ClerkProvider
        appearance={{
          elements: {
            rootBox: "clerk-root",
            card: "clerk-card",
          },
        }}
      >
        {children}
      </ClerkProvider>
    );
  }

  // Otherwise, render children without Clerk
  return <>{children}</>;
}

/**
 * Providers component wraps the application with necessary context providers
 * Now includes:
 * - ClerkSetupGuard for graceful configuration error handling
 * - SafeClerkProvider for conditional Clerk loading
 * - WorkspaceProvider for workspace context and switching functionality
 */
export function Providers({ children }: ProvidersProps) {
  return (
    <ClerkSetupGuard>
      <SafeClerkProvider>
        <WorkspaceProvider>
          {children}
          <ToastProvider />
        </WorkspaceProvider>
      </SafeClerkProvider>
    </ClerkSetupGuard>
  );
}