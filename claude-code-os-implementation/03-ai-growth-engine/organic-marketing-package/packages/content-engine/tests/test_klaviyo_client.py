"""
Integration tests for Klaviyo API client.

Tests cover:
- Client initialization and authentication
- Profile management (create, update, get, search)
- Event tracking
- List management
- Segment operations
- Error handling and retries
- Rate limiting
"""

import pytest
import os
from unittest.mock import patch, Mock, MagicMock
from datetime import datetime
import requests
import time

from integrations.klaviyo.client import KlaviyoClient
from integrations.klaviyo.models import (
    KlaviyoProfile,
    KlaviyoEvent,
    KlaviyoList,
    KlaviyoSegment,
    ProfileLocation
)
from integrations.klaviyo.exceptions import (
    KlaviyoAPIError,
    KlaviyoAuthError,
    KlaviyoRateLimitError,
    KlaviyoValidationError,
    KlaviyoNotFoundError,
    KlaviyoServerError,
    KlaviyoNetworkError
)


class TestClientInitialization:
    """Test suite for KlaviyoClient initialization and setup"""

    @patch.dict('os.environ', {'KLAVIYO_API_KEY': 'test_key_123', 'KLAVIYO_API_BASE_URL': 'https://a.klaviyo.com/api'})
    def test_client_initialization_with_env_vars(self):
        """Test client initializes correctly with environment variables"""
        client = KlaviyoClient()

        assert client is not None
        assert client.api_key == 'test_key_123'
        assert client.api_base_url == 'https://a.klaviyo.com/api'
        assert client._rate_limiter is not None

    def test_client_initialization_with_params(self):
        """Test client initializes correctly with explicit parameters"""
        client = KlaviyoClient(
            api_key='explicit_key_456',
            api_base_url='https://custom.klaviyo.com/api'
        )

        assert client.api_key == 'explicit_key_456'
        assert client.api_base_url == 'https://custom.klaviyo.com/api'

    @patch.dict('os.environ', {}, clear=True)
    def test_client_initialization_missing_credentials(self):
        """Test client raises error when credentials are missing"""
        with pytest.raises(KlaviyoAuthError):
            KlaviyoClient()

    @patch.dict('os.environ', {'KLAVIYO_API_KEY': 'test_key'})
    def test_client_has_correct_default_settings(self):
        """Test client has correct default configuration"""
        client = KlaviyoClient()

        assert client.DEFAULT_TIMEOUT == 30
        assert client.API_REVISION == "2024-10-15"
        assert client.DEFAULT_RATE_LIMIT == 10.0
        assert client.MAX_RETRY_ATTEMPTS == 3


class TestAuthenticationHeaders:
    """Test suite for authentication header generation"""

    @patch.dict('os.environ', {'KLAVIYO_API_KEY': 'test_key_789'})
    def test_get_headers_includes_authorization(self):
        """Test that auth headers include authorization token"""
        client = KlaviyoClient()
        headers = client._get_headers()

        assert 'Authorization' in headers
        assert 'Klaviyo-API-Key' in headers['Authorization'] or headers['Authorization'].startswith('Klaviyo-API-Key')

    @patch.dict('os.environ', {'KLAVIYO_API_KEY': 'test_key_789'})
    def test_get_headers_includes_content_type(self):
        """Test that auth headers include content type"""
        client = KlaviyoClient()
        headers = client._get_headers()

        assert 'Content-Type' in headers or 'content-type' in headers

    @patch.dict('os.environ', {'KLAVIYO_API_KEY': 'test_key_789'})
    def test_get_headers_includes_api_revision(self):
        """Test that auth headers include API revision"""
        client = KlaviyoClient()
        headers = client._get_headers()

        assert 'revision' in headers or 'Revision' in headers


