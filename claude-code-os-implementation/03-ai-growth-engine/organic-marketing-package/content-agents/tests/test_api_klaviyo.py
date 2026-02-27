"""
Integration tests for Klaviyo API endpoints.

Tests cover:
- Profile creation and updates
- Profile retrieval and search
- Event tracking
- List management
- Profile list operations
- Request validation
- Error handling
- Response structure
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock, MagicMock
from datetime import datetime

from api.main import app
from integrations.klaviyo.client import KlaviyoClient
from integrations.klaviyo.exceptions import (
    KlaviyoAPIError,
    KlaviyoAuthError,
    KlaviyoRateLimitError,
    KlaviyoValidationError,
    KlaviyoNotFoundError
)


class TestProfileCreationAndUpdates:
    """Test suite for /api/klaviyo/profiles endpoint"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    @pytest.fixture
    def mock_klaviyo_client(self):
        """Mock KlaviyoClient for testing"""
        with patch('api.routes.klaviyo.KlaviyoClient') as mock_client_class:
            mock_client = Mock(spec=KlaviyoClient)
            mock_client.create_or_update_profile.return_value = {
                "id": "01HXYZ123",
                "type": "profile",
                "attributes": {
                    "email": "customer@example.com",
                    "first_name": "John",
                    "last_name": "Doe"
                }
            }
            mock_client_class.return_value = mock_client
            yield mock_client

    def test_create_profile_success(self, client, mock_klaviyo_client):
        """Test successful profile creation"""
        request_data = {
            "email": "customer@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "phone_number": "+14155551234",
            "external_id": "customer_12345",
            "properties": {
                "customer_tier": "VIP",
                "lifetime_value": 5000.00
            }
        }

        response = client.post("/api/klaviyo/profiles", json=request_data)

        assert response.status_code == 200
        data = response.json()

        assert "request_id" in data
        assert "profile_id" in data
        assert "email" in data
        assert data["status"] == "success"
        assert data["email"] == "customer@example.com"
        assert data["message"] == "Profile created/updated successfully"

    def test_create_profile_minimal_request(self, client, mock_klaviyo_client):
        """Test profile creation with minimal required fields"""
        request_data = {
            "email": "minimal@example.com"
        }

        response = client.post("/api/klaviyo/profiles", json=request_data)

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "success"
        assert data["email"] == "minimal@example.com"

        # Verify client was called
        mock_klaviyo_client.create_or_update_profile.assert_called_once()

    def test_create_profile_with_location(self, client, mock_klaviyo_client):
        """Test profile creation with location data"""
        request_data = {
            "email": "customer@example.com",
            "first_name": "Jane",
            "location": {
                "city": "San Francisco",
                "region": "CA",
                "country": "United States",
                "zip": "94102",
                "timezone": "America/Los_Angeles"
            }
        }

        response = client.post("/api/klaviyo/profiles", json=request_data)

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "success"

        # Verify location was passed to client
        mock_klaviyo_client.create_or_update_profile.assert_called_once()
        call_args = mock_klaviyo_client.create_or_update_profile.call_args
        profile = call_args[0][0]
        assert profile.location is not None
        assert profile.location.city == "San Francisco"

    def test_create_profile_with_custom_request_id(self, client, mock_klaviyo_client):
        """Test profile creation with custom request ID in header"""
        request_data = {
            "email": "customer@example.com"
        }

        response = client.post(
            "/api/klaviyo/profiles",
            json=request_data,
            headers={"X-Request-ID": "custom-request-123"}
        )

        assert response.status_code == 200
        data = response.json()

        assert data["request_id"] == "custom-request-123"

    def test_create_profile_response_structure(self, client, mock_klaviyo_client):
        """Test that response has correct structure"""
        request_data = {
            "email": "customer@example.com"
        }

        response = client.post("/api/klaviyo/profiles", json=request_data)
        data = response.json()

        assert "request_id" in data
        assert "profile_id" in data
        assert "email" in data
        assert "status" in data
        assert "message" in data
        assert "timestamp" in data

        assert isinstance(data["timestamp"], str)

    def test_create_profile_invalid_email(self, client):
        """Test validation error for invalid email"""
        request_data = {
            "email": "not-a-valid-email"
        }

        response = client.post("/api/klaviyo/profiles", json=request_data)

        assert response.status_code == 422

    def test_create_profile_missing_required_field(self, client):
        """Test validation error when required field is missing"""
        request_data = {
            "first_name": "John"
        }

        response = client.post("/api/klaviyo/profiles", json=request_data)

        assert response.status_code == 422

    def test_create_profile_auth_error(self, client):
        """Test error handling when authentication fails"""
        with patch('api.routes.klaviyo.KlaviyoClient') as mock_client_class:
            mock_client = Mock()
            mock_client.create_or_update_profile.side_effect = KlaviyoAuthError("Invalid API key")
            mock_client_class.return_value = mock_client

            request_data = {
                "email": "customer@example.com"
            }

            response = client.post("/api/klaviyo/profiles", json=request_data)

            assert response.status_code == 401
            data = response.json()

            assert "detail" in data
            assert "KlaviyoAuthError" in str(data["detail"])

    def test_create_profile_validation_error(self, client):
        """Test error handling when Klaviyo validation fails"""
        with patch('api.routes.klaviyo.KlaviyoClient') as mock_client_class:
            mock_client = Mock()
            mock_client.create_or_update_profile.side_effect = KlaviyoValidationError("Invalid data")
            mock_client_class.return_value = mock_client

            request_data = {
                "email": "customer@example.com"
            }

            response = client.post("/api/klaviyo/profiles", json=request_data)

            assert response.status_code == 400
            data = response.json()

            assert "KlaviyoValidationError" in str(data["detail"])

    def test_create_profile_rate_limit_error(self, client):
        """Test error handling when rate limit is exceeded"""
        with patch('api.routes.klaviyo.KlaviyoClient') as mock_client_class:
            mock_client = Mock()
            mock_client.create_or_update_profile.side_effect = KlaviyoRateLimitError("Rate limit exceeded")
            mock_client_class.return_value = mock_client

            request_data = {
                "email": "customer@example.com"
            }

            response = client.post("/api/klaviyo/profiles", json=request_data)

            assert response.status_code == 429
            data = response.json()

            assert "KlaviyoRateLimitError" in str(data["detail"])

    def test_create_profile_generic_error(self, client):
        """Test error handling for generic exceptions"""
        with patch('api.routes.klaviyo.KlaviyoClient') as mock_client_class:
            mock_client = Mock()
            mock_client.create_or_update_profile.side_effect = Exception("Unexpected error")
            mock_client_class.return_value = mock_client

            request_data = {
                "email": "customer@example.com"
            }

            response = client.post("/api/klaviyo/profiles", json=request_data)

            assert response.status_code == 500
            data = response.json()

            assert "ProfileOperationError" in str(data["detail"])


