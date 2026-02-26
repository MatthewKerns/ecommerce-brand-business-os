"use client";

import { useState } from "react";
import { Settings } from "lucide-react";
import { ApiKeyManager } from "@/components/ApiKeyManager";

/**
 * Configuration Management Page
 *
 * Interface for managing API keys, service settings, and workspace configuration.
 *
 * Features:
 * - API key management with secure storage
 * - Service configuration forms (TikTok, Blog, Email)
 * - Workspace settings (name, members, invites)
 * - Tabbed interface for different config sections
 * - Key masking and copy-to-clipboard functionality
 *
 * @route /config
 */
export default function ConfigPage() {
  const [activeTab, setActiveTab] = useState<"api-keys" | "services" | "workspace">("api-keys");

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center gap-3">
        <div className="rounded-lg bg-blue-100 p-3">
          <Settings className="h-6 w-6 text-blue-700" />
        </div>
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Configuration</h1>
          <p className="text-sm text-slate-600">
            Manage API keys, services, and workspace settings
          </p>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-slate-200">
        <div className="flex gap-6">
          {[
            { id: "api-keys", label: "API Keys" },
            { id: "services", label: "Services" },
            { id: "workspace", label: "Workspace" },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as typeof activeTab)}
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
