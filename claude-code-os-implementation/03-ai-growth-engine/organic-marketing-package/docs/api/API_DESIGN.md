# API Design Documentation

## Overview

This document defines the REST API design for the E-Commerce Brand Business OS, specifically the AI Content Agents service. The API exposes content generation capabilities through a FastAPI-based REST interface.

## Design Principles

1. **RESTful Architecture**: Resource-based URLs with standard HTTP methods
2. **JSON-First**: All requests and responses use JSON format
3. **Validation-First**: Pydantic models for request/response validation
4. **Error Consistency**: Standardized error response format
5. **Versioning**: URL-based versioning (/api/v1/...)
6. **Async Support**: Non-blocking operations for concurrent requests

## Base Configuration

- **Base URL**: `http://localhost:8000` (development)
- **API Version**: `v1` (implicit in current implementation)
- **Content Type**: `application/json`
- **Character Encoding**: UTF-8

## Authentication Strategy

### Current Implementation (Phase 1)

**No Authentication** - For initial development and testing only.

### Planned Implementation (Phase 2)

#### Option 1: API Key Authentication (Recommended for MVP)

**Header-Based Authentication**:
```
X-API-Key: your-api-key-here
```

**Features**:
- Simple client implementation
- Easy to rotate keys
- Per-client rate limiting
- Usage tracking per API key

**Implementation**:
```python
from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key")

async def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key not in valid_api_keys:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return api_key
```

#### Option 2: JWT Authentication (Future)

**Bearer Token Authentication**:
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Features**:
- Stateless authentication
- Role-based access control (RBAC)
- Token expiration and refresh
- User session management

### Rate Limiting Strategy

**Per-Endpoint Limits**:
- Content Generation: 100 requests/hour per API key
- Content History: 1000 requests/hour per API key
- Metrics: 500 requests/hour per API key

**Implementation**:
- Use `slowapi` or `fastapi-limiter` library
- Store rate limit state in Redis (production)
- Return standard rate limit headers:
  - `X-RateLimit-Limit`: Maximum requests
  - `X-RateLimit-Remaining`: Remaining requests
  - `X-RateLimit-Reset`: Unix timestamp when limit resets

## API Endpoints

### Content Generation Endpoints

#### 1. Universal Content Generation

**Endpoint**: `POST /api/content/generate`

**Description**: Generate content using any available agent based on content type.

**Request Body**:
```json
{
  "content_type": "blog",
  "prompt": "Write a blog post about tactical backpacks for urban professionals",
  "parameters": {
    "pillar": "Battle-Ready Lifestyle",
    "tone": "authoritative",
    "max_tokens": 4096,
    "temperature": 1.0
  },
  "metadata": {
    "campaign_id": "spring-2024",
    "user_id": "user123"
  }
}
```

**Request Schema**:
```python
class ContentRequest(BaseModel):
    content_type: str = Field(..., description="Type of content: blog, social, amazon, competitor")
    prompt: str = Field(..., min_length=10, max_length=5000)
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
```

**Response** (200 OK):
```json
{
  "request_id": "req_abc123def456",
  "content_type": "blog",
  "content": "# Tactical Backpacks for the Modern Urban Professional\n\n...",
  "metadata": {
    "agent": "blog_agent",
    "model": "claude-sonnet-4-5-20250929",
    "tokens_used": 2847,
    "generation_time_ms": 3421,
    "timestamp": "2024-02-26T10:30:45Z"
  },
  "status": "success"
}
```

**Response Schema**:
```python
class ContentResponse(BaseModel):
    request_id: str
    content_type: str
    content: str
    metadata: ContentMetadata
    status: str = "success"
```

**Error Response** (400 Bad Request):
```json
{
  "error": "ValidationError",
  "message": "Invalid content_type: 'unknown'. Must be one of: blog, social, amazon, competitor",
  "details": {
    "field": "content_type",
    "allowed_values": ["blog", "social", "amazon", "competitor"]
  },
  "request_id": "req_abc123def456",
  "timestamp": "2024-02-26T10:30:45Z"
}
```

