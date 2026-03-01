"""
Klaviyo API Client

This module provides the main API client for interacting with Klaviyo's email marketing API,
including profile management, event tracking, list management, and segmentation.
"""
import time
import requests
from typing import Dict, Optional, Any, List
from urllib.parse import urljoin

from integrations.klaviyo.auth import KlaviyoAuth
from integrations.klaviyo.models import (
    KlaviyoProfile,
    KlaviyoEvent,
    KlaviyoList,
    KlaviyoSegment,
    ListMembership
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
from integrations.tiktok_shop.rate_limiter import RateLimiter


class KlaviyoClient:
    """
    Main client for Klaviyo API integration

    This client provides methods for interacting with Klaviyo's email marketing APIs:
    - Profiles API: Customer profile management
    - Events API: Event tracking and metrics
    - Lists API: Email list management
    - Segments API: Dynamic segmentation

    Attributes:
        api_key: Klaviyo private API key
        api_base_url: Base URL for Klaviyo API
        auth: Authentication handler
        _rate_limiter: Rate limiter for controlling request rate
    """

    # Default request timeout in seconds
    DEFAULT_TIMEOUT = 30

    # API revision date (Klaviyo uses date-based API versioning)
    API_REVISION = "2024-10-15"

    # Rate limiting configuration
    # Klaviyo API allows different rates per endpoint, using conservative defaults
    DEFAULT_RATE_LIMIT = 10.0  # requests per second
    DEFAULT_BURST_CAPACITY = 20  # allow burst requests

    # Automatic backoff configuration for rate limit errors
    MAX_RETRY_ATTEMPTS = 3
    INITIAL_BACKOFF_SECONDS = 1.0
    MAX_BACKOFF_SECONDS = 32.0

    # Retry configuration for server and network errors
    MAX_SERVER_ERROR_RETRIES = 2
    MAX_NETWORK_ERROR_RETRIES = 2

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_base_url: Optional[str] = None
    ):
        """
        Initialize Klaviyo API client

        Args:
            api_key: Klaviyo private API key (optional, can use environment variable)
            api_base_url: Base URL for Klaviyo API (optional, defaults to production)

        Raises:
            KlaviyoAuthError: If required credentials are missing

        Example:
            >>> client = KlaviyoClient('pk_abc123...')
            >>> # Client is ready to make API requests

            >>> # Or use environment variables
            >>> client = KlaviyoClient()
        """
        # Initialize authentication handler
        self.auth = KlaviyoAuth(api_key=api_key, api_base_url=api_base_url)

        # Get credentials from auth handler
        credentials = self.auth.get_credentials()
        self.api_key = credentials["api_key"]
        self.api_base_url = credentials["api_base_url"].rstrip('/')

        # Initialize rate limiter with token bucket algorithm
        # This prevents hitting Klaviyo API rate limits
        self._rate_limiter = RateLimiter(
            requests_per_second=self.DEFAULT_RATE_LIMIT,
            bucket_capacity=self.DEFAULT_BURST_CAPACITY
        )

    def _get_headers(self) -> Dict[str, str]:
        """
        Get request headers with authentication

        Returns:
            Dictionary containing Authorization and other required headers
        """
        return self.auth.get_auth_headers()

    def _handle_error(
        self,
        error: Exception,
        retry_count: int
    ) -> tuple[bool, float]:
        """
        Determine if an error should be retried and calculate backoff time

        This method analyzes errors to determine if they are transient and
        should be retried. It implements different retry strategies for
        different error types:
        - Rate limit errors: Retry with API-provided wait time or exponential backoff
        - Server errors (5xx): Retry with exponential backoff
        - Network errors: Retry with exponential backoff
        - Other errors: Do not retry

        Args:
            error: The exception that was raised
            retry_count: Current retry attempt number

        Returns:
            Tuple of (should_retry, wait_seconds):
                - should_retry: Boolean indicating if the error should be retried
                - wait_seconds: Number of seconds to wait before retrying

        Example:
            >>> should_retry, wait_time = client._handle_error(error, 1)
            >>> if should_retry:
            ...     time.sleep(wait_time)
            ...     # retry request
        """
        # Handle rate limit errors
        if isinstance(error, KlaviyoRateLimitError):
            if retry_count > self.MAX_RETRY_ATTEMPTS:
                return False, 0

            # Use retry_after from API if available
            if error.retry_after:
                return True, error.retry_after

            # Otherwise use exponential backoff
            backoff = self.INITIAL_BACKOFF_SECONDS * (2 ** retry_count)
            wait_time = min(backoff, self.MAX_BACKOFF_SECONDS)
            return True, wait_time

        # Handle server errors (5xx) - these are often transient
        if isinstance(error, KlaviyoServerError):
            if retry_count > self.MAX_SERVER_ERROR_RETRIES:
                return False, 0

            # Use exponential backoff for server errors
            backoff = self.INITIAL_BACKOFF_SECONDS * (2 ** retry_count)
            wait_time = min(backoff, self.MAX_BACKOFF_SECONDS)
            return True, wait_time

        # Handle network errors - these may be transient
        if isinstance(error, KlaviyoNetworkError):
            if retry_count > self.MAX_NETWORK_ERROR_RETRIES:
                return False, 0

            # Use exponential backoff for network errors
            backoff = self.INITIAL_BACKOFF_SECONDS * (2 ** retry_count)
            wait_time = min(backoff, self.MAX_BACKOFF_SECONDS)
            return True, wait_time

        # Don't retry other errors (auth, validation, not found, etc.)
        return False, 0

    def _parse_error_response(self, response: requests.Response) -> str:
        """
        Parse error message from API response

        Args:
            response: HTTP response object

        Returns:
            Human-readable error message
        """
        try:
            error_data = response.json()

            # Klaviyo API returns errors in this format:
            # {"errors": [{"detail": "...", "source": {...}}]}
            if "errors" in error_data and error_data["errors"]:
                error = error_data["errors"][0]
                detail = error.get("detail", "Unknown error")
                return detail

            return error_data.get("message", response.text)
        except Exception:
            return response.text or f"HTTP {response.status_code}"

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        retry_count: int = 0
    ) -> Dict[str, Any]:
        """
        Make HTTP request to Klaviyo API with error handling and retries

        This is the core request method that handles:
        - Rate limiting
        - Authentication
        - Error handling
        - Automatic retries for transient errors

        Args:
            method: HTTP method (GET, POST, PATCH, DELETE)
            endpoint: API endpoint path (e.g., '/profiles')
            params: URL query parameters
            data: Request body data
            retry_count: Current retry attempt (for internal use)

        Returns:
            Parsed JSON response

        Raises:
            KlaviyoAuthError: For authentication/authorization errors
            KlaviyoRateLimitError: For rate limit errors
            KlaviyoValidationError: For validation errors
            KlaviyoNotFoundError: For 404 errors
            KlaviyoServerError: For server errors
            KlaviyoNetworkError: For network errors
            KlaviyoAPIError: For other API errors
        """
        # Apply rate limiting
        self._rate_limiter.acquire()

        # Build full URL
        url = urljoin(self.api_base_url, endpoint)

        # Get headers
        headers = self._get_headers()

        try:
            # Make request
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=data,
                timeout=self.DEFAULT_TIMEOUT
            )

            # Handle different status codes
            if response.status_code == 401 or response.status_code == 403:
                error_msg = self._parse_error_response(response)
                raise KlaviyoAuthError(
                    f"Authentication failed: {error_msg}",
                    status_code=response.status_code,
                    response=response.json() if response.text else None
                )

            elif response.status_code == 429:
                error_msg = self._parse_error_response(response)
                retry_after = response.headers.get('Retry-After')
                retry_after_seconds = int(retry_after) if retry_after else None

                error = KlaviyoRateLimitError(
                    f"Rate limit exceeded: {error_msg}",
                    status_code=429,
                    response=response.json() if response.text else None,
                    retry_after=retry_after_seconds
                )

                # Try to retry rate limit errors
                should_retry, wait_time = self._handle_error(error, retry_count)
                if should_retry:
                    time.sleep(wait_time)
                    return self._make_request(method, endpoint, params, data, retry_count + 1)
                raise error

            elif response.status_code == 400 or response.status_code == 422:
                error_msg = self._parse_error_response(response)
                raise KlaviyoValidationError(
                    f"Validation error: {error_msg}",
                    status_code=response.status_code,
                    response=response.json() if response.text else None
                )

            elif response.status_code == 404:
                error_msg = self._parse_error_response(response)
                raise KlaviyoNotFoundError(
                    f"Resource not found: {error_msg}",
                    status_code=404,
                    response=response.json() if response.text else None
                )

            elif response.status_code >= 500:
                error_msg = self._parse_error_response(response)
                error = KlaviyoServerError(
                    f"Server error: {error_msg}",
                    status_code=response.status_code,
                    response=response.json() if response.text else None
                )

                # Try to retry server errors
                should_retry, wait_time = self._handle_error(error, retry_count)
                if should_retry:
                    time.sleep(wait_time)
                    return self._make_request(method, endpoint, params, data, retry_count + 1)
                raise error

            elif not response.ok:
                error_msg = self._parse_error_response(response)
                raise KlaviyoAPIError(
                    f"API error: {error_msg}",
                    status_code=response.status_code,
                    response=response.json() if response.text else None
                )

            # Parse successful response
            if response.text:
                return response.json()
            return {}

        except requests.exceptions.Timeout as e:
            error = KlaviyoNetworkError(f"Request timeout: {str(e)}", original_exception=e)
            should_retry, wait_time = self._handle_error(error, retry_count)
            if should_retry:
                time.sleep(wait_time)
                return self._make_request(method, endpoint, params, data, retry_count + 1)
            raise error

        except requests.exceptions.ConnectionError as e:
            error = KlaviyoNetworkError(f"Connection error: {str(e)}", original_exception=e)
            should_retry, wait_time = self._handle_error(error, retry_count)
            if should_retry:
                time.sleep(wait_time)
                return self._make_request(method, endpoint, params, data, retry_count + 1)
            raise error

        except requests.exceptions.RequestException as e:
            raise KlaviyoNetworkError(f"Network error: {str(e)}", original_exception=e)

    # ============================================================================
    # Profile API Methods
    # ============================================================================

    def create_profile(self, profile: KlaviyoProfile) -> KlaviyoProfile:
        """
        Create a new customer profile in Klaviyo

        Args:
            profile: KlaviyoProfile object with customer data

        Returns:
            Created KlaviyoProfile with ID assigned by API

        Raises:
            KlaviyoValidationError: If profile data is invalid
            KlaviyoAPIError: If API request fails

        Example:
            >>> profile = KlaviyoProfile(
            ...     email="customer@example.com",
            ...     first_name="John",
            ...     last_name="Doe"
            ... )
            >>> created = client.create_profile(profile)
            >>> print(created.profile_id)
        """
        endpoint = "/profiles"
        payload = profile.to_klaviyo_dict()

        response = self._make_request("POST", endpoint, data=payload)
        return KlaviyoProfile.from_klaviyo_response(response)

    def update_profile(self, profile: KlaviyoProfile) -> KlaviyoProfile:
        """
        Update an existing customer profile in Klaviyo

        Args:
            profile: KlaviyoProfile object with profile_id and updated data

        Returns:
            Updated KlaviyoProfile

        Raises:
            KlaviyoNotFoundError: If profile doesn't exist
            KlaviyoValidationError: If profile data is invalid
            KlaviyoAPIError: If API request fails

        Example:
            >>> profile.first_name = "Jane"
            >>> updated = client.update_profile(profile)
        """
        if not profile.profile_id:
            raise KlaviyoValidationError("Profile ID is required for updates")

        endpoint = f"/profiles/{profile.profile_id}"
        payload = profile.to_klaviyo_dict()

        response = self._make_request("PATCH", endpoint, data=payload)
        return KlaviyoProfile.from_klaviyo_response(response)

    def get_profile(self, profile_id: str) -> KlaviyoProfile:
        """
        Get a customer profile by ID

        Args:
            profile_id: Klaviyo profile ID

        Returns:
            KlaviyoProfile object

        Raises:
            KlaviyoNotFoundError: If profile doesn't exist
            KlaviyoAPIError: If API request fails

        Example:
            >>> profile = client.get_profile("01HXYZ123...")
            >>> print(profile.email)
        """
        endpoint = f"/profiles/{profile_id}"
        response = self._make_request("GET", endpoint)
        return KlaviyoProfile.from_klaviyo_response(response)

    def search_profiles(
        self,
        email: Optional[str] = None,
        phone_number: Optional[str] = None,
        external_id: Optional[str] = None
    ) -> List[KlaviyoProfile]:
        """
        Search for profiles by email, phone, or external ID

        Args:
            email: Email address to search for
            phone_number: Phone number to search for
            external_id: External ID to search for

        Returns:
            List of matching KlaviyoProfile objects

        Raises:
            KlaviyoValidationError: If no search criteria provided
            KlaviyoAPIError: If API request fails

        Example:
            >>> profiles = client.search_profiles(email="customer@example.com")
            >>> if profiles:
            ...     print(profiles[0].profile_id)
        """
        if not any([email, phone_number, external_id]):
            raise KlaviyoValidationError("At least one search criterion is required")

        # Build filter criteria
        filters = []
        if email:
            filters.append(f'equals(email,"{email}")')
        if phone_number:
            filters.append(f'equals(phone_number,"{phone_number}")')
        if external_id:
            filters.append(f'equals(external_id,"{external_id}")')

        filter_str = ",".join(filters) if len(filters) > 1 else filters[0]

        endpoint = "/profiles"
        params = {"filter": filter_str}

        response = self._make_request("GET", endpoint, params=params)

        # Parse multiple profiles from response
        profiles = []
        data_list = response.get("data", [])
        for profile_data in data_list:
            profiles.append(KlaviyoProfile.from_klaviyo_response({"data": profile_data}))

        return profiles

    # ============================================================================
    # Event API Methods
    # ============================================================================

    def track_event(self, event: KlaviyoEvent) -> Dict[str, Any]:
        """
        Track a customer event in Klaviyo

        Args:
            event: KlaviyoEvent object with event data

        Returns:
            API response data

        Raises:
            KlaviyoValidationError: If event data is invalid
            KlaviyoAPIError: If API request fails

        Example:
            >>> event = KlaviyoEvent(
            ...     event_name="Placed Order",
            ...     profile={"email": "customer@example.com"},
            ...     value=99.99,
            ...     properties={"order_id": "12345", "items": 3}
            ... )
            >>> client.track_event(event)
        """
        endpoint = "/events"
        payload = event.to_klaviyo_dict()

        return self._make_request("POST", endpoint, data=payload)

    def get_events(
        self,
        metric_id: Optional[str] = None,
        profile_id: Optional[str] = None,
        limit: int = 20
    ) -> List[KlaviyoEvent]:
        """
        Get events, optionally filtered by metric or profile

        Args:
            metric_id: Filter by metric ID
            profile_id: Filter by profile ID
            limit: Maximum number of events to return

        Returns:
            List of KlaviyoEvent objects

        Raises:
            KlaviyoAPIError: If API request fails

        Example:
            >>> events = client.get_events(profile_id="01HXYZ123...", limit=10)
            >>> for event in events:
            ...     print(event.event_name)
        """
        endpoint = "/events"
        params = {"page[size]": limit}

        # Add filters
        filters = []
        if metric_id:
            filters.append(f'equals(metric_id,"{metric_id}")')
        if profile_id:
            filters.append(f'equals(profile_id,"{profile_id}")')

        if filters:
            filter_str = ",".join(filters) if len(filters) > 1 else filters[0]
            params["filter"] = filter_str

        response = self._make_request("GET", endpoint, params=params)

        # Parse multiple events from response
        events = []
        data_list = response.get("data", [])
        for event_data in data_list:
            events.append(KlaviyoEvent.from_klaviyo_response({"data": event_data}))

        return events

    # ============================================================================
    # List API Methods
    # ============================================================================

    def create_list(self, list_obj: KlaviyoList) -> KlaviyoList:
        """
        Create a new email list in Klaviyo

        Args:
            list_obj: KlaviyoList object with list data

        Returns:
            Created KlaviyoList with ID assigned by API

        Raises:
            KlaviyoValidationError: If list data is invalid
            KlaviyoAPIError: If API request fails

        Example:
            >>> new_list = KlaviyoList(name="VIP Customers")
            >>> created = client.create_list(new_list)
            >>> print(created.list_id)
        """
        endpoint = "/lists"
        payload = list_obj.to_klaviyo_dict()

        response = self._make_request("POST", endpoint, data=payload)
        return KlaviyoList.from_klaviyo_response(response)

    def get_list(self, list_id: str) -> KlaviyoList:
        """
        Get an email list by ID

        Args:
            list_id: Klaviyo list ID

        Returns:
            KlaviyoList object

        Raises:
            KlaviyoNotFoundError: If list doesn't exist
            KlaviyoAPIError: If API request fails

        Example:
            >>> email_list = client.get_list("ABC123")
            >>> print(email_list.name)
        """
        endpoint = f"/lists/{list_id}"
        response = self._make_request("GET", endpoint)
        return KlaviyoList.from_klaviyo_response(response)

    def get_lists(self, limit: int = 20) -> List[KlaviyoList]:
        """
        Get all email lists

        Args:
            limit: Maximum number of lists to return

        Returns:
            List of KlaviyoList objects

        Raises:
            KlaviyoAPIError: If API request fails

        Example:
            >>> lists = client.get_lists()
            >>> for lst in lists:
            ...     print(f"{lst.name}: {lst.profile_count} members")
        """
        endpoint = "/lists"
        params = {"page[size]": limit}

        response = self._make_request("GET", endpoint, params=params)

        # Parse multiple lists from response
        lists = []
        data_list = response.get("data", [])
        for list_data in data_list:
            lists.append(KlaviyoList.from_klaviyo_response({"data": list_data}))

        return lists

    def add_profiles_to_list(self, list_id: str, profile_ids: List[str]) -> Dict[str, Any]:
        """
        Add profiles to an email list

        Args:
            list_id: Klaviyo list ID
            profile_ids: List of profile IDs to add

        Returns:
            API response data

        Raises:
            KlaviyoValidationError: If list_id or profile_ids are invalid
            KlaviyoAPIError: If API request fails

        Example:
            >>> client.add_profiles_to_list("ABC123", ["01HXYZ1...", "01HXYZ2..."])
        """
        if not list_id or not profile_ids:
            raise KlaviyoValidationError("list_id and profile_ids are required")

        endpoint = f"/lists/{list_id}/relationships/profiles"

        # Build payload with profile IDs
        payload = {
            "data": [
                {"type": "profile", "id": profile_id}
                for profile_id in profile_ids
            ]
        }

        return self._make_request("POST", endpoint, data=payload)

    def remove_profiles_from_list(self, list_id: str, profile_ids: List[str]) -> Dict[str, Any]:
        """
        Remove profiles from an email list

        Args:
            list_id: Klaviyo list ID
            profile_ids: List of profile IDs to remove

        Returns:
            API response data

        Raises:
            KlaviyoValidationError: If list_id or profile_ids are invalid
            KlaviyoAPIError: If API request fails

        Example:
            >>> client.remove_profiles_from_list("ABC123", ["01HXYZ1..."])
        """
        if not list_id or not profile_ids:
            raise KlaviyoValidationError("list_id and profile_ids are required")

        endpoint = f"/lists/{list_id}/relationships/profiles"

        # Build payload with profile IDs
        payload = {
            "data": [
                {"type": "profile", "id": profile_id}
                for profile_id in profile_ids
            ]
        }

        return self._make_request("DELETE", endpoint, data=payload)

    # ============================================================================
    # Segment API Methods
    # ============================================================================

    def get_segment(self, segment_id: str) -> KlaviyoSegment:
        """
        Get a segment by ID

        Args:
            segment_id: Klaviyo segment ID

        Returns:
            KlaviyoSegment object

        Raises:
            KlaviyoNotFoundError: If segment doesn't exist
            KlaviyoAPIError: If API request fails

        Example:
            >>> segment = client.get_segment("XYZ789")
            >>> print(segment.name)
        """
        endpoint = f"/segments/{segment_id}"
        response = self._make_request("GET", endpoint)
        return KlaviyoSegment.from_klaviyo_response(response)

    def get_segments(self, limit: int = 20) -> List[KlaviyoSegment]:
        """
        Get all segments

        Args:
            limit: Maximum number of segments to return

        Returns:
            List of KlaviyoSegment objects

        Raises:
            KlaviyoAPIError: If API request fails

        Example:
            >>> segments = client.get_segments()
            >>> for seg in segments:
            ...     print(f"{seg.name}: {seg.profile_count} profiles")
        """
        endpoint = "/segments"
        params = {"page[size]": limit}

        response = self._make_request("GET", endpoint, params=params)

        # Parse multiple segments from response
        segments = []
        data_list = response.get("data", [])
        for segment_data in data_list:
            segments.append(KlaviyoSegment.from_klaviyo_response({"data": segment_data}))

        return segments

    def get_segment_profiles(
        self,
        segment_id: str,
        limit: int = 100
    ) -> List[KlaviyoProfile]:
        """
        Get profiles in a segment

        Args:
            segment_id: Klaviyo segment ID
            limit: Maximum number of profiles to return

        Returns:
            List of KlaviyoProfile objects

        Raises:
            KlaviyoNotFoundError: If segment doesn't exist
            KlaviyoAPIError: If API request fails

        Example:
            >>> profiles = client.get_segment_profiles("XYZ789", limit=50)
            >>> for profile in profiles:
            ...     print(profile.email)
        """
        endpoint = f"/segments/{segment_id}/profiles"
        params = {"page[size]": limit}

        response = self._make_request("GET", endpoint, params=params)

        # Parse multiple profiles from response
        profiles = []
        data_list = response.get("data", [])
        for profile_data in data_list:
            profiles.append(KlaviyoProfile.from_klaviyo_response({"data": profile_data}))

        return profiles
