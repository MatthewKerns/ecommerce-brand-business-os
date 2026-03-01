# Mobile Responsiveness Testing Guide

## Overview

This guide provides comprehensive testing procedures for verifying mobile responsiveness across all dashboard pages and components. The dashboard is built with a mobile-first approach using Tailwind CSS responsive breakpoints.

## Test Environment

### Prerequisites

1. **Development Server Running**
   ```bash
   cd dashboard
   npm install
   npm run dev
   ```
   Server should be accessible at: http://localhost:3000

2. **Clerk Environment Variables**
   - `.env.local` configured with Clerk credentials
   - User authenticated with workspace access

3. **Testing Tools**
   - Chrome DevTools Device Toolbar (Cmd+Shift+M / Ctrl+Shift+M)
   - Real device testing (optional but recommended)
   - Touch simulation enabled in DevTools

### Test Viewports

| Device | Width | Height | Breakpoint |
|--------|-------|--------|------------|
| iPhone SE | 375px | 667px | Mobile (< 768px) |
| iPhone 12/13 Pro | 390px | 844px | Mobile (< 768px) |
| iPad Mini | 768px | 1024px | Tablet (md: 768px+) |
| iPad Pro | 1024px | 1366px | Desktop (lg: 1024px+) |
| Desktop | 1920px | 1080px | Desktop (lg: 1024px+) |

### Tailwind Breakpoints

- `sm`: 640px
- `md`: 768px
- `lg`: 1024px
- `xl`: 1280px
- `2xl`: 1536px

---

## Test Flow 1: Layout & Navigation Responsiveness

### Mobile (375px - 767px)

#### Expected Behavior:
- Sidebar hidden by default
- Mobile menu toggle button visible in top-left
- Header displays workspace selector on left side
- Main content uses full width (no left padding)
- All grids collapse to single column

#### Testing Steps:

1. **Open Dashboard in Chrome DevTools**
   ```
   1. Open http://localhost:3000
   2. Press Cmd+Shift+M (Mac) or Ctrl+Shift+M (Windows)
   3. Select "iPhone SE" or set custom width to 375px
   ```

2. **Verify Sidebar Behavior**
   - [ ] Sidebar is hidden by default (not visible)
   - [ ] Mobile menu toggle button visible at top-left
   - [ ] Button shows hamburger menu icon (three lines)
   - [ ] Click button → sidebar slides in from left
   - [ ] Dark backdrop overlay appears behind sidebar
   - [ ] Sidebar displays full navigation items
   - [ ] WorkspaceSelector visible in sidebar
   - [ ] Click backdrop → sidebar closes
   - [ ] Click X icon → sidebar closes
   - [ ] Sidebar animation is smooth (200ms transition)

3. **Verify Header Layout**
   - [ ] Header spans full width
   - [ ] WorkspaceSelector appears on left side (mobile)
   - [ ] UserMenu (avatar) appears on right side
   - [ ] Header height: 64px (h-16)
   - [ ] All interactive elements easily tappable (min 44x44px)

4. **Verify Main Content Area**
   - [ ] Content starts at top edge (no left padding)
   - [ ] Content padding: 16px (p-4)
   - [ ] Page headers visible and readable
   - [ ] Icons display at appropriate size

5. **Test Touch Navigation**
   - [ ] All sidebar navigation links are tappable
   - [ ] Active route highlighted correctly
   - [ ] Navigation works without delay
   - [ ] Smooth page transitions

### Tablet (768px - 1023px)

#### Expected Behavior:
- Sidebar hidden by default (still mobile behavior)
- Mobile menu toggle button visible
- Header workspace selector moves to left
- Main content grids expand to 2 columns (md:grid-cols-2)

#### Testing Steps:

1. **Set Viewport to 768px**
   ```
   1. In DevTools Device Toolbar
   2. Select "iPad Mini" or set custom width to 768px
   ```

2. **Verify Layout**
   - [ ] Sidebar behavior same as mobile (collapsible)
   - [ ] Mobile menu button still visible
   - [ ] Content grids show 2 columns (md:grid-cols-2)
   - [ ] KPI cards display in 2-column grid
   - [ ] Service status cards display in 2-column grid
   - [ ] Content padding increases: 24px (md:p-6)

