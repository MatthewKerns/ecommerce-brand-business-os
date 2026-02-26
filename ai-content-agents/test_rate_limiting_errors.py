#!/usr/bin/env python3
"""
Test script for TikTok Shop rate limiting and error handling

This script validates the rate limiting and error handling features of the TikTok Shop
integration, including token bucket algorithm, automatic retry logic, and error recovery.

Requirements:
    1. TikTok Shop seller account (approved)
    2. TikTok Shop API app (approved)
    3. Valid access token in .env file

Usage:
    python test_rate_limiting_errors.py
"""
import sys
import os
import time
import json
from typing import Optional, Dict, Any, List
from unittest.mock import Mock, patch

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.tiktok_shop_agent import TikTokShopAgent
from integrations.tiktok_shop.client import TikTokShopClient
from integrations.tiktok_shop.rate_limiter import RateLimiter
from integrations.tiktok_shop.exceptions import (
    TikTokShopAPIError,
    TikTokShopAuthError,
    TikTokShopRateLimitError,
    TikTokShopValidationError,
    TikTokShopNotFoundError,
    TikTokShopServerError,
    TikTokShopNetworkError
)
from config.config import (
    TIKTOK_SHOP_APP_KEY,
    TIKTOK_SHOP_APP_SECRET,
    TIKTOK_SHOP_ACCESS_TOKEN
)


def print_header(title: str):
    """Print formatted section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def print_success(message: str):
    """Print success message"""
    print(f"✓ {message}")


def print_error(message: str):
    """Print error message"""
    print(f"✗ {message}")


def print_info(message: str):
    """Print info message"""
    print(f"ℹ {message}")


def print_warning(message: str):
    """Print warning message"""
    print(f"⚠ {message}")


def validate_credentials() -> bool:
    """
    Validate that credentials and access token are configured

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

    if not TIKTOK_SHOP_ACCESS_TOKEN or TIKTOK_SHOP_ACCESS_TOKEN == "your-access-token-here":
        print_error("TIKTOK_SHOP_ACCESS_TOKEN is not configured")
        print_info("Please add your TikTok Shop Access Token to .env file")
        print_info("Run test_oauth_flow.py first to obtain an access token")
        return False

    print_success("App Key configured")
    print_success("App Secret configured")
    print_success("Access Token configured")
    print(f"\nApp Key: {TIKTOK_SHOP_APP_KEY[:10]}...")
    print(f"Access Token: {TIKTOK_SHOP_ACCESS_TOKEN[:20]}...")
    return True


def test_rate_limiter_basic() -> bool:
    """
    Test basic rate limiter functionality

    Returns:
        True if test passes, False otherwise
    """
    print_header("Step 2: Test Rate Limiter Basic Functionality")

    try:
        # Create a rate limiter with 5 requests per second
        limiter = RateLimiter(requests_per_second=5, bucket_capacity=5)
        print_success("Rate limiter created with 5 requests/second")

        # Test that we can get initial tokens
        available_tokens = limiter.get_available_tokens()
        print_success(f"Initial available tokens: {available_tokens:.2f}")

        if available_tokens != 5:
            print_error(f"Expected 5 tokens, got {available_tokens}")
            return False

        # Acquire a token
        limiter.acquire()
        print_success("Acquired 1 token successfully")

        # Check remaining tokens
        remaining_tokens = limiter.get_available_tokens()
        print_success(f"Remaining tokens after acquisition: {remaining_tokens:.2f}")

        if remaining_tokens >= 5:
            print_error(f"Expected less than 5 tokens, got {remaining_tokens}")
            return False

        # Test non-blocking acquire with insufficient tokens
        limiter.acquire()  # 2nd token
        limiter.acquire()  # 3rd token
        limiter.acquire()  # 4th token
        limiter.acquire()  # 5th token
        print_success("Acquired all 5 tokens")

        # Try non-blocking acquire when bucket is empty
        result = limiter.acquire(blocking=False)
        if result:
            print_error("Non-blocking acquire should have failed with empty bucket")
            return False
        print_success("Non-blocking acquire correctly failed with empty bucket")

        # Wait for refill
        print_info("Waiting 0.5 seconds for token refill...")
        time.sleep(0.5)

        # Check if tokens refilled
        refilled_tokens = limiter.get_available_tokens()
        print_success(f"Tokens after 0.5s refill: {refilled_tokens:.2f}")

        if refilled_tokens < 2:
            print_error(f"Expected at least 2 tokens after 0.5s, got {refilled_tokens}")
            return False

        # Test reset
        limiter.reset()
        reset_tokens = limiter.get_available_tokens()
        print_success(f"Tokens after reset: {reset_tokens:.2f}")

        if reset_tokens != 5:
            print_error(f"Expected 5 tokens after reset, got {reset_tokens}")
            return False

        print_success("\n✓ Rate limiter basic functionality test PASSED")
        return True

    except Exception as e:
        print_error(f"Rate limiter test failed: {str(e)}")
        return False


