"use client";

import { useState } from "react";
import { useOrganization } from "@clerk/nextjs";
import { ConfigField } from "./ConfigField";
import { cn } from "@/lib/utils";
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
 * WorkspaceSettings component manages workspace configuration and team members
 *
 * Features:
 * - Workspace name editing with Clerk Organizations API
 * - Team members list with role indicators (admin/member)
 * - Invite member button with Clerk's built-in invite flow
 * - Member management (remove members) - admin only
 * - Loading states during save operations
 * - Success/error feedback
 * - Responsive design
 *
 * Uses Clerk Organizations API for workspace management:
 * - useOrganization() for current workspace data and mutations
 * - organization.update() for name changes
 * - organization.inviteMember() for invitations
 * - organization.removeMember() for member removal
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
  const { organization, membership, memberships, isLoaded } = useOrganization({
    memberships: {
      infinite: true,
    },
  });

  const [workspaceName, setWorkspaceName] = useState(
    organization?.name || ""
  );
  const [isSaving, setIsSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);
  const [showInviteForm, setShowInviteForm] = useState(false);
  const [inviteEmail, setInviteEmail] = useState("");
  const [inviteRole, setInviteRole] = useState<"admin" | "basic_member">(
    "basic_member"
  );
  const [isInviting, setIsInviting] = useState(false);
  const [inviteSuccess, setInviteSuccess] = useState(false);
  const [inviteError, setInviteError] = useState<string | null>(null);

  // Check if current user is admin
  const isAdmin = membership?.role === "admin";

  // Update workspace name when organization changes
  if (organization?.name && workspaceName !== organization.name) {
    setWorkspaceName(organization.name);
  }

  // Handle workspace name save
  const handleSaveName = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaveSuccess(false);
    setSaveError(null);

    if (!workspaceName.trim()) {
      setSaveError("Workspace name cannot be empty");
      return;
    }

    if (!organization) {
      setSaveError("No workspace selected");
      return;
    }

    setIsSaving(true);

    try {
      await organization.update({
        name: workspaceName.trim(),
      });

      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 3000);
    } catch (error) {
      setSaveError(
        error instanceof Error ? error.message : "Failed to update workspace name"
      );
    } finally {
      setIsSaving(false);
    }
  };

  // Handle invite member
  const handleInviteMember = async (e: React.FormEvent) => {
    e.preventDefault();
    setInviteSuccess(false);
    setInviteError(null);

    if (!inviteEmail.trim()) {
      setInviteError("Email address is required");
      return;
    }

    // Simple email validation
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(inviteEmail)) {
      setInviteError("Invalid email address");
      return;
    }

    if (!organization) {
      setInviteError("No workspace selected");
      return;
    }

    setIsInviting(true);

    try {
      await organization.inviteMember({
        emailAddress: inviteEmail.trim(),
        role: inviteRole,
      });

      setInviteSuccess(true);
      setInviteEmail("");
      setInviteRole("basic_member");
      setTimeout(() => {
        setInviteSuccess(false);
        setShowInviteForm(false);
      }, 2000);
    } catch (error) {
      setInviteError(
        error instanceof Error ? error.message : "Failed to send invitation"
      );
    } finally {
      setIsInviting(false);
    }
  };

  // Handle remove member
  const handleRemoveMember = async (userId: string) => {
    if (!organization || !isAdmin) {
      return;
    }

    if (
      !confirm(
        "Are you sure you want to remove this member from the workspace?"
      )
    ) {
      return;
    }

    try {
      await organization.removeMember(userId);
    } catch (error) {
      alert(
        error instanceof Error
          ? error.message
          : "Failed to remove member"
      );
    }
  };

  // Loading state
  if (!isLoaded) {
    return (
      <div className={cn("space-y-6", className)}>
        <div className="h-8 w-48 animate-pulse rounded bg-slate-200"></div>
        <div className="space-y-4">
          <div className="h-20 animate-pulse rounded-lg bg-slate-200"></div>
          <div className="h-64 animate-pulse rounded-lg bg-slate-200"></div>
        </div>
      </div>
    );
  }

  // No workspace selected
  if (!organization) {
    return (
      <div className={cn("rounded-lg border border-slate-200 bg-white p-6", className)}>
        <div className="flex items-center gap-3 text-slate-600">
          <AlertCircle className="h-5 w-5" />
          <p className="text-sm">No workspace selected</p>
        </div>
      </div>
    );
  }

  return (
    <div className={cn("space-y-6", className)}>
      {/* Workspace Name Section */}
      <div className="rounded-lg border border-slate-200 bg-white p-6">
        <div className="mb-4 flex items-start gap-3">
          <div className="rounded-lg bg-purple-100 p-2">
            <Building2 className="h-5 w-5 text-purple-700" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-slate-900">
              Workspace Name
            </h3>
            <p className="text-sm text-slate-600">
              Update your workspace name visible to all team members
            </p>
          </div>
        </div>

        <form onSubmit={handleSaveName} className="space-y-4">
          <ConfigField
            id="workspace-name"
            label="Workspace Name"
            type="text"
            value={workspaceName}
            onChange={(e) => setWorkspaceName(e.target.value)}
            placeholder="Enter workspace name"
            required
            disabled={!isAdmin || isSaving}
            helperText={
              isAdmin
                ? "This name will be displayed in the workspace selector"
                : "Only admins can change the workspace name"
            }
          />

          {/* Success/Error Messages */}
          {saveSuccess && (
            <div className="flex items-center gap-2 rounded-lg bg-green-50 p-3 text-sm text-green-700">
              <Check className="h-4 w-4" />
              <span>Workspace name updated successfully!</span>
            </div>
          )}

          {saveError && (
            <div className="flex items-center gap-2 rounded-lg bg-red-50 p-3 text-sm text-red-700">
              <AlertCircle className="h-4 w-4" />
              <span>{saveError}</span>
            </div>
          )}

          {/* Save Button */}
          {isAdmin && (
            <div className="flex justify-end">
              <button
                type="submit"
                disabled={isSaving || workspaceName === organization.name}
                className={cn(
                  "flex items-center gap-2 rounded-lg px-6 py-2.5 text-sm font-medium text-white transition-colors",
                  isSaving || workspaceName === organization.name
                    ? "cursor-not-allowed bg-blue-400"
                    : "bg-blue-600 hover:bg-blue-700"
                )}
              >
                {isSaving ? (
                  <>
                    <div className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
                    <span>Saving...</span>
                  </>
                ) : (
                  <>
                    <Check className="h-4 w-4" />
                    <span>Save Changes</span>
                  </>
                )}
              </button>
            </div>
          )}
        </form>
      </div>

      {/* Team Members Section */}
      <div className="rounded-lg border border-slate-200 bg-white p-6">
        <div className="mb-4 flex items-start justify-between">
          <div className="flex items-start gap-3">
            <div className="rounded-lg bg-blue-100 p-2">
              <Users className="h-5 w-5 text-blue-700" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-slate-900">
                Team Members
              </h3>
              <p className="text-sm text-slate-600">
                Manage workspace members and their roles
              </p>
            </div>
          </div>

          {/* Invite Member Button */}
          {isAdmin && !showInviteForm && (
            <button
              onClick={() => setShowInviteForm(true)}
              className="flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-blue-700"
            >
              <Mail className="h-4 w-4" />
              Invite Member
            </button>
          )}
        </div>

        {/* Invite Form */}
        {showInviteForm && (
          <form
            onSubmit={handleInviteMember}
            className="mb-6 space-y-4 rounded-lg border border-blue-200 bg-blue-50 p-4"
          >
            <div className="flex items-start gap-3">
              <Mail className="h-5 w-5 text-blue-600" />
              <div className="flex-1 space-y-3">
                <h4 className="text-sm font-semibold text-blue-900">
                  Invite New Member
                </h4>

                <ConfigField
                  id="invite-email"
                  label="Email Address"
                  type="text"
                  value={inviteEmail}
                  onChange={(e) => setInviteEmail(e.target.value)}
                  placeholder="member@example.com"
                  required
                  disabled={isInviting}
                  helperText="An invitation email will be sent to this address"
                />

                <ConfigField
                  id="invite-role"
                  label="Role"
                  type="select"
                  value={inviteRole}
                  onChange={(e) =>
                    setInviteRole(e.target.value as "admin" | "basic_member")
                  }
                  disabled={isInviting}
                  options={[
                    { value: "basic_member", label: "Member" },
                    { value: "admin", label: "Admin" },
                  ]}
                  helperText="Admins can manage workspace settings and members"
                />

                {/* Invite Success/Error Messages */}
                {inviteSuccess && (
                  <div className="flex items-center gap-2 rounded-lg bg-green-50 p-3 text-sm text-green-700">
                    <Check className="h-4 w-4" />
                    <span>Invitation sent successfully!</span>
                  </div>
                )}

                {inviteError && (
                  <div className="flex items-center gap-2 rounded-lg bg-red-50 p-3 text-sm text-red-700">
                    <AlertCircle className="h-4 w-4" />
                    <span>{inviteError}</span>
                  </div>
                )}

                {/* Invite Actions */}
                <div className="flex gap-3">
                  <button
                    type="submit"
                    disabled={isInviting}
                    className={cn(
                      "flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-medium text-white transition-colors",
                      isInviting
                        ? "cursor-not-allowed bg-blue-400"
                        : "bg-blue-600 hover:bg-blue-700"
                    )}
                  >
                    {isInviting ? (
                      <>
                        <div className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
                        <span>Sending...</span>
                      </>
                    ) : (
                      <>
                        <Mail className="h-4 w-4" />
                        <span>Send Invitation</span>
                      </>
                    )}
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setShowInviteForm(false);
                      setInviteEmail("");
                      setInviteRole("basic_member");
                      setInviteError(null);
                    }}
                    disabled={isInviting}
                    className="rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 transition-colors hover:bg-slate-50"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            </div>
          </form>
        )}

        {/* Members List */}
        <div className="space-y-2">
          {memberships?.data?.map((member) => (
            <div
              key={member.id}
              className="flex items-center justify-between rounded-lg border border-slate-200 bg-slate-50 p-4"
            >
              <div className="flex items-center gap-3">
                {/* Avatar */}
                {member.publicUserData.imageUrl ? (
                  <img
                    src={member.publicUserData.imageUrl}
                    alt={member.publicUserData.identifier || "Member"}
                    className="h-10 w-10 rounded-full"
                  />
                ) : (
                  <div className="flex h-10 w-10 items-center justify-center rounded-full bg-slate-300">
                    <User className="h-5 w-5 text-slate-600" />
                  </div>
                )}

                {/* Member Info */}
                <div>
                  <div className="flex items-center gap-2">
                    <p className="text-sm font-medium text-slate-900">
                      {member.publicUserData.firstName ||
                        member.publicUserData.identifier ||
                        "Unknown"}
                      {member.publicUserData.lastName &&
                        ` ${member.publicUserData.lastName}`}
                    </p>
                    {member.role === "admin" && (
                      <span className="inline-flex items-center gap-1 rounded-full bg-purple-100 px-2 py-0.5 text-xs font-medium text-purple-700">
                        <Crown className="h-3 w-3" />
                        Admin
                      </span>
                    )}
                    {member.role === "basic_member" && (
                      <span className="inline-flex items-center gap-1 rounded-full bg-blue-100 px-2 py-0.5 text-xs font-medium text-blue-700">
                        <User className="h-3 w-3" />
                        Member
                      </span>
                    )}
                  </div>
                  <p className="text-xs text-slate-600">
                    {member.publicUserData.identifier}
                  </p>
                </div>
              </div>

              {/* Remove Button (admin only, can't remove self) */}
              {isAdmin &&
                member.publicUserData.userId !== membership?.publicUserData.userId && (
                  <button
                    onClick={() =>
                      handleRemoveMember(member.publicUserData.userId!)
                    }
                    className="flex items-center gap-1 rounded-lg border border-red-300 bg-white px-3 py-1.5 text-xs font-medium text-red-700 transition-colors hover:bg-red-50"
                  >
                    <Trash2 className="h-3 w-3" />
                    Remove
                  </button>
                )}
            </div>
          ))}

          {/* Empty state */}
          {memberships?.data?.length === 0 && (
            <div className="rounded-lg border-2 border-dashed border-slate-300 bg-slate-50 p-8 text-center">
              <Users className="mx-auto mb-2 h-8 w-8 text-slate-400" />
              <p className="text-sm text-slate-600">
                No team members yet. Invite your first member to get started.
              </p>
            </div>
          )}
        </div>

        {/* Member Count */}
        {memberships?.data && memberships.data.length > 0 && (
          <div className="mt-4 border-t border-slate-200 pt-4">
            <p className="text-sm text-slate-600">
              {memberships.data.length}{" "}
              {memberships.data.length === 1 ? "member" : "members"} in this
              workspace
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
