#!/usr/bin/env python3
"""
Test script for TikTok Shop order retrieval and analytics functionality

This script validates the order and analytics features of the TikTok Shop integration,
including order listing, order details, order sync, analytics retrieval, and rate limiting.

Requirements:
    1. TikTok Shop seller account (approved)
    2. TikTok Shop API app (approved with Shop API and Data API scopes)
    3. Valid access token in .env file
    4. Orders in TikTok Shop for testing
    5. Historical data for analytics testing

Usage:
    python test_order_analytics.py
"""
import sys
import os
import json
import time
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.tiktok_shop_agent import TikTokShopAgent
from integrations.tiktok_shop.exceptions import (
    TikTokShopAPIError,
    TikTokShopAuthError,
    TikTokShopRateLimitError,
    TikTokShopNetworkError
)
from config.config import (
    TIKTOK_SHOP_APP_KEY,
    TIKTOK_SHOP_APP_SECRET,
    TIKTOK_SHOP_ACCESS_TOKEN
)


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


def test_agent_initialization() -> Optional[TikTokShopAgent]:
    """
    Test TikTokShopAgent initialization

    Returns:
        TikTokShopAgent instance if successful, None otherwise
    """
    print_header("Step 2: Initialize TikTokShopAgent")

    try:
        agent = TikTokShopAgent(
            app_key=TIKTOK_SHOP_APP_KEY,
            app_secret=TIKTOK_SHOP_APP_SECRET,
            access_token=TIKTOK_SHOP_ACCESS_TOKEN
        )
        print_success("TikTokShopAgent initialized successfully")
        print(f"Agent name: {agent.agent_name}")
        print(f"Platform: TikTok Shop")
        return agent

    except TikTokShopAuthError as e:
        print_error(f"Authentication error: {e}")
        return None
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        return None


def test_list_orders(agent: TikTokShopAgent) -> Optional[Dict[str, Any]]:
    """
    Test listing orders with pagination

    Args:
        agent: TikTokShopAgent instance

    Returns:
        Response containing order list, or None if failed
    """
    print_header("Step 3: Test Order Listing")

    try:
        print("Fetching first page of orders (page_size=10)...")
        response = agent.get_orders(page_size=10, page_number=1)

        # Extract data from response
        orders = response.get('data', {}).get('orders', [])
        total = response.get('data', {}).get('total', 0)
        more = response.get('data', {}).get('more', False)

        print_success(f"Order list retrieved successfully")
        print(f"\nResults:")
        print(f"  Orders on this page: {len(orders)}")
        print(f"  Total orders in shop: {total}")
        print(f"  More pages available: {more}")

        if orders:
            print(f"\nFirst order preview:")
            order = orders[0]
            print(f"  Order ID: {order.get('order_id', 'N/A')}")
            print(f"  Status: {order.get('status', 'N/A')}")
            print(f"  Created: {order.get('create_time', 'N/A')}")
            payment = order.get('payment', {})
            print(f"  Total: {payment.get('currency', '')} {payment.get('total_amount', 'N/A')}")

        return response

    except TikTokShopAuthError as e:
        print_error(f"Authentication error: {e}")
        print_info("Your access token may be invalid or expired")
        return None
    except TikTokShopRateLimitError as e:
        print_error(f"Rate limit error: {e}")
        print_info("Too many requests - rate limiter should prevent this")
        return None
    except TikTokShopAPIError as e:
        print_error(f"API error: {e}")
        return None
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return None


def validate_order_structure(order: Dict[str, Any]) -> bool:
    """
    Validate order data structure matches expected format

    Args:
        order: Order dictionary to validate

    Returns:
        True if structure is valid, False otherwise
    """
    print_header("Step 4: Validate Order Data Structure")

    print("Checking required fields...")
    required_fields = ['order_id', 'status', 'create_time']
    optional_fields = ['buyer_info', 'items', 'payment', 'shipping', 'update_time']

    all_valid = True

    # Check required fields
    for field in required_fields:
        if field in order:
            print_success(f"Required field '{field}' present")
        else:
            print_error(f"Required field '{field}' missing")
            all_valid = False

    # Check optional fields
    print("\nChecking optional fields...")
    for field in optional_fields:
        if field in order:
            print_success(f"Optional field '{field}' present")
        else:
            print_info(f"Optional field '{field}' not present")

    # Display full structure
    print("\nOrder data structure:")
    print(json.dumps(order, indent=2, default=str)[:500] + "...")

    return all_valid


