#!/usr/bin/env python3
"""
Test script for TikTok Shop OAuth flow

This script helps validate the OAuth 2.0 authentication flow with a real TikTok Shop
seller account. It provides an interactive command-line interface to test each step
of the OAuth process.

Requirements:
    1. TikTok Shop seller account (approved)
    2. TikTok Shop API app (approved with required scopes)
    3. Credentials added to .env file

Usage:
    python test_oauth_flow.py
"""
import sys
import os
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from integrations.tiktok_shop.oauth import TikTokShopOAuth
from integrations.tiktok_shop.exceptions import (
    TikTokShopAuthError,
    TikTokShopNetworkError,
    TikTokShopAPIError
)
from config.config import TIKTOK_SHOP_APP_KEY, TIKTOK_SHOP_APP_SECRET


def print_header(title: str):
    """Print formatted section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def print_success(message: str):
    """Print success message"""
    print(f"✓ {message}")


def print_error(message: str):
    """Print error message"""
    print(f"✗ {message}")


def print_info(message: str):
    """Print info message"""
    print(f"ℹ {message}")


def validate_credentials() -> bool:
    """
    Validate that credentials are configured

    Returns:
        True if credentials are valid, False otherwise
    """
    print_header("Step 1: Validate Credentials")

    if not TIKTOK_SHOP_APP_KEY or TIKTOK_SHOP_APP_KEY == "your-app-key-here":
        print_error("TIKTOK_SHOP_APP_KEY is not configured")
        print_info("Please add your TikTok Shop App Key to .env file")
        return False

    if not TIKTOK_SHOP_APP_SECRET or TIKTOK_SHOP_APP_SECRET == "your-app-secret-here":
        print_error("TIKTOK_SHOP_APP_SECRET is not configured")
        print_info("Please add your TikTok Shop App Secret to .env file")
        return False

    print_success("App Key configured")
    print_success("App Secret configured")
    print(f"\nApp Key: {TIKTOK_SHOP_APP_KEY[:10]}...")
    return True


def test_oauth_initialization() -> Optional[TikTokShopOAuth]:
    """
    Test OAuth handler initialization

    Returns:
        TikTokShopOAuth instance if successful, None otherwise
    """
    print_header("Step 2: Initialize OAuth Handler")

    try:
        oauth = TikTokShopOAuth(
            app_key=TIKTOK_SHOP_APP_KEY,
            app_secret=TIKTOK_SHOP_APP_SECRET
        )
        print_success("OAuth handler initialized successfully")
        print(f"API Base URL: {oauth.api_base_url}")
        return oauth

    except TikTokShopAuthError as e:
        print_error(f"Authentication error: {e}")
        return None
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        return None


def test_authorization_url(oauth: TikTokShopOAuth):
    """
    Test authorization URL generation

    Args:
        oauth: TikTokShopOAuth instance
    """
    print_header("Step 3: Generate Authorization URL")

    # Use a test redirect URI
    redirect_uri = "https://localhost:8000/callback"
    state = "test_state_123"

    try:
        auth_url = oauth.generate_authorization_url(
            redirect_uri=redirect_uri,
            state=state
        )
        print_success("Authorization URL generated successfully")
        print(f"\nAuthorization URL:\n{auth_url}")
        print("\n" + "-" * 70)
        print("INSTRUCTIONS:")
        print("1. Copy the URL above")
        print("2. Open it in a web browser")
        print("3. Log in with your TikTok Shop seller account")
        print("4. Authorize the application")
        print("5. You will be redirected to the callback URL with an authorization code")
        print("6. Copy the 'code' parameter from the redirect URL")
        print("-" * 70)

    except Exception as e:
        print_error(f"Failed to generate authorization URL: {e}")


def test_token_exchange(oauth: TikTokShopOAuth):
    """
    Test authorization code to token exchange

    Args:
        oauth: TikTokShopOAuth instance
    """
    print_header("Step 4: Exchange Authorization Code for Token")

    print("Enter the authorization code from the redirect URL:")
    print("(Or press Enter to skip this step)")
    auth_code = input("> ").strip()

    if not auth_code:
        print_info("Skipping token exchange test")
        return

    try:
        print("\nExchanging authorization code for access token...")
        tokens = oauth.exchange_code_for_token(auth_code)

        print_success("Token exchange successful!")
        print("\nToken Information:")
        print(f"  Access Token: {tokens['access_token'][:20]}...")
        print(f"  Refresh Token: {tokens['refresh_token'][:20]}...")
        print(f"  Expires In: {tokens['expires_in']} seconds")
        print(f"  Refresh Expires In: {tokens['refresh_expires_in']} seconds")
        print(f"  Scope: {tokens.get('scope', 'N/A')}")

        # Save tokens to a file for future use
        print("\n" + "-" * 70)
        print("IMPORTANT: Save these tokens securely!")
        print("Add the following to your .env file:")
        print(f"\nTIKTOK_SHOP_ACCESS_TOKEN={tokens['access_token']}")
        print(f"TIKTOK_SHOP_REFRESH_TOKEN={tokens['refresh_token']}")
        print("-" * 70)

        # Ask if user wants to test token refresh
        print("\nDo you want to test token refresh? (y/n)")
        if input("> ").strip().lower() == 'y':
            test_token_refresh(oauth, tokens['refresh_token'])

    except TikTokShopAuthError as e:
        print_error(f"Authentication error: {e}")
        print_info("Make sure the authorization code is correct and hasn't expired")
    except TikTokShopNetworkError as e:
        print_error(f"Network error: {e}")
        print_info("Check your internet connection and try again")
    except Exception as e:
        print_error(f"Unexpected error: {e}")


def test_token_refresh(oauth: TikTokShopOAuth, refresh_token: str):
    """
    Test token refresh

    Args:
        oauth: TikTokShopOAuth instance
        refresh_token: Refresh token to use
    """
    print_header("Step 5: Test Token Refresh")

    try:
        print("Refreshing access token...")
        new_tokens = oauth.refresh_access_token(refresh_token)

        print_success("Token refresh successful!")
        print("\nNew Token Information:")
        print(f"  New Access Token: {new_tokens['access_token'][:20]}...")
        print(f"  New Refresh Token: {new_tokens['refresh_token'][:20]}...")
        print(f"  Expires In: {new_tokens['expires_in']} seconds")

        print("\n" + "-" * 70)
        print("Update your .env file with the new tokens:")
        print(f"\nTIKTOK_SHOP_ACCESS_TOKEN={new_tokens['access_token']}")
        print(f"TIKTOK_SHOP_REFRESH_TOKEN={new_tokens['refresh_token']}")
        print("-" * 70)

    except TikTokShopAuthError as e:
        print_error(f"Authentication error: {e}")
        print_info("The refresh token may be invalid or expired")
    except TikTokShopNetworkError as e:
        print_error(f"Network error: {e}")
    except Exception as e:
        print_error(f"Unexpected error: {e}")


def test_signature_generation(oauth: TikTokShopOAuth):
    """
    Test signature generation

    Args:
        oauth: TikTokShopOAuth instance
    """
    print_header("Step 6: Test Signature Generation")

    try:
        # Test signature generation with sample parameters
        path = "/api/products/search"
        params = {
            "shop_id": "12345",
            "page_size": 10
        }
        timestamp = 1234567890

        signature = oauth.generate_signature(path, params, timestamp)

        print_success("Signature generated successfully")
        print(f"\nTest Parameters:")
        print(f"  Path: {path}")
        print(f"  Params: {params}")
        print(f"  Timestamp: {timestamp}")
        print(f"\nGenerated Signature: {signature}")

    except Exception as e:
        print_error(f"Failed to generate signature: {e}")


def main():
    """Main test flow"""
    print("\n" + "=" * 70)
    print("  TikTok Shop OAuth Flow Test")
    print("=" * 70)
    print("\nThis script will guide you through testing the TikTok Shop OAuth flow.")
    print("Make sure you have:")
    print("  1. A TikTok Shop seller account (approved)")
    print("  2. A TikTok Shop API app (approved with required scopes)")
    print("  3. Your credentials added to the .env file")
    print("\nPress Enter to continue or Ctrl+C to exit...")
    input()

    # Step 1: Validate credentials
    if not validate_credentials():
        print("\n" + "=" * 70)
        print("  Test Failed: Invalid Credentials")
        print("=" * 70)
        print("\nPlease configure your credentials and try again.")
        sys.exit(1)

    # Step 2: Initialize OAuth handler
    oauth = test_oauth_initialization()
    if not oauth:
        print("\n" + "=" * 70)
        print("  Test Failed: OAuth Initialization")
        print("=" * 70)
        sys.exit(1)

    # Step 3: Generate authorization URL
    test_authorization_url(oauth)

    # Step 4: Exchange authorization code for token
    test_token_exchange(oauth)

    # Step 5: Test signature generation
    test_signature_generation(oauth)

    # Summary
    print_header("Test Summary")
    print("OAuth flow test completed!")
    print("\nNext steps:")
    print("  1. Document the results in VALIDATION.md")
    print("  2. Update .env with the access token")
    print("  3. Test API calls with the access token")
    print("\n" + "=" * 70)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(0)
    except Exception as e:
        print_error(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
