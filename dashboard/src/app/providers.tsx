"use client";

import { ClerkProvider } from "@clerk/nextjs";
import { ReactNode } from "react";
import { WorkspaceProvider } from "@/contexts/WorkspaceContext";

interface ProvidersProps {
  children: ReactNode;
}

/**
 * Providers component wraps the application with necessary context providers
 * Currently includes:
 * - ClerkProvider for authentication and organization/workspace management
 * - WorkspaceProvider for workspace context and switching functionality
 */
export function Providers({ children }: ProvidersProps) {
  return (
    <ClerkProvider>
      <WorkspaceProvider>{children}</WorkspaceProvider>
    </ClerkProvider>
  );
}
