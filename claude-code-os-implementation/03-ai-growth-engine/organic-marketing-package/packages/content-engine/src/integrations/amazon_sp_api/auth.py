"""
Amazon SP-API Authentication Module

Handles LWA (Login with Amazon) OAuth authentication for Amazon Selling Partner API access.
Manages access token generation and credential provisioning for SP-API requests.
"""
import requests
from typing import Dict, Optional
from datetime import datetime, timedelta
import threading

from config.config import (
    AMAZON_SELLER_ID,
    AMAZON_SP_API_CLIENT_ID,
    AMAZON_SP_API_CLIENT_SECRET,
    AMAZON_SP_API_REFRESH_TOKEN,
    AMAZON_SP_API_REGION,
    AMAZON_MARKETPLACE_ID
)


class SPAPIAuthError(Exception):
    """Exception raised for SP-API authentication errors"""
    pass


class SPAPIAuth:
    """
    Amazon SP-API Authentication Handler

    Manages LWA OAuth token refresh and credential provisioning for Amazon SP-API.
    Implements token caching to minimize authentication requests.
    """

    # LWA token endpoint
    LWA_TOKEN_URL = "https://api.amazon.com/auth/o2/token"

    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        refresh_token: Optional[str] = None,
        seller_id: Optional[str] = None,
        region: Optional[str] = None,
        marketplace_id: Optional[str] = None
    ):
        """
        Initialize SP-API authentication handler

        Args:
            client_id: LWA client ID (defaults to config)
            client_secret: LWA client secret (defaults to config)
            refresh_token: LWA refresh token (defaults to config)
            seller_id: Amazon seller/merchant ID (defaults to config)
            region: AWS region for SP-API (defaults to config)
            marketplace_id: Amazon marketplace ID (defaults to config)

        Raises:
            SPAPIAuthError: If required credentials are missing
        """
        self.client_id = client_id or AMAZON_SP_API_CLIENT_ID
        self.client_secret = client_secret or AMAZON_SP_API_CLIENT_SECRET
        self.refresh_token = refresh_token or AMAZON_SP_API_REFRESH_TOKEN
        self.seller_id = seller_id or AMAZON_SELLER_ID
        self.region = region or AMAZON_SP_API_REGION
        self.marketplace_id = marketplace_id or AMAZON_MARKETPLACE_ID

        # Validate required credentials
        self._validate_credentials()

        # Token caching
        self._access_token: Optional[str] = None
        self._token_expires_at: Optional[datetime] = None
        self._lock = threading.Lock()

    def _validate_credentials(self) -> None:
        """
        Validate that all required credentials are present

        Raises:
            SPAPIAuthError: If any required credential is missing
        """
        required_creds = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": self.refresh_token,
            "seller_id": self.seller_id
        }

        missing = [name for name, value in required_creds.items() if not value]

        if missing:
            raise SPAPIAuthError(
                f"Missing required credentials: {', '.join(missing)}. "
                f"Please set them in environment variables or .env file."
            )

    def _request_access_token(self) -> Dict[str, any]:
        """
        Request a new access token from LWA

        Returns:
            Token response containing access_token and expires_in

        Raises:
            SPAPIAuthError: If token request fails
        """
        payload = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }

        try:
            response = requests.post(
                self.LWA_TOKEN_URL,
                data=payload,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            response.raise_for_status()

            token_data = response.json()

            if "access_token" not in token_data:
                raise SPAPIAuthError("Token response missing access_token")

            return token_data

        except requests.RequestException as e:
            raise SPAPIAuthError(f"Failed to obtain access token: {str(e)}")

    def get_access_token(self, force_refresh: bool = False) -> str:
        """
        Get a valid access token, refreshing if necessary

        Args:
            force_refresh: Force token refresh even if cached token is valid

        Returns:
            Valid access token string

        Raises:
            SPAPIAuthError: If token acquisition fails
        """
        with self._lock:
            # Check if we have a valid cached token
            if not force_refresh and self._access_token and self._token_expires_at:
                # Add 60 second buffer to avoid using token at edge of expiration
                if datetime.now() < self._token_expires_at - timedelta(seconds=60):
                    return self._access_token

            # Request new token
            token_data = self._request_access_token()

            self._access_token = token_data["access_token"]
            expires_in = token_data.get("expires_in", 3600)
            self._token_expires_at = datetime.now() + timedelta(seconds=expires_in)

            return self._access_token

    def get_credentials(self) -> Dict[str, str]:
        """
        Get complete credential set for SP-API requests

        Returns:
            Dictionary containing all required credentials:
            - access_token: LWA access token
            - seller_id: Amazon seller/merchant ID
            - region: AWS region
            - marketplace_id: Amazon marketplace ID

        Raises:
            SPAPIAuthError: If credential acquisition fails
        """
        return {
            "access_token": self.get_access_token(),
            "seller_id": self.seller_id,
            "region": self.region,
            "marketplace_id": self.marketplace_id
        }

    def invalidate_token(self) -> None:
        """Invalidate cached access token to force refresh on next request"""
        with self._lock:
            self._access_token = None
            self._token_expires_at = None


# Module-level singleton instance for convenience
_default_auth: Optional[SPAPIAuth] = None
_auth_lock = threading.Lock()


def get_sp_api_credentials() -> Dict[str, str]:
    """
    Get SP-API credentials using default configuration

    Convenience function that uses a singleton auth instance.
    For custom configuration, instantiate SPAPIAuth directly.

    Returns:
        Dictionary containing access_token, seller_id, region, marketplace_id

    Raises:
        SPAPIAuthError: If authentication fails
    """
    global _default_auth

    with _auth_lock:
        if _default_auth is None:
            _default_auth = SPAPIAuth()

    return _default_auth.get_credentials()


def get_access_token(force_refresh: bool = False) -> str:
    """
    Get SP-API access token using default configuration

    Convenience function that uses a singleton auth instance.

    Args:
        force_refresh: Force token refresh even if cached token is valid

    Returns:
        Valid access token string

    Raises:
        SPAPIAuthError: If authentication fails
    """
    global _default_auth

    with _auth_lock:
        if _default_auth is None:
            _default_auth = SPAPIAuth()

    return _default_auth.get_access_token(force_refresh=force_refresh)