#### 2. Blog Content Generation

**Endpoint**: `POST /api/blog/generate`

**Description**: Generate blog content with blog-specific parameters.

**Request Body**:
```json
{
  "topic": "Tactical backpacks for urban professionals",
  "pillar": "Battle-Ready Lifestyle",
  "content_format": "listicle",
  "target_word_count": 1500,
  "seo_keywords": ["tactical backpack", "urban EDC", "professional carry"],
  "include_outline": true
}
```

**Request Schema**:
```python
class BlogRequest(BaseModel):
    topic: str = Field(..., min_length=10, max_length=500)
    pillar: str = Field(..., description="Content pillar from brand strategy")
    content_format: str = Field(default="article", pattern="^(article|listicle|how-to|review)$")
    target_word_count: int = Field(default=1500, ge=500, le=5000)
    seo_keywords: Optional[List[str]] = Field(default_factory=list, max_items=10)
    include_outline: bool = Field(default=False)
```

**Response** (200 OK):
```json
{
  "request_id": "req_blog_789xyz",
  "content": "# 7 Best Tactical Backpacks for Urban Professionals\n\n...",
  "outline": "I. Introduction\nII. Key Features to Look For\n...",
  "metadata": {
    "word_count": 1547,
    "reading_time_minutes": 6,
    "seo_score": 85,
    "tokens_used": 3241
  },
  "status": "success"
}
```

#### 3. Social Media Content Generation

**Endpoint**: `POST /api/social/generate`

**Description**: Generate platform-specific social media content.

**Request Body**:
```json
{
  "platform": "instagram",
  "content_type": "carousel",
  "topic": "5 EDC essentials for urban professionals",
  "pillar": "Battle-Ready Lifestyle",
  "include_hashtags": true,
  "target_audience": "urban_professionals_25_40"
}
```

**Request Schema**:
```python
class SocialRequest(BaseModel):
    platform: str = Field(..., pattern="^(instagram|reddit|facebook|twitter)$")
    content_type: str = Field(..., pattern="^(post|carousel|story|reel)$")
    topic: str = Field(..., min_length=10, max_length=300)
    pillar: str
    include_hashtags: bool = Field(default=True)
    target_audience: Optional[str] = None
```

**Response** (200 OK):
```json
{
  "request_id": "req_social_456abc",
  "platform": "instagram",
  "content": {
    "slides": [
      {
        "slide_number": 1,
        "heading": "EDC Essentials",
        "body": "Be prepared for anything the city throws at you...",
        "cta": "Swipe to see #2 →"
      }
    ],
    "caption": "Your urban survival kit starts here. 5 essential items...",
    "hashtags": ["#EDC", "#UrbanPrep", "#BattleReady", "#InfinityVault"]
  },
  "metadata": {
    "slide_count": 5,
    "character_count": 487,
    "hashtag_count": 15
  },
  "status": "success"
}
```

#### 4. Amazon Listing Generation

**Endpoint**: `POST /api/amazon/generate`

**Description**: Generate Amazon product listing content.

**Request Body**:
```json
{
  "product_name": "Tactical EDC Backpack - 30L",
  "listing_type": "bullets",
  "product_features": [
    "Water-resistant 1000D nylon",
    "MOLLE webbing system",
    "Laptop compartment up to 17 inches"
  ],
  "target_keywords": ["tactical backpack", "EDC bag", "MOLLE backpack"],
  "competitor_asins": ["B07XYZ123", "B08ABC456"]
}
```

**Request Schema**:
```python
class AmazonRequest(BaseModel):
    product_name: str = Field(..., min_length=10, max_length=200)
    listing_type: str = Field(..., pattern="^(title|bullets|description|a_plus)$")
    product_features: List[str] = Field(..., min_items=3, max_items=20)
    target_keywords: List[str] = Field(..., min_items=3, max_items=20)
    competitor_asins: Optional[List[str]] = Field(default_factory=list, max_items=5)
```

