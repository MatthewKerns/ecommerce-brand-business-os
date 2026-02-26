"""
Integration tests for social media API endpoints.

Tests cover:
- Instagram post generation endpoint
- Reddit post generation endpoint
- Content calendar generation endpoint
- Carousel script generation endpoint
- Batch post generation endpoint
- Request validation
- Error handling
- Response structure
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock
from pathlib import Path
from datetime import datetime

from api.main import app
from agents.social_agent import SocialAgent


class TestInstagramPostGeneration:
    """Test suite for /api/social/instagram endpoint"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    @pytest.fixture
    def mock_social_agent(self):
        """Mock SocialAgent for testing"""
        with patch('api.routes.social.SocialAgent') as mock_agent_class:
            mock_agent = Mock(spec=SocialAgent)
            mock_agent.generate_instagram_post.return_value = (
                "Test Instagram post caption #hashtags",
                Path("/tmp/instagram_post.txt")
            )
            mock_agent_class.return_value = mock_agent
            yield mock_agent

    def test_generate_instagram_post_success(self, client, mock_social_agent):
        """Test successful Instagram post generation"""
        request_data = {
            "topic": "Tournament preparation checklist for TCG players",
            "content_pillar": "Battle-Ready Lifestyle",
            "image_description": "Player organizing cards in binder",
            "include_hashtags": True
        }

        response = client.post("/api/social/instagram", json=request_data)

        assert response.status_code == 200
        data = response.json()

        assert "request_id" in data
        assert "content" in data
        assert "file_path" in data
        assert "metadata" in data
        assert data["status"] == "success"

    def test_generate_instagram_post_minimal_request(self, client, mock_social_agent):
        """Test Instagram post generation with minimal fields"""
        request_data = {
            "topic": "Essential gear for tournament players"
        }

        response = client.post("/api/social/instagram", json=request_data)

        assert response.status_code == 200
        data = response.json()

        # Should use default values
        assert data["status"] == "success"

        # Verify agent was called with defaults
        mock_social_agent.generate_instagram_post.assert_called_once()
        call_kwargs = mock_social_agent.generate_instagram_post.call_args.kwargs
        assert call_kwargs["include_hashtags"] is True  # Default value

    def test_generate_instagram_post_without_hashtags(self, client, mock_social_agent):
        """Test Instagram post generation without hashtags"""
        request_data = {
            "topic": "Product showcase post",
            "include_hashtags": False
        }

        response = client.post("/api/social/instagram", json=request_data)

        assert response.status_code == 200

        # Verify include_hashtags was passed correctly
        call_kwargs = mock_social_agent.generate_instagram_post.call_args.kwargs
        assert call_kwargs["include_hashtags"] is False

    def test_generate_instagram_post_metadata_structure(self, client, mock_social_agent):
        """Test that response metadata has correct structure"""
        request_data = {
            "topic": "Daily tournament prep routine"
        }

        response = client.post("/api/social/instagram", json=request_data)
        data = response.json()

        metadata = data["metadata"]

        assert "agent" in metadata
        assert "model" in metadata
        assert "tokens_used" in metadata
        assert "generation_time_ms" in metadata
        assert "timestamp" in metadata

        assert metadata["agent"] == "social_agent"
        assert isinstance(metadata["generation_time_ms"], int)

    def test_generate_instagram_post_invalid_topic_too_short(self, client):
        """Test validation error for topic that's too short"""
        request_data = {
            "topic": "Short"  # Less than 10 characters
        }

        response = client.post("/api/social/instagram", json=request_data)

        assert response.status_code == 422  # Validation error

    def test_generate_instagram_post_agent_error(self, client):
        """Test error handling when agent raises exception"""
        with patch('api.routes.social.SocialAgent') as mock_agent_class:
            mock_agent = Mock()
            mock_agent.generate_instagram_post.side_effect = Exception("Agent error")
            mock_agent_class.return_value = mock_agent

            request_data = {
                "topic": "Test error handling"
            }

            response = client.post("/api/social/instagram", json=request_data)

            assert response.status_code == 500
            data = response.json()

            assert "detail" in data
            assert "Failed to generate Instagram post" in str(data["detail"])


