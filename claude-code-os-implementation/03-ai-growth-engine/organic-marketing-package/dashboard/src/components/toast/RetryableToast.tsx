"use client";

import { RefreshCw, X } from "lucide-react";
import toast, { Toast } from "react-hot-toast";

interface RetryableToastProps {
  t: Toast;
  message: string;
  onRetry: () => void;
}

/**
 * A toast component with a built-in retry button for failed operations.
 * Used by the useToast hook for retryable error scenarios.
 */
export function RetryableToast({ t, message, onRetry }: RetryableToastProps) {
  return (
    <div
      className={`flex items-start gap-3 ${t.visible ? "animate-in fade-in slide-in-from-right" : "animate-out fade-out slide-out-to-right"}`}
    >
      <div className="flex-shrink-0 rounded-full bg-red-100 p-1.5">
        <svg
          className="h-4 w-4 text-red-600"
          fill="none"
          viewBox="0 0 24 24"
          strokeWidth={2}
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126ZM12 15.75h.007v.008H12v-.008Z"
          />
        </svg>
      </div>

      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-slate-900">Operation Failed</p>
        <p className="mt-0.5 text-sm text-slate-600">{message}</p>
        <button
          onClick={() => {
            toast.dismiss(t.id);
            onRetry();
          }}
          className="mt-2 inline-flex items-center gap-1.5 rounded-md bg-slate-900 px-3 py-1.5 text-xs font-medium text-white transition-colors hover:bg-slate-800"
        >
          <RefreshCw className="h-3 w-3" />
          Retry
        </button>
      </div>

      <button
        onClick={() => toast.dismiss(t.id)}
        className="flex-shrink-0 rounded-md p-1 text-slate-400 transition-colors hover:bg-slate-100 hover:text-slate-600"
      >
        <X className="h-4 w-4" />
      </button>
    </div>
  );
}