**Response** (200 OK):
```json
{
  "request_id": "req_amazon_321def",
  "listing_type": "bullets",
  "content": [
    "⚡ BATTLE-READY DURABILITY: Military-grade 1000D nylon construction...",
    "🎒 VERSATILE MOLLE SYSTEM: Customizable external attachment points...",
    "💻 TECH-OPTIMIZED DESIGN: Dedicated padded laptop compartment...",
    "🌧️ WEATHER-RESISTANT PROTECTION: Water-resistant coating keeps...",
    "✅ LIFETIME WARRANTY: Infinity Vault stands behind every product..."
  ],
  "metadata": {
    "bullet_count": 5,
    "keyword_density": {
      "tactical backpack": 3,
      "EDC bag": 2,
      "MOLLE backpack": 2
    },
    "character_count_per_bullet": [87, 92, 84, 89, 78]
  },
  "status": "success"
}
```

#### 5. Competitor Analysis

**Endpoint**: `POST /api/competitor/analyze`

**Description**: Analyze competitor content and extract insights.

**Request Body**:
```json
{
  "analysis_type": "amazon_listing",
  "competitor_url": "https://www.amazon.com/dp/B07XYZ123",
  "focus_areas": ["features", "benefits", "positioning", "reviews"],
  "extract_keywords": true
}
```

**Request Schema**:
```python
class CompetitorRequest(BaseModel):
    analysis_type: str = Field(..., pattern="^(amazon_listing|blog_post|social_content)$")
    competitor_url: Optional[str] = Field(None, max_length=2000)
    competitor_content: Optional[str] = Field(None, max_length=10000)
    focus_areas: List[str] = Field(default_factory=list)
    extract_keywords: bool = Field(default=True)
```

**Response** (200 OK):
```json
{
  "request_id": "req_comp_654ghi",
  "analysis": {
    "strengths": ["Strong focus on durability", "Clear military aesthetic"],
    "weaknesses": ["Generic positioning", "Limited lifestyle integration"],
    "opportunities": ["Urban professional segment underserved"],
    "keywords": ["tactical", "military-grade", "durable", "EDC"],
    "positioning": "Military surplus approach vs. lifestyle integration",
    "recommendations": [
      "Emphasize professional/lifestyle use cases",
      "Differentiate with urban scenarios",
      "Highlight premium materials and craftsmanship"
    ]
  },
  "metadata": {
    "analyzed_sections": ["title", "bullets", "description", "reviews"],
    "review_count_analyzed": 50,
    "sentiment_score": 4.3
  },
  "status": "success"
}
```

### Content Retrieval Endpoints

#### 6. Content History

**Endpoint**: `GET /api/content/history`

**Description**: Retrieve previously generated content with filtering and pagination.

**Query Parameters**:
- `content_type` (optional): Filter by content type (blog, social, amazon, competitor)
- `start_date` (optional): ISO 8601 timestamp
- `end_date` (optional): ISO 8601 timestamp
- `limit` (optional): Number of results (default: 50, max: 100)
- `offset` (optional): Pagination offset (default: 0)
- `order_by` (optional): Sort field (created_at, tokens_used)
- `order` (optional): Sort direction (asc, desc)

**Example Request**:
```
GET /api/content/history?content_type=blog&limit=10&order_by=created_at&order=desc
```

**Response** (200 OK):
```json
{
  "results": [
    {
      "id": "content_123abc",
      "content_type": "blog",
      "prompt": "Write about tactical backpacks...",
      "content": "# Tactical Backpacks...",
      "created_at": "2024-02-26T10:30:45Z",
      "metadata": {
        "tokens_used": 2847,
        "generation_time_ms": 3421
      }
    }
  ],
  "pagination": {
    "total": 156,
    "limit": 10,
    "offset": 0,
    "has_more": true
  }
}
```

#### 7. Metrics and Usage

**Endpoint**: `GET /api/metrics`

**Description**: Retrieve API usage metrics and statistics.

