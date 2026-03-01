#!/usr/bin/env python3
"""
End-to-end verification script for customer profile sync flow.

This script verifies:
1. FastAPI server can start
2. POST /api/klaviyo/sync/profiles endpoint works
3. Profiles are created in database
4. Sync history is recorded
5. API returns success response

Usage:
    python tests/verify_e2e_profile_sync.py
"""
import sys
import time
import requests
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.models import KlaviyoProfile, KlaviyoSyncHistory
from database.connection import get_db_session


class E2EVerifier:
    """End-to-end verification for customer profile sync flow."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        """Initialize verifier with API base URL."""
        self.base_url = base_url
        self.errors = []
        self.successes = []

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

    def verify_sync_profiles_endpoint(self) -> dict:
        """
        Verify POST /api/klaviyo/sync/profiles endpoint works.

        Returns:
            Response data dict if successful, empty dict otherwise
        """
        try:
            # Prepare request with mock data for testing
            payload = {
                "use_mock_data": True,
                "page_size": 10,
                "max_pages": 1
            }

            # Call sync endpoint
            response = requests.post(
                f"{self.base_url}/api/klaviyo/sync/profiles",
                json=payload,
                timeout=30
            )

            # Check response status
            if response.status_code != 200:
                self.log_error(
                    f"Sync profiles endpoint returned status {response.status_code}: "
                    f"{response.text}"
                )
                return {}

            # Parse response
            data = response.json()

            # Verify response structure
            required_fields = ["request_id", "profiles_synced", "stats", "status", "message"]
            missing_fields = [f for f in required_fields if f not in data]
            if missing_fields:
                self.log_error(f"Response missing required fields: {missing_fields}")
                return {}

            # Verify success status
            if data["status"] != "success":
                self.log_error(f"Sync failed with status: {data['status']}")
                return {}

            # Verify profiles were synced
            if data["profiles_synced"] <= 0:
                self.log_error("No profiles were synced")
                return {}

            self.log_success(
                f"Sync profiles endpoint worked: {data['profiles_synced']} profiles synced"
            )
            return data

        except requests.exceptions.RequestException as e:
            self.log_error(f"Request to sync endpoint failed: {e}")
            return {}
        except Exception as e:
            self.log_error(f"Unexpected error calling sync endpoint: {e}")
            return {}

    def verify_profiles_in_database(self, expected_count: int) -> bool:
        """
        Verify profiles were created in database.

        Args:
            expected_count: Number of profiles expected to be in database

        Returns:
            True if verification passed, False otherwise
        """
        try:
            with get_db_session() as db:
                # Query for test profiles (created with mock data)
                profiles = db.query(KlaviyoProfile).filter(
                    KlaviyoProfile.email.like('test%@example.com')
                ).all()

                # Verify count
                actual_count = len(profiles)
                if actual_count < expected_count:
                    self.log_error(
                        f"Expected at least {expected_count} profiles in database, "
                        f"found {actual_count}"
                    )
                    return False

                # Verify profile data
                for profile in profiles[:3]:  # Check first 3 profiles
                    if not profile.email:
                        self.log_error(f"Profile {profile.id} missing email")
                        return False
                    if not profile.first_name:
                        self.log_error(f"Profile {profile.id} missing first_name")
                        return False

                self.log_success(
                    f"Found {actual_count} profiles in database with correct data"
                )
                return True

        except Exception as e:
            self.log_error(f"Database query failed: {e}")
            return False

    def verify_sync_history(self) -> bool:
        """
        Verify sync history was recorded in database.

        Returns:
            True if verification passed, False otherwise
        """
        try:
            with get_db_session() as db:
                # Query for recent sync history
                sync_records = db.query(KlaviyoSyncHistory).filter(
                    KlaviyoSyncHistory.sync_type == 'profile_sync'
                ).order_by(
                    KlaviyoSyncHistory.created_at.desc()
                ).limit(5).all()

                # Verify records exist
                if not sync_records:
                    self.log_error("No sync history records found in database")
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
            self.log_error(f"Failed to query sync history: {e}")
            return False

    def cleanup_test_data(self):
        """Clean up test data from database."""
        try:
            with get_db_session() as db:
                # Delete test profiles
                db.query(KlaviyoProfile).filter(
                    KlaviyoProfile.email.like('test%@example.com')
                ).delete(synchronize_session=False)

                db.commit()
                print("🧹 Cleaned up test data")
        except Exception as e:
            print(f"⚠️  Warning: Failed to clean up test data: {e}")

    def run(self, cleanup: bool = True) -> bool:
        """
        Run all verification steps.

        Args:
            cleanup: Whether to clean up test data after verification

        Returns:
            True if all verifications passed, False otherwise
        """
        print("\n" + "="*70)
        print("🔍 Starting End-to-End Verification: Customer Profile Sync Flow")
        print("="*70 + "\n")

        # Step 1: Verify server is running
        print("Step 1: Verifying FastAPI server is running...")
        if not self.verify_server_running():
            print("\n❌ Server is not running. Please start it with:")
            print("   cd claude-code-os-implementation/03-ai-growth-engine/organic-marketing-package/content-agents")
            print("   uvicorn api.main:app --reload")
            return False

        # Step 2: Call sync endpoint
        print("\nStep 2: Calling POST /api/klaviyo/sync/profiles endpoint...")
        sync_response = self.verify_sync_profiles_endpoint()
        if not sync_response:
            return False

        # Wait a moment for database to update
        time.sleep(1)

        # Step 3: Verify profiles in database
        print("\nStep 3: Verifying profiles were created in database...")
        expected_count = sync_response.get("profiles_synced", 0)
        if not self.verify_profiles_in_database(expected_count):
            return False

        # Step 4: Verify sync history
        print("\nStep 4: Verifying sync history was recorded...")
        if not self.verify_sync_history():
            return False

        # Step 5: Verify API response
        print("\nStep 5: Verifying API response structure...")
        if sync_response.get("status") == "success":
            self.log_success("API returned success response with all required fields")
        else:
            self.log_error("API response validation failed")
            return False

        # Cleanup test data
        if cleanup:
            print("\nCleaning up test data...")
            self.cleanup_test_data()

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
            print("\n🎉 End-to-end customer profile sync flow is working correctly!")
            return True


def main():
    """Main entry point for verification script."""
    import argparse

    parser = argparse.ArgumentParser(
        description="End-to-end verification for customer profile sync flow"
    )
    parser.add_argument(
        "--base-url",
        default="http://localhost:8000",
        help="Base URL for FastAPI server (default: http://localhost:8000)"
    )
    parser.add_argument(
        "--no-cleanup",
        action="store_true",
        help="Do not clean up test data after verification"
    )

    args = parser.parse_args()

    # Run verification
    verifier = E2EVerifier(base_url=args.base_url)
    success = verifier.run(cleanup=not args.no_cleanup)

    # Exit with appropriate status code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
