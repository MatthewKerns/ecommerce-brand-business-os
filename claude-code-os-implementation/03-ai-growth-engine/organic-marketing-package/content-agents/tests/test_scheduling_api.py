"""
Integration tests for TikTok scheduling API endpoints.

Tests cover:
- Single content scheduling endpoint
- Bulk content scheduling endpoint
- List scheduled content endpoint
- Get scheduled content details endpoint
- Update scheduled content endpoint
- Delete scheduled content endpoint
- Retry failed content endpoint
- Request validation
- Error handling
- Response structure
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock, MagicMock
from datetime import datetime, timedelta
import json

from api.main import app
from database.models import ScheduledContent


class TestScheduleContent:
    """Test suite for /api/tiktok/schedule POST endpoint"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    @pytest.fixture
    def mock_db_session(self):
        """Mock database session"""
        with patch('api.routes.tiktok_scheduling.get_session') as mock_get_session:
            mock_session = Mock()
            mock_get_session.return_value = iter([mock_session])
            yield mock_session

    @pytest.fixture
    def future_time(self):
        """Return a future datetime for scheduling"""
        return datetime.utcnow() + timedelta(hours=2)

    def test_schedule_content_success(self, client, mock_db_session, future_time):
        """Test successful content scheduling"""
        # Create mock scheduled content
        mock_scheduled = ScheduledContent(
            id=1,
            content_type="video",
            content_data=json.dumps({
                "video_url": "https://example.com/video.mp4",
                "caption": "Test video caption"
            }),
            scheduled_time=future_time,
            status="pending",
            retry_count=0,
            max_retries=3,
            created_at=datetime.utcnow()
        )

        mock_db_session.add.return_value = None
        mock_db_session.commit.return_value = None
        mock_db_session.refresh.side_effect = lambda obj: setattr(obj, 'id', 1)

        # Mock the query chain
        mock_db_session.add.return_value = None
        mock_db_session.commit.return_value = None
        mock_db_session.refresh.return_value = None

        request_data = {
            "content_type": "video",
            "content_data": {
                "video_url": "https://example.com/video.mp4",
                "caption": "Test video caption",
                "tags": ["test", "video"]
            },
            "scheduled_time": future_time.isoformat(),
            "max_retries": 3
        }

        # Patch the ScheduledContent constructor to return our mock
        with patch('api.routes.tiktok_scheduling.ScheduledContent') as mock_model:
            mock_model.return_value = mock_scheduled
            response = client.post("/api/tiktok/schedule", json=request_data)

        assert response.status_code == 201
        data = response.json()

        assert "id" in data
        assert data["content_type"] == "video"
        assert data["status"] == "pending"
        assert data["max_retries"] == 3
        assert "scheduled_time" in data
        assert "created_at" in data

    def test_schedule_content_minimal_request(self, client, mock_db_session, future_time):
        """Test content scheduling with minimal required fields"""
        mock_scheduled = ScheduledContent(
            id=2,
            content_type="post",
            content_data=json.dumps({"content": "Test post"}),
            scheduled_time=future_time,
            status="pending",
            retry_count=0,
            max_retries=3,
            created_at=datetime.utcnow()
        )

        request_data = {
            "content_type": "post",
            "content_data": {"content": "Test post"},
            "scheduled_time": future_time.isoformat()
        }

        with patch('api.routes.tiktok_scheduling.ScheduledContent') as mock_model:
            mock_model.return_value = mock_scheduled
            response = client.post("/api/tiktok/schedule", json=request_data)

        assert response.status_code == 201
        data = response.json()

        assert data["content_type"] == "post"
        assert data["max_retries"] == 3  # Default value

    def test_schedule_content_with_custom_request_id(self, client, mock_db_session, future_time):
        """Test content scheduling with custom request ID in header"""
        mock_scheduled = ScheduledContent(
            id=3,
            content_type="video",
            content_data=json.dumps({"video_url": "https://example.com/video.mp4"}),
            scheduled_time=future_time,
            status="pending",
            retry_count=0,
            max_retries=3,
            created_at=datetime.utcnow()
        )

        request_data = {
            "content_type": "video",
            "content_data": {"video_url": "https://example.com/video.mp4"},
            "scheduled_time": future_time.isoformat()
        }

        with patch('api.routes.tiktok_scheduling.ScheduledContent') as mock_model:
            mock_model.return_value = mock_scheduled
            response = client.post(
                "/api/tiktok/schedule",
                json=request_data,
                headers={"X-Request-ID": "custom-schedule-123"}
            )

        assert response.status_code == 201

    def test_schedule_content_past_time_error(self, client, mock_db_session):
        """Test validation error for scheduled time in the past"""
        past_time = datetime.utcnow() - timedelta(hours=1)

        request_data = {
            "content_type": "video",
            "content_data": {"video_url": "https://example.com/video.mp4"},
            "scheduled_time": past_time.isoformat()
        }

        response = client.post("/api/tiktok/schedule", json=request_data)

        assert response.status_code == 400
        assert "future" in response.json()["detail"].lower()

    def test_schedule_content_invalid_content_type(self, client, future_time):
        """Test validation error for invalid content type"""
        request_data = {
            "content_type": "invalid_type",
            "content_data": {"content": "Test"},
            "scheduled_time": future_time.isoformat()
        }

        response = client.post("/api/tiktok/schedule", json=request_data)

        assert response.status_code == 422  # Validation error

    def test_schedule_content_missing_required_field(self, client, future_time):
        """Test validation error when required field is missing"""
        request_data = {
            "content_data": {"content": "Test"},
            "scheduled_time": future_time.isoformat()
            # Missing required 'content_type' field
        }

        response = client.post("/api/tiktok/schedule", json=request_data)

        assert response.status_code == 422  # Validation error

    def test_schedule_content_database_error(self, client, future_time):
        """Test error handling when database raises exception"""
        with patch('api.routes.tiktok_scheduling.get_session') as mock_get_session:
            mock_session = Mock()
            mock_session.add.side_effect = Exception("Database connection error")
            mock_get_session.return_value = iter([mock_session])

            request_data = {
                "content_type": "video",
                "content_data": {"video_url": "https://example.com/video.mp4"},
                "scheduled_time": future_time.isoformat()
            }

            response = client.post("/api/tiktok/schedule", json=request_data)

            assert response.status_code == 500
            assert "detail" in response.json()


