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


@pytest.fixture
def mock_anthropic_client():
    """
    Mock Anthropic API client that returns realistic responses.
    Used across all agent tests to avoid real API calls.
    """
    mock = Mock()
    mock.messages.create.return_value = Mock(
        content=[Mock(text="Generated blog content about test topic")]
    )
    return mock


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
