#!/usr/bin/env python3
"""
End-to-end verification script for order event tracking flow.

This script verifies:
1. POST /api/klaviyo/events endpoint works for tracking order events
2. Event is sent to Klaviyo API (or mocked)
3. Sync history is updated
4. Proper error handling for invalid data

Usage:
    python tests/verify_e2e_event_tracking.py
"""
import sys
import time
import requests
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.models import KlaviyoSyncHistory
from database.connection import get_db_session


class E2EEventTrackingVerifier:
    """End-to-end verification for order event tracking flow."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        """Initialize verifier with API base URL."""
        self.base_url = base_url
        self.errors = []
        self.successes = []
        self.test_event_id = None

    def log_success(self, message: str):
        """Log a successful verification step."""
        self.successes.append(message)
        print(f"✅ {message}")

    def log_error(self, message: str):
        """Log a failed verification step."""
        self.errors.append(message)
        print(f"❌ {message}")

    def verify_server_running(self) -> bool:
        """Verify FastAPI server is running."""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                self.log_success("FastAPI server is running")
                return True
            else:
                self.log_error(f"Server health check failed with status {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            self.log_error(f"Cannot connect to server: {e}")
            return False

    def verify_track_order_event(self) -> dict:
        """
        Verify POST /api/klaviyo/events endpoint works for order tracking.

        Returns:
            Response data dict if successful, empty dict otherwise
        """
        try:
            # Prepare order event request
            payload = {
                "metric_name": "Placed Order",
                "customer_email": "test_event_customer@example.com",
                "customer_phone": "+1234567890",
                "customer_external_id": "test_customer_123",
                "properties": {
                    "order_id": "TEST-ORDER-12345",
                    "total": 299.98,
                    "currency": "USD",
                    "items": [
                        {
                            "product_id": "PROD-001",
                            "name": "Tactical Backpack",
                            "price": 149.99,
                            "quantity": 1,
                            "sku": "TB-001"
                        },
                        {
                            "product_id": "PROD-002",
                            "name": "Camping Gear Set",
                            "price": 149.99,
                            "quantity": 1,
                            "sku": "CG-002"
                        }
                    ],
                    "shipping_address": {
                        "address1": "123 Test St",
                        "city": "San Francisco",
                        "region": "CA",
                        "country": "United States",
                        "zip": "94102"
                    },
                    "payment_method": "credit_card",
                    "tracking_number": "TRACK123456"
                },
                "time": datetime.utcnow().isoformat() + "Z"
            }

            # Call event tracking endpoint
            response = requests.post(
                f"{self.base_url}/api/klaviyo/events",
                json=payload,
                timeout=30
            )

            # Check response status
            if response.status_code not in [200, 201]:
                self.log_error(
                    f"Event tracking endpoint returned status {response.status_code}: "
                    f"{response.text}"
                )
                return {}

            # Parse response
            data = response.json()

            # Verify response structure
            required_fields = ["request_id", "metric_name", "status", "message"]
            missing_fields = [f for f in required_fields if f not in data]
            if missing_fields:
                self.log_error(f"Response missing required fields: {missing_fields}")
                return {}

            # Verify success status
            if data["status"] != "success":
                self.log_error(f"Event tracking failed with status: {data['status']}")
                return {}

            # Store event ID for later verification
            if "event_id" in data:
                self.test_event_id = data["event_id"]

            self.log_success(
                f"Event tracking endpoint worked: '{payload['metric_name']}' event tracked"
            )
            return data

        except requests.exceptions.RequestException as e:
            self.log_error(f"Request to event tracking endpoint failed: {e}")
            return {}
        except Exception as e:
            self.log_error(f"Unexpected error calling event tracking endpoint: {e}")
            return {}

    def verify_invalid_data_handling(self) -> bool:
        """
        Verify proper error handling for invalid event data.

        Returns:
            True if error handling works correctly, False otherwise
        """
        test_cases = [
            {
                "name": "Missing required fields",
                "payload": {
                    "metric_name": "Placed Order"
                    # Missing customer identifier
                },
                "expected_status": 422  # Validation error
            },
            {
                "name": "Invalid email format",
                "payload": {
                    "metric_name": "Placed Order",
                    "customer_email": "not-an-email",
                    "properties": {}
                },
                "expected_status": 422  # Validation error
            },
            {
                "name": "Empty metric name",
                "payload": {
                    "metric_name": "",
                    "customer_email": "test@example.com",
                    "properties": {}
                },
                "expected_status": 422  # Validation error
            }
        ]

        all_passed = True
        for test_case in test_cases:
            try:
                response = requests.post(
                    f"{self.base_url}/api/klaviyo/events",
                    json=test_case["payload"],
                    timeout=10
                )

                # Verify error response
                if response.status_code == test_case["expected_status"]:
                    self.log_success(
                        f"Error handling works for: {test_case['name']} "
                        f"(status {response.status_code})"
                    )
                else:
                    self.log_error(
                        f"Incorrect status for {test_case['name']}: "
                        f"expected {test_case['expected_status']}, "
                        f"got {response.status_code}"
                    )
                    all_passed = False

            except Exception as e:
                self.log_error(f"Error testing {test_case['name']}: {e}")
                all_passed = False

        return all_passed

    def verify_sync_history_updated(self) -> bool:
        """
        Verify sync history was updated for event tracking.

        Returns:
            True if verification passed, False otherwise
        """
        try:
            with get_db_session() as db:
                # Query for recent event sync history
                sync_records = db.query(KlaviyoSyncHistory).filter(
                    KlaviyoSyncHistory.sync_type == 'event_sync'
                ).order_by(
                    KlaviyoSyncHistory.created_at.desc()
                ).limit(10).all()

                # Note: Single event tracking may not create sync history
                # (that's more for bulk sync operations), but we can check
                # if the database connection and model are working

                # Even if no records, just verify the query works
                if sync_records:
                    self.log_success(
                        f"Found {len(sync_records)} event sync history records "
                        f"(most recent processed {sync_records[0].records_processed or 0} records)"
                    )
                else:
                    # This is OK for single event tracking
                    self.log_success(
                        "Sync history query works (single events may not create sync records)"
                    )

                return True

        except Exception as e:
            self.log_error(f"Failed to query sync history: {e}")
            return False

    def verify_bulk_event_sync(self) -> dict:
        """
        Verify POST /api/klaviyo/sync/events endpoint for bulk sync.

        Returns:
            Response data dict if successful, empty dict otherwise
        """
        try:
            # Prepare request with mock data for testing
            payload = {
                "use_mock_data": True,
                "page_size": 5,
                "max_pages": 1
            }

            # Call bulk sync endpoint
            response = requests.post(
                f"{self.base_url}/api/klaviyo/sync/events",
                json=payload,
                timeout=30
            )

            # Check response status
            if response.status_code != 200:
                self.log_error(
                    f"Bulk event sync endpoint returned status {response.status_code}: "
                    f"{response.text}"
                )
                return {}

            # Parse response
            data = response.json()

            # Verify response structure
            required_fields = ["request_id", "events_tracked", "stats", "status", "message"]
            missing_fields = [f for f in required_fields if f not in data]
            if missing_fields:
                self.log_error(f"Response missing required fields: {missing_fields}")
                return {}

            # Verify success status
            if data["status"] != "success":
                self.log_error(f"Bulk sync failed with status: {data['status']}")
                return {}

            # Verify events were tracked
            if data["events_tracked"] <= 0:
                self.log_error("No events were tracked in bulk sync")
                return {}

            self.log_success(
                f"Bulk event sync endpoint worked: {data['events_tracked']} events tracked"
            )
            return data

        except requests.exceptions.RequestException as e:
            self.log_error(f"Request to bulk sync endpoint failed: {e}")
            return {}
        except Exception as e:
            self.log_error(f"Unexpected error calling bulk sync endpoint: {e}")
            return {}

    def verify_bulk_sync_history(self) -> bool:
        """
        Verify sync history was created for bulk event sync.

        Returns:
            True if verification passed, False otherwise
        """
        try:
            with get_db_session() as db:
                # Query for recent event sync history
                sync_records = db.query(KlaviyoSyncHistory).filter(
                    KlaviyoSyncHistory.sync_type == 'event_sync'
                ).order_by(
                    KlaviyoSyncHistory.created_at.desc()
                ).limit(5).all()

                # Verify records exist
                if not sync_records:
                    self.log_error("No event sync history records found in database")
                    return False

                # Verify most recent record has data
                latest_record = sync_records[0]
                if latest_record.records_processed is None:
                    self.log_error("Sync history missing records_processed")
                    return False

                self.log_success(
                    f"Found {len(sync_records)} sync history records, "
                    f"latest processed {latest_record.records_processed} records"
                )
                return True

        except Exception as e:
            self.log_error(f"Failed to query bulk sync history: {e}")
            return False

    def run(self) -> bool:
        """
        Run all verification steps.

        Returns:
            True if all verifications passed, False otherwise
        """
        print("\n" + "="*70)
        print("🔍 Starting End-to-End Verification: Order Event Tracking Flow")
        print("="*70 + "\n")

        # Step 1: Verify server is running
        print("Step 1: Verifying FastAPI server is running...")
        if not self.verify_server_running():
            print("\n❌ Server is not running. Please start it with:")
            print("   cd claude-code-os-implementation/03-ai-growth-engine/organic-marketing-package/content-agents")
            print("   uvicorn api.main:app --reload")
            return False

        # Step 2: Call event tracking endpoint
        print("\nStep 2: Calling POST /api/klaviyo/events to track an order event...")
        event_response = self.verify_track_order_event()
        if not event_response:
            return False

        # Step 3: Verify error handling for invalid data
        print("\nStep 3: Verifying proper error handling for invalid data...")
        if not self.verify_invalid_data_handling():
            return False

        # Step 4: Verify sync history (single events may not create records)
        print("\nStep 4: Checking sync history database access...")
        if not self.verify_sync_history_updated():
            return False

        # Step 5: Test bulk event sync (which does create sync history)
        print("\nStep 5: Testing bulk event sync endpoint...")
        bulk_response = self.verify_bulk_event_sync()
        if not bulk_response:
            return False

        # Wait a moment for database to update
        time.sleep(1)

        # Step 6: Verify bulk sync history was created
        print("\nStep 6: Verifying bulk sync history was recorded...")
        if not self.verify_bulk_sync_history():
            return False

        # Print summary
        print("\n" + "="*70)
        print("📊 Verification Summary")
        print("="*70)
        print(f"✅ Successful checks: {len(self.successes)}")
        print(f"❌ Failed checks: {len(self.errors)}")

        if self.errors:
            print("\n❌ VERIFICATION FAILED")
            print("\nErrors:")
            for i, error in enumerate(self.errors, 1):
                print(f"  {i}. {error}")
            return False
        else:
            print("\n✅ ALL VERIFICATIONS PASSED!")
            print("\n🎉 End-to-end order event tracking flow is working correctly!")
            print("\nVerified capabilities:")
            print("  • Single event tracking via POST /api/klaviyo/events")
            print("  • Bulk event sync via POST /api/klaviyo/sync/events")
            print("  • Error handling for invalid data")
            print("  • Sync history tracking in database")
            return True


def main():
    """Main entry point for verification script."""
    import argparse

    parser = argparse.ArgumentParser(
        description="End-to-end verification for order event tracking flow"
    )
    parser.add_argument(
        "--base-url",
        default="http://localhost:8000",
        help="Base URL for FastAPI server (default: http://localhost:8000)"
    )

    args = parser.parse_args()

    # Run verification
    verifier = E2EEventTrackingVerifier(base_url=args.base_url)
    success = verifier.run()

    # Exit with appropriate status code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