**Query Parameters**:
- `start_date` (optional): ISO 8601 timestamp
- `end_date` (optional): ISO 8601 timestamp
- `group_by` (optional): Grouping dimension (day, week, month, content_type)

**Example Request**:
```
GET /api/metrics?start_date=2024-02-01&end_date=2024-02-26&group_by=content_type
```

**Response** (200 OK):
```json
{
  "period": {
    "start": "2024-02-01T00:00:00Z",
    "end": "2024-02-26T23:59:59Z"
  },
  "metrics": {
    "total_requests": 1247,
    "successful_requests": 1198,
    "failed_requests": 49,
    "total_tokens_used": 3482914,
    "average_generation_time_ms": 3215,
    "by_content_type": {
      "blog": {
        "requests": 456,
        "tokens": 1892341,
        "avg_time_ms": 4123
      },
      "social": {
        "requests": 589,
        "tokens": 982145,
        "avg_time_ms": 2341
      },
      "amazon": {
        "requests": 134,
        "tokens": 421893,
        "avg_time_ms": 2987
      },
      "competitor": {
        "requests": 68,
        "tokens": 186535,
        "avg_time_ms": 5621
      }
    }
  },
  "cost_estimate": {
    "total_usd": 52.24,
    "by_model": {
      "claude-sonnet-4-5-20250929": 52.24
    }
  }
}
```

### Health and Status Endpoints

#### 8. Health Check

**Endpoint**: `GET /api/health`

**Description**: Simple health check endpoint.

**Response** (200 OK):
```json
{
  "status": "healthy",
  "timestamp": "2024-02-26T10:30:45Z",
  "version": "0.2.0",
  "services": {
    "database": "connected",
    "anthropic_api": "available"
  }
}
```

#### 9. API Information

**Endpoint**: `GET /api/info`

**Description**: API version and capability information.

**Response** (200 OK):
```json
{
  "name": "AI Content Agents API",
  "version": "0.2.0",
  "description": "REST API for AI-powered content generation",
  "supported_content_types": ["blog", "social", "amazon", "competitor"],
  "supported_models": [
    "claude-sonnet-4-5-20250929",
    "claude-3-5-sonnet-20241022"
  ],
  "documentation_url": "/docs",
  "openapi_url": "/openapi.json"
}
```

## Error Handling

### Standard Error Response Format

All errors follow this consistent structure:

```json
{
  "error": "ErrorType",
  "message": "Human-readable error description",
  "details": {
    "field": "specific_field",
    "constraint": "validation_rule"
  },
  "request_id": "req_abc123def456",
  "timestamp": "2024-02-26T10:30:45Z"
}
```

### HTTP Status Codes

| Status Code | Error Type | Description |
|-------------|------------|-------------|
| 200 | Success | Request completed successfully |
| 400 | ValidationError | Invalid request parameters |
| 401 | AuthenticationError | Missing or invalid API key |
| 403 | AuthorizationError | Insufficient permissions |
| 404 | NotFoundError | Resource not found |
| 429 | RateLimitError | Rate limit exceeded |
| 500 | InternalServerError | Unexpected server error |
| 502 | APIError | Anthropic API communication failure |
| 503 | ServiceUnavailable | Service temporarily unavailable |

### Error Examples

**Validation Error** (400):
```json
{
  "error": "ValidationError",
  "message": "Invalid content_type parameter",
  "details": {
    "field": "content_type",
    "value": "unknown",
    "allowed_values": ["blog", "social", "amazon", "competitor"]
  },
  "request_id": "req_abc123",
  "timestamp": "2024-02-26T10:30:45Z"
}
```

**Rate Limit Error** (429):
```json
{
  "error": "RateLimitError",
  "message": "Rate limit exceeded: 100 requests per hour",
  "details": {
    "limit": 100,
    "reset_at": "2024-02-26T11:00:00Z",
    "retry_after_seconds": 1245
  },
  "request_id": "req_def456",
  "timestamp": "2024-02-26T10:30:45Z"
}
```

