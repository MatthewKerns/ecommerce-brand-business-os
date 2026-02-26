"""
OAuth 2.0 flow implementation for TikTok Shop API

This module handles the complete OAuth 2.0 authentication flow for TikTok Shop,
including authorization URL generation, token exchange, and token refresh.
"""
import urllib.parse
from typing import Dict, Optional, List
import requests
import hashlib
import hmac
import time

from config.config import TIKTOK_SHOP_API_BASE_URL
from integrations.tiktok_shop.exceptions import (
    TikTokShopAuthError,
    TikTokShopNetworkError,
    TikTokShopAPIError
)


class TikTokShopOAuth:
    """
    OAuth 2.0 handler for TikTok Shop API authentication

    This class manages the complete OAuth flow including:
    - Generating authorization URLs for user consent
    - Exchanging authorization codes for access tokens
    - Refreshing expired access tokens

    Attributes:
        app_key: TikTok Shop application key
        app_secret: TikTok Shop application secret
        api_base_url: Base URL for TikTok Shop API
    """

    # OAuth endpoints
    AUTHORIZE_ENDPOINT = "/authorization/token"
    TOKEN_ENDPOINT = "/api/token/get"
    REFRESH_ENDPOINT = "/api/token/refresh"

    def __init__(
        self,
        app_key: str,
        app_secret: str,
        api_base_url: str = TIKTOK_SHOP_API_BASE_URL
    ):
        """
        Initialize TikTok Shop OAuth handler

        Args:
            app_key: TikTok Shop application key
            app_secret: TikTok Shop application secret
            api_base_url: Base URL for TikTok Shop API (default from config)

        Raises:
            TikTokShopAuthError: If credentials are missing or invalid
        """
        if not app_key or not app_secret:
            raise TikTokShopAuthError(
                "Missing required credentials: app_key and app_secret are required"
            )

        self.app_key = app_key
        self.app_secret = app_secret
        self.api_base_url = api_base_url.rstrip('/')

    def generate_authorization_url(
        self,
        redirect_uri: str,
        state: Optional[str] = None
    ) -> str:
        """
        Generate the authorization URL for TikTok Shop OAuth flow

        This URL should be used to redirect users to TikTok Shop for authorization.
        After authorization, users will be redirected back to the redirect_uri with
        an authorization code.

        Args:
            redirect_uri: URL to redirect back to after authorization
            state: Optional state parameter for CSRF protection

        Returns:
            Complete authorization URL for user redirect

        Example:
            >>> oauth = TikTokShopOAuth('key', 'secret')
            >>> url = oauth.generate_authorization_url('https://example.com/callback')
            >>> # Redirect user to this URL for authorization
        """
        params = {
            'app_key': self.app_key,
            'redirect_uri': redirect_uri
        }

        if state:
            params['state'] = state

        query_string = urllib.parse.urlencode(params)
        return f"{self.api_base_url}{self.AUTHORIZE_ENDPOINT}?{query_string}"

    def exchange_code_for_token(
        self,
        authorization_code: str
    ) -> Dict[str, any]:
        """
        Exchange authorization code for access token

        After user authorizes the app, TikTok Shop redirects back with an
        authorization code. This method exchanges that code for an access token
        and refresh token.

        Args:
            authorization_code: Authorization code from redirect callback

        Returns:
            Dictionary containing:
                - access_token: Access token for API requests
                - refresh_token: Token for refreshing access token
                - expires_in: Token lifetime in seconds
                - scope: Granted permissions

        Raises:
            TikTokShopAuthError: If token exchange fails
            TikTokShopNetworkError: If network request fails

        Example:
            >>> oauth = TikTokShopOAuth('key', 'secret')
            >>> tokens = oauth.exchange_code_for_token('auth_code_here')
            >>> access_token = tokens['access_token']
        """
        endpoint = f"{self.api_base_url}{self.TOKEN_ENDPOINT}"

        # Build request parameters
        params = {
            'app_key': self.app_key,
            'app_secret': self.app_secret,
            'auth_code': authorization_code,
            'grant_type': 'authorized_code'
        }

        try:
            response = requests.post(endpoint, json=params, timeout=30)
            response.raise_for_status()

            data = response.json()

            # Check for API-level errors
            if data.get('code') != 0:
                error_msg = data.get('message', 'Unknown error during token exchange')
                raise TikTokShopAuthError(
                    f"Token exchange failed: {error_msg}",
                    response=data
                )

            # Extract token data
            token_data = data.get('data', {})

            return {
                'access_token': token_data.get('access_token'),
                'refresh_token': token_data.get('refresh_token'),
                'expires_in': token_data.get('access_token_expire_in'),
                'refresh_expires_in': token_data.get('refresh_token_expire_in'),
                'scope': token_data.get('scope')
            }

        except requests.exceptions.RequestException as e:
            raise TikTokShopNetworkError(
                f"Network error during token exchange: {str(e)}",
                original_exception=e
            )
        except TikTokShopAuthError:
            raise
        except Exception as e:
            raise TikTokShopAPIError(f"Unexpected error during token exchange: {str(e)}")

    def refresh_access_token(
        self,
        refresh_token: str
    ) -> Dict[str, any]:
        """
        Refresh an expired access token using refresh token

        When an access token expires, use this method to obtain a new one
        without requiring user re-authorization.

        Args:
            refresh_token: Refresh token obtained during initial authorization

        Returns:
            Dictionary containing:
                - access_token: New access token for API requests
                - refresh_token: New refresh token (rotate refresh tokens)
                - expires_in: Token lifetime in seconds

        Raises:
            TikTokShopAuthError: If token refresh fails
            TikTokShopNetworkError: If network request fails

        Example:
            >>> oauth = TikTokShopOAuth('key', 'secret')
            >>> new_tokens = oauth.refresh_access_token('refresh_token_here')
            >>> new_access_token = new_tokens['access_token']
        """
        endpoint = f"{self.api_base_url}{self.REFRESH_ENDPOINT}"

        # Build request parameters
        params = {
            'app_key': self.app_key,
            'app_secret': self.app_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token'
        }

        try:
            response = requests.post(endpoint, json=params, timeout=30)
            response.raise_for_status()

            data = response.json()

            # Check for API-level errors
            if data.get('code') != 0:
                error_msg = data.get('message', 'Unknown error during token refresh')
                raise TikTokShopAuthError(
                    f"Token refresh failed: {error_msg}",
                    response=data
                )

            # Extract token data
            token_data = data.get('data', {})

            return {
                'access_token': token_data.get('access_token'),
                'refresh_token': token_data.get('refresh_token'),
                'expires_in': token_data.get('access_token_expire_in'),
                'refresh_expires_in': token_data.get('refresh_token_expire_in')
            }

        except requests.exceptions.RequestException as e:
            raise TikTokShopNetworkError(
                f"Network error during token refresh: {str(e)}",
                original_exception=e
            )
        except TikTokShopAuthError:
            raise
        except Exception as e:
            raise TikTokShopAPIError(f"Unexpected error during token refresh: {str(e)}")

    def generate_signature(
        self,
        path: str,
        params: Dict[str, any],
        timestamp: Optional[int] = None
    ) -> str:
        """
        Generate HMAC-SHA256 signature for API requests

        TikTok Shop API requires signed requests for authentication.
        This method generates the required signature.

        Args:
            path: API endpoint path (e.g., '/api/products/search')
            params: Request parameters dictionary
            timestamp: Unix timestamp (uses current time if not provided)

        Returns:
            HMAC-SHA256 signature string

        Example:
            >>> oauth = TikTokShopOAuth('key', 'secret')
            >>> sig = oauth.generate_signature('/api/products', {'shop_id': '123'})
        """
        if timestamp is None:
            timestamp = int(time.time())

        # Build the string to sign
        # Format: app_key{app_key}path{path}timestamp{timestamp}param_key1{param_value1}...
        sign_string = f"app_key{self.app_key}path{path}timestamp{timestamp}"

        # Add sorted parameters
        for key in sorted(params.keys()):
            sign_string += f"{key}{params[key]}"

        # Add app_secret at the end
        sign_string += self.app_secret

        # Generate HMAC-SHA256 signature
        signature = hmac.new(
            self.app_secret.encode('utf-8'),
            sign_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        return signature

    def validate_webhook_signature(
        self,
        signature: str,
        timestamp: str,
        body: str
    ) -> bool:
        """
        Validate webhook signature from TikTok Shop

        When TikTok Shop sends webhook events, they include a signature
        for verification. Use this method to validate the signature.

        Args:
            signature: Signature from webhook headers
            timestamp: Timestamp from webhook headers
            body: Raw webhook request body

        Returns:
            True if signature is valid, False otherwise

        Example:
            >>> oauth = TikTokShopOAuth('key', 'secret')
            >>> is_valid = oauth.validate_webhook_signature(sig, ts, body)
            >>> if is_valid:
            ...     # Process webhook
        """
        # Build the string to verify
        verify_string = f"{self.app_secret}{timestamp}{body}"

        # Generate expected signature
        expected_signature = hmac.new(
            self.app_secret.encode('utf-8'),
            verify_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        # Compare signatures (constant-time comparison to prevent timing attacks)
        return hmac.compare_digest(signature, expected_signature)
