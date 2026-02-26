import { Settings } from "lucide-react";
import { ConfigurationDashboard } from "@/components/ConfigurationDashboard";

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

      {/* Configuration Dashboard */}
      <ConfigurationDashboard />
    </div>
  );
}