class TestProfileRetrieval:
    """Test suite for /api/klaviyo/profiles/{profile_id} endpoint"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    @pytest.fixture
    def mock_klaviyo_client(self):
        """Mock KlaviyoClient for testing"""
        with patch('api.routes.klaviyo.KlaviyoClient') as mock_client_class:
            mock_client = Mock(spec=KlaviyoClient)
            mock_client.get_profile.return_value = {
                "id": "01HXYZ123",
                "type": "profile",
                "attributes": {
                    "email": "customer@example.com",
                    "first_name": "John",
                    "last_name": "Doe"
                }
            }
            mock_client_class.return_value = mock_client
            yield mock_client

    def test_get_profile_success(self, client, mock_klaviyo_client):
        """Test successful profile retrieval"""
        profile_id = "01HXYZ123"

        response = client.get(f"/api/klaviyo/profiles/{profile_id}")

        assert response.status_code == 200
        data = response.json()

        assert "request_id" in data
        assert "profile" in data
        assert "status" in data
        assert data["status"] == "success"

        profile = data["profile"]
        assert profile["id"] == "01HXYZ123"
        assert profile["attributes"]["email"] == "customer@example.com"

    def test_get_profile_not_found(self, client):
        """Test error handling when profile is not found"""
        with patch('api.routes.klaviyo.KlaviyoClient') as mock_client_class:
            mock_client = Mock()
            mock_client.get_profile.side_effect = KlaviyoNotFoundError("Profile not found")
            mock_client_class.return_value = mock_client

            response = client.get("/api/klaviyo/profiles/invalid_id")

            assert response.status_code == 404
            data = response.json()

            assert "ProfileNotFound" in str(data["detail"])

    def test_get_profile_auth_error(self, client):
        """Test error handling when authentication fails"""
        with patch('api.routes.klaviyo.KlaviyoClient') as mock_client_class:
            mock_client = Mock()
            mock_client.get_profile.side_effect = KlaviyoAuthError("Invalid API key")
            mock_client_class.return_value = mock_client

            response = client.get("/api/klaviyo/profiles/01HXYZ123")

            assert response.status_code == 401
            data = response.json()

            assert "KlaviyoAuthError" in str(data["detail"])

    def test_get_profile_generic_error(self, client):
        """Test error handling for generic exceptions"""
        with patch('api.routes.klaviyo.KlaviyoClient') as mock_client_class:
            mock_client = Mock()
            mock_client.get_profile.side_effect = Exception("Unexpected error")
            mock_client_class.return_value = mock_client

            response = client.get("/api/klaviyo/profiles/01HXYZ123")

            assert response.status_code == 500
            data = response.json()

            assert "ProfileFetchError" in str(data["detail"])


class TestProfileSearch:
    """Test suite for /api/klaviyo/profiles/search endpoint"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    @pytest.fixture
    def mock_klaviyo_client(self):
        """Mock KlaviyoClient for testing"""
        with patch('api.routes.klaviyo.KlaviyoClient') as mock_client_class:
            mock_client = Mock(spec=KlaviyoClient)
            mock_client.search_profiles.return_value = {
                "data": [
                    {
                        "id": "01HXYZ123",
                        "type": "profile",
                        "attributes": {
                            "email": "customer@example.com"
                        }
                    }
                ]
            }
            mock_client_class.return_value = mock_client
            yield mock_client

    def test_search_profiles_by_email(self, client, mock_klaviyo_client):
        """Test successful profile search by email"""
        request_data = {
            "email": "customer@example.com"
        }

        response = client.post("/api/klaviyo/profiles/search", json=request_data)

        assert response.status_code == 200
        data = response.json()

        assert "request_id" in data
        assert "profiles" in data
        assert "count" in data
        assert "status" in data
        assert data["status"] == "success"
        assert data["count"] == 1

    def test_search_profiles_by_phone(self, client, mock_klaviyo_client):
        """Test profile search by phone number"""
        request_data = {
            "phone_number": "+14155551234"
        }

        response = client.post("/api/klaviyo/profiles/search", json=request_data)

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "success"

        # Verify search was called with phone number
        mock_klaviyo_client.search_profiles.assert_called_once()
        call_kwargs = mock_klaviyo_client.search_profiles.call_args.kwargs
        assert call_kwargs["phone_number"] == "+14155551234"

    def test_search_profiles_by_external_id(self, client, mock_klaviyo_client):
        """Test profile search by external ID"""
        request_data = {
            "external_id": "customer_12345"
        }

        response = client.post("/api/klaviyo/profiles/search", json=request_data)

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "success"

        # Verify search was called with external ID
        mock_klaviyo_client.search_profiles.assert_called_once()
        call_kwargs = mock_klaviyo_client.search_profiles.call_args.kwargs
        assert call_kwargs["external_id"] == "customer_12345"

    def test_search_profiles_no_criteria(self, client):
        """Test validation error when no search criteria provided"""
        request_data = {}

        response = client.post("/api/klaviyo/profiles/search", json=request_data)

        assert response.status_code == 400
        data = response.json()

        assert "ValidationError" in str(data["detail"])

    def test_search_profiles_auth_error(self, client):
        """Test error handling when authentication fails"""
        with patch('api.routes.klaviyo.KlaviyoClient') as mock_client_class:
            mock_client = Mock()
            mock_client.search_profiles.side_effect = KlaviyoAuthError("Invalid API key")
            mock_client_class.return_value = mock_client

            request_data = {
                "email": "customer@example.com"
            }

            response = client.post("/api/klaviyo/profiles/search", json=request_data)

            assert response.status_code == 401
            data = response.json()

            assert "KlaviyoAuthError" in str(data["detail"])

    def test_search_profiles_generic_error(self, client):
        """Test error handling for generic exceptions"""
        with patch('api.routes.klaviyo.KlaviyoClient') as mock_client_class:
            mock_client = Mock()
            mock_client.search_profiles.side_effect = Exception("Unexpected error")
            mock_client_class.return_value = mock_client

            request_data = {
                "email": "customer@example.com"
            }

            response = client.post("/api/klaviyo/profiles/search", json=request_data)

            assert response.status_code == 500
            data = response.json()

            assert "ProfileSearchError" in str(data["detail"])


