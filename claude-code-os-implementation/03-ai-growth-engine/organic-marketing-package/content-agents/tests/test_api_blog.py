"""
Integration tests for blog API endpoints.

Tests cover:
- Blog post generation endpoint
- Blog series generation endpoint
- Listicle generation endpoint
- How-to guide generation endpoint
- Request validation
- Error handling
- Response structure
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock, MagicMock
from pathlib import Path
from datetime import datetime

from api.main import app
from agents.blog_agent import BlogAgent


class TestBlogPostGeneration:
    """Test suite for /api/blog/generate endpoint"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    @pytest.fixture
    def mock_blog_agent(self):
        """Mock BlogAgent for testing"""
        with patch('api.routes.blog.BlogAgent') as mock_agent_class:
            mock_agent = Mock(spec=BlogAgent)
            mock_agent.generate_blog_post.return_value = (
                "# Test Blog Post\n\nThis is test content.",
                Path("/tmp/test_blog.md"),
                None  # seo_analysis (None when include_seo_analysis=False)
            )
            mock_agent_class.return_value = mock_agent
            yield mock_agent

    def test_generate_blog_post_success(self, client, mock_blog_agent):
        """Test successful blog post generation"""
        request_data = {
            "topic": "How to Organize Your Trading Card Collection",
            "content_pillar": "Gear & Equipment",
            "target_keywords": ["trading cards", "organization"],
            "word_count": 1500,
            "include_cta": True
        }

        response = client.post("/api/blog/generate", json=request_data)

        assert response.status_code == 200
        data = response.json()

        assert "request_id" in data
        assert "content" in data
        assert "file_path" in data
        assert "metadata" in data
        assert data["status"] == "success"

    def test_generate_blog_post_minimal_request(self, client, mock_blog_agent):
        """Test blog post generation with minimal required fields"""
        request_data = {
            "topic": "Essential Tournament Gear for TCG Players"
        }

        response = client.post("/api/blog/generate", json=request_data)

        assert response.status_code == 200
        data = response.json()

        # Should use default values
        assert data["status"] == "success"

        # Verify agent was called with defaults
        mock_blog_agent.generate_blog_post.assert_called_once()
        call_kwargs = mock_blog_agent.generate_blog_post.call_args.kwargs

        assert call_kwargs["topic"] == "Essential Tournament Gear for TCG Players"
        assert call_kwargs["word_count"] == 1000  # Default value
        assert call_kwargs["include_cta"] is True  # Default value

    def test_generate_blog_post_with_custom_request_id(self, client, mock_blog_agent):
        """Test blog post generation with custom request ID in header"""
        request_data = {
            "topic": "How to Store Trading Cards Properly"
        }

        response = client.post(
            "/api/blog/generate",
            json=request_data,
            headers={"X-Request-ID": "custom-request-123"}
        )

        assert response.status_code == 200
        data = response.json()

        assert data["request_id"] == "custom-request-123"

    def test_generate_blog_post_metadata_structure(self, client, mock_blog_agent):
        """Test that response metadata has correct structure"""
        request_data = {
            "topic": "Tournament Preparation Checklist"
        }

        response = client.post("/api/blog/generate", json=request_data)
        data = response.json()

        metadata = data["metadata"]

        assert "agent" in metadata
        assert "model" in metadata
        assert "tokens_used" in metadata
        assert "generation_time_ms" in metadata
        assert "timestamp" in metadata

        assert metadata["agent"] == "blog_agent"
        assert isinstance(metadata["generation_time_ms"], int)

    def test_generate_blog_post_invalid_topic_too_short(self, client):
        """Test validation error for topic that's too short"""
        request_data = {
            "topic": "Short"  # Less than 10 characters
        }

        response = client.post("/api/blog/generate", json=request_data)

        assert response.status_code == 422  # Validation error

    def test_generate_blog_post_invalid_word_count(self, client):
        """Test validation error for invalid word count"""
        request_data = {
            "topic": "How to Organize Your Collection",
            "word_count": 100  # Less than minimum (300)
        }

        response = client.post("/api/blog/generate", json=request_data)

        assert response.status_code == 422  # Validation error

    def test_generate_blog_post_missing_required_field(self, client):
        """Test validation error when required field is missing"""
        request_data = {
            "content_pillar": "Gear & Equipment"
            # Missing required 'topic' field
        }

        response = client.post("/api/blog/generate", json=request_data)

        assert response.status_code == 422  # Validation error

    def test_generate_blog_post_agent_error(self, client):
        """Test error handling when agent raises exception"""
        with patch('api.routes.blog.BlogAgent') as mock_agent_class:
            mock_agent = Mock()
            mock_agent.generate_blog_post.side_effect = Exception("Agent error")
            mock_agent_class.return_value = mock_agent

            request_data = {
                "topic": "Test Topic for Error Handling"
            }

            response = client.post("/api/blog/generate", json=request_data)

            assert response.status_code == 500
            data = response.json()

            assert "detail" in data
            assert "BlogGenerationError" in str(data["detail"])


