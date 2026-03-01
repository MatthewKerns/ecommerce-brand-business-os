# End-to-End Workflow Verification Guide

## Overview

This document describes the complete end-to-end workflow verification for the AI Content Agent Integration feature, specifically testing:

1. Human review workflow
2. Content generation queue with priorities
3. Content versioning/revision system

## Test Workflow

The complete workflow tests the following sequence:

```
Async Generation → Draft Creation → Review Submission → Approval → Versioning
```

## Prerequisites

### 1. Services Required

- **PostgreSQL Database** (or SQLite for development)
- **Redis Server** (for Celery broker/backend)
- **FastAPI Server** (content-engine API)
- **Celery Worker** (with content generation queues)

### 2. Environment Setup

```bash
# Navigate to content-engine directory
cd claude-code-os-implementation/03-ai-growth-engine/organic-marketing-package/packages/content-engine

# Ensure .env file exists with required configuration
cp .env.example .env

# Edit .env with your API keys (minimum required: ANTHROPIC_API_KEY)
```

### 3. Database Migration

```bash
# Run the migration to create new tables and fields
cd claude-code-os-implementation/03-ai-growth-engine/organic-marketing-package/packages/content-engine
python -c "from src.database.migrations.add_review_and_versioning import run_migration; run_migration()"
```

## Running the Test

### Option 1: Automated Test Script

The automated test script (`test_e2e_workflow.py`) runs all 8 steps automatically:

```bash
# Start services (in terminal 1)
./start_services.sh

# Run the E2E test (in terminal 2)
./test_e2e_workflow.py
```

### Option 2: Manual Step-by-Step Testing

Follow the steps below to manually test each part of the workflow.

## Test Steps

### Step 1: Start Celery Worker

Start the Celery worker with content generation queues:

```bash
cd claude-code-os-implementation/03-ai-growth-engine/organic-marketing-package/packages/content-engine
celery -A celery_app worker --loglevel=info -Q content_high,content_medium,content_low,default
```

**Expected Output:**
- Worker starts successfully
- Queues registered: `content_high`, `content_medium`, `content_low`, `default`
- Tasks discovered: `generate_blog_post_task`, `generate_social_post_task`

### Step 2: POST to /blog/generate-async

Generate a blog post asynchronously with high priority:

```bash
curl -X POST http://localhost:8000/api/blog/generate-async \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "The Future of E-commerce: AI-Powered Shopping Experiences",
    "content_pillar": "Technology Trends",
    "target_keywords": ["AI shopping", "e-commerce automation", "personalized recommendations"],
    "word_count": 800,
    "priority": "high"
  }'
```

**Expected Response:**
```json
{
  "task_id": "1234-5678-9012-3456",
  "status": "pending",
  "message": "Blog post generation task queued"
}
```

**Verification:**
- Status code: `202 Accepted`
- Response contains `task_id`
- Response contains `status: "pending"`

### Step 3: Poll /tasks/status/{task_id}

Poll the task status endpoint until the task completes:

```bash
curl http://localhost:8000/api/tasks/status/1234-5678-9012-3456
```

**Expected Progression:**
```json
// Initial state
{
  "task_id": "1234-5678-9012-3456",
  "status": "pending",
  "result": null
}

// Running state
{
  "task_id": "1234-5678-9012-3456",
  "status": "running",
  "result": null
}

// Completed state
{
  "task_id": "1234-5678-9012-3456",
  "status": "completed",
  "result": {
    "success": true,
    "content_id": 42,
    "request_id": "req_123"
  }
}
```

**Verification:**
- Initial status: `pending` or `running`
- Final status: `completed`
- Result contains `content_id`

### Step 4: Verify ContentHistory Record

Verify the ContentHistory record was created with `is_draft=True`:

**Option A: Database Query**
```sql
SELECT id, content_type, is_draft, version_number, parent_content_id
FROM content_history
WHERE id = 42;
```

**Expected Result:**
```
id  | content_type | is_draft | version_number | parent_content_id
----|--------------|----------|----------------|------------------
42  | blog         | true     | 1              | null
```

**Option B: API Endpoint (if available)**
```bash
curl http://localhost:8000/api/content/42
```

**Verification:**
- Record exists with correct `content_id`
- `is_draft` = `true`
- `version_number` = `1`
- `parent_content_id` = `null` (first version)

### Step 5: POST to /review/submit

Submit the content for human review:

```bash
curl -X POST http://localhost:8000/api/review/submit \
  -H "Content-Type: application/json" \
  -d '{
    "content_id": 42,
    "reviewer_id": "test_reviewer"
  }'
```

