"""
Custom exceptions for Klaviyo API integration

This module defines a hierarchy of exceptions for handling various
error scenarios when interacting with the Klaviyo API.
"""


class KlaviyoAPIError(Exception):
    """
    Base exception for all Klaviyo API errors

    This is the parent class for all Klaviyo API-related exceptions.
    Use this for catching any Klaviyo API error generically.

    Attributes:
        message: Error message
        status_code: HTTP status code (if applicable)
        response: Raw response data (if applicable)
    """

    def __init__(self, message: str, status_code: int = None, response: dict = None):
        """
        Initialize KlaviyoAPIError

        Args:
            message: Human-readable error message
            status_code: HTTP status code from API response
            response: Full response data from the API
        """
        self.message = message
        self.status_code = status_code
        self.response = response
        super().__init__(self.message)

    def __str__(self):
        if self.status_code:
            return f"[{self.status_code}] {self.message}"
        return self.message


class KlaviyoAuthError(KlaviyoAPIError):
    """
    Exception raised for authentication and authorization errors

    This exception is raised when there are issues with:
    - Invalid or expired API keys
    - Missing or invalid API credentials
    - Insufficient permissions/scopes
    - OAuth flow failures
    """

    def __init__(self, message: str, status_code: int = 401, response: dict = None):
        """
        Initialize KlaviyoAuthError

        Args:
            message: Human-readable error message
            status_code: HTTP status code (default 401)
            response: Full response data from the API
        """
        super().__init__(message, status_code, response)


class KlaviyoRateLimitError(KlaviyoAPIError):
    """
    Exception raised when API rate limits are exceeded

    This exception is raised when:
    - Too many requests are made in a given time window
    - Rate limit quotas are exhausted

    Attributes:
        retry_after: Seconds to wait before retrying (if provided by API)
    """

    def __init__(self, message: str, status_code: int = 429, response: dict = None, retry_after: int = None):
        """
        Initialize KlaviyoRateLimitError

        Args:
            message: Human-readable error message
            status_code: HTTP status code (default 429)
            response: Full response data from the API
            retry_after: Seconds to wait before retrying
        """
        self.retry_after = retry_after
        super().__init__(message, status_code, response)

    def __str__(self):
        base_msg = super().__str__()
        if self.retry_after:
            return f"{base_msg} (retry after {self.retry_after}s)"
        return base_msg


class KlaviyoValidationError(KlaviyoAPIError):
    """
    Exception raised for request validation errors

    This exception is raised when:
    - Invalid parameters are provided
    - Required fields are missing
    - Data format is incorrect
    """

    def __init__(self, message: str, status_code: int = 400, response: dict = None):
        """
        Initialize KlaviyoValidationError

        Args:
            message: Human-readable error message
            status_code: HTTP status code (default 400)
            response: Full response data from the API
        """
        super().__init__(message, status_code, response)


class KlaviyoNotFoundError(KlaviyoAPIError):
    """
    Exception raised when a requested resource is not found

    This exception is raised when:
    - Profile, list, or other resource doesn't exist
    - Invalid resource ID is provided
    - Resource has been deleted
    """

    def __init__(self, message: str, status_code: int = 404, response: dict = None):
        """
        Initialize KlaviyoNotFoundError

        Args:
            message: Human-readable error message
            status_code: HTTP status code (default 404)
            response: Full response data from the API
        """
        super().__init__(message, status_code, response)


class KlaviyoServerError(KlaviyoAPIError):
    """
    Exception raised for Klaviyo server-side errors

    This exception is raised when:
    - Klaviyo API returns 5xx status codes
    - Internal server errors occur
    - Service is temporarily unavailable
    """

    def __init__(self, message: str, status_code: int = 500, response: dict = None):
        """
        Initialize KlaviyoServerError

        Args:
            message: Human-readable error message
            status_code: HTTP status code (default 500)
            response: Full response data from the API
        """
        super().__init__(message, status_code, response)


class KlaviyoNetworkError(KlaviyoAPIError):
    """
    Exception raised for network-related errors

    This exception is raised when:
    - Connection timeouts occur
    - Network is unreachable
    - DNS resolution fails
    """

    def __init__(self, message: str, original_exception: Exception = None):
        """
        Initialize KlaviyoNetworkError

        Args:
            message: Human-readable error message
            original_exception: The underlying network exception
        """
        self.original_exception = original_exception
        super().__init__(message)

    def __str__(self):
        if self.original_exception:
            return f"{self.message} (caused by: {str(self.original_exception)})"
        return self.message