class TestRedditPostGeneration:
    """Test suite for /api/social/reddit endpoint"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    @pytest.fixture
    def mock_social_agent(self):
        """Mock SocialAgent for testing"""
        with patch('api.routes.social.SocialAgent') as mock_agent_class:
            mock_agent = Mock(spec=SocialAgent)
            mock_agent.generate_reddit_post.return_value = (
                "Title: Test Post\n\nBody: Test content for Reddit",
                Path("/tmp/reddit_post.txt")
            )
            mock_agent_class.return_value = mock_agent
            yield mock_agent

    def test_generate_reddit_post_success(self, client, mock_social_agent):
        """Test successful Reddit post generation"""
        request_data = {
            "subreddit": "PokemonTCG",
            "topic": "Best practices for storing rare cards long-term",
            "post_type": "guide",
            "include_product_mention": False
        }

        response = client.post("/api/social/reddit", json=request_data)

        assert response.status_code == 200
        data = response.json()

        assert "request_id" in data
        assert "content" in data
        assert "file_path" in data
        assert "metadata" in data
        assert data["status"] == "success"

    def test_generate_reddit_post_minimal_request(self, client, mock_social_agent):
        """Test Reddit post generation with minimal fields"""
        request_data = {
            "subreddit": "mtg",
            "topic": "Tips for organizing your collection"
        }

        response = client.post("/api/social/reddit", json=request_data)

        assert response.status_code == 200
        data = response.json()

        # Should use defaults
        assert data["status"] == "success"

        # Verify defaults were used
        call_kwargs = mock_social_agent.generate_reddit_post.call_args.kwargs
        assert call_kwargs["post_type"] == "discussion"  # Default
        assert call_kwargs["include_product_mention"] is False  # Default

    def test_generate_reddit_post_all_post_types(self, client, mock_social_agent):
        """Test that all valid post types are accepted"""
        valid_types = ["discussion", "question", "guide", "showcase"]

        for post_type in valid_types:
            request_data = {
                "subreddit": "tcgcollecting",
                "topic": f"Test {post_type} post",
                "post_type": post_type
            }

            response = client.post("/api/social/reddit", json=request_data)
            assert response.status_code == 200

    def test_generate_reddit_post_invalid_post_type(self, client):
        """Test validation error for invalid post type"""
        request_data = {
            "subreddit": "tcg",
            "topic": "Test validation",
            "post_type": "invalid_type"
        }

        response = client.post("/api/social/reddit", json=request_data)

        assert response.status_code == 422  # Validation error

    def test_generate_reddit_post_with_product_mention(self, client, mock_social_agent):
        """Test Reddit post generation with product mention"""
        request_data = {
            "subreddit": "yugioh",
            "topic": "Tournament preparation tips",
            "include_product_mention": True
        }

        response = client.post("/api/social/reddit", json=request_data)

        assert response.status_code == 200

        # Verify include_product_mention was passed correctly
        call_kwargs = mock_social_agent.generate_reddit_post.call_args.kwargs
        assert call_kwargs["include_product_mention"] is True

    def test_generate_reddit_post_agent_error(self, client):
        """Test error handling when Reddit post generation fails"""
        with patch('api.routes.social.SocialAgent') as mock_agent_class:
            mock_agent = Mock()
            mock_agent.generate_reddit_post.side_effect = Exception("Reddit post failed")
            mock_agent_class.return_value = mock_agent

            request_data = {
                "subreddit": "test",
                "topic": "Test error handling"
            }

            response = client.post("/api/social/reddit", json=request_data)

            assert response.status_code == 500
            data = response.json()

            assert "Failed to generate Reddit post" in str(data["detail"])


class TestContentCalendarGeneration:
    """Test suite for /api/social/calendar endpoint"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    @pytest.fixture
    def mock_social_agent(self):
        """Mock SocialAgent for testing"""
        with patch('api.routes.social.SocialAgent') as mock_agent_class:
            mock_agent = Mock(spec=SocialAgent)
            mock_agent.generate_content_calendar.return_value = (
                "Content Calendar:\nDay 1: Post about...\nDay 2: Post about...",
                Path("/tmp/content_calendar.txt")
            )
            mock_agent_class.return_value = mock_agent
            yield mock_agent

    def test_generate_content_calendar_success(self, client, mock_social_agent):
        """Test successful content calendar generation"""
        request_data = {
            "platform": "instagram",
            "num_days": 7,
            "content_pillar": "Gear & Equipment"
        }

        response = client.post("/api/social/calendar", json=request_data)

        assert response.status_code == 200
        data = response.json()

        assert "request_id" in data
        assert "content" in data
        assert "file_path" in data
        assert "metadata" in data
        assert data["status"] == "success"

    def test_generate_content_calendar_minimal_request(self, client, mock_social_agent):
        """Test content calendar generation with minimal fields"""
        request_data = {
            "platform": "reddit"
        }

        response = client.post("/api/social/calendar", json=request_data)

        assert response.status_code == 200
        data = response.json()

        # Should use default num_days
        assert data["status"] == "success"

        # Verify default was used
        call_kwargs = mock_social_agent.generate_content_calendar.call_args.kwargs
        assert call_kwargs["num_days"] == 7  # Default value

    def test_generate_content_calendar_all_platforms(self, client, mock_social_agent):
        """Test that all valid platforms are accepted"""
        valid_platforms = ["instagram", "reddit", "discord", "twitter"]

        for platform in valid_platforms:
            request_data = {
                "platform": platform,
                "num_days": 7
            }

            response = client.post("/api/social/calendar", json=request_data)
            assert response.status_code == 200

    def test_generate_content_calendar_invalid_platform(self, client):
        """Test validation error for invalid platform"""
        request_data = {
            "platform": "invalid_platform",
            "num_days": 7
        }

        response = client.post("/api/social/calendar", json=request_data)

        assert response.status_code == 422  # Validation error

    def test_generate_content_calendar_invalid_num_days(self, client):
        """Test validation error for invalid number of days"""
        request_data = {
            "platform": "instagram",
            "num_days": 0  # Less than minimum (1)
        }

        response = client.post("/api/social/calendar", json=request_data)

        assert response.status_code == 422  # Validation error

    def test_generate_content_calendar_agent_error(self, client):
        """Test error handling when calendar generation fails"""
        with patch('api.routes.social.SocialAgent') as mock_agent_class:
            mock_agent = Mock()
            mock_agent.generate_content_calendar.side_effect = Exception("Calendar failed")
            mock_agent_class.return_value = mock_agent

            request_data = {
                "platform": "instagram",
                "num_days": 7
            }

            response = client.post("/api/social/calendar", json=request_data)

            assert response.status_code == 500
            data = response.json()

            assert "Failed to generate content calendar" in str(data["detail"])


