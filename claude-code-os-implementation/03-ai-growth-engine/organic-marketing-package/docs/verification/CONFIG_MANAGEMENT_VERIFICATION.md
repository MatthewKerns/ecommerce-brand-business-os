# Configuration Management - End-to-End Verification Guide

This guide provides step-by-step instructions for testing the configuration management functionality end-to-end. Follow these procedures to verify that all configuration features work correctly.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Test Flow 1: Navigate to Config Page](#test-flow-1-navigate-to-config-page)
3. [Test Flow 2: API Key Management](#test-flow-2-api-key-management)
4. [Test Flow 3: Update Service Settings](#test-flow-3-update-service-settings)
5. [Test Flow 4: Verify Changes Persist](#test-flow-4-verify-changes-persist)
6. [Test Flow 5: Test Key Masking and Copy](#test-flow-5-test-key-masking-and-copy)
7. [Test Flow 6: Workspace Settings](#test-flow-6-workspace-settings)
8. [Security Verification](#security-verification)
9. [Performance Expectations](#performance-expectations)
10. [Common Issues & Troubleshooting](#common-issues--troubleshooting)
11. [QA Acceptance Checklist](#qa-acceptance-checklist)

---

## Prerequisites

Before starting verification, ensure the following:

### 1. Development Server Running

```bash
cd dashboard
npm install
npm run dev
```

Verify the server is running at: **http://localhost:3000**

### 2. Clerk Environment Variables Configured

Ensure `.env.local` contains:

```env
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_SECRET_KEY=sk_test_...

# URLs
NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in
NEXT_PUBLIC_CLERK_SIGN_UP_URL=/sign-up
NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL=/
NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL=/

# Multi-tenancy
NEXT_PUBLIC_CLERK_ORGANIZATION_PROFILE_URL=/org-profile
NEXT_PUBLIC_CLERK_CREATE_ORGANIZATION_URL=/create-org
```

### 3. Authenticated User with Workspace

- User must be signed in
- User must have an active workspace (organization)
- User should have admin role for full testing

### 4. Browser Developer Tools Open

- Open DevTools (F12 or Cmd+Opt+I)
- Go to Console tab to monitor for errors
- Go to Network tab to monitor API calls

---

## Test Flow 1: Navigate to Config Page

### Objective
Verify that users can access the configuration page and see the tabbed interface.

### Steps

1. **Navigate to Configuration Page**
   - From the dashboard, click "Configuration" in the sidebar
   - URL should change to: `http://localhost:3000/config`

2. **Verify Page Loads**
   - ✅ Page renders without errors
   - ✅ Page title "Configuration" visible in header area
   - ✅ Tabbed interface displays with 3 tabs:
     - API Keys
     - Services
     - Workspace

3. **Verify Default Tab**
   - ✅ "API Keys" tab is active by default
   - ✅ Blue underline indicates active tab
   - ✅ API key list is visible

4. **Test Tab Navigation**
   - Click "Services" tab
     - ✅ Tab becomes active (blue underline)
     - ✅ Service selector appears with 3 buttons (TikTok, Blog Engine, Email Automation)
     - ✅ Service configuration form displays
   - Click "Workspace" tab
     - ✅ Tab becomes active (blue underline)
     - ✅ Workspace settings form displays
   - Click back to "API Keys" tab
     - ✅ Tab becomes active
     - ✅ API key list displays

5. **Verify Responsive Design**
   - Test on mobile viewport (375px width)
     - ✅ Tabs stack or scroll horizontally
     - ✅ Content is readable
     - ✅ No horizontal overflow
   - Test on tablet viewport (768px width)
     - ✅ Tabs display properly
     - ✅ Forms are usable
   - Test on desktop viewport (1920px width)
     - ✅ Layout uses available space effectively

### Expected Results

- ✅ Configuration page accessible via sidebar navigation
- ✅ URL routing works correctly (`/config`)
- ✅ Tabbed interface displays all 3 tabs
- ✅ Default "API Keys" tab is active on load
- ✅ Tab switching works smoothly with visual feedback
- ✅ No console errors
- ✅ Responsive design works on all screen sizes

### Common Issues

- **Tab not switching**: Check React state management in ConfigurationDashboard
- **404 error**: Verify file exists at `dashboard/src/app/(dashboard)/config/page.tsx`
- **Styling issues**: Check Tailwind CSS classes and cn() utility usage

---

## Test Flow 2: API Key Management

### Objective
Verify API key display, copy, and delete functionality.

### Steps

#### A. View Existing API Keys

1. **Navigate to API Keys Tab**
   - Ensure "API Keys" tab is active
   - ✅ Header shows "API Keys" title
   - ✅ Description text visible: "Manage authentication keys for external services"
   - ✅ "Add API Key" button visible in top-right

2. **Verify Default Keys Display**
   - ✅ 3 default API keys are visible:
     1. **TikTok API Key** (Service: TikTok)
     2. **OpenAI API Key** (Service: AI Agents)
     3. **SendGrid API Key** (Service: Email)

3. **Verify Key Card Information**
   - For each key, verify the following fields:
     - ✅ Key icon with blue background
     - ✅ Key name (e.g., "TikTok API Key")
     - ✅ Service tag (e.g., "TikTok" with colored badge)
     - ✅ Masked value (e.g., "sk-••••••••••••••••")
     - ✅ Created date (e.g., "2024-01-15")
     - ✅ Last used date (e.g., "Last used: 2024-02-20")
     - ✅ Copy button (clipboard icon)
     - ✅ Delete button (trash icon)

#### B. Copy API Key Functionality

1. **Click Copy Button**
   - Click the copy button (clipboard icon) on the first key
   - ✅ Copy icon changes to checkmark (green)
   - ✅ Visual feedback indicates success
   - ✅ Icon returns to clipboard after ~2 seconds

2. **Verify Clipboard Content**
   - Paste into a text editor (Cmd+V or Ctrl+V)
   - ✅ Full unmasked key value is copied
   - ✅ Expected format: `sk-tiktok-api-key-example-12345678`
   - **Note**: In production, this would copy the actual API key value

3. **Test Multiple Keys**
   - Copy the second key (OpenAI)
     - ✅ Copy works independently
     - ✅ Feedback shows on correct button
   - Copy the third key (SendGrid)
     - ✅ Copy functionality consistent

#### C. Delete API Key Functionality

1. **Click Delete Button**
   - Click the delete button (trash icon) on the third key (SendGrid)
   - ✅ Confirmation dialog appears
   - ✅ Dialog shows:
     - Trash icon in header
     - "Delete API Key" title
     - Key name in message: "Are you sure you want to delete SendGrid API Key?"
     - Warning text about breaking services
     - "Cancel" button
     - "Delete Key" button (red)

2. **Cancel Deletion**
   - Click "Cancel" button
   - ✅ Dialog closes
   - ✅ Key remains in list
   - ✅ No changes made

3. **Confirm Deletion**
   - Click delete button again
   - Click "Delete Key" button (red)
   - ✅ Dialog closes
   - ✅ Key is removed from list
   - ✅ Only 2 keys remain (TikTok, OpenAI)
   - ✅ Smooth animation/transition

4. **Verify All Keys Can Be Deleted**
   - Delete remaining keys one by one
   - ✅ Each deletion works correctly
   - ✅ When all keys deleted, empty state appears

#### D. Empty State

1. **After Deleting All Keys**
   - ✅ Empty state displays:
     - Large key icon (gray)
     - "No API Keys" heading
     - Description text
     - "Add Your First API Key" button
   - ✅ Layout is centered
   - ✅ Call-to-action is clear

#### E. Add API Key (Placeholder Test)

1. **Click "Add API Key" Button**
   - Click button in top-right (or in empty state)
   - ✅ Alert dialog appears with message:
     - "Add API Key dialog would open here. This will be implemented in a future subtask."
   - ✅ Click OK to dismiss
   - **Note**: Full implementation with API integration will be added later

#### F. Loading State

1. **Trigger Loading State** (Developer Test)
   - This requires modifying the component temporarily
   - Set `isLoading={true}` prop on ApiKeyManager
   - ✅ Loading skeleton displays:
     - 3 skeleton cards with pulse animation
     - Header skeleton
     - Button skeleton
   - ✅ Smooth animation
   - Set `isLoading={false}` to restore normal view

### Expected Results

- ✅ API keys display with all required information
- ✅ Masked values protect sensitive data (sk-••••••••••••••••)
- ✅ Copy functionality works and copies full value
- ✅ Copy button shows success feedback (green checkmark)
- ✅ Delete confirmation prevents accidental deletion
- ✅ Delete removes key from list
- ✅ Empty state displays when no keys exist
- ✅ Add button shows placeholder alert
- ✅ Loading state shows skeleton screens
- ✅ No console errors during any operation

### Common Issues

- **Copy not working**: Check browser clipboard API permissions
- **Delete confirmation not showing**: Verify state management in ApiKeyItem
- **Keys not updating**: Check local state in ApiKeyManager
- **Layout issues**: Verify Tailwind CSS classes and responsive design

---

## Test Flow 3: Update Service Settings

### Objective
Verify that service configuration forms work correctly for all three services.

### Steps

#### A. Navigate to Services Tab

1. **Click Services Tab**
   - Click "Services" tab in configuration page
   - ✅ Services tab becomes active (blue underline)
   - ✅ Service selector displays with 3 buttons
   - ✅ "TikTok" is selected by default (blue background)
   - ✅ TikTok configuration form displays

#### B. Test TikTok Configuration Form

1. **Verify Form Fields**
   - ✅ Form header shows:
     - Blue settings icon
     - "TikTok API Settings" title
     - Description text
   - ✅ Form contains 5 fields:
     1. **TikTok API Key** (text, required, red asterisk)
     2. **Posting Schedule** (select, required)
     3. **Max Videos Per Day** (number, required)
     4. **Target Video Length** (number, optional)
     5. **Auto-Post** (select, optional)
   - ✅ Each field has helper text explaining purpose
   - ✅ Required fields marked with red asterisk (*)

2. **Test Form Validation - Empty Fields**
   - Leave all fields empty
   - Click "Save Configuration" button
   - ✅ Validation errors appear below required fields:
     - "API Key is required"
     - "Posting schedule is required"
     - "Must be at least 1" (for Max Videos)
   - ✅ Error messages have red text
   - ✅ AlertCircle icon appears with errors
   - ✅ Save did not proceed

3. **Test Form Validation - Field Correction**
   - Enter value in "TikTok API Key" field: `sk-test-tiktok-12345`
   - ✅ Error message for that field disappears
   - ✅ Other errors remain visible
   - Select "Daily" in "Posting Schedule"
   - ✅ Error disappears
   - Enter "3" in "Max Videos Per Day"
   - ✅ Error disappears
   - ✅ All errors cleared

4. **Test Form Validation - Invalid Number**
   - Enter "0" in "Max Videos Per Day"
   - Click "Save Configuration"
   - ✅ Error appears: "Must be at least 1"
   - Change to "3"
   - ✅ Error clears

5. **Fill Complete TikTok Form**
   - Enter the following values:
     - **TikTok API Key**: `sk-test-tiktok-api-key-123456`
     - **Posting Schedule**: Select "Daily"
     - **Max Videos Per Day**: `3`
     - **Target Video Length**: `30`
     - **Auto-Post**: Select "Enabled"
   - ✅ All fields filled correctly
   - ✅ No validation errors

6. **Save TikTok Configuration**
   - Click "Save Configuration" button
   - ✅ Button shows loading state:
     - Spinner icon appears
     - Text changes to "Saving..."
     - Button is disabled (gray background)
   - After ~1 second:
     - ✅ Loading state ends
     - ✅ Success message appears (green background):
       - Green checkmark icon
       - "Configuration saved successfully!"
     - ✅ Success message auto-dismisses after 3 seconds
   - ✅ Button returns to normal state

7. **Monitor Network Activity**
   - Open DevTools Network tab
   - Save configuration again
   - ✅ POST request to `/api/config` visible
   - ✅ Request body contains service and settings
   - ✅ Response status 200
   - **Note**: Currently saves to in-memory storage (Map)

#### C. Test Blog Configuration Form

1. **Switch to Blog Service**
   - Click "Blog Engine" button in service selector
   - ✅ Button becomes active (blue background)
   - ✅ TikTok button becomes inactive (gray)
   - ✅ Form changes to Blog configuration

2. **Verify Blog Form Fields**
   - ✅ Form header shows "Blog Engine Configuration"
   - ✅ Form contains 5 fields:
     1. **Blog Platform** (select, required)
     2. **Posting Frequency** (select, required)
     3. **Posts Per Week** (number, required)
     4. **Target Word Count** (number, optional)
     5. **SEO Optimization** (select, optional)

3. **Test Blog Form Validation**
   - Click "Save Configuration" without filling
   - ✅ Validation errors appear:
     - "Platform is required"
     - "Posting frequency is required"
     - "Must be at least 1" (Posts Per Week)

4. **Fill Complete Blog Form**
   - Enter the following values:
     - **Blog Platform**: Select "WordPress"
     - **Posting Frequency**: Select "Weekly"
     - **Posts Per Week**: `2`
     - **Target Word Count**: `800`
     - **SEO Optimization**: Select "Enabled"
   - ✅ All fields filled correctly

5. **Save Blog Configuration**
   - Click "Save Configuration"
   - ✅ Loading state displays
   - ✅ Success message appears after save
   - ✅ Configuration saved successfully

#### D. Test Email Configuration Form

1. **Switch to Email Service**
   - Click "Email Automation" button in service selector
   - ✅ Button becomes active (blue background)
   - ✅ Form changes to Email configuration

2. **Verify Email Form Fields**
   - ✅ Form header shows "Email Automation Settings"
   - ✅ Form contains 5 fields:
     1. **Email Provider** (select, required)
     2. **From Email Address** (text, required)
     3. **From Name** (text, required)
     4. **Reply-To Address** (text, optional)
     5. **Emails Per Month** (number, optional)

3. **Test Email Validation**
   - Fill fields with invalid email:
     - **Email Provider**: Select "SendGrid"
     - **From Email Address**: `invalid-email` (no @ symbol)
     - **From Name**: `Test Brand`
   - Click "Save Configuration"
   - ✅ Validation error appears:
     - "Invalid email address"
   - ✅ Email field highlighted in red

4. **Test Valid Email**
   - Correct email to: `newsletter@example.com`
   - Click "Save Configuration"
   - ✅ Validation passes
   - ✅ No email error

5. **Fill Complete Email Form**
   - Enter the following values:
     - **Email Provider**: Select "SendGrid"
     - **From Email Address**: `newsletter@mybrand.com`
     - **From Name**: `My Brand Newsletter`
     - **Reply-To Address**: `support@mybrand.com`
     - **Emails Per Month**: `4`
   - ✅ All fields filled correctly

6. **Save Email Configuration**
   - Click "Save Configuration"
   - ✅ Loading state displays
   - ✅ Success message appears
   - ✅ Configuration saved successfully

### Expected Results

- ✅ All 3 service forms (TikTok, Blog, Email) display correctly
- ✅ Service selector switches between forms
- ✅ All required fields validated
- ✅ Email validation works for email fields
- ✅ Number validation works (min value 1)
- ✅ Error messages clear when fields are corrected
- ✅ Save button shows loading state during save
- ✅ Success message displays after successful save
- ✅ Success message auto-dismisses after 3 seconds
- ✅ Network requests sent to `/api/config`
- ✅ No console errors during form operations

### Common Issues

- **Form not switching**: Check activeService state in ConfigurationDashboard
- **Validation not working**: Verify validation logic in ServiceConfigForm
- **Save not working**: Check onSave callback and API route
- **Email validation failing**: Verify regex pattern in validate function

---

## Test Flow 4: Verify Changes Persist

### Objective
Verify that configuration changes are saved and persist across page reloads and tab switches.

### Steps

#### A. Save Configuration and Switch Tabs

1. **Save TikTok Configuration**
   - Navigate to Services tab
   - Select TikTok service
   - Fill form with test data (from Test Flow 3)
   - Click "Save Configuration"
   - ✅ Success message appears

2. **Switch to Different Tab**
   - Click "API Keys" tab
   - ✅ API keys view displays
   - Click "Services" tab again
   - ✅ TikTok form still displays
   - **Note**: Form values may reset to defaults in current implementation
   - **Expected in future**: Form should reload saved values from API

3. **Check API for Saved Configuration**
   - Open browser DevTools
   - Go to Console tab
   - Fetch configuration:
     ```javascript
     fetch('/api/config')
       .then(r => r.json())
       .then(data => console.log(data))
     ```
   - ✅ Response shows all configurations:
     ```json
     {
       "tiktok": {
         "settings": { /* saved values */ },
         "lastUpdated": "2024-02-26T12:00:00.000Z"
       },
       "blog": { /* ... */ },
       "email": { /* ... */ }
     }
     ```

4. **Check Individual Service Configuration**
   - Fetch TikTok configuration:
     ```javascript
     fetch('/api/config/tiktok')
       .then(r => r.json())
       .then(data => console.log(data))
     ```
   - ✅ Response shows TikTok configuration:
     ```json
     {
       "service": "tiktok",
       "settings": {
         "apiKey": "sk-test-tiktok-api-key-123456",
         "webhookUrl": "...",
         "refreshInterval": 300,
         "autoPost": true,
         "contentPillars": [...]
       },
       "lastUpdated": "2024-02-26T12:00:00.000Z"
     }
     ```

#### B. Verify API Persistence (In-Memory)

1. **Save Multiple Configurations**
   - Save TikTok configuration
   - Save Blog configuration
   - Save Email configuration
   - ✅ All saves succeed with success messages

2. **Fetch All Configurations**
   - Use `/api/config` endpoint
   - ✅ All three services show in response
   - ✅ Each has `lastUpdated` timestamp
   - ✅ Settings match what was saved

3. **Update Existing Configuration**
   - Change TikTok "Max Videos Per Day" from 3 to 5
   - Save configuration
   - Fetch `/api/config/tiktok`
   - ✅ Updated value appears in response
   - ✅ `lastUpdated` timestamp is more recent

4. **Reset Configuration**
   - Use DELETE endpoint:
     ```javascript
     fetch('/api/config/tiktok', { method: 'DELETE' })
       .then(r => r.json())
       .then(data => console.log(data))
     ```
   - ✅ Response shows reset to defaults
   - ✅ Configuration reverted to default values

#### C. Verify Persistence Across Page Reload

**Note**: Current implementation uses in-memory storage (Map). Data persists during server runtime but resets on server restart. This section tests current behavior.

1. **Save Configuration**
   - Save TikTok configuration with specific values
   - Note the values saved

2. **Reload Page**
   - Press Cmd+R or Ctrl+R to reload page
   - Navigate back to Services → TikTok
   - **Current Behavior**: Form shows default values
   - **Future Enhancement**: Should fetch saved values from API on mount

3. **Check API Still Has Data**
   - Without restarting dev server, fetch `/api/config/tiktok`
   - ✅ Saved data still exists in API (in-memory storage persists during server runtime)

4. **Restart Dev Server**
   - Stop dev server (Ctrl+C)
   - Start dev server (`npm run dev`)
   - Fetch `/api/config/tiktok`
   - **Current Behavior**: Returns default configuration
   - **Note**: In-memory storage is cleared on restart
   - **Future Enhancement**: Will use database for true persistence

### Expected Results

- ✅ Configurations save successfully via `/api/config` POST endpoint
- ✅ Saved configurations accessible via `/api/config` GET endpoint
- ✅ Individual service configs accessible via `/api/config/[service]`
- ✅ Updates modify existing configuration (not create new)
- ✅ `lastUpdated` timestamp updates on save
- ✅ DELETE endpoint resets to defaults
- ✅ In-memory storage persists during server runtime
- ✅ Data clears on server restart (expected with current implementation)
- **Future**: Form will reload saved values from API on mount
- **Future**: Database persistence for true data durability

### Common Issues

- **Data not saving**: Check config-manager.ts Map storage
- **API returning defaults**: Verify POST request succeeded
- **Data lost on reload**: Expected - in-memory storage, database needed for persistence
- **Network errors**: Check dev server is running and API routes exist

---

## Test Flow 5: Test Key Masking and Copy

### Objective
Verify that API keys are properly masked for security and copy functionality works correctly.

### Steps

#### A. Verify Key Masking

1. **Navigate to API Keys Tab**
   - Go to Configuration → API Keys
   - ✅ API key list displays with 3 default keys

2. **Inspect Masked Values**
   - For each key, verify the masked value format:
     - **TikTok Key**: `sk-••••••••••••••••`
     - **OpenAI Key**: `sk-••••••••••••••••`
     - **SendGrid Key**: `SG.••••••••••••••••`
   - ✅ Only prefix is visible
   - ✅ Rest of key replaced with bullet characters (••••)
   - ✅ Masking is consistent across all keys

3. **Inspect DOM Elements**
   - Open DevTools
   - Inspect the masked value element
   - ✅ Visible text shows masked value
   - ✅ Full key value NOT visible in HTML
   - ✅ Security: Full key only available via fullValue prop (not rendered)

4. **Check for Key Exposure**
   - View page source (Cmd+Opt+U or Ctrl+U)
   - Search for "sk-tiktok" or "sk-openai"
   - ✅ Full keys should NOT appear in page source
   - ✅ Only masked values visible
   - **Security**: Full values exist in JavaScript but not rendered

#### B. Test Copy Functionality

1. **Copy First Key (TikTok)**
   - Hover over first API key card
   - ✅ Copy button visible (clipboard icon)
   - Click copy button
   - ✅ Icon changes to green checkmark
   - ✅ Smooth transition animation
   - Wait 2 seconds
   - ✅ Icon returns to clipboard

2. **Verify Clipboard Content**
   - Open a text editor
   - Paste content (Cmd+V or Ctrl+V)
   - ✅ Full unmasked key is pasted:
     - Expected: `sk-tiktok-api-key-example-12345678`
   - ✅ Full key copied, not masked version
   - ✅ No extra characters or formatting

3. **Copy Multiple Keys in Sequence**
   - Copy TikTok key
   - Immediately copy OpenAI key
   - ✅ Both copy operations work
   - ✅ Feedback shows on correct button
   - ✅ Previous button returns to normal
   - Paste clipboard
   - ✅ Shows most recent key (OpenAI)

4. **Copy Same Key Twice**
   - Copy TikTok key
   - Wait for checkmark to appear
   - Click copy button again (while still showing checkmark)
   - ✅ Copy still works
   - ✅ Checkmark resets and shows again
   - Paste clipboard
   - ✅ Key copied successfully

#### C. Test Browser Clipboard API

1. **Check Clipboard Permissions**
   - Some browsers require HTTPS or localhost
   - ✅ Localhost allows clipboard access
   - ✅ No permission errors in console

2. **Test in Different Browsers**
   - **Chrome/Edge**:
     - ✅ Copy works without issues
     - ✅ Uses navigator.clipboard.writeText()
   - **Firefox**:
     - ✅ Copy works
     - ✅ May show permission prompt first time
   - **Safari**:
     - ✅ Copy works on localhost
     - ✅ Requires user gesture (button click)

3. **Test Fallback (if clipboard API unavailable)**
   - Current implementation uses modern clipboard API
   - If API unavailable:
     - ✅ Error logged to console
     - ✅ User sees error feedback (could be improved)
   - **Enhancement**: Add fallback using execCommand('copy')

#### D. Test Copy Callback

1. **Monitor Copy Events**
   - Open DevTools Console
   - Click copy button
   - ✅ No errors logged
   - ✅ Copy operation completes silently
   - ✅ onCopy callback fires (if provided)

2. **Verify Copy Handler**
   - In ApiKeyItem component, onCopy prop receives full value
   - ✅ Handler called with fullValue, not maskedValue
   - ✅ Parent component can track copy events

### Expected Results

- ✅ API keys displayed with masked values (sk-••••••••••••••••)
- ✅ Only prefix visible, rest obscured with bullets
- ✅ Full key values NOT visible in HTML/DOM
- ✅ Copy button visible on each key card
- ✅ Click copy button copies full unmasked value
- ✅ Copy button shows success feedback (green checkmark)
- ✅ Feedback auto-reverts to clipboard icon after 2 seconds
- ✅ Multiple keys can be copied independently
- ✅ Clipboard API works in all major browsers
- ✅ No security issues - keys masked in UI
- ✅ No console errors during copy operations

### Common Issues

- **Copy not working**: Check browser clipboard API support
- **Permission denied**: Ensure running on localhost or HTTPS
- **Wrong value copied**: Verify fullValue prop passed correctly
- **No feedback**: Check CopySuccess state management
- **Keys visible in HTML**: Verify maskedValue used in render, not fullValue

---

## Test Flow 6: Workspace Settings

### Objective
Verify workspace management functionality including name editing, member list, and invitations.

### Steps

#### A. Navigate to Workspace Tab

1. **Click Workspace Tab**
   - Navigate to Configuration page
   - Click "Workspace" tab
   - ✅ Workspace tab becomes active (blue underline)
   - ✅ Workspace settings form displays

#### B. Verify Workspace Information

1. **Check Workspace Name Field**
   - ✅ "Workspace Name" field displays
   - ✅ Current workspace name pre-filled
   - ✅ Input is editable
   - ✅ Save button visible

2. **Check Team Members Section**
   - ✅ "Team Members" section displays
   - ✅ Member count visible (e.g., "3 members")
   - ✅ List of members shown:
     - Member avatar (image or initials)
     - Full name
     - Email address
     - Role badge (Admin/Member)
   - ✅ Remove button for each member (trash icon)
   - **Note**: Admin cannot remove themselves

3. **Check Invite Section**
   - ✅ "Invite New Member" section displays
   - ✅ Email input field
   - ✅ Role selector (Admin/Member dropdown)
   - ✅ "Send Invitation" button

#### C. Test Workspace Name Editing

1. **Edit Workspace Name**
   - Current name: "My Workspace"
   - Change to: "Updated Brand Workspace"
   - ✅ Text updates in field
   - ✅ Save button enabled

2. **Save Workspace Name**
   - Click "Save Changes" button
   - ✅ Button shows loading state (spinner)
   - ✅ Success message appears (green background)
   - ✅ Message: "Workspace settings updated successfully"
   - ✅ Success message auto-dismisses after 3 seconds

3. **Verify Name Update in Clerk**
   - Name should update in Clerk Organization
   - Check WorkspaceSelector in header
   - ✅ New name appears in workspace dropdown
   - **Note**: Requires Clerk organization.update() to succeed

4. **Test Validation**
   - Clear workspace name field (empty)
   - Click "Save Changes"
   - ✅ Validation error may appear
   - ✅ Empty name not allowed
   - Restore valid name

#### D. Test Member Invitation

1. **Fill Invitation Form**
   - Enter email: `newuser@example.com`
   - Select role: "Member" (basic_member)
   - ✅ Both fields filled

2. **Send Invitation**
   - Click "Send Invitation" button
   - ✅ Button shows loading state
   - ✅ Invitation sent via Clerk API
   - ✅ Success message appears (green background)
   - ✅ Message: "Invitation sent successfully"
   - ✅ Form resets (email cleared)

3. **Test Email Validation**
   - Enter invalid email: `invalid-email`
   - Click "Send Invitation"
   - ✅ Validation error appears
   - ✅ Message: "Please enter a valid email address"
   - Correct to valid email
   - ✅ Error clears

4. **Invite as Admin**
   - Enter email: `admin@example.com`
   - Select role: "Admin" (admin)
   - Click "Send Invitation"
   - ✅ Invitation sent with admin role
   - ✅ Success feedback

5. **Check Invitation in Clerk**
   - Invited user should receive email from Clerk
   - ✅ Email contains organization invitation link
   - ✅ User can accept invitation
   - **Note**: Requires valid Clerk email configuration

#### E. Test Member Removal

1. **Identify Removable Member**
   - ✅ Current user (admin) should NOT have remove button
   - ✅ Other members have remove button

2. **Click Remove Button**
   - Click trash icon on a member
   - **Note**: Current implementation may show confirmation
   - ✅ Confirmation appears (optional)
   - Confirm removal
   - ✅ Member removed from list
   - ✅ Member count decreases

3. **Verify Removal in Clerk**
   - Member should be removed from Clerk Organization
   - ✅ Member no longer has access to workspace
   - ✅ Removed member loses workspace in their list

4. **Test Admin Protection**
   - Try removing current admin user (yourself)
   - ✅ Remove button disabled or hidden
   - ✅ Cannot remove yourself
   - **Security**: Prevents admins from locking themselves out

#### F. Test Role Display

1. **Verify Role Badges**
   - Admin members:
     - ✅ Badge shows "Admin"
     - ✅ Crown icon visible
     - ✅ Purple background color
   - Regular members:
     - ✅ Badge shows "Member"
     - ✅ User icon visible
     - ✅ Blue background color

2. **Check Role Permissions**
   - Admin users:
     - ✅ Can edit workspace name
     - ✅ Can invite new members
     - ✅ Can remove other members
     - ✅ Can assign admin role to invites
   - Regular members:
     - ✅ May have limited permissions
     - **Note**: Implement role-based access control if needed

### Expected Results

- ✅ Workspace settings tab displays correctly
- ✅ Workspace name editable with save functionality
- ✅ Team members list shows all members with roles
- ✅ Role badges display correctly (Admin/Member)
- ✅ Invite form sends invitations via Clerk API
- ✅ Email validation works on invite form
- ✅ Both Admin and Member roles can be invited
- ✅ Member removal works (except for current admin)
- ✅ Success messages appear for all operations
- ✅ Loading states shown during async operations
- ✅ Error handling for failed operations
- ✅ Integration with Clerk Organizations API works
- ✅ No console errors

### Common Issues

- **Name not saving**: Check Clerk organization.update() API call
- **Invitations not sending**: Verify Clerk API permissions and email config
- **Members not loading**: Check Clerk organization members list API
- **Removal failing**: Verify admin permissions and Clerk member removal API
- **Role badges wrong color**: Check badge styling in WorkspaceSettings component

---

## Security Verification

### Objective
Ensure configuration management implements proper security practices.

### Critical Security Checks

#### A. API Key Masking

- ✅ API keys masked in UI (sk-••••••••••••••••)
- ✅ Full keys NOT visible in HTML source
- ✅ Full keys NOT exposed in network responses (future enhancement)
- ✅ Masking pattern consistent and secure

#### B. Authentication Required

1. **Test Unauthenticated Access**
   - Sign out from dashboard
   - Navigate to: `http://localhost:3000/config`
   - ✅ Redirected to `/sign-in`
   - ✅ Cannot access config page without auth

2. **Test API Endpoints Without Auth**
   - Sign out
   - Fetch: `http://localhost:3000/api/config`
   - **Current**: Returns data (no auth middleware yet)
   - **Future**: Should return 401 Unauthorized
   - **Note**: API auth middleware created in subtask-7-4, will be integrated in Phase 8

#### C. Workspace Isolation

1. **Create Multiple Workspaces**
   - Create workspace "Brand A"
   - Save TikTok configuration with specific API key
   - Switch to workspace "Brand B"
   - Navigate to config page
   - **Expected**: Different configuration for Brand B
   - ✅ Configurations isolated per workspace
   - **Note**: Full workspace isolation requires database storage

2. **Test Cross-Workspace Access**
   - Try accessing other workspace's config
   - ✅ Should NOT see other workspace's API keys
   - ✅ Should NOT be able to modify other workspace's settings
   - **Security**: Workspace ID validation in API middleware

#### D. Input Validation

1. **Test XSS Prevention**
   - Enter script tag in workspace name: `<script>alert('XSS')</script>`
   - Save workspace name
   - ✅ Script not executed
   - ✅ Input sanitized or escaped
   - Check DOM: `<script>` tags rendered as text, not executed

2. **Test SQL Injection** (Future)
   - When database is added
   - Enter SQL in fields: `'; DROP TABLE users; --`
   - ✅ Input treated as string, not executed
   - ✅ Parameterized queries used

3. **Test Email Validation**
   - Enter malicious email: `attacker@example.com<script>alert(1)</script>`
   - ✅ Validation rejects input
   - ✅ Email format strictly enforced

#### E. HTTPS in Production

- ✅ Development: Localhost (HTTP) acceptable
- ✅ Production: MUST use HTTPS
- ✅ Clerk requires HTTPS for production
- ✅ Environment variables protected

### Expected Security Results

- ✅ API keys masked in all UI displays
- ✅ Authentication required for config page access
- ✅ API endpoints will be protected with auth middleware (Phase 8)
- ✅ Workspace isolation prevents cross-workspace access
- ✅ Input validation prevents XSS attacks
- ✅ Email validation strict and secure
- ✅ No sensitive data in console logs
- ✅ No API keys in browser DevTools Network tab responses
- ✅ Environment variables not exposed to client
- ✅ HTTPS enforced in production

### Common Security Issues

- **API keys visible**: Verify masking logic in ApiKeyItem
- **Unauthenticated access**: Implement withAuth() middleware on API routes
- **Cross-workspace leaks**: Add workspace ID validation in API layer
- **XSS vulnerabilities**: Use React's automatic escaping, avoid dangerouslySetInnerHTML
- **Exposed secrets**: Check .env.local not committed to git

---

## Performance Expectations

### Loading Times

- ✅ **Page Load**: < 2 seconds
- ✅ **Tab Switch**: < 500ms (instant)
- ✅ **Form Save**: < 2 seconds (includes 1s simulated API delay)
- ✅ **API Key Copy**: < 100ms (instant feedback)
- ✅ **Delete Confirmation**: < 100ms (instant modal display)

### API Response Times

- ✅ **GET /api/config**: < 200ms
- ✅ **POST /api/config**: < 1500ms (includes 1s simulated delay)
- ✅ **DELETE /api/config/[service]**: < 500ms

### User Experience Metrics

- ✅ **Time to Interactive**: < 3 seconds
- ✅ **Form Validation Feedback**: < 100ms (instant)
- ✅ **Loading States**: Display within 100ms of action
- ✅ **Success Messages**: Auto-dismiss after 3 seconds
- ✅ **Copy Feedback**: Visible within 50ms

### Responsive Design

- ✅ **Mobile (375px)**: Fully functional, no horizontal scroll
- ✅ **Tablet (768px)**: Optimized layout, all features accessible
- ✅ **Desktop (1920px)**: Full layout with proper spacing

### Browser Compatibility

- ✅ **Chrome/Edge**: Full support
- ✅ **Firefox**: Full support
- ✅ **Safari**: Full support (clipboard API requires user gesture)
- ✅ **Mobile Safari**: Responsive design works

---

## Common Issues & Troubleshooting

### Issue: Tab Navigation Not Working

**Symptoms:**
- Clicking tabs doesn't switch content
- Active tab indicator doesn't change

**Solution:**
- Check `activeTab` state in ConfigurationDashboard
- Verify tab button onClick handlers
- Confirm conditional rendering logic

**Code Check:**
```tsx
const [activeTab, setActiveTab] = useState<ConfigTab>(defaultTab);
// Verify state updates on click
```

---

### Issue: API Keys Not Displaying

**Symptoms:**
- Empty state shows when keys should exist
- Loading state persists indefinitely

**Solution:**
- Check DEFAULT_KEYS in ApiKeyManager
- Verify component props passed correctly
- Check isLoading prop is false

**Code Check:**
```tsx
// Verify DEFAULT_KEYS exists and has data
const DEFAULT_KEYS: ApiKey[] = [/* ... */];
```

---

### Issue: Copy to Clipboard Failing

**Symptoms:**
- Copy button doesn't work
- Console error: "navigator.clipboard is undefined"

**Solution:**
- Ensure running on localhost or HTTPS
- Check browser clipboard API support
- Verify fullValue prop passed to ApiKeyItem

**Code Check:**
```tsx
// ApiKeyItem should receive fullValue prop
<ApiKeyItem fullValue={key.fullValue} />
```

**Browser Check:**
```javascript
// Test clipboard API availability
console.log('Clipboard API:', navigator.clipboard);
```

---

### Issue: Form Validation Not Working

**Symptoms:**
- Can save form with empty required fields
- Error messages not appearing

**Solution:**
- Check validate() function in ServiceConfigForm
- Verify required prop on ConfigField components
- Confirm error state management

**Code Check:**
```tsx
// Ensure required fields checked in validate()
if (!config.apiKey) newErrors.apiKey = "API Key is required";
```

---

### Issue: Configuration Not Persisting

**Symptoms:**
- Save succeeds but data resets on reload
- API returns default configuration

**Solution:**
- Current: In-memory storage expected behavior
- Check if save request succeeded (200 status)
- Verify /api/config endpoint working

**Expected Behavior:**
- In-memory: Data persists during server runtime
- Resets on server restart (normal)
- Future: Database persistence needed

---

### Issue: Workspace Settings Not Loading

**Symptoms:**
- Workspace tab shows error
- Member list empty
- Cannot save workspace name

**Solution:**
- Check Clerk environment variables configured
- Verify user has workspace/organization selected
- Check Clerk API calls in WorkspaceSettings

**Clerk Check:**
```javascript
// Ensure organization exists
const { organization } = useOrganization();
console.log('Current org:', organization);
```

---

### Issue: Invitation Emails Not Sending

**Symptoms:**
- Invitation form succeeds but email not received
- Clerk API returns error

**Solution:**
- Verify Clerk email configuration in dashboard
- Check organization invitation permissions
- Confirm email address valid and not already member

**Clerk Dashboard:**
- Settings → Email & SMS → Verify email provider configured
- Organizations → Verify invitations enabled

---

### Issue: Delete Confirmation Not Showing

**Symptoms:**
- Clicking delete immediately removes key
- No confirmation dialog appears

**Solution:**
- Check showDeleteConfirm state in ApiKeyItem
- Verify conditional rendering of dialog
- Confirm onClick handlers wired correctly

**Code Check:**
```tsx
const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
// Should toggle on delete button click
```

---

### Issue: Loading States Not Appearing

**Symptoms:**
- No spinner during save
- Button doesn't change to "Saving..."

**Solution:**
- Check isSaving state in ServiceConfigForm
- Verify loading state in button render
- Confirm async save function sets state

**Code Check:**
```tsx
const [isSaving, setIsSaving] = useState(false);
setIsSaving(true);
// ... await save operation
setIsSaving(false);
```

---

### Issue: Success Messages Not Auto-Dismissing

**Symptoms:**
- Success message stays visible
- No auto-dismiss after 3 seconds

**Solution:**
- Check setTimeout in save handler
- Verify saveSuccess state resets
- Confirm cleanup in useEffect

**Code Check:**
```tsx
setSaveSuccess(true);
setTimeout(() => setSaveSuccess(false), 3000);
```

---

## QA Acceptance Checklist

Use this checklist for final QA sign-off.

### Page Navigation

- [ ] Configuration page accessible via sidebar
- [ ] URL routing works (`/config`)
- [ ] Page loads without errors
- [ ] Responsive design on mobile/tablet/desktop
- [ ] No horizontal scroll on mobile

### Tab Interface

- [ ] All 3 tabs visible (API Keys, Services, Workspace)
- [ ] Default tab is "API Keys"
- [ ] Tab switching works smoothly
- [ ] Active tab indicator (blue underline) displays
- [ ] Tab content changes correctly

### API Key Management

- [ ] Default 3 API keys display
- [ ] Each key shows: name, service, masked value, dates
- [ ] Copy button copies full unmasked value
- [ ] Copy button shows success feedback (green checkmark)
- [ ] Delete button shows confirmation dialog
- [ ] Delete confirmation prevents accidental deletion
- [ ] Delete removes key from list
- [ ] Empty state displays when no keys
- [ ] Add button shows placeholder alert
- [ ] Loading state shows skeleton screens

### Service Configuration Forms

- [ ] All 3 service forms work (TikTok, Blog, Email)
- [ ] Service selector switches between forms
- [ ] Required fields marked with red asterisk
- [ ] Validation works for empty required fields
- [ ] Email validation works (Email form)
- [ ] Number validation works (min value 1)
- [ ] Error messages clear when fields corrected
- [ ] Save button shows loading state
- [ ] Success message displays after save
- [ ] Success message auto-dismisses after 3 seconds

### Workspace Settings

- [ ] Workspace name editable
- [ ] Workspace name save works
- [ ] Team members list displays
- [ ] Role badges show correctly (Admin/Member)
- [ ] Invite form sends invitations
- [ ] Email validation on invite form
- [ ] Member removal works (except current admin)
- [ ] Admin cannot remove themselves

### API Integration

- [ ] GET /api/config returns all configurations
- [ ] POST /api/config updates configuration
- [ ] GET /api/config/[service] returns service config
- [ ] PUT /api/config/[service] updates service config
- [ ] DELETE /api/config/[service] resets to defaults
- [ ] API responses have correct status codes
- [ ] Network requests visible in DevTools

### Security

- [ ] API keys masked in UI (sk-••••••••••••••••)
- [ ] Full keys NOT visible in HTML source
- [ ] Authentication required for config page
- [ ] Input validation prevents XSS
- [ ] Email validation strict
- [ ] No sensitive data in console logs

### Performance

- [ ] Page load < 2 seconds
- [ ] Tab switch < 500ms
- [ ] Form save < 2 seconds
- [ ] Copy feedback < 100ms
- [ ] No performance warnings in console

### User Experience

- [ ] All buttons have hover states
- [ ] Loading states clear and visible
- [ ] Error messages helpful and clear
- [ ] Success messages provide feedback
- [ ] Forms keyboard accessible
- [ ] Tab navigation works with keyboard

### Browser Testing

- [ ] Works in Chrome/Edge
- [ ] Works in Firefox
- [ ] Works in Safari
- [ ] Works on mobile browsers
- [ ] No console errors in any browser

### Accessibility

- [ ] Form labels associated with inputs
- [ ] Required fields marked semantically
- [ ] Error messages announced to screen readers
- [ ] Keyboard navigation works throughout
- [ ] Focus states visible
- [ ] Color contrast meets WCAG standards

### Error Handling

- [ ] Network errors handled gracefully
- [ ] Form validation errors clear
- [ ] API errors show user-friendly messages
- [ ] No unhandled promise rejections
- [ ] Console errors investigated and resolved

---

## Sign-Off

**QA Tester:** ____________________

**Date:** ____________________

**Test Environment:**
- Browser: ____________________
- OS: ____________________
- Screen Resolution: ____________________

**Overall Status:** [ ] PASS [ ] FAIL

**Notes:**

---

**End of Verification Guide**
