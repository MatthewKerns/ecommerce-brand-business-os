"""
Unit tests for PublishingService class.

Tests cover:
- Service initialization (with/without custom client)
- Content publishing (success and error cases)
- Retry logic with exponential backoff
- Status updates and error handling
- Publish logging
- Video and post publishing
- All TikTok API error types
"""

import sys
from unittest.mock import Mock, MagicMock

# Mock anthropic module before any imports that might use it
sys.modules['anthropic'] = MagicMock()

import pytest
from unittest.mock import patch, call
from datetime import datetime, timedelta
import json
import time

from services.publishing_service import PublishingService
from database.models import ScheduledContent, PublishLog
from integrations.tiktok_shop.exceptions import (
    TikTokShopAPIError,
    TikTokShopAuthError,
    TikTokShopRateLimitError,
    TikTokShopValidationError,
    TikTokShopServerError,
    TikTokShopNetworkError
)
from exceptions import DatabaseError, ConfigurationError


class TestPublishingServiceInitialization:
    """Test suite for PublishingService initialization"""

    @patch('services.publishing_service.TikTokShopClient')
    @patch('services.publishing_service.TIKTOK_SHOP_APP_KEY', 'test_app_key')
    @patch('services.publishing_service.TIKTOK_SHOP_APP_SECRET', 'test_app_secret')
    @patch('services.publishing_service.TIKTOK_SHOP_ACCESS_TOKEN', 'test_access_token')
    def test_init_with_default_client(self, mock_client_class):
        """Test service initialization with default TikTok client"""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        service = PublishingService()

        assert service.tiktok_client is not None
        assert service.max_retries == PublishingService.DEFAULT_MAX_RETRIES
        mock_client_class.assert_called_once_with(
            app_key='test_app_key',
            app_secret='test_app_secret',
            access_token='test_access_token'
        )

    def test_init_with_custom_client(self):
        """Test service initialization with custom TikTok client"""
        mock_client = Mock()

        service = PublishingService(tiktok_client=mock_client)

        assert service.tiktok_client == mock_client
        assert service.max_retries == PublishingService.DEFAULT_MAX_RETRIES

    def test_init_with_custom_max_retries(self):
        """Test service initialization with custom max_retries"""
        mock_client = Mock()

        service = PublishingService(tiktok_client=mock_client, max_retries=5)

        assert service.max_retries == 5

    @patch('services.publishing_service.TIKTOK_SHOP_APP_KEY', None)
    @patch('services.publishing_service.TIKTOK_SHOP_APP_SECRET', 'test_secret')
    def test_init_without_app_key(self):
        """Test initialization fails without app key"""
        with pytest.raises(ConfigurationError) as exc_info:
            PublishingService()

        assert "Missing TikTok Shop credentials" in str(exc_info.value)

    @patch('services.publishing_service.TIKTOK_SHOP_APP_KEY', 'test_key')
    @patch('services.publishing_service.TIKTOK_SHOP_APP_SECRET', None)
    def test_init_without_app_secret(self):
        """Test initialization fails without app secret"""
        with pytest.raises(ConfigurationError) as exc_info:
            PublishingService()

        assert "Missing TikTok Shop credentials" in str(exc_info.value)


