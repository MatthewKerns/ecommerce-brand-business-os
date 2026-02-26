"""
Shared pytest fixtures for AI Content Agents tests.

This module provides reusable test fixtures for:
- Mocking Anthropic API client
- Sample test data (topics, brand context)
- Temporary directories for test outputs
- Common test utilities
"""

import pytest
from pathlib import Path
from unittest.mock import Mock

from tests.fixtures.mock_responses import (
    create_mock_client,
    create_error_client,
    MOCK_BLOG_RESPONSE,
    MOCK_SOCIAL_RESPONSE,
    MOCK_EMAIL_RESPONSE,
    MOCK_VIDEO_SCRIPT_RESPONSE,
    MOCK_API_ERROR,
    create_mock_response
)


@pytest.fixture
def mock_anthropic_client():
    """
    Mock Anthropic API client that returns realistic responses.
    Used across all agent tests to avoid real API calls.
    """
    return create_mock_client(MOCK_BLOG_RESPONSE)


@pytest.fixture
def mock_blog_client():
    """Mock client for blog content generation"""
    return create_mock_client(MOCK_BLOG_RESPONSE)


@pytest.fixture
def mock_social_client():
    """Mock client for social media content generation"""
    return create_mock_client(MOCK_SOCIAL_RESPONSE)


@pytest.fixture
def mock_email_client():
    """Mock client for email content generation"""
    return create_mock_client(MOCK_EMAIL_RESPONSE)


@pytest.fixture
def mock_video_script_client():
    """Mock client for video script generation"""
    return create_mock_client(MOCK_VIDEO_SCRIPT_RESPONSE)


@pytest.fixture
def mock_error_client():
    """Mock client that raises API errors"""
    return create_error_client(MOCK_API_ERROR)


@pytest.fixture
def sample_blog_topic():
    """Sample blog topic for testing"""
    return {
        "topic": "Essential Gear for Tactical Readiness",
        "pillar": "Battle-Ready Lifestyle",
        "keywords": ["tactical gear", "EDC", "preparedness"]
    }


@pytest.fixture
def sample_social_topic():
    """Sample social media topic for testing"""
    return {
        "topic": "Daily EDC Essentials",
        "platform": "instagram",
        "keywords": ["EDC", "tactical", "preparedness"]
    }


@pytest.fixture
def temp_output_dir(tmp_path):
    """Temporary directory for test output files"""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    return output_dir


@pytest.fixture
def mock_brand_context():
    """Mock brand context files"""
    return {
        "brand_voice": "Direct, knowledgeable, empowering",
        "brand_strategy": "Position as authority in tactical lifestyle",
        "target_market": "Men 25-45 interested in preparedness"
    }


@pytest.fixture
def mock_content_response():
    """Mock content generation response"""
    return {
        "content": "This is generated test content",
        "metadata": {
            "agent": "TestAgent",
            "model": "claude-sonnet-4-5-20250929",
            "timestamp": "2025-01-01T00:00:00Z"
        }
    }