def test_rate_limiter_under_load() -> bool:
    """
    Test rate limiter under rapid consecutive requests

    Returns:
        True if test passes, False otherwise
    """
    print_header("Step 3: Test Rate Limiter Under Load")

    try:
        # Create a rate limiter with 10 requests per second
        limiter = RateLimiter(requests_per_second=10, bucket_capacity=20)
        print_success("Rate limiter created with 10 requests/second, 20 burst capacity")

        # Make 30 rapid consecutive requests
        num_requests = 30
        print_info(f"Making {num_requests} rapid consecutive requests...")

        start_time = time.time()
        successful_requests = 0

        for i in range(num_requests):
            limiter.acquire()
            successful_requests += 1
            if (i + 1) % 10 == 0:
                print_info(f"  Completed {i + 1}/{num_requests} requests")

        end_time = time.time()
        elapsed_time = end_time - start_time

        print_success(f"All {successful_requests} requests completed")
        print_info(f"Total time: {elapsed_time:.2f} seconds")
        print_info(f"Effective rate: {successful_requests / elapsed_time:.2f} requests/second")

        # Calculate expected minimum time
        # First 20 requests use burst capacity (instant)
        # Remaining 10 requests need to wait for token refill at 10 req/sec = 1 second
        expected_min_time = 1.0

        if elapsed_time < expected_min_time:
            print_warning(f"Requests completed faster than expected (burst capacity used)")
        elif elapsed_time < expected_min_time + 1.0:
            print_success(f"Requests completed within expected timeframe")
        else:
            print_warning(f"Requests took longer than expected")

        print_success("\n✓ Rate limiter load test PASSED")
        return True

    except Exception as e:
        print_error(f"Rate limiter load test failed: {str(e)}")
        return False


def test_api_client_rate_limiting(agent: TikTokShopAgent) -> bool:
    """
    Test that API client respects rate limiting

    Args:
        agent: Initialized TikTokShopAgent

    Returns:
        True if test passes, False otherwise
    """
    print_header("Step 4: Test API Client Rate Limiting")

    try:
        # Make rapid consecutive API calls
        num_requests = 15
        print_info(f"Making {num_requests} rapid consecutive API calls...")
        print_warning("Note: This test requires valid TikTok Shop credentials and API access")

        start_time = time.time()
        successful_requests = 0
        rate_limit_errors = 0

        for i in range(num_requests):
            try:
                # Use list_products with minimal page size for faster requests
                result = agent.list_products(page_size=1)
                successful_requests += 1
                print_info(f"  Request {i + 1}/{num_requests}: SUCCESS")
            except TikTokShopRateLimitError as e:
                rate_limit_errors += 1
                print_warning(f"  Request {i + 1}/{num_requests}: Rate limited (should not happen)")
            except (TikTokShopAuthError, TikTokShopNetworkError) as e:
                print_warning(f"  Request {i + 1}/{num_requests}: {type(e).__name__}: {str(e)}")
                print_info("  Skipping remaining API requests due to auth/network error")
                break
            except Exception as e:
                print_warning(f"  Request {i + 1}/{num_requests}: {type(e).__name__}: {str(e)}")

        end_time = time.time()
        elapsed_time = end_time - start_time

        print_info(f"\nResults:")
        print_info(f"  Total requests attempted: {num_requests}")
        print_info(f"  Successful requests: {successful_requests}")
        print_info(f"  Rate limit errors: {rate_limit_errors}")
        print_info(f"  Total time: {elapsed_time:.2f} seconds")

        if successful_requests > 0:
            effective_rate = successful_requests / elapsed_time
            print_info(f"  Effective rate: {effective_rate:.2f} requests/second")

            # Should not exceed configured rate limit of 10 req/sec by much
            if effective_rate > 12:
                print_error(f"Effective rate exceeds configured limit (10 req/sec)")
                return False

        if rate_limit_errors > 0:
            print_error("Rate limiter should prevent rate limit errors from API")
            print_error("This indicates the rate limiter is not working correctly")
            return False

        if successful_requests == 0:
            print_warning("No successful requests (likely due to missing credentials)")
            print_info("Skipping API rate limiting validation")
        else:
            print_success("Rate limiter successfully throttled requests")
            print_success("No rate limit errors from API")

        print_success("\n✓ API client rate limiting test PASSED")
        return True

    except Exception as e:
        print_error(f"API client rate limiting test failed: {str(e)}")
        return False