class TestPublishContent:
    """Test suite for publish_content method"""

    @pytest.fixture
    def mock_service(self):
        """Create mock publishing service"""
        mock_client = Mock()
        return PublishingService(tiktok_client=mock_client, max_retries=3)

    @pytest.fixture
    def mock_scheduled_content(self):
        """Create mock scheduled content"""
        return ScheduledContent(
            id=1,
            content_type="video",
            content_data=json.dumps({
                "video_url": "https://example.com/video.mp4",
                "title": "Test Video",
                "description": "Test description"
            }),
            scheduled_time=datetime.utcnow(),
            status="pending",
            retry_count=0,
            max_retries=3,
            created_at=datetime.utcnow()
        )

    @patch('services.publishing_service.get_db_session')
    def test_publish_content_success(self, mock_get_db, mock_service, mock_scheduled_content):
        """Test successful content publishing"""
        mock_db = Mock()
        mock_get_db.return_value = mock_db

        # Setup query chain
        mock_query = Mock()
        mock_filter = Mock()
        mock_filter.first.return_value = mock_scheduled_content
        mock_query.filter.return_value = mock_filter
        mock_db.query.return_value = mock_query

        # Mock successful publish
        with patch.object(mock_service, '_attempt_publish') as mock_attempt:
            mock_attempt.return_value = (True, {"video_id": "video_123", "status": "published"})

            result = mock_service.publish_content(1)

        assert result is True
        assert mock_scheduled_content.status == "published"
        assert mock_scheduled_content.tiktok_video_id == "video_123"
        assert mock_scheduled_content.retry_count == 1
        assert mock_scheduled_content.error_message is None
        mock_db.commit.assert_called()
        mock_db.close.assert_called()

    @patch('services.publishing_service.get_db_session')
    def test_publish_content_not_found(self, mock_get_db, mock_service):
        """Test publishing content that doesn't exist"""
        mock_db = Mock()
        mock_get_db.return_value = mock_db

        # Setup query to return None
        mock_query = Mock()
        mock_filter = Mock()
        mock_filter.first.return_value = None
        mock_query.filter.return_value = mock_filter
        mock_db.query.return_value = mock_query

        with pytest.raises(DatabaseError) as exc_info:
            mock_service.publish_content(999)

        assert "not found" in str(exc_info.value)
        mock_db.close.assert_called()

    @patch('services.publishing_service.get_db_session')
    def test_publish_content_wrong_status(self, mock_get_db, mock_service):
        """Test publishing content not in pending status"""
        mock_db = Mock()
        mock_get_db.return_value = mock_db

        scheduled_content = ScheduledContent(
            id=1,
            content_type="video",
            content_data=json.dumps({"video_url": "test.mp4"}),
            scheduled_time=datetime.utcnow(),
            status="published",  # Already published
            retry_count=0,
            max_retries=3,
            created_at=datetime.utcnow()
        )

        mock_query = Mock()
        mock_filter = Mock()
        mock_filter.first.return_value = scheduled_content
        mock_query.filter.return_value = mock_filter
        mock_db.query.return_value = mock_query

        result = mock_service.publish_content(1)

        assert result is False
        mock_db.close.assert_called()

    @patch('services.publishing_service.get_db_session')
    def test_publish_content_failed_retry(self, mock_get_db, mock_service, mock_scheduled_content):
        """Test publishing failure with retry available"""
        mock_db = Mock()
        mock_get_db.return_value = mock_db

        mock_query = Mock()
        mock_filter = Mock()
        mock_filter.first.return_value = mock_scheduled_content
        mock_query.filter.return_value = mock_filter
        mock_db.query.return_value = mock_query

        # Mock failed publish
        with patch.object(mock_service, '_attempt_publish') as mock_attempt:
            mock_attempt.return_value = (False, None)

            result = mock_service.publish_content(1)

        assert result is False
        assert mock_scheduled_content.status == "pending"  # Still pending for retry
        assert mock_scheduled_content.retry_count == 1
        mock_db.commit.assert_called()

    @patch('services.publishing_service.get_db_session')
    def test_publish_content_max_retries_exceeded(self, mock_get_db, mock_service):
        """Test publishing failure after max retries"""
        mock_db = Mock()
        mock_get_db.return_value = mock_db

        scheduled_content = ScheduledContent(
            id=1,
            content_type="video",
            content_data=json.dumps({"video_url": "test.mp4"}),
            scheduled_time=datetime.utcnow(),
            status="pending",
            retry_count=2,  # One more attempt will hit max_retries=3
            max_retries=3,
            created_at=datetime.utcnow()
        )

        mock_query = Mock()
        mock_filter = Mock()
        mock_filter.first.return_value = scheduled_content
        mock_query.filter.return_value = mock_filter
        mock_db.query.return_value = mock_query

        # Mock failed publish
        with patch.object(mock_service, '_attempt_publish') as mock_attempt:
            mock_attempt.return_value = (False, None)

            result = mock_service.publish_content(1)

        assert result is False
        assert scheduled_content.status == "failed"  # Marked as failed
        assert scheduled_content.retry_count == 3


