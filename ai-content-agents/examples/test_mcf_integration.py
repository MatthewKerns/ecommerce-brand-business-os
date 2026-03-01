#!/usr/bin/env python3
"""
Amazon SP-API MCF Integration Test Example

This script demonstrates how to use the Amazon Multi-Channel Fulfillment (MCF) client
to create orders, track shipments, and query inventory. It's designed to be run as
both an integration test and a reference example for developers.

Requirements:
- Amazon Seller Central account with FBA inventory
- SP-API app credentials with Fulfillment scope
- Environment variables configured (see .env.example)

Usage:
    python examples/test_mcf_integration.py

Environment Variables Required:
    AMAZON_SELLER_ID
    AMAZON_SP_API_CLIENT_ID
    AMAZON_SP_API_CLIENT_SECRET
    AMAZON_SP_API_REFRESH_TOKEN
    AMAZON_SP_API_REGION
    AMAZON_MARKETPLACE_ID
"""
import sys
import os
from datetime import datetime, timezone
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from integrations.amazon_sp_api.mcf_client import MCFClient, MCFClientError
    from integrations.amazon_sp_api.models import (
        Address,
        MCFOrderItem,
        MCFFulfillmentOrder,
        ShippingSpeedCategory
    )
    from integrations.amazon_sp_api.auth import get_sp_api_credentials
except ImportError as e:
    print(f"Error importing MCF modules: {e}")
    print("Make sure you're running this from the ai-content-agents directory")
    sys.exit(1)


