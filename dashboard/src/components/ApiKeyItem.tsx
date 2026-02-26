"use client";

import { useState } from "react";
import { Copy, Trash2, Key, Check } from "lucide-react";
import { cn } from "@/lib/utils";

/**
 * ApiKeyItem component displays a single API key with masked value and actions
 *
 * Features:
 * - Displays API key name, service tag, and masked value
 * - Shows created date and last used timestamp
 * - Copy to clipboard button with success feedback
 * - Delete button with confirmation dialog
 * - Loading state with skeleton animation
 * - Responsive design with hover effects
 *
 * @example
 * ```tsx
 * <ApiKeyItem
 *   id="key-123"
 *   name="TikTok API Key"
 *   service="TikTok"
 *   maskedValue="sk-••••••••••••••••"
 *   createdAt="2024-01-15"
 *   lastUsed="2024-02-20"
 *   onDelete={(id) => handleDelete(id)}
 *   onCopy={(value) => handleCopy(value)}
 * />
 * ```
 */

export interface ApiKeyItemProps {
  /** Unique identifier for the API key */
  id: string;
  /** Display name of the API key */
  name: string;
  /** Service or platform this key is for */
  service: string;
  /** Masked value to display (e.g., "sk-••••••••••••••••") */
  maskedValue: string;
  /** Full value for copying (not displayed) */
  fullValue: string;
  /** Date the key was created */
  createdAt: string;
  /** Date the key was last used (optional) */
  lastUsed?: string;
  /** Callback when delete is confirmed */
  onDelete?: (id: string) => void;
  /** Callback when copy is clicked */
  onCopy?: (value: string) => void;
  /** Loading state - shows skeleton when true */
  isLoading?: boolean;
  /** Optional custom className for card wrapper */
  className?: string;
}

export function ApiKeyItem({
  id,
  name,
  service,
  maskedValue,
  fullValue,
  createdAt,
  lastUsed,
  onDelete,
  onCopy,
  isLoading = false,
  className,
}: ApiKeyItemProps) {
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [copied, setCopied] = useState(false);

  // Loading state
  if (isLoading) {
    return (
      <div
        className={cn(
          "rounded-lg border border-slate-200 bg-white p-4",
          className
        )}
      >
        <div className="flex items-center justify-between">
          <div className="flex-1 space-y-2">
            <div className="flex items-center gap-2">
              <div className="h-5 w-32 animate-pulse rounded bg-slate-200"></div>
              <div className="h-4 w-16 animate-pulse rounded-full bg-slate-200"></div>
            </div>
            <div className="h-4 w-48 animate-pulse rounded bg-slate-200"></div>
          </div>
          <div className="flex gap-2">
            <div className="h-8 w-16 animate-pulse rounded-lg bg-slate-200"></div>
            <div className="h-8 w-16 animate-pulse rounded-lg bg-slate-200"></div>
          </div>
        </div>
      </div>
    );
  }

  // Handle copy to clipboard
  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(fullValue);
      setCopied(true);
      onCopy?.(fullValue);

      // Reset copied state after 2 seconds
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error("Failed to copy:", err);
    }
  };

  // Handle delete confirmation
  const handleDeleteConfirm = () => {
    onDelete?.(id);
    setShowDeleteDialog(false);
  };

  return (
    <>
      <div
        className={cn(
          "rounded-lg border border-slate-200 bg-white p-4 transition-shadow hover:shadow-md",
          className
        )}
      >
        <div className="flex items-center justify-between gap-4">
          {/* Key Info */}
          <div className="flex flex-1 items-center gap-3">
            {/* Icon */}
            <div className="rounded-md bg-blue-100 p-2">
              <Key className="h-4 w-4 text-blue-700" />
            </div>

            {/* Details */}
            <div className="flex-1 space-y-1">
              <div className="flex items-center gap-2">
                <h3 className="font-semibold text-slate-900">{name}</h3>
                <span className="rounded-full bg-slate-100 px-2 py-0.5 text-xs font-medium text-slate-700">
                  {service}
                </span>
              </div>
              <div className="flex flex-wrap items-center gap-3 text-sm text-slate-600">
                <span className="font-mono text-xs">{maskedValue}</span>
                <span className="text-xs">Created {createdAt}</span>
                {lastUsed && (
                  <span className="text-xs">Last used {lastUsed}</span>
                )}
              </div>
            </div>
          </div>

          {/* Actions */}
          <div className="flex gap-2">
            <button
              onClick={handleCopy}
              className={cn(
                "flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-sm font-medium transition-colors",
                copied
                  ? "bg-green-100 text-green-700"
                  : "text-slate-700 hover:bg-slate-100"
              )}
              title="Copy to clipboard"
            >
              {copied ? (
                <>
                  <Check className="h-3.5 w-3.5" />
                  <span>Copied</span>
                </>
              ) : (
                <>
                  <Copy className="h-3.5 w-3.5" />
                  <span>Copy</span>
                </>
              )}
            </button>
            <button
              onClick={() => setShowDeleteDialog(true)}
              className="flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-sm font-medium text-red-600 transition-colors hover:bg-red-50"
              title="Delete API key"
            >
              <Trash2 className="h-3.5 w-3.5" />
              <span>Delete</span>
            </button>
          </div>
        </div>
      </div>

      {/* Delete Confirmation Dialog */}
      {showDeleteDialog && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          {/* Backdrop */}
          <div
            className="absolute inset-0 bg-black/50"
            onClick={() => setShowDeleteDialog(false)}
          />

          {/* Dialog */}
          <div className="relative z-10 w-full max-w-md rounded-lg bg-white p-6 shadow-xl">
            <div className="mb-4 flex items-start gap-3">
              <div className="rounded-full bg-red-100 p-2">
                <Trash2 className="h-5 w-5 text-red-600" />
              </div>
              <div className="flex-1">
                <h3 className="text-lg font-semibold text-slate-900">
                  Delete API Key
                </h3>
                <p className="mt-1 text-sm text-slate-600">
                  Are you sure you want to delete <strong>{name}</strong>? This
                  action cannot be undone and may break services using this key.
                </p>
              </div>
            </div>

            <div className="flex justify-end gap-3">
              <button
                onClick={() => setShowDeleteDialog(false)}
                className="rounded-lg px-4 py-2 text-sm font-medium text-slate-700 transition-colors hover:bg-slate-100"
              >
                Cancel
              </button>
              <button
                onClick={handleDeleteConfirm}
                className="rounded-lg bg-red-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-red-700"
              >
                Delete Key
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