class TestEventTracking:
    """Test suite for /api/klaviyo/events endpoint"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    @pytest.fixture
    def mock_klaviyo_client(self):
        """Mock KlaviyoClient for testing"""
        with patch('api.routes.klaviyo.KlaviyoClient') as mock_client_class:
            mock_client = Mock(spec=KlaviyoClient)
            mock_client.track_event.return_value = {
                "id": "event_123",
                "type": "event"
            }
            mock_client_class.return_value = mock_client
            yield mock_client

    def test_track_event_success(self, client, mock_klaviyo_client):
        """Test successful event tracking"""
        request_data = {
            "metric_name": "Placed Order",
            "customer_email": "customer@example.com",
            "properties": {
                "order_id": "ORD-12345",
                "total": 149.99,
                "items": [
                    {
                        "product_id": "PROD-001",
                        "name": "Tactical Backpack",
                        "price": 149.99,
                        "quantity": 1
                    }
                ]
            }
        }

        response = client.post("/api/klaviyo/events", json=request_data)

        assert response.status_code == 200
        data = response.json()

        assert "request_id" in data
        assert "event_id" in data
        assert "metric_name" in data
        assert "status" in data
        assert data["status"] == "success"
        assert data["metric_name"] == "Placed Order"
        assert data["message"] == "Event tracked successfully"

    def test_track_event_minimal_request(self, client, mock_klaviyo_client):
        """Test event tracking with minimal required fields"""
        request_data = {
            "metric_name": "Page View",
            "customer_email": "customer@example.com"
        }

        response = client.post("/api/klaviyo/events", json=request_data)

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "success"
        assert data["metric_name"] == "Page View"

        # Verify event was tracked
        mock_klaviyo_client.track_event.assert_called_once()

    def test_track_event_with_phone_and_external_id(self, client, mock_klaviyo_client):
        """Test event tracking with additional customer identifiers"""
        request_data = {
            "metric_name": "Added to Cart",
            "customer_email": "customer@example.com",
            "customer_phone": "+14155551234",
            "customer_external_id": "customer_12345",
            "properties": {
                "product_id": "PROD-002"
            }
        }

        response = client.post("/api/klaviyo/events", json=request_data)

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "success"

        # Verify all identifiers were passed
        mock_klaviyo_client.track_event.assert_called_once()
        call_args = mock_klaviyo_client.track_event.call_args
        event = call_args[0][0]
        assert event.customer_phone == "+14155551234"
        assert event.customer_external_id == "customer_12345"

    def test_track_event_invalid_email(self, client):
        """Test validation error for invalid email"""
        request_data = {
            "metric_name": "Test Event",
            "customer_email": "not-a-valid-email"
        }

        response = client.post("/api/klaviyo/events", json=request_data)

        assert response.status_code == 422

    def test_track_event_missing_required_fields(self, client):
        """Test validation error when required fields are missing"""
        request_data = {
            "customer_email": "customer@example.com"
        }

        response = client.post("/api/klaviyo/events", json=request_data)

        assert response.status_code == 422

    def test_track_event_auth_error(self, client):
        """Test error handling when authentication fails"""
        with patch('api.routes.klaviyo.KlaviyoClient') as mock_client_class:
            mock_client = Mock()
            mock_client.track_event.side_effect = KlaviyoAuthError("Invalid API key")
            mock_client_class.return_value = mock_client

            request_data = {
                "metric_name": "Test Event",
                "customer_email": "customer@example.com"
            }

            response = client.post("/api/klaviyo/events", json=request_data)

            assert response.status_code == 401
            data = response.json()

            assert "KlaviyoAuthError" in str(data["detail"])

    def test_track_event_validation_error(self, client):
        """Test error handling when Klaviyo validation fails"""
        with patch('api.routes.klaviyo.KlaviyoClient') as mock_client_class:
            mock_client = Mock()
            mock_client.track_event.side_effect = KlaviyoValidationError("Invalid event data")
            mock_client_class.return_value = mock_client

            request_data = {
                "metric_name": "Test Event",
                "customer_email": "customer@example.com"
            }

            response = client.post("/api/klaviyo/events", json=request_data)

            assert response.status_code == 400
            data = response.json()

            assert "KlaviyoValidationError" in str(data["detail"])

    def test_track_event_generic_error(self, client):
        """Test error handling for generic exceptions"""
        with patch('api.routes.klaviyo.KlaviyoClient') as mock_client_class:
            mock_client = Mock()
            mock_client.track_event.side_effect = Exception("Unexpected error")
            mock_client_class.return_value = mock_client

            request_data = {
                "metric_name": "Test Event",
                "customer_email": "customer@example.com"
            }

            response = client.post("/api/klaviyo/events", json=request_data)

            assert response.status_code == 500
            data = response.json()

            assert "EventTrackingError" in str(data["detail"])


class TestListManagement:
    """Test suite for /api/klaviyo/lists endpoint"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    @pytest.fixture
    def mock_klaviyo_client(self):
        """Mock KlaviyoClient for testing"""
        with patch('api.routes.klaviyo.KlaviyoClient') as mock_client_class:
            mock_client = Mock(spec=KlaviyoClient)
            mock_client.get_lists.return_value = {
                "data": [
                    {
                        "id": "list_123",
                        "type": "list",
                        "attributes": {
                            "name": "VIP Customers",
                            "created": "2024-01-01T00:00:00Z"
                        }
                    },
                    {
                        "id": "list_456",
                        "type": "list",
                        "attributes": {
                            "name": "Newsletter Subscribers",
                            "created": "2024-01-01T00:00:00Z"
                        }
                    }
                ]
            }
            mock_client_class.return_value = mock_client
            yield mock_client

    def test_get_lists_success(self, client, mock_klaviyo_client):
        """Test successful retrieval of all lists"""
        response = client.get("/api/klaviyo/lists")

        assert response.status_code == 200
        data = response.json()

        assert "request_id" in data
        assert "lists" in data
        assert "count" in data
        assert "status" in data
        assert data["status"] == "success"
        assert data["count"] == 2

        lists = data["lists"]
        assert len(lists) == 2
        assert lists[0]["attributes"]["name"] == "VIP Customers"
        assert lists[1]["attributes"]["name"] == "Newsletter Subscribers"

    def test_get_lists_empty(self, client):
        """Test getting lists when no lists exist"""
        with patch('api.routes.klaviyo.KlaviyoClient') as mock_client_class:
            mock_client = Mock()
            mock_client.get_lists.return_value = {"data": []}
            mock_client_class.return_value = mock_client

            response = client.get("/api/klaviyo/lists")

            assert response.status_code == 200
            data = response.json()

            assert data["count"] == 0
            assert data["lists"] == []

    def test_get_lists_auth_error(self, client):
        """Test error handling when authentication fails"""
        with patch('api.routes.klaviyo.KlaviyoClient') as mock_client_class:
            mock_client = Mock()
            mock_client.get_lists.side_effect = KlaviyoAuthError("Invalid API key")
            mock_client_class.return_value = mock_client

            response = client.get("/api/klaviyo/lists")

            assert response.status_code == 401
            data = response.json()

            assert "KlaviyoAuthError" in str(data["detail"])

    def test_get_lists_generic_error(self, client):
        """Test error handling for generic exceptions"""
        with patch('api.routes.klaviyo.KlaviyoClient') as mock_client_class:
            mock_client = Mock()
            mock_client.get_lists.side_effect = Exception("Unexpected error")
            mock_client_class.return_value = mock_client

            response = client.get("/api/klaviyo/lists")

            assert response.status_code == 500
            data = response.json()

            assert "ListFetchError" in str(data["detail"])