class TestProfileOperations:
    """Test suite for profile management operations"""

    @patch.dict('os.environ', {'KLAVIYO_API_KEY': 'test_key'})
    @patch('integrations.klaviyo.client.requests.request')
    def test_create_profile_success(self, mock_request):
        """Test successful profile creation"""
        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.ok = True
        mock_response.text = '{"data": {"id": "profile_123", "type": "profile", "attributes": {"email": "test@example.com"}}}'
        mock_response.json.return_value = {
            "data": {
                "id": "profile_123",
                "type": "profile",
                "attributes": {
                    "email": "test@example.com",
                    "first_name": "John",
                    "last_name": "Doe"
                }
            }
        }
        mock_request.return_value = mock_response

        client = KlaviyoClient()
        profile = KlaviyoProfile(
            email="test@example.com",
            first_name="John",
            last_name="Doe"
        )

        result = client.create_profile(profile)

        assert mock_request.called
        assert result.profile_id == "profile_123"
        assert result.email == "test@example.com"

    @patch.dict('os.environ', {'KLAVIYO_API_KEY': 'test_key'})
    @patch('integrations.klaviyo.client.requests.request')
    def test_update_profile_success(self, mock_request):
        """Test successful profile update"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.ok = True
        mock_response.text = '{}'
        mock_response.json.return_value = {
            "data": {
                "id": "profile_123",
                "type": "profile",
                "attributes": {
                    "email": "test@example.com",
                    "first_name": "Jane"
                }
            }
        }
        mock_request.return_value = mock_response

        client = KlaviyoClient()
        profile = KlaviyoProfile(
            profile_id="profile_123",
            email="test@example.com",
            first_name="Jane"
        )

        result = client.update_profile(profile)

        assert mock_request.called
        assert result.first_name == "Jane"

    @patch.dict('os.environ', {'KLAVIYO_API_KEY': 'test_key'})
    def test_update_profile_without_id_raises_error(self):
        """Test that updating profile without ID raises validation error"""
        client = KlaviyoClient()
        profile = KlaviyoProfile(email="test@example.com")

        with pytest.raises(KlaviyoValidationError):
            client.update_profile(profile)

    @patch.dict('os.environ', {'KLAVIYO_API_KEY': 'test_key'})
    @patch('integrations.klaviyo.client.requests.request')
    def test_get_profile_success(self, mock_request):
        """Test successful profile retrieval"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.ok = True
        mock_response.text = '{}'
        mock_response.json.return_value = {
            "data": {
                "id": "profile_123",
                "type": "profile",
                "attributes": {
                    "email": "test@example.com"
                }
            }
        }
        mock_request.return_value = mock_response

        client = KlaviyoClient()
        result = client.get_profile("profile_123")

        assert result.profile_id == "profile_123"
        assert result.email == "test@example.com"

    @patch.dict('os.environ', {'KLAVIYO_API_KEY': 'test_key'})
    @patch('integrations.klaviyo.client.requests.request')
    def test_search_profiles_by_email(self, mock_request):
        """Test searching profiles by email"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.ok = True
        mock_response.text = '{}'
        mock_response.json.return_value = {
            "data": [
                {
                    "id": "profile_123",
                    "type": "profile",
                    "attributes": {
                        "email": "test@example.com"
                    }
                }
            ]
        }
        mock_request.return_value = mock_response

        client = KlaviyoClient()
        results = client.search_profiles(email="test@example.com")

        assert len(results) == 1
        assert results[0].email == "test@example.com"

    @patch.dict('os.environ', {'KLAVIYO_API_KEY': 'test_key'})
    def test_search_profiles_no_criteria_raises_error(self):
        """Test that searching without criteria raises validation error"""
        client = KlaviyoClient()

        with pytest.raises(KlaviyoValidationError):
            client.search_profiles()


class TestEventTracking:
    """Test suite for event tracking operations"""

    @patch.dict('os.environ', {'KLAVIYO_API_KEY': 'test_key'})
    @patch('integrations.klaviyo.client.requests.request')
    def test_track_event_success(self, mock_request):
        """Test successful event tracking"""
        mock_response = Mock()
        mock_response.status_code = 202
        mock_response.ok = True
        mock_response.text = '{}'
        mock_response.json.return_value = {
            "data": {
                "id": "event_123",
                "type": "event"
            }
        }
        mock_request.return_value = mock_response

        client = KlaviyoClient()
        event = KlaviyoEvent(
            metric_name="Placed Order",
            customer_email="test@example.com",
            properties={"order_id": "12345", "total": 99.99}
        )

        result = client.track_event(event)

        assert mock_request.called
        assert result["data"]["id"] == "event_123"

    @patch.dict('os.environ', {'KLAVIYO_API_KEY': 'test_key'})
    @patch('integrations.klaviyo.client.requests.request')
    def test_get_events_success(self, mock_request):
        """Test retrieving events"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.ok = True
        mock_response.text = '{}'
        mock_response.json.return_value = {
            "data": [
                {
                    "id": "event_123",
                    "type": "event",
                    "attributes": {
                        "metric_name": "Placed Order"
                    }
                }
            ]
        }
        mock_request.return_value = mock_response

        client = KlaviyoClient()
        results = client.get_events(profile_id="profile_123", limit=10)

        assert len(results) == 1
        assert results[0].metric_name == "Placed Order"