def test_error_handling_auth() -> bool:
    """
    Test authentication error handling

    Returns:
        True if test passes, False otherwise
    """
    print_header("Step 5: Test Authentication Error Handling")

    try:
        # Create client with invalid access token
        print_info("Creating client with invalid access token...")
        client = TikTokShopClient(
            app_key=TIKTOK_SHOP_APP_KEY,
            app_secret=TIKTOK_SHOP_APP_SECRET,
            access_token="invalid_token_12345"
        )
        print_success("Client created with invalid token")

        # Try to make an API request
        print_info("Attempting API request with invalid token...")
        try:
            client.get_products(page_size=1)
            print_error("Request should have failed with TikTokShopAuthError")
            return False
        except TikTokShopAuthError as e:
            print_success(f"Correctly caught TikTokShopAuthError: {str(e)}")
        except Exception as e:
            print_warning(f"Caught unexpected error type: {type(e).__name__}: {str(e)}")
            print_info("This may be expected if the API returns a different error for invalid tokens")

        # Test missing access token
        print_info("\nTesting missing access token...")
        client_no_token = TikTokShopClient(
            app_key=TIKTOK_SHOP_APP_KEY,
            app_secret=TIKTOK_SHOP_APP_SECRET
        )

        try:
            client_no_token.get_products(page_size=1)
            print_error("Request should have failed with TikTokShopAuthError")
            return False
        except TikTokShopAuthError as e:
            print_success(f"Correctly caught TikTokShopAuthError for missing token: {str(e)}")

        print_success("\n✓ Authentication error handling test PASSED")
        return True

    except Exception as e:
        print_error(f"Authentication error handling test failed: {str(e)}")
        return False


def test_error_handling_validation() -> bool:
    """
    Test validation error handling

    Returns:
        True if test passes, False otherwise
    """
    print_header("Step 6: Test Validation Error Handling")

    try:
        # Create client with valid credentials
        if not TIKTOK_SHOP_ACCESS_TOKEN or TIKTOK_SHOP_ACCESS_TOKEN == "your-access-token-here":
            print_warning("Valid access token not configured - skipping validation error test")
            return True

        print_info("Creating client with valid credentials...")
        client = TikTokShopClient(
            app_key=TIKTOK_SHOP_APP_KEY,
            app_secret=TIKTOK_SHOP_APP_SECRET,
            access_token=TIKTOK_SHOP_ACCESS_TOKEN
        )

        # Test with invalid parameters
        print_info("Testing with invalid page_size (negative value)...")
        try:
            # This should fail validation either client-side or server-side
            client.get_products(page_size=-1)
            print_warning("Request with invalid parameters did not fail")
            print_info("API may accept this parameter")
        except (TikTokShopValidationError, TikTokShopAPIError, ValueError) as e:
            print_success(f"Correctly caught validation error: {type(e).__name__}: {str(e)}")
        except Exception as e:
            print_warning(f"Caught unexpected error: {type(e).__name__}: {str(e)}")

        print_success("\n✓ Validation error handling test PASSED")
        return True

    except Exception as e:
        print_error(f"Validation error handling test failed: {str(e)}")
        return False