3. **Test Grid Layouts**
   - [ ] Dashboard: KPI grid shows 2 columns
   - [ ] Health page: Service status grid shows 2 columns
   - [ ] Config page: Forms display properly
   - [ ] All cards have consistent spacing

### Desktop (1024px+)

#### Expected Behavior:
- Sidebar always visible and fixed
- No mobile menu button
- Header workspace selector on right side
- Main content offset by sidebar width (256px)
- Grids expand to 3 columns (lg:grid-cols-3)

#### Testing Steps:

1. **Set Viewport to 1920px**
   ```
   1. In DevTools Device Toolbar
   2. Select "Responsive" and set width to 1920px
   3. Or disable Device Toolbar for full desktop view
   ```

2. **Verify Sidebar**
   - [ ] Sidebar permanently visible on left
   - [ ] Sidebar width: 256px (w-64)
   - [ ] No mobile menu button visible
   - [ ] Sidebar has fixed positioning
   - [ ] Navigation items clearly visible
   - [ ] WorkspaceSelector displays in sidebar
   - [ ] Sidebar footer displays copyright

3. **Verify Header Layout**
   - [ ] Header starts at 256px from left edge
   - [ ] WorkspaceSelector appears on right side (desktop)
   - [ ] UserMenu appears next to workspace selector
   - [ ] Header has proper spacing

4. **Verify Main Content Area**
   - [ ] Content area offset by sidebar: pl-64 (padding-left: 256px)
   - [ ] Content padding: 24px (lg:p-6)
   - [ ] Grids display 3 columns (lg:grid-cols-3)
   - [ ] Maximum content width is readable

5. **Test Grid Layouts**
   - [ ] Dashboard: KPI grid shows 3 columns
   - [ ] Health page: Service status grid shows 3 columns
   - [ ] Config page: Forms display in optimal width
   - [ ] All spacing is consistent and proportional

---

## Test Flow 2: Component Responsiveness

### MetricCard Component

#### Mobile (375px):
- [ ] Card displays in single column
- [ ] Title text readable (not truncated)
- [ ] Value displays clearly (text-3xl)
- [ ] Change indicator visible with icon
- [ ] Icon displays in top-right
- [ ] Padding: 24px (p-6)
- [ ] Touch target size adequate

#### Tablet (768px):
- [ ] Cards display in 2-column grid
- [ ] Consistent spacing between cards
- [ ] All card content visible

#### Desktop (1024px+):
- [ ] Cards display in 3-column grid
- [ ] Hover effects work (shadow on hover)
- [ ] Consistent alignment across row

### KPIOverview Component

#### Mobile (375px):
- [ ] Single column layout (stack vertically)
- [ ] All 6 metrics visible
- [ ] Scrollable if content exceeds viewport
- [ ] Gap between cards: 16px (gap-4)

#### Tablet (768px):
- [ ] 2-column grid (md:grid-cols-2)
- [ ] 3 rows of 2 cards each
- [ ] Consistent spacing

#### Desktop (1024px+):
- [ ] 3-column grid (lg:grid-cols-3)
- [ ] 2 rows of 3 cards each
- [ ] Optimal layout utilization

### SystemHealthDashboard Component

#### Mobile (375px):
- [ ] Overall status card full width
- [ ] Service status cards stack vertically
- [ ] Activity log below service cards
- [ ] Refresh button accessible
- [ ] All status indicators visible

#### Tablet (768px):
- [ ] Service cards in 2-column grid
- [ ] Activity log spans full width
- [ ] Proper spacing maintained

#### Desktop (1024px+):
- [ ] Service cards in 3-column grid
- [ ] Activity log in sidebar layout (if implemented)
- [ ] All information easily scannable

### ConfigurationDashboard Component

#### Mobile (375px):
- [ ] Tab buttons stack or scroll horizontally
- [ ] Active tab clearly indicated
- [ ] Tab content full width
- [ ] Forms display in single column
- [ ] Input fields full width
- [ ] Buttons full width or properly sized

#### Tablet (768px):
- [ ] Tabs display horizontally
- [ ] Form fields maintain readable width
- [ ] Multi-column forms if appropriate

#### Desktop (1024px+):
- [ ] Tabs display horizontally with spacing
- [ ] Forms use optimal width (not too wide)
- [ ] Side-by-side layouts where appropriate

