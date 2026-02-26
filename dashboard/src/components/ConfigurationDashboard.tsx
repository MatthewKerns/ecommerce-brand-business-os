"use client";

import { useState } from "react";
import { ApiKeyManager } from "@/components/ApiKeyManager";
import { cn } from "@/lib/utils";

/**
 * ConfigurationDashboard component provides tabbed interface for managing configuration
 *
 * Features:
 * - Tabbed interface with API Keys, Services, and Workspace sections
 * - API key management with secure storage
 * - Service configuration forms (TikTok, Blog, Email) - placeholder
 * - Workspace settings (name, members, invites) - placeholder
 * - Tab state management with active highlighting
 * - Responsive design
 *
 * @example
 * ```tsx
 * <ConfigurationDashboard />
 * ```
 */

export type ConfigTab = "api-keys" | "services" | "workspace";

export interface ConfigurationDashboardProps {
  /** Initial active tab - defaults to "api-keys" */
  defaultTab?: ConfigTab;
  /** Optional custom className for wrapper */
  className?: string;
}

const TABS = [
  { id: "api-keys" as ConfigTab, label: "API Keys" },
  { id: "services" as ConfigTab, label: "Services" },
  { id: "workspace" as ConfigTab, label: "Workspace" },
];

export function ConfigurationDashboard({
  defaultTab = "api-keys",
  className,
}: ConfigurationDashboardProps) {
  const [activeTab, setActiveTab] = useState<ConfigTab>(defaultTab);

  return (
    <div className={cn("space-y-6", className)}>
      {/* Tab Navigation */}
      <div className="border-b border-slate-200">
        <div className="flex gap-6">
          {TABS.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`border-b-2 px-1 pb-3 text-sm font-medium transition-colors ${
                activeTab === tab.id
                  ? "border-blue-600 text-blue-600"
                  : "border-transparent text-slate-600 hover:text-slate-900"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Tab Content */}
      {activeTab === "api-keys" && (
        <ApiKeyManager
          onAddKey={() => {
            // TODO: Implement add key dialog in future subtask
          }}
          onDeleteKey={(id) => {
            // TODO: Implement delete API call in future subtask
          }}
          onCopyKey={(value) => {
            // Success feedback is handled in ApiKeyItem
          }}
        />
      )}

      {activeTab === "services" && (
        <div className="rounded-lg border border-slate-200 bg-white p-6">
          <h2 className="mb-4 text-lg font-semibold text-slate-900">
            Service Configuration
          </h2>
          <p className="text-sm text-slate-600">
            Configure settings for TikTok, Blog Engine, Email Automation, and other services.
            Configuration forms will be displayed here in a future subtask.
          </p>
        </div>
      )}

      {activeTab === "workspace" && (
        <div className="rounded-lg border border-slate-200 bg-white p-6">
          <h2 className="mb-4 text-lg font-semibold text-slate-900">
            Workspace Settings
          </h2>
          <p className="text-sm text-slate-600">
            Manage workspace name, team members, and invitations.
            Workspace settings will be displayed here in a future subtask.
          </p>
        </div>
      )}
    </div>
  );
}
