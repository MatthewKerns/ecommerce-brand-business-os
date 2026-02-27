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


class SEOAnalysisRequest(BaseModel):
    """
    SEO analysis request.

    This model handles SEO analysis requests for content optimization.
    """
    content: str = Field(
        ...,
        min_length=50,
        max_length=50000,
        description="Content to analyze for SEO"
    )
    target_keywords: Optional[List[str]] = Field(
        default_factory=list,
        max_length=20,
        description="Target keywords to analyze for"
    )
    url: Optional[str] = Field(
        None,
        max_length=2000,
        description="URL of the content being analyzed"
    )
    content_type: str = Field(
        default="blog",
        pattern="^(blog|product|landing_page)$",
        description="Type of content being analyzed"
    )
    include_recommendations: bool = Field(
        default=True,
        description="Whether to include optimization recommendations"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "content": "# Tactical Backpacks for Urban Professionals\n\nDiscover the best tactical backpacks...",
                "target_keywords": ["tactical backpack", "urban EDC", "professional carry"],
                "url": "https://example.com/blog/tactical-backpacks",
                "content_type": "blog",
                "include_recommendations": True
            }
        }


class KeywordResearchRequest(BaseModel):
    """
    Keyword research request.

    This model handles keyword research and discovery requests.
    """
    seed_keywords: List[str] = Field(
        ...,
        min_length=1,
        max_length=10,
        description="Seed keywords for research"
    )
    topic: str = Field(
        ...,
        min_length=5,
        max_length=500,
        description="Topic or niche for keyword research"
    )
    max_keywords: int = Field(
        default=50,
        ge=10,
        le=200,
        description="Maximum number of keywords to return"
    )
    include_long_tail: bool = Field(
        default=True,
        description="Whether to include long-tail keywords"
    )
    competitor_urls: Optional[List[str]] = Field(
        default_factory=list,
        max_length=5,
        description="Competitor URLs for keyword analysis"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "seed_keywords": ["tactical backpack", "EDC bag"],
                "topic": "Tactical gear for urban professionals",
                "max_keywords": 50,
                "include_long_tail": True,
                "competitor_urls": [
                    "https://competitor1.com/tactical-backpacks",
                    "https://competitor2.com/edc-gear"
                ]
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


class KeywordMetrics(BaseModel):
    """
    Metrics for individual keywords.

    This model captures SEO metrics for a specific keyword.
    """
    keyword: str = Field(
        ...,
        description="The keyword phrase"
    )
    search_volume: Optional[int] = Field(
        None,
        description="Estimated monthly search volume"
    )
    difficulty: Optional[float] = Field(
        None,
        ge=0.0,
        le=100.0,
        description="Keyword difficulty score (0-100)"
    )
    relevance_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Relevance to content (0-1)"
    )
    density: Optional[float] = Field(
        None,
        ge=0.0,
        le=100.0,
        description="Keyword density percentage in content"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "keyword": "tactical backpack",
                "search_volume": 12000,
                "difficulty": 45.5,
                "relevance_score": 0.92,
                "density": 2.3
            }
        }


class SEOScore(BaseModel):
    """
    SEO scoring breakdown.

    This model provides detailed SEO scoring for content.
    """
    overall_score: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Overall SEO score (0-100)"
    )
    keyword_optimization: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Keyword optimization score (0-100)"
    )
    content_quality: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Content quality score (0-100)"
    )
    readability: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Readability score (0-100)"
    )
    structure: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Content structure score (0-100)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "overall_score": 78.5,
                "keyword_optimization": 82.0,
                "content_quality": 85.5,
                "readability": 75.0,
                "structure": 70.0
            }
        }


class SEORecommendation(BaseModel):
    """
    Individual SEO recommendation.

    This model represents a single optimization recommendation.
    """
    category: str = Field(
        ...,
        pattern="^(keywords|content|structure|readability|technical)$",
        description="Category of the recommendation"
    )
    priority: str = Field(
        ...,
        pattern="^(high|medium|low)$",
        description="Priority level"
    )
    issue: str = Field(
        ...,
        description="Description of the issue"
    )
    recommendation: str = Field(
        ...,
        description="Recommended action"
    )
    impact: str = Field(
        ...,
        description="Expected impact of implementing this recommendation"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "category": "keywords",
                "priority": "high",
                "issue": "Target keyword 'tactical backpack' appears only once in content",
                "recommendation": "Increase keyword density to 1-2% by naturally incorporating the phrase 3-4 more times",
                "impact": "Improved search engine ranking for target keyword"
            }
        }


class SEOAnalysisResponse(BaseModel):
    """
    SEO analysis response.

    This model structures the response for SEO analysis requests.
    """
    request_id: str = Field(
        ...,
        description="Unique identifier for the request"
    )
    seo_score: SEOScore = Field(
        ...,
        description="SEO scoring breakdown"
    )
    keyword_analysis: List[KeywordMetrics] = Field(
        ...,
        description="Analysis of keywords in content"
    )
    recommendations: List[SEORecommendation] = Field(
        default_factory=list,
        description="SEO optimization recommendations"
    )
    content_stats: Dict[str, Any] = Field(
        ...,
        description="Content statistics (word count, headings, etc.)"
    )
    metadata: ContentMetadata = Field(
        ...,
        description="Metadata about the analysis process"
    )
    status: str = Field(
        default="success",
        description="Status of the analysis"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "request_id": "req_seo123abc",
                "seo_score": {
                    "overall_score": 78.5,
                    "keyword_optimization": 82.0,
                    "content_quality": 85.5,
                    "readability": 75.0,
                    "structure": 70.0
                },
                "keyword_analysis": [
                    {
                        "keyword": "tactical backpack",
                        "search_volume": 12000,
                        "difficulty": 45.5,
                        "relevance_score": 0.92,
                        "density": 2.3
                    }
                ],
                "recommendations": [
                    {
                        "category": "keywords",
                        "priority": "high",
                        "issue": "Target keyword density is low",
                        "recommendation": "Increase keyword usage naturally",
                        "impact": "Improved search ranking"
                    }
                ],
                "content_stats": {
                    "word_count": 1542,
                    "heading_count": 8,
                    "paragraph_count": 12,
                    "image_count": 3
                },
                "metadata": {
                    "agent": "seo_agent",
                    "model": "claude-sonnet-4-5-20250929",
                    "tokens_used": 1523,
                    "generation_time_ms": 2341,
                    "timestamp": "2024-02-26T10:30:45Z"
                },
                "status": "success"
            }
        }
