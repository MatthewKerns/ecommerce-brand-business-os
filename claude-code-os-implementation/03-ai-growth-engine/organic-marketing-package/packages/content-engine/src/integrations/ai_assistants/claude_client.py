"""
Claude API Client

This module provides a client for interacting with Anthropic's Claude API
for citation monitoring purposes.
"""
import time
import requests
from typing import Dict, Optional, Any, List
from urllib.parse import urljoin

from integrations.ai_assistants.exceptions import (
    AIAssistantAPIError,
    AIAssistantAuthError,
    AIAssistantRateLimitError,
    AIAssistantValidationError,
    AIAssistantServerError,
    AIAssistantNetworkError
)


class ClaudeClient:
    """
    Client for Anthropic Claude API integration

    This client provides methods for querying Claude to monitor
    brand citations and recommendations in AI-generated responses.

    Attributes:
        api_key: Anthropic API key
        api_base_url: Base URL for Anthropic API
        model: Claude model to use (default: claude-3-5-sonnet-20241022)
    """

    # Default request timeout in seconds
    DEFAULT_TIMEOUT = 60

    # Default model
    DEFAULT_MODEL = "claude-3-5-sonnet-20241022"

    # Anthropic API base URL
    DEFAULT_API_BASE_URL = "https://api.anthropic.com"

    # API version
    API_VERSION = "2023-06-01"

    # Rate limiting configuration
    # Anthropic API typically allows different rates based on tier
    # Using conservative defaults
    DEFAULT_RATE_LIMIT = 3.0  # requests per second
    DEFAULT_BURST_CAPACITY = 10  # allow burst requests

    # Automatic backoff configuration for rate limit errors
    MAX_RETRY_ATTEMPTS = 3
    INITIAL_BACKOFF_SECONDS = 1.0
    MAX_BACKOFF_SECONDS = 32.0

    # Retry configuration for server and network errors
    MAX_SERVER_ERROR_RETRIES = 2
    MAX_NETWORK_ERROR_RETRIES = 2

    def __init__(
        self,
        api_key: str,
        model: str = DEFAULT_MODEL,
        api_base_url: str = DEFAULT_API_BASE_URL
    ):
        """
        Initialize Claude API client

        Args:
            api_key: Anthropic API key
            model: Claude model to use (default: claude-3-5-sonnet-20241022)
            api_base_url: Base URL for Anthropic API

        Raises:
            AIAssistantAuthError: If API key is missing

        Example:
            >>> client = ClaudeClient(api_key='sk-ant-...')
            >>> # Client is ready to make API requests
        """
        if not api_key:
            raise AIAssistantAuthError(
                "Missing required credentials: api_key is required"
            )

        self.api_key = api_key
        self.model = model
        self.api_base_url = api_base_url.rstrip('/')

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
        if isinstance(error, AIAssistantRateLimitError):
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
        if isinstance(error, AIAssistantServerError):
            if retry_count > self.MAX_SERVER_ERROR_RETRIES:
                return False, 0

            # Use exponential backoff for server errors
            backoff = self.INITIAL_BACKOFF_SECONDS * (2 ** retry_count)
            wait_time = min(backoff, self.MAX_BACKOFF_SECONDS)
            return True, wait_time

        # Handle network errors - these might be transient
        if isinstance(error, AIAssistantNetworkError):
            if retry_count > self.MAX_NETWORK_ERROR_RETRIES:
                return False, 0

            # Use exponential backoff for network errors
            backoff = self.INITIAL_BACKOFF_SECONDS * (2 ** retry_count)
            wait_time = min(backoff, self.MAX_BACKOFF_SECONDS)
            return True, wait_time

        # Non-retryable errors (auth, validation, etc.)
        return False, 0

    def _make_request(
        self,
        method: str,
        path: str,
        data: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Make an authenticated request to Anthropic API

        This is the core request method that handles:
        - Adding authentication headers
        - Making the HTTP request
        - Parsing and validating the response
        - Error handling with automatic backoff for rate limits

        Args:
            method: HTTP method (GET, POST)
            path: API endpoint path (e.g., '/v1/messages')
            data: Body data for POST requests
            timeout: Request timeout in seconds (uses DEFAULT_TIMEOUT if not provided)

        Returns:
            Parsed JSON response from the API

        Raises:
            AIAssistantAuthError: For authentication errors
            AIAssistantRateLimitError: For rate limit errors (after retry attempts)
            AIAssistantValidationError: For validation errors
            AIAssistantServerError: For server errors
            AIAssistantNetworkError: For network errors
            AIAssistantAPIError: For other API errors

        Example:
            >>> response = client._make_request('POST', '/v1/messages',
            ...                                  data={'model': 'claude-3-5-sonnet-20241022', ...})
        """
        # Implement automatic retry logic for transient errors
        retry_count = 0

        while True:
            try:
                # Build the full URL
                url = urljoin(self.api_base_url, path)

                # Set headers
                headers = {
                    'x-api-key': self.api_key,
                    'anthropic-version': self.API_VERSION,
                    'Content-Type': 'application/json'
                }

                # Set timeout
                request_timeout = timeout or self.DEFAULT_TIMEOUT

                # Make the request
                response = requests.request(
                    method,
                    url,
                    headers=headers,
                    json=data,
                    timeout=request_timeout
                )

                # Handle HTTP errors
                response.raise_for_status()

                # Parse JSON response
                response_data = response.json()

                return response_data

            except (AIAssistantRateLimitError, AIAssistantServerError, AIAssistantNetworkError) as e:
                # These are potentially transient errors that may be retried
                # Determine if we should retry using the error handler
                should_retry, wait_time = self._handle_error(e, retry_count)

                if not should_retry:
                    # Max retries reached or non-retryable error
                    raise

                # Wait before retrying
                time.sleep(wait_time)
                retry_count += 1

            except requests.exceptions.Timeout as e:
                # Convert to AIAssistantNetworkError and check if retryable
                network_error = AIAssistantNetworkError(
                    f"Request timeout after {request_timeout}s",
                    original_exception=e
                )

                should_retry, wait_time = self._handle_error(network_error, retry_count)

                if not should_retry:
                    raise network_error

                time.sleep(wait_time)
                retry_count += 1

            except requests.exceptions.ConnectionError as e:
                # Convert to AIAssistantNetworkError and check if retryable
                network_error = AIAssistantNetworkError(
                    "Failed to connect to Anthropic API",
                    original_exception=e
                )

                should_retry, wait_time = self._handle_error(network_error, retry_count)

                if not should_retry:
                    raise network_error

                time.sleep(wait_time)
                retry_count += 1

            except requests.exceptions.HTTPError as e:
                # Convert to appropriate AIAssistant exception
                self._handle_http_error(e, response)

            except requests.exceptions.RequestException as e:
                # Convert to AIAssistantNetworkError and check if retryable
                network_error = AIAssistantNetworkError(
                    f"Network error during API request: {str(e)}",
                    original_exception=e
                )

                should_retry, wait_time = self._handle_error(network_error, retry_count)

                if not should_retry:
                    raise network_error

                time.sleep(wait_time)
                retry_count += 1

            except ValueError:
                # JSON parsing error - not retryable
                raise AIAssistantAPIError(
                    "Failed to parse JSON response from API"
                )

            except (AIAssistantAuthError, AIAssistantValidationError):
                # These errors are not retryable - immediately re-raise
                raise

            except Exception as e:
                # Unexpected error - not retryable
                raise AIAssistantAPIError(
                    f"Unexpected error during API request: {str(e)}"
                )

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
            Appropriate AIAssistant exception based on status code
        """
        status_code = response.status_code

        try:
            response_data = response.json()
            error_info = response_data.get('error', {})
            message = error_info.get('message', str(error))
        except:
            response_data = None
            message = str(error)

        if status_code == 401:
            raise AIAssistantAuthError(
                f"Authentication failed: {message}",
                status_code=status_code,
                response=response_data
            )
        elif status_code == 429:
            retry_after = response.headers.get('Retry-After')
            raise AIAssistantRateLimitError(
                f"Rate limit exceeded: {message}",
                status_code=status_code,
                response=response_data,
                retry_after=int(retry_after) if retry_after else None
            )
        elif status_code == 400:
            raise AIAssistantValidationError(
                f"Invalid request: {message}",
                status_code=status_code,
                response=response_data
            )
        elif status_code >= 500:
            raise AIAssistantServerError(
                f"Server error: {message}",
                status_code=status_code,
                response=response_data
            )
        else:
            raise AIAssistantAPIError(
                f"HTTP error {status_code}: {message}",
                status_code=status_code,
                response=response_data
            )

    # ========================================================================
    # MESSAGE METHODS
    # ========================================================================

    def query(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 1.0,
        max_tokens: int = 1024,
        system_prompt: Optional[str] = None,
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Query Claude with a prompt and return the response

        Args:
            prompt: The user query/prompt to send to Claude
            model: Model to use (defaults to instance model)
            temperature: Sampling temperature (0.0-1.0, default 1.0)
            max_tokens: Maximum tokens in response (default 1024)
            system_prompt: Optional system prompt to set context
            timeout: Request timeout in seconds (uses DEFAULT_TIMEOUT if not provided)

        Returns:
            Dictionary containing:
                - id: Response ID
                - type: Response type ('message')
                - role: Role ('assistant')
                - content: List of content blocks
                - model: Model used
                - stop_reason: Reason for stopping
                - usage: Token usage information

        Raises:
            AIAssistantAuthError: If authentication fails
            AIAssistantValidationError: If parameters are invalid
            AIAssistantAPIError: If API request fails

        Example:
            >>> client = ClaudeClient(api_key='sk-ant-...')
            >>> response = client.query("What are the best TCG storage solutions?")
            >>> answer = response['content'][0]['text']
        """
        if not prompt:
            raise AIAssistantValidationError(
                "prompt is required and cannot be empty",
                status_code=400
            )

        # Build request data
        data = {
            'model': model or self.model,
            'max_tokens': max_tokens,
            'messages': [
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            'temperature': temperature
        }

        if system_prompt:
            data['system'] = system_prompt

        return self._make_request(
            method='POST',
            path='/v1/messages',
            data=data,
            timeout=timeout
        )

    def get_response_text(self, response: Dict[str, Any]) -> str:
        """
        Extract the text content from a Claude API response

        Args:
            response: Response dictionary from query() method

        Returns:
            The text content of the first content block

        Raises:
            AIAssistantAPIError: If response format is invalid

        Example:
            >>> response = client.query("What are the best TCG storage solutions?")
            >>> text = client.get_response_text(response)
        """
        try:
            # Claude API returns content as a list of content blocks
            # Get the first text block
            content_blocks = response.get('content', [])
            if not content_blocks:
                raise AIAssistantAPIError("No content blocks in response")

            for block in content_blocks:
                if block.get('type') == 'text':
                    return block.get('text', '')

            raise AIAssistantAPIError("No text content block found in response")
        except (KeyError, IndexError) as e:
            raise AIAssistantAPIError(
                f"Invalid response format: {str(e)}"
            )

    def check_brand_mention(
        self,
        prompt: str,
        brand_name: str,
        model: Optional[str] = None,
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Query Claude and check if the response mentions a specific brand

        This is a convenience method for citation monitoring that:
        1. Sends the query to Claude
        2. Extracts the response text
        3. Checks if the brand is mentioned

        Args:
            prompt: The user query/prompt to send to Claude
            brand_name: Name of the brand to look for in the response
            model: Model to use (defaults to instance model)
            timeout: Request timeout in seconds (uses DEFAULT_TIMEOUT if not provided)

        Returns:
            Dictionary containing:
                - response: Full API response
                - response_text: Extracted response text
                - brand_mentioned: Boolean indicating if brand was mentioned
                - brand_name: The brand name that was searched for

        Raises:
            AIAssistantAuthError: If authentication fails
            AIAssistantValidationError: If parameters are invalid
            AIAssistantAPIError: If API request fails

        Example:
            >>> client = ClaudeClient(api_key='sk-ant-...')
            >>> result = client.check_brand_mention(
            ...     "What are the best TCG storage solutions?",
            ...     "Infinity Vault"
            ... )
            >>> if result['brand_mentioned']:
            ...     print("Brand was mentioned!")
        """
        # Query Claude
        response = self.query(prompt, model=model, timeout=timeout)

        # Extract response text
        response_text = self.get_response_text(response)

        # Check if brand is mentioned (case-insensitive)
        brand_mentioned = brand_name.lower() in response_text.lower()

        return {
            'response': response,
            'response_text': response_text,
            'brand_mentioned': brand_mentioned,
            'brand_name': brand_name
        }