### ApiKeyManager Component

#### Mobile (375px):
- [ ] API key items stack vertically
- [ ] Key name visible
- [ ] Masked value readable (sk-••••••••)
- [ ] Copy button accessible
- [ ] Delete button accessible
- [ ] Confirmation modal centered and readable

#### Tablet/Desktop:
- [ ] API key list displays properly
- [ ] Action buttons aligned
- [ ] Copy feedback visible
- [ ] Modal properly sized

### WorkspaceSelector Component

#### Mobile (375px):
- [ ] Button displays workspace name
- [ ] Dropdown menu full width or properly positioned
- [ ] Menu items clearly visible
- [ ] Avatar/icon displays correctly
- [ ] Touch-friendly menu items

#### Tablet/Desktop:
- [ ] Dropdown positioned correctly (not off-screen)
- [ ] Menu width appropriate
- [ ] Hover states work

---

## Test Flow 3: Page-Specific Responsiveness

### Dashboard Page (/)

#### Mobile (375px):
```
Test Steps:
1. Navigate to http://localhost:3000/
2. Set viewport to 375px width
```

- [ ] **Page header**:
  - Icon displays (rounded bg-slate-100, p-3)
  - Title "Dashboard" readable (text-3xl)
  - Subtitle visible
- [ ] **KPI Overview**:
  - 6 metric cards stack vertically
  - All cards full width
  - Consistent spacing (space-y-4)
- [ ] **Loading States Demo** (if present):
  - Section visible and readable
  - Toggle button accessible
  - Demo components display properly
- [ ] **Scroll behavior**:
  - Smooth scrolling
  - No horizontal overflow
  - All content accessible

#### Tablet (768px):
- [ ] KPI cards in 2-column grid
- [ ] Page sections properly spaced
- [ ] Loading demo displays in 2 columns

#### Desktop (1920px):
- [ ] KPI cards in 3-column grid
- [ ] Content uses optimal width
- [ ] No excessive whitespace

### System Health Page (/health)

#### Mobile (375px):
```
Test Steps:
1. Navigate to http://localhost:3000/health
2. Set viewport to 375px width
```

- [ ] **Page header**:
  - Green icon background displays
  - Title and subtitle readable
- [ ] **Overall status card**:
  - Full width
  - Status indicator visible (color-coded)
  - Refresh button accessible and functional
- [ ] **Service status cards**:
  - Stack vertically (single column)
  - Each card shows:
    - Service name
    - Status badge (up/down/degraded)
    - Uptime percentage
    - Last check timestamp
  - Loading states display correctly
- [ ] **Activity log**:
  - Full width below service cards
  - Log items readable
  - Timestamps display
  - Icons visible
- [ ] **Real-time updates**:
  - Status updates visible
  - Timestamps update
  - No layout shift during updates

#### Tablet (768px):
- [ ] Service cards in 2-column grid
- [ ] Activity log spans full width
- [ ] Proper spacing between sections

#### Desktop (1920px):
- [ ] Service cards in 3-column grid
- [ ] Activity log positioned appropriately
- [ ] All status information easily scannable

### Configuration Page (/config)

#### Mobile (375px):
```
Test Steps:
1. Navigate to http://localhost:3000/config
2. Set viewport to 375px width
```

- [ ] **Page header**:
  - Blue icon background displays
  - Title and subtitle readable

- [ ] **Tab Navigation**:
  - All 3 tabs visible (API Keys, Services, Workspace)
  - Active tab highlighted
  - Tab buttons touch-friendly
  - Tabs scroll horizontally if needed
  - Active tab indicator visible

- [ ] **API Keys Tab**:
  - API key items stack vertically
  - Key details readable:
    - Name
    - Service tag
    - Masked value (sk-••••••••)
    - Created date
    - Last used
  - Copy button accessible (min 44x44px)
  - Delete button accessible
  - Confirmation dialog:
    - Centered on screen
    - Full overlay backdrop
    - Buttons clearly visible
    - Cancel and Delete options
  - Empty state (if no keys):
    - Icon centered
    - Message readable
    - "Add API Key" button visible

