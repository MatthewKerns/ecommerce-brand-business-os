# Health Check API - Verification Guide

## Overview

The health check API endpoint provides comprehensive system health monitoring for all organic marketing components.

## Files Created

### 1. `dashboard/src/lib/health-checker.ts`
- **Purpose**: Library for checking system component health
- **Exports**:
  - `checkSystemHealth()`: Returns comprehensive health report for all services
  - `checkServiceHealth(serviceName)`: Returns health for a specific service
  - TypeScript types: `HealthStatus`, `ServiceHealth`, `SystemHealth`

### 2. `dashboard/src/app/api/health/route.ts`
- **Purpose**: Next.js API route for health checks
- **Endpoint**: `GET /api/health`
- **Features**:
  - Returns overall system health status
  - Supports `?service=name` query parameter for specific service checks
  - Returns 200 for healthy/degraded, 503 for unhealthy
  - No-cache headers for real-time data

## Components Checked

The health checker monitors 7 system components:

1. **Environment** - Verifies required environment variables (Clerk keys)
2. **TikTok API** - Checks TikTok API service status
3. **Blog Engine** - Verifies blog generation service
4. **Email Automation** - Checks email service status
5. **Python Agents** - Verifies AI content agents are operational
6. **Database** - Checks database connection health
7. **Cache** - Verifies cache service (Redis/memory)

## API Response Format

### Overall System Health
```json
{
  "status": "healthy",
  "timestamp": "2024-02-26T06:50:00.000Z",
  "services": [
    {
      "name": "Environment",
      "status": "healthy",
      "message": "All required environment variables are set",
      "lastCheck": "2024-02-26T06:50:00.000Z",
      "uptime": 100
    },
    // ... more services
  ],
  "summary": {
    "total": 7,
    "healthy": 6,
    "degraded": 1,
    "unhealthy": 0
  }
}
```

### Single Service Health
```json
{
  "service": {
    "name": "TikTok API",
    "status": "healthy",
    "message": "Service operational",
    "lastCheck": "2024-02-26T06:50:00.000Z",
    "uptime": 99.9,
    "responseTime": 120
  },
  "timestamp": "2024-02-26T06:50:00.000Z"
}
```

## Verification Steps

### 1. Install Dependencies
```bash
cd dashboard
npm install
```

### 2. Set Environment Variables
Create `.env.local` file:
```bash
cp .env.local.example .env.local
# Edit .env.local with your Clerk keys
```

### 3. Start Development Server
```bash
npm run dev
```

### 4. Test Overall Health Check
```bash
curl -X GET http://localhost:3000/api/health -H "Content-Type: application/json"
```

Expected response: Status 200 with JSON containing all service statuses.

### 5. Test Specific Service Check
```bash
curl -X GET "http://localhost:3000/api/health?service=tiktok" -H "Content-Type: application/json"
```

Expected response: Status 200 with JSON containing TikTok API service status.

### 6. Test Unknown Service
```bash
curl -X GET "http://localhost:3000/api/health?service=unknown" -H "Content-Type: application/json"
```

Expected response: Status 503 with unhealthy status for unknown service.

### 7. Browser Testing
Open browser to:
- http://localhost:3000/api/health

Should display JSON response with system health.

## Integration with Frontend

The health check API is designed to integrate with the SystemHealthDashboard component:

1. **Current State**: SystemHealthDashboard uses `useHealthMonitor` hook with simulated data
2. **Future Integration**: Update `useHealthMonitor` to fetch from `/api/health`:

```typescript
// In dashboard/src/hooks/useHealthMonitor.ts
const fetchHealthData = async (): Promise<ServiceHealth[]> => {
  const response = await fetch('/api/health')
  const data = await response.json()
  return data.services
}
```

3. **Real-time Polling**: The hook already supports 30-second polling intervals

## Next Steps

1. **Replace Simulated Checks**: Update health-checker.ts functions to call real service endpoints
2. **Add Authentication**: Integrate Clerk authentication for API endpoint (Phase 7, subtask-7-4)
3. **Connect Frontend**: Update useHealthMonitor hook to use /api/health endpoint
4. **Add Metrics**: Include performance metrics (response time, uptime %) in service checks
5. **Alerting**: Add webhook notifications for service degradation/failures

## Pattern Compliance

✅ **Follows Python test_setup.py pattern**:
- Multiple component checks (imports → services, API keys → environment, etc.)
- Clear status indicators (healthy/degraded/unhealthy vs ✅/⚠️/❌)
- Comprehensive error handling
- Detailed status messages

✅ **Follows Dashboard patterns**:
- TypeScript with proper interfaces
- Comprehensive JSDoc documentation
- Proper error boundaries
- Next.js App Router conventions

## Troubleshooting

### Issue: Environment check fails
**Solution**: Ensure `.env.local` file exists with required Clerk keys

### Issue: All services show degraded/unhealthy
**Solution**: This is expected - services use simulated checks. Replace with real service endpoints.

### Issue: API returns 404
**Solution**: Verify Next.js dev server is running and route file exists at `src/app/api/health/route.ts`

### Issue: CORS errors in browser
**Solution**: Health API is on same domain as dashboard, no CORS needed. Check if dev server is running.

## Commit Reference

Git commit: `ed89863`
- Created health-checker.ts library
- Created /api/health route
- Updated implementation_plan.json