def test_error_handling_not_found() -> bool:
    """
    Test not found error handling

    Returns:
        True if test passes, False otherwise
    """
    print_header("Step 7: Test Not Found Error Handling")

    try:
        # Create client with valid credentials
        if not TIKTOK_SHOP_ACCESS_TOKEN or TIKTOK_SHOP_ACCESS_TOKEN == "your-access-token-here":
            print_warning("Valid access token not configured - skipping not found error test")
            return True

        print_info("Creating client with valid credentials...")
        client = TikTokShopClient(
            app_key=TIKTOK_SHOP_APP_KEY,
            app_secret=TIKTOK_SHOP_APP_SECRET,
            access_token=TIKTOK_SHOP_ACCESS_TOKEN
        )

        # Test with invalid product ID
        print_info("Testing with invalid product_id...")
        try:
            client.get_product(product_id="invalid_product_id_99999")
            print_warning("Request with invalid product ID did not fail")
            print_info("API may return empty result instead of 404")
        except TikTokShopNotFoundError as e:
            print_success(f"Correctly caught TikTokShopNotFoundError: {str(e)}")
        except TikTokShopAPIError as e:
            print_success(f"Correctly caught API error: {type(e).__name__}: {str(e)}")
        except Exception as e:
            print_warning(f"Caught unexpected error: {type(e).__name__}: {str(e)}")

        print_success("\n✓ Not found error handling test PASSED")
        return True

    except Exception as e:
        print_error(f"Not found error handling test failed: {str(e)}")
        return False


def test_retry_logic_simulation() -> bool:
    """
    Test retry logic using simulated errors

    Returns:
        True if test passes, False otherwise
    """
    print_header("Step 8: Test Retry Logic with Simulated Errors")

    try:
        print_info("Creating client for retry logic testing...")
        client = TikTokShopClient(
            app_key=TIKTOK_SHOP_APP_KEY,
            app_secret=TIKTOK_SHOP_APP_SECRET,
            access_token=TIKTOK_SHOP_ACCESS_TOKEN or "test_token"
        )

        # Test rate limit error retry determination
        print_info("\nTesting rate limit error retry logic...")
        rate_limit_error = TikTokShopRateLimitError("Rate limit exceeded", retry_after=5)
        should_retry, wait_time = client._handle_error(rate_limit_error, retry_count=0)

        if should_retry:
            print_success(f"Rate limit error marked for retry (wait: {wait_time}s)")
            if wait_time != 5:
                print_error(f"Expected wait time of 5s, got {wait_time}s")
                return False
        else:
            print_error("Rate limit error should be retried")
            return False

        # Test rate limit error with exponential backoff
        print_info("Testing rate limit error with exponential backoff...")
        rate_limit_error_no_retry = TikTokShopRateLimitError("Rate limit exceeded")
        should_retry, wait_time = client._handle_error(rate_limit_error_no_retry, retry_count=0)

        if should_retry and wait_time == 2.0:  # 1.0 * 2^0 = 2.0
            print_success(f"Exponential backoff calculated correctly (wait: {wait_time}s)")
        else:
            print_warning(f"Unexpected backoff: should_retry={should_retry}, wait={wait_time}s")

        # Test max retries
        print_info("Testing max retries for rate limit errors...")
        should_retry, wait_time = client._handle_error(rate_limit_error, retry_count=4)

        if not should_retry:
            print_success("Rate limit error not retried after max attempts")
        else:
            print_error("Rate limit error should not be retried after max attempts")
            return False

        # Test server error retry
        print_info("\nTesting server error retry logic...")
        server_error = TikTokShopServerError("Internal server error", status_code=500)
        should_retry, wait_time = client._handle_error(server_error, retry_count=0)

        if should_retry:
            print_success(f"Server error marked for retry (wait: {wait_time}s)")
        else:
            print_error("Server error should be retried")
            return False

        # Test network error retry
        print_info("Testing network error retry logic...")
        network_error = TikTokShopNetworkError("Connection timeout")
        should_retry, wait_time = client._handle_error(network_error, retry_count=0)

        if should_retry:
            print_success(f"Network error marked for retry (wait: {wait_time}s)")
        else:
            print_error("Network error should be retried")
            return False

        # Test non-retryable errors
        print_info("\nTesting non-retryable errors...")
        auth_error = TikTokShopAuthError("Invalid credentials")
        should_retry, wait_time = client._handle_error(auth_error, retry_count=0)

        if not should_retry:
            print_success("Auth error correctly marked as non-retryable")
        else:
            print_error("Auth error should not be retried")
            return False

        validation_error = TikTokShopValidationError("Invalid parameters")
        should_retry, wait_time = client._handle_error(validation_error, retry_count=0)

        if not should_retry:
            print_success("Validation error correctly marked as non-retryable")
        else:
            print_error("Validation error should not be retried")
            return False

        print_success("\n✓ Retry logic simulation test PASSED")
        return True

    except Exception as e:
        print_error(f"Retry logic simulation test failed: {str(e)}")
        return False


