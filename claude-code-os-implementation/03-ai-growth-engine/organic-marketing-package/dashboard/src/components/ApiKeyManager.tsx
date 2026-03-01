"use client";

import { useState } from "react";
import { Plus, Key } from "lucide-react";
import { ApiKeyItem } from "./ApiKeyItem";
import { cn } from "@/lib/utils";
import { useToast } from "@/hooks/useToast";

/**
 * ApiKeyManager component manages the list of API keys
 *
 * Features:
 * - Displays list of API keys with ApiKeyItem components
 * - "Add API Key" button to create new keys
 * - Empty state when no keys exist
 * - Loading state for initial data fetch
 * - Handles copy and delete actions
 * - Responsive design
 *
 * @example
 * ```tsx
 * <ApiKeyManager
 *   keys={apiKeys}
 *   onAddKey={() => handleAddKey()}
 *   onDeleteKey={(id) => handleDeleteKey(id)}
 *   onCopyKey={(value) => handleCopyKey(value)}
 *   isLoading={false}
 * />
 * ```
 */

export interface ApiKey {
  /** Unique identifier */
  id: string;
  /** Display name */
  name: string;
  /** Service or platform */
  service: string;
  /** Masked value for display */
  maskedValue: string;
  /** Full value (not displayed) */
  fullValue: string;
  /** Created date */
  createdAt: string;
  /** Last used date (optional) */
  lastUsed?: string;
}

export interface ApiKeyManagerProps {
  /** Array of API keys to display */
  keys?: ApiKey[];
  /** Callback when "Add API Key" is clicked */
  onAddKey?: () => void;
  /** Callback when a key is deleted */
  onDeleteKey?: (id: string) => void;
  /** Callback when a key is copied */
  onCopyKey?: (value: string) => void;
  /** Loading state - shows skeleton when true */
  isLoading?: boolean;
  /** Optional custom className for container */
  className?: string;
}

/**
 * Default mock data for demonstration
 */
const DEFAULT_KEYS: ApiKey[] = [
  {
    id: "key-1",
    name: "TikTok API Key",
    service: "TikTok",
    maskedValue: "sk-••••••••••••••••",
    fullValue: "sk-tiktok-api-key-example-12345678",
    createdAt: "2024-01-15",
    lastUsed: "2024-02-20",
  },
  {
    id: "key-2",
    name: "OpenAI API Key",
    service: "AI Agents",
    maskedValue: "sk-••••••••••••••••",
    fullValue: "sk-openai-api-key-example-87654321",
    createdAt: "2024-01-10",
    lastUsed: "2024-02-19",
  },
  {
    id: "key-3",
    name: "SendGrid API Key",
    service: "Email",
    maskedValue: "SG.••••••••••••••••",
    fullValue: "SG.sendgrid-api-key-example-abcdefgh",
    createdAt: "2024-01-05",
    lastUsed: "2024-02-18",
  },
];

export function ApiKeyManager({
  keys = DEFAULT_KEYS,
  onAddKey,
  onDeleteKey,
  onCopyKey,
  isLoading = false,
  className,
}: ApiKeyManagerProps) {
  const [localKeys, setLocalKeys] = useState<ApiKey[]>(keys);

  // Handle local delete if no callback provided
  const handleDelete = (id: string) => {
    if (onDeleteKey) {
      onDeleteKey(id);
    } else {
      // Local state management for demo
      setLocalKeys((prev) => prev.filter((key) => key.id !== id));
    }
  };

  // Handle copy
  const handleCopy = (value: string) => {
    onCopyKey?.(value);
  };

  const { showInfo } = useToast();

  // Handle add key
  const handleAddKey = () => {
    if (onAddKey) {
      onAddKey();
    } else {
      showInfo("Add API Key dialog coming soon");
    }
  };

  // Loading state
  if (isLoading) {
    return (
      <div className={cn("space-y-4", className)}>
        <div className="flex items-center justify-between">
          <div className="space-y-1">
            <div className="h-6 w-32 animate-pulse rounded bg-slate-200"></div>
            <div className="h-4 w-64 animate-pulse rounded bg-slate-200"></div>
          </div>
          <div className="h-10 w-28 animate-pulse rounded-lg bg-slate-200"></div>
        </div>
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <ApiKeyItem
              key={i}
              id={`loading-${i}`}
              name=""
              service=""
              maskedValue=""
              fullValue=""
              createdAt=""
              isLoading={true}
            />
          ))}
        </div>
      </div>
    );
  }

  // Empty state
  if (localKeys.length === 0) {
    return (
      <div className={cn("space-y-4", className)}>
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-slate-900">API Keys</h2>
            <p className="text-sm text-slate-600">
              Manage authentication keys for external services
            </p>
          </div>
          <button
            onClick={handleAddKey}
            className="flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-blue-700"
          >
            <Plus className="h-4 w-4" />
            Add API Key
          </button>
        </div>

        {/* Empty state */}
        <div className="rounded-lg border-2 border-dashed border-slate-300 bg-slate-50 p-12 text-center">
          <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-slate-200">
            <Key className="h-8 w-8 text-slate-400" />
          </div>
          <h3 className="mb-2 text-lg font-semibold text-slate-900">
            No API Keys
          </h3>
          <p className="mb-4 text-sm text-slate-600">
            You haven&apos;t added any API keys yet. Add your first key to get
            started.
          </p>
          <button
            onClick={handleAddKey}
            className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-blue-700"
          >
            <Plus className="h-4 w-4" />
            Add Your First API Key
          </button>
        </div>
      </div>
    );
  }

  // Keys list
  return (
    <div className={cn("space-y-4", className)}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold text-slate-900">API Keys</h2>
          <p className="text-sm text-slate-600">
            Manage authentication keys for external services
          </p>
        </div>
        <button
          onClick={handleAddKey}
          className="flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-blue-700"
        >
          <Plus className="h-4 w-4" />
          Add API Key
        </button>
      </div>

      {/* Keys List */}
      <div className="space-y-3">
        {localKeys.map((key) => (
          <ApiKeyItem
            key={key.id}
            {...key}
            onDelete={handleDelete}
            onCopy={handleCopy}
          />
        ))}
      </div>
    </div>
  );
}
