/**
 * API Middleware for Authentication and Request Context
 *
 * Provides middleware utilities for Next.js API routes to verify authentication
 * and extract workspace context using Clerk authentication.
 *
 * @example
 * ```typescript
 * import { withAuth } from '@/lib/api-middleware'
 *
 * export async function GET(request: NextRequest) {
 *   return withAuth(request, async (context) => {
 *     // Access authenticated user and workspace
 *     const { userId, workspaceId, user } = context
 *
 *     // Your API logic here
 *     return NextResponse.json({ data: 'success' })
 *   })
 * }
 * ```
 */

import { auth, clerkClient } from '@clerk/nextjs'
import { NextRequest, NextResponse } from 'next/server'

/**
 * Authentication context provided to API route handlers
 */
export interface ApiAuthContext {
  /**
   * Authenticated user ID from Clerk
   */
  userId: string

  /**
   * Current workspace (organization) ID from Clerk
   * May be null if user has no active workspace
   */
  workspaceId: string | null

  /**
   * Session ID from Clerk
   */
  sessionId: string | null

  /**
   * Full user object from Clerk (optional, loaded if needed)
   */
  user?: {
    id: string
    firstName: string | null
    lastName: string | null
    emailAddresses: Array<{ emailAddress: string; id: string }>
    imageUrl: string
  }
}

/**
 * Options for authentication middleware
 */
export interface AuthMiddlewareOptions {
  /**
   * Whether to require workspace (organization) membership
   * @default true
   */
  requireWorkspace?: boolean

  /**
   * Whether to load full user object (requires additional API call)
   * @default false
   */
  loadUser?: boolean

  /**
   * Custom unauthorized response handler
   */
  onUnauthorized?: () => NextResponse
}

/**
 * Verifies authentication and extracts user/workspace context
 *
 * This function checks Clerk authentication and returns the auth context
 * including userId and workspaceId (orgId). Throws an error if not authenticated.
 *
 * @returns {Promise<ApiAuthContext>} Authentication context
 * @throws {Error} If user is not authenticated
 *
 * @example
 * ```typescript
 * const context = await verifyAuth()
 * console.log(context.userId, context.workspaceId)
 * ```
 */
export async function verifyAuth(
  options: AuthMiddlewareOptions = {}
): Promise<ApiAuthContext> {
  const { requireWorkspace = true, loadUser = false } = options

  // Get authentication from Clerk
  const { userId, orgId, sessionId } = auth()

  // Check if user is authenticated
  if (!userId) {
    throw new Error('Unauthorized: No user ID found')
  }

  // Check workspace requirement
  if (requireWorkspace && !orgId) {
    throw new Error('Unauthorized: No workspace (organization) selected')
  }

  // Build base context
  const context: ApiAuthContext = {
    userId,
    workspaceId: orgId || null,
    sessionId,
  }

  // Load full user object if requested
  if (loadUser) {
    try {
      const clerkUser = await clerkClient.users.getUser(userId)
      context.user = {
        id: clerkUser.id,
        firstName: clerkUser.firstName,
        lastName: clerkUser.lastName,
        emailAddresses: clerkUser.emailAddresses,
        imageUrl: clerkUser.imageUrl,
      }
    } catch (error) {
      // Log error but don't fail the request
      if (error instanceof Error) {
        // eslint-disable-next-line no-console
        console.error('Failed to load user:', error.message)
      }
    }
  }

  return context
}

/**
 * Higher-order function that wraps API route handlers with authentication
 *
 * Automatically verifies authentication and provides auth context to the handler.
 * Returns 401 Unauthorized if authentication fails.
 *
 * @param {NextRequest} request - Next.js request object
 * @param {Function} handler - API route handler that receives auth context
 * @param {AuthMiddlewareOptions} options - Authentication options
 * @returns {Promise<NextResponse>} API response
 *
 * @example
 * ```typescript
 * export async function GET(request: NextRequest) {
 *   return withAuth(request, async (context) => {
 *     // context.userId and context.workspaceId are available
 *     return NextResponse.json({ userId: context.userId })
 *   })
 * }
 * ```
 */
export async function withAuth(
  request: NextRequest,
  handler: (context: ApiAuthContext) => Promise<NextResponse>,
  options: AuthMiddlewareOptions = {}
): Promise<NextResponse> {
  try {
    // Verify authentication and get context
    const context = await verifyAuth(options)

    // Call the handler with auth context
    return await handler(context)
  } catch (error) {
    // Handle custom unauthorized response
    if (options.onUnauthorized) {
      return options.onUnauthorized()
    }

    // Default unauthorized response
    const message =
      error instanceof Error ? error.message : 'Authentication required'

    return NextResponse.json(
      {
        error: 'Unauthorized',
        message,
        timestamp: new Date().toISOString(),
      },
      { status: 401 }
    )
  }
}

/**
 * Middleware wrapper for API routes that don't require workspace
 *
 * Useful for routes like user profile or global settings that don't
 * depend on workspace context.
 *
 * @param {NextRequest} request - Next.js request object
 * @param {Function} handler - API route handler
 * @returns {Promise<NextResponse>} API response
 *
 * @example
 * ```typescript
 * export async function GET(request: NextRequest) {
 *   return withAuthNoWorkspace(request, async (context) => {
 *     // context.userId is available, workspaceId may be null
 *     return NextResponse.json({ userId: context.userId })
 *   })
 * }
 * ```
 */
export async function withAuthNoWorkspace(
  request: NextRequest,
  handler: (context: ApiAuthContext) => Promise<NextResponse>
): Promise<NextResponse> {
  return withAuth(request, handler, { requireWorkspace: false })
}

/**
 * Extract workspace ID from request
 *
 * Convenience function to get the current workspace ID without full auth check.
 * Returns null if no workspace is active.
 *
 * @returns {string | null} Workspace (organization) ID or null
 *
 * @example
 * ```typescript
 * const workspaceId = getWorkspaceId()
 * if (workspaceId) {
 *   // User has active workspace
 * }
 * ```
 */
export function getWorkspaceId(): string | null {
  const { orgId } = auth()
  return orgId || null
}

/**
 * Extract user ID from request
 *
 * Convenience function to get the current user ID without full auth check.
 * Returns null if user is not authenticated.
 *
 * @returns {string | null} User ID or null
 *
 * @example
 * ```typescript
 * const userId = getUserId()
 * if (userId) {
 *   // User is authenticated
 * }
 * ```
 */
export function getUserId(): string | null {
  const { userId } = auth()
  return userId || null
}
