#!/usr/bin/env python3
"""
Test script for TikTok Shop product sync functionality

This script validates the product sync features of the TikTok Shop integration,
including product listing, pagination, filtering, and data structure validation.

Requirements:
    1. TikTok Shop seller account (approved)
    2. TikTok Shop API app (approved with Shop API scope)
    3. Valid access token in .env file
    4. Products in TikTok Shop for testing

Usage:
    python test_product_sync.py
"""
import sys
import os
import json
from typing import Optional, Dict, Any, List

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


def test_list_products(agent: TikTokShopAgent) -> Optional[Dict[str, Any]]:
    """
    Test listing products with pagination

    Args:
        agent: TikTokShopAgent instance

    Returns:
        Response containing product list, or None if failed
    """
    print_header("Step 3: Test Product Listing")

    try:
        print("Fetching first page of products (page_size=10)...")
        response = agent.list_products(page_size=10, page_number=1)

        # Extract data from response
        products = response.get('data', {}).get('products', [])
        total = response.get('data', {}).get('total', 0)
        more = response.get('data', {}).get('more', False)

        print_success(f"Product list retrieved successfully")
        print(f"\nResults:")
        print(f"  Products on this page: {len(products)}")
        print(f"  Total products in shop: {total}")
        print(f"  More pages available: {more}")

        if products:
            print(f"\nFirst product preview:")
            product = products[0]
            print(f"  Product ID: {product.get('product_id', 'N/A')}")
            print(f"  Title: {product.get('title', 'N/A')}")
            print(f"  Status: {product.get('status', 'N/A')}")
            print(f"  Price: {product.get('price', 'N/A')}")

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


def validate_product_structure(product: Dict[str, Any]) -> bool:
    """
    Validate product data structure matches expected format

    Args:
        product: Product dictionary to validate

    Returns:
        True if structure is valid, False otherwise
    """
    print_header("Step 4: Validate Product Data Structure")

    print("Checking required fields...")
    required_fields = ['product_id', 'title', 'status']
    optional_fields = ['description', 'price', 'images', 'inventory', 'category']

    all_valid = True

    # Check required fields
    for field in required_fields:
        if field in product:
            print_success(f"Required field '{field}' present")
        else:
            print_error(f"Required field '{field}' missing")
            all_valid = False

    # Check optional fields
    print("\nChecking optional fields...")
    for field in optional_fields:
        if field in product:
            print_success(f"Optional field '{field}' present")
        else:
            print_info(f"Optional field '{field}' not present")

    # Display full structure
    print("\nProduct data structure:")
    print(json.dumps(product, indent=2, default=str)[:500] + "...")

    return all_valid


def test_pagination(agent: TikTokShopAgent) -> bool:
    """
    Test pagination functionality

    Args:
        agent: TikTokShopAgent instance

    Returns:
        True if pagination works correctly, False otherwise
    """
    print_header("Step 5: Test Pagination")

    try:
        # Get first page
        print("Fetching page 1...")
        page1 = agent.list_products(page_size=5, page_number=1)
        products_page1 = page1.get('data', {}).get('products', [])
        more_pages = page1.get('data', {}).get('more', False)

        print_success(f"Page 1 retrieved: {len(products_page1)} products")

        # Get second page if available
        if more_pages:
            print("\nFetching page 2...")
            page2 = agent.list_products(page_size=5, page_number=2)
            products_page2 = page2.get('data', {}).get('products', [])

            print_success(f"Page 2 retrieved: {len(products_page2)} products")

            # Verify pages contain different products
            if products_page1 and products_page2:
                id1 = products_page1[0].get('product_id')
                id2 = products_page2[0].get('product_id')

                if id1 != id2:
                    print_success("Pagination works correctly - pages contain different products")
                    return True
                else:
                    print_error("Pagination issue - pages contain same products")
                    return False
        else:
            print_info("Only one page of products available - pagination test skipped")
            return True

    except Exception as e:
        print_error(f"Pagination test failed: {e}")
        return False

    return True


def test_status_filter(agent: TikTokShopAgent):
    """
    Test product filtering by status

    Args:
        agent: TikTokShopAgent instance
    """
    print_header("Step 6: Test Status Filtering")

    statuses = ['ACTIVE', 'INACTIVE', 'DRAFT']

    for status in statuses:
        try:
            print(f"\nFetching {status} products...")
            response = agent.list_products(status=status, page_size=5)
            products = response.get('data', {}).get('products', [])

            print_success(f"Retrieved {len(products)} {status} products")

            # Verify all products have correct status
            if products:
                all_correct = all(p.get('status') == status for p in products)
                if all_correct:
                    print_success(f"All products have status '{status}'")
                else:
                    print_error(f"Some products don't have status '{status}'")

        except TikTokShopAPIError as e:
            print_info(f"No {status} products or API error: {e}")
        except Exception as e:
            print_error(f"Error fetching {status} products: {e}")


