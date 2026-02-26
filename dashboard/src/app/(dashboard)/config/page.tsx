import { Settings } from "lucide-react";

/**
 * Configuration Management Page
 *
 * Interface for managing API keys, service settings, and workspace configuration.
 *
 * Features (to be implemented):
 * - API key management with secure storage
 * - Service configuration forms (TikTok, Blog, Email)
 * - Workspace settings (name, members, invites)
 * - Tabbed interface for different config sections
 * - Key masking and copy-to-clipboard functionality
 *
 * @route /config
 */
export default function ConfigPage() {
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

      {/* Tab Navigation Placeholder */}
      <div className="border-b border-slate-200">
        <div className="flex gap-6">
          {["API Keys", "Services", "Workspace"].map((tab, index) => (
            <button
              key={tab}
              className={`border-b-2 px-1 pb-3 text-sm font-medium transition-colors ${
                index === 0
                  ? "border-blue-600 text-blue-600"
                  : "border-transparent text-slate-600 hover:text-slate-900"
              }`}
            >
              {tab}
            </button>
          ))}
        </div>
      </div>

      {/* API Keys Section */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-slate-900">API Keys</h2>
            <p className="text-sm text-slate-600">
              Manage authentication keys for external services
            </p>
          </div>
          <button className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700">
            Add API Key
          </button>
        </div>

        {/* API Keys List Placeholder */}
        <div className="space-y-3">
          {[
            { name: "TikTok API Key", service: "TikTok", created: "2024-01-15" },
            { name: "OpenAI API Key", service: "AI Agents", created: "2024-01-10" },
            { name: "SendGrid API Key", service: "Email", created: "2024-01-05" },
          ].map((key) => (
            <div
              key={key.name}
              className="flex items-center justify-between rounded-lg border border-slate-200 bg-white p-4"
            >
              <div className="flex-1">
                <div className="flex items-center gap-3">
                  <h3 className="font-semibold text-slate-900">{key.name}</h3>
                  <span className="rounded-full bg-slate-100 px-2 py-0.5 text-xs font-medium text-slate-700">
                    {key.service}
                  </span>
                </div>
                <div className="mt-1 flex items-center gap-4 text-sm text-slate-600">
                  <span className="font-mono">sk-••••••••••••••••</span>
                  <span>Created {key.created}</span>
                </div>
              </div>
              <div className="flex gap-2">
                <button className="rounded-lg px-3 py-1.5 text-sm font-medium text-slate-700 hover:bg-slate-100">
                  Copy
                </button>
                <button className="rounded-lg px-3 py-1.5 text-sm font-medium text-red-600 hover:bg-red-50">
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Service Configuration Section */}
      <div className="rounded-lg border border-slate-200 bg-white p-6">
        <h2 className="mb-4 text-lg font-semibold text-slate-900">
          Service Configuration
        </h2>
        <p className="text-sm text-slate-600">
          Configure settings for TikTok, Blog Engine, Email Automation, and other services.
          Configuration forms will be displayed here.
        </p>
      </div>
    </div>
  );
}
