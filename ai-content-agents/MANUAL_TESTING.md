# Manual API Testing Guide

This guide provides step-by-step instructions for manually testing the AI Content Agents API.

## Prerequisites

1. **Install dependencies:**
   ```bash
   cd ai-content-agents
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   ```bash
   export ANTHROPIC_API_KEY=your-api-key-here
   ```

3. **Ensure you have curl installed:**
   ```bash
   curl --version
   ```

## Starting the API Server

1. Navigate to the ai-content-agents directory:
   ```bash
   cd ai-content-agents
   ```

2. Start the server with uvicorn:
   ```bash
   uvicorn api.main:app --reload
   ```

3. Wait for the startup message:
   ```
   INFO:     Application startup complete.
   INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
   ```

4. Verify the server is running:
   ```bash
   curl http://localhost:8000/health
   ```

   Expected response:
   ```json
   {
     "status": "healthy",
     "timestamp": "2024-01-01T12:00:00.000000Z",
     "service": "ai-content-agents"
   }
   ```

## Testing Basic Endpoints

### 1. Root Endpoint

```bash
curl http://localhost:8000/
```

Expected response:
```json
{
  "service": "AI Content Agents API",
  "version": "1.0.0",
  "status": "operational",
  "docs": "/api/docs"
}
```

### 2. Health Check

```bash
curl http://localhost:8000/health
```

### 3. API Documentation

Open in your browser:
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc
- OpenAPI JSON: http://localhost:8000/api/openapi.json

## Testing Blog Endpoints

### Generate Blog Post

```bash
curl -X POST http://localhost:8000/api/blog/generate \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "How to Organize Your Trading Card Collection for Tournament Play",
    "content_pillar": "Battle-Ready Lifestyle",
    "target_keywords": ["trading card storage", "tournament preparation"],
    "word_count": 1000,
    "include_cta": true
  }'
```

Expected response structure:
```json
{
  "request_id": "uuid-string",
  "content": "Generated blog post content...",
  "file_path": "output/blog/YYYYMMDD_HHMMSS_blog_post.md",
  "metadata": {
    "agent": "blog_agent",
    "model": "claude-sonnet-4-5-20250929",
    "tokens_used": 0,
    "generation_time_ms": 1234,
    "timestamp": "2024-01-01T12:00:00.000000"
  },
  "status": "success"
}
```

### Generate Blog Series

```bash
curl -X POST http://localhost:8000/api/blog/series \
  -H "Content-Type: application/json" \
  -d '{
    "series_topic": "Complete Guide to Tournament Preparation",
    "num_posts": 3,
    "content_pillar": "Battle-Ready Lifestyle"
  }'
```

### Generate Listicle

```bash
curl -X POST http://localhost:8000/api/blog/listicle \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Essential Accessories Every TCG Player Needs",
    "num_items": 7,
    "content_pillar": "Gear & Equipment"
  }'
```

### Generate How-To Guide

```bash
curl -X POST http://localhost:8000/api/blog/how-to \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "How to Double Sleeve Your Trading Cards for Maximum Protection",
    "target_audience": "Competitive players",
    "difficulty_level": "beginner"
  }'
```

## Testing Social Media Endpoints

### Instagram Post

```bash
curl -X POST http://localhost:8000/api/social/instagram/post \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "New product launch: Ultimate Card Storage System",
    "content_pillar": "Gear & Equipment",
    "post_type": "product_showcase",
    "include_hashtags": true,
    "platform_specific": {
      "use_emojis": true,
      "hashtag_count": 15
    }
  }'
```

### Reddit Post

```bash
curl -X POST http://localhost:8000/api/social/reddit/post \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Tournament results and lessons learned",
    "content_pillar": "Battle-Ready Lifestyle",
    "subreddit": "CompetitiveTCG",
    "post_type": "discussion",
    "include_tldr": true
  }'
```

### Content Calendar

```bash
curl -X POST http://localhost:8000/api/social/calendar \
  -H "Content-Type: application/json" \
  -d '{
    "month": "2024-03",
    "content_pillar": "Battle-Ready Lifestyle",
    "platforms": ["instagram", "reddit", "twitter"],
    "posts_per_week": 5
  }'
```

## Testing Amazon Endpoints

### Product Description

```bash
curl -X POST http://localhost:8000/api/amazon/product-description \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "Premium Double-Sleeve Card Protectors",
    "product_category": "card_protection",
    "key_features": ["UV protection", "archival quality", "perfect fit"],
    "target_keywords": ["card sleeves", "TCG protection"],
    "word_count": 250
  }'
```

### Bullet Points

```bash
curl -X POST http://localhost:8000/api/amazon/bullet-points \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "Tournament-Grade Card Storage Box",
    "product_category": "storage_solutions",
    "key_features": ["holds 1000 cards", "waterproof", "lockable"],
    "num_bullets": 5
  }'
```

## Testing Competitor Analysis Endpoints

### Analysis Report

```bash
curl -X POST http://localhost:8000/api/competitor/analysis \
  -H "Content-Type: application/json" \
  -d '{
    "competitor_url": "https://example.com/competitor-product",
    "analysis_type": "product_description",
    "focus_areas": ["messaging", "features", "pricing"]
  }'
```

## Testing Error Handling

### Invalid Request (Topic Too Short)

```bash
curl -X POST http://localhost:8000/api/blog/generate \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "test",
    "content_pillar": "Battle-Ready Lifestyle"
  }'
```

Expected response (422 Validation Error):
```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "topic"],
      "msg": "String should have at least 10 characters",
      "input": "test"
    }
  ]
}
```

### Missing Required Field

```bash
curl -X POST http://localhost:8000/api/blog/generate \
  -H "Content-Type: application/json" \
  -d '{
    "content_pillar": "Battle-Ready Lifestyle"
  }'
```

## What to Verify

For each successful request, check:

1. **Response Status:** HTTP 200 OK
2. **Response Structure:**
   - `request_id` is present and unique
   - `content` contains generated text
   - `file_path` shows where content was saved
   - `metadata` includes generation time and timestamp
   - `status` is "success"

3. **File Creation:**
   - Check that files are created in the `output/` directory
   - Verify content matches the response

4. **Logging:**
   - Check console output for structured logs
   - Verify request IDs match between request and logs

5. **Error Responses:**
   - Invalid requests return appropriate HTTP error codes (422, 500)
   - Error messages are clear and helpful
   - Error responses include timestamp and request_id

## Common Issues and Troubleshooting

### Issue: Connection Refused

**Solution:** Make sure the API server is running:
```bash
uvicorn api.main:app --reload
```

### Issue: Module Not Found Errors

**Solution:** Install dependencies:
```bash
pip install -r requirements.txt
```

### Issue: Anthropic API Key Not Found

**Solution:** Set the environment variable:
```bash
export ANTHROPIC_API_KEY=your-api-key-here
```

### Issue: 500 Internal Server Error

**Solution:** Check the server logs for detailed error messages. Common causes:
- Missing or invalid API key
- Network issues connecting to Anthropic API
- Invalid brand context file

## Using the Automated Test Script

For convenience, you can use the provided test script:

```bash
chmod +x test_api_manual.sh
./test_api_manual.sh
```

This script will:
1. Guide you through starting the server
2. Test all major endpoints
3. Display formatted responses
4. Highlight any errors

## Next Steps

After manual testing:
1. Verify all endpoints work as expected
2. Check that files are created in the correct locations
3. Review logs for any warnings or errors
4. Test with different parameter combinations
5. Verify error handling works correctly