**API Error** (502):
```json
{
  "error": "APIError",
  "message": "Failed to communicate with Anthropic API",
  "details": {
    "upstream_error": "Connection timeout",
    "retry_attempted": true
  },
  "request_id": "req_ghi789",
  "timestamp": "2024-02-26T10:30:45Z"
}
```

## Request/Response Headers

### Standard Request Headers

```
Content-Type: application/json
Accept: application/json
X-API-Key: your-api-key-here (when authentication enabled)
User-Agent: ClientName/Version
```

### Standard Response Headers

```
Content-Type: application/json; charset=utf-8
X-Request-ID: req_abc123def456
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 87
X-RateLimit-Reset: 1709032800
X-Response-Time: 3421ms
```

## Pydantic Models Reference

### Core Request Models

```python
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime

class ContentRequest(BaseModel):
    """Universal content generation request"""
    content_type: str = Field(..., description="Content type identifier")
    prompt: str = Field(..., min_length=10, max_length=5000)
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

class BlogRequest(BaseModel):
    """Blog-specific content request"""
    topic: str = Field(..., min_length=10, max_length=500)
    pillar: str
    content_format: str = Field(default="article")
    target_word_count: int = Field(default=1500, ge=500, le=5000)
    seo_keywords: Optional[List[str]] = Field(default_factory=list)
    include_outline: bool = Field(default=False)

class SocialRequest(BaseModel):
    """Social media content request"""
    platform: str = Field(..., pattern="^(instagram|reddit|facebook|twitter)$")
    content_type: str = Field(..., pattern="^(post|carousel|story|reel)$")
    topic: str = Field(..., min_length=10, max_length=300)
    pillar: str
    include_hashtags: bool = Field(default=True)
    target_audience: Optional[str] = None

class AmazonRequest(BaseModel):
    """Amazon listing content request"""
    product_name: str = Field(..., min_length=10, max_length=200)
    listing_type: str = Field(..., pattern="^(title|bullets|description|a_plus)$")
    product_features: List[str] = Field(..., min_items=3, max_items=20)
    target_keywords: List[str] = Field(..., min_items=3, max_items=20)
    competitor_asins: Optional[List[str]] = Field(default_factory=list)

class CompetitorRequest(BaseModel):
    """Competitor analysis request"""
    analysis_type: str = Field(..., pattern="^(amazon_listing|blog_post|social_content)$")
    competitor_url: Optional[str] = Field(None, max_length=2000)
    competitor_content: Optional[str] = Field(None, max_length=10000)
    focus_areas: List[str] = Field(default_factory=list)
    extract_keywords: bool = Field(default=True)
```

### Core Response Models

```python
class ContentMetadata(BaseModel):
    """Metadata for generated content"""
    agent: str
    model: str
    tokens_used: int
    generation_time_ms: int
    timestamp: datetime

class ContentResponse(BaseModel):
    """Universal content generation response"""
    request_id: str
    content_type: str
    content: str
    metadata: ContentMetadata
    status: str = "success"

class ErrorResponse(BaseModel):
    """Standard error response"""
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None
    request_id: str
    timestamp: datetime
```

## WebSocket Support (Future)

For real-time content generation streaming:

**Endpoint**: `ws://localhost:8000/ws/content/generate`

**Use Case**: Stream content as it's being generated for better UX.

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/content/generate');

ws.send(JSON.stringify({
  content_type: 'blog',
  prompt: 'Write about tactical backpacks...'
}));

ws.onmessage = (event) => {
  const chunk = JSON.parse(event.data);
  // Append chunk.content to display
};
```

## API Versioning Strategy

### URL-Based Versioning (Recommended)

```
/api/v1/content/generate  (current)
/api/v2/content/generate  (future breaking changes)
```

### Benefits
- Clear version in URL
- Easy to support multiple versions
- Client migration at their own pace
- Deprecation timeline visibility

### Version Lifecycle
1. **Active**: Current production version
2. **Deprecated**: Supported but discouraged (6-month notice)
3. **Sunset**: No longer supported

## Testing the API

### Using cURL

```bash
# Generate blog content
curl -X POST http://localhost:8000/api/blog/generate \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-key-here" \
  -d '{
    "topic": "Best tactical backpacks for urban professionals",
    "pillar": "Battle-Ready Lifestyle",
    "content_format": "listicle",
    "target_word_count": 1500
  }'

