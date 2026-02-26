# Authentication Flow Verification Guide

This guide provides step-by-step instructions for testing the complete authentication flow end-to-end.

## Overview

This verification covers the full user authentication journey from sign-up to sign-out, including workspace management and protected route access.

## Test Flow Outline

1. **Sign up new user** - Create a new account
2. **Create/join workspace** - Set up multi-tenant workspace
3. **Access protected dashboard** - Verify authentication gates work
4. **Switch workspaces** - Test multi-workspace switching
5. **Sign out** - Complete the authentication cycle

---

## Prerequisites

### 1. Start Development Server

```bash
cd dashboard
npm install
npm run dev
```

The development server should start at `http://localhost:3000`

### 2. Configure Clerk Environment Variables

Ensure `.env.local` exists with valid Clerk API keys:

```env
# Clerk Authentication
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_SECRET_KEY=sk_test_...

# Clerk URLs
NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in
NEXT_PUBLIC_CLERK_SIGN_UP_URL=/sign-up
NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL=/
NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL=/

# Organization Settings
NEXT_PUBLIC_CLERK_ORGANIZATION_ENABLED=true
NEXT_PUBLIC_CLERK_ORGANIZATION_REQUIRED=true
```

### 3. Verify Middleware Configuration

Check that `src/middleware.ts` is configured correctly:
- Authentication middleware is active
- Public routes exclude `/sign-in` and `/sign-up`
- Organization requirement is enforced

---

## Test 1: Sign Up New User

### Steps

1. **Navigate to Sign-Up Page**
   - Open browser to: `http://localhost:3000/sign-up`
   - Verify sign-up page loads without errors
   - Check browser console for errors (should be none)

2. **Complete Sign-Up Form**
   - Enter email address (use a test email or temp email service)
   - Enter password (minimum 8 characters)
   - Optional: Enter first name and last name
   - Click "Sign up" button

3. **Email Verification**
   - Check email inbox for verification code
   - Enter verification code in the form
   - Or click verification link if using email link verification

4. **Verify Account Created**
   - After verification, user should be signed in
   - Check that authentication succeeded

### Expected Results

- ✅ Sign-up page renders with Clerk UI components
- ✅ Form validation works (invalid email, weak password, etc.)
- ✅ Verification email sent successfully
- ✅ Account created after email verification
- ✅ User automatically signed in after verification
- ✅ No console errors during the process
- ✅ Redirected according to middleware rules

### Common Issues

- **Email not received**: Check spam folder, verify Clerk email settings
- **Invalid email format**: Clerk validates email format
- **Password too weak**: Must meet Clerk's password requirements
- **Console errors**: Check Clerk API keys are correct

---

## Test 2: Create/Join Workspace

After signing up, users must create or join a workspace (Clerk Organization).

### Steps

#### Option A: Create New Workspace

1. **Workspace Creation Prompt**
   - After sign-up, middleware should redirect to workspace creation
   - Clerk's organization creation modal should appear
   - Or navigate to Clerk's organization creation UI

2. **Fill Workspace Details**
   - Enter workspace name (e.g., "Test Marketing Team")
   - Optional: Upload workspace logo/avatar
   - Click "Create workspace" or "Create organization"

3. **Verify Workspace Created**
   - Workspace should be created successfully
   - User should be automatically added as admin
   - Redirected to dashboard with workspace context

#### Option B: Join Existing Workspace

1. **Receive Invitation**
   - Another workspace admin sends invitation
   - Check email for invitation link

2. **Accept Invitation**
   - Click invitation link
   - Sign in if not already signed in
   - Accept the workspace invitation

3. **Verify Workspace Joined**
   - Workspace appears in workspace selector
   - User has member role (not admin unless promoted)

### Expected Results

- ✅ Workspace creation UI appears after sign-up
- ✅ Workspace name is required and validated
- ✅ Workspace created successfully
- ✅ User is added as workspace admin (for created workspaces)
- ✅ User is added as workspace member (for joined workspaces)
- ✅ Middleware allows access to dashboard after workspace selection
- ✅ WorkspaceContext provides workspace data to components

### Common Issues

- **Can't create workspace**: Check Clerk organization settings are enabled
- **Middleware redirect loop**: Verify NEXT_PUBLIC_CLERK_ORGANIZATION_REQUIRED is set
- **Workspace not appearing**: Check user is authenticated and organization membership exists

---

## Test 3: Access Protected Dashboard

