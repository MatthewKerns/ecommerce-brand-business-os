"use client";

import { createElement } from "react";
import toast from "react-hot-toast";
import { RetryableToast } from "@/components/toast/RetryableToast";

/**
 * Custom hook providing toast notification presets for common scenarios.
 *
 * @example
 * const { showSuccess, showError, showRetryable } = useToast();
 *
 * showSuccess("Settings saved");
 * showError("Failed to load data");
 * showRetryable("Upload failed", () => uploadFile());
 */
export function useToast() {
  const showSuccess = (message: string) => {
    toast.success(message);
  };

  const showError = (message: string) => {
    toast.error(message);
  };

  const showWarning = (message: string) => {
    toast(message, {
      icon: "\u26A0\uFE0F",
      duration: 5000,
      style: {
        borderLeft: "4px solid #eab308",
      },
    });
  };

  const showInfo = (message: string) => {
    toast(message, {
      icon: "\u2139\uFE0F",
      duration: 4000,
    });
  };

  /**
   * Show a toast with a built-in retry button.
   * Useful for failed network requests, uploads, etc.
   */
  const showRetryable = (message: string, onRetry: () => void) => {
    toast(
      (t) => createElement(RetryableToast, { t, message, onRetry }),
      {
        duration: 10000,
        style: {
          padding: "12px",
          maxWidth: "420px",
        },
      },
    );
  };

  /**
   * Show a loading toast that can be resolved or rejected.
   * Returns an object with resolve/reject methods.
   */
  const showLoading = (message: string) => {
    const id = toast.loading(message);

    return {
      resolve: (successMessage: string) => {
        toast.success(successMessage, { id });
      },
      reject: (errorMessage: string) => {
        toast.error(errorMessage, { id });
      },
      dismiss: () => {
        toast.dismiss(id);
      },
    };
  };

  return {
    showSuccess,
    showError,
    showWarning,
    showInfo,
    showRetryable,
    showLoading,
  };
}