class TestRetryFailedContent:
    """Test suite for retry_failed_content method"""

    @pytest.fixture
    def mock_service(self):
        """Create mock publishing service"""
        mock_client = Mock()
        return PublishingService(tiktok_client=mock_client, max_retries=3)

    @patch('services.publishing_service.get_db_session')
    def test_retry_failed_content_success(self, mock_get_db, mock_service):
        """Test successful retry of failed content"""
        mock_db = Mock()
        mock_get_db.return_value = mock_db

        scheduled_content = ScheduledContent(
            id=1,
            content_type="video",
            content_data=json.dumps({"video_url": "test.mp4"}),
            scheduled_time=datetime.utcnow(),
            status="failed",
            retry_count=1,
            max_retries=3,
            created_at=datetime.utcnow()
        )

        mock_query = Mock()
        mock_filter = Mock()
        mock_filter.first.return_value = scheduled_content
        mock_query.filter.return_value = mock_filter
        mock_db.query.return_value = mock_query

        # Mock successful publish_content
        with patch.object(mock_service, 'publish_content') as mock_publish:
            mock_publish.return_value = True

            result = mock_service.retry_failed_content(1)

        assert result is True
        assert scheduled_content.status == "pending"  # Reset to pending
        mock_db.commit.assert_called()

    @patch('services.publishing_service.get_db_session')
    def test_retry_content_not_found(self, mock_get_db, mock_service):
        """Test retrying content that doesn't exist"""
        mock_db = Mock()
        mock_get_db.return_value = mock_db

        mock_query = Mock()
        mock_filter = Mock()
        mock_filter.first.return_value = None
        mock_query.filter.return_value = mock_filter
        mock_db.query.return_value = mock_query

        with pytest.raises(DatabaseError) as exc_info:
            mock_service.retry_failed_content(999)

        assert "not found" in str(exc_info.value)

    @patch('services.publishing_service.get_db_session')
    def test_retry_wrong_status(self, mock_get_db, mock_service):
        """Test retrying content with wrong status"""
        mock_db = Mock()
        mock_get_db.return_value = mock_db

        scheduled_content = ScheduledContent(
            id=1,
            content_type="video",
            content_data=json.dumps({"video_url": "test.mp4"}),
            scheduled_time=datetime.utcnow(),
            status="published",  # Already published
            retry_count=0,
            max_retries=3,
            created_at=datetime.utcnow()
        )

        mock_query = Mock()
        mock_filter = Mock()
        mock_filter.first.return_value = scheduled_content
        mock_query.filter.return_value = mock_filter
        mock_db.query.return_value = mock_query

        result = mock_service.retry_failed_content(1)

        assert result is False

    @patch('services.publishing_service.get_db_session')
    def test_retry_max_retries_exceeded(self, mock_get_db, mock_service):
        """Test retrying content that exceeded max retries"""
        mock_db = Mock()
        mock_get_db.return_value = mock_db

        scheduled_content = ScheduledContent(
            id=1,
            content_type="video",
            content_data=json.dumps({"video_url": "test.mp4"}),
            scheduled_time=datetime.utcnow(),
            status="failed",
            retry_count=3,  # Already at max_retries
            max_retries=3,
            created_at=datetime.utcnow()
        )

        mock_query = Mock()
        mock_filter = Mock()
        mock_filter.first.return_value = scheduled_content
        mock_query.filter.return_value = mock_filter
        mock_db.query.return_value = mock_query

        result = mock_service.retry_failed_content(1)

        assert result is False