class TestListManagement:
    """Test suite for list management operations"""

    @patch.dict('os.environ', {'KLAVIYO_API_KEY': 'test_key'})
    @patch('integrations.klaviyo.client.requests.request')
    def test_create_list_success(self, mock_request):
        """Test successful list creation"""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.ok = True
        mock_response.text = '{}'
        mock_response.json.return_value = {
            "data": {
                "id": "list_123",
                "type": "list",
                "attributes": {
                    "name": "VIP Customers"
                }
            }
        }
        mock_request.return_value = mock_response

        client = KlaviyoClient()
        list_obj = KlaviyoList(name="VIP Customers")

        result = client.create_list(list_obj)

        assert result.list_id == "list_123"
        assert result.name == "VIP Customers"

    @patch.dict('os.environ', {'KLAVIYO_API_KEY': 'test_key'})
    @patch('integrations.klaviyo.client.requests.request')
    def test_get_list_success(self, mock_request):
        """Test successful list retrieval"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.ok = True
        mock_response.text = '{}'
        mock_response.json.return_value = {
            "data": {
                "id": "list_123",
                "type": "list",
                "attributes": {
                    "name": "VIP Customers"
                }
            }
        }
        mock_request.return_value = mock_response

        client = KlaviyoClient()
        result = client.get_list("list_123")

        assert result.list_id == "list_123"
        assert result.name == "VIP Customers"

    @patch.dict('os.environ', {'KLAVIYO_API_KEY': 'test_key'})
    @patch('integrations.klaviyo.client.requests.request')
    def test_get_lists_success(self, mock_request):
        """Test retrieving all lists"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.ok = True
        mock_response.text = '{}'
        mock_response.json.return_value = {
            "data": [
                {
                    "id": "list_1",
                    "type": "list",
                    "attributes": {"name": "List 1"}
                },
                {
                    "id": "list_2",
                    "type": "list",
                    "attributes": {"name": "List 2"}
                }
            ]
        }
        mock_request.return_value = mock_response

        client = KlaviyoClient()
        results = client.get_lists()

        assert len(results) == 2
        assert results[0].name == "List 1"

    @patch.dict('os.environ', {'KLAVIYO_API_KEY': 'test_key'})
    @patch('integrations.klaviyo.client.requests.request')
    def test_add_profiles_to_list_success(self, mock_request):
        """Test adding profiles to a list"""
        mock_response = Mock()
        mock_response.status_code = 204
        mock_response.ok = True
        mock_response.text = ''
        mock_response.json.return_value = {}
        mock_request.return_value = mock_response

        client = KlaviyoClient()
        result = client.add_profiles_to_list("list_123", ["profile_1", "profile_2"])

        assert mock_request.called

    @patch.dict('os.environ', {'KLAVIYO_API_KEY': 'test_key'})
    def test_add_profiles_to_list_validation_error(self):
        """Test that adding profiles without list_id raises error"""
        client = KlaviyoClient()

        with pytest.raises(KlaviyoValidationError):
            client.add_profiles_to_list("", ["profile_1"])

    @patch.dict('os.environ', {'KLAVIYO_API_KEY': 'test_key'})
    @patch('integrations.klaviyo.client.requests.request')
    def test_remove_profiles_from_list_success(self, mock_request):
        """Test removing profiles from a list"""
        mock_response = Mock()
        mock_response.status_code = 204
        mock_response.ok = True
        mock_response.text = ''
        mock_response.json.return_value = {}
        mock_request.return_value = mock_response

        client = KlaviyoClient()
        result = client.remove_profiles_from_list("list_123", ["profile_1"])

        assert mock_request.called