- [ ] **Services Tab**:
  - Service selector buttons:
    - Display horizontally or wrap
    - Active service highlighted
    - Touch-friendly size
  - Service form:
    - All fields full width
    - Labels visible above inputs
    - Helper text readable
    - Required indicators visible (red asterisk)
    - Input fields adequate height (touch-friendly)
    - Select dropdowns work properly
    - Number inputs display spinners
    - Save button:
      - Full width or min-width
      - Loading state visible
      - Success/error messages display
  - Form validation:
    - Error messages display below fields
    - Error styling visible (red border)
    - Error icon displays

- [ ] **Workspace Tab**:
  - Workspace name field full width
  - Save button accessible
  - Team members list:
    - Members stack vertically
    - Avatar visible
    - Name and role readable
    - Admin badge visible
    - Remove button accessible (admin only)
  - Invite member section:
    - Form fields full width
    - Role selector accessible
    - Send invitation button visible
  - Success/error feedback displays properly

#### Tablet (768px):
- [ ] Tabs display horizontally without wrapping
- [ ] Forms use appropriate width
- [ ] API key list items have better layout
- [ ] Service selector horizontal
- [ ] Member list more spacious

#### Desktop (1920px):
- [ ] Tab content uses optimal width
- [ ] Forms not too wide (max-w-2xl or similar)
- [ ] Multi-column layouts where appropriate
- [ ] API key list items well-spaced
- [ ] Member list displays efficiently

### Analytics Page (/analytics)

#### Mobile (375px):
```
Test Steps:
1. Navigate to http://localhost:3000/analytics
2. Set viewport to 375px width
```

- [ ] Page header displays correctly
- [ ] Placeholder content readable
- [ ] Date range selector accessible
- [ ] Metric cards stack vertically
- [ ] Chart placeholder displays
- [ ] Channel breakdown list readable

#### Tablet/Desktop:
- [ ] Grid layouts expand appropriately
- [ ] Charts display at optimal size
- [ ] Date picker positioned correctly

---

## Test Flow 4: Touch Interaction Testing

### Prerequisites
- Enable touch simulation in Chrome DevTools
- Or use actual touch device (iPad, iPhone)

### Touch Target Sizes

#### Minimum Requirements:
- All interactive elements: **44x44px minimum**
- Buttons: adequate padding (px-4 py-2 minimum)
- Links: adequate padding or margin
- Form inputs: min-height 44px

### Testing Steps:

#### 1. Navigation Elements
```
Test with touch simulation:
1. Enable touch simulation in DevTools (Settings > Devices > Add custom device with touch)
2. Use cursor as touch pointer
```

- [ ] **Sidebar menu button**:
  - Easy to tap (44x44px+)
  - Clear touch feedback
  - No accidental clicks
- [ ] **Sidebar navigation links**:
  - All links easily tappable
  - Adequate spacing between items
  - Visual feedback on touch (hover state)
  - No mis-taps
- [ ] **Header buttons**:
  - Workspace selector dropdown trigger
  - UserMenu avatar button
  - All touch-friendly size

#### 2. Interactive Components

- [ ] **MetricCard**:
  - Card itself not interactive (correct)
  - No accidental actions

- [ ] **API Key Manager**:
  - Copy button: touch-friendly, clear feedback
  - Delete button: touch-friendly, confirmation required
  - Confirmation modal buttons: clearly separated

- [ ] **Form Inputs**:
  - Text inputs: min-height 44px
  - Select dropdowns: easy to open
  - Checkboxes: adequate target size
  - Radio buttons: adequate target size

- [ ] **Buttons**:
  - Primary buttons: full width on mobile or adequate size
  - Secondary buttons: adequate size
  - Icon buttons: 44x44px minimum
  - Clear spacing between adjacent buttons

#### 3. Dropdown Menus

- [ ] **WorkspaceSelector**:
  - Opens on touch/click
  - Menu items touch-friendly
  - Can scroll if many workspaces
  - Closes properly on selection or outside click

- [ ] **Select Dropdowns** (in forms):
  - Open correctly
  - Options easily selectable
  - No accidental selections

#### 4. Scrolling

- [ ] **Page scroll**: Smooth, no janky behavior
- [ ] **Horizontal scroll** (if any): Works properly, clear indicators
- [ ] **Nested scroll**: Activity log or lists scroll independently
- [ ] **Momentum scrolling**: Natural feel on touch devices

---