class TestAttemptPublish:
    """Test suite for _attempt_publish method"""

    @pytest.fixture
    def mock_service(self):
        """Create mock publishing service"""
        mock_client = Mock()
        return PublishingService(tiktok_client=mock_client, max_retries=3)

    @pytest.fixture
    def mock_db(self):
        """Create mock database session"""
        return Mock()

    @pytest.fixture
    def scheduled_video_content(self):
        """Create mock scheduled video content"""
        return ScheduledContent(
            id=1,
            content_type="video",
            content_data=json.dumps({
                "video_url": "https://example.com/video.mp4",
                "title": "Test Video"
            }),
            scheduled_time=datetime.utcnow(),
            status="pending",
            retry_count=0,
            max_retries=3,
            created_at=datetime.utcnow()
        )

    def test_attempt_publish_video_success(self, mock_service, mock_db, scheduled_video_content):
        """Test successful video publish attempt"""
        with patch.object(mock_service, '_publish_video') as mock_publish:
            mock_publish.return_value = {
                "video_id": "video_123",
                "status": "published"
            }

            success, result = mock_service._attempt_publish(scheduled_video_content, 1, mock_db)

        assert success is True
        assert result["video_id"] == "video_123"
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called()

    def test_attempt_publish_post_success(self, mock_service, mock_db):
        """Test successful post publish attempt"""
        scheduled_content = ScheduledContent(
            id=1,
            content_type="post",
            content_data=json.dumps({"content": "Test post"}),
            scheduled_time=datetime.utcnow(),
            status="pending",
            retry_count=0,
            max_retries=3,
            created_at=datetime.utcnow()
        )

        with patch.object(mock_service, '_publish_post') as mock_publish:
            mock_publish.return_value = {
                "post_id": "post_123",
                "status": "published"
            }

            success, result = mock_service._attempt_publish(scheduled_content, 1, mock_db)

        assert success is True
        assert result["post_id"] == "post_123"

    def test_attempt_publish_auth_error(self, mock_service, mock_db, scheduled_video_content):
        """Test publish attempt with authentication error"""
        with patch.object(mock_service, '_publish_video') as mock_publish:
            mock_publish.side_effect = TikTokShopAuthError("Invalid credentials")

            success, result = mock_service._attempt_publish(scheduled_video_content, 1, mock_db)

        assert success is False
        assert result is None
        assert scheduled_video_content.error_message == "Authentication error: [401] Invalid credentials"

    def test_attempt_publish_validation_error(self, mock_service, mock_db, scheduled_video_content):
        """Test publish attempt with validation error"""
        with patch.object(mock_service, '_publish_video') as mock_publish:
            mock_publish.side_effect = TikTokShopValidationError("Missing required field")

            success, result = mock_service._attempt_publish(scheduled_video_content, 1, mock_db)

        assert success is False
        assert result is None
        assert "Validation error" in scheduled_video_content.error_message

    @patch('services.publishing_service.time.sleep')
    def test_attempt_publish_rate_limit_error(self, mock_sleep, mock_service, mock_db, scheduled_video_content):
        """Test publish attempt with rate limit error and backoff"""
        with patch.object(mock_service, '_publish_video') as mock_publish:
            error = TikTokShopRateLimitError("Rate limit exceeded")
            error.retry_after = 5
            mock_publish.side_effect = error

            success, result = mock_service._attempt_publish(scheduled_video_content, 1, mock_db)

        assert success is False
        assert result is None
        assert "Rate limit exceeded" in scheduled_video_content.error_message
        mock_sleep.assert_called_once_with(5)

    @patch('services.publishing_service.time.sleep')
    def test_attempt_publish_rate_limit_exponential_backoff(self, mock_sleep, mock_service, mock_db, scheduled_video_content):
        """Test rate limit error with exponential backoff"""
        with patch.object(mock_service, '_publish_video') as mock_publish:
            error = TikTokShopRateLimitError("Rate limit exceeded")
            error.retry_after = None  # No retry_after, should use exponential backoff
            mock_publish.side_effect = error

            success, result = mock_service._attempt_publish(scheduled_video_content, 2, mock_db)

        assert success is False
        # Attempt 2 should have backoff of INITIAL_BACKOFF * 2^1 = 1.0 * 2 = 2.0
        mock_sleep.assert_called_once_with(2.0)

    @patch('services.publishing_service.time.sleep')
    def test_attempt_publish_server_error(self, mock_sleep, mock_service, mock_db, scheduled_video_content):
        """Test publish attempt with server error and backoff"""
        with patch.object(mock_service, '_publish_video') as mock_publish:
            mock_publish.side_effect = TikTokShopServerError("Internal server error")

            success, result = mock_service._attempt_publish(scheduled_video_content, 1, mock_db)

        assert success is False
        assert "Server/Network error" in scheduled_video_content.error_message
        mock_sleep.assert_called_once()

    @patch('services.publishing_service.time.sleep')
    def test_attempt_publish_network_error(self, mock_sleep, mock_service, mock_db, scheduled_video_content):
        """Test publish attempt with network error and backoff"""
        with patch.object(mock_service, '_publish_video') as mock_publish:
            mock_publish.side_effect = TikTokShopNetworkError("Connection timeout")

            success, result = mock_service._attempt_publish(scheduled_video_content, 1, mock_db)

        assert success is False
        assert "Server/Network error" in scheduled_video_content.error_message
        mock_sleep.assert_called_once()

    def test_attempt_publish_unexpected_error(self, mock_service, mock_db, scheduled_video_content):
        """Test publish attempt with unexpected error"""
        with patch.object(mock_service, '_publish_video') as mock_publish:
            mock_publish.side_effect = Exception("Unexpected error")

            success, result = mock_service._attempt_publish(scheduled_video_content, 1, mock_db)

        assert success is False
        assert "Unexpected error" in scheduled_video_content.error_message

    def test_attempt_publish_creates_log_entry(self, mock_service, mock_db, scheduled_video_content):
        """Test that publish attempt creates a log entry"""
        with patch.object(mock_service, '_publish_video') as mock_publish:
            mock_publish.return_value = {"video_id": "video_123"}

            mock_service._attempt_publish(scheduled_video_content, 1, mock_db)

        # Verify log entry was added
        mock_db.add.assert_called_once()
        added_log = mock_db.add.call_args[0][0]
        assert isinstance(added_log, PublishLog)
        assert added_log.scheduled_content_id == 1
        assert added_log.attempt_number == 1


