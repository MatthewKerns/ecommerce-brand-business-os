# API Manual Test Results

This document records the manual testing results for the AI Content Agents API.

## Test Environment Setup

- **Date:** [To be filled by tester]
- **API Version:** 1.0.0
- **Python Version:** [To be filled by tester]
- **OS:** [To be filled by tester]

## Pre-Test Checklist

- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] ANTHROPIC_API_KEY environment variable set
- [ ] Server started with `uvicorn api.main:app --reload`
- [ ] Server shows "Application startup complete" message
- [ ] Health check endpoint responds: `curl http://localhost:8000/health`

## Test Cases

### 1. Basic Endpoints

#### 1.1 Root Endpoint
```bash
curl http://localhost:8000/
```

**Expected Result:**
- Status: 200 OK
- Response contains: service, version, status, docs fields

**Actual Result:**
- [ ] PASS
- [ ] FAIL - Details: _______________

---

#### 1.2 Health Check
```bash
curl http://localhost:8000/health
```

**Expected Result:**
- Status: 200 OK
- Response contains: status="healthy", timestamp, service="ai-content-agents"

**Actual Result:**
- [ ] PASS
- [ ] FAIL - Details: _______________

---

#### 1.3 API Documentation
Open in browser: http://localhost:8000/api/docs

**Expected Result:**
- Swagger UI loads successfully
- All endpoints are visible
- Can test endpoints directly from UI

**Actual Result:**
- [ ] PASS
- [ ] FAIL - Details: _______________

---

### 2. Blog Endpoints

#### 2.1 Generate Blog Post
```bash
curl -X POST http://localhost:8000/api/blog/generate \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "How to Organize Your Trading Card Collection for Tournament Play",
    "content_pillar": "Battle-Ready Lifestyle",
    "word_count": 1000
  }'
```

**Expected Result:**
- Status: 200 OK
- Response contains: request_id, content, file_path, metadata, status="success"
- File created at file_path location
- Metadata includes generation_time_ms

**Actual Result:**
- [ ] PASS
- [ ] FAIL - Details: _______________
- File path: _______________
- Generation time: _______ ms

---

#### 2.2 Generate Blog Series
```bash
curl -X POST http://localhost:8000/api/blog/series \
  -H "Content-Type: application/json" \
  -d '{
    "series_topic": "Complete Guide to Tournament Preparation",
    "num_posts": 3
  }'
```

**Expected Result:**
- Status: 200 OK
- Response contains: outline, file_path, num_posts=3
- Outline includes 3 post titles

**Actual Result:**
- [ ] PASS
- [ ] FAIL - Details: _______________

---

#### 2.3 Generate Listicle
```bash
curl -X POST http://localhost:8000/api/blog/listicle \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Essential Accessories Every TCG Player Needs",
    "num_items": 7
  }'
```

**Expected Result:**
- Status: 200 OK
- Content includes 7 list items

**Actual Result:**
- [ ] PASS
- [ ] FAIL - Details: _______________

---

#### 2.4 Generate How-To Guide
```bash
curl -X POST http://localhost:8000/api/blog/how-to \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "How to Double Sleeve Your Trading Cards for Maximum Protection",
    "difficulty_level": "beginner"
  }'
```

**Expected Result:**
- Status: 200 OK
- Content includes step-by-step instructions

**Actual Result:**
- [ ] PASS
- [ ] FAIL - Details: _______________

---

### 3. Social Media Endpoints

#### 3.1 Instagram Post
```bash
curl -X POST http://localhost:8000/api/social/instagram/post \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "New product launch: Ultimate Card Storage System",
    "post_type": "product_showcase"
  }'
```

**Expected Result:**
- Status: 200 OK
- Content includes Instagram-optimized text and hashtags

**Actual Result:**
- [ ] PASS
- [ ] FAIL - Details: _______________

---

#### 3.2 Reddit Post
```bash
curl -X POST http://localhost:8000/api/social/reddit/post \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Tournament results and lessons learned",
    "subreddit": "CompetitiveTCG",
    "post_type": "discussion"
  }'
```

**Expected Result:**
- Status: 200 OK
- Content follows Reddit formatting style

**Actual Result:**
- [ ] PASS
- [ ] FAIL - Details: _______________

---

### 4. Error Handling

#### 4.1 Validation Error - Topic Too Short
```bash
curl -X POST http://localhost:8000/api/blog/generate \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "test"
  }'
```

**Expected Result:**
- Status: 422 Unprocessable Entity
- Error details include validation message about minimum length

**Actual Result:**
- [ ] PASS
- [ ] FAIL - Details: _______________

---

#### 4.2 Missing Required Field
```bash
curl -X POST http://localhost:8000/api/blog/generate \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Expected Result:**
- Status: 422 Unprocessable Entity
- Error details include missing field information

**Actual Result:**
- [ ] PASS
- [ ] FAIL - Details: _______________

---

## Performance Tests

### Response Time Test
Test the same endpoint 5 times and record generation times:

```bash
for i in {1..5}; do
  curl -s -X POST http://localhost:8000/api/blog/generate \
    -H "Content-Type: application/json" \
    -d '{
      "topic": "Test post for performance measurement number '$i'",
      "word_count": 500
    }' | grep -o '"generation_time_ms":[0-9]*'
done
```

**Results:**
1. _______ ms
2. _______ ms
3. _______ ms
4. _______ ms
5. _______ ms

**Average:** _______ ms

---

## File System Tests

### Verify Output Files

Check that generated content is saved to files:

```bash
ls -lh ai-content-agents/output/blog/
ls -lh ai-content-agents/output/social/
```

**Expected:**
- Files created with timestamps in filenames
- Files contain the generated content
- Files have appropriate permissions

**Actual Result:**
- [ ] PASS
- [ ] FAIL - Details: _______________

---

## Logging Tests

### Check Server Logs

Review the uvicorn server output for:

- [ ] Startup message logged
- [ ] Request IDs logged for each request
- [ ] Generation success messages logged
- [ ] Error messages logged (for error test cases)
- [ ] No unexpected warnings or errors

**Notes:**
_______________________________________________

---

## Overall Test Summary

- **Total Tests:** 14
- **Passed:** _______
- **Failed:** _______
- **Success Rate:** _______%

### Critical Issues Found

1. _______________________________________________
2. _______________________________________________
3. _______________________________________________

### Recommendations

1. _______________________________________________
2. _______________________________________________
3. _______________________________________________

---

## Sign-off

**Tested By:** _______________
**Date:** _______________
**Approved:** [ ] Yes [ ] No
**Notes:** _______________________________________________