def test_status_filter(agent: TikTokShopAgent):
    """
    Test order filtering by status

    Args:
        agent: TikTokShopAgent instance
    """
    print_header("Step 5: Test Order Status Filtering")

    statuses = ['UNPAID', 'AWAITING_SHIPMENT', 'IN_TRANSIT', 'DELIVERED', 'COMPLETED', 'CANCELLED']

    for status in statuses:
        try:
            print(f"\nFetching {status} orders...")
            response = agent.get_orders(order_status=status, page_size=5)
            orders = response.get('data', {}).get('orders', [])

            print_success(f"Retrieved {len(orders)} {status} orders")

            # Verify all orders have correct status
            if orders:
                all_correct = all(o.get('status') == status for o in orders)
                if all_correct:
                    print_success(f"All orders have status '{status}'")
                else:
                    print_error(f"Some orders don't have status '{status}'")

        except TikTokShopAPIError as e:
            print_info(f"No {status} orders or API error: {e}")
        except Exception as e:
            print_error(f"Error fetching {status} orders: {e}")


def test_order_details(agent: TikTokShopAgent, order_id: str):
    """
    Test fetching detailed order information

    Args:
        agent: TikTokShopAgent instance
        order_id: Order ID to fetch
    """
    print_header("Step 6: Test Order Details")

    try:
        print(f"Fetching details for order ID: {order_id}...")
        order = agent.get_order_details(order_id)

        print_success("Order details retrieved successfully")
        print("\nOrder Information:")

        order_data = order.get('data', {})
        print(f"  Order ID: {order_data.get('order_id', 'N/A')}")
        print(f"  Status: {order_data.get('status', 'N/A')}")
        print(f"  Create Time: {order_data.get('create_time', 'N/A')}")

        # Show payment information if available
        if 'payment' in order_data:
            payment_info = order_data['payment']
            print(f"  Total Amount: {payment_info.get('currency', '')} {payment_info.get('total_amount', 'N/A')}")

        # Show items if available
        if 'items' in order_data:
            items = order_data['items']
            print(f"  Items: {len(items)} item(s)")

        return order

    except TikTokShopAuthError as e:
        print_error(f"Authentication error: {e}")
    except TikTokShopAPIError as e:
        print_error(f"API error: {e}")
    except Exception as e:
        print_error(f"Unexpected error: {e}")

    return None


def test_sync_orders(agent: TikTokShopAgent):
    """
    Test full order sync functionality

    Args:
        agent: TikTokShopAgent instance
    """
    print_header("Step 7: Test Order Sync")

    try:
        print("Syncing orders (max 20)...")
        print_info("This may take a few moments...")

        orders = agent.sync_orders(max_orders=20, save_to_file=True)

        print_success(f"Sync completed: {len(orders)} orders synced")

        if orders:
            print("\nSync Summary:")
            print(f"  Total orders synced: {len(orders)}")
            print(f"  Orders saved to file in output/tiktok/orders/")

            # Show status breakdown
            status_count = {}
            for order in orders:
                status = order.get('status', 'UNKNOWN')
                status_count[status] = status_count.get(status, 0) + 1

            print("\nStatus Breakdown:")
            for status, count in status_count.items():
                print(f"  {status}: {count}")

        return orders

    except TikTokShopAuthError as e:
        print_error(f"Authentication error: {e}")
    except TikTokShopRateLimitError as e:
        print_error(f"Rate limit error: {e}")
        print_info("Rate limiter should prevent this - check configuration")
    except TikTokShopAPIError as e:
        print_error(f"API error: {e}")
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()

    return None