class TestPublishVideo:
    """Test suite for _publish_video method"""

    @pytest.fixture
    def mock_service(self):
        """Create mock publishing service"""
        mock_client = Mock()
        return PublishingService(tiktok_client=mock_client)

    def test_publish_video_success(self, mock_service):
        """Test successful video publishing"""
        content_data = {
            "video_url": "https://example.com/video.mp4",
            "title": "Test Video",
            "description": "Test description",
            "product_ids": ["123"],
            "tags": ["test", "video"]
        }

        mock_service.tiktok_client.upload_video.return_value = {
            "data": {
                "video_id": "video_123",
                "status": "published"
            }
        }

        result = mock_service._publish_video(content_data)

        assert result["video_id"] == "video_123"
        assert result["status"] == "published"
        mock_service.tiktok_client.upload_video.assert_called_once_with(
            video_url="https://example.com/video.mp4",
            title="Test Video",
            description="Test description",
            product_ids=["123"],
            tags=["test", "video"]
        )

    def test_publish_video_missing_url(self, mock_service):
        """Test video publishing with missing video_url"""
        content_data = {
            "title": "Test Video"
        }

        with pytest.raises(TikTokShopValidationError) as exc_info:
            mock_service._publish_video(content_data)

        assert "video_url" in str(exc_info.value)

    def test_publish_video_missing_title(self, mock_service):
        """Test video publishing with missing title"""
        content_data = {
            "video_url": "https://example.com/video.mp4"
        }

        with pytest.raises(TikTokShopValidationError) as exc_info:
            mock_service._publish_video(content_data)

        assert "title" in str(exc_info.value)

    def test_publish_video_invalid_response(self, mock_service):
        """Test video publishing with invalid API response"""
        content_data = {
            "video_url": "https://example.com/video.mp4",
            "title": "Test Video"
        }

        mock_service.tiktok_client.upload_video.return_value = {
            "data": {}  # Missing video_id
        }

        with pytest.raises(TikTokShopAPIError) as exc_info:
            mock_service._publish_video(content_data)

        assert "missing video_id" in str(exc_info.value)

    def test_publish_video_minimal_data(self, mock_service):
        """Test video publishing with minimal required data"""
        content_data = {
            "video_url": "https://example.com/video.mp4",
            "title": "Test Video"
        }

        mock_service.tiktok_client.upload_video.return_value = {
            "data": {
                "video_id": "video_123",
                "status": "processing"
            }
        }

        result = mock_service._publish_video(content_data)

        assert result["video_id"] == "video_123"
        mock_service.tiktok_client.upload_video.assert_called_once_with(
            video_url="https://example.com/video.mp4",
            title="Test Video",
            description=None,
            product_ids=None,
            tags=None
        )