class TestBlogSeriesGeneration:
    """Test suite for /api/blog/series endpoint"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    @pytest.fixture
    def mock_blog_agent(self):
        """Mock BlogAgent for testing"""
        with patch('api.routes.blog.BlogAgent') as mock_agent_class:
            mock_agent = Mock(spec=BlogAgent)
            mock_agent.generate_blog_series.return_value = [
                ("# Blog Series Outline\n\n1. Part One\n2. Part Two", Path("/tmp/series_outline.md"))
            ]
            mock_agent_class.return_value = mock_agent
            yield mock_agent

    def test_generate_blog_series_success(self, client, mock_blog_agent):
        """Test successful blog series generation"""
        request_data = {
            "series_topic": "Complete Guide to Tournament Preparation",
            "num_posts": 5,
            "content_pillar": "Battle-Ready Lifestyle"
        }

        response = client.post("/api/blog/series", json=request_data)

        assert response.status_code == 200
        data = response.json()

        assert "request_id" in data
        assert "outline" in data
        assert "file_path" in data
        assert "num_posts" in data
        assert "metadata" in data
        assert data["status"] == "success"
        assert data["num_posts"] == 5

    def test_generate_blog_series_minimal_request(self, client, mock_blog_agent):
        """Test blog series generation with minimal fields"""
        request_data = {
            "series_topic": "Mastering Card Storage"
        }

        response = client.post("/api/blog/series", json=request_data)

        assert response.status_code == 200
        data = response.json()

        # Should use default num_posts
        assert data["num_posts"] == 3

    def test_generate_blog_series_invalid_num_posts(self, client):
        """Test validation error for invalid number of posts"""
        request_data = {
            "series_topic": "Test Series Topic",
            "num_posts": 1  # Less than minimum (2)
        }

        response = client.post("/api/blog/series", json=request_data)

        assert response.status_code == 422  # Validation error

    def test_generate_blog_series_agent_error(self, client):
        """Test error handling when series generation fails"""
        with patch('api.routes.blog.BlogAgent') as mock_agent_class:
            mock_agent = Mock()
            mock_agent.generate_blog_series.side_effect = Exception("Series generation failed")
            mock_agent_class.return_value = mock_agent

            request_data = {
                "series_topic": "Test Series Topic"
            }

            response = client.post("/api/blog/series", json=request_data)

            assert response.status_code == 500
            data = response.json()

            assert "BlogSeriesGenerationError" in str(data["detail"])


class TestListicleGeneration:
    """Test suite for /api/blog/listicle endpoint"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    @pytest.fixture
    def mock_blog_agent(self):
        """Mock BlogAgent for testing"""
        with patch('api.routes.blog.BlogAgent') as mock_agent_class:
            mock_agent = Mock(spec=BlogAgent)
            mock_agent.generate_listicle.return_value = (
                "# Top 10 Items\n\n1. First item\n2. Second item",
                Path("/tmp/listicle.md")
            )
            mock_agent_class.return_value = mock_agent
            yield mock_agent

    def test_generate_listicle_success(self, client, mock_blog_agent):
        """Test successful listicle generation"""
        request_data = {
            "topic": "Essential Accessories Every TCG Player Needs",
            "num_items": 10,
            "content_pillar": "Gear & Equipment"
        }

        response = client.post("/api/blog/listicle", json=request_data)

        assert response.status_code == 200
        data = response.json()

        assert "request_id" in data
        assert "content" in data
        assert "file_path" in data
        assert "metadata" in data
        assert data["status"] == "success"

    def test_generate_listicle_minimal_request(self, client, mock_blog_agent):
        """Test listicle generation with minimal fields"""
        request_data = {
            "topic": "Top Tournament Mistakes to Avoid"
        }

        response = client.post("/api/blog/listicle", json=request_data)

        assert response.status_code == 200
        data = response.json()

        # Should succeed with defaults
        assert data["status"] == "success"

        # Verify default num_items was used
        mock_blog_agent.generate_listicle.assert_called_once()
        call_kwargs = mock_blog_agent.generate_listicle.call_args.kwargs
        assert call_kwargs["num_items"] == 10  # Default value

    def test_generate_listicle_invalid_num_items(self, client):
        """Test validation error for invalid number of items"""
        request_data = {
            "topic": "Test Listicle Topic",
            "num_items": 2  # Less than minimum (3)
        }

        response = client.post("/api/blog/listicle", json=request_data)

        assert response.status_code == 422  # Validation error

    def test_generate_listicle_agent_error(self, client):
        """Test error handling when listicle generation fails"""
        with patch('api.routes.blog.BlogAgent') as mock_agent_class:
            mock_agent = Mock()
            mock_agent.generate_listicle.side_effect = Exception("Listicle generation failed")
            mock_agent_class.return_value = mock_agent

            request_data = {
                "topic": "Test Listicle Topic"
            }

            response = client.post("/api/blog/listicle", json=request_data)

            assert response.status_code == 500
            data = response.json()

            assert "ListicleGenerationError" in str(data["detail"])


