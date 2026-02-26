"use client";

import { useWorkspace } from "@/contexts/WorkspaceContext";
import { useState } from "react";
import { Check, ChevronsUpDown, Plus } from "lucide-react";
import { cn } from "@/lib/utils";

/**
 * WorkspaceSelector component allows users to view and switch between workspaces
 *
 * Features:
 * - Displays current workspace with avatar
 * - Dropdown list of all available workspaces
 * - Visual indicator for active workspace
 * - Option to create new workspace
 * - Loading states during workspace switch
 *
 * Uses Clerk Organizations for multi-tenant workspace management.
 *
 * @example
 * ```tsx
 * <WorkspaceSelector />
 * ```
 */
export function WorkspaceSelector() {
  const {
    currentWorkspace,
    workspaces,
    switchWorkspace,
    isLoading,
    hasWorkspaces,
  } = useWorkspace();

  const [isOpen, setIsOpen] = useState(false);
  const [isSwitching, setIsSwitching] = useState(false);

  const handleSwitchWorkspace = async (workspaceId: string) => {
    if (workspaceId === currentWorkspace?.id) {
      setIsOpen(false);
      return;
    }

    try {
      setIsSwitching(true);
      await switchWorkspace(workspaceId);
      setIsOpen(false);
    } catch (error) {
      // Error handling - in production, this should show a toast notification
      // eslint-disable-next-line no-console
      console.error("Failed to switch workspace:", error);
    } finally {
      setIsSwitching(false);
    }
  };

  // Loading state
  if (isLoading) {
    return (
      <div className="flex items-center gap-2 rounded-md border border-slate-200 bg-white px-3 py-2">
        <div className="h-8 w-8 animate-pulse rounded-md bg-slate-200" />
        <div className="flex-1">
          <div className="h-4 w-24 animate-pulse rounded bg-slate-200" />
        </div>
      </div>
    );
  }

  // No workspaces state
  if (!hasWorkspaces || !currentWorkspace) {
    return (
      <div className="flex items-center gap-2 rounded-md border border-slate-200 bg-white px-3 py-2">
        <div className="flex h-8 w-8 items-center justify-center rounded-md bg-slate-100">
          <Plus className="h-4 w-4 text-slate-600" />
        </div>
        <div className="flex-1">
          <p className="text-sm font-medium text-slate-900">No Workspace</p>
          <p className="text-xs text-slate-500">Create or join a workspace</p>
        </div>
      </div>
    );
  }

  return (
    <div className="relative">
      {/* Workspace selector button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        disabled={isSwitching}
        className={cn(
          "flex w-full items-center gap-2 rounded-md border border-slate-200 bg-white px-3 py-2 text-left transition-colors hover:bg-slate-50",
          isSwitching && "cursor-not-allowed opacity-50"
        )}
        aria-haspopup="listbox"
        aria-expanded={isOpen}
      >
        {/* Workspace avatar */}
        <div className="relative h-8 w-8 flex-shrink-0 overflow-hidden rounded-md bg-slate-100">
          {currentWorkspace.imageUrl ? (
            <img
              src={currentWorkspace.imageUrl}
              alt={currentWorkspace.name}
              className="h-full w-full object-cover"
            />
          ) : (
            <div className="flex h-full w-full items-center justify-center bg-gradient-to-br from-blue-500 to-purple-600 text-sm font-semibold text-white">
              {currentWorkspace.name.substring(0, 2).toUpperCase()}
            </div>
          )}
        </div>

        {/* Workspace name */}
        <div className="min-w-0 flex-1">
          <p className="truncate text-sm font-medium text-slate-900">
            {currentWorkspace.name}
          </p>
          <p className="text-xs text-slate-500">
            {currentWorkspace.membersCount}{" "}
            {currentWorkspace.membersCount === 1 ? "member" : "members"}
          </p>
        </div>

        {/* Dropdown icon */}
        <ChevronsUpDown className="h-4 w-4 flex-shrink-0 text-slate-400" />
      </button>

      {/* Dropdown menu */}
      {isOpen && (
        <>
          {/* Backdrop to close dropdown */}
          <div
            className="fixed inset-0 z-10"
            onClick={() => setIsOpen(false)}
          />

          {/* Workspace list */}
          <div className="absolute left-0 right-0 top-full z-20 mt-2 max-h-80 overflow-auto rounded-md border border-slate-200 bg-white shadow-lg">
            <div className="p-1">
              {/* Existing workspaces */}
              <div className="mb-1 px-2 py-1.5">
                <p className="text-xs font-semibold uppercase text-slate-500">
                  Your Workspaces
                </p>
              </div>

              {workspaces.map((workspace) => {
                const isActive = workspace.id === currentWorkspace.id;

                return (
                  <button
                    key={workspace.id}
                    onClick={() => handleSwitchWorkspace(workspace.id)}
                    disabled={isSwitching}
                    className={cn(
                      "flex w-full items-center gap-2 rounded-md px-2 py-2 text-left transition-colors",
                      isActive
                        ? "bg-slate-100"
                        : "hover:bg-slate-50 active:bg-slate-100",
                      isSwitching && "cursor-not-allowed opacity-50"
                    )}
                  >
                    {/* Workspace avatar */}
                    <div className="relative h-8 w-8 flex-shrink-0 overflow-hidden rounded-md bg-slate-100">
                      {workspace.imageUrl ? (
                        <img
                          src={workspace.imageUrl}
                          alt={workspace.name}
                          className="h-full w-full object-cover"
                        />
                      ) : (
                        <div className="flex h-full w-full items-center justify-center bg-gradient-to-br from-blue-500 to-purple-600 text-xs font-semibold text-white">
                          {workspace.name.substring(0, 2).toUpperCase()}
                        </div>
                      )}
                    </div>

                    {/* Workspace info */}
                    <div className="min-w-0 flex-1">
                      <p className="truncate text-sm font-medium text-slate-900">
                        {workspace.name}
                      </p>
                      <p className="text-xs text-slate-500">
                        {workspace.membersCount}{" "}
                        {workspace.membersCount === 1 ? "member" : "members"}
                      </p>
                    </div>

                    {/* Active indicator */}
                    {isActive && (
                      <Check className="h-4 w-4 flex-shrink-0 text-blue-600" />
                    )}
                  </button>
                );
              })}

              {/* Create new workspace option */}
              <div className="mt-1 border-t border-slate-200 pt-1">
                <button
                  onClick={() => {
                    // In production, this would trigger Clerk's organization creation modal
                    // For now, we'll just close the dropdown
                    setIsOpen(false);
                  }}
                  className="flex w-full items-center gap-2 rounded-md px-2 py-2 text-left transition-colors hover:bg-slate-50"
                >
                  <div className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-md bg-slate-100">
                    <Plus className="h-4 w-4 text-slate-600" />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-slate-900">
                      Create Workspace
                    </p>
                    <p className="text-xs text-slate-500">
                      Start a new workspace
                    </p>
                  </div>
                </button>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
