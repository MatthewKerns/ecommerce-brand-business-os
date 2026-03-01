"""
Tests for API models (Pydantic schemas).

This module tests the validation and serialization of API request/response models.
"""

import pytest
from datetime import datetime
from api.models import (
    ContentRequest,
    ContentResponse,
    ContentMetadata,
    BlogRequest,
    SocialRequest,
    AmazonRequest,
    CompetitorRequest,
    ErrorResponse,
)


class TestContentRequest:
    """Tests for ContentRequest model."""

    def test_valid_content_request(self):
        """Test creating a valid ContentRequest."""
        request = ContentRequest(
            content_type="blog",
            prompt="Write a blog post about tactical backpacks",
            parameters={"pillar": "Battle-Ready Lifestyle"},
            metadata={"user_id": "test123"}
        )
        assert request.content_type == "blog"
        assert len(request.prompt) >= 10
        assert request.parameters["pillar"] == "Battle-Ready Lifestyle"

    def test_content_request_minimal(self):
        """Test ContentRequest with minimal required fields."""
        request = ContentRequest(
            content_type="social",
            prompt="This is a test prompt for social media"
        )
        assert request.content_type == "social"
        assert request.parameters == {}
        assert request.metadata == {}

    def test_content_request_prompt_too_short(self):
        """Test ContentRequest with prompt that's too short."""
        with pytest.raises(ValueError):
            ContentRequest(
                content_type="blog",
                prompt="short"  # Less than 10 characters
            )


class TestContentResponse:
    """Tests for ContentResponse model."""

    def test_valid_content_response(self):
        """Test creating a valid ContentResponse."""
        metadata = ContentMetadata(
            agent="blog_agent",
            model="claude-sonnet-4-5-20250929",
            tokens_used=1500,
            generation_time_ms=2500,
            timestamp=datetime.utcnow()
        )
        response = ContentResponse(
            request_id="req_123",
            content_type="blog",
            content="Generated blog content here...",
            metadata=metadata
        )
        assert response.request_id == "req_123"
        assert response.status == "success"
        assert response.metadata.agent == "blog_agent"


class TestBlogRequest:
    """Tests for BlogRequest model."""

    def test_valid_blog_request(self):
        """Test creating a valid BlogRequest."""
        request = BlogRequest(
            topic="Tactical backpacks for urban professionals",
            pillar="Battle-Ready Lifestyle",
            content_format="listicle",
            target_word_count=1500,
            seo_keywords=["tactical", "backpack", "EDC"],
            include_outline=True
        )
        assert request.topic == "Tactical backpacks for urban professionals"
        assert request.content_format == "listicle"
        assert request.target_word_count == 1500

    def test_blog_request_defaults(self):
        """Test BlogRequest with default values."""
        request = BlogRequest(
            topic="Test topic for blog content",
            pillar="Test Pillar"
        )
        assert request.content_format == "article"
        assert request.target_word_count == 1500
        assert request.seo_keywords == []
        assert request.include_outline is False


class TestSocialRequest:
    """Tests for SocialRequest model."""

    def test_valid_social_request(self):
        """Test creating a valid SocialRequest."""
        request = SocialRequest(
            platform="instagram",
            content_type="carousel",
            topic="5 EDC essentials for urban professionals",
            pillar="Battle-Ready Lifestyle",
            include_hashtags=True,
            target_audience="urban_professionals_25_40"
        )
        assert request.platform == "instagram"
        assert request.content_type == "carousel"
        assert request.include_hashtags is True


class TestAmazonRequest:
    """Tests for AmazonRequest model."""

    def test_valid_amazon_request(self):
        """Test creating a valid AmazonRequest."""
        request = AmazonRequest(
            product_name="Tactical EDC Backpack - 30L",
            listing_type="bullets",
            product_features=[
                "Water-resistant 1000D nylon",
                "MOLLE webbing system",
                "Laptop compartment up to 17 inches"
            ],
            target_keywords=["tactical backpack", "EDC bag", "MOLLE backpack"],
            competitor_asins=["B07XYZ123", "B08ABC456"]
        )
        assert request.product_name == "Tactical EDC Backpack - 30L"
        assert request.listing_type == "bullets"
        assert len(request.product_features) == 3
        assert len(request.target_keywords) == 3


class TestCompetitorRequest:
    """Tests for CompetitorRequest model."""

    def test_valid_competitor_request(self):
        """Test creating a valid CompetitorRequest."""
        request = CompetitorRequest(
            analysis_type="amazon_listing",
            competitor_url="https://www.amazon.com/dp/B07XYZ123",
            focus_areas=["features", "benefits", "positioning"],
            extract_keywords=True
        )
        assert request.analysis_type == "amazon_listing"
        assert request.competitor_url == "https://www.amazon.com/dp/B07XYZ123"
        assert len(request.focus_areas) == 3


class TestErrorResponse:
    """Tests for ErrorResponse model."""

    def test_valid_error_response(self):
        """Test creating a valid ErrorResponse."""
        response = ErrorResponse(
            error="ValidationError",
            message="Invalid content_type parameter",
            details={"field": "content_type", "value": "unknown"},
            request_id="req_abc123",
            timestamp=datetime.utcnow()
        )
        assert response.error == "ValidationError"
        assert response.message == "Invalid content_type parameter"
        assert response.details["field"] == "content_type"


def test_models_import():
    """Test that all models can be imported successfully."""
    assert ContentRequest is not None
    assert ContentResponse is not None
    assert BlogRequest is not None
    assert SocialRequest is not None
    assert AmazonRequest is not None
    assert CompetitorRequest is not None
    assert ErrorResponse is not None
    assert ContentMetadata is not None