class TestCarouselScriptGeneration:
    """Test suite for /api/social/carousel endpoint"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    @pytest.fixture
    def mock_social_agent(self):
        """Mock SocialAgent for testing"""
        with patch('api.routes.social.SocialAgent') as mock_agent_class:
            mock_agent = Mock(spec=SocialAgent)
            mock_agent.generate_carousel_script.return_value = (
                "Slide 1: Intro\nSlide 2: Point 1\nSlide 3: Point 2",
                Path("/tmp/carousel_script.txt")
            )
            mock_agent_class.return_value = mock_agent
            yield mock_agent

    def test_generate_carousel_script_success(self, client, mock_social_agent):
        """Test successful carousel script generation"""
        request_data = {
            "topic": "10 Must-Have Accessories for Tournament Players",
            "num_slides": 10
        }

        response = client.post("/api/social/carousel", json=request_data)

        assert response.status_code == 200
        data = response.json()

        assert "request_id" in data
        assert "content" in data
        assert "file_path" in data
        assert "metadata" in data
        assert data["status"] == "success"

    def test_generate_carousel_script_minimal_request(self, client, mock_social_agent):
        """Test carousel script generation with minimal fields"""
        request_data = {
            "topic": "Tournament preparation essentials"
        }

        response = client.post("/api/social/carousel", json=request_data)

        assert response.status_code == 200
        data = response.json()

        # Should use default num_slides
        assert data["status"] == "success"

        # Verify default was used
        call_kwargs = mock_social_agent.generate_carousel_script.call_args.kwargs
        assert call_kwargs["num_slides"] == 10  # Default value

    def test_generate_carousel_script_invalid_num_slides(self, client):
        """Test validation error for invalid number of slides"""
        request_data = {
            "topic": "Test carousel",
            "num_slides": 2  # Less than minimum (3)
        }

        response = client.post("/api/social/carousel", json=request_data)

        assert response.status_code == 422  # Validation error

    def test_generate_carousel_script_max_slides(self, client, mock_social_agent):
        """Test carousel script generation with maximum slides"""
        request_data = {
            "topic": "Comprehensive tournament guide",
            "num_slides": 10  # Maximum allowed
        }

        response = client.post("/api/social/carousel", json=request_data)

        assert response.status_code == 200

    def test_generate_carousel_script_agent_error(self, client):
        """Test error handling when carousel generation fails"""
        with patch('api.routes.social.SocialAgent') as mock_agent_class:
            mock_agent = Mock()
            mock_agent.generate_carousel_script.side_effect = Exception("Carousel failed")
            mock_agent_class.return_value = mock_agent

            request_data = {
                "topic": "Test error handling"
            }

            response = client.post("/api/social/carousel", json=request_data)

            assert response.status_code == 500
            data = response.json()

            assert "Failed to generate carousel script" in str(data["detail"])


class TestBatchPostsGeneration:
    """Test suite for /api/social/batch endpoint"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    @pytest.fixture
    def mock_social_agent(self):
        """Mock SocialAgent for testing"""
        with patch('api.routes.social.SocialAgent') as mock_agent_class:
            mock_agent = Mock(spec=SocialAgent)
            mock_agent.batch_generate_posts.return_value = [
                ("Post 1 content", Path("/tmp/post1.txt")),
                ("Post 2 content", Path("/tmp/post2.txt")),
                ("Post 3 content", Path("/tmp/post3.txt"))
            ]
            mock_agent_class.return_value = mock_agent
            yield mock_agent

    def test_batch_generate_posts_success(self, client, mock_social_agent):
        """Test successful batch post generation"""
        request_data = {
            "platform": "instagram",
            "num_posts": 5,
            "content_mix": ["Battle-Ready Lifestyle", "Gear & Equipment"]
        }

        response = client.post("/api/social/batch", json=request_data)

        assert response.status_code == 200
        data = response.json()

        assert "request_id" in data
        assert "posts" in data
        assert "total_generated" in data
        assert "metadata" in data
        assert data["status"] == "success"

        # Check posts structure
        assert isinstance(data["posts"], list)
        assert len(data["posts"]) == 3  # Mocked to return 3 posts

        # Each post should have content and file_path
        for post in data["posts"]:
            assert "content" in post
            assert "file_path" in post

    def test_batch_generate_posts_minimal_request(self, client, mock_social_agent):
        """Test batch generation with minimal fields"""
        request_data = {
            "platform": "instagram"
        }

        response = client.post("/api/social/batch", json=request_data)

        assert response.status_code == 200
        data = response.json()

        # Should use default num_posts
        assert data["status"] == "success"

        # Verify default was used
        call_kwargs = mock_social_agent.batch_generate_posts.call_args.kwargs
        assert call_kwargs["num_posts"] == 5  # Default value

    def test_batch_generate_posts_valid_platforms(self, client, mock_social_agent):
        """Test that valid platforms are accepted for batch generation"""
        valid_platforms = ["instagram", "reddit"]

        for platform in valid_platforms:
            request_data = {
                "platform": platform,
                "num_posts": 3
            }

            response = client.post("/api/social/batch", json=request_data)
            assert response.status_code == 200

    def test_batch_generate_posts_invalid_platform(self, client):
        """Test validation error for invalid platform in batch generation"""
        request_data = {
            "platform": "twitter",  # Not allowed for batch generation
            "num_posts": 3
        }

        response = client.post("/api/social/batch", json=request_data)

        assert response.status_code == 422  # Validation error

    def test_batch_generate_posts_invalid_num_posts(self, client):
        """Test validation error for invalid number of posts"""
        request_data = {
            "platform": "instagram",
            "num_posts": 0  # Less than minimum (1)
        }

        response = client.post("/api/social/batch", json=request_data)

        assert response.status_code == 422  # Validation error

    def test_batch_generate_posts_with_content_mix(self, client, mock_social_agent):
        """Test batch generation with content mix specified"""
        request_data = {
            "platform": "instagram",
            "num_posts": 3,
            "content_mix": ["Battle-Ready Lifestyle", "Community & Culture"]
        }

        response = client.post("/api/social/batch", json=request_data)

        assert response.status_code == 200

        # Verify content_mix was passed correctly
        call_kwargs = mock_social_agent.batch_generate_posts.call_args.kwargs
        assert call_kwargs["content_mix"] == ["Battle-Ready Lifestyle", "Community & Culture"]

    def test_batch_generate_posts_agent_error(self, client):
        """Test error handling when batch generation fails"""
        with patch('api.routes.social.SocialAgent') as mock_agent_class:
            mock_agent = Mock()
            mock_agent.batch_generate_posts.side_effect = Exception("Batch generation failed")
            mock_agent_class.return_value = mock_agent

            request_data = {
                "platform": "instagram",
                "num_posts": 3
            }

            response = client.post("/api/social/batch", json=request_data)

            assert response.status_code == 500
            data = response.json()

            assert "Failed to batch generate posts" in str(data["detail"])

    def test_batch_generate_posts_total_generated_count(self, client, mock_social_agent):
        """Test that total_generated matches the number of posts returned"""
        request_data = {
            "platform": "instagram",
            "num_posts": 5
        }

        response = client.post("/api/social/batch", json=request_data)
        data = response.json()

        assert data["total_generated"] == len(data["posts"])