class TestHowToGuideGeneration:
    """Test suite for /api/blog/how-to endpoint"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    @pytest.fixture
    def mock_blog_agent(self):
        """Mock BlogAgent for testing"""
        with patch('api.routes.blog.BlogAgent') as mock_agent_class:
            mock_agent = Mock(spec=BlogAgent)
            mock_agent.generate_how_to_guide.return_value = (
                "# How-To Guide\n\nStep 1: First step\nStep 2: Second step",
                Path("/tmp/how_to_guide.md")
            )
            mock_agent_class.return_value = mock_agent
            yield mock_agent

    def test_generate_how_to_guide_success(self, client, mock_blog_agent):
        """Test successful how-to guide generation"""
        request_data = {
            "topic": "How to Double Sleeve Your Trading Cards",
            "target_audience": "Competitive players",
            "difficulty_level": "beginner"
        }

        response = client.post("/api/blog/how-to", json=request_data)

        assert response.status_code == 200
        data = response.json()

        assert "request_id" in data
        assert "content" in data
        assert "file_path" in data
        assert "metadata" in data
        assert data["status"] == "success"

    def test_generate_how_to_guide_minimal_request(self, client, mock_blog_agent):
        """Test how-to guide generation with minimal fields"""
        request_data = {
            "topic": "How to Prepare for Your First Tournament"
        }

        response = client.post("/api/blog/how-to", json=request_data)

        assert response.status_code == 200
        data = response.json()

        # Should use defaults
        assert data["status"] == "success"

        # Verify defaults were used
        mock_blog_agent.generate_how_to_guide.assert_called_once()
        call_kwargs = mock_blog_agent.generate_how_to_guide.call_args.kwargs
        assert call_kwargs["target_audience"] == "Tournament players"  # Default
        assert call_kwargs["difficulty_level"] == "beginner"  # Default

    def test_generate_how_to_guide_invalid_difficulty(self, client):
        """Test validation error for invalid difficulty level"""
        request_data = {
            "topic": "How to Test Validation",
            "difficulty_level": "expert"  # Not in allowed values
        }

        response = client.post("/api/blog/how-to", json=request_data)

        assert response.status_code == 422  # Validation error

    def test_generate_how_to_guide_all_difficulty_levels(self, client, mock_blog_agent):
        """Test that all valid difficulty levels are accepted"""
        valid_levels = ["beginner", "intermediate", "advanced"]

        for level in valid_levels:
            request_data = {
                "topic": f"How to Test {level.title()} Level",
                "difficulty_level": level
            }

            response = client.post("/api/blog/how-to", json=request_data)
            assert response.status_code == 200

    def test_generate_how_to_guide_agent_error(self, client):
        """Test error handling when how-to guide generation fails"""
        with patch('api.routes.blog.BlogAgent') as mock_agent_class:
            mock_agent = Mock()
            mock_agent.generate_how_to_guide.side_effect = Exception("How-to generation failed")
            mock_agent_class.return_value = mock_agent

            request_data = {
                "topic": "How to Test Error Handling"
            }

            response = client.post("/api/blog/how-to", json=request_data)

            assert response.status_code == 500
            data = response.json()

            assert "HowToGuideGenerationError" in str(data["detail"])


class TestBlogAPIRequestValidation:
    """Test suite for blog API request validation"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    def test_invalid_json_body(self, client):
        """Test that invalid JSON returns proper error"""
        response = client.post(
            "/api/blog/generate",
            data="not valid json",
            headers={"Content-Type": "application/json"}
        )

        assert response.status_code == 422

    def test_empty_request_body(self, client):
        """Test that empty request body returns validation error"""
        response = client.post("/api/blog/generate", json={})

        assert response.status_code == 422

    def test_response_content_type(self, client):
        """Test that responses have correct content type"""
        with patch('api.routes.blog.BlogAgent') as mock_agent_class:
            mock_agent = Mock()
            mock_agent.generate_blog_post.return_value = (
                "Test content",
                Path("/tmp/test.md"),
                None  # seo_analysis
            )
            mock_agent_class.return_value = mock_agent

            request_data = {
                "topic": "Test Content Type Response"
            }

            response = client.post("/api/blog/generate", json=request_data)

            assert "application/json" in response.headers["content-type"]