class TestSegmentOperations:
    """Test suite for segment operations"""

    @patch.dict('os.environ', {'KLAVIYO_API_KEY': 'test_key'})
    @patch('integrations.klaviyo.client.requests.request')
    def test_get_segment_success(self, mock_request):
        """Test successful segment retrieval"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.ok = True
        mock_response.text = '{}'
        mock_response.json.return_value = {
            "data": {
                "id": "segment_123",
                "type": "segment",
                "attributes": {
                    "name": "High Value Customers"
                }
            }
        }
        mock_request.return_value = mock_response

        client = KlaviyoClient()
        result = client.get_segment("segment_123")

        assert result.segment_id == "segment_123"
        assert result.name == "High Value Customers"

    @patch.dict('os.environ', {'KLAVIYO_API_KEY': 'test_key'})
    @patch('integrations.klaviyo.client.requests.request')
    def test_get_segments_success(self, mock_request):
        """Test retrieving all segments"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.ok = True
        mock_response.text = '{}'
        mock_response.json.return_value = {
            "data": [
                {
                    "id": "segment_1",
                    "type": "segment",
                    "attributes": {"name": "Segment 1"}
                }
            ]
        }
        mock_request.return_value = mock_response

        client = KlaviyoClient()
        results = client.get_segments()

        assert len(results) == 1

    @patch.dict('os.environ', {'KLAVIYO_API_KEY': 'test_key'})
    @patch('integrations.klaviyo.client.requests.request')
    def test_get_segment_profiles_success(self, mock_request):
        """Test retrieving profiles in a segment"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.ok = True
        mock_response.text = '{}'
        mock_response.json.return_value = {
            "data": [
                {
                    "id": "profile_1",
                    "type": "profile",
                    "attributes": {"email": "test@example.com"}
                }
            ]
        }
        mock_request.return_value = mock_response

        client = KlaviyoClient()
        results = client.get_segment_profiles("segment_123", limit=50)

        assert len(results) == 1
        assert results[0].email == "test@example.com"


class TestErrorHandling:
    """Test suite for error handling"""

    @patch.dict('os.environ', {'KLAVIYO_API_KEY': 'test_key'})
    @patch('integrations.klaviyo.client.requests.request')
    def test_401_raises_auth_error(self, mock_request):
        """Test that 401 status raises KlaviyoAuthError"""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.ok = False
        mock_response.text = '{"errors": [{"detail": "Invalid API key"}]}'
        mock_response.json.return_value = {"errors": [{"detail": "Invalid API key"}]}
        mock_request.return_value = mock_response

        client = KlaviyoClient()

        with pytest.raises(KlaviyoAuthError) as exc_info:
            client.get_profile("profile_123")

        assert exc_info.value.status_code == 401

    @patch.dict('os.environ', {'KLAVIYO_API_KEY': 'test_key'})
    @patch('integrations.klaviyo.client.requests.request')
    def test_403_raises_auth_error(self, mock_request):
        """Test that 403 status raises KlaviyoAuthError"""
        mock_response = Mock()
        mock_response.status_code = 403
        mock_response.ok = False
        mock_response.text = '{"errors": [{"detail": "Insufficient permissions"}]}'
        mock_response.json.return_value = {"errors": [{"detail": "Insufficient permissions"}]}
        mock_request.return_value = mock_response

        client = KlaviyoClient()

        with pytest.raises(KlaviyoAuthError):
            client.get_profile("profile_123")

    @patch.dict('os.environ', {'KLAVIYO_API_KEY': 'test_key'})
    @patch('integrations.klaviyo.client.requests.request')
    def test_404_raises_not_found_error(self, mock_request):
        """Test that 404 status raises KlaviyoNotFoundError"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.ok = False
        mock_response.text = '{"errors": [{"detail": "Profile not found"}]}'
        mock_response.json.return_value = {"errors": [{"detail": "Profile not found"}]}
        mock_request.return_value = mock_response

        client = KlaviyoClient()

        with pytest.raises(KlaviyoNotFoundError):
            client.get_profile("invalid_profile")

    @patch.dict('os.environ', {'KLAVIYO_API_KEY': 'test_key'})
    @patch('integrations.klaviyo.client.requests.request')
    def test_400_raises_validation_error(self, mock_request):
        """Test that 400 status raises KlaviyoValidationError"""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.ok = False
        mock_response.text = '{"errors": [{"detail": "Invalid email format"}]}'
        mock_response.json.return_value = {"errors": [{"detail": "Invalid email format"}]}
        mock_request.return_value = mock_response

        client = KlaviyoClient()
        profile = KlaviyoProfile(email="invalid")

        with pytest.raises(KlaviyoValidationError):
            client.create_profile(profile)

    @patch.dict('os.environ', {'KLAVIYO_API_KEY': 'test_key'})
    @patch('integrations.klaviyo.client.requests.request')
    def test_422_raises_validation_error(self, mock_request):
        """Test that 422 status raises KlaviyoValidationError"""
        mock_response = Mock()
        mock_response.status_code = 422
        mock_response.ok = False
        mock_response.text = '{"errors": [{"detail": "Validation failed"}]}'
        mock_response.json.return_value = {"errors": [{"detail": "Validation failed"}]}
        mock_request.return_value = mock_response

        client = KlaviyoClient()
        profile = KlaviyoProfile(email="test@example.com")

        with pytest.raises(KlaviyoValidationError):
            client.create_profile(profile)

    @patch.dict('os.environ', {'KLAVIYO_API_KEY': 'test_key'})
    @patch('integrations.klaviyo.client.requests.request')
    def test_500_raises_server_error(self, mock_request):
        """Test that 500 status raises KlaviyoServerError"""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.ok = False
        mock_response.text = '{"errors": [{"detail": "Internal server error"}]}'
        mock_response.json.return_value = {"errors": [{"detail": "Internal server error"}]}
        mock_request.return_value = mock_response

        client = KlaviyoClient()

        with pytest.raises(KlaviyoServerError):
            client.get_profile("profile_123")


