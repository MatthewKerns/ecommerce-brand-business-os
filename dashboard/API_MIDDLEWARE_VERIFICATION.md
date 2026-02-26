# API Middleware Verification Guide

This guide explains how to verify the API authentication middleware and workspace resolver.

## Created Files

1. **`src/lib/api-middleware.ts`** - Authentication middleware for API routes
2. **`src/lib/workspace-resolver.ts`** - Workspace context utilities

## Features Implemented

### API Middleware (`api-middleware.ts`)

- ✅ `verifyAuth()` - Verifies Clerk authentication and extracts user/workspace context
- ✅ `withAuth()` - Higher-order function that wraps API routes with authentication
- ✅ `withAuthNoWorkspace()` - Wrapper for routes that don't require workspace
- ✅ `getWorkspaceId()` - Convenience function to extract workspace ID
- ✅ `getUserId()` - Convenience function to extract user ID
- ✅ Returns 401 Unauthorized if authentication fails
- ✅ Supports optional workspace requirement
- ✅ Supports optional user object loading

### Workspace Resolver (`workspace-resolver.ts`)

- ✅ `getWorkspaceContext()` - Fetches workspace details from Clerk
- ✅ `isWorkspaceMember()` - Checks if user is a member of a workspace
- ✅ `getWorkspaceMember()` - Gets member details and role
- ✅ `isWorkspaceAdmin()` - Checks if user has admin role
- ✅ `validateWorkspaceAccess()` - Validates and throws error if access denied
- ✅ `getUserWorkspaces()` - Lists all workspaces for a user

## Manual Verification Steps

### Prerequisites

1. Start the development server:
   ```bash
   cd dashboard
   npm install
   npm run dev
   ```

2. Ensure Clerk environment variables are configured in `.env.local`:
   ```
   NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
   CLERK_SECRET_KEY=sk_test_...
   ```

### Test 1: Unauthenticated Request Returns 401

Create a test API route at `src/app/api/test-auth/route.ts`:

```typescript
import { NextRequest } from 'next/server'
import { withAuth } from '@/lib/api-middleware'

export async function GET(request: NextRequest) {
  return withAuth(request, async (context) => {
    return Response.json({
      success: true,
      userId: context.userId,
      workspaceId: context.workspaceId,
    })
  })
}
```

Test unauthenticated request:
```bash
curl http://localhost:3000/api/test-auth
```

**Expected Result:**
```json
{
  "error": "Unauthorized",
  "message": "Unauthorized: No user ID found",
  "timestamp": "2024-01-01T00:00:00.000Z"
}
```
Status code: **401**

### Test 2: Authenticated Request Includes Workspace Context

1. Sign in to the dashboard at http://localhost:3000
2. Open browser console and run:
   ```javascript
   fetch('/api/test-auth').then(r => r.json()).then(console.log)
   ```

**Expected Result:**
```json
{
  "success": true,
  "userId": "user_abc123",
  "workspaceId": "org_xyz789"
}
```
Status code: **200**

### Test 3: Request Without Workspace Returns 401

Modify the test route to require workspace:

```typescript
export async function GET(request: NextRequest) {
  // requireWorkspace: true is the default
  return withAuth(request, async (context) => {
    return Response.json({ workspaceId: context.workspaceId })
  })
}
```

Sign in but don't select a workspace, then test the endpoint.

**Expected Result:**
```json
{
  "error": "Unauthorized",
  "message": "Unauthorized: No workspace (organization) selected",
  "timestamp": "2024-01-01T00:00:00.000Z"
}
```
Status code: **401**

### Test 4: Workspace Resolver Functions

Create a test route at `src/app/api/test-workspace/route.ts`:

```typescript
import { NextRequest, NextResponse } from 'next/server'
import { withAuth } from '@/lib/api-middleware'
import {
  getWorkspaceContext,
  isWorkspaceMember,
  isWorkspaceAdmin,
  getUserWorkspaces,
} from '@/lib/workspace-resolver'

export async function GET(request: NextRequest) {
  return withAuth(request, async (context) => {
    const { userId, workspaceId } = context

    if (!workspaceId) {
      return NextResponse.json({ error: 'No workspace' }, { status: 400 })
    }

    // Test all workspace resolver functions
    const [workspace, isMember, isAdmin, userWorkspaces] = await Promise.all([
      getWorkspaceContext(workspaceId),
      isWorkspaceMember(userId, workspaceId),
      isWorkspaceAdmin(userId, workspaceId),
      getUserWorkspaces(userId),
    ])

    return NextResponse.json({
      workspace,
      isMember,
      isAdmin,
      userWorkspacesCount: userWorkspaces.length,
    })
  })
}
```

Test while signed in with a workspace selected:
```bash
# In browser console (while authenticated)
fetch('/api/test-workspace').then(r => r.json()).then(console.log)
```

**Expected Result:**
```json
{
  "workspace": {
    "id": "org_xyz789",
    "name": "My Workspace",
    "slug": "my-workspace",
    "imageUrl": "https://...",
    "membersCount": 1,
    "createdAt": "2024-01-01T00:00:00.000Z",
    "updatedAt": "2024-01-01T00:00:00.000Z"
  },
  "isMember": true,
  "isAdmin": true,
  "userWorkspacesCount": 1
}
```

### Test 5: withAuthNoWorkspace Allows Requests Without Workspace

Create a route that doesn't require workspace:

```typescript
import { NextRequest, NextResponse } from 'next/server'
import { withAuthNoWorkspace } from '@/lib/api-middleware'

export async function GET(request: NextRequest) {
  return withAuthNoWorkspace(request, async (context) => {
    return NextResponse.json({
      userId: context.userId,
      hasWorkspace: context.workspaceId !== null,
    })
  })
}
```

Test while signed in without selecting a workspace:

**Expected Result:**
```json
{
  "userId": "user_abc123",
  "hasWorkspace": false
}
```
Status code: **200** (even without workspace)

## Integration Example

Here's how to use the middleware in existing API routes:

### Example: Update Health API to Use Middleware

```typescript
// src/app/api/health/route.ts
import { NextRequest } from 'next/server'
import { withAuth } from '@/lib/api-middleware'
import { checkSystemHealth } from '@/lib/health-checker'

export async function GET(request: NextRequest) {
  // Protect with authentication
  return withAuth(request, async (context) => {
    const health = await checkSystemHealth()

    // Optionally filter data by workspace
    // const workspaceHealth = filterByWorkspace(health, context.workspaceId)

    return Response.json(health)
  })
}
```

### Example: Workspace-Scoped Metrics

```typescript
// src/app/api/metrics/route.ts
import { NextRequest, NextResponse } from 'next/server'
import { withAuth } from '@/lib/api-middleware'
import { getWorkspaceContext } from '@/lib/workspace-resolver'
import { fetchAllMetrics } from '@/lib/metrics-fetcher'

export async function GET(request: NextRequest) {
  return withAuth(request, async (context) => {
    // Get workspace details
    const workspace = await getWorkspaceContext(context.workspaceId!)

    // Fetch metrics for this workspace
    const metrics = await fetchAllMetrics()

    return NextResponse.json({
      workspace: workspace.name,
      metrics,
    })
  })
}
```

## Checklist

- [ ] Unauthenticated requests return 401 status code
- [ ] Authenticated requests receive user and workspace context
- [ ] Requests without workspace return 401 when workspace is required
- [ ] `withAuthNoWorkspace` allows requests without workspace
- [ ] `getWorkspaceContext()` returns correct workspace details
- [ ] `isWorkspaceMember()` correctly validates membership
- [ ] `isWorkspaceAdmin()` correctly validates admin role
- [ ] `getUserWorkspaces()` returns all user's workspaces
- [ ] Error messages are user-friendly and don't expose internal details
- [ ] TypeScript types are properly exported and documented

## Notes

- The middleware uses Clerk's `auth()` function from `@clerk/nextjs`
- Workspace ID is the Clerk organization ID (`orgId`)
- All functions include comprehensive JSDoc documentation
- Error handling follows established patterns from other API routes
- Functions use `clerkClient` for server-side Clerk API calls
