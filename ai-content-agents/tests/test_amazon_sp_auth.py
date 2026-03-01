"""
Unit tests for Amazon SP-API Authentication Module

Tests cover:
- SPAPIAuth initialization and credential validation
- LWA OAuth token acquisition and refresh
- Token caching and expiration handling
- Thread-safe token management
- Module-level convenience functions
- Error handling and edge cases
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import threading
import time

# Mock the config module before importing auth
@pytest.fixture(autouse=True)
def mock_config(monkeypatch):
    """Mock Amazon SP-API configuration for all tests"""
    monkeypatch.setenv("AMAZON_SELLER_ID", "TEST_SELLER_123")
    monkeypatch.setenv("AMAZON_SP_API_CLIENT_ID", "amzn1.application-oa2-client.test123")
    monkeypatch.setenv("AMAZON_SP_API_CLIENT_SECRET", "test_client_secret_456")
    monkeypatch.setenv("AMAZON_SP_API_REFRESH_TOKEN", "Atzr|test_refresh_token_789")
    monkeypatch.setenv("AMAZON_SP_API_REGION", "us-east-1")
    monkeypatch.setenv("AMAZON_MARKETPLACE_ID", "ATVPDKIKX0DER")


@pytest.fixture
def mock_successful_token_response():
    """Mock successful LWA token response"""
    return {
        "access_token": "Atza|test_access_token_abc123",
        "token_type": "bearer",
        "expires_in": 3600,
        "refresh_token": "Atzr|test_refresh_token_789"
    }


@pytest.fixture
def mock_requests_post():
    """Mock requests.post for LWA token requests"""
    with patch('integrations.amazon_sp_api.auth.requests.post') as mock_post:
        yield mock_post


class TestSPAPIAuthInitialization:
    """Tests for SPAPIAuth initialization and validation"""

    def test_init_with_config_defaults(self, mock_config):
        """Test initialization using environment config defaults"""
        from integrations.amazon_sp_api.auth import SPAPIAuth

        auth = SPAPIAuth()

        assert auth.client_id == "amzn1.application-oa2-client.test123"
        assert auth.client_secret == "test_client_secret_456"
        assert auth.refresh_token == "Atzr|test_refresh_token_789"
        assert auth.seller_id == "TEST_SELLER_123"
        assert auth.region == "us-east-1"
        assert auth.marketplace_id == "ATVPDKIKX0DER"

    def test_init_with_custom_credentials(self):
        """Test initialization with custom credentials"""
        from integrations.amazon_sp_api.auth import SPAPIAuth

        auth = SPAPIAuth(
            client_id="custom_client_id",
            client_secret="custom_secret",
            refresh_token="custom_token",
            seller_id="CUSTOM_SELLER",
            region="eu-west-1",
            marketplace_id="A1F83G8C2ARO7P"
        )

        assert auth.client_id == "custom_client_id"
        assert auth.client_secret == "custom_secret"
        assert auth.refresh_token == "custom_token"
        assert auth.seller_id == "CUSTOM_SELLER"
        assert auth.region == "eu-west-1"
        assert auth.marketplace_id == "A1F83G8C2ARO7P"

    def test_init_missing_client_id(self, monkeypatch):
        """Test initialization fails with missing client_id"""
        from integrations.amazon_sp_api.auth import SPAPIAuth, SPAPIAuthError

        monkeypatch.setenv("AMAZON_SP_API_CLIENT_ID", "")

        with pytest.raises(SPAPIAuthError) as exc_info:
            SPAPIAuth()

        assert "Missing required credentials" in str(exc_info.value)
        assert "client_id" in str(exc_info.value)

    def test_init_missing_multiple_credentials(self, monkeypatch):
        """Test initialization fails with multiple missing credentials"""
        from integrations.amazon_sp_api.auth import SPAPIAuth, SPAPIAuthError

        monkeypatch.setenv("AMAZON_SP_API_CLIENT_ID", "")
        monkeypatch.setenv("AMAZON_SP_API_CLIENT_SECRET", "")
        monkeypatch.setenv("AMAZON_SELLER_ID", "")

        with pytest.raises(SPAPIAuthError) as exc_info:
            SPAPIAuth()

        error_msg = str(exc_info.value)
        assert "Missing required credentials" in error_msg
        assert "client_id" in error_msg
        assert "client_secret" in error_msg
        assert "seller_id" in error_msg

    def test_init_token_cache_empty(self, mock_config):
        """Test that token cache is initially empty"""
        from integrations.amazon_sp_api.auth import SPAPIAuth

        auth = SPAPIAuth()

        assert auth._access_token is None
        assert auth._token_expires_at is None

    def test_init_creates_lock(self, mock_config):
        """Test that initialization creates a threading lock"""
        from integrations.amazon_sp_api.auth import SPAPIAuth

        auth = SPAPIAuth()

        assert isinstance(auth._lock, type(threading.Lock()))


class TestTokenAcquisition:
    """Tests for access token acquisition and refresh"""

    def test_request_access_token_success(self, mock_config, mock_requests_post, mock_successful_token_response):
        """Test successful access token request"""
        from integrations.amazon_sp_api.auth import SPAPIAuth

        # Setup mock response
        mock_response = Mock()
        mock_response.json.return_value = mock_successful_token_response
        mock_response.raise_for_status = Mock()
        mock_requests_post.return_value = mock_response

        auth = SPAPIAuth()
        token_data = auth._request_access_token()

        assert token_data["access_token"] == "Atza|test_access_token_abc123"
        assert token_data["expires_in"] == 3600

        # Verify request was made with correct parameters
        mock_requests_post.assert_called_once()
        call_args = mock_requests_post.call_args

        assert call_args[0][0] == SPAPIAuth.LWA_TOKEN_URL
        assert call_args[1]["data"]["grant_type"] == "refresh_token"
        assert call_args[1]["data"]["client_id"] == "amzn1.application-oa2-client.test123"
        assert call_args[1]["data"]["refresh_token"] == "Atzr|test_refresh_token_789"

    def test_request_access_token_missing_access_token(self, mock_config, mock_requests_post):
        """Test token request fails when response missing access_token"""
        from integrations.amazon_sp_api.auth import SPAPIAuth, SPAPIAuthError

        # Setup mock response without access_token
        mock_response = Mock()
        mock_response.json.return_value = {"token_type": "bearer"}
        mock_response.raise_for_status = Mock()
        mock_requests_post.return_value = mock_response

        auth = SPAPIAuth()

        with pytest.raises(SPAPIAuthError) as exc_info:
            auth._request_access_token()

        assert "missing access_token" in str(exc_info.value)

    def test_request_access_token_network_error(self, mock_config, mock_requests_post):
        """Test token request handles network errors"""
        from integrations.amazon_sp_api.auth import SPAPIAuth, SPAPIAuthError
        import requests

        # Setup mock to raise network error
        mock_requests_post.side_effect = requests.RequestException("Connection timeout")

        auth = SPAPIAuth()

        with pytest.raises(SPAPIAuthError) as exc_info:
            auth._request_access_token()

        assert "Failed to obtain access token" in str(exc_info.value)

    def test_request_access_token_http_error(self, mock_config, mock_requests_post):
        """Test token request handles HTTP errors"""
        from integrations.amazon_sp_api.auth import SPAPIAuth, SPAPIAuthError
        import requests

        # Setup mock to raise HTTP error
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("401 Unauthorized")
        mock_requests_post.return_value = mock_response

        auth = SPAPIAuth()

        with pytest.raises(SPAPIAuthError) as exc_info:
            auth._request_access_token()

        assert "Failed to obtain access token" in str(exc_info.value)

    def test_get_access_token_first_call(self, mock_config, mock_requests_post, mock_successful_token_response):
        """Test get_access_token on first call requests new token"""
        from integrations.amazon_sp_api.auth import SPAPIAuth

        # Setup mock response
        mock_response = Mock()
        mock_response.json.return_value = mock_successful_token_response
        mock_response.raise_for_status = Mock()
        mock_requests_post.return_value = mock_response

        auth = SPAPIAuth()
        token = auth.get_access_token()

        assert token == "Atza|test_access_token_abc123"
        assert auth._access_token == "Atza|test_access_token_abc123"
        assert auth._token_expires_at is not None
        mock_requests_post.assert_called_once()

    def test_get_access_token_uses_cache(self, mock_config, mock_requests_post, mock_successful_token_response):
        """Test get_access_token uses cached token when valid"""
        from integrations.amazon_sp_api.auth import SPAPIAuth

        # Setup mock response
        mock_response = Mock()
        mock_response.json.return_value = mock_successful_token_response
        mock_response.raise_for_status = Mock()
        mock_requests_post.return_value = mock_response

        auth = SPAPIAuth()

        # First call - should request token
        token1 = auth.get_access_token()
        assert mock_requests_post.call_count == 1

        # Second call - should use cache
        token2 = auth.get_access_token()
        assert mock_requests_post.call_count == 1
        assert token1 == token2

    def test_get_access_token_refreshes_expired(self, mock_config, mock_requests_post, mock_successful_token_response):
        """Test get_access_token refreshes expired token"""
        from integrations.amazon_sp_api.auth import SPAPIAuth

        # Setup mock response
        mock_response = Mock()
        mock_response.json.return_value = mock_successful_token_response
        mock_response.raise_for_status = Mock()
        mock_requests_post.return_value = mock_response

        auth = SPAPIAuth()

        # Get token
        token1 = auth.get_access_token()

        # Manually expire the token
        auth._token_expires_at = datetime.now() - timedelta(seconds=10)

        # Get token again - should refresh
        token2 = auth.get_access_token()

        assert mock_requests_post.call_count == 2
        assert token1 == token2

    def test_get_access_token_force_refresh(self, mock_config, mock_requests_post, mock_successful_token_response):
        """Test get_access_token with force_refresh parameter"""
        from integrations.amazon_sp_api.auth import SPAPIAuth

        # Setup mock response
        mock_response = Mock()
        mock_response.json.return_value = mock_successful_token_response
        mock_response.raise_for_status = Mock()
        mock_requests_post.return_value = mock_response

        auth = SPAPIAuth()

        # Get token
        auth.get_access_token()
        assert mock_requests_post.call_count == 1

        # Force refresh
        auth.get_access_token(force_refresh=True)
        assert mock_requests_post.call_count == 2

    def test_get_access_token_expiration_buffer(self, mock_config, mock_requests_post, mock_successful_token_response):
        """Test that token is refreshed 60 seconds before expiration"""
        from integrations.amazon_sp_api.auth import SPAPIAuth

        # Setup mock response
        mock_response = Mock()
        mock_response.json.return_value = mock_successful_token_response
        mock_response.raise_for_status = Mock()
        mock_requests_post.return_value = mock_response

        auth = SPAPIAuth()

        # Get token
        auth.get_access_token()

        # Set expiration to 59 seconds in future (within buffer)
        auth._token_expires_at = datetime.now() + timedelta(seconds=59)

        # Should refresh due to buffer
        auth.get_access_token()
        assert mock_requests_post.call_count == 2


class TestCredentials:
    """Tests for get_credentials method"""

    def test_get_credentials_success(self, mock_config, mock_requests_post, mock_successful_token_response):
        """Test get_credentials returns complete credential set"""
        from integrations.amazon_sp_api.auth import SPAPIAuth

        # Setup mock response
        mock_response = Mock()
        mock_response.json.return_value = mock_successful_token_response
        mock_response.raise_for_status = Mock()
        mock_requests_post.return_value = mock_response

        auth = SPAPIAuth()
        credentials = auth.get_credentials()

        assert "access_token" in credentials
        assert "seller_id" in credentials
        assert "region" in credentials
        assert "marketplace_id" in credentials

        assert credentials["access_token"] == "Atza|test_access_token_abc123"
        assert credentials["seller_id"] == "TEST_SELLER_123"
        assert credentials["region"] == "us-east-1"
        assert credentials["marketplace_id"] == "ATVPDKIKX0DER"

    def test_get_credentials_custom_values(self, mock_requests_post, mock_successful_token_response):
        """Test get_credentials with custom configuration"""
        from integrations.amazon_sp_api.auth import SPAPIAuth

        # Setup mock response
        mock_response = Mock()
        mock_response.json.return_value = mock_successful_token_response
        mock_response.raise_for_status = Mock()
        mock_requests_post.return_value = mock_response

        auth = SPAPIAuth(
            client_id="custom_id",
            client_secret="custom_secret",
            refresh_token="custom_token",
            seller_id="CUSTOM_SELLER",
            region="eu-west-1",
            marketplace_id="A1F83G8C2ARO7P"
        )

        credentials = auth.get_credentials()

        assert credentials["seller_id"] == "CUSTOM_SELLER"
        assert credentials["region"] == "eu-west-1"
        assert credentials["marketplace_id"] == "A1F83G8C2ARO7P"


class TestTokenInvalidation:
    """Tests for token invalidation"""

    def test_invalidate_token(self, mock_config):
        """Test invalidate_token clears cached token"""
        from integrations.amazon_sp_api.auth import SPAPIAuth

        auth = SPAPIAuth()

        # Set some cached values
        auth._access_token = "test_token"
        auth._token_expires_at = datetime.now() + timedelta(hours=1)

        # Invalidate
        auth.invalidate_token()

        assert auth._access_token is None
        assert auth._token_expires_at is None

    def test_invalidate_token_forces_refresh(self, mock_config, mock_requests_post, mock_successful_token_response):
        """Test that invalidate_token forces refresh on next get_access_token call"""
        from integrations.amazon_sp_api.auth import SPAPIAuth

        # Setup mock response
        mock_response = Mock()
        mock_response.json.return_value = mock_successful_token_response
        mock_response.raise_for_status = Mock()
        mock_requests_post.return_value = mock_response

        auth = SPAPIAuth()

        # Get token (first request)
        auth.get_access_token()
        assert mock_requests_post.call_count == 1

        # Invalidate
        auth.invalidate_token()

        # Get token again (should make second request)
        auth.get_access_token()
        assert mock_requests_post.call_count == 2


class TestThreadSafety:
    """Tests for thread-safe token management"""

    def test_concurrent_token_requests(self, mock_config, mock_requests_post, mock_successful_token_response):
        """Test that concurrent requests only fetch token once"""
        from integrations.amazon_sp_api.auth import SPAPIAuth

        # Setup mock response with delay to simulate network call
        mock_response = Mock()
        mock_response.json.return_value = mock_successful_token_response
        mock_response.raise_for_status = Mock()

        def delayed_post(*args, **kwargs):
            time.sleep(0.1)
            return mock_response

        mock_requests_post.side_effect = delayed_post

        auth = SPAPIAuth()
        tokens = []

        def get_token():
            token = auth.get_access_token()
            tokens.append(token)

        # Start multiple threads
        threads = [threading.Thread(target=get_token) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # All tokens should be the same
        assert len(tokens) == 5
        assert all(t == tokens[0] for t in tokens)

        # Should have made only one request (due to lock)
        assert mock_requests_post.call_count == 1


class TestModuleLevelFunctions:
    """Tests for module-level convenience functions"""

    def test_get_sp_api_credentials(self, mock_config, mock_requests_post, mock_successful_token_response):
        """Test module-level get_sp_api_credentials function"""
        from integrations.amazon_sp_api.auth import get_sp_api_credentials

        # Setup mock response
        mock_response = Mock()
        mock_response.json.return_value = mock_successful_token_response
        mock_response.raise_for_status = Mock()
        mock_requests_post.return_value = mock_response

        credentials = get_sp_api_credentials()

        assert "access_token" in credentials
        assert "seller_id" in credentials
        assert credentials["access_token"] == "Atza|test_access_token_abc123"

    def test_get_access_token_module_function(self, mock_config, mock_requests_post, mock_successful_token_response):
        """Test module-level get_access_token function"""
        from integrations.amazon_sp_api.auth import get_access_token

        # Setup mock response
        mock_response = Mock()
        mock_response.json.return_value = mock_successful_token_response
        mock_response.raise_for_status = Mock()
        mock_requests_post.return_value = mock_response

        token = get_access_token()

        assert token == "Atza|test_access_token_abc123"

    def test_get_access_token_module_function_force_refresh(self, mock_config, mock_requests_post, mock_successful_token_response):
        """Test module-level get_access_token with force_refresh"""
        from integrations.amazon_sp_api.auth import get_access_token

        # Setup mock response
        mock_response = Mock()
        mock_response.json.return_value = mock_successful_token_response
        mock_response.raise_for_status = Mock()
        mock_requests_post.return_value = mock_response

        # First call
        get_access_token()
        assert mock_requests_post.call_count == 1

        # Force refresh
        get_access_token(force_refresh=True)
        assert mock_requests_post.call_count == 2

    def test_module_functions_use_singleton(self, mock_config, mock_requests_post, mock_successful_token_response):
        """Test that module-level functions use singleton instance"""
        from integrations.amazon_sp_api.auth import get_sp_api_credentials, get_access_token

        # Setup mock response
        mock_response = Mock()
        mock_response.json.return_value = mock_successful_token_response
        mock_response.raise_for_status = Mock()
        mock_requests_post.return_value = mock_response

        # Call both functions
        get_access_token()
        credentials = get_sp_api_credentials()

        # Should have made only one token request (shared singleton)
        assert mock_requests_post.call_count == 1
        assert credentials["access_token"] == "Atza|test_access_token_abc123"


class TestErrorHandling:
    """Tests for error handling edge cases"""

    def test_error_messages_helpful(self, monkeypatch):
        """Test that error messages provide helpful guidance"""
        from integrations.amazon_sp_api.auth import SPAPIAuth, SPAPIAuthError

        monkeypatch.setenv("AMAZON_SP_API_CLIENT_ID", "")

        with pytest.raises(SPAPIAuthError) as exc_info:
            SPAPIAuth()

        error_msg = str(exc_info.value)
        assert "environment variables" in error_msg or ".env file" in error_msg

    def test_spapi_auth_error_is_exception(self):
        """Test that SPAPIAuthError is a proper Exception"""
        from integrations.amazon_sp_api.auth import SPAPIAuthError

        assert issubclass(SPAPIAuthError, Exception)

        error = SPAPIAuthError("Test error")
        assert str(error) == "Test error"


def test_auth_module_imports():
    """Test that all key components can be imported"""
    from integrations.amazon_sp_api.auth import (
        SPAPIAuth,
        SPAPIAuthError,
        get_sp_api_credentials,
        get_access_token
    )

    assert SPAPIAuth is not None
    assert SPAPIAuthError is not None
    assert get_sp_api_credentials is not None
    assert get_access_token is not None