class TestListProfileOperations:
    """Test suite for list profile operations"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    @pytest.fixture
    def mock_klaviyo_client(self):
        """Mock KlaviyoClient for testing"""
        with patch('api.routes.klaviyo.KlaviyoClient') as mock_client_class:
            mock_client = Mock(spec=KlaviyoClient)
            mock_client.add_profiles_to_list.return_value = {
                "id": "list_123",
                "type": "list",
                "attributes": {
                    "name": "VIP Customers"
                }
            }
            mock_client.remove_profiles_from_list.return_value = {
                "id": "list_123",
                "type": "list",
                "attributes": {
                    "name": "VIP Customers"
                }
            }
            mock_client_class.return_value = mock_client
            yield mock_client

    def test_add_profiles_to_list_success(self, client, mock_klaviyo_client):
        """Test successfully adding profiles to a list"""
        list_id = "list_123"
        request_data = {
            "profile_ids": ["01H5X123", "01H5Y456"]
        }

        response = client.post(f"/api/klaviyo/lists/{list_id}/profiles", json=request_data)

        assert response.status_code == 200
        data = response.json()

        assert "request_id" in data
        assert "list_id" in data
        assert "list_name" in data
        assert "profile_count" in data
        assert "status" in data
        assert data["status"] == "success"
        assert data["list_id"] == "list_123"
        assert data["list_name"] == "VIP Customers"
        assert data["profile_count"] == 2

    def test_add_profiles_to_list_single_profile(self, client, mock_klaviyo_client):
        """Test adding a single profile to a list"""
        list_id = "list_123"
        request_data = {
            "profile_ids": ["01H5X123"]
        }

        response = client.post(f"/api/klaviyo/lists/{list_id}/profiles", json=request_data)

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "success"
        assert data["profile_count"] == 1

        # Verify correct profile IDs were passed
        mock_klaviyo_client.add_profiles_to_list.assert_called_once()
        call_args = mock_klaviyo_client.add_profiles_to_list.call_args
        assert call_args[0][0] == "list_123"
        assert call_args[0][1] == ["01H5X123"]

    def test_add_profiles_to_list_empty_array(self, client):
        """Test validation error when profile_ids is empty"""
        list_id = "list_123"
        request_data = {
            "profile_ids": []
        }

        response = client.post(f"/api/klaviyo/lists/{list_id}/profiles", json=request_data)

        assert response.status_code == 422

    def test_add_profiles_to_list_not_found(self, client):
        """Test error handling when list is not found"""
        with patch('api.routes.klaviyo.KlaviyoClient') as mock_client_class:
            mock_client = Mock()
            mock_client.add_profiles_to_list.side_effect = KlaviyoNotFoundError("List not found")
            mock_client_class.return_value = mock_client

            list_id = "invalid_list"
            request_data = {
                "profile_ids": ["01H5X123"]
            }

            response = client.post(f"/api/klaviyo/lists/{list_id}/profiles", json=request_data)

            assert response.status_code == 404
            data = response.json()

            assert "ListNotFound" in str(data["detail"])

    def test_add_profiles_to_list_auth_error(self, client):
        """Test error handling when authentication fails"""
        with patch('api.routes.klaviyo.KlaviyoClient') as mock_client_class:
            mock_client = Mock()
            mock_client.add_profiles_to_list.side_effect = KlaviyoAuthError("Invalid API key")
            mock_client_class.return_value = mock_client

            list_id = "list_123"
            request_data = {
                "profile_ids": ["01H5X123"]
            }

            response = client.post(f"/api/klaviyo/lists/{list_id}/profiles", json=request_data)

            assert response.status_code == 401
            data = response.json()

            assert "KlaviyoAuthError" in str(data["detail"])

    def test_add_profiles_to_list_generic_error(self, client):
        """Test error handling for generic exceptions"""
        with patch('api.routes.klaviyo.KlaviyoClient') as mock_client_class:
            mock_client = Mock()
            mock_client.add_profiles_to_list.side_effect = Exception("Unexpected error")
            mock_client_class.return_value = mock_client

            list_id = "list_123"
            request_data = {
                "profile_ids": ["01H5X123"]
            }

            response = client.post(f"/api/klaviyo/lists/{list_id}/profiles", json=request_data)

            assert response.status_code == 500
            data = response.json()

            assert "ListOperationError" in str(data["detail"])

    def test_remove_profile_from_list_success(self, client, mock_klaviyo_client):
        """Test successfully removing a profile from a list"""
        list_id = "list_123"
        profile_id = "01H5X123"

        response = client.delete(f"/api/klaviyo/lists/{list_id}/profiles/{profile_id}")

        assert response.status_code == 200
        data = response.json()

        assert "request_id" in data
        assert "list_id" in data
        assert "list_name" in data
        assert "status" in data
        assert data["status"] == "success"
        assert data["list_id"] == "list_123"
        assert data["message"] == "Successfully removed profile from list"

        # Verify correct parameters were passed
        mock_klaviyo_client.remove_profiles_from_list.assert_called_once()
        call_args = mock_klaviyo_client.remove_profiles_from_list.call_args
        assert call_args[0][0] == "list_123"
        assert call_args[0][1] == ["01H5X123"]

    def test_remove_profile_from_list_not_found(self, client):
        """Test error handling when list or profile is not found"""
        with patch('api.routes.klaviyo.KlaviyoClient') as mock_client_class:
            mock_client = Mock()
            mock_client.remove_profiles_from_list.side_effect = KlaviyoNotFoundError("Resource not found")
            mock_client_class.return_value = mock_client

            list_id = "list_123"
            profile_id = "invalid_profile"

            response = client.delete(f"/api/klaviyo/lists/{list_id}/profiles/{profile_id}")

            assert response.status_code == 404
            data = response.json()

            assert "ResourceNotFound" in str(data["detail"])

    def test_remove_profile_from_list_auth_error(self, client):
        """Test error handling when authentication fails"""
        with patch('api.routes.klaviyo.KlaviyoClient') as mock_client_class:
            mock_client = Mock()
            mock_client.remove_profiles_from_list.side_effect = KlaviyoAuthError("Invalid API key")
            mock_client_class.return_value = mock_client

            list_id = "list_123"
            profile_id = "01H5X123"

            response = client.delete(f"/api/klaviyo/lists/{list_id}/profiles/{profile_id}")

            assert response.status_code == 401
            data = response.json()

            assert "KlaviyoAuthError" in str(data["detail"])

    def test_remove_profile_from_list_generic_error(self, client):
        """Test error handling for generic exceptions"""
        with patch('api.routes.klaviyo.KlaviyoClient') as mock_client_class:
            mock_client = Mock()
            mock_client.remove_profiles_from_list.side_effect = Exception("Unexpected error")
            mock_client_class.return_value = mock_client

            list_id = "list_123"
            profile_id = "01H5X123"

            response = client.delete(f"/api/klaviyo/lists/{list_id}/profiles/{profile_id}")

            assert response.status_code == 500
            data = response.json()

            assert "ListOperationError" in str(data["detail"])


class TestKlaviyoAPIRequestValidation:
    """Test suite for Klaviyo API request validation"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    def test_invalid_json_body(self, client):
        """Test that invalid JSON returns proper error"""
        response = client.post(
            "/api/klaviyo/profiles",
            data="not valid json",
            headers={"Content-Type": "application/json"}
        )

        assert response.status_code == 422

    def test_empty_request_body_for_profile(self, client):
        """Test that empty request body returns validation error"""
        response = client.post("/api/klaviyo/profiles", json={})

        assert response.status_code == 422

    def test_response_content_type(self, client):
        """Test that responses have correct content type"""
        with patch('api.routes.klaviyo.KlaviyoClient') as mock_client_class:
            mock_client = Mock()
            mock_client.create_or_update_profile.return_value = {
                "id": "01HXYZ123",
                "type": "profile"
            }
            mock_client_class.return_value = mock_client

            request_data = {
                "email": "customer@example.com"
            }

            response = client.post("/api/klaviyo/profiles", json=request_data)

            assert "application/json" in response.headers["content-type"]

    def test_location_coordinates_validation(self, client):
        """Test that location coordinates are properly validated"""
        request_data = {
            "email": "customer@example.com",
            "location": {
                "latitude": 91.0,  # Invalid: exceeds max
                "longitude": 0.0
            }
        }

        response = client.post("/api/klaviyo/profiles", json=request_data)

        assert response.status_code == 422

    def test_metric_name_too_short(self, client):
        """Test validation error for empty metric name"""
        request_data = {
            "metric_name": "",
            "customer_email": "customer@example.com"
        }

        response = client.post("/api/klaviyo/events", json=request_data)

        assert response.status_code == 422