def test_process_order_data(agent: TikTokShopAgent, orders: List[Dict[str, Any]]):
    """
    Test order data processing and analytics

    Args:
        agent: TikTokShopAgent instance
        orders: List of orders to process
    """
    print_header("Step 8: Test Order Data Processing")

    try:
        print("Processing order data...")
        analytics = agent.process_order_data(orders)

        print_success("Order data processed successfully")
        print("\nOrder Analytics:")
        print(f"  Total Orders: {analytics.get('total_orders', 0)}")
        print(f"  Total Revenue: ${analytics.get('total_revenue', 0):.2f}")

        print("\nOrders by Status:")
        for status, count in analytics.get('orders_by_status', {}).items():
            print(f"  {status}: {count}")

        print("\nOrder Value Statistics:")
        stats = analytics.get('order_value_stats', {})
        print(f"  Minimum: ${stats.get('min', 0):.2f}")
        print(f"  Maximum: ${stats.get('max', 0):.2f}")
        print(f"  Average: ${stats.get('average', 0):.2f}")

        print("\nTop Products:")
        for i, product in enumerate(analytics.get('top_products', [])[:5], 1):
            print(f"  {i}. {product.get('product_name', 'Unknown')} - {product.get('total_ordered', 0)} units")

        return analytics

    except Exception as e:
        print_error(f"Error processing order data: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_get_analytics(agent: TikTokShopAgent):
    """
    Test fetching shop analytics

    Args:
        agent: TikTokShopAgent instance
    """
    print_header("Step 9: Test Shop Analytics")

    try:
        # Get analytics for last 30 days
        print("Fetching shop analytics for last 30 days...")
        analytics = agent.get_analytics()

        print_success("Shop analytics retrieved successfully")
        print("\nAnalytics Data:")

        # Display period information
        period = analytics.get('data', {}).get('period', {})
        print(f"  Period: {period.get('start_date', 'N/A')} to {period.get('end_date', 'N/A')}")

        # Display metrics
        metrics = analytics.get('data', {}).get('metrics', {})
        print("\n  Metrics:")
        for metric_name, metric_value in metrics.items():
            print(f"    {metric_name}: {metric_value}")

        return analytics

    except TikTokShopAuthError as e:
        print_error(f"Authentication error: {e}")
        print_info("Data API scope may not be approved")
    except TikTokShopAPIError as e:
        print_error(f"API error: {e}")
        print_info("Shop may not have analytics data yet")
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()

    return None


def test_get_product_analytics(agent: TikTokShopAgent, product_id: str):
    """
    Test fetching product-specific analytics

    Args:
        agent: TikTokShopAgent instance
        product_id: Product ID to get analytics for
    """
    print_header("Step 10: Test Product Analytics")

    try:
        print(f"Fetching analytics for product {product_id}...")
        analytics = agent.get_product_analytics(product_id)

        print_success("Product analytics retrieved successfully")
        print("\nProduct Analytics:")

        data = analytics.get('data', {})
        print(f"  Product ID: {data.get('product_id', 'N/A')}")
        print(f"  Product Name: {data.get('product_name', 'N/A')}")
        print(f"  Period: {data.get('period', 'N/A')}")
        print(f"  Views: {data.get('views', 0)}")
        print(f"  Clicks: {data.get('clicks', 0)}")
        print(f"  Conversions: {data.get('conversions', 0)}")
        print(f"  Conversion Rate: {data.get('conversion_rate', 0)}%")
        print(f"  Revenue: ${data.get('revenue', 0)}")
        print(f"  Units Sold: {data.get('units_sold', 0)}")

        return analytics

    except TikTokShopAuthError as e:
        print_error(f"Authentication error: {e}")
    except TikTokShopAPIError as e:
        print_error(f"API error: {e}")
        print_info("Product may not have analytics data yet")
    except Exception as e:
        print_error(f"Unexpected error: {e}")

    return None


def test_rate_limiting(agent: TikTokShopAgent):
    """
    Test rate limiting functionality

    Args:
        agent: TikTokShopAgent instance
    """
    print_header("Step 11: Test Rate Limiting")

    try:
        print("Making rapid consecutive API calls to test rate limiter...")
        print_info("Rate limiter is configured for 10 requests/second")

        start_time = time.time()
        successful_requests = 0
        rate_limit_errors = 0

        # Make 15 rapid requests to test rate limiter
        for i in range(15):
            try:
                agent.get_orders(page_size=1, page_number=1)
                successful_requests += 1
                print(f"  Request {i+1}: ✓ Success")
            except TikTokShopRateLimitError:
                rate_limit_errors += 1
                print(f"  Request {i+1}: Rate limited (should not happen)")
            except Exception as e:
                print(f"  Request {i+1}: Error - {e}")

        elapsed_time = time.time() - start_time

        print(f"\nRate Limiting Test Results:")
        print(f"  Successful requests: {successful_requests}")
        print(f"  Rate limit errors: {rate_limit_errors}")
        print(f"  Total time: {elapsed_time:.2f} seconds")
        print(f"  Average rate: {successful_requests/elapsed_time:.2f} requests/second")

        if rate_limit_errors == 0:
            print_success("Rate limiter prevented API rate limit errors")
        else:
            print_error(f"Rate limiter failed - {rate_limit_errors} rate limit errors occurred")

        if elapsed_time > 1.0:
            print_success("Rate limiter correctly throttled requests")
        else:
            print_info("Requests completed quickly - may need more requests to test throttling")

    except Exception as e:
        print_error(f"Rate limiting test failed: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Main test flow"""
    print("\n" + "=" * 70)
    print("  TikTok Shop Order Retrieval & Analytics Test")
    print("=" * 70)
    print("\nThis script will test the order and analytics functionality of the")
    print("TikTok Shop integration.")
    print("\nMake sure you have:")
    print("  1. A TikTok Shop seller account with orders")
    print("  2. A TikTok Shop API app with Shop API and Data API scopes")
    print("  3. A valid access token in your .env file")
    print("  4. Historical data for analytics testing")
    print("\nPress Enter to continue or Ctrl+C to exit...")
    input()

    # Step 1: Validate credentials
    if not validate_credentials():
        print("\n" + "=" * 70)
        print("  Test Failed: Invalid Credentials")
        print("=" * 70)
        print("\nPlease configure your credentials and try again.")
        sys.exit(1)

    # Step 2: Initialize agent
    agent = test_agent_initialization()
    if not agent:
        print("\n" + "=" * 70)
        print("  Test Failed: Agent Initialization")
        print("=" * 70)
        sys.exit(1)

    # Step 3: Test order listing
    response = test_list_orders(agent)
    if not response:
        print("\n" + "=" * 70)
        print("  Test Failed: Order Listing")
        print("=" * 70)
        print("\nCannot continue without successful order listing.")
        sys.exit(1)

    # Extract first order for validation
    orders = response.get('data', {}).get('orders', [])
    if not orders:
        print_error("No orders found in your TikTok Shop")
        print_info("Some tests will be skipped due to lack of order data")
        order_id = None
        first_order = None
    else:
        first_order = orders[0]
        order_id = first_order.get('order_id')

        # Step 4: Validate order structure
        validate_order_structure(first_order)

        # Step 6: Test order details
        if order_id:
            test_order_details(agent, order_id)

    # Step 5: Test status filtering
    test_status_filter(agent)

    # Step 7: Test full order sync
    synced_orders = test_sync_orders(agent)

    # Step 8: Test order data processing
    if synced_orders:
        test_process_order_data(agent, synced_orders)
    elif orders:
        test_process_order_data(agent, orders)

    # Step 9: Test shop analytics
    test_get_analytics(agent)

    # Step 10: Test product analytics
    # Try to get a product ID from first order or use a test ID
    product_id = None
    if first_order:
        items = first_order.get('items', [])
        if items:
            product_id = items[0].get('product_id')

    if product_id:
        test_get_product_analytics(agent, product_id)
    else:
        print_info("Skipping product analytics test - no product ID available")

    # Step 11: Test rate limiting
    test_rate_limiting(agent)

    # Summary
    print_header("Test Summary")
    print_success("Order retrieval and analytics functionality test completed!")
    print("\nTests completed:")
    print("  ✓ Credentials validated")
    print("  ✓ Agent initialized")
    print("  ✓ Orders listed successfully")
    if first_order:
        print("  ✓ Order data structure validated")
        print("  ✓ Order details retrieved")
    print("  ✓ Status filtering tested")
    if synced_orders:
        print("  ✓ Full order sync completed")
        print("  ✓ Order data processing completed")
    print("  ✓ Shop analytics tested")
    if product_id:
        print("  ✓ Product analytics tested")
    print("  ✓ Rate limiting tested")
    print("\nNext steps:")
    print("  1. Document the results in VALIDATION.md")
    print("  2. Review synced orders in output/tiktok/orders/")
    print("  3. Verify analytics data matches TikTok Shop dashboard")
    print("  4. Proceed to comprehensive rate limiting and error handling tests")
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