## Test Flow 5: Orientation Changes

### Testing Steps:

#### 1. Portrait to Landscape (Mobile)
```
1. Use DevTools Device Toolbar
2. Start with iPhone 12 Pro portrait (390x844)
3. Click rotation icon to switch to landscape (844x390)
```

- [ ] Layout adapts immediately
- [ ] Sidebar behavior unchanged (collapses by default)
- [ ] Content reflows properly
- [ ] Grids adjust column count
- [ ] No content cut off
- [ ] Navigation still accessible

#### 2. Landscape to Portrait (Tablet)
```
1. Use iPad Pro portrait (1024x1366)
2. Switch to landscape (1366x1024)
```

- [ ] Layout transitions smoothly
- [ ] Desktop layout appears (sidebar fixed) in landscape
- [ ] Mobile layout appears in portrait if < 1024px
- [ ] Content remains accessible
- [ ] Modals/dialogs reposition correctly

---

## Test Flow 6: Cross-Browser Responsiveness

### Browsers to Test:
- Chrome (primary)
- Safari (iOS devices)
- Firefox
- Edge

### Testing Steps:

#### Chrome (Desktop & DevTools)
- [ ] All responsive features work
- [ ] DevTools Device Toolbar accurate
- [ ] Touch simulation works

#### Safari (iOS)
- [ ] Test on actual iPhone/iPad if possible
- [ ] Sidebar animations smooth
- [ ] Touch interactions work
- [ ] Viewport height correct (100vh issues)
- [ ] Safe areas respected (notch)
- [ ] Form inputs work (no zoom on focus)
  - Verify input font-size ≥ 16px to prevent zoom

#### Firefox
- [ ] Responsive design consistent
- [ ] CSS features supported
- [ ] Animations smooth

#### Edge
- [ ] Layout consistent
- [ ] All features functional

---

## Test Flow 7: Accessibility on Mobile

### Screen Reader Testing (Optional but Recommended)

#### iOS VoiceOver:
```
1. Settings > Accessibility > VoiceOver > On
2. Navigate using swipe gestures
```

- [ ] All interactive elements announced
- [ ] Proper labels for buttons (aria-label)
- [ ] Heading hierarchy correct (h1, h2, h3)
- [ ] Skip navigation available

#### Android TalkBack:
```
1. Settings > Accessibility > TalkBack > On
2. Navigate using swipe gestures
```

- [ ] Similar to VoiceOver checks

### Keyboard Navigation on Desktop
- [ ] Tab through all interactive elements
- [ ] Focus indicators visible
- [ ] Logical tab order
- [ ] Enter/Space activate buttons
- [ ] Escape closes modals

### Color Contrast
- [ ] Text readable on all backgrounds
- [ ] Adequate contrast ratios (WCAG AA)
- [ ] Status indicators distinguishable without color alone

---

## Test Flow 8: Performance on Mobile

### Metrics to Check:

#### Page Load Time:
- [ ] Initial page load < 3 seconds on 3G
- [ ] Fast 3G simulation in DevTools:
  - Network tab > Throttling > Fast 3G

#### Interaction Responsiveness:
- [ ] Button clicks respond < 100ms
- [ ] Navigation changes < 500ms
- [ ] Sidebar animation smooth (60fps)
- [ ] Scroll performance smooth

#### Asset Loading:
- [ ] Images optimized for mobile
- [ ] No large uncompressed images
- [ ] Fonts load quickly
- [ ] Icons render immediately

#### Lighthouse Mobile Audit:
```
1. Open Chrome DevTools
2. Go to Lighthouse tab
3. Select "Mobile" device
4. Run audit on each page
```

- [ ] **Performance Score**: > 90
- [ ] **Accessibility Score**: > 95
- [ ] **Best Practices Score**: > 90
- [ ] **SEO Score**: > 90

#### Key Metrics:
- [ ] First Contentful Paint (FCP): < 1.8s
- [ ] Largest Contentful Paint (LCP): < 2.5s
- [ ] Total Blocking Time (TBT): < 200ms
- [ ] Cumulative Layout Shift (CLS): < 0.1

---

## Common Issues & Troubleshooting

### Issue 1: Horizontal Scroll on Mobile

**Symptoms:**
- Content extends beyond viewport width
- Horizontal scrollbar appears

