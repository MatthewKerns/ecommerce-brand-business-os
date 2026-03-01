/**
 * Workspace Resolver for API Routes
 *
 * Provides utilities to resolve workspace (organization) context from Clerk
 * and validate workspace access for API routes.
 *
 * @example
 * ```typescript
 * import { getWorkspaceContext } from '@/lib/workspace-resolver'
 *
 * export async function GET(request: NextRequest) {
 *   const workspace = await getWorkspaceContext(workspaceId)
 *   console.log(workspace.name, workspace.membersCount)
 * }
 * ```
 */

import { clerkClient } from '@clerk/nextjs'

/**
 * Workspace data structure
 */
export interface WorkspaceContext {
  /**
   * Workspace (organization) ID
   */
  id: string

  /**
   * Workspace name
   */
  name: string

  /**
   * URL-friendly slug
   */
  slug: string | null

  /**
   * Workspace logo/image URL
   */
  imageUrl: string

  /**
   * Number of members in the workspace
   */
  membersCount: number

  /**
   * When the workspace was created
   */
  createdAt: Date

  /**
   * When the workspace was last updated
   */
  updatedAt: Date
}

/**
 * Workspace member information
 */
export interface WorkspaceMember {
  /**
   * User ID
   */
  userId: string

  /**
   * Role in the workspace (e.g., 'admin', 'basic_member')
   */
  role: string

  /**
   * When the user joined the workspace
   */
  createdAt: Date
}

/**
 * Get workspace context by ID
 *
 * Fetches workspace (organization) details from Clerk.
 * Throws an error if the workspace is not found.
 *
 * @param {string} workspaceId - The workspace (organization) ID
 * @returns {Promise<WorkspaceContext>} Workspace details
 * @throws {Error} If workspace is not found
 *
 * @example
 * ```typescript
 * const workspace = await getWorkspaceContext('org_abc123')
 * console.log(workspace.name)
 * ```
 */
export async function getWorkspaceContext(
  workspaceId: string
): Promise<WorkspaceContext> {
  try {
    // Fetch organization from Clerk
    const organization = await clerkClient.organizations.getOrganization({
      organizationId: workspaceId,
    })

    if (!organization) {
      throw new Error(`Workspace not found: ${workspaceId}`)
    }

    return {
      id: organization.id,
      name: organization.name,
      slug: organization.slug,
      imageUrl: organization.imageUrl,
      membersCount: organization.membersCount || 0,
      createdAt: new Date(organization.createdAt),
      updatedAt: new Date(organization.updatedAt),
    }
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(`Failed to get workspace: ${error.message}`)
    }
    throw new Error('Failed to get workspace: Unknown error')
  }
}

/**
 * Check if a user is a member of a workspace
 *
 * Verifies that the user has access to the specified workspace.
 * Returns true if the user is a member, false otherwise.
 *
 * @param {string} userId - The user ID
 * @param {string} workspaceId - The workspace (organization) ID
 * @returns {Promise<boolean>} True if user is a member, false otherwise
 *
 * @example
 * ```typescript
 * const isMember = await isWorkspaceMember(userId, workspaceId)
 * if (!isMember) {
 *   throw new Error('Access denied')
 * }
 * ```
 */
export async function isWorkspaceMember(
  userId: string,
  workspaceId: string
): Promise<boolean> {
  try {
    // Get organization memberships for the user
    const memberships =
      await clerkClient.users.getOrganizationMembershipList({
        userId,
      })

    // Check if user is a member of the workspace
    return memberships.some((membership) => membership.organization.id === workspaceId)
  } catch (error) {
    // Log error but don't expose internal details
    if (error instanceof Error) {
      // eslint-disable-next-line no-console
      console.error('Failed to check workspace membership:', error.message)
    }
    return false
  }
}