class MCFIntegrationTest:
    """
    Integration test runner for Amazon MCF operations

    Demonstrates real-world usage patterns and validates the integration
    without requiring pytest or other test frameworks.
    """

    def __init__(self):
        """Initialize the MCF client for testing"""
        try:
            self.client = MCFClient()
            print("✓ MCF Client initialized successfully")
        except MCFClientError as e:
            print(f"✗ Failed to initialize MCF client: {e}")
            raise

    def test_credentials(self) -> bool:
        """
        Test 1: Verify Amazon SP-API credentials are configured

        Returns:
            True if credentials are valid, False otherwise
        """
        print("\n=== Test 1: Verify Credentials ===")
        try:
            creds = get_sp_api_credentials()
            required_keys = ["access_token", "seller_id", "region", "marketplace_id"]

            for key in required_keys:
                if key not in creds or not creds[key]:
                    print(f"✗ Missing credential: {key}")
                    return False

            print(f"✓ Seller ID: {creds['seller_id']}")
            print(f"✓ Region: {creds['region']}")
            print(f"✓ Marketplace: {creds['marketplace_id']}")
            print(f"✓ Access token acquired")
            return True
        except Exception as e:
            print(f"✗ Credential verification failed: {e}")
            return False

    def test_inventory_query(self, test_sku: Optional[str] = None) -> bool:
        """
        Test 2: Query inventory levels

        Args:
            test_sku: Optional SKU to check (queries all if not provided)

        Returns:
            True if inventory query succeeds, False otherwise
        """
        print("\n=== Test 2: Query Inventory ===")
        try:
            if test_sku:
                print(f"Querying inventory for SKU: {test_sku}")
                result = self.client.get_inventory_summaries(seller_skus=[test_sku])
            else:
                print("Querying all MCF-eligible inventory...")
                result = self.client.get_inventory_summaries()

            items = result.get("inventory_items", [])

            if not items:
                print("⚠ No inventory items found")
                print("  Make sure you have FBA inventory in your account")
                return True  # Not a failure, just no inventory

            print(f"✓ Found {len(items)} inventory item(s):")
            for item in items[:5]:  # Show first 5 items
                print(f"  - SKU: {item.seller_sku}")
                print(f"    Fulfillable: {item.fulfillable_quantity}")
                print(f"    Total: {item.total_quantity}")
                if item.asin:
                    print(f"    ASIN: {item.asin}")

            if result.get("has_more"):
                print(f"  ... and more (next_token: {result.get('next_token')[:20]}...)")

            return True
        except MCFClientError as e:
            print(f"✗ Inventory query failed: {e}")
            return False

    def test_sku_availability(self, sku: str, quantity: int = 1) -> bool:
        """
        Test 3: Check if specific SKU is available

        Args:
            sku: Seller SKU to check
            quantity: Required quantity

        Returns:
            True if SKU check succeeds, False otherwise
        """
        print(f"\n=== Test 3: Check SKU Availability ===")
        print(f"Checking SKU '{sku}' for quantity {quantity}")

        try:
            result = self.client.check_sku_availability(sku, required_quantity=quantity)

            if result["available"]:
                print(f"✓ SKU '{sku}' is available")
                print(f"  Fulfillable: {result['fulfillable_quantity']}")
                print(f"  Required: {result['required_quantity']}")
                if result.get("total_inbound", 0) > 0:
                    print(f"  Inbound: {result['total_inbound']}")
            else:
                print(f"⚠ SKU '{sku}' is not available or insufficient quantity")
                print(f"  Fulfillable: {result['fulfillable_quantity']}")
                print(f"  Required: {result['required_quantity']}")
                print(f"  Message: {result.get('message', 'N/A')}")

            return True
        except MCFClientError as e:
            print(f"✗ SKU availability check failed: {e}")
            return False

    def test_create_fulfillment_order(
        self,
        order_id: str,
        sku: str,
        quantity: int = 1,
        dry_run: bool = True
    ) -> bool:
        """
        Test 4: Create MCF fulfillment order

        Args:
            order_id: Unique order ID
            sku: Seller SKU to fulfill
            quantity: Quantity to fulfill
            dry_run: If True, shows what would be created without submitting

        Returns:
            True if order creation succeeds (or dry run completes), False otherwise
        """
        print(f"\n=== Test 4: Create Fulfillment Order {'(DRY RUN)' if dry_run else ''} ===")

        try:
            # Create test address
            address = Address(
                name="John Doe",
                address_line1="123 Main Street",
                address_line2="Apt 4B",
                city="Seattle",
                state_or_province_code="WA",
                postal_code="98101",
                country_code="US",
                phone="206-555-0100"
            )

            # Create order items
            items = [
                MCFOrderItem(
                    seller_sku=sku,
                    seller_fulfillment_order_item_id=f"{order_id}-item-1",
                    quantity=quantity
                )
            ]

            # Create fulfillment order
            order = MCFFulfillmentOrder(
                seller_fulfillment_order_id=order_id,
                marketplace_id=self.client.marketplace_id,
                displayable_order_id=order_id,
                displayable_order_date=datetime.now(timezone.utc).isoformat(),
                displayable_order_comment="Test order - MCF integration verification",
                shipping_speed_category=ShippingSpeedCategory.STANDARD,
                destination_address=address,
                items=items
            )

            print(f"Order ID: {order_id}")
            print(f"SKU: {sku} x {quantity}")
            print(f"Ship to: {address.name}, {address.city}, {address.state_or_province_code}")
            print(f"Shipping: {ShippingSpeedCategory.STANDARD}")

            if dry_run:
                print("\n✓ Dry run complete - order prepared but NOT submitted")
                print("  To create a real order, set dry_run=False")
                print("  WARNING: Real orders will consume inventory and may incur charges!")
                return True

            # Actually create the order (only if dry_run=False)
            result = self.client.create_fulfillment_order(order)

            if result.get("success"):
                print(f"✓ Order created successfully!")
                print(f"  Order ID: {result.get('seller_fulfillment_order_id')}")
            else:
                print(f"⚠ Order creation returned unexpected response: {result}")

            return True
        except MCFClientError as e:
            print(f"✗ Order creation failed: {e}")
            return False

    def test_get_fulfillment_order(self, order_id: str) -> bool:
        """
        Test 5: Retrieve fulfillment order details

        Args:
            order_id: Seller fulfillment order ID to retrieve

        Returns:
            True if order retrieval succeeds, False otherwise
        """
        print(f"\n=== Test 5: Get Fulfillment Order ===")
        print(f"Retrieving order: {order_id}")

        try:
            order = self.client.get_fulfillment_order(order_id)

            print(f"✓ Order retrieved successfully")
            print(f"  Order ID: {order.seller_fulfillment_order_id}")
            print(f"  Status: {order.status}")
            print(f"  Ship to: {order.destination_address.name}")
            print(f"  Items: {len(order.items)}")

            for item in order.items:
                print(f"    - {item.seller_sku} x {item.quantity}")

            if order.shipments:
                print(f"  Shipments: {len(order.shipments)}")
                for shipment in order.shipments:
                    if shipment.packages:
                        for package in shipment.packages:
                            print(f"    - Tracking: {package.tracking_number}")
                            print(f"      Carrier: {package.carrier_code}")

            return True
        except MCFClientError as e:
            print(f"✗ Order retrieval failed: {e}")
            if "not found" in str(e).lower():
                print("  This is expected if the order doesn't exist yet")
            return False

    def test_list_fulfillment_orders(self, days_back: int = 7) -> bool:
        """
        Test 6: List recent fulfillment orders

        Args:
            days_back: Number of days to look back

        Returns:
            True if listing succeeds, False otherwise
        """
        print(f"\n=== Test 6: List Fulfillment Orders ===")
        print(f"Listing orders from the last {days_back} days...")

        try:
            from datetime import timedelta
            start_date = datetime.now(timezone.utc) - timedelta(days=days_back)

            result = self.client.list_all_fulfillment_orders(query_start_date=start_date)

            orders = result.get("orders", [])

            if not orders:
                print("⚠ No orders found in the specified time period")
                return True  # Not a failure

            print(f"✓ Found {len(orders)} order(s):")
            for order in orders[:5]:  # Show first 5
                print(f"  - Order: {order.seller_fulfillment_order_id}")
                print(f"    Status: {order.status}")
                print(f"    Date: {order.displayable_order_date}")

            if result.get("has_more"):
                print(f"  ... and more (use next_token for pagination)")

            return True
        except MCFClientError as e:
            print(f"✗ Order listing failed: {e}")
            return False

    def run_all_tests(
        self,
        test_sku: Optional[str] = None,
        test_order_id: Optional[str] = None,
        create_real_order: bool = False
    ):
        """
        Run all integration tests

        Args:
            test_sku: Optional SKU for testing (uses first available if not provided)
            test_order_id: Optional order ID to retrieve (creates new if not provided)
            create_real_order: If True, creates a real MCF order (WARNING: uses inventory!)
        """
        print("=" * 60)
        print("Amazon SP-API MCF Integration Test Suite")
        print("=" * 60)

        results = []

        # Test 1: Credentials
        results.append(("Credentials", self.test_credentials()))

        # Test 2: Inventory Query
        results.append(("Inventory Query", self.test_inventory_query(test_sku)))

        # Test 3: SKU Availability (only if we have a SKU)
        if test_sku:
            results.append(("SKU Availability", self.test_sku_availability(test_sku)))

        # Test 4: Create Order (dry run by default)
        if test_sku:
            order_id = test_order_id or f"TEST-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            results.append((
                "Create Order",
                self.test_create_fulfillment_order(
                    order_id,
                    test_sku,
                    quantity=1,
                    dry_run=not create_real_order
                )
            ))

        # Test 5: Get Order (only if we have an order ID)
        if test_order_id:
            results.append(("Get Order", self.test_get_fulfillment_order(test_order_id)))

        # Test 6: List Orders
        results.append(("List Orders", self.test_list_fulfillment_orders()))

        # Print summary
        print("\n" + "=" * 60)
        print("Test Summary")
        print("=" * 60)

        passed = sum(1 for _, result in results if result)
        total = len(results)

        for test_name, result in results:
            status = "✓ PASS" if result else "✗ FAIL"
            print(f"{status}: {test_name}")

        print(f"\nPassed: {passed}/{total}")

        if passed == total:
            print("\n🎉 All tests passed!")
            return 0
        else:
            print(f"\n⚠ {total - passed} test(s) failed")
            return 1


