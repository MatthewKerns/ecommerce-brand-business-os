"""
Klaviyo Authentication Module

Handles API key authentication for Klaviyo API access.
Manages credential validation and header construction for Klaviyo API requests.
"""
from typing import Dict, Optional
import threading
import os

from .exceptions import KlaviyoAuthError


class KlaviyoAuth:
    """
    Klaviyo Authentication Handler

    Manages API key authentication for Klaviyo API.
    Klaviyo uses a simple private API key model passed via Authorization header.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_base_url: Optional[str] = None
    ):
        """
        Initialize Klaviyo authentication handler

        Args:
            api_key: Klaviyo private API key (defaults to environment variable)
            api_base_url: Klaviyo API base URL (defaults to environment variable)

        Raises:
            KlaviyoAuthError: If required credentials are missing
        """
        self.api_key = api_key or os.getenv("KLAVIYO_API_KEY", "")
        self.api_base_url = api_base_url or os.getenv("KLAVIYO_API_BASE_URL", "https://a.klaviyo.com/api")

        # Validate required credentials
        self._validate_credentials()

        # Thread safety for potential multi-threaded use
        self._lock = threading.Lock()

    def _validate_credentials(self) -> None:
        """
        Validate that all required credentials are present

        Raises:
            KlaviyoAuthError: If API key is missing
        """
        if not self.api_key:
            raise KlaviyoAuthError(
                "Missing required KLAVIYO_API_KEY. "
                "Please set it in environment variables or .env file."
            )

    def get_api_key(self) -> str:
        """
        Get the Klaviyo API key

        Returns:
            The API key string

        Raises:
            KlaviyoAuthError: If API key is not available
        """
        with self._lock:
            if not self.api_key:
                raise KlaviyoAuthError("API key not available")
            return self.api_key

    def get_auth_headers(self) -> Dict[str, str]:
        """
        Get authentication headers for Klaviyo API requests

        Returns:
            Dictionary containing Authorization and other required headers:
            - Authorization: Klaviyo private API key
            - revision: API revision date (2024-10-15 is latest stable)
            - Content-Type: application/json

        Raises:
            KlaviyoAuthError: If credential acquisition fails
        """
        return {
            "Authorization": f"Klaviyo-API-Key {self.get_api_key()}",
            "revision": "2024-10-15",
            "Content-Type": "application/json"
        }

    def get_credentials(self) -> Dict[str, str]:
        """
        Get complete credential set for Klaviyo API requests

        Returns:
            Dictionary containing all required credentials:
            - api_key: Klaviyo private API key
            - api_base_url: Klaviyo API base URL

        Raises:
            KlaviyoAuthError: If credential acquisition fails
        """
        return {
            "api_key": self.get_api_key(),
            "api_base_url": self.api_base_url
        }

    def invalidate_credentials(self) -> None:
        """
        Invalidate cached credentials

        Note: Unlike OAuth-based auth, Klaviyo uses static API keys,
        so this method is mainly for consistency with other auth modules.
        It can be used to force re-reading from environment variables.
        """
        with self._lock:
            self.api_key = os.getenv("KLAVIYO_API_KEY", "")
            self._validate_credentials()


# Module-level singleton instance for convenience
_default_auth: Optional[KlaviyoAuth] = None
_auth_lock = threading.Lock()


def get_klaviyo_credentials() -> Dict[str, str]:
    """
    Get Klaviyo credentials using default configuration

    Convenience function that uses a singleton auth instance.
    For custom configuration, instantiate KlaviyoAuth directly.

    Returns:
        Dictionary containing api_key and api_base_url

    Raises:
        KlaviyoAuthError: If credential acquisition fails

    Example:
        >>> creds = get_klaviyo_credentials()
        >>> api_key = creds["api_key"]
        >>> base_url = creds["api_base_url"]
    """
    global _default_auth

    with _auth_lock:
        if _default_auth is None:
            _default_auth = KlaviyoAuth()

        return _default_auth.get_credentials()


def get_klaviyo_auth_headers() -> Dict[str, str]:
    """
    Get Klaviyo authentication headers using default configuration

    Convenience function that uses a singleton auth instance.
    For custom configuration, instantiate KlaviyoAuth directly.

    Returns:
        Dictionary containing Authorization and other required headers

    Raises:
        KlaviyoAuthError: If credential acquisition fails

    Example:
        >>> import requests
        >>> headers = get_klaviyo_auth_headers()
        >>> response = requests.get("https://a.klaviyo.com/api/profiles", headers=headers)
    """
    global _default_auth

    with _auth_lock:
        if _default_auth is None:
            _default_auth = KlaviyoAuth()

        return _default_auth.get_auth_headers()


def invalidate_default_credentials() -> None:
    """
    Invalidate the default singleton credentials

    This forces the next call to get_klaviyo_credentials() or
    get_klaviyo_auth_headers() to re-read from environment variables.
    """
    global _default_auth

    with _auth_lock:
        if _default_auth is not None:
            _default_auth.invalidate_credentials()