**Causes:**
- Fixed-width elements (width: 500px)
- Negative margins escaping container
- Absolute positioned elements

**Solutions:**
- Use max-w-full or w-full for containers
- Use responsive width classes (w-screen, w-full)
- Check for hardcoded pixel widths
- Use overflow-x-hidden on body/main

### Issue 2: Sidebar Not Closing

**Symptoms:**
- Sidebar stays open on mobile
- Backdrop click doesn't close sidebar

**Causes:**
- State management issue
- Z-index conflicts
- Event listener not attached

**Solutions:**
- Check isMobileOpen state in Sidebar.tsx
- Verify backdrop onClick handler: `onClick={() => setIsMobileOpen(false)}`
- Ensure backdrop z-index (z-30) is less than sidebar (z-40)

### Issue 3: Buttons Too Small on Mobile

**Symptoms:**
- Difficult to tap buttons
- Accidental mis-taps
- Poor user experience

**Causes:**
- Button padding too small
- Icon buttons without adequate size

**Solutions:**
- Ensure min-height and min-width 44px
- Use p-2 or p-3 for icon buttons
- Use px-4 py-2 minimum for text buttons
- Test with touch simulation

### Issue 4: Text Truncation

**Symptoms:**
- Text cut off with ellipsis
- Content not fully readable

**Causes:**
- Fixed width + overflow-hidden + text-ellipsis
- Single-line text truncation

**Solutions:**
- Remove text-ellipsis on mobile
- Use line-clamp-2 for multi-line truncation
- Allow text to wrap naturally on mobile

### Issue 5: Grid Layout Not Responsive

**Symptoms:**
- Grid doesn't adjust to viewport
- Too many columns on mobile
- Content squished

**Causes:**
- Missing responsive prefixes (md:, lg:)
- Using fixed grid-cols-3 without breakpoints

**Solutions:**
- Use: `grid-cols-1 md:grid-cols-2 lg:grid-cols-3`
- Always start with mobile (grid-cols-1) first
- Add breakpoint prefixes for larger screens

### Issue 6: Forms Not Mobile-Friendly

**Symptoms:**
- Input fields too small
- Labels not visible
- Keyboard overlaps content

**Causes:**
- Inadequate input padding
- Small font sizes
- Fixed positioning conflicts

**Solutions:**
- Input min-height: 44px
- Font size: 16px minimum (prevents zoom on iOS)
- Use padding: px-3 py-2 minimum
- Avoid position: fixed on mobile forms

### Issue 7: Viewport Height Issues

**Symptoms:**
- Content cut off by address bar (mobile browsers)
- min-h-screen doesn't work correctly

**Causes:**
- Mobile browsers have dynamic viewport height
- Address bar shrinks/expands

**Solutions:**
- Use min-h-screen for main containers
- Avoid vh units for critical content
- Consider using CSS env() for safe areas
- Test on actual devices

### Issue 8: Slow Animations on Mobile

**Symptoms:**
- Sidebar animation janky
- Scrolling not smooth
- UI feels sluggish

**Causes:**
- Heavy CSS animations
- Layout thrashing
- Too many concurrent animations

**Solutions:**
- Use transform and opacity for animations (GPU-accelerated)
- Avoid animating width/height/top/left
- Use will-change sparingly
- Reduce transition duration on slower devices

---

## QA Acceptance Checklist

### Layout & Navigation (25 items)

#### Mobile (< 768px):
- [ ] Sidebar hidden by default
- [ ] Mobile menu button visible and functional
- [ ] Sidebar slides in smoothly on button click
- [ ] Backdrop overlay appears and closes sidebar on click
- [ ] X button closes sidebar
- [ ] Header displays workspace selector on left
- [ ] UserMenu displays on right
- [ ] Content uses full width (no sidebar offset)
- [ ] Content padding: p-4
- [ ] No horizontal overflow

#### Tablet (768px - 1023px):
- [ ] Sidebar still collapsible (mobile behavior)
- [ ] Grids expand to 2 columns (md:grid-cols-2)
- [ ] Content padding increases: p-6
- [ ] Workspace selector visible
- [ ] All navigation functional