/**
 * Get workspace member details
 *
 * Fetches information about a specific member in a workspace.
 * Returns null if the user is not a member.
 *
 * @param {string} userId - The user ID
 * @param {string} workspaceId - The workspace (organization) ID
 * @returns {Promise<WorkspaceMember | null>} Member details or null
 *
 * @example
 * ```typescript
 * const member = await getWorkspaceMember(userId, workspaceId)
 * if (member?.role === 'admin') {
 *   // User is an admin
 * }
 * ```
 */
export async function getWorkspaceMember(
  userId: string,
  workspaceId: string
): Promise<WorkspaceMember | null> {
  try {
    // Get organization memberships for the user
    const memberships =
      await clerkClient.users.getOrganizationMembershipList({
        userId,
      })

    // Find membership for this workspace
    const membership = memberships.find(
      (m) => m.organization.id === workspaceId
    )

    if (!membership) {
      return null
    }

    return {
      userId,
      role: membership.role,
      createdAt: new Date(membership.createdAt),
    }
  } catch (error) {
    // Log error but don't expose internal details
    if (error instanceof Error) {
      // eslint-disable-next-line no-console
      console.error('Failed to get workspace member:', error.message)
    }
    return null
  }
}

/**
 * Check if a user is an admin of a workspace
 *
 * Verifies that the user has admin role in the specified workspace.
 * Useful for protecting admin-only API endpoints.
 *
 * @param {string} userId - The user ID
 * @param {string} workspaceId - The workspace (organization) ID
 * @returns {Promise<boolean>} True if user is an admin, false otherwise
 *
 * @example
 * ```typescript
 * const isAdmin = await isWorkspaceAdmin(userId, workspaceId)
 * if (!isAdmin) {
 *   return NextResponse.json(
 *     { error: 'Admin access required' },
 *     { status: 403 }
 *   )
 * }
 * ```
 */
export async function isWorkspaceAdmin(
  userId: string,
  workspaceId: string
): Promise<boolean> {
  const member = await getWorkspaceMember(userId, workspaceId)
  return member?.role === 'admin' || member?.role === 'org:admin'
}

/**
 * Validate workspace access and throw error if denied
 *
 * Convenience function that checks workspace membership and throws
 * an error if the user doesn't have access. Useful for protecting
 * API routes.
 *
 * @param {string} userId - The user ID
 * @param {string} workspaceId - The workspace (organization) ID
 * @throws {Error} If user is not a workspace member
 *
 * @example
 * ```typescript
 * await validateWorkspaceAccess(userId, workspaceId)
 * // Continues only if user has access, otherwise throws error
 * ```
 */
export async function validateWorkspaceAccess(
  userId: string,
  workspaceId: string
): Promise<void> {
  const isMember = await isWorkspaceMember(userId, workspaceId)

  if (!isMember) {
    throw new Error(
      `Access denied: User ${userId} is not a member of workspace ${workspaceId}`
    )
  }
}

/**
 * Get all workspaces for a user
 *
 * Fetches all workspaces (organizations) that the user is a member of.
 * Returns an empty array if the user has no workspaces.
 *
 * @param {string} userId - The user ID
 * @returns {Promise<WorkspaceContext[]>} List of workspaces
 *
 * @example
 * ```typescript
 * const workspaces = await getUserWorkspaces(userId)
 * console.log(`User has ${workspaces.length} workspaces`)
 * ```
 */
export async function getUserWorkspaces(
  userId: string
): Promise<WorkspaceContext[]> {
  try {
    // Get organization memberships for the user
    const memberships =
      await clerkClient.users.getOrganizationMembershipList({
        userId,
      })

    // Map to workspace context objects
    return memberships.map((membership) => ({
      id: membership.organization.id,
      name: membership.organization.name,
      slug: membership.organization.slug,
      imageUrl: membership.organization.imageUrl,
      membersCount: membership.organization.membersCount || 0,
      createdAt: new Date(membership.createdAt),
      updatedAt: new Date(membership.createdAt), // Clerk doesn't provide updatedAt for memberships
    }))
  } catch (error) {
    // Log error but don't expose internal details
    if (error instanceof Error) {
      // eslint-disable-next-line no-console
      console.error('Failed to get user workspaces:', error.message)
    }
    return []
  }
}