**Expected Response:**
```json
{
  "review_id": 1,
  "content_id": 42,
  "status": "in_review",
  "reviewer_id": "test_reviewer",
  "submitted_at": "2026-03-01T10:00:00Z"
}
```

**Verification:**
- Status code: `201 Created`
- Response contains `review_id`
- `status` = `in_review`
- `submitted_at` is set

### Step 6: POST to /review/approve

Approve the content under review:

```bash
curl -X POST http://localhost:8000/api/review/approve \
  -H "Content-Type: application/json" \
  -d '{
    "review_id": 1,
    "action": "approve",
    "notes": "Content looks great! Ready to publish."
  }'
```

**Expected Response:**
```json
{
  "review_id": 1,
  "content_id": 42,
  "status": "approved",
  "reviewer_id": "test_reviewer",
  "submitted_at": "2026-03-01T10:00:00Z",
  "reviewed_at": "2026-03-01T10:05:00Z",
  "notes": "Content looks great! Ready to publish."
}
```

**Verification:**
- Status code: `200 OK`
- `status` changed to `approved`
- `reviewed_at` is set
- `notes` contains approval message

### Step 7: POST to /versions/create-revision

Create a new revision of the content:

```bash
curl -X POST http://localhost:8000/api/versions/create-revision \
  -H "Content-Type: application/json" \
  -d '{
    "content_id": 42,
    "content": "Updated blog post content with revisions...",
    "generated_by": "test_user",
    "prompt_used": "Update with more details and examples"
  }'
```

**Expected Response:**
```json
{
  "content_id": 43,
  "version_number": 2,
  "parent_content_id": 42,
  "message": "New revision created successfully"
}
```

**Verification:**
- Status code: `201 Created`
- New `content_id` created (e.g., 43)
- `version_number` = `2`
- `parent_content_id` = original content_id (42)

### Step 8: GET /versions/history/{content_id}

Retrieve the complete version history:

```bash
curl http://localhost:8000/api/versions/history/42
```

**Expected Response:**
```json
{
  "content_id": 42,
  "versions": [
    {
      "id": 42,
      "version_number": 1,
      "parent_content_id": null,
      "is_draft": true,
      "created_at": "2026-03-01T10:00:00Z",
      "generated_by": "blog_agent"
    },
    {
      "id": 43,
      "version_number": 2,
      "parent_content_id": 42,
      "is_draft": true,
      "created_at": "2026-03-01T10:10:00Z",
      "generated_by": "test_user"
    }
  ],
  "total_versions": 2
}
```

**Verification:**
- Status code: `200 OK`
- At least 2 versions returned
- Version numbers are sequential (1, 2)
- Second version's `parent_content_id` matches first version's `id`

## Success Criteria

All 8 steps must complete successfully for the E2E workflow to pass:

- [x] Celery worker starts and registers content generation tasks
- [x] Async blog generation returns 202 with task_id
- [x] Task status polling works and task completes
- [x] ContentHistory record created with is_draft=True
- [x] Review submission creates review record with in_review status
- [x] Review approval changes status to approved
- [x] Revision creation increments version_number to 2
- [x] Version history shows all versions with proper relationships

## Troubleshooting

### Service Not Starting

**FastAPI:**
```bash
# Check if port 8000 is in use
lsof -i :8000

# Check logs
tail -f /tmp/fastapi.log
```

**Celery:**
```bash
# Check Redis is running
redis-cli ping

# Check Celery logs
tail -f /tmp/celery.log
```

### Task Not Completing

1. Check Celery worker logs for errors
2. Verify ANTHROPIC_API_KEY is set in .env
3. Check Redis connection
4. Ensure task queues are properly configured

### Database Errors

1. Ensure migration has been run
2. Check database connection in .env
3. Verify tables exist:
   ```sql
   \dt content_*
   ```

### API Errors

1. Check FastAPI logs for details
2. Verify request payload matches Pydantic models
3. Ensure database records exist before operating on them

## Cleanup

After testing, stop the services:

```bash
# Find and kill processes
pkill -f 'uvicorn api.main'
pkill -f 'celery.*worker'

# Or use specific PIDs from start_services.sh output
kill <FASTAPI_PID> <CELERY_PID>
```

## Notes

- This test requires actual API keys (ANTHROPIC_API_KEY at minimum)
- Content generation may take 30-60 seconds depending on API response time
- The test creates real database records
- Consider using a test database for E2E testing
