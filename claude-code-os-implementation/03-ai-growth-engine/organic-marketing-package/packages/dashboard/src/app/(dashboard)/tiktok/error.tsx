"use client";

import { useEffect } from "react";
import { AlertCircle, RefreshCw } from "lucide-react";

export default function TikTokError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // Log the error to an error reporting service
    console.error("TikTok page error:", error);
  }, [error]);

  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh]">
      <div className="text-center max-w-md">
        <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
        <h2 className="text-lg font-semibold text-slate-900 mb-2">
          Something went wrong loading TikTok Studio
        </h2>
        <p className="text-sm text-slate-600 mb-6">
          {error.message || "An unexpected error occurred while loading the TikTok Content Studio."}
        </p>

        {/* Troubleshooting tips */}
        <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 mb-6 text-left">
          <p className="text-xs font-medium text-amber-900 mb-2">Troubleshooting Tips:</p>
          <ul className="text-xs text-amber-800 space-y-1">
            <li>• Try disabling browser extensions temporarily</li>
            <li>• Clear your browser cache and cookies</li>
            <li>• Check if the backend API is running on port 8000</li>
            <li>• Refresh the page or try a different browser</li>
          </ul>
        </div>

        <button
          onClick={reset}
          className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <RefreshCw className="h-4 w-4" />
          Try Again
        </button>
      </div>
    </div>
  );
}