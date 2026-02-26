# Health Monitor Real-Time Polling Verification

This document provides instructions for manually verifying the real-time health monitoring feature with automatic 30-second polling.

## Feature Overview

The `useHealthMonitor` hook now provides:
- Automatic health status polling every 30 seconds
- Real-time service status updates
- Manual refresh capability
- Loading states during updates
- Error handling and retry

## Files Modified/Created

### Created:
- `dashboard/src/hooks/useHealthMonitor.ts` - Custom hook for health monitoring with polling

### Modified:
- `dashboard/src/components/SystemHealthDashboard.tsx` - Updated to use the polling hook

## Verification Steps

### 1. Initial Load
1. Start the development server:
   ```bash
   cd dashboard
   npm install
   npm run dev
   ```

2. Navigate to: `http://localhost:3000/health`

3. **Expected Behavior:**
   - Page shows loading state initially
   - After ~500ms, service status cards appear
   - All services display with current timestamps
   - Overall status indicator shows green (healthy) or yellow (warning)

### 2. Real-Time Polling (30-second updates)
1. Keep the health page open
2. Watch the "Last Check" timestamps on the service cards
3. Wait for 30 seconds

4. **Expected Behavior:**
   - After 30 seconds, you should see:
     - All "Last Check" timestamps update to current time
     - Brief loading state (spinning refresh icon)
     - Possible status changes (5% chance of degraded status)
     - Possible uptime percentage changes (slight variations)

5. **Verification:**
   - Open browser console (F12)
   - Watch for network activity or state updates every 30 seconds
   - No errors should appear in the console
   - The refresh icon should spin briefly every 30 seconds

### 3. Manual Refresh
1. Click the refresh icon (↻) in the top right of the "Overall Status" card

2. **Expected Behavior:**
   - Refresh icon spins immediately
   - Loading state activates
   - Service data updates within ~500ms
   - All timestamps update to current time
   - Polling timer resets (next auto-update in 30 seconds)

### 4. Status Changes Simulation
The hook randomly simulates status changes to demonstrate real-time updates:
- 5% chance of "degraded" status
- 2% chance of "down" status
- 93% chance of "up" status

1. Keep page open for 2-3 minutes
2. Watch for status badges to change from green to yellow (degraded) or red (down)
3. Error messages may appear when status is degraded/down

4. **Expected Behavior:**
   - Status badge colors change dynamically
   - Overall status indicator reflects changes
   - Error messages appear/disappear appropriately

### 5. Multiple Windows Test
1. Open the health page in two browser windows side-by-side
2. Wait for polling updates

3. **Expected Behavior:**
   - Both windows update independently
   - Updates may not be synchronized (slight timing differences)
   - Each window maintains its own 30-second interval

### 6. Error Handling (Manual Test)
To test error handling, you can temporarily modify the `fetchHealthData` function:

1. Edit `dashboard/src/hooks/useHealthMonitor.ts`
2. Temporarily add `throw new Error("Simulated error");` at the start of `fetchHealthData`
3. Reload the page

4. **Expected Behavior:**
   - Error state displays with red background
   - Error message: "Simulated error"
   - "Retry" button appears
   - Clicking retry attempts to fetch data again

5. **Cleanup:** Remove the error simulation code

### 7. Performance Check
1. Open browser DevTools → Performance tab
2. Record for 60 seconds (covering 2 polling cycles)
3. Stop recording

4. **Expected Behavior:**
   - No memory leaks
   - Clean interval cleanup on unmount
   - Minimal CPU usage between polls
   - Brief activity spikes every 30 seconds

## Acceptance Criteria Checklist

- [ ] Health status updates every 30 seconds automatically
- [ ] Initial load displays service data correctly
- [ ] Manual refresh button works and resets timer
- [ ] Loading states appear during updates
- [ ] Status changes are reflected in real-time
- [ ] Overall status indicator updates based on service statuses
- [ ] No console errors during normal operation
- [ ] Polling stops when component unmounts
- [ ] Multiple instances poll independently
- [ ] Error states display correctly with retry option

## Technical Details

### Polling Implementation
- **Interval:** 30,000ms (30 seconds)
- **Initial Fetch:** Immediate on component mount
- **Cleanup:** `clearInterval` on component unmount
- **API Simulation:** 200-500ms latency

### Service Status Simulation
- **Default State:** All services "up"
- **Random Changes:** Applied on each poll
- **Uptime Variation:** ±0.05% per poll
- **Timestamp:** Updated to current time on each poll

### Hook Configuration
```typescript
useHealthMonitor({
  pollingInterval: 30000, // Default: 30 seconds
  enabled: true,           // Default: enabled
})
```

## Troubleshooting

### Polling Not Working
- Check browser console for errors
- Verify no JavaScript errors blocking execution
- Check Network tab for simulated API calls
- Ensure component is properly mounted

### Status Not Updating
- Verify timestamps are changing (proves polling works)
- Check that services array is not empty
- Confirm `isLoading` state toggles during polls

### Memory Leaks
- Verify `clearInterval` is called on unmount
- Check DevTools Memory tab for growing heap
- Ensure no lingering intervals after navigation

## Notes

- Current implementation uses simulated data (no real backend yet)
- When integrated with `/api/health` endpoint, replace `fetchHealthData` function
- Polling interval can be customized via component prop
- Consider using SWR or React Query for production implementation