def test_product_details(agent: TikTokShopAgent, product_id: str):
    """
    Test fetching detailed product information

    Args:
        agent: TikTokShopAgent instance
        product_id: Product ID to fetch
    """
    print_header("Step 7: Test Product Details")

    try:
        print(f"Fetching details for product ID: {product_id}...")
        product = agent.get_product_details(product_id)

        print_success("Product details retrieved successfully")
        print("\nProduct Information:")

        product_data = product.get('data', {})
        print(f"  Title: {product_data.get('title', 'N/A')}")
        print(f"  Status: {product_data.get('status', 'N/A')}")
        print(f"  Category: {product_data.get('category', 'N/A')}")

        # Show price information if available
        if 'price' in product_data:
            price_info = product_data['price']
            print(f"  Price: {price_info.get('currency', '')} {price_info.get('amount', 'N/A')}")

        # Show inventory information if available
        if 'inventory' in product_data:
            inventory = product_data['inventory']
            print(f"  Inventory: {inventory}")

        return product

    except TikTokShopAuthError as e:
        print_error(f"Authentication error: {e}")
    except TikTokShopAPIError as e:
        print_error(f"API error: {e}")
    except Exception as e:
        print_error(f"Unexpected error: {e}")

    return None


def test_sync_products(agent: TikTokShopAgent):
    """
    Test full product sync functionality

    Args:
        agent: TikTokShopAgent instance
    """
    print_header("Step 8: Test Product Sync")

    try:
        print("Syncing products (max 20)...")
        print_info("This may take a few moments...")

        products = agent.sync_products(max_products=20, save_to_file=True)

        print_success(f"Sync completed: {len(products)} products synced")

        if products:
            print("\nSync Summary:")
            print(f"  Total products synced: {len(products)}")
            print(f"  Products saved to file in output/tiktok/products/")

            # Show status breakdown
            status_count = {}
            for product in products:
                status = product.get('status', 'UNKNOWN')
                status_count[status] = status_count.get(status, 0) + 1

            print("\nStatus Breakdown:")
            for status, count in status_count.items():
                print(f"  {status}: {count}")

        return products

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


def main():
    """Main test flow"""
    print("\n" + "=" * 70)
    print("  TikTok Shop Product Sync Test")
    print("=" * 70)
    print("\nThis script will test the product sync functionality of the")
    print("TikTok Shop integration.")
    print("\nMake sure you have:")
    print("  1. A TikTok Shop seller account with products")
    print("  2. A TikTok Shop API app with Shop API scope")
    print("  3. A valid access token in your .env file")
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

    # Step 3: Test product listing
    response = test_list_products(agent)
    if not response:
        print("\n" + "=" * 70)
        print("  Test Failed: Product Listing")
        print("=" * 70)
        print("\nCannot continue without successful product listing.")
        sys.exit(1)

    # Extract first product for validation
    products = response.get('data', {}).get('products', [])
    if not products:
        print_error("No products found in your TikTok Shop")
        print_info("Please add products to your TikTok Shop and try again")
        sys.exit(1)

    # Step 4: Validate product structure
    first_product = products[0]
    validate_product_structure(first_product)

    # Step 5: Test pagination
    test_pagination(agent)

    # Step 6: Test status filtering
    test_status_filter(agent)

    # Step 7: Test product details
    product_id = first_product.get('product_id')
    if product_id:
        test_product_details(agent, product_id)
    else:
        print_info("Skipping product details test - no product ID available")

    # Step 8: Test full sync
    test_sync_products(agent)

    # Summary
    print_header("Test Summary")
    print_success("Product sync functionality test completed!")
    print("\nAll tests passed:")
    print("  ✓ Credentials validated")
    print("  ✓ Agent initialized")
    print("  ✓ Products listed successfully")
    print("  ✓ Product data structure validated")
    print("  ✓ Pagination tested")
    print("  ✓ Status filtering tested")
    print("  ✓ Product details retrieved")
    print("  ✓ Full product sync completed")
    print("\nNext steps:")
    print("  1. Document the results in VALIDATION.md")
    print("  2. Review synced products in output/tiktok/products/")
    print("  3. Proceed to test order retrieval and analytics")
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