class TestRateLimiting:
    """Test suite for rate limiting and retry logic"""

    @patch.dict('os.environ', {'KLAVIYO_API_KEY': 'test_key'})
    @patch('integrations.klaviyo.client.requests.request')
    @patch('integrations.klaviyo.client.time.sleep')
    def test_429_triggers_retry(self, mock_sleep, mock_request):
        """Test that 429 status triggers retry with backoff"""
        # First call returns 429, second call succeeds
        mock_response_429 = Mock()
        mock_response_429.status_code = 429
        mock_response_429.ok = False
        mock_response_429.text = '{"errors": [{"detail": "Rate limit exceeded"}]}'
        mock_response_429.json.return_value = {"errors": [{"detail": "Rate limit exceeded"}]}
        mock_response_429.headers = {'Retry-After': '2'}

        mock_response_200 = Mock()
        mock_response_200.status_code = 200
        mock_response_200.ok = True
        mock_response_200.text = '{}'
        mock_response_200.json.return_value = {
            "data": {
                "id": "profile_123",
                "type": "profile",
                "attributes": {"email": "test@example.com"}
            }
        }

        mock_request.side_effect = [mock_response_429, mock_response_200]

        client = KlaviyoClient()
        result = client.get_profile("profile_123")

        assert mock_sleep.called
        assert result.profile_id == "profile_123"

    @patch.dict('os.environ', {'KLAVIYO_API_KEY': 'test_key'})
    @patch('integrations.klaviyo.client.requests.request')
    def test_429_exceeds_max_retries(self, mock_request):
        """Test that rate limit errors fail after max retries"""
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.ok = False
        mock_response.text = '{"errors": [{"detail": "Rate limit exceeded"}]}'
        mock_response.json.return_value = {"errors": [{"detail": "Rate limit exceeded"}]}
        mock_response.headers = {}
        mock_request.return_value = mock_response

        client = KlaviyoClient()

        with pytest.raises(KlaviyoRateLimitError):
            client.get_profile("profile_123")

    @patch.dict('os.environ', {'KLAVIYO_API_KEY': 'test_key'})
    @patch('integrations.klaviyo.client.requests.request')
    @patch('integrations.klaviyo.client.time.sleep')
    def test_server_error_triggers_retry(self, mock_sleep, mock_request):
        """Test that server errors trigger retry"""
        # First call returns 503, second call succeeds
        mock_response_503 = Mock()
        mock_response_503.status_code = 503
        mock_response_503.ok = False
        mock_response_503.text = '{"errors": [{"detail": "Service unavailable"}]}'
        mock_response_503.json.return_value = {"errors": [{"detail": "Service unavailable"}]}

        mock_response_200 = Mock()
        mock_response_200.status_code = 200
        mock_response_200.ok = True
        mock_response_200.text = '{}'
        mock_response_200.json.return_value = {
            "data": {
                "id": "profile_123",
                "type": "profile",
                "attributes": {"email": "test@example.com"}
            }
        }

        mock_request.side_effect = [mock_response_503, mock_response_200]

        client = KlaviyoClient()
        result = client.get_profile("profile_123")

        assert mock_sleep.called
        assert result.profile_id == "profile_123"