# Get content history
curl -X GET "http://localhost:8000/api/content/history?limit=10" \
  -H "X-API-Key: your-key-here"

# Health check
curl http://localhost:8000/api/health
```

### Using Python requests

```python
import requests

# Generate content
response = requests.post(
    'http://localhost:8000/api/content/generate',
    headers={
        'Content-Type': 'application/json',
        'X-API-Key': 'your-key-here'
    },
    json={
        'content_type': 'blog',
        'prompt': 'Write about tactical backpacks...',
        'parameters': {'pillar': 'Battle-Ready Lifestyle'}
    }
)

data = response.json()
print(data['content'])
```

### Using HTTPie

```bash
# Generate social content
http POST localhost:8000/api/social/generate \
  X-API-Key:your-key-here \
  platform=instagram \
  content_type=carousel \
  topic="5 EDC essentials" \
  pillar="Battle-Ready Lifestyle"
```

## OpenAPI/Swagger Documentation

FastAPI automatically generates interactive API documentation:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

## Performance Considerations

1. **Request Timeout**: 60 seconds default, 120 seconds for complex content
2. **Max Request Size**: 1MB for request body
3. **Connection Pooling**: Reuse HTTP connections to Anthropic API
4. **Response Caching**: Cache frequently requested content (future)
5. **Async Endpoints**: All endpoints support async for concurrency

## Security Best Practices

1. **Input Validation**: All inputs validated via Pydantic
2. **Output Sanitization**: Remove sensitive data from responses
3. **Rate Limiting**: Prevent abuse and control costs
4. **CORS Configuration**: Whitelist allowed origins
5. **HTTPS Only**: Enforce TLS in production
6. **API Key Rotation**: Support key rotation without downtime
7. **Audit Logging**: Log all API requests for security review

## Monitoring and Observability

### Metrics to Track

- Request rate (requests/second)
- Error rate (percentage)
- Response time (p50, p95, p99)
- Token consumption (per endpoint)
- API key usage distribution
- Anthropic API latency

### Logging Standards

- Request ID on all log entries
- Structured JSON logging
- Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Sensitive data redaction

## Migration from CLI to API

For users currently using the CLI interface:

**Before (CLI)**:
```bash
python ai-content-agents/generate_content.py \
  --type blog \
  --topic "tactical backpacks"
```

**After (API)**:
```bash
curl -X POST http://localhost:8000/api/blog/generate \
  -H "Content-Type: application/json" \
  -d '{"topic": "tactical backpacks", "pillar": "Battle-Ready Lifestyle"}'
```

**Benefits of API**:
- Remote access and integration
- Better error handling
- Request tracking and history
- Rate limiting and usage controls
- Multi-user support

## Future Enhancements

1. **Batch Endpoints**: Generate multiple content pieces in one request
2. **Content Templates**: Reusable content templates with placeholders
3. **Scheduled Generation**: Cron-like content generation scheduling
4. **Content Variants**: A/B testing with multiple content variations
5. **Feedback Loop**: Rate content quality to improve future generations
6. **Export Formats**: Support PDF, DOCX, HTML exports
7. **Webhook Notifications**: Notify external systems when content ready
8. **GraphQL Support**: Alternative to REST for complex queries

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [REST API Best Practices](https://restfulapi.net/)
- [OpenAPI Specification](https://swagger.io/specification/)

## Changelog

- **v0.2.0** - API design documentation created
- **v0.3.0** - Planned: Initial API implementation
- **v0.4.0** - Planned: Authentication and rate limiting
- **v0.5.0** - Planned: WebSocket support for streaming
