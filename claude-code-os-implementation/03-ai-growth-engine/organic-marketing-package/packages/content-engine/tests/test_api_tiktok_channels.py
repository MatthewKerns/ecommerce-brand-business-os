"""
Integration tests for TikTok channels API endpoints.

Tests cover:
- List all channels endpoint
- Get specific channel endpoint
- Create channel endpoint
- Update channel endpoint
- Deactivate channel endpoint
- Channel metrics endpoint
- Content generation endpoint
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
from agents.tiktok_channel_agent import TikTokChannelAgent


class TestListChannels:
    """Test suite for GET /api/tiktok-channels endpoint"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    @pytest.fixture
    def mock_channel_agent(self):
        """Mock TikTokChannelAgent for testing"""
        with patch('api.routes.tiktok_channels.TikTokChannelAgent') as mock_agent_class:
            mock_agent = Mock(spec=TikTokChannelAgent)
            mock_agent.list_channels.return_value = [
                {
                    "element": "air",
                    "channel_name": "QuickTCG Air",
                    "description": "Fast-paced tips",
                    "is_active": True
                },
                {
                    "element": "water",
                    "channel_name": "DeepDive Water",
                    "description": "In-depth strategies",
                    "is_active": True
                },
                {
                    "element": "fire",
                    "channel_name": "HypePlay Fire",
                    "description": "High-energy content",
                    "is_active": True
                },
                {
                    "element": "earth",
                    "channel_name": "BuildStrong Earth",
                    "description": "Foundation building",
                    "is_active": True
                }
            ]
            mock_agent_class.return_value = mock_agent
            yield mock_agent

    def test_list_all_channels_success(self, client, mock_channel_agent):
        """Test successful retrieval of all channels"""
        response = client.get("/api/tiktok-channels")

        assert response.status_code == 200
        data = response.json()

        assert "request_id" in data
        assert "channels" in data
        assert "total_channels" in data
        assert data["status"] == "success"
        assert data["total_channels"] == 4
        assert len(data["channels"]) == 4

    def test_list_all_channels_structure(self, client, mock_channel_agent):
        """Test response structure for list channels"""
        response = client.get("/api/tiktok-channels")
        data = response.json()

        # Verify each channel has expected fields
        for channel in data["channels"]:
            assert "element" in channel
            assert "channel_name" in channel
            assert "description" in channel
            assert "is_active" in channel

    def test_list_all_channels_agent_error(self, client):
        """Test error handling when agent raises exception"""
        with patch('api.routes.tiktok_channels.TikTokChannelAgent') as mock_agent_class:
            mock_agent = Mock()
            mock_agent.list_channels.side_effect = Exception("Database error")
            mock_agent_class.return_value = mock_agent

            response = client.get("/api/tiktok-channels")

            assert response.status_code == 500
            data = response.json()
            assert "detail" in data
            assert "Failed to list channels" in str(data["detail"])


