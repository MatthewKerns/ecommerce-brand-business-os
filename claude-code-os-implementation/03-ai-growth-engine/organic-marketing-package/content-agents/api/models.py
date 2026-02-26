"""
Pydantic models for API request and response validation.

This module defines the data models used for validating incoming requests
and structuring outgoing responses for the AI Content Agents API.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


# ============================================================================
# Request Models
# ============================================================================

class ContentRequest(BaseModel):
    """
    Universal content generation request.

    This model handles generic content generation requests for any content type.
    """
    content_type: str = Field(
        ...,
        description="Type of content: blog, social, amazon, competitor"
    )
    prompt: str = Field(
        ...,
        min_length=10,
        max_length=5000,
        description="The content generation prompt"
    )
    parameters: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Additional parameters for content generation"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Optional metadata for tracking and organization"
    )

    class Config:
        json_schema_extra = {
            "example": {
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
        }


class BlogRequest(BaseModel):
    """
    Blog-specific content generation request.

    This model provides specialized parameters for blog content generation.
    """
    topic: str = Field(
        ...,
        min_length=10,
        max_length=500,
        description="The blog topic or title"
    )
    pillar: str = Field(
        ...,
        description="Content pillar from brand strategy"
    )
    content_format: str = Field(
        default="article",
        pattern="^(article|listicle|how-to|review)$",
        description="Format of the blog content"
    )
    target_word_count: int = Field(
        default=1500,
        ge=500,
        le=5000,
        description="Target word count for the blog post"
    )
    seo_keywords: Optional[List[str]] = Field(
        default_factory=list,
        max_length=10,
        description="SEO keywords to incorporate"
    )
    include_outline: bool = Field(
        default=False,
        description="Whether to include a content outline"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "topic": "Tactical backpacks for urban professionals",
                "pillar": "Battle-Ready Lifestyle",
                "content_format": "listicle",
                "target_word_count": 1500,
                "seo_keywords": ["tactical backpack", "urban EDC", "professional carry"],
                "include_outline": True
            }
        }


class SocialRequest(BaseModel):
    """
    Social media content generation request.

    This model handles platform-specific social media content generation.
    """
    platform: str = Field(
        ...,
        pattern="^(instagram|reddit|facebook|twitter)$",
        description="Social media platform"
    )
    content_type: str = Field(
        ...,
        pattern="^(post|carousel|story|reel)$",
        description="Type of social content"
    )
    topic: str = Field(
        ...,
        min_length=10,
        max_length=300,
        description="Content topic or theme"
    )
    pillar: str = Field(
        ...,
        description="Content pillar from brand strategy"
    )
    include_hashtags: bool = Field(
        default=True,
        description="Whether to include hashtags"
    )
    target_audience: Optional[str] = Field(
        None,
        description="Target audience segment"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "platform": "instagram",
                "content_type": "carousel",
                "topic": "5 EDC essentials for urban professionals",
                "pillar": "Battle-Ready Lifestyle",
                "include_hashtags": True,
                "target_audience": "urban_professionals_25_40"
            }
        }


class AmazonRequest(BaseModel):
    """
    Amazon listing content generation request.

    This model handles Amazon product listing content generation.
    """
    product_name: str = Field(
        ...,
        min_length=10,
        max_length=200,
        description="Product name or title"
    )
    listing_type: str = Field(
        ...,
        pattern="^(title|bullets|description|a_plus)$",
        description="Type of Amazon listing content"
    )
    product_features: List[str] = Field(
        ...,
        min_length=3,
        max_length=20,
        description="List of product features"
    )
    target_keywords: List[str] = Field(
        ...,
        min_length=3,
        max_length=20,
        description="Target keywords for SEO"
    )
    competitor_asins: Optional[List[str]] = Field(
        default_factory=list,
        max_length=5,
        description="Competitor ASINs for reference"
    )

    class Config:
        json_schema_extra = {
            "example": {
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
        }


class CompetitorRequest(BaseModel):
    """
    Competitor analysis request.

    This model handles competitor content analysis and insight extraction.
    """
    analysis_type: str = Field(
        ...,
        pattern="^(amazon_listing|blog_post|social_content)$",
        description="Type of content to analyze"
    )
    competitor_url: Optional[str] = Field(
        None,
        max_length=2000,
        description="URL of competitor content"
    )
    competitor_content: Optional[str] = Field(
        None,
        max_length=10000,
        description="Raw competitor content text"
    )
    focus_areas: List[str] = Field(
        default_factory=list,
        description="Specific areas to analyze"
    )
    extract_keywords: bool = Field(
        default=True,
        description="Whether to extract keywords"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "analysis_type": "amazon_listing",
                "competitor_url": "https://www.amazon.com/dp/B07XYZ123",
                "focus_areas": ["features", "benefits", "positioning", "reviews"],
                "extract_keywords": True
            }
        }


# ============================================================================
# Response Models
# ============================================================================

class ContentMetadata(BaseModel):
    """
    Metadata for generated content.

    This model captures metadata about the content generation process.
    """
    agent: str = Field(
        ...,
        description="Agent that generated the content"
    )
    model: str = Field(
        ...,
        description="AI model used for generation"
    )
    tokens_used: int = Field(
        ...,
        description="Number of tokens consumed"
    )
    generation_time_ms: int = Field(
        ...,
        description="Generation time in milliseconds"
    )
    timestamp: datetime = Field(
        ...,
        description="Timestamp of content generation"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "agent": "blog_agent",
                "model": "claude-sonnet-4-5-20250929",
                "tokens_used": 2847,
                "generation_time_ms": 3421,
                "timestamp": "2024-02-26T10:30:45Z"
            }
        }


class ContentResponse(BaseModel):
    """
    Universal content generation response.

    This model structures the response for all content generation requests.
    """
    request_id: str = Field(
        ...,
        description="Unique identifier for the request"
    )
    content_type: str = Field(
        ...,
        description="Type of content generated"
    )
    content: str = Field(
        ...,
        description="The generated content"
    )
    metadata: ContentMetadata = Field(
        ...,
        description="Metadata about the generation process"
    )
    status: str = Field(
        default="success",
        description="Status of the content generation"
    )

    class Config:
        json_schema_extra = {
            "example": {
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
        }


class ErrorResponse(BaseModel):
    """
    Standard error response.

    This model provides a consistent structure for all API errors.
    """
    error: str = Field(
        ...,
        description="Error type identifier"
    )
    message: str = Field(
        ...,
        description="Human-readable error message"
    )
    details: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional error details"
    )
    request_id: str = Field(
        ...,
        description="Request identifier for tracking"
    )
    timestamp: datetime = Field(
        ...,
        description="Timestamp when error occurred"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "error": "ValidationError",
                "message": "Invalid content_type: 'unknown'. Must be one of: blog, social, amazon, competitor",
                "details": {
                    "field": "content_type",
                    "allowed_values": ["blog", "social", "amazon", "competitor"]
                },
                "request_id": "req_abc123def456",
                "timestamp": "2024-02-26T10:30:45Z"
            }
        }


# ============================================================================
# TikTok Scheduling Models
# ============================================================================

class VideoContentData(BaseModel):
    """
    Content data for TikTok video uploads.

    This model defines the structure for video content to be scheduled.
    """
    video_url: str = Field(
        ...,
        description="URL of the video to upload (must be accessible)"
    )
    title: str = Field(
        ...,
        min_length=1,
        max_length=150,
        description="Video title (max 150 characters)"
    )
    description: Optional[str] = Field(
        None,
        max_length=1000,
        description="Video description (max 1000 characters)"
    )
    product_ids: Optional[List[str]] = Field(
        default_factory=list,
        description="List of product IDs to tag in the video"
    )
    tags: Optional[List[str]] = Field(
        default_factory=list,
        description="List of hashtags (without # symbol)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "video_url": "https://example.com/videos/product-demo.mp4",
                "title": "Check out our new tactical backpack!",
                "description": "Perfect for urban professionals who need battle-ready gear",
                "product_ids": ["prod_12345", "prod_67890"],
                "tags": ["tactical", "edc", "backpack"]
            }
        }


class PostContentData(BaseModel):
    """
    Content data for TikTok posts.

    This model defines the structure for post content to be scheduled.
    """
    content: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Post content/text (max 2000 characters)"
    )
    media_urls: Optional[List[str]] = Field(
        default_factory=list,
        description="List of media URLs (images/videos) to attach"
    )
    product_ids: Optional[List[str]] = Field(
        default_factory=list,
        description="List of product IDs to tag in the post"
    )
    tags: Optional[List[str]] = Field(
        default_factory=list,
        description="List of hashtags (without # symbol)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "content": "New arrival! Our tactical EDC backpack is perfect for the modern urban warrior.",
                "media_urls": ["https://example.com/images/backpack-1.jpg"],
                "product_ids": ["prod_12345"],
                "tags": ["newarrival", "tactical", "edc"]
            }
        }


class ScheduleContentRequest(BaseModel):
    """
    Request model for scheduling TikTok content.

    This model handles single content scheduling requests.
    """
    content_type: str = Field(
        ...,
        pattern="^(video|post)$",
        description="Type of content: video or post"
    )
    content_data: Dict[str, Any] = Field(
        ...,
        description="Content data (VideoContentData for video, PostContentData for post)"
    )
    scheduled_time: datetime = Field(
        ...,
        description="When the content should be published (ISO 8601 format)"
    )
    max_retries: int = Field(
        default=3,
        ge=0,
        le=10,
        description="Maximum number of retry attempts (0-10)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "content_type": "video",
                "content_data": {
                    "video_url": "https://example.com/videos/product-demo.mp4",
                    "title": "Check out our new tactical backpack!",
                    "description": "Perfect for urban professionals",
                    "product_ids": ["prod_12345"],
                    "tags": ["tactical", "edc"]
                },
                "scheduled_time": "2024-12-31T12:00:00Z",
                "max_retries": 3
            }
        }


class ScheduleContentResponse(BaseModel):
    """
    Response model for content scheduling.

    This model provides the response after successfully scheduling content.
    """
    id: int = Field(
        ...,
        description="Unique identifier for the scheduled content"
    )
    content_type: str = Field(
        ...,
        description="Type of content (video or post)"
    )
    status: str = Field(
        ...,
        description="Current status (pending, published, failed)"
    )
    scheduled_time: datetime = Field(
        ...,
        description="When the content will be published"
    )
    created_at: datetime = Field(
        ...,
        description="When the schedule was created"
    )
    max_retries: int = Field(
        ...,
        description="Maximum number of retry attempts"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "id": 123,
                "content_type": "video",
                "status": "pending",
                "scheduled_time": "2024-12-31T12:00:00Z",
                "created_at": "2024-12-20T10:30:00Z",
                "max_retries": 3
            }
        }


class ScheduledContentDetail(BaseModel):
    """
    Detailed model for scheduled content.

    This model provides full details about scheduled content including
    publish status, error messages, and TikTok video ID.
    """
    id: int = Field(
        ...,
        description="Unique identifier for the scheduled content"
    )
    content_type: str = Field(
        ...,
        description="Type of content (video or post)"
    )
    content_data: Dict[str, Any] = Field(
        ...,
        description="Full content data"
    )
    scheduled_time: datetime = Field(
        ...,
        description="When the content will be/was published"
    )
    status: str = Field(
        ...,
        description="Current status (pending, published, failed)"
    )
    retry_count: int = Field(
        ...,
        description="Number of publish attempts made"
    )
    max_retries: int = Field(
        ...,
        description="Maximum number of retry attempts allowed"
    )
    tiktok_video_id: Optional[str] = Field(
        None,
        description="TikTok video/post ID after successful publish"
    )
    error_message: Optional[str] = Field(
        None,
        description="Error details if publishing failed"
    )
    created_at: datetime = Field(
        ...,
        description="When the schedule was created"
    )
    updated_at: datetime = Field(
        ...,
        description="When the record was last updated"
    )
    published_at: Optional[datetime] = Field(
        None,
        description="When the content was successfully published"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "id": 123,
                "content_type": "video",
                "content_data": {
                    "video_url": "https://example.com/videos/product-demo.mp4",
                    "title": "Check out our new tactical backpack!",
                    "description": "Perfect for urban professionals",
                    "product_ids": ["prod_12345"],
                    "tags": ["tactical", "edc"]
                },
                "scheduled_time": "2024-12-31T12:00:00Z",
                "status": "published",
                "retry_count": 0,
                "max_retries": 3,
                "tiktok_video_id": "7123456789012345678",
                "error_message": None,
                "created_at": "2024-12-20T10:30:00Z",
                "updated_at": "2024-12-31T12:01:00Z",
                "published_at": "2024-12-31T12:00:30Z"
            }
        }


class BulkScheduleRequest(BaseModel):
    """
    Request model for bulk content scheduling.

    This model handles multiple content scheduling requests in a single API call.
    """
    items: List[ScheduleContentRequest] = Field(
        ...,
        min_length=1,
        max_length=100,
        description="List of content items to schedule (1-100 items)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "items": [
                    {
                        "content_type": "video",
                        "content_data": {
                            "video_url": "https://example.com/videos/video1.mp4",
                            "title": "Product Demo 1",
                            "product_ids": ["prod_12345"]
                        },
                        "scheduled_time": "2024-12-31T12:00:00Z",
                        "max_retries": 3
                    },
                    {
                        "content_type": "post",
                        "content_data": {
                            "content": "Check out our new products!",
                            "product_ids": ["prod_67890"]
                        },
                        "scheduled_time": "2024-12-31T18:00:00Z",
                        "max_retries": 3
                    }
                ]
            }
        }


class BulkScheduleResponse(BaseModel):
    """
    Response model for bulk content scheduling.

    This model provides the results of bulk scheduling operations.
    """
    scheduled: List[ScheduleContentResponse] = Field(
        ...,
        description="Successfully scheduled content items"
    )
    failed: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Failed items with error details"
    )
    total_requested: int = Field(
        ...,
        description="Total number of items in the request"
    )
    total_scheduled: int = Field(
        ...,
        description="Number of successfully scheduled items"
    )
    total_failed: int = Field(
        ...,
        description="Number of failed items"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "scheduled": [
                    {
                        "id": 123,
                        "content_type": "video",
                        "status": "pending",
                        "scheduled_time": "2024-12-31T12:00:00Z",
                        "created_at": "2024-12-20T10:30:00Z",
                        "max_retries": 3
                    },
                    {
                        "id": 124,
                        "content_type": "post",
                        "status": "pending",
                        "scheduled_time": "2024-12-31T18:00:00Z",
                        "created_at": "2024-12-20T10:30:00Z",
                        "max_retries": 3
                    }
                ],
                "failed": [],
                "total_requested": 2,
                "total_scheduled": 2,
                "total_failed": 0
            }
        }