class TestBulkScheduleContent:
    """Test suite for /api/tiktok/schedule/bulk POST endpoint"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    @pytest.fixture
    def mock_db_session(self):
        """Mock database session"""
        with patch('api.routes.tiktok_scheduling.get_session') as mock_get_session:
            mock_session = Mock()
            mock_get_session.return_value = iter([mock_session])
            yield mock_session

    @pytest.fixture
    def future_time(self):
        """Return a future datetime for scheduling"""
        return datetime.utcnow() + timedelta(hours=2)

    def test_bulk_schedule_success(self, client, mock_db_session, future_time):
        """Test successful bulk content scheduling"""
        # Create mock scheduled content items
        mock_scheduled_1 = ScheduledContent(
            id=1,
            content_type="video",
            content_data=json.dumps({"video_url": "https://example.com/video1.mp4"}),
            scheduled_time=future_time,
            status="pending",
            retry_count=0,
            max_retries=3,
            created_at=datetime.utcnow()
        )

        mock_scheduled_2 = ScheduledContent(
            id=2,
            content_type="post",
            content_data=json.dumps({"content": "Test post"}),
            scheduled_time=future_time + timedelta(hours=1),
            status="pending",
            retry_count=0,
            max_retries=3,
            created_at=datetime.utcnow()
        )

        mock_db_session.flush.return_value = None
        mock_db_session.commit.return_value = None

        request_data = {
            "items": [
                {
                    "content_type": "video",
                    "content_data": {"video_url": "https://example.com/video1.mp4"},
                    "scheduled_time": future_time.isoformat()
                },
                {
                    "content_type": "post",
                    "content_data": {"content": "Test post"},
                    "scheduled_time": (future_time + timedelta(hours=1)).isoformat()
                }
            ]
        }

        with patch('api.routes.tiktok_scheduling.ScheduledContent') as mock_model:
            mock_model.side_effect = [mock_scheduled_1, mock_scheduled_2]
            response = client.post("/api/tiktok/schedule/bulk", json=request_data)

        assert response.status_code == 201
        data = response.json()

        assert "scheduled" in data
        assert "failed" in data
        assert data["total_requested"] == 2
        assert data["total_scheduled"] == 2
        assert data["total_failed"] == 0

    def test_bulk_schedule_partial_success(self, client, mock_db_session, future_time):
        """Test bulk scheduling with some items failing validation"""
        past_time = datetime.utcnow() - timedelta(hours=1)

        mock_scheduled = ScheduledContent(
            id=1,
            content_type="video",
            content_data=json.dumps({"video_url": "https://example.com/video1.mp4"}),
            scheduled_time=future_time,
            status="pending",
            retry_count=0,
            max_retries=3,
            created_at=datetime.utcnow()
        )

        mock_db_session.flush.return_value = None
        mock_db_session.commit.return_value = None

        request_data = {
            "items": [
                {
                    "content_type": "video",
                    "content_data": {"video_url": "https://example.com/video1.mp4"},
                    "scheduled_time": future_time.isoformat()
                },
                {
                    "content_type": "post",
                    "content_data": {"content": "Test post"},
                    "scheduled_time": past_time.isoformat()  # This will fail
                }
            ]
        }

        with patch('api.routes.tiktok_scheduling.ScheduledContent') as mock_model:
            mock_model.return_value = mock_scheduled
            response = client.post("/api/tiktok/schedule/bulk", json=request_data)

        assert response.status_code == 201
        data = response.json()

        assert data["total_requested"] == 2
        assert data["total_scheduled"] == 1
        assert data["total_failed"] == 1
        assert len(data["failed"]) == 1
        assert data["failed"][0]["index"] == 1

    def test_bulk_schedule_empty_list(self, client):
        """Test validation error for empty items list"""
        request_data = {
            "items": []
        }

        response = client.post("/api/tiktok/schedule/bulk", json=request_data)

        assert response.status_code == 422  # Validation error

    def test_bulk_schedule_exceeds_max_items(self, client, future_time):
        """Test validation error when exceeding max items limit"""
        # Create 101 items (max is 100)
        request_data = {
            "items": [
                {
                    "content_type": "video",
                    "content_data": {"video_url": f"https://example.com/video{i}.mp4"},
                    "scheduled_time": future_time.isoformat()
                }
                for i in range(101)
            ]
        }

        response = client.post("/api/tiktok/schedule/bulk", json=request_data)

        assert response.status_code == 422  # Validation error


class TestListScheduledContent:
    """Test suite for /api/tiktok/schedule GET endpoint"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    @pytest.fixture
    def mock_db_session(self):
        """Mock database session with query chain"""
        with patch('api.routes.tiktok_scheduling.get_session') as mock_get_session:
            mock_session = Mock()
            mock_query = Mock()

            # Setup query chain
            mock_session.query.return_value = mock_query
            mock_query.filter.return_value = mock_query
            mock_query.order_by.return_value = mock_query
            mock_query.limit.return_value = mock_query
            mock_query.offset.return_value = mock_query

            mock_get_session.return_value = iter([mock_session])
            yield mock_session, mock_query

    def test_list_scheduled_content_success(self, client, mock_db_session):
        """Test successful listing of scheduled content"""
        mock_session, mock_query = mock_db_session

        # Create mock scheduled content
        future_time = datetime.utcnow() + timedelta(hours=2)
        mock_items = [
            ScheduledContent(
                id=1,
                content_type="video",
                content_data=json.dumps({"video_url": "https://example.com/video1.mp4"}),
                scheduled_time=future_time,
                status="pending",
                retry_count=0,
                max_retries=3,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            ),
            ScheduledContent(
                id=2,
                content_type="post",
                content_data=json.dumps({"content": "Test post"}),
                scheduled_time=future_time + timedelta(hours=1),
                status="pending",
                retry_count=0,
                max_retries=3,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
        ]

        mock_query.all.return_value = mock_items

        response = client.get("/api/tiktok/schedule")

        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, list)
        assert len(data) == 2
        assert data[0]["id"] == 1
        assert data[0]["content_type"] == "video"
        assert data[1]["id"] == 2

    def test_list_scheduled_content_with_status_filter(self, client, mock_db_session):
        """Test listing scheduled content with status filter"""
        mock_session, mock_query = mock_db_session

        future_time = datetime.utcnow() + timedelta(hours=2)
        mock_items = [
            ScheduledContent(
                id=1,
                content_type="video",
                content_data=json.dumps({"video_url": "https://example.com/video1.mp4"}),
                scheduled_time=future_time,
                status="pending",
                retry_count=0,
                max_retries=3,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
        ]

        mock_query.all.return_value = mock_items

        response = client.get("/api/tiktok/schedule?status=pending")

        assert response.status_code == 200
        data = response.json()

        assert len(data) == 1
        assert data[0]["status"] == "pending"

    def test_list_scheduled_content_with_pagination(self, client, mock_db_session):
        """Test listing scheduled content with pagination"""
        mock_session, mock_query = mock_db_session

        mock_query.all.return_value = []

        response = client.get("/api/tiktok/schedule?limit=10&offset=5")

        assert response.status_code == 200

        # Verify limit and offset were called
        mock_query.limit.assert_called_once_with(10)
        mock_query.offset.assert_called_once_with(5)

    def test_list_scheduled_content_invalid_status(self, client):
        """Test validation error for invalid status filter"""
        response = client.get("/api/tiktok/schedule?status=invalid")

        assert response.status_code == 400
        assert "status must be one of" in response.json()["detail"]

    def test_list_scheduled_content_invalid_limit(self, client):
        """Test validation error for invalid limit"""
        response = client.get("/api/tiktok/schedule?limit=2000")

        assert response.status_code == 400
        assert "limit must be between" in response.json()["detail"]


class TestGetScheduledContent:
    """Test suite for /api/tiktok/schedule/{schedule_id} GET endpoint"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    @pytest.fixture
    def mock_db_session(self):
        """Mock database session with query chain"""
        with patch('api.routes.tiktok_scheduling.get_session') as mock_get_session:
            mock_session = Mock()
            mock_query = Mock()

            mock_session.query.return_value = mock_query
            mock_query.filter.return_value = mock_query

            mock_get_session.return_value = iter([mock_session])
            yield mock_session, mock_query

    def test_get_scheduled_content_success(self, client, mock_db_session):
        """Test successful retrieval of scheduled content details"""
        mock_session, mock_query = mock_db_session

        future_time = datetime.utcnow() + timedelta(hours=2)
        mock_item = ScheduledContent(
            id=1,
            content_type="video",
            content_data=json.dumps({"video_url": "https://example.com/video1.mp4", "caption": "Test"}),
            scheduled_time=future_time,
            status="pending",
            retry_count=0,
            max_retries=3,
            tiktok_video_id=None,
            error_message=None,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            published_at=None
        )

        mock_query.first.return_value = mock_item

        response = client.get("/api/tiktok/schedule/1")

        assert response.status_code == 200
        data = response.json()

        assert data["id"] == 1
        assert data["content_type"] == "video"
        assert data["status"] == "pending"
        assert "content_data" in data
        assert data["content_data"]["video_url"] == "https://example.com/video1.mp4"

    def test_get_scheduled_content_not_found(self, client, mock_db_session):
        """Test 404 error when scheduled content not found"""
        mock_session, mock_query = mock_db_session

        mock_query.first.return_value = None

        response = client.get("/api/tiktok/schedule/999")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestUpdateScheduledContent:
    """Test suite for /api/tiktok/schedule/{schedule_id} PUT endpoint"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    @pytest.fixture
    def mock_db_session(self):
        """Mock database session with query chain"""
        with patch('api.routes.tiktok_scheduling.get_session') as mock_get_session:
            mock_session = Mock()
            mock_query = Mock()

            mock_session.query.return_value = mock_query
            mock_query.filter.return_value = mock_query
            mock_session.commit.return_value = None
            mock_session.refresh.return_value = None

            mock_get_session.return_value = iter([mock_session])
            yield mock_session, mock_query

    @pytest.fixture
    def future_time(self):
        """Return a future datetime for scheduling"""
        return datetime.utcnow() + timedelta(hours=3)

    def test_update_scheduled_content_success(self, client, mock_db_session, future_time):
        """Test successful update of scheduled content"""
        mock_session, mock_query = mock_db_session

        mock_item = ScheduledContent(
            id=1,
            content_type="video",
            content_data=json.dumps({"video_url": "https://example.com/video1.mp4"}),
            scheduled_time=datetime.utcnow() + timedelta(hours=2),
            status="pending",
            retry_count=0,
            max_retries=3,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        mock_query.first.return_value = mock_item

        request_data = {
            "content_type": "video",
            "content_data": {"video_url": "https://example.com/updated_video.mp4"},
            "scheduled_time": future_time.isoformat(),
            "max_retries": 5
        }

        response = client.put("/api/tiktok/schedule/1", json=request_data)

        assert response.status_code == 200
        data = response.json()

        assert data["id"] == 1
        assert data["status"] == "pending"

    def test_update_scheduled_content_not_found(self, client, mock_db_session, future_time):
        """Test 404 error when scheduled content not found"""
        mock_session, mock_query = mock_db_session

        mock_query.first.return_value = None

        request_data = {
            "content_type": "video",
            "content_data": {"video_url": "https://example.com/video.mp4"},
            "scheduled_time": future_time.isoformat()
        }

        response = client.put("/api/tiktok/schedule/999", json=request_data)

        assert response.status_code == 404

    def test_update_scheduled_content_not_pending(self, client, mock_db_session, future_time):
        """Test error when trying to update non-pending content"""
        mock_session, mock_query = mock_db_session

        mock_item = ScheduledContent(
            id=1,
            content_type="video",
            content_data=json.dumps({"video_url": "https://example.com/video1.mp4"}),
            scheduled_time=datetime.utcnow() + timedelta(hours=2),
            status="published",  # Already published
            retry_count=0,
            max_retries=3,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        mock_query.first.return_value = mock_item

        request_data = {
            "content_type": "video",
            "content_data": {"video_url": "https://example.com/updated_video.mp4"},
            "scheduled_time": future_time.isoformat()
        }

        response = client.put("/api/tiktok/schedule/1", json=request_data)

        assert response.status_code == 400
        assert "Only pending content" in response.json()["detail"]


class TestDeleteScheduledContent:
    """Test suite for /api/tiktok/schedule/{schedule_id} DELETE endpoint"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    @pytest.fixture
    def mock_db_session(self):
        """Mock database session with query chain"""
        with patch('api.routes.tiktok_scheduling.get_session') as mock_get_session:
            mock_session = Mock()
            mock_query = Mock()

            mock_session.query.return_value = mock_query
            mock_query.filter.return_value = mock_query
            mock_session.delete.return_value = None
            mock_session.commit.return_value = None

            mock_get_session.return_value = iter([mock_session])
            yield mock_session, mock_query

    def test_delete_scheduled_content_success(self, client, mock_db_session):
        """Test successful deletion of scheduled content"""
        mock_session, mock_query = mock_db_session

        mock_item = ScheduledContent(
            id=1,
            content_type="video",
            content_data=json.dumps({"video_url": "https://example.com/video1.mp4"}),
            scheduled_time=datetime.utcnow() + timedelta(hours=2),
            status="pending",
            retry_count=0,
            max_retries=3,
            created_at=datetime.utcnow()
        )

        mock_query.first.return_value = mock_item

        response = client.delete("/api/tiktok/schedule/1")

        assert response.status_code == 204

    def test_delete_scheduled_content_not_found(self, client, mock_db_session):
        """Test 404 error when scheduled content not found"""
        mock_session, mock_query = mock_db_session

        mock_query.first.return_value = None

        response = client.delete("/api/tiktok/schedule/999")

        assert response.status_code == 404

    def test_delete_scheduled_content_not_pending(self, client, mock_db_session):
        """Test error when trying to delete non-pending content"""
        mock_session, mock_query = mock_db_session

        mock_item = ScheduledContent(
            id=1,
            content_type="video",
            content_data=json.dumps({"video_url": "https://example.com/video1.mp4"}),
            scheduled_time=datetime.utcnow() + timedelta(hours=2),
            status="published",  # Already published
            retry_count=0,
            max_retries=3,
            created_at=datetime.utcnow()
        )

        mock_query.first.return_value = mock_item

        response = client.delete("/api/tiktok/schedule/1")

        assert response.status_code == 400
        assert "Only pending content" in response.json()["detail"]


class TestRetryScheduledContent:
    """Test suite for /api/tiktok/schedule/{schedule_id}/retry POST endpoint"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    @pytest.fixture
    def mock_db_session(self):
        """Mock database session with query chain"""
        with patch('api.routes.tiktok_scheduling.get_session') as mock_get_session:
            mock_session = Mock()
            mock_query = Mock()

            mock_session.query.return_value = mock_query
            mock_query.filter.return_value = mock_query
            mock_session.commit.return_value = None
            mock_session.refresh.return_value = None

            mock_get_session.return_value = iter([mock_session])
            yield mock_session, mock_query

    def test_retry_scheduled_content_success(self, client, mock_db_session):
        """Test successful retry of failed content"""
        mock_session, mock_query = mock_db_session

        mock_item = ScheduledContent(
            id=1,
            content_type="video",
            content_data=json.dumps({"video_url": "https://example.com/video1.mp4"}),
            scheduled_time=datetime.utcnow() + timedelta(hours=2),
            status="failed",
            retry_count=3,
            max_retries=3,
            error_message="Network error",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        mock_query.first.return_value = mock_item

        response = client.post("/api/tiktok/schedule/1/retry")

        assert response.status_code == 200
        data = response.json()

        assert data["id"] == 1
        assert data["status"] == "pending"

        # Verify that status and retry_count were reset
        assert mock_item.status == "pending"
        assert mock_item.retry_count == 0
        assert mock_item.error_message is None

    def test_retry_scheduled_content_not_found(self, client, mock_db_session):
        """Test 404 error when scheduled content not found"""
        mock_session, mock_query = mock_db_session

        mock_query.first.return_value = None

        response = client.post("/api/tiktok/schedule/999/retry")

        assert response.status_code == 404

    def test_retry_scheduled_content_not_failed(self, client, mock_db_session):
        """Test error when trying to retry non-failed content"""
        mock_session, mock_query = mock_db_session

        mock_item = ScheduledContent(
            id=1,
            content_type="video",
            content_data=json.dumps({"video_url": "https://example.com/video1.mp4"}),
            scheduled_time=datetime.utcnow() + timedelta(hours=2),
            status="pending",  # Not failed
            retry_count=0,
            max_retries=3,
            created_at=datetime.utcnow()
        )

        mock_query.first.return_value = mock_item

        response = client.post("/api/tiktok/schedule/1/retry")

        assert response.status_code == 400
        assert "Only failed content" in response.json()["detail"]


class TestSchedulingAPIErrorHandling:
    """Test suite for general error handling and edge cases"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    def test_malformed_json_request(self, client):
        """Test error handling for malformed JSON"""
        response = client.post(
            "/api/tiktok/schedule",
            data="invalid json{",
            headers={"Content-Type": "application/json"}
        )

        assert response.status_code == 422  # Unprocessable Entity

    def test_invalid_datetime_format(self, client):
        """Test error handling for invalid datetime format"""
        request_data = {
            "content_type": "video",
            "content_data": {"video_url": "https://example.com/video.mp4"},
            "scheduled_time": "not-a-valid-datetime"
        }

        response = client.post("/api/tiktok/schedule", json=request_data)

        assert response.status_code == 422  # Validation error

    def test_empty_content_data(self, client):
        """Test scheduling with empty content_data"""
        future_time = datetime.utcnow() + timedelta(hours=2)

        request_data = {
            "content_type": "video",
            "content_data": {},  # Empty but valid
            "scheduled_time": future_time.isoformat()
        }

        with patch('api.routes.tiktok_scheduling.get_session') as mock_get_session:
            mock_session = Mock()
            mock_scheduled = ScheduledContent(
                id=1,
                content_type="video",
                content_data=json.dumps({}),
                scheduled_time=future_time,
                status="pending",
                retry_count=0,
                max_retries=3,
                created_at=datetime.utcnow()
            )

            mock_get_session.return_value = iter([mock_session])

            with patch('api.routes.tiktok_scheduling.ScheduledContent') as mock_model:
                mock_model.return_value = mock_scheduled
                response = client.post("/api/tiktok/schedule", json=request_data)

        assert response.status_code == 201