#### Desktop (1024px+):
- [ ] Sidebar permanently visible (w-64, 256px)
- [ ] No mobile menu button
- [ ] Main content offset by sidebar (lg:pl-64)
- [ ] Grids expand to 3 columns (lg:grid-cols-3)
- [ ] Workspace selector on right in header
- [ ] All spacing proportional and consistent

### Component Responsiveness (30 items)

#### MetricCard:
- [ ] Mobile: Single column, full width, readable
- [ ] Tablet: 2-column grid
- [ ] Desktop: 3-column grid
- [ ] Loading states display correctly on all viewports
- [ ] Icons visible, trends color-coded
- [ ] Touch targets adequate size

#### KPIOverview:
- [ ] Mobile: 6 cards stack vertically
- [ ] Tablet: 2x3 grid
- [ ] Desktop: 3x2 grid
- [ ] Consistent spacing (gap-4)
- [ ] All metrics visible and readable

#### SystemHealthDashboard:
- [ ] Mobile: Single column layout
- [ ] Tablet: 2-column service grid
- [ ] Desktop: 3-column service grid
- [ ] Overall status card full width on mobile
- [ ] Refresh button accessible
- [ ] Activity log displays properly
- [ ] Real-time updates work without layout shift

#### ConfigurationDashboard:
- [ ] Mobile: Tabs horizontal with scroll if needed
- [ ] Forms display in single column on mobile
- [ ] Input fields full width on mobile
- [ ] Buttons touch-friendly (min 44x44px)
- [ ] Service selector responsive
- [ ] Validation errors display correctly

#### ApiKeyManager:
- [ ] Mobile: List items stack vertically
- [ ] Copy button accessible and functional
- [ ] Delete confirmation dialog centered
- [ ] Masked values readable
- [ ] Empty state displays correctly

#### WorkspaceSelector:
- [ ] Dropdown positioned correctly (not off-screen)
- [ ] Touch-friendly menu items
- [ ] Avatars display correctly
- [ ] Active workspace indicated
- [ ] Scrollable if many workspaces

### Page-Specific Tests (25 items)

#### Dashboard Page (/):
- [ ] Mobile: All sections stack vertically
- [ ] Tablet: KPI grid 2 columns
- [ ] Desktop: KPI grid 3 columns
- [ ] Page header visible and readable
- [ ] Loading demo functional
- [ ] No horizontal overflow

#### System Health Page (/health):
- [ ] Mobile: Service cards stack vertically
- [ ] Tablet: Service cards 2 columns
- [ ] Desktop: Service cards 3 columns
- [ ] Overall status card displays correctly
- [ ] Activity log readable on all viewports
- [ ] Real-time polling works
- [ ] Refresh button accessible

#### Configuration Page (/config):
- [ ] Mobile: All tabs accessible
- [ ] Mobile: API key items readable
- [ ] Mobile: Forms full width, inputs touch-friendly
- [ ] Tablet: Better form layout
- [ ] Desktop: Optimal form width
- [ ] All three tabs functional (API Keys, Services, Workspace)
- [ ] Form validation displays correctly
- [ ] Save buttons accessible

#### Analytics Page (/analytics):
- [ ] Mobile: Placeholder content readable
- [ ] Tablet: Grid layouts expand
- [ ] Desktop: Charts display optimally

### Touch Interaction (15 items)

- [ ] All buttons min 44x44px touch targets
- [ ] Adequate spacing between interactive elements
- [ ] Clear visual feedback on touch
- [ ] No accidental taps or mis-clicks
- [ ] Sidebar navigation links easily tappable
- [ ] Form inputs adequate height (min 44px)
- [ ] Dropdowns open correctly on touch
- [ ] Modals/dialogs accessible on touch
- [ ] Scrolling smooth and natural
- [ ] Copy buttons provide clear feedback
- [ ] Delete confirmations require explicit action
- [ ] Tab navigation works on touch devices
- [ ] Workspace selector dropdown functional
- [ ] UserMenu accessible
- [ ] No touch interaction conflicts

### Orientation Changes (5 items)

- [ ] Portrait to landscape adapts immediately
- [ ] Landscape to portrait adapts immediately
- [ ] No content cut off during orientation change
- [ ] Layout remains functional in both orientations
- [ ] Sidebar behavior consistent

### Cross-Browser (10 items)