After workspace creation/joining, verify protected routes work correctly.

### Steps

1. **Automatic Redirect to Dashboard**
   - After workspace setup, should redirect to `/` (dashboard home)
   - Dashboard layout should render with sidebar and header
   - Workspace selector should show current workspace

2. **Navigate to Protected Routes**
   - Click "Dashboard" in sidebar → Navigate to `/`
   - Click "System Health" in sidebar → Navigate to `/health`
   - Click "Configuration" in sidebar → Navigate to `/config`
   - Click "Analytics" in sidebar → Navigate to `/analytics`

3. **Verify Route Protection**
   - All routes should be accessible with authentication
   - Sidebar should highlight active route
   - Content should load without errors

4. **Test Direct URL Access**
   - Open new tab while signed in
   - Navigate directly to: `http://localhost:3000/health`
   - Should load immediately without redirect
   - Workspace context should be available

5. **Test Unauthenticated Access**
   - Open incognito/private browser window
   - Navigate to: `http://localhost:3000/`
   - Should redirect to `/sign-in` with `redirect_url` parameter
   - After signing in, should redirect back to original URL

### Expected Results

- ✅ Dashboard loads with full layout (sidebar, header, main content)
- ✅ All navigation routes are accessible
- ✅ Active route highlighted in sidebar
- ✅ Workspace selector shows current workspace
- ✅ User menu (UserButton) shows user profile
- ✅ Unauthenticated access redirects to sign-in
- ✅ After sign-in, redirects back to original protected route
- ✅ No console errors
- ✅ Workspace context available in all protected routes

### Common Issues

- **Infinite redirect loop**: Check middleware configuration and Clerk URLs
- **No workspace context**: Verify organization is selected and middleware afterAuth logic
- **Routes not loading**: Check Next.js routing and file structure
- **Console errors**: Verify all Clerk environment variables are set

---

## Test 4: Switch Workspaces

Test multi-workspace functionality by creating/joining multiple workspaces and switching between them.

### Steps

#### Setup: Create Second Workspace

1. **Open Workspace Selector**
   - Click workspace selector in header (displays current workspace name)
   - Dropdown menu should appear

2. **Create New Workspace**
   - Click "Create workspace" or equivalent option
   - Enter new workspace name (e.g., "Second Marketing Team")
   - Click "Create"

3. **Verify Second Workspace**
   - New workspace should appear in workspace list
   - Should automatically switch to new workspace
   - Dashboard should update with new workspace context

#### Test: Switch Between Workspaces

1. **Open Workspace Selector**
   - Click workspace selector dropdown
   - Verify both workspaces are listed

2. **Switch to First Workspace**
   - Click first workspace in list
   - Active workspace indicator (checkmark) should update
   - Page should reload or update with new context

3. **Verify Context Changed**
   - Workspace selector shows first workspace name
   - Member count updates if different
   - Dashboard data should reflect first workspace (when backend integration is complete)

4. **Switch to Second Workspace**
   - Open workspace selector again
   - Click second workspace
   - Verify context switches back

5. **Test Workspace Switching Across Routes**
   - Navigate to `/health` page
   - Switch workspaces using selector
   - Verify workspace context updates on health page
   - Navigate to `/config` page
   - Switch workspaces again
   - Verify workspace context updates on config page

### Expected Results

- ✅ Workspace selector dropdown displays all user's workspaces
- ✅ Can create new workspaces from selector
- ✅ Active workspace indicated with checkmark
- ✅ Switching workspaces updates context immediately
- ✅ Workspace name updates in selector
- ✅ Member count updates in selector
- ✅ Workspace avatar/image displays correctly
- ✅ Workspace switching works on all routes
- ✅ No page errors during workspace switching
- ✅ WorkspaceContext hook provides correct workspace data after switch

### Common Issues

- **Workspaces not appearing**: Check user's organization memberships in Clerk
- **Can't switch workspaces**: Verify WorkspaceContext and useOrganization() hook
- **Context not updating**: Check setActive() is called correctly
- **Page reload on switch**: Expected behavior; Clerk updates context

---

## Test 5: Sign Out

Complete the authentication cycle by signing out.

### Steps

1. **Open User Menu**
   - Click UserButton component in header (top-right)
   - Dropdown menu should appear
   - User profile information should be visible

2. **Click Sign Out**
   - Click "Sign out" button in UserButton dropdown
   - Clerk should process sign-out request