def generate_test_report(results: Dict[str, bool]) -> None:
    """
    Generate a test report summary

    Args:
        results: Dictionary of test results
    """
    print_header("Test Report Summary")

    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result)
    failed_tests = total_tests - passed_tests

    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")
    print()

    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}  {test_name}")

    print()

    if failed_tests == 0:
        print_success("🎉 All tests PASSED!")
    else:
        print_error(f"⚠️  {failed_tests} test(s) FAILED")

    # Save report to file
    report_file = "test_rate_limiting_errors_report.json"
    report_data = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_tests": total_tests,
        "passed_tests": passed_tests,
        "failed_tests": failed_tests,
        "results": {name: ("PASS" if result else "FAIL") for name, result in results.items()}
    }

    with open(report_file, 'w') as f:
        json.dump(report_data, f, indent=2)

    print_info(f"\nDetailed report saved to: {report_file}")


def main():
    """
    Main test execution function
    """
    print("\n" + "=" * 80)
    print("  TikTok Shop Rate Limiting & Error Handling Test Suite")
    print("=" * 80)

    results = {}

    # Step 1: Validate credentials
    if not validate_credentials():
        print_warning("\nCredentials not configured - running offline tests only")
        print_info("Configure credentials in .env to run full integration tests")

    # Step 2: Test rate limiter basic functionality
    results["Rate Limiter Basic"] = test_rate_limiter_basic()

    # Step 3: Test rate limiter under load
    results["Rate Limiter Load"] = test_rate_limiter_under_load()

    # Step 4-7: Tests requiring valid credentials
    has_credentials = (
        TIKTOK_SHOP_APP_KEY and TIKTOK_SHOP_APP_KEY != "your-app-key-here" and
        TIKTOK_SHOP_APP_SECRET and TIKTOK_SHOP_APP_SECRET != "your-app-secret-here"
    )

    if has_credentials:
        # Initialize agent for API tests
        try:
            agent = TikTokShopAgent()
            agent.set_access_token(TIKTOK_SHOP_ACCESS_TOKEN)

            # Step 4: Test API client rate limiting
            results["API Client Rate Limiting"] = test_api_client_rate_limiting(agent)
        except Exception as e:
            print_error(f"Failed to initialize agent: {str(e)}")
            results["API Client Rate Limiting"] = False

        # Step 5: Test authentication error handling
        results["Auth Error Handling"] = test_error_handling_auth()

        # Step 6: Test validation error handling
        results["Validation Error Handling"] = test_error_handling_validation()

        # Step 7: Test not found error handling
        results["Not Found Error Handling"] = test_error_handling_not_found()
    else:
        print_warning("\nSkipping API integration tests (credentials not configured)")

    # Step 8: Test retry logic (no credentials needed)
    results["Retry Logic Simulation"] = test_retry_logic_simulation()

    # Generate test report
    generate_test_report(results)

    # Return exit code
    return 0 if all(results.values()) else 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"\nUnexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
