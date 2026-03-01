"use client";

import { createContext, useContext, ReactNode, useMemo } from "react";

/**
 * Workspace data structure representing a Clerk organization
 */
export interface Workspace {
  id: string;
  name: string;
  slug: string | null;
  imageUrl: string;
  membersCount?: number;
}

/**
 * WorkspaceContext provides workspace (organization) state and operations
 * throughout the application
 */
interface WorkspaceContextValue {
  /**
   * Current active workspace (organization)
   */
  currentWorkspace: Workspace | null;

  /**
   * List of all workspaces the user has access to
   */
  workspaces: Workspace[];

  /**
   * Whether workspace data is currently loading
   */
  isLoading: boolean;

  /**
   * Switch to a different workspace
   * @param workspaceId - The ID of the workspace to switch to
   */
  switchWorkspace: (workspaceId: string) => Promise<void>;

  /**
   * Whether the user is a member of any workspaces
   */
  hasWorkspaces: boolean;
}

const WorkspaceContext = createContext<WorkspaceContextValue | undefined>(
  undefined
);

interface WorkspaceProviderProps {
  children: ReactNode;
}

/**
 * Mock workspace provider for development without Clerk
 */
function MockWorkspaceProvider({ children }: WorkspaceProviderProps) {
  const mockWorkspace: Workspace = {
    id: "dev-workspace",
    name: "Development Workspace",
    slug: "dev-workspace",
    imageUrl: "https://api.dicebear.com/7.x/shapes/svg?seed=workspace",
    membersCount: 1,
  };

  const value: WorkspaceContextValue = {
    currentWorkspace: mockWorkspace,
    workspaces: [mockWorkspace],
    isLoading: false,
    switchWorkspace: async () => {
      console.log("Switching workspaces is disabled in development mode");
    },
    hasWorkspaces: true,
  };

  return (
    <WorkspaceContext.Provider value={value}>
      {children}
    </WorkspaceContext.Provider>
  );
}

/**
 * Clerk-based workspace provider for production
 */
function ClerkWorkspaceProvider({ children }: WorkspaceProviderProps) {
  // Dynamically import Clerk hooks to avoid errors when not available
  const { useUser, useOrganization, useOrganizationList } = require("@clerk/nextjs");

  const { isLoaded: isUserLoaded } = useUser();
  const { organization, isLoaded: isOrgLoaded } = useOrganization();
  const {
    userMemberships,
    isLoaded: isListLoaded,
    setActive,
  } = useOrganizationList({
    userMemberships: {
      infinite: true,
    },
  });

  const isLoading = !isUserLoaded || !isOrgLoaded || !isListLoaded;

  // Map Clerk organizations to workspace objects
  const workspaces: Workspace[] = useMemo(
    () =>
      userMemberships?.data?.map((membership: any) => ({
        id: membership.organization.id,
        name: membership.organization.name,
        slug: membership.organization.slug,
        imageUrl: membership.organization.imageUrl,
        membersCount: membership.organization.membersCount,
      })) ?? [],
    [userMemberships?.data]
  );

  const currentWorkspace: Workspace | null = organization
    ? {
        id: organization.id,
        name: organization.name,
        slug: organization.slug,
        imageUrl: organization.imageUrl,
        membersCount: organization.membersCount,
      }
    : null;

  /**
   * Switch to a different workspace by setting it as the active organization
   */
  const switchWorkspace = async (workspaceId: string) => {
    if (!setActive) {
      throw new Error("setActive is not available");
    }

    await setActive({ organization: workspaceId });
  };

  const value: WorkspaceContextValue = {
    currentWorkspace,
    workspaces,
    isLoading,
    switchWorkspace,
    hasWorkspaces: workspaces.length > 0,
  };

  return (
    <WorkspaceContext.Provider value={value}>
      {children}
    </WorkspaceContext.Provider>
  );
}

/**
 * WorkspaceProvider wraps the application and provides workspace context
 *
 * Uses Clerk Organizations as the multi-tenant workspace system in production,
 * or provides mock data in development when skip-auth is enabled.
 *
 * @example
 * ```tsx
 * <WorkspaceProvider>
 *   <YourApp />
 * </WorkspaceProvider>
 * ```
 */
export function WorkspaceProvider({ children }: WorkspaceProviderProps) {
  // Check if we're in skip-auth mode
  const skipAuth = process.env.NEXT_PUBLIC_SKIP_AUTH === 'true';
  const hasClerkKey = process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY &&
                      !process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY.includes('PLACEHOLDER');

  // Use mock provider in development or when Clerk isn't configured
  if (skipAuth || !hasClerkKey) {
    return <MockWorkspaceProvider>{children}</MockWorkspaceProvider>;
  }

  // Try to use Clerk provider
  try {
    return <ClerkWorkspaceProvider>{children}</ClerkWorkspaceProvider>;
  } catch (error) {
    console.warn("Clerk not available, using mock workspace provider");
    return <MockWorkspaceProvider>{children}</MockWorkspaceProvider>;
  }
}

/**
 * Hook to access workspace context
 *
 * @throws {Error} If used outside of WorkspaceProvider
 *
 * @example
 * ```tsx
 * function MyComponent() {
 *   const { currentWorkspace, switchWorkspace } = useWorkspace();
 *
 *   return (
 *     <div>
 *       <p>Current workspace: {currentWorkspace?.name}</p>
 *       <button onClick={() => switchWorkspace('workspace-id')}>
 *         Switch
 *       </button>
 *     </div>
 *   );
 * }
 * ```
 */
export function useWorkspace() {
  const context = useContext(WorkspaceContext);

  if (context === undefined) {
    throw new Error("useWorkspace must be used within a WorkspaceProvider");
  }

  return context;
}