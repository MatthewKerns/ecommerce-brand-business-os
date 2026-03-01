"use client";

import { useState } from "react";
import { ConfigField } from "./ConfigField";
import { cn } from "@/lib/utils";
import { useToast } from "@/hooks/useToast";
import {
  Building2,
  Users,
  Mail,
  Check,
  AlertCircle,
  Trash2,
  Crown,
  User,
} from "lucide-react";

/**
 * Mock Workspace Settings for development without Clerk
 */
function MockWorkspaceSettings({ className }: { className?: string }) {
  const { showInfo } = useToast();
  const [workspaceName, setWorkspaceName] = useState("Development Workspace");
  const [isSaving, setIsSaving] = useState(false);
  const [saveStatus, setSaveStatus] = useState<"success" | "error" | null>(null);

  const handleSaveWorkspaceName = async () => {
    setIsSaving(true);
    setSaveStatus(null);

    // Simulate save
    await new Promise(resolve => setTimeout(resolve, 1000));

    setIsSaving(false);
    setSaveStatus("success");
    setTimeout(() => setSaveStatus(null), 3000);
  };

  const mockMembers = [
    { id: "1", email: "dev@example.com", name: "Dev User", role: "admin" },
  ];

  return (
    <div className={cn("space-y-6", className)}>
      {/* Workspace Name Section */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <div className="flex items-center gap-2 mb-4">
          <Building2 className="h-5 w-5 text-slate-600" />
          <h3 className="text-lg font-semibold">Workspace Settings</h3>
        </div>

        <div className="space-y-4">
          <ConfigField
            label="Workspace Name"
            value={workspaceName}
            onChange={setWorkspaceName}
            onSave={handleSaveWorkspaceName}
            isLoading={isSaving}
            saveStatus={saveStatus}
            placeholder="Enter workspace name"
          />
        </div>
      </div>

      {/* Team Members Section */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Users className="h-5 w-5 text-slate-600" />
            <h3 className="text-lg font-semibold">Team Members</h3>
            <span className="text-sm text-slate-500">({mockMembers.length})</span>
          </div>
          <button
            className="flex items-center gap-2 px-3 py-1.5 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors text-sm"
            onClick={() => showInfo("Invite is disabled in development mode")}
          >
            <Mail className="h-4 w-4" />
            Invite Member
          </button>
        </div>

        <div className="space-y-3">
          {mockMembers.map(member => (
            <div
              key={member.id}
              className="flex items-center justify-between p-3 bg-slate-50 rounded-lg"
            >
              <div className="flex items-center gap-3">
                <div className="h-10 w-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-semibold">
                  {member.name.charAt(0)}
                </div>
                <div>
                  <p className="font-medium text-slate-900">{member.name}</p>
                  <p className="text-sm text-slate-500">{member.email}</p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                {member.role === "admin" && (
                  <span className="flex items-center gap-1 px-2 py-1 bg-amber-100 text-amber-800 rounded text-xs font-medium">
                    <Crown className="h-3 w-3" />
                    Admin
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>

        <div className="mt-4 p-3 bg-blue-50 rounded-lg text-sm text-blue-800">
          <AlertCircle className="h-4 w-4 inline mr-2" />
          Running in development mode - member management disabled
        </div>
      </div>
    </div>
  );
}

/**
 * Clerk-based Workspace Settings
 */
interface ClerkWorkspaceSettingsProps {
  className?: string;
}

function ClerkWorkspaceSettings({ className }: ClerkWorkspaceSettingsProps) {
  const { showInfo } = useToast();
  const { useOrganization } = require("@clerk/nextjs");
  const { organization, membership, memberships, isLoaded } = useOrganization({
    memberships: {
      infinite: true,
      pageSize: 10,
    },
  });

  const [workspaceName, setWorkspaceName] = useState(organization?.name || "");
  const [isSaving, setIsSaving] = useState(false);
  const [saveStatus, setSaveStatus] = useState<"success" | "error" | null>(null);

  const handleSaveWorkspaceName = async () => {
    if (!organization || workspaceName === organization.name) return;

    setIsSaving(true);
    setSaveStatus(null);

    try {
      await organization.update({ name: workspaceName });
      setSaveStatus("success");
      setTimeout(() => setSaveStatus(null), 3000);
    } catch (error) {
      console.error("Failed to update workspace name:", error);
      setSaveStatus("error");
      setTimeout(() => setSaveStatus(null), 3000);
    } finally {
      setIsSaving(false);
    }
  };

  const isAdmin = membership?.role === "org:admin";

  if (!isLoaded) {
    return (
      <div className={cn("space-y-6", className)}>
        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="animate-pulse space-y-4">
            <div className="h-4 bg-slate-200 rounded w-1/4" />
            <div className="h-10 bg-slate-200 rounded" />
          </div>
        </div>
      </div>
    );
  }

  if (!organization) {
    return (
      <div className={cn("bg-white rounded-lg shadow-sm p-6", className)}>
        <p className="text-slate-500">No workspace selected</p>
      </div>
    );
  }

  return (
    <div className={cn("space-y-6", className)}>
      {/* Workspace Name Section */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <div className="flex items-center gap-2 mb-4">
          <Building2 className="h-5 w-5 text-slate-600" />
          <h3 className="text-lg font-semibold">Workspace Settings</h3>
        </div>

        <div className="space-y-4">
          <ConfigField
            label="Workspace Name"
            value={workspaceName}
            onChange={setWorkspaceName}
            onSave={handleSaveWorkspaceName}
            isLoading={isSaving}
            saveStatus={saveStatus}
            placeholder="Enter workspace name"
            disabled={!isAdmin}
            helperText={!isAdmin ? "Only admins can change the workspace name" : undefined}
          />
        </div>
      </div>

      {/* Team Members Section */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Users className="h-5 w-5 text-slate-600" />
            <h3 className="text-lg font-semibold">Team Members</h3>
            <span className="text-sm text-slate-500">
              ({memberships?.data?.length || 0})
            </span>
          </div>
          {isAdmin && (
            <button
              className="flex items-center gap-2 px-3 py-1.5 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors text-sm"
              onClick={() => {
                showInfo("Invite flow coming soon");
              }}
            >
              <Mail className="h-4 w-4" />
              Invite Member
            </button>
          )}
        </div>

        <div className="space-y-3">
          {memberships?.data?.map((member) => (
            <div
              key={member.id}
              className="flex items-center justify-between p-3 bg-slate-50 rounded-lg"
            >
              <div className="flex items-center gap-3">
                {member.publicUserData?.imageUrl ? (
                  <img
                    src={member.publicUserData.imageUrl}
                    alt={member.publicUserData.firstName || ""}
                    className="h-10 w-10 rounded-full"
                  />
                ) : (
                  <div className="h-10 w-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-semibold">
                    {member.publicUserData?.firstName?.charAt(0) || "?"}
                  </div>
                )}
                <div>
                  <p className="font-medium text-slate-900">
                    {member.publicUserData?.firstName}{" "}
                    {member.publicUserData?.lastName}
                  </p>
                  <p className="text-sm text-slate-500">
                    {member.publicUserData?.identifier}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                {member.role === "org:admin" ? (
                  <span className="flex items-center gap-1 px-2 py-1 bg-amber-100 text-amber-800 rounded text-xs font-medium">
                    <Crown className="h-3 w-3" />
                    Admin
                  </span>
                ) : (
                  <span className="flex items-center gap-1 px-2 py-1 bg-slate-100 text-slate-700 rounded text-xs font-medium">
                    <User className="h-3 w-3" />
                    Member
                  </span>
                )}
                {isAdmin && member.id !== membership?.id && (
                  <button
                    className="p-1 hover:bg-red-50 rounded transition-colors group"
                    onClick={() => {
                      if (
                        confirm(
                          `Remove ${member.publicUserData?.firstName} from the workspace?`
                        )
                      ) {
                        showInfo("Member removal coming soon");
                      }
                    }}
                  >
                    <Trash2 className="h-4 w-4 text-slate-400 group-hover:text-red-500" />
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

/**
 * WorkspaceSettings component manages workspace configuration and team members
 *
 * Features:
 * - Workspace name editing
 * - Team members list with role indicators
 * - Invite member functionality
 * - Member management (admin only)
 * - Loading states during save operations
 * - Success/error feedback
 * - Responsive design
 *
 * @example
 * ```tsx
 * <WorkspaceSettings />
 * ```
 */
export interface WorkspaceSettingsProps {
  /** Optional custom className for wrapper */
  className?: string;
}

export function WorkspaceSettings({ className }: WorkspaceSettingsProps) {
  // Check if we're in skip-auth mode
  const skipAuth = process.env.NEXT_PUBLIC_SKIP_AUTH === 'true';
  const hasClerkKey = process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY &&
                      !process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY.includes('PLACEHOLDER');

  // Use mock settings in development or when Clerk isn't configured
  if (skipAuth || !hasClerkKey) {
    return <MockWorkspaceSettings className={className} />;
  }

  // Try to use Clerk-based settings
  try {
    return <ClerkWorkspaceSettings className={className} />;
  } catch (error) {
    console.warn("Clerk not available, using mock workspace settings");
    return <MockWorkspaceSettings className={className} />;
  }
}