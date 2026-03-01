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


class KlaviyoProfileLocationRequest(BaseModel):
    """
    Location data for Klaviyo customer profiles.

    This model handles geographic location information for customer profiles.
    """
    address1: Optional[str] = Field(
        None,
        max_length=200,
        description="First line of address"
    )
    address2: Optional[str] = Field(
        None,
        max_length=200,
        description="Second line of address"
    )
    city: Optional[str] = Field(
        None,
        max_length=100,
        description="City name"
    )
    country: Optional[str] = Field(
        None,
        max_length=100,
        description="Country name or code"
    )
    region: Optional[str] = Field(
        None,
        max_length=100,
        description="State/province/region"
    )
    zip: Optional[str] = Field(
        None,
        max_length=20,
        description="Postal/ZIP code"
    )
    timezone: Optional[str] = Field(
        None,
        description="IANA timezone (e.g., 'America/New_York')"
    )
    latitude: Optional[float] = Field(
        None,
        ge=-90,
        le=90,
        description="Geographic latitude"
    )
    longitude: Optional[float] = Field(
        None,
        ge=-180,
        le=180,
        description="Geographic longitude"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "city": "San Francisco",
                "region": "CA",
                "country": "United States",
                "zip": "94102",
                "timezone": "America/Los_Angeles"
            }
        }


class KlaviyoProfileRequest(BaseModel):
    """
    Klaviyo customer profile request.

    This model handles requests for creating or updating customer profiles in Klaviyo.
    """
    email: str = Field(
        ...,
        pattern="^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\\.[a-zA-Z0-9-.]+$",
        description="Email address (required)"
    )
    phone_number: Optional[str] = Field(
        None,
        description="Phone number with country code (e.g., +1234567890)"
    )
    external_id: Optional[str] = Field(
        None,
        description="External ID from your system"
    )
    first_name: Optional[str] = Field(
        None,
        max_length=100,
        description="First name"
    )
    last_name: Optional[str] = Field(
        None,
        max_length=100,
        description="Last name"
    )
    organization: Optional[str] = Field(
        None,
        max_length=200,
        description="Organization name"
    )
    title: Optional[str] = Field(
        None,
        max_length=100,
        description="Job title"
    )
    location: Optional[KlaviyoProfileLocationRequest] = Field(
        None,
        description="Geographic location"
    )
    properties: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Custom properties"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "email": "customer@example.com",
                "phone_number": "+14155551234",
                "first_name": "John",
                "last_name": "Doe",
                "external_id": "customer_12345",
                "location": {
                    "city": "San Francisco",
                    "region": "CA",
                    "country": "United States",
                    "zip": "94102"
                },
                "properties": {
                    "customer_tier": "VIP",
                    "lifetime_value": 5000.00
                }
            }
        }


class KlaviyoEventRequest(BaseModel):
    """
    Klaviyo event tracking request.

    This model handles requests for tracking customer events and behaviors in Klaviyo.
    """
    metric_name: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Name of the event/metric (e.g., 'Placed Order', 'Viewed Product')"
    )
    customer_email: str = Field(
        ...,
        pattern="^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\\.[a-zA-Z0-9-.]+$",
        description="Email of the customer who triggered the event"
    )
    customer_phone: Optional[str] = Field(
        None,
        description="Phone number of the customer"
    )
    customer_external_id: Optional[str] = Field(
        None,
        description="External ID of the customer"
    )
    properties: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Event properties (e.g., product details, order value)"
    )
    time: Optional[datetime] = Field(
        None,
        description="Timestamp of the event (defaults to now)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "metric_name": "Placed Order",
                "customer_email": "customer@example.com",
                "properties": {
                    "order_id": "ORD-12345",
                    "total": 149.99,
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
