"use client";

import { useState } from "react";
import { ApiKeyManager } from "@/components/ApiKeyManager";
import { ServiceConfigForm, ServiceType } from "@/components/ServiceConfigForm";
import { WorkspaceSettings } from "@/components/WorkspaceSettings";
import { cn } from "@/lib/utils";

/**
 * ConfigurationDashboard component provides tabbed interface for managing configuration
 *
 * Features:
 * - Tabbed interface with API Keys, Services, and Workspace sections
 * - API key management with secure storage
 * - Service configuration forms (TikTok, Blog, Email)
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
  const [activeService, setActiveService] = useState<ServiceType>("tiktok");

  const services: Array<{ id: ServiceType; label: string }> = [
    { id: "tiktok", label: "TikTok" },
    { id: "blog", label: "Blog Engine" },
    { id: "email", label: "Email Automation" },
  ];

  // Handle service configuration save
  const handleSaveConfig = async (config: Record<string, string | number>) => {
    // TODO: Implement API call in future subtask
    // For now, just log the config
    // console.log(`Saving ${activeService} config:`, config);
    // Simulate API delay
    await new Promise((resolve) => setTimeout(resolve, 1000));
  };

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
        <div className="space-y-6">
          {/* Service Selection */}
          <div className="flex gap-3 rounded-lg border border-slate-200 bg-white p-2">
            {services.map((service) => (
              <button
                key={service.id}
                onClick={() => setActiveService(service.id)}
                className={cn(
                  "flex-1 rounded-md px-4 py-2 text-sm font-medium transition-colors",
                  activeService === service.id
                    ? "bg-blue-100 text-blue-700"
                    : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"
                )}
              >
                {service.label}
              </button>
            ))}
          </div>

          {/* Service Configuration Form */}
          <div className="rounded-lg border border-slate-200 bg-white p-6">
            <ServiceConfigForm
              service={activeService}
              onSave={handleSaveConfig}
            />
          </div>
        </div>
      )}

      {activeTab === "workspace" && <WorkspaceSettings />}
    </div>
  );
}