class TestPublishPost:
    """Test suite for _publish_post method"""

    @pytest.fixture
    def mock_service(self):
        """Create mock publishing service"""
        mock_client = Mock()
        return PublishingService(tiktok_client=mock_client)

    def test_publish_post_success(self, mock_service):
        """Test successful post publishing"""
        content_data = {
            "content": "Test post content",
            "media_urls": ["https://example.com/image.jpg"],
            "product_ids": ["123"],
            "tags": ["test", "post"]
        }

        mock_service.tiktok_client.create_post.return_value = {
            "data": {
                "post_id": "post_123",
                "status": "published",
                "url": "https://tiktok.com/post/123"
            }
        }

        result = mock_service._publish_post(content_data)

        assert result["post_id"] == "post_123"
        assert result["status"] == "published"
        assert result["url"] == "https://tiktok.com/post/123"
        mock_service.tiktok_client.create_post.assert_called_once_with(
            content="Test post content",
            media_urls=["https://example.com/image.jpg"],
            product_ids=["123"],
            tags=["test", "post"]
        )

    def test_publish_post_missing_content(self, mock_service):
        """Test post publishing with missing content"""
        content_data = {
            "product_ids": ["123"]
        }

        with pytest.raises(TikTokShopValidationError) as exc_info:
            mock_service._publish_post(content_data)

        assert "content" in str(exc_info.value)

    def test_publish_post_invalid_response(self, mock_service):
        """Test post publishing with invalid API response"""
        content_data = {
            "content": "Test post"
        }

        mock_service.tiktok_client.create_post.return_value = {
            "data": {}  # Missing post_id
        }

        with pytest.raises(TikTokShopAPIError) as exc_info:
            mock_service._publish_post(content_data)

        assert "missing post_id" in str(exc_info.value)

    def test_publish_post_minimal_data(self, mock_service):
        """Test post publishing with minimal required data"""
        content_data = {
            "content": "Simple test post"
        }

        mock_service.tiktok_client.create_post.return_value = {
            "data": {
                "post_id": "post_123",
                "status": "published"
            }
        }

        result = mock_service._publish_post(content_data)

        assert result["post_id"] == "post_123"
        mock_service.tiktok_client.create_post.assert_called_once_with(
            content="Simple test post",
            media_urls=None,
            product_ids=None,
            tags=None
        )


