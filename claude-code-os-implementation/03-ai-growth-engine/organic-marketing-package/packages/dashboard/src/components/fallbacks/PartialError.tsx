"use client";

import { AlertCircle, CheckCircle2, XCircle, MailOpen } from "lucide-react";
import { cn } from "@/lib/utils";

interface FeatureStatus {
  name: string;
  available: boolean;
}

interface PartialErrorProps {
  title?: string;
  message?: string;
  features: FeatureStatus[];
  onContactSupport?: () => void;
  className?: string;
}

/**
 * Displayed when partial functionality is available.
 * Shows a checklist of what's working and what's not.
 */
export function PartialError({
  title = "Limited Functionality",
  message = "Some features are temporarily unavailable. You can still use the features listed below.",
  features,
  onContactSupport,
  className,
}: PartialErrorProps) {
  const working = features.filter((f) => f.available);
  const broken = features.filter((f) => !f.available);

  return (
    <div className={cn("rounded-lg border border-amber-200 bg-amber-50 p-5", className)}>
      <div className="flex items-start gap-3">
        <div className="flex-shrink-0 rounded-full bg-amber-100 p-1.5">
          <AlertCircle className="h-5 w-5 text-amber-600" />
        </div>

        <div className="flex-1 min-w-0">
          <h3 className="text-sm font-semibold text-amber-900">{title}</h3>
          <p className="mt-0.5 text-sm text-amber-800">{message}</p>

          <div className="mt-3 grid gap-3 sm:grid-cols-2">
            {working.length > 0 && (
              <div>
                <p className="mb-1.5 text-xs font-medium uppercase tracking-wide text-slate-500">
                  Available
                </p>
                <ul className="space-y-1">
                  {working.map((feature) => (
                    <li
                      key={feature.name}
                      className="flex items-center gap-2 text-sm text-slate-700"
                    >
                      <CheckCircle2 className="h-4 w-4 flex-shrink-0 text-green-500" />
                      {feature.name}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {broken.length > 0 && (
              <div>
                <p className="mb-1.5 text-xs font-medium uppercase tracking-wide text-slate-500">
                  Unavailable
                </p>
                <ul className="space-y-1">
                  {broken.map((feature) => (
                    <li
                      key={feature.name}
                      className="flex items-center gap-2 text-sm text-slate-400"
                    >
                      <XCircle className="h-4 w-4 flex-shrink-0 text-red-400" />
                      {feature.name}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          {onContactSupport && (
            <button
              onClick={onContactSupport}
              className="mt-3 inline-flex items-center gap-1.5 text-sm font-medium text-amber-800 hover:text-amber-700"
            >
              <MailOpen className="h-3.5 w-3.5" />
              Contact Support
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