3. **Verify Sign-Out Redirect**
   - After sign-out, should redirect to `/sign-in`
   - User should no longer be authenticated
   - Session should be cleared

4. **Verify Protected Routes Blocked**
   - Try to navigate to: `http://localhost:3000/`
   - Should redirect to `/sign-in`
   - Try to navigate to: `http://localhost:3000/health`
   - Should redirect to `/sign-in` with redirect_url parameter

5. **Verify Clean State**
   - Open browser DevTools → Application → Cookies
   - Clerk session cookies should be removed
   - No authentication state in localStorage
   - Workspace context cleared

### Expected Results

- ✅ UserButton displays user menu with sign-out option
- ✅ Sign-out button works correctly
- ✅ Redirected to `/sign-in` after sign-out
- ✅ Session cleared (no authentication cookies)
- ✅ Protected routes redirect to sign-in
- ✅ No console errors during sign-out
- ✅ Can sign back in immediately after sign-out

### Common Issues

- **Sign-out doesn't work**: Check Clerk configuration and network requests
- **Still authenticated after sign-out**: Clear browser cache and cookies
- **Redirect issues**: Verify Clerk sign-in URL configuration

---

## Test 6: Re-Sign In (Bonus)

Verify users can sign back in after signing out.

### Steps

1. **Navigate to Sign-In Page**
   - After sign-out, should be on `/sign-in`
   - Or manually navigate to: `http://localhost:3000/sign-in`

2. **Enter Credentials**
   - Enter email address used during sign-up
   - Enter password
   - Click "Sign in"

3. **Verify Workspace Selection**
   - If user has workspaces, may need to select workspace
   - Or automatically select last active workspace

4. **Access Dashboard**
   - Should redirect to dashboard home `/`
   - Full authentication and workspace context restored
   - All protected routes accessible again

### Expected Results

- ✅ Sign-in form accepts correct credentials
- ✅ Invalid credentials show error message
- ✅ After sign-in, workspace context restored
- ✅ Dashboard accessible after sign-in
- ✅ User can access all previously created workspaces

---

## Mobile Responsiveness (Bonus Test)

Test authentication flow on mobile viewport.

### Steps

1. **Open Browser DevTools**
   - Press F12 or right-click → Inspect
   - Click device toolbar icon (mobile emulation)
   - Select device: iPhone 12 Pro (390x844)

2. **Test Sign-Up Flow**
   - Navigate to `/sign-up`
   - Verify Clerk UI is responsive
   - Complete sign-up on mobile viewport

3. **Test Workspace Selector**
   - Open workspace selector on mobile
   - Should display properly on small screen
   - Test workspace switching

4. **Test Navigation**
   - Click mobile menu toggle (hamburger icon)
   - Sidebar should slide in from left
   - Navigate to different routes
   - Sidebar should close after navigation

5. **Test Sign-Out**
   - Open UserButton on mobile
   - Verify dropdown menu is accessible
   - Sign out successfully

### Expected Results

- ✅ Sign-up/sign-in forms responsive on mobile
- ✅ Workspace selector accessible on mobile
- ✅ Mobile sidebar navigation works correctly
- ✅ All touch interactions work smoothly
- ✅ No horizontal scrolling issues
- ✅ UserButton menu accessible on mobile

---

## Acceptance Checklist

Use this checklist to verify all authentication flow requirements are met:

### Sign Up
- [ ] Sign-up page renders correctly at `/sign-up`
- [ ] Email validation works
- [ ] Password validation works
- [ ] Verification email sent
- [ ] Account created after verification
- [ ] User automatically signed in after sign-up
- [ ] No console errors

### Workspace Management
- [ ] Workspace creation prompt appears after sign-up
- [ ] Can create new workspace successfully
- [ ] User is workspace admin for created workspaces
- [ ] Workspace selector displays all user workspaces
- [ ] Can switch between workspaces
- [ ] Workspace context updates after switching
- [ ] Member count displays correctly

### Protected Routes
- [ ] Unauthenticated users redirected to `/sign-in`
- [ ] Authenticated users can access all protected routes
- [ ] Users without workspace redirected to workspace selection
- [ ] Redirect_url parameter works correctly
- [ ] After sign-in, redirects to original protected route
- [ ] Sidebar navigation works on all routes
- [ ] Active route highlighted in sidebar

### Sign Out
- [ ] UserButton displays user menu
- [ ] Sign-out button visible in menu
- [ ] Sign-out successfully clears session
- [ ] Redirected to `/sign-in` after sign-out
- [ ] Protected routes blocked after sign-out
- [ ] Session cookies cleared