class TestBackoffCalculation:
    """Test suite for exponential backoff calculation"""

    @pytest.fixture
    def mock_service(self):
        """Create mock publishing service"""
        mock_client = Mock()
        return PublishingService(tiktok_client=mock_client)

    @patch('services.publishing_service.time.sleep')
    def test_exponential_backoff_attempt_1(self, mock_sleep, mock_service, mock_db=Mock()):
        """Test backoff calculation for first attempt"""
        scheduled_content = ScheduledContent(
            id=1,
            content_type="video",
            content_data=json.dumps({"video_url": "test.mp4", "title": "Test"}),
            scheduled_time=datetime.utcnow(),
            status="pending",
            retry_count=0,
            max_retries=3,
            created_at=datetime.utcnow()
        )

        with patch.object(mock_service, '_publish_video') as mock_publish:
            error = TikTokShopServerError("Server error")
            mock_publish.side_effect = error

            mock_service._attempt_publish(scheduled_content, 1, mock_db)

        # Attempt 1: backoff = 1.0 * 2^0 = 1.0
        mock_sleep.assert_called_once_with(1.0)

    @patch('services.publishing_service.time.sleep')
    def test_exponential_backoff_max_backoff(self, mock_sleep, mock_service, mock_db=Mock()):
        """Test that backoff doesn't exceed max backoff"""
        scheduled_content = ScheduledContent(
            id=1,
            content_type="video",
            content_data=json.dumps({"video_url": "test.mp4", "title": "Test"}),
            scheduled_time=datetime.utcnow(),
            status="pending",
            retry_count=0,
            max_retries=10,
            created_at=datetime.utcnow()
        )

        with patch.object(mock_service, '_publish_video') as mock_publish:
            error = TikTokShopServerError("Server error")
            mock_publish.side_effect = error

            # Attempt 9 with max_retries 10 should still sleep
            # Backoff = 1.0 * 2^8 = 256, which exceeds max of 32.0
            mock_service._attempt_publish(scheduled_content, 9, mock_db)

        # Should be capped at max backoff (32.0 seconds)
        backoff_time = mock_sleep.call_args[0][0]
        assert backoff_time == PublishingService.MAX_BACKOFF_SECONDS


class TestEdgeCases:
    """Test suite for edge cases and error handling"""

    @pytest.fixture
    def mock_service(self):
        """Create mock publishing service"""
        mock_client = Mock()
        return PublishingService(tiktok_client=mock_client)

    def test_publish_unknown_content_type(self, mock_service, mock_db=Mock()):
        """Test publishing with unknown content type"""
        scheduled_content = ScheduledContent(
            id=1,
            content_type="unknown",
            content_data=json.dumps({"data": "test"}),
            scheduled_time=datetime.utcnow(),
            status="pending",
            retry_count=0,
            max_retries=3,
            created_at=datetime.utcnow()
        )

        success, result = mock_service._attempt_publish(scheduled_content, 1, mock_db)

        assert success is False
        assert result is None
        assert "Unknown content type" in scheduled_content.error_message

    def test_publish_invalid_json_content_data(self, mock_service, mock_db=Mock()):
        """Test publishing with invalid JSON in content_data"""
        scheduled_content = ScheduledContent(
            id=1,
            content_type="video",
            content_data="invalid json",
            scheduled_time=datetime.utcnow(),
            status="pending",
            retry_count=0,
            max_retries=3,
            created_at=datetime.utcnow()
        )

        success, result = mock_service._attempt_publish(scheduled_content, 1, mock_db)

        assert success is False
        assert result is None

    @patch('services.publishing_service.get_db_session')
    def test_publish_database_error_rollback(self, mock_get_db, mock_service):
        """Test that database errors trigger rollback"""
        mock_db = Mock()
        mock_get_db.return_value = mock_db

        # Make query raise an exception
        mock_db.query.side_effect = Exception("Database connection error")

        with pytest.raises(DatabaseError):
            mock_service.publish_content(1)

        mock_db.rollback.assert_called_once()
        mock_db.close.assert_called_once()
