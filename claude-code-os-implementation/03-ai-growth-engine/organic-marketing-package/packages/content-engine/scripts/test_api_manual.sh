#!/bin/bash
# Manual API Testing Script
# This script provides curl commands to test all API endpoints

echo "==================================="
echo "AI Content Agents - Manual API Test"
echo "==================================="
echo ""
echo "Prerequisites:"
echo "1. Start the API server in a separate terminal:"
echo "   cd ai-content-agents"
echo "   export ANTHROPIC_API_KEY=your-api-key-here"
echo "   uvicorn api.main:app --reload"
echo ""
echo "2. Wait for the server to start (look for 'Application startup complete')"
echo ""
echo "Press Enter to begin testing..."
read

BASE_URL="http://localhost:8000"

echo ""
echo "==================================="
echo "1. Testing Health Check"
echo "==================================="
curl -s -X GET "${BASE_URL}/health" | python -m json.tool
echo ""

echo ""
echo "==================================="
echo "2. Testing Root Endpoint"
echo "==================================="
curl -s -X GET "${BASE_URL}/" | python -m json.tool
echo ""

echo ""
echo "==================================="
echo "3. Testing API Documentation"
echo "==================================="
echo "Open in browser: ${BASE_URL}/api/docs"
echo ""

echo ""
echo "==================================="
echo "4. Testing Blog Post Generation"
echo "==================================="
echo "Request: POST /api/blog/generate"
curl -s -X POST "${BASE_URL}/api/blog/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "How to Organize Your Trading Card Collection for Tournament Play",
    "content_pillar": "Battle-Ready Lifestyle",
    "target_keywords": ["trading card storage", "tournament preparation"],
    "word_count": 1000,
    "include_cta": true
  }' | python -m json.tool
echo ""

echo ""
echo "==================================="
echo "5. Testing Blog Series Generation"
echo "==================================="
echo "Request: POST /api/blog/series"
curl -s -X POST "${BASE_URL}/api/blog/series" \
  -H "Content-Type: application/json" \
  -d '{
    "series_topic": "Complete Guide to Tournament Preparation",
    "num_posts": 3,
    "content_pillar": "Battle-Ready Lifestyle"
  }' | python -m json.tool
echo ""

echo ""
echo "==================================="
echo "6. Testing Listicle Generation"
echo "==================================="
echo "Request: POST /api/blog/listicle"
curl -s -X POST "${BASE_URL}/api/blog/listicle" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Essential Accessories Every TCG Player Needs",
    "num_items": 7,
    "content_pillar": "Gear & Equipment"
  }' | python -m json.tool
echo ""

echo ""
echo "==================================="
echo "7. Testing How-To Guide Generation"
echo "==================================="
echo "Request: POST /api/blog/how-to"
curl -s -X POST "${BASE_URL}/api/blog/how-to" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "How to Double Sleeve Your Trading Cards for Maximum Protection",
    "target_audience": "Competitive players",
    "difficulty_level": "beginner"
  }' | python -m json.tool
echo ""

echo ""
echo "==================================="
echo "8. Testing Instagram Post Generation"
echo "==================================="
echo "Request: POST /api/social/instagram/post"
curl -s -X POST "${BASE_URL}/api/social/instagram/post" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "New product launch: Ultimate Card Storage System",
    "content_pillar": "Gear & Equipment",
    "post_type": "product_showcase"
  }' | python -m json.tool
echo ""

echo ""
echo "==================================="
echo "9. Testing Error Handling (Invalid Request)"
echo "==================================="
echo "Request: POST /api/blog/generate (with invalid topic - too short)"
curl -s -X POST "${BASE_URL}/api/blog/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "test",
    "content_pillar": "Battle-Ready Lifestyle"
  }' | python -m json.tool
echo ""

echo ""
echo "==================================="
echo "Testing Complete!"
echo "==================================="
echo ""
echo "Check the output above for:"
echo "- HTTP 200 responses for successful requests"
echo "- Proper JSON formatting in responses"
echo "- request_id in each response"
echo "- metadata with generation_time_ms"
echo "- file_path showing where content was saved"
echo "- Validation errors for invalid requests (test 9)"
echo ""
