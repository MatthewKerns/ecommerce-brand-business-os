"use client";

import { useState } from "react";
import { AlertTriangle } from "lucide-react";
import { cn } from "@/lib/utils";

/**
 * ErrorTest component - FOR TESTING ERROR BOUNDARIES ONLY
 *
 * This component is used to manually test error boundary functionality.
 * It provides a button that throws an error when clicked.
 *
 * To test:
 * 1. Wrap this component with <ErrorBoundary>
 * 2. Click the "Trigger Error" button
 * 3. Verify error boundary catches the error
 * 4. Verify error UI displays with retry option
 * 5. Click retry and verify component resets
 *
 * @example
 * ```tsx
 * import { ErrorBoundary } from "@/components/ErrorBoundary";
 * import { ErrorTest } from "@/components/ErrorTest";
 *
 * <ErrorBoundary>
 *   <ErrorTest />
 * </ErrorBoundary>
 * ```
 */

export function ErrorTest() {
  const [shouldThrow, setShouldThrow] = useState(false);

  if (shouldThrow) {
    throw new Error("Test error triggered by ErrorTest component");
  }

  return (
    <div className="rounded-lg border border-orange-200 bg-orange-50 p-6">
      <div className="mb-4 flex items-center gap-2">
        <AlertTriangle className="h-5 w-5 text-orange-600" />
        <h3 className="font-semibold text-orange-900">
          Error Boundary Test Component
        </h3>
      </div>

      <p className="mb-4 text-sm text-orange-800">
        This component is for testing error boundaries. Click the button below
        to trigger an error and verify the error boundary catches it.
      </p>

      <button
        onClick={() => setShouldThrow(true)}
        className={cn(
          "inline-flex items-center justify-center gap-2 rounded-md px-4 py-2",
          "bg-orange-600 text-sm font-medium text-white",
          "transition-colors hover:bg-orange-700",
          "focus:outline-none focus:ring-2 focus:ring-orange-500 focus:ring-offset-2"
        )}
      >
        <AlertTriangle className="h-4 w-4" />
        Trigger Error
      </button>

      <p className="mt-3 text-xs text-orange-700">
        Remove this component from production code after testing.
      </p>
    </div>
  );
}