- [ ] Chrome: All features work
- [ ] Safari (iOS): No zoom on input focus (font-size ≥ 16px)
- [ ] Safari (iOS): Safe areas respected
- [ ] Safari (iOS): Viewport height correct
- [ ] Safari (iOS): Animations smooth
- [ ] Firefox: Layout consistent
- [ ] Edge: All features functional
- [ ] All browsers: No horizontal overflow
- [ ] All browsers: Touch interactions work
- [ ] All browsers: Responsive breakpoints trigger correctly

### Performance (10 items)

- [ ] Page load < 3 seconds on Fast 3G
- [ ] Button clicks respond < 100ms
- [ ] Navigation changes < 500ms
- [ ] Sidebar animation smooth (60fps)
- [ ] Scroll performance smooth
- [ ] Lighthouse Mobile Performance > 90
- [ ] Lighthouse Accessibility > 95
- [ ] First Contentful Paint < 1.8s
- [ ] Largest Contentful Paint < 2.5s
- [ ] Cumulative Layout Shift < 0.1

### Accessibility (10 items)

- [ ] All interactive elements have labels
- [ ] Heading hierarchy correct
- [ ] Focus indicators visible
- [ ] Keyboard navigation works
- [ ] Color contrast adequate (WCAG AA)
- [ ] Touch targets meet minimum size
- [ ] Error messages associated with fields
- [ ] Form fields have labels
- [ ] Modals trap focus correctly
- [ ] Skip navigation available (if implemented)

---

## Summary

**Total Checklist Items**: 130+

### Testing Priority:

1. **Critical (Must Pass)**:
   - Layout responsiveness on all 3 viewports
   - Sidebar collapse/expand functionality
   - Touch target sizes
   - No horizontal overflow
   - Navigation works on all devices

2. **High (Should Pass)**:
   - All components responsive
   - Touch interactions smooth
   - Performance metrics acceptable
   - Cross-browser consistency

3. **Medium (Nice to Have)**:
   - Orientation changes
   - Advanced touch gestures
   - Lighthouse perfect scores

### Estimated Testing Time:
- **Quick Pass**: 30 minutes (critical items only)
- **Thorough Test**: 2-3 hours (all items)
- **Complete Audit**: 4-5 hours (includes real device testing, accessibility)

---

## Reporting Issues

When reporting mobile responsiveness issues, include:

1. **Device/Viewport**: Specific width and height
2. **Browser**: Chrome, Safari, Firefox, etc.
3. **Page/Component**: Which page or component has the issue
4. **Expected Behavior**: What should happen
5. **Actual Behavior**: What actually happens
6. **Screenshots**: Visual evidence of the issue
7. **Steps to Reproduce**: Clear step-by-step instructions

### Example Issue Report:

```
Title: Sidebar doesn't close on backdrop click on mobile

Device: iPhone 12 Pro (390px width)
Browser: Safari iOS 16
Page: Dashboard (/)
Breakpoint: Mobile (< 768px)

Expected Behavior:
When sidebar is open, clicking the dark backdrop should close the sidebar.

Actual Behavior:
Clicking the backdrop does nothing. Sidebar remains open.

Steps to Reproduce:
1. Open http://localhost:3000 on iPhone 12 Pro
2. Tap the hamburger menu button (top-left)
3. Sidebar slides in with backdrop
4. Tap anywhere on the dark backdrop
5. Sidebar does not close

Screenshot: [attached]

Additional Info:
X button does work to close sidebar. Only backdrop click is broken.
```

---

## Next Steps After Verification

Once mobile responsiveness testing is complete:

1. **Document all issues** found during testing
2. **Prioritize fixes** based on severity and user impact
3. **Implement fixes** for critical issues
4. **Re-test** after fixes applied
5. **Sign off** on mobile responsiveness when all critical issues resolved
6. **Proceed to subtask-8-5**: Performance and accessibility audit

---

## References

- Tailwind CSS Responsive Design: https://tailwindcss.com/docs/responsive-design
- Touch Target Sizes: https://web.dev/accessible-tap-targets/
- Mobile-First Design: https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps/Responsive/Mobile_first
- Chrome DevTools Device Mode: https://developer.chrome.com/docs/devtools/device-mode/

---

**Document Version**: 1.0
**Last Updated**: 2026-02-26
**Status**: Ready for QA Testing
