# End-to-End Verification: Customer Profile Sync Flow

This document describes the end-to-end verification for the Klaviyo customer profile sync flow (subtask-5-3).

## Overview

The verification tests the complete flow of syncing customer profiles from TikTok Shop to Klaviyo:

1. ✅ Start FastAPI server
2. ✅ Call POST `/api/klaviyo/sync/profiles` to sync customer profiles
3. ✅ Verify profiles are created in database
4. ✅ Verify sync history is recorded
5. ✅ Check API returns success response

## New Endpoints Added

### 1. POST /api/klaviyo/sync/profiles

Syncs customer profiles from TikTok Shop to Klaviyo.

**Request:**
```json
{
  "use_mock_data": true,
  "page_size": 10,
  "max_pages": 1
}
```

**Response:**
```json
{
  "request_id": "req_abc123",
  "profiles_synced": 3,
  "stats": {
    "orders_fetched": 3,
    "customers_found": 3,
    "customers_synced": 3,
    "customers_created": 3,
    "customers_updated": 0,
    "errors": 0
  },
  "status": "success",
  "message": "Successfully synced 3 customer profiles from TikTok Shop",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### 2. POST /api/klaviyo/sync/events

Syncs order events from TikTok Shop to Klaviyo.

**Request:**
```json
{
  "use_mock_data": true,
  "page_size": 10,
  "max_pages": 1
}
```

**Response:**
```json
{
  "request_id": "req_abc123",
  "events_tracked": 3,
  "stats": {
    "orders_fetched": 3,
    "events_tracked": 3,
    "events_failed": 0,
    "total_value": 269.97
  },
  "status": "success",
  "message": "Successfully tracked 3 order events in Klaviyo",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## Mock Data Mode

Both endpoints support `use_mock_data: true` for testing without requiring:
- Real TikTok Shop API credentials
- Real Klaviyo API credentials
- Actual order data

When `use_mock_data` is enabled:
- Test profiles/events are created directly in the database
- No external API calls are made
- Sync history is still tracked normally
- All verification steps can be completed

## Running the Verification

### Option 1: Automated Test Runner (Recommended)

```bash
cd claude-code-os-implementation/03-ai-growth-engine/organic-marketing-package/content-agents
./tests/run_e2e_verification.sh
```

This script will:
1. Check/run database migration
2. Start FastAPI server (if not already running)
3. Run all verification steps
4. Clean up test data
5. Stop server (if it started one)

### Option 2: Manual Verification

#### Step 1: Set up database

```bash
cd claude-code-os-implementation/03-ai-growth-engine/organic-marketing-package/content-agents
python database/migrations/add_klaviyo_models.py
```

#### Step 2: Start server

```bash
uvicorn api.main:app --reload
```

#### Step 3: Run verification script

In a new terminal:

```bash
cd claude-code-os-implementation/03-ai-growth-engine/organic-marketing-package/content-agents
python tests/verify_e2e_profile_sync.py
```

#### Step 4: Check results

The script will output:
- ✅ for each successful verification step
- ❌ for any failures
- Final summary with pass/fail status

### Option 3: Manual API Testing with curl

#### Test profile sync:

```bash
curl -X POST http://localhost:8000/api/klaviyo/sync/profiles \
  -H "Content-Type: application/json" \
  -d '{
    "use_mock_data": true,
    "page_size": 10
  }'
```

#### Test event sync:

```bash
curl -X POST http://localhost:8000/api/klaviyo/sync/events \
  -H "Content-Type: application/json" \
  -d '{
    "use_mock_data": true,
    "page_size": 10
  }'
```

#### Verify in database:

```bash
# Connect to database and check
sqlite3 content_agents.db  # or your database file

# Check profiles
SELECT COUNT(*) FROM klaviyo_profiles WHERE email LIKE 'test%@example.com';

# Check sync history
SELECT * FROM klaviyo_sync_history ORDER BY created_at DESC LIMIT 5;
```

## Verification Checklist

The verification script checks:

- [x] **Server Health**: FastAPI server responds to /health endpoint
- [x] **Endpoint Availability**: POST /api/klaviyo/sync/profiles endpoint exists
- [x] **Request Processing**: Endpoint accepts valid requests
- [x] **Response Structure**: Response contains all required fields
- [x] **Response Status**: API returns 200 status code
- [x] **Success Message**: Response indicates successful sync
- [x] **Database Profiles**: Profiles are created in klaviyo_profiles table
- [x] **Profile Data**: Profiles contain required fields (email, first_name, etc.)
- [x] **Sync History**: Sync operations are recorded in klaviyo_sync_history table
- [x] **History Data**: Sync history contains correct stats and metadata

## Expected Output

```
======================================================================
🔍 Starting End-to-End Verification: Customer Profile Sync Flow
======================================================================

Step 1: Verifying FastAPI server is running...
✅ FastAPI server is running

Step 2: Calling POST /api/klaviyo/sync/profiles endpoint...
✅ Sync profiles endpoint worked: 3 profiles synced

Step 3: Verifying profiles were created in database...
✅ Found 3 profiles in database with correct data

Step 4: Verifying sync history was recorded...
✅ Found 5 sync history records, latest processed 3 records

Step 5: Verifying API response structure...
✅ API returned success response with all required fields

Cleaning up test data...
🧹 Cleaned up test data

======================================================================
📊 Verification Summary
======================================================================
✅ Successful checks: 5
❌ Failed checks: 0

✅ ALL VERIFICATIONS PASSED!

🎉 End-to-end customer profile sync flow is working correctly!
```

## Troubleshooting

### Server won't start

**Error**: `Cannot connect to server`

**Solution**: Check if port 8000 is available:
```bash
lsof -i :8000  # Check what's using port 8000
kill <PID>     # Kill if needed
```

### Database tables don't exist

**Error**: `no such table: klaviyo_profiles`

**Solution**: Run the migration:
```bash
python database/migrations/add_klaviyo_models.py
```

### Import errors

**Error**: `ModuleNotFoundError`

**Solution**: Install dependencies:
```bash
pip install -r requirements.txt
```

### Python command not found

**Error**: `python: command not found`

**Solution**: Use python3:
```bash
python3 tests/verify_e2e_profile_sync.py
```

## Order Event Tracking Verification (Subtask 5-4)

Subtask 5-4 focuses specifically on verifying the order event tracking flow. A dedicated verification script has been created to test:

1. ✅ Single event tracking via POST `/api/klaviyo/events`
2. ✅ Event validation and error handling
3. ✅ Bulk event sync via POST `/api/klaviyo/sync/events`
4. ✅ Sync history tracking for events

### Running Event Tracking Verification

#### Automated Test Runner:

```bash
cd claude-code-os-implementation/03-ai-growth-engine/organic-marketing-package/content-agents
./tests/run_e2e_event_tracking.sh
```

#### Manual Python Script:

```bash
cd claude-code-os-implementation/03-ai-growth-engine/organic-marketing-package/content-agents
python tests/verify_e2e_event_tracking.py
```

### Event Tracking Endpoint

#### POST /api/klaviyo/events

Tracks a single customer event in Klaviyo.

**Request:**
```json
{
  "metric_name": "Placed Order",
  "customer_email": "customer@example.com",
  "customer_phone": "+1234567890",
  "properties": {
    "order_id": "ORD-12345",
    "total": 299.98,
    "currency": "USD",
    "items": [
      {
        "product_id": "PROD-001",
        "name": "Tactical Backpack",
        "price": 149.99,
        "quantity": 1
      }
    ]
  }
}
```

**Response:**
```json
{
  "request_id": "req_xyz789",
  "event_id": "evt_abc123",
  "metric_name": "Placed Order",
  "status": "success",
  "message": "Event tracked successfully",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Event Tracking Verification Checklist

The event tracking verification script checks:

- [x] **Server Health**: FastAPI server is running
- [x] **Single Event Tracking**: POST /api/klaviyo/events endpoint works
- [x] **Event Response**: Response contains required fields (event_id, metric_name, status)
- [x] **Error Handling - Missing Fields**: Returns 422 for missing customer identifier
- [x] **Error Handling - Invalid Email**: Returns 422 for invalid email format
- [x] **Error Handling - Empty Metric**: Returns 422 for empty metric name
- [x] **Bulk Event Sync**: POST /api/klaviyo/sync/events endpoint works
- [x] **Sync History**: Event sync operations recorded in database

### Expected Output (Event Tracking)

```
======================================================================
🔍 Starting End-to-End Verification: Order Event Tracking Flow
======================================================================

Step 1: Verifying FastAPI server is running...
✅ FastAPI server is running

Step 2: Calling POST /api/klaviyo/events to track an order event...
✅ Event tracking endpoint worked: 'Placed Order' event tracked

Step 3: Verifying proper error handling for invalid data...
✅ Error handling works for: Missing required fields (status 422)
✅ Error handling works for: Invalid email format (status 422)
✅ Error handling works for: Empty metric name (status 422)

Step 4: Checking sync history database access...
✅ Sync history query works (single events may not create sync records)

Step 5: Testing bulk event sync endpoint...
✅ Bulk event sync endpoint worked: 5 events tracked

Step 6: Verifying bulk sync history was recorded...
✅ Found 3 sync history records, latest processed 5 records

======================================================================
📊 Verification Summary
======================================================================
✅ Successful checks: 9
❌ Failed checks: 0

✅ ALL VERIFICATIONS PASSED!

🎉 End-to-end order event tracking flow is working correctly!

Verified capabilities:
  • Single event tracking via POST /api/klaviyo/events
  • Bulk event sync via POST /api/klaviyo/sync/events
  • Error handling for invalid data
  • Sync history tracking in database
```

## Files Created/Modified

### Created (Subtask 5-3):
- `api/routes/klaviyo.py`: Added sync endpoints (POST /sync/profiles, POST /sync/events)
- `tests/verify_e2e_profile_sync.py`: Automated verification script for profile sync
- `tests/run_e2e_verification.sh`: Shell script test runner for profile sync
- `tests/E2E_VERIFICATION.md`: This documentation

### Created (Subtask 5-4):
- `tests/verify_e2e_event_tracking.py`: Automated verification script for event tracking
- `tests/run_e2e_event_tracking.sh`: Shell script test runner for event tracking

### Modified:
- `api/routes/klaviyo.py`:
  - Added KlaviyoSyncService import
  - Added SyncProfilesRequest, SyncProfilesResponse models
  - Added SyncEventsRequest, SyncEventsResponse models
  - Added sync_profiles_from_tiktok endpoint
  - Added sync_events_from_tiktok endpoint
  - ~483 lines added

## Next Steps

After this verification passes:
1. Proceed to subtask-5-4: End-to-end verification for order event tracking
2. Complete subtask-5-5: Documentation (README for Klaviyo integration)
3. Run full test suite
4. Final QA verification

## Success Criteria

All verification steps must pass:
1. ✅ Server starts successfully
2. ✅ Endpoint responds correctly
3. ✅ Profiles created in database
4. ✅ Sync history recorded
5. ✅ API returns success response

When all checks pass, the subtask can be marked as completed.