class TestGetChannel:
    """Test suite for GET /api/tiktok-channels/{channel_element} endpoint"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    @pytest.fixture
    def mock_channel_agent(self):
        """Mock TikTokChannelAgent for testing"""
        with patch('api.routes.tiktok_channels.TikTokChannelAgent') as mock_agent_class:
            mock_agent = Mock(spec=TikTokChannelAgent)
            mock_agent.get_channel.return_value = {
                "element": "air",
                "channel_name": "QuickTCG Air",
                "description": "Fast-paced tournament tips and deck techs",
                "target_audience": "Competitive players seeking quick wins",
                "posting_schedule": {
                    "frequency": "daily",
                    "days": ["Mon", "Tue", "Wed", "Thu", "Fri"],
                    "best_times": ["07:00", "12:00", "18:00"]
                },
                "is_active": True
            }
            mock_agent_class.return_value = mock_agent
            yield mock_agent

    def test_get_channel_success(self, client, mock_channel_agent):
        """Test successful retrieval of specific channel"""
        response = client.get("/api/tiktok-channels/air")

        assert response.status_code == 200
        data = response.json()

        assert "request_id" in data
        assert "channel" in data
        assert data["status"] == "success"
        assert data["channel"]["element"] == "air"
        assert data["channel"]["channel_name"] == "QuickTCG Air"

    def test_get_channel_not_found(self, client):
        """Test 404 error when channel not found"""
        with patch('api.routes.tiktok_channels.TikTokChannelAgent') as mock_agent_class:
            mock_agent = Mock()
            mock_agent.get_channel.side_effect = ValueError("Channel 'invalid' not found")
            mock_agent_class.return_value = mock_agent

            response = client.get("/api/tiktok-channels/invalid")

            assert response.status_code == 404
            data = response.json()
            assert "detail" in data
            assert "Channel not found" in str(data["detail"])

    def test_get_channel_agent_error(self, client):
        """Test error handling when agent raises exception"""
        with patch('api.routes.tiktok_channels.TikTokChannelAgent') as mock_agent_class:
            mock_agent = Mock()
            mock_agent.get_channel.side_effect = Exception("Database error")
            mock_agent_class.return_value = mock_agent

            response = client.get("/api/tiktok-channels/air")

            assert response.status_code == 500
            data = response.json()
            assert "detail" in data
            assert "Failed to get channel" in str(data["detail"])


class TestCreateChannel:
    """Test suite for POST /api/tiktok-channels endpoint"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    @pytest.fixture
    def mock_channel_agent(self):
        """Mock TikTokChannelAgent for testing"""
        with patch('api.routes.tiktok_channels.TikTokChannelAgent') as mock_agent_class:
            mock_agent = Mock(spec=TikTokChannelAgent)
            mock_agent.create_channel.return_value = {
                "element": "air",
                "channel_name": "QuickTCG Air",
                "description": "Fast-paced tips",
                "target_audience": "Competitive players",
                "is_active": True
            }
            mock_agent_class.return_value = mock_agent
            yield mock_agent

    def test_create_channel_success(self, client, mock_channel_agent):
        """Test successful channel creation"""
        request_data = {
            "channel_name": "QuickTCG Air",
            "element_theme": "air",
            "description": "Fast-paced tournament tips",
            "target_audience": "Competitive TCG players"
        }

        response = client.post("/api/tiktok-channels", json=request_data)

        assert response.status_code == 200
        data = response.json()

        assert "request_id" in data
        assert "message" in data
        assert "channel" in data
        assert data["status"] == "success"
        assert "created successfully" in data["message"]

    def test_create_channel_minimal_request(self, client, mock_channel_agent):
        """Test channel creation with minimal fields"""
        request_data = {
            "channel_name": "QuickTCG Air",
            "element_theme": "air"
        }

        response = client.post("/api/tiktok-channels", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"

        # Verify agent was called with None for optional fields
        mock_channel_agent.create_channel.assert_called_once()

    def test_create_channel_full_request(self, client, mock_channel_agent):
        """Test channel creation with all fields"""
        request_data = {
            "channel_name": "QuickTCG Air",
            "element_theme": "air",
            "description": "Fast-paced tips",
            "target_audience": "Competitive players",
            "posting_schedule": {
                "frequency": "daily",
                "days": ["Mon", "Tue", "Wed", "Thu", "Fri"],
                "best_times": ["07:00", "12:00", "18:00"]
            },
            "branding_guidelines": {
                "hashtags": ["#QuickTCG", "#AirStrategy"],
                "visual_style": "Fast cuts"
            }
        }

        response = client.post("/api/tiktok-channels", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"

    def test_create_channel_invalid_element(self, client):
        """Test validation error for invalid element theme"""
        request_data = {
            "channel_name": "Invalid Channel",
            "element_theme": "invalid"  # Not air/water/fire/earth
        }

        response = client.post("/api/tiktok-channels", json=request_data)

        assert response.status_code == 422  # Validation error

    def test_create_channel_name_too_short(self, client):
        """Test validation error for channel name too short"""
        request_data = {
            "channel_name": "Ab",  # Less than 3 characters
            "element_theme": "air"
        }

        response = client.post("/api/tiktok-channels", json=request_data)

        assert response.status_code == 422  # Validation error

    def test_create_channel_agent_value_error(self, client):
        """Test 400 error when agent raises ValueError"""
        with patch('api.routes.tiktok_channels.TikTokChannelAgent') as mock_agent_class:
            mock_agent = Mock()
            mock_agent.create_channel.side_effect = ValueError("Duplicate channel")
            mock_agent_class.return_value = mock_agent

            request_data = {
                "channel_name": "Duplicate",
                "element_theme": "air"
            }

            response = client.post("/api/tiktok-channels", json=request_data)

            assert response.status_code == 400
            data = response.json()
            assert "detail" in data
            assert "Invalid channel data" in str(data["detail"])

    def test_create_channel_agent_error(self, client):
        """Test error handling when agent raises exception"""
        with patch('api.routes.tiktok_channels.TikTokChannelAgent') as mock_agent_class:
            mock_agent = Mock()
            mock_agent.create_channel.side_effect = Exception("Database error")
            mock_agent_class.return_value = mock_agent

            request_data = {
                "channel_name": "Test Channel",
                "element_theme": "air"
            }

            response = client.post("/api/tiktok-channels", json=request_data)

            assert response.status_code == 500
            data = response.json()
            assert "detail" in data
            assert "Failed to create channel" in str(data["detail"])


class TestUpdateChannel:
    """Test suite for PUT /api/tiktok-channels/{channel_element} endpoint"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    @pytest.fixture
    def mock_channel_agent(self):
        """Mock TikTokChannelAgent for testing"""
        with patch('api.routes.tiktok_channels.TikTokChannelAgent') as mock_agent_class:
            mock_agent = Mock(spec=TikTokChannelAgent)
            mock_agent.update_channel.return_value = {
                "element": "air",
                "channel_name": "Updated QuickTCG Air",
                "description": "Updated description",
                "is_active": True
            }
            mock_agent_class.return_value = mock_agent
            yield mock_agent

    def test_update_channel_success(self, client, mock_channel_agent):
        """Test successful channel update"""
        request_data = {
            "channel_name": "Updated QuickTCG Air",
            "description": "Updated description"
        }

        response = client.put("/api/tiktok-channels/air", json=request_data)

        assert response.status_code == 200
        data = response.json()

        assert "request_id" in data
        assert "message" in data
        assert "channel" in data
        assert data["status"] == "success"
        assert "updated successfully" in data["message"]

    def test_update_channel_partial_update(self, client, mock_channel_agent):
        """Test partial channel update (only some fields)"""
        request_data = {
            "description": "New description only"
        }

        response = client.put("/api/tiktok-channels/air", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"

        # Verify only description was passed to agent
        call_kwargs = mock_channel_agent.update_channel.call_args.kwargs
        assert "description" in call_kwargs
        assert call_kwargs["description"] == "New description only"

    def test_update_channel_posting_schedule(self, client, mock_channel_agent):
        """Test updating posting schedule"""
        request_data = {
            "posting_schedule": {
                "frequency": "twice_daily",
                "days": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
                "best_times": ["08:00", "19:00"]
            }
        }

        response = client.put("/api/tiktok-channels/air", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"

    def test_update_channel_deactivate(self, client, mock_channel_agent):
        """Test deactivating channel via update"""
        request_data = {
            "is_active": False
        }

        response = client.put("/api/tiktok-channels/air", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"

    def test_update_channel_not_found(self, client):
        """Test 404 error when channel not found"""
        with patch('api.routes.tiktok_channels.TikTokChannelAgent') as mock_agent_class:
            mock_agent = Mock()
            mock_agent.update_channel.side_effect = ValueError("Channel 'invalid' not found")
            mock_agent_class.return_value = mock_agent

            request_data = {
                "description": "New description"
            }

            response = client.put("/api/tiktok-channels/invalid", json=request_data)

            assert response.status_code == 404
            data = response.json()
            assert "detail" in data
            assert "Channel not found" in str(data["detail"])

    def test_update_channel_agent_error(self, client):
        """Test error handling when agent raises exception"""
        with patch('api.routes.tiktok_channels.TikTokChannelAgent') as mock_agent_class:
            mock_agent = Mock()
            mock_agent.update_channel.side_effect = Exception("Database error")
            mock_agent_class.return_value = mock_agent

            request_data = {
                "description": "New description"
            }

            response = client.put("/api/tiktok-channels/air", json=request_data)

            assert response.status_code == 500
            data = response.json()
            assert "detail" in data
            assert "Failed to update channel" in str(data["detail"])


class TestDeactivateChannel:
    """Test suite for DELETE /api/tiktok-channels/{channel_element} endpoint"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    @pytest.fixture
    def mock_channel_agent(self):
        """Mock TikTokChannelAgent for testing"""
        with patch('api.routes.tiktok_channels.TikTokChannelAgent') as mock_agent_class:
            mock_agent = Mock(spec=TikTokChannelAgent)
            mock_agent.update_channel.return_value = {
                "element": "air",
                "channel_name": "QuickTCG Air",
                "is_active": False
            }
            mock_agent_class.return_value = mock_agent
            yield mock_agent

    def test_deactivate_channel_success(self, client, mock_channel_agent):
        """Test successful channel deactivation"""
        response = client.delete("/api/tiktok-channels/air")

        assert response.status_code == 200
        data = response.json()

        assert "request_id" in data
        assert "message" in data
        assert "channel" in data
        assert data["status"] == "success"
        assert "deactivated successfully" in data["message"]

        # Verify agent was called with is_active=False
        mock_channel_agent.update_channel.assert_called_once()
        call_args = mock_channel_agent.update_channel.call_args
        assert call_args[0][0] == "air"  # channel_element
        assert call_args[1]["is_active"] is False

    def test_deactivate_channel_not_found(self, client):
        """Test 404 error when channel not found"""
        with patch('api.routes.tiktok_channels.TikTokChannelAgent') as mock_agent_class:
            mock_agent = Mock()
            mock_agent.update_channel.side_effect = ValueError("Channel 'invalid' not found")
            mock_agent_class.return_value = mock_agent

            response = client.delete("/api/tiktok-channels/invalid")

            assert response.status_code == 404
            data = response.json()
            assert "detail" in data
            assert "Channel not found" in str(data["detail"])

    def test_deactivate_channel_agent_error(self, client):
        """Test error handling when agent raises exception"""
        with patch('api.routes.tiktok_channels.TikTokChannelAgent') as mock_agent_class:
            mock_agent = Mock()
            mock_agent.update_channel.side_effect = Exception("Database error")
            mock_agent_class.return_value = mock_agent

            response = client.delete("/api/tiktok-channels/air")

            assert response.status_code == 500
            data = response.json()
            assert "detail" in data
            assert "Failed to deactivate channel" in str(data["detail"])


class TestChannelMetrics:
    """Test suite for GET /api/tiktok-channels/{channel_element}/metrics endpoint"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    @pytest.fixture
    def mock_channel_agent(self):
        """Mock TikTokChannelAgent for testing"""
        with patch('api.routes.tiktok_channels.TikTokChannelAgent') as mock_agent_class:
            mock_agent = Mock(spec=TikTokChannelAgent)
            mock_agent.get_channel_performance.return_value = {
                "channel_element": "air",
                "total_posts": 50,
                "total_saves": 1200,
                "total_views": 50000,
                "save_rate": 2.4,
                "avg_saves_per_post": 24.0,
                "avg_views_per_post": 1000.0,
                "avg_engagement_rate": 5.5,
                "top_performing_content": [
                    {"topic": "Quick deck tips", "saves": 150, "views": 3000},
                    {"topic": "Tournament prep", "saves": 120, "views": 2500}
                ]
            }
            mock_agent_class.return_value = mock_agent
            yield mock_agent

    def test_get_channel_metrics_success(self, client, mock_channel_agent):
        """Test successful metrics retrieval"""
        response = client.get("/api/tiktok-channels/air/metrics")

        assert response.status_code == 200
        data = response.json()

        assert "request_id" in data
        assert "metrics" in data
        assert data["status"] == "success"

        # Verify metrics structure
        metrics = data["metrics"]
        assert "channel_element" in metrics
        assert "total_posts" in metrics
        assert "total_saves" in metrics
        assert "total_views" in metrics
        assert "save_rate" in metrics
        assert metrics["save_rate"] == 2.4

    def test_get_channel_metrics_with_days_back(self, client, mock_channel_agent):
        """Test metrics retrieval with custom days_back parameter"""
        response = client.get("/api/tiktok-channels/air/metrics?days_back=7")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"

        # Verify agent was called with days_back parameter
        mock_channel_agent.get_channel_performance.assert_called_once()
        call_kwargs = mock_channel_agent.get_channel_performance.call_args.kwargs
        assert call_kwargs["days_back"] == 7

    def test_get_channel_metrics_default_days_back(self, client, mock_channel_agent):
        """Test metrics retrieval with default days_back (30)"""
        response = client.get("/api/tiktok-channels/air/metrics")

        assert response.status_code == 200

        # Verify default days_back was used
        call_kwargs = mock_channel_agent.get_channel_performance.call_args.kwargs
        assert call_kwargs["days_back"] == 30

    def test_get_channel_metrics_top_content(self, client, mock_channel_agent):
        """Test that top performing content is included in metrics"""
        response = client.get("/api/tiktok-channels/air/metrics")
        data = response.json()

        metrics = data["metrics"]
        assert "top_performing_content" in metrics
        assert len(metrics["top_performing_content"]) == 2
        assert metrics["top_performing_content"][0]["topic"] == "Quick deck tips"

    def test_get_channel_metrics_not_found(self, client):
        """Test 404 error when channel not found"""
        with patch('api.routes.tiktok_channels.TikTokChannelAgent') as mock_agent_class:
            mock_agent = Mock()
            mock_agent.get_channel_performance.side_effect = ValueError("Channel 'invalid' not found")
            mock_agent_class.return_value = mock_agent

            response = client.get("/api/tiktok-channels/invalid/metrics")

            assert response.status_code == 404
            data = response.json()
            assert "detail" in data
            assert "Channel not found" in str(data["detail"])

    def test_get_channel_metrics_agent_error(self, client):
        """Test error handling when agent raises exception"""
        with patch('api.routes.tiktok_channels.TikTokChannelAgent') as mock_agent_class:
            mock_agent = Mock()
            mock_agent.get_channel_performance.side_effect = Exception("Database error")
            mock_agent_class.return_value = mock_agent

            response = client.get("/api/tiktok-channels/air/metrics")

            assert response.status_code == 500
            data = response.json()
            assert "detail" in data
            assert "Failed to get channel metrics" in str(data["detail"])


class TestContentGeneration:
    """Test suite for POST /api/tiktok-channels/content/generate endpoint"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    @pytest.fixture
    def mock_channel_agent_video_script(self):
        """Mock TikTokChannelAgent for video script generation"""
        with patch('api.routes.tiktok_channels.TikTokChannelAgent') as mock_agent_class:
            mock_agent = Mock(spec=TikTokChannelAgent)
            mock_agent.generate_channel_video_script.return_value = (
                "Test video script content for air channel",
                Path("/tmp/air_video_script.txt")
            )
            mock_agent_class.return_value = mock_agent
            yield mock_agent

    @pytest.fixture
    def mock_channel_agent_calendar(self):
        """Mock TikTokChannelAgent for calendar generation"""
        with patch('api.routes.tiktok_channels.TikTokChannelAgent') as mock_agent_class:
            mock_agent = Mock(spec=TikTokChannelAgent)
            mock_agent.generate_channel_content_calendar.return_value = (
                "Test content calendar for air channel",
                Path("/tmp/air_calendar.txt")
            )
            mock_agent_class.return_value = mock_agent
            yield mock_agent

    @pytest.fixture
    def mock_channel_agent_multi_strategy(self):
        """Mock TikTokChannelAgent for multi-channel strategy"""
        with patch('api.routes.tiktok_channels.TikTokChannelAgent') as mock_agent_class:
            mock_agent = Mock(spec=TikTokChannelAgent)
            mock_agent.generate_multi_channel_strategy.return_value = (
                "Test multi-channel strategy",
                Path("/tmp/multi_channel_strategy.txt")
            )
            mock_agent_class.return_value = mock_agent
            yield mock_agent

    def test_generate_video_script_success(self, client, mock_channel_agent_video_script):
        """Test successful video script generation"""
        request_data = {
            "channel_element": "air",
            "topic": "Quick deck building tips for tournaments",
            "content_type": "video_script"
        }

        response = client.post("/api/tiktok-channels/content/generate", json=request_data)

        assert response.status_code == 200
        data = response.json()

        assert "request_id" in data
        assert "content" in data
        assert "file_path" in data
        assert "metadata" in data
        assert data["status"] == "success"

        # Verify metadata
        metadata = data["metadata"]
        assert metadata["content_type"] == "video_script"
        assert metadata["channel_element"] == "air"
        assert metadata["topic"] == "Quick deck building tips for tournaments"

    def test_generate_video_script_with_product(self, client, mock_channel_agent_video_script):
        """Test video script generation with product mention"""
        request_data = {
            "channel_element": "air",
            "topic": "Tournament preparation essentials",
            "content_type": "video_script",
            "product": "Tournament Deck Box",
            "include_product_link": True
        }

        response = client.post("/api/tiktok-channels/content/generate", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"

        # Verify product metadata
        metadata = data["metadata"]
        assert metadata["product"] == "Tournament Deck Box"
        assert metadata["include_product_link"] is True

        # Verify agent was called with product parameters
        mock_channel_agent_video_script.generate_channel_video_script.assert_called_once()
        call_kwargs = mock_channel_agent_video_script.generate_channel_video_script.call_args.kwargs
        assert call_kwargs["product"] == "Tournament Deck Box"
        assert call_kwargs["include_product_link"] is True

    def test_generate_content_calendar_success(self, client, mock_channel_agent_calendar):
        """Test successful content calendar generation"""
        request_data = {
            "channel_element": "water",
            "topic": "Weekly content strategy",
            "content_type": "content_calendar",
            "num_days": 7
        }

        response = client.post("/api/tiktok-channels/content/generate", json=request_data)

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "success"
        assert "content" in data
        assert "file_path" in data

        # Verify metadata
        metadata = data["metadata"]
        assert metadata["content_type"] == "content_calendar"
        assert metadata["channel_element"] == "water"
        assert metadata["num_days"] == 7

    def test_generate_content_calendar_custom_days(self, client, mock_channel_agent_calendar):
        """Test content calendar generation with custom num_days"""
        request_data = {
            "channel_element": "fire",
            "topic": "Monthly content plan",
            "content_type": "content_calendar",
            "num_days": 30
        }

        response = client.post("/api/tiktok-channels/content/generate", json=request_data)

        assert response.status_code == 200

        # Verify agent was called with num_days
        mock_channel_agent_calendar.generate_channel_content_calendar.assert_called_once()
        call_kwargs = mock_channel_agent_calendar.generate_channel_content_calendar.call_args.kwargs
        assert call_kwargs["num_days"] == 30

    def test_generate_multi_channel_strategy_success(self, client, mock_channel_agent_multi_strategy):
        """Test successful multi-channel strategy generation"""
        request_data = {
            "channel_element": "air",  # Required but not used for multi-channel
            "topic": "Weekly cross-channel strategy",
            "content_type": "multi_channel_strategy"
        }

        response = client.post("/api/tiktok-channels/content/generate", json=request_data)

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "success"

        # Verify metadata
        metadata = data["metadata"]
        assert metadata["content_type"] == "multi_channel_strategy"
        assert metadata["time_period"] == "weekly"

    def test_generate_content_invalid_channel_element(self, client):
        """Test validation error for invalid channel element"""
        request_data = {
            "channel_element": "invalid",  # Not air/water/fire/earth
            "topic": "Test topic",
            "content_type": "video_script"
        }

        response = client.post("/api/tiktok-channels/content/generate", json=request_data)

        assert response.status_code == 422  # Validation error

    def test_generate_content_invalid_content_type(self, client):
        """Test validation error for invalid content type"""
        request_data = {
            "channel_element": "air",
            "topic": "Test topic",
            "content_type": "invalid_type"
        }

        response = client.post("/api/tiktok-channels/content/generate", json=request_data)

        assert response.status_code == 422  # Validation error

    def test_generate_content_topic_too_short(self, client):
        """Test validation error for topic too short"""
        request_data = {
            "channel_element": "air",
            "topic": "Short",  # Less than 10 characters
            "content_type": "video_script"
        }

        response = client.post("/api/tiktok-channels/content/generate", json=request_data)

        assert response.status_code == 422  # Validation error

    def test_generate_content_num_days_too_large(self, client):
        """Test validation error for num_days exceeding limit"""
        request_data = {
            "channel_element": "air",
            "topic": "Test topic for calendar",
            "content_type": "content_calendar",
            "num_days": 31  # Exceeds max of 30
        }

        response = client.post("/api/tiktok-channels/content/generate", json=request_data)

        assert response.status_code == 422  # Validation error

    def test_generate_content_agent_value_error(self, client):
        """Test 400 error when agent raises ValueError"""
        with patch('api.routes.tiktok_channels.TikTokChannelAgent') as mock_agent_class:
            mock_agent = Mock()
            mock_agent.generate_channel_video_script.side_effect = ValueError("Invalid channel")
            mock_agent_class.return_value = mock_agent

            request_data = {
                "channel_element": "air",
                "topic": "Test topic",
                "content_type": "video_script"
            }

            response = client.post("/api/tiktok-channels/content/generate", json=request_data)

            assert response.status_code == 400
            data = response.json()
            assert "detail" in data
            assert "Invalid request" in str(data["detail"])

    def test_generate_content_agent_error(self, client):
        """Test error handling when agent raises exception"""
        with patch('api.routes.tiktok_channels.TikTokChannelAgent') as mock_agent_class:
            mock_agent = Mock()
            mock_agent.generate_channel_video_script.side_effect = Exception("API error")
            mock_agent_class.return_value = mock_agent

            request_data = {
                "channel_element": "air",
                "topic": "Test topic",
                "content_type": "video_script"
            }

            response = client.post("/api/tiktok-channels/content/generate", json=request_data)

            assert response.status_code == 500
            data = response.json()
            assert "detail" in data
            assert "Failed to generate content" in str(data["detail"])

    def test_generate_content_default_include_topics(self, client, mock_channel_agent_calendar):
        """Test that include_topics defaults to True for calendars"""
        request_data = {
            "channel_element": "air",
            "topic": "Test calendar",
            "content_type": "content_calendar"
        }

        response = client.post("/api/tiktok-channels/content/generate", json=request_data)

        assert response.status_code == 200

        # Verify default value was used
        call_kwargs = mock_channel_agent_calendar.generate_channel_content_calendar.call_args.kwargs
        assert call_kwargs["include_topics"] is True

    def test_generate_content_default_include_product_link(self, client, mock_channel_agent_video_script):
        """Test that include_product_link defaults to False for video scripts"""
        request_data = {
            "channel_element": "air",
            "topic": "Test video script",
            "content_type": "video_script"
        }

        response = client.post("/api/tiktok-channels/content/generate", json=request_data)

        assert response.status_code == 200

        # Verify default value was used
        call_kwargs = mock_channel_agent_video_script.generate_channel_video_script.call_args.kwargs
        assert call_kwargs["include_product_link"] is False