def main():
    """Main entry point for the integration test"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Amazon SP-API MCF Integration Test",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run all tests (dry run, no real orders created)
  python examples/test_mcf_integration.py

  # Test with a specific SKU
  python examples/test_mcf_integration.py --sku DECK-BOX-001

  # Retrieve a specific order
  python examples/test_mcf_integration.py --order-id ORDER-12345

  # Create a REAL order (WARNING: uses inventory!)
  python examples/test_mcf_integration.py --sku DECK-BOX-001 --create-real-order
        """
    )

    parser.add_argument(
        "--sku",
        help="Seller SKU to use for testing"
    )
    parser.add_argument(
        "--order-id",
        help="Existing order ID to retrieve and test"
    )
    parser.add_argument(
        "--create-real-order",
        action="store_true",
        help="Create a real MCF order (WARNING: uses inventory and may incur charges!)"
    )

    args = parser.parse_args()

    # Verify environment variables
    required_env_vars = [
        "AMAZON_SELLER_ID",
        "AMAZON_SP_API_CLIENT_ID",
        "AMAZON_SP_API_CLIENT_SECRET",
        "AMAZON_SP_API_REFRESH_TOKEN",
        "AMAZON_SP_API_REGION",
        "AMAZON_MARKETPLACE_ID"
    ]

    missing_vars = [var for var in required_env_vars if not os.getenv(var)]

    if missing_vars:
        print("Error: Missing required environment variables:")
        for var in missing_vars:
            print(f"  - {var}")
        print("\nPlease configure these variables in your .env file")
        print("See .env.example for reference")
        return 1

    # Run tests
    try:
        tester = MCFIntegrationTest()
        return tester.run_all_tests(
            test_sku=args.sku,
            test_order_id=args.order_id,
            create_real_order=args.create_real_order
        )
    except Exception as e:
        print(f"\n✗ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
