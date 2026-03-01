"use client";

import { Toaster } from "react-hot-toast";

/**
 * ToastProvider wraps react-hot-toast's Toaster with dashboard-consistent styling.
 * Add this once at the app root (inside providers.tsx).
 */
export function ToastProvider() {
  return (
    <Toaster
      position="top-right"
      gutter={8}
      toastOptions={{
        duration: 4000,
        style: {
          background: "#fff",
          color: "#0f172a",
          fontSize: "14px",
          borderRadius: "8px",
          border: "1px solid #e2e8f0",
          padding: "12px 16px",
          boxShadow:
            "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1)",
          maxWidth: "420px",
        },
        success: {
          iconTheme: {
            primary: "#16a34a",
            secondary: "#fff",
          },
        },
        error: {
          duration: 6000,
          iconTheme: {
            primary: "#dc2626",
            secondary: "#fff",
          },
        },
      }}
    />
  );
}