### Multi-Workspace
- [ ] Can create multiple workspaces
- [ ] Can join existing workspaces via invitation
- [ ] Workspace selector lists all workspaces
- [ ] Switching workspaces updates context
- [ ] Active workspace indicated with checkmark
- [ ] Workspace context persists across routes

### Re-Sign In
- [ ] Can sign back in after sign-out
- [ ] Workspace context restored after sign-in
- [ ] Dashboard accessible after sign-in
- [ ] All workspaces still accessible

### Mobile Responsiveness
- [ ] Sign-up/sign-in responsive on mobile (375px)
- [ ] Workspace selector accessible on mobile
- [ ] Mobile sidebar navigation works
- [ ] UserButton menu accessible on mobile
- [ ] No layout issues on tablet (768px)

### Browser Console
- [ ] No console errors during sign-up
- [ ] No console errors during workspace creation
- [ ] No console errors during navigation
- [ ] No console errors during workspace switching
- [ ] No console errors during sign-out
- [ ] No console warnings (except Clerk development mode)

---

## Common Issues and Solutions

### Issue: Infinite Redirect Loop

**Symptoms:** Page keeps redirecting between `/sign-in` and `/`

**Solutions:**
1. Check middleware.ts afterAuth callback logic
2. Verify Clerk environment variables are set correctly
3. Ensure organization is selected after sign-in
4. Check NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL is set to `/`

### Issue: Workspace Not Required

**Symptoms:** Can access dashboard without selecting workspace

**Solutions:**
1. Set NEXT_PUBLIC_CLERK_ORGANIZATION_REQUIRED=true
2. Update middleware.ts to check auth.orgId
3. Verify afterAuth callback enforces organization requirement

### Issue: Sign-Out Not Working

**Symptoms:** User still authenticated after clicking sign-out

**Solutions:**
1. Check Clerk's UserButton is configured correctly
2. Clear browser cache and cookies
3. Verify Clerk secret key is correct
4. Check network tab for sign-out request errors

### Issue: Workspace Context Missing

**Symptoms:** useWorkspace() returns null or undefined

**Solutions:**
1. Ensure WorkspaceProvider wraps entire app
2. Verify user has selected a workspace
3. Check useOrganization() returns valid data
4. Confirm Clerk organization settings are enabled

### Issue: Can't Create Workspace

**Symptoms:** Workspace creation fails or doesn't show UI

**Solutions:**
1. Enable organizations in Clerk dashboard
2. Verify NEXT_PUBLIC_CLERK_ORGANIZATION_ENABLED=true
3. Check user has permission to create organizations
4. Review Clerk console for organization settings

---

## Performance Expectations

- Sign-up process: < 3 seconds (excluding email verification)
- Workspace creation: < 2 seconds
- Workspace switching: < 1 second
- Sign-out: < 1 second
- Protected route load: < 2 seconds (after authentication)
- No memory leaks during authentication flow
- No excessive re-renders during workspace switching

---

## Security Verification

### Verify Protected Route Security

1. **Test without authentication:**
   ```bash
   curl http://localhost:3000/
   ```
   Should return sign-in redirect HTML

2. **Test API routes without authentication:**
   ```bash
   curl http://localhost:3000/api/health
   ```
   Should return 401 Unauthorized (once middleware is integrated)

3. **Test with invalid session:**
   - Manipulate session cookie in browser DevTools
   - Try to access protected route
   - Should redirect to sign-in

### Verify Workspace Isolation

1. Create two workspaces
2. Add data specific to workspace A (future: API keys, config)
3. Switch to workspace B
4. Verify workspace A's data is not accessible
5. Switch back to workspace A
6. Verify data is still there

---

## Notes

- All authentication handled by Clerk
- Workspaces use Clerk Organizations (orgId)
- Middleware enforces authentication and workspace requirement
- WorkspaceContext provides workspace data to components
- UserButton component handles user menu and sign-out
- Session persists across browser refreshes
- Multiple workspaces support multi-tenant architecture

---

## Next Steps After Verification

Once this verification is complete and all tests pass:

1. Mark subtask-8-2 as completed in implementation_plan.json
2. Update build-progress.txt with verification results
3. Commit changes with message: "auto-claude: subtask-8-2 - Test complete authentication flow"
4. Proceed to subtask-8-3: Test configuration management end-to-end