class TestSocialAPIRequestValidation:
    """Test suite for social API request validation"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    def test_invalid_json_body(self, client):
        """Test that invalid JSON returns proper error"""
        response = client.post(
            "/api/social/instagram",
            data="not valid json",
            headers={"Content-Type": "application/json"}
        )

        assert response.status_code == 422

    def test_empty_request_body(self, client):
        """Test that empty request body returns validation error"""
        response = client.post("/api/social/instagram", json={})

        assert response.status_code == 422

    def test_missing_required_fields(self, client):
        """Test validation error when required fields are missing"""
        # Instagram endpoint requires 'topic'
        response = client.post("/api/social/instagram", json={
            "content_pillar": "Gear & Equipment"
        })

        assert response.status_code == 422

    def test_response_content_type(self, client):
        """Test that responses have correct content type"""
        with patch('api.routes.social.SocialAgent') as mock_agent_class:
            mock_agent = Mock()
            mock_agent.generate_instagram_post.return_value = (
                "Test content",
                Path("/tmp/test.txt")
            )
            mock_agent_class.return_value = mock_agent

            request_data = {
                "topic": "Test content type response"
            }

            response = client.post("/api/social/instagram", json=request_data)

            assert "application/json" in response.headers["content-type"]

    def test_custom_request_id_header(self, client):
        """Test that custom request ID is used when provided"""
        with patch('api.routes.social.SocialAgent') as mock_agent_class:
            mock_agent = Mock()
            mock_agent.generate_instagram_post.return_value = (
                "Test content",
                Path("/tmp/test.txt")
            )
            mock_agent_class.return_value = mock_agent

            request_data = {
                "topic": "Test custom request ID"
            }

            response = client.post(
                "/api/social/instagram",
                json=request_data,
                headers={"X-Request-ID": "custom-123"}
            )

            assert response.status_code == 200
            data = response.json()
            assert data["request_id"] == "custom-123"
