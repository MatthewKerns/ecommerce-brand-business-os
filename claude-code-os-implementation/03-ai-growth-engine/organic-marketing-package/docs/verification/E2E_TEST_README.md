# End-to-End Test for TikTok Scheduling & Auto-Publishing

This document describes how to run the end-to-end verification test for the TikTok content scheduling and auto-publishing feature.

## Overview

The E2E test verifies the complete workflow:

1. **Schedule Content** - POST to `/api/tiktok/schedule` with content scheduled 1 minute in the future
2. **Wait for Execution** - Scheduler service detects due content and publishes it
3. **Verify Published Status** - Content status changes to 'published'
4. **Verify TikTok Video ID** - TikTok video/post ID is populated
5. **Verify Publish Log** - PublishLog table has successful attempt record
6. **Verify Database State** - All database fields are correctly updated

## Prerequisites

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set Up Mock TikTok Client**

   The E2E test uses a mock TikTok client to avoid making real API calls. To enable the mock:

   **Option A: Environment Variable (Recommended)**
   ```bash
   export USE_MOCK_TIKTOK_CLIENT=true
   ```

   **Option B: Modify services/publishing_service.py**
   ```python
   # At the top of the file, add:
   import os
   from tests.mocks.mock_tiktok_client import MockTikTokShopClient

   # In PublishingService.__init__, replace the TikTokShopClient instantiation:
   if os.getenv('USE_MOCK_TIKTOK_CLIENT') == 'true':
       self.tiktok_client = MockTikTokShopClient()
   else:
       self.tiktok_client = TikTokShopClient(...)
   ```

3. **Initialize Database**
   ```bash
   python database/init_db.py
   ```

## Running the Test

### Method 1: Direct Script Execution

```bash
cd content-agents
export USE_MOCK_TIKTOK_CLIENT=true
python tests/test_e2e_scheduling.py
```

### Method 2: With pytest

```bash
cd content-agents
export USE_MOCK_TIKTOK_CLIENT=true
pytest tests/test_e2e_scheduling.py -v -s
```

## Expected Output

```
================================================================================
STARTING END-TO-END TEST: TikTok Scheduling & Auto-Publishing
================================================================================
2024-01-15 10:30:00 - INFO - Starting API server...
2024-01-15 10:30:05 - INFO - API server started successfully
2024-01-15 10:30:05 - INFO - Starting scheduler service...
2024-01-15 10:30:10 - INFO - Scheduler service started successfully
2024-01-15 10:30:10 - INFO - Scheduling test content...
2024-01-15 10:30:11 - INFO - Content scheduled successfully with ID: 1
2024-01-15 10:30:11 - INFO - Scheduled time: 2024-01-15T10:31:11Z
2024-01-15 10:30:11 - INFO - Waiting 130 seconds for scheduler to execute...
2024-01-15 10:30:11 - INFO - Time remaining: 130 seconds
2024-01-15 10:30:26 - INFO - Time remaining: 115 seconds
...
2024-01-15 10:32:21 - INFO - Verifying published status for content ID: 1
2024-01-15 10:32:21 - INFO - ✓ Status: published
2024-01-15 10:32:21 - INFO - ✓ TikTok Video ID: mock_post_abc123def456
2024-01-15 10:32:21 - INFO - ✓ Published at: 2024-01-15T10:31:15Z
2024-01-15 10:32:21 - INFO - ✓ API verification passed
2024-01-15 10:32:21 - INFO - Verifying database state for content ID: 1
2024-01-15 10:32:21 - INFO - ✓ DB Status: published
2024-01-15 10:32:21 - INFO - ✓ DB TikTok Video ID: mock_post_abc123def456
2024-01-15 10:32:21 - INFO - ✓ DB Published at: 2024-01-15T10:31:15Z
2024-01-15 10:32:21 - INFO - ✓ PublishLog records: 1
2024-01-15 10:32:21 - INFO - ✓ Successful attempt: #1
2024-01-15 10:32:21 - INFO - ✓ Database verification passed
================================================================================
✓ END-TO-END TEST PASSED SUCCESSFULLY
================================================================================
```

## Test Duration

- **Total time**: ~2-3 minutes
  - API server startup: ~5 seconds
  - Scheduler service startup: ~5 seconds
  - Scheduler execution wait: ~130 seconds (to ensure content is due + executed)
  - Verification: ~1 second
  - Service shutdown: ~5 seconds

## Troubleshooting

### API Server Won't Start

- Check if port 8000 is already in use: `lsof -i :8000`
- Kill existing process: `kill -9 <PID>`
- Check logs in test output for specific error

### Scheduler Service Won't Start

- Verify APScheduler is installed: `pip show APScheduler`
- Check database connection is working
- Verify scheduler/scheduler_service.py exists

### Content Not Published After Wait

- Check scheduler logs for errors
- Verify database has the scheduled content record
- Check TikTok client mock is enabled
- Manually check scheduled_time is in the past after waiting

### Database Errors

- Reinitialize database: `python database/init_db.py`
- Check PostgreSQL is running (if using PostgreSQL)
- Verify database connection string in config

## Manual Verification Steps

If the automated test fails, you can manually verify each step:

1. **Start API Server**
   ```bash
   uvicorn api.main:app --host 0.0.0.0 --port 8000
   ```

2. **Start Scheduler Service (in another terminal)**
   ```bash
   export USE_MOCK_TIKTOK_CLIENT=true
   python scheduler/scheduler_service.py
   ```

3. **Schedule Content (in another terminal)**
   ```bash
   curl -X POST http://localhost:8000/api/tiktok/schedule \
     -H "Content-Type: application/json" \
     -d '{
       "content_type": "post",
       "content_data": {
         "content": "Test post",
         "product_ids": [],
         "tags": ["test"]
       },
       "scheduled_time": "2024-01-15T10:31:00Z",
       "max_retries": 3
     }'
   ```

4. **Wait 2 Minutes**

5. **Check Status**
   ```bash
   curl http://localhost:8000/api/tiktok/schedule/1
   ```

6. **Verify Database**
   ```bash
   python -c "
   from database.connection import get_db_session
   from database.models import ScheduledContent, PublishLog

   db = get_db_session()
   content = db.query(ScheduledContent).first()
   print(f'Status: {content.status}')
   print(f'TikTok ID: {content.tiktok_video_id}')

   logs = db.query(PublishLog).all()
   print(f'Publish attempts: {len(logs)}')
   "
   ```

## Success Criteria

The test passes if:

- ✅ API server starts successfully
- ✅ Scheduler service starts successfully
- ✅ Content is scheduled via API (returns 201)
- ✅ After waiting, content status is 'published'
- ✅ tiktok_video_id is populated (starts with 'mock_post_' or 'mock_video_')
- ✅ published_at timestamp is set
- ✅ PublishLog has at least one successful attempt record
- ✅ Both services stop gracefully

## Next Steps

After successful E2E testing:

1. **Production Setup**: Replace mock client with real TikTok Shop credentials
2. **Monitoring**: Set up alerts for failed publishes
3. **Scaling**: Consider running multiple scheduler instances with leader election
4. **Logging**: Configure centralized logging for production monitoring
5. **Deployment**: Deploy API and scheduler as separate services