class TestNetworkErrors:
    """Test suite for network error handling"""

    @patch.dict('os.environ', {'KLAVIYO_API_KEY': 'test_key'})
    @patch('integrations.klaviyo.client.requests.request')
    def test_connection_error_raises_network_error(self, mock_request):
        """Test that connection errors raise KlaviyoNetworkError"""
        mock_request.side_effect = requests.exceptions.ConnectionError("Connection failed")

        client = KlaviyoClient()

        with pytest.raises(KlaviyoNetworkError):
            client.get_profile("profile_123")

    @patch.dict('os.environ', {'KLAVIYO_API_KEY': 'test_key'})
    @patch('integrations.klaviyo.client.requests.request')
    def test_timeout_error_raises_network_error(self, mock_request):
        """Test that timeout errors raise KlaviyoNetworkError"""
        mock_request.side_effect = requests.exceptions.Timeout("Request timeout")

        client = KlaviyoClient()

        with pytest.raises(KlaviyoNetworkError):
            client.get_profile("profile_123")

    @patch.dict('os.environ', {'KLAVIYO_API_KEY': 'test_key'})
    @patch('integrations.klaviyo.client.requests.request')
    @patch('integrations.klaviyo.client.time.sleep')
    def test_network_error_triggers_retry(self, mock_sleep, mock_request):
        """Test that network errors trigger retry"""
        # First call raises timeout, second call succeeds
        mock_response_200 = Mock()
        mock_response_200.status_code = 200
        mock_response_200.ok = True
        mock_response_200.text = '{}'
        mock_response_200.json.return_value = {
            "data": {
                "id": "profile_123",
                "type": "profile",
                "attributes": {"email": "test@example.com"}
            }
        }

        mock_request.side_effect = [
            requests.exceptions.Timeout("Request timeout"),
            mock_response_200
        ]

        client = KlaviyoClient()
        result = client.get_profile("profile_123")

        assert mock_sleep.called
        assert result.profile_id == "profile_123"


