"""
TikTok Shop API Client

This module provides the main API client for interacting with TikTok Shop APIs,
including Shop API, Content API, and Data API endpoints.
"""
import time
import requests
from typing import Dict, Optional, Any
from urllib.parse import urljoin

from config.config import TIKTOK_SHOP_API_BASE_URL
from integrations.tiktok_shop.oauth import TikTokShopOAuth
from integrations.tiktok_shop.exceptions import (
    TikTokShopAPIError,
    TikTokShopAuthError,
    TikTokShopRateLimitError,
    TikTokShopValidationError,
    TikTokShopNotFoundError,
    TikTokShopServerError,
    TikTokShopNetworkError
)


class TikTokShopClient:
    """
    Main client for TikTok Shop API integration

    This client provides methods for interacting with TikTok Shop's various APIs:
    - Shop API: Products, orders, inventory management
    - Content API: Video and post management
    - Data API: Analytics and performance metrics

    Attributes:
        app_key: TikTok Shop application key
        app_secret: TikTok Shop application secret
        access_token: Access token for authenticated requests
        api_base_url: Base URL for TikTok Shop API
        oauth: OAuth handler for authentication
    """

    # Default request timeout in seconds
    DEFAULT_TIMEOUT = 30

    # API version
    API_VERSION = "202309"

    def __init__(
        self,
        app_key: str,
        app_secret: str,
        access_token: Optional[str] = None,
        api_base_url: str = TIKTOK_SHOP_API_BASE_URL
    ):
        """
        Initialize TikTok Shop API client

        Args:
            app_key: TikTok Shop application key
            app_secret: TikTok Shop application secret
            access_token: Access token for API requests (optional, can be set later)
            api_base_url: Base URL for TikTok Shop API

        Raises:
            TikTokShopAuthError: If required credentials are missing

        Example:
            >>> client = TikTokShopClient('app_key', 'app_secret', 'access_token')
            >>> # Client is ready to make API requests
        """
        if not app_key or not app_secret:
            raise TikTokShopAuthError(
                "Missing required credentials: app_key and app_secret are required"
            )

        self.app_key = app_key
        self.app_secret = app_secret
        self.access_token = access_token
        self.api_base_url = api_base_url.rstrip('/')

        # Initialize OAuth handler for authentication
        self.oauth = TikTokShopOAuth(app_key, app_secret, api_base_url)

    def set_access_token(self, access_token: str) -> None:
        """
        Set or update the access token

        Args:
            access_token: New access token to use for API requests

        Example:
            >>> client = TikTokShopClient('app_key', 'app_secret')
            >>> client.set_access_token('new_access_token')
        """
        self.access_token = access_token

    def _build_common_params(self) -> Dict[str, Any]:
        """
        Build common parameters required for all API requests

        Returns:
            Dictionary containing common parameters like app_key, timestamp, etc.
        """
        timestamp = int(time.time())

        return {
            'app_key': self.app_key,
            'timestamp': timestamp
        }

    def _generate_request_signature(
        self,
        path: str,
        params: Dict[str, Any]
    ) -> str:
        """
        Generate signature for API request

        Args:
            path: API endpoint path
            params: Request parameters

        Returns:
            Generated signature string
        """
        return self.oauth.generate_signature(path, params)

    def _make_request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        require_auth: bool = True,
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Make an authenticated request to TikTok Shop API

        This is the core request method that handles:
        - Adding common parameters
        - Generating signatures
        - Adding authentication headers
        - Making the HTTP request
        - Parsing and validating the response
        - Error handling

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            path: API endpoint path (e.g., '/api/products/search')
            params: Query parameters for GET requests
            data: Body data for POST/PUT requests
            require_auth: Whether this request requires authentication
            timeout: Request timeout in seconds (uses DEFAULT_TIMEOUT if not provided)

        Returns:
            Parsed JSON response from the API

        Raises:
            TikTokShopAuthError: For authentication errors
            TikTokShopRateLimitError: For rate limit errors
            TikTokShopValidationError: For validation errors
            TikTokShopNotFoundError: For 404 errors
            TikTokShopServerError: For server errors
            TikTokShopNetworkError: For network errors
            TikTokShopAPIError: For other API errors

        Example:
            >>> response = client._make_request('GET', '/api/products/search',
            ...                                  params={'page_size': 10})
        """
        if require_auth and not self.access_token:
            raise TikTokShopAuthError(
                "Access token is required for this request. "
                "Set it using set_access_token() or during initialization."
            )

        # Build the full URL
        url = urljoin(self.api_base_url, path)

        # Initialize parameters
        if params is None:
            params = {}

        # Add common parameters
        common_params = self._build_common_params()
        params.update(common_params)

        # Add access token if authentication is required
        if require_auth:
            params['access_token'] = self.access_token

        # Generate signature
        signature = self._generate_request_signature(path, params)
        params['sign'] = signature

        # Set timeout
        request_timeout = timeout or self.DEFAULT_TIMEOUT

        # Make the request
        try:
            if method.upper() in ['GET', 'DELETE']:
                response = requests.request(
                    method,
                    url,
                    params=params,
                    timeout=request_timeout
                )
            else:  # POST, PUT
                response = requests.request(
                    method,
                    url,
                    params=params,
                    json=data,
                    timeout=request_timeout
                )

            # Handle HTTP errors
            response.raise_for_status()

            # Parse JSON response
            response_data = response.json()

            # Check for API-level errors
            return self._handle_api_response(response_data)

        except requests.exceptions.Timeout as e:
            raise TikTokShopNetworkError(
                f"Request timeout after {request_timeout}s",
                original_exception=e
            )
        except requests.exceptions.ConnectionError as e:
            raise TikTokShopNetworkError(
                "Failed to connect to TikTok Shop API",
                original_exception=e
            )
        except requests.exceptions.HTTPError as e:
            self._handle_http_error(e, response)
        except requests.exceptions.RequestException as e:
            raise TikTokShopNetworkError(
                f"Network error during API request: {str(e)}",
                original_exception=e
            )
        except ValueError as e:
            raise TikTokShopAPIError(
                "Failed to parse JSON response from API"
            )
        except Exception as e:
            raise TikTokShopAPIError(
                f"Unexpected error during API request: {str(e)}"
            )

    def _handle_api_response(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle and validate API response

        Args:
            response_data: Parsed JSON response from API

        Returns:
            Response data if successful

        Raises:
            TikTokShopAPIError: If API returns an error code
        """
        # TikTok Shop API uses 'code' field to indicate success/failure
        # code = 0 means success
        code = response_data.get('code', -1)

        if code != 0:
            message = response_data.get('message', 'Unknown API error')

            # Map common error codes to specific exceptions
            if code in [401, 10002, 10003]:  # Auth-related errors
                raise TikTokShopAuthError(
                    f"Authentication error: {message}",
                    status_code=code,
                    response=response_data
                )
            elif code == 429 or code == 10001:  # Rate limit
                retry_after = response_data.get('retry_after')
                raise TikTokShopRateLimitError(
                    f"Rate limit exceeded: {message}",
                    status_code=code,
                    response=response_data,
                    retry_after=retry_after
                )
            elif code in [400, 40000, 40001]:  # Validation errors
                raise TikTokShopValidationError(
                    f"Validation error: {message}",
                    status_code=code,
                    response=response_data
                )
            elif code == 404 or code == 40004:  # Not found
                raise TikTokShopNotFoundError(
                    f"Resource not found: {message}",
                    status_code=code,
                    response=response_data
                )
            elif code >= 500:  # Server errors
                raise TikTokShopServerError(
                    f"Server error: {message}",
                    status_code=code,
                    response=response_data
                )
            else:  # Generic API error
                raise TikTokShopAPIError(
                    f"API error: {message}",
                    status_code=code,
                    response=response_data
                )

        return response_data

    def _handle_http_error(
        self,
        error: requests.exceptions.HTTPError,
        response: requests.Response
    ) -> None:
        """
        Handle HTTP errors from requests

        Args:
            error: The HTTP error exception
            response: The response object

        Raises:
            Appropriate TikTokShop exception based on status code
        """
        status_code = response.status_code

        try:
            response_data = response.json()
            message = response_data.get('message', str(error))
        except:
            response_data = None
            message = str(error)

        if status_code == 401:
            raise TikTokShopAuthError(
                f"Authentication failed: {message}",
                status_code=status_code,
                response=response_data
            )
        elif status_code == 429:
            retry_after = response.headers.get('Retry-After')
            raise TikTokShopRateLimitError(
                f"Rate limit exceeded: {message}",
                status_code=status_code,
                response=response_data,
                retry_after=int(retry_after) if retry_after else None
            )
        elif status_code == 400:
            raise TikTokShopValidationError(
                f"Invalid request: {message}",
                status_code=status_code,
                response=response_data
            )
        elif status_code == 404:
            raise TikTokShopNotFoundError(
                f"Resource not found: {message}",
                status_code=status_code,
                response=response_data
            )
        elif status_code >= 500:
            raise TikTokShopServerError(
                f"Server error: {message}",
                status_code=status_code,
                response=response_data
            )
        else:
            raise TikTokShopAPIError(
                f"HTTP error {status_code}: {message}",
                status_code=status_code,
                response=response_data
            )
