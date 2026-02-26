"use client";

import { ClerkProvider } from "@clerk/nextjs";
import { ReactNode } from "react";

interface ProvidersProps {
  children: ReactNode;
}

/**
 * Providers component wraps the application with necessary context providers
 * Currently includes:
 * - ClerkProvider for authentication and organization/workspace management
 */
export function Providers({ children }: ProvidersProps) {
  return <ClerkProvider>{children}</ClerkProvider>;
}