class TestErrorResponseParsing:
    """Test suite for error response parsing"""

    @patch.dict('os.environ', {'KLAVIYO_API_KEY': 'test_key'})
    def test_parse_error_response_with_errors_array(self):
        """Test parsing error response with errors array"""
        client = KlaviyoClient()

        mock_response = Mock()
        mock_response.json.return_value = {
            "errors": [
                {"detail": "Test error message"}
            ]
        }
        mock_response.text = '{"errors": [{"detail": "Test error message"}]}'

        error_msg = client._parse_error_response(mock_response)

        assert error_msg == "Test error message"

    @patch.dict('os.environ', {'KLAVIYO_API_KEY': 'test_key'})
    def test_parse_error_response_with_message_field(self):
        """Test parsing error response with message field"""
        client = KlaviyoClient()

        mock_response = Mock()
        mock_response.json.return_value = {
            "message": "Error message from API"
        }
        mock_response.text = '{"message": "Error message from API"}'

        error_msg = client._parse_error_response(mock_response)

        assert error_msg == "Error message from API"

    @patch.dict('os.environ', {'KLAVIYO_API_KEY': 'test_key'})
    def test_parse_error_response_fallback_to_text(self):
        """Test parsing error response falls back to text"""
        client = KlaviyoClient()

        mock_response = Mock()
        mock_response.json.side_effect = Exception("Not JSON")
        mock_response.text = "Plain text error"
        mock_response.status_code = 500

        error_msg = client._parse_error_response(mock_response)

        assert error_msg == "Plain text error"


class TestRetryLogic:
    """Test suite for retry logic and backoff"""

    @patch.dict('os.environ', {'KLAVIYO_API_KEY': 'test_key'})
    def test_handle_error_rate_limit_with_retry_after(self):
        """Test retry logic uses retry_after from rate limit error"""
        client = KlaviyoClient()

        error = KlaviyoRateLimitError("Rate limited", retry_after=5)
        should_retry, wait_time = client._handle_error(error, retry_count=0)

        assert should_retry is True
        assert wait_time == 5

    @patch.dict('os.environ', {'KLAVIYO_API_KEY': 'test_key'})
    def test_handle_error_rate_limit_exponential_backoff(self):
        """Test retry logic uses exponential backoff for rate limits"""
        client = KlaviyoClient()

        error = KlaviyoRateLimitError("Rate limited", retry_after=None)
        should_retry, wait_time = client._handle_error(error, retry_count=1)

        assert should_retry is True
        assert wait_time == 2.0  # INITIAL_BACKOFF_SECONDS * (2 ** 1)

    @patch.dict('os.environ', {'KLAVIYO_API_KEY': 'test_key'})
    def test_handle_error_max_retries_exceeded(self):
        """Test retry logic stops after max retries"""
        client = KlaviyoClient()

        error = KlaviyoRateLimitError("Rate limited")
        should_retry, wait_time = client._handle_error(error, retry_count=10)

        assert should_retry is False

    @patch.dict('os.environ', {'KLAVIYO_API_KEY': 'test_key'})
    def test_handle_error_server_error_retries(self):
        """Test server errors are retried"""
        client = KlaviyoClient()

        error = KlaviyoServerError("Server error")
        should_retry, wait_time = client._handle_error(error, retry_count=0)

        assert should_retry is True
        assert wait_time > 0

    @patch.dict('os.environ', {'KLAVIYO_API_KEY': 'test_key'})
    def test_handle_error_network_error_retries(self):
        """Test network errors are retried"""
        client = KlaviyoClient()

        error = KlaviyoNetworkError("Network error")
        should_retry, wait_time = client._handle_error(error, retry_count=0)

        assert should_retry is True
        assert wait_time > 0

    @patch.dict('os.environ', {'KLAVIYO_API_KEY': 'test_key'})
    def test_handle_error_auth_error_no_retry(self):
        """Test auth errors are not retried"""
        client = KlaviyoClient()

        error = KlaviyoAuthError("Auth failed")
        should_retry, wait_time = client._handle_error(error, retry_count=0)

        assert should_retry is False

    @patch.dict('os.environ', {'KLAVIYO_API_KEY': 'test_key'})
    def test_handle_error_validation_error_no_retry(self):
        """Test validation errors are not retried"""
        client = KlaviyoClient()

        error = KlaviyoValidationError("Validation failed")
        should_retry, wait_time = client._handle_error(error, retry_count=0)

        assert should_retry is False

    @patch.dict('os.environ', {'KLAVIYO_API_KEY': 'test_key'})
    def test_handle_error_not_found_error_no_retry(self):
        """Test not found errors are not retried"""
        client = KlaviyoClient()

        error = KlaviyoNotFoundError("Not found")
        should_retry, wait_time = client._handle_error(error, retry_count=0)

        assert should_retry is False
