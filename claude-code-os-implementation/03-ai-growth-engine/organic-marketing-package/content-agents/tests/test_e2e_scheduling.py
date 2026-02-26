"""
End-to-End Test for TikTok Content Scheduling & Auto-Publishing

This script performs a complete end-to-end verification of the scheduling system:
1. Starts backend API server (uvicorn)
2. Starts scheduler service in background
3. Schedules content for 1 minute in the future
4. Waits for scheduler to execute
5. Verifies content was published successfully
6. Verifies all database state changes
7. Stops both services gracefully

Usage:
    # Run from content-agents directory
    python tests/test_e2e_scheduling.py

    # Or with pytest
    pytest tests/test_e2e_scheduling.py -v -s
"""

import os
import sys
import time
import subprocess
import signal
import requests
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Tuple
import logging

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.connection import get_db_session
from database.models import ScheduledContent, PublishLog

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class E2ETestRunner:
    """
    Orchestrates end-to-end testing of the scheduling system.

    This class manages the lifecycle of services (API server, scheduler)
    and verifies the complete workflow from scheduling to publishing.
    """

    def __init__(self):
        self.api_process: Optional[subprocess.Popen] = None
        self.scheduler_process: Optional[subprocess.Popen] = None
        self.api_base_url = "http://localhost:8000"
        self.content_id: Optional[int] = None

    def start_api_server(self) -> bool:
        """
        Start the FastAPI server using uvicorn.

        Returns:
            bool: True if server started successfully, False otherwise
        """
        try:
            logger.info("Starting API server...")

            # Start uvicorn in a subprocess
            self.api_process = subprocess.Popen(
                [
                    sys.executable, "-m", "uvicorn",
                    "api.main:app",
                    "--host", "0.0.0.0",
                    "--port", "8000",
                    "--log-level", "info"
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Wait for server to be ready (max 30 seconds)
            max_attempts = 30
            for attempt in range(max_attempts):
                try:
                    response = requests.get(f"{self.api_base_url}/health", timeout=1)
                    if response.status_code == 200:
                        logger.info("API server started successfully")
                        return True
                except requests.exceptions.RequestException:
                    time.sleep(1)

            logger.error("API server failed to start within 30 seconds")
            return False

        except Exception as e:
            logger.error(f"Failed to start API server: {e}")
            return False

    def start_scheduler_service(self) -> bool:
        """
        Start the scheduler service in background.

        Returns:
            bool: True if scheduler started successfully, False otherwise
        """
        try:
            logger.info("Starting scheduler service...")

            # Start scheduler in a subprocess
            self.scheduler_process = subprocess.Popen(
                [sys.executable, "scheduler/scheduler_service.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Give scheduler time to initialize (5 seconds)
            time.sleep(5)

            # Check if process is still running
            if self.scheduler_process.poll() is None:
                logger.info("Scheduler service started successfully")
                return True
            else:
                logger.error("Scheduler service terminated unexpectedly")
                return False

        except Exception as e:
            logger.error(f"Failed to start scheduler service: {e}")
            return False

    def schedule_content(self) -> Optional[int]:
        """
        Schedule test content via API for 1 minute in the future.

        Returns:
            Optional[int]: Content ID if successful, None otherwise
        """
        try:
            logger.info("Scheduling test content...")

            # Calculate scheduled time (1 minute from now)
            scheduled_time = datetime.utcnow() + timedelta(minutes=1)

            # Prepare request payload
            payload = {
                "content_type": "post",
                "content_data": {
                    "content": "E2E Test: Automated TikTok post via scheduler",
                    "product_ids": [],
                    "tags": ["e2e-test", "automated"]
                },
                "scheduled_time": scheduled_time.isoformat() + "Z",
                "max_retries": 3
            }

            # Send POST request to schedule content
            response = requests.post(
                f"{self.api_base_url}/api/tiktok/schedule",
                json=payload,
                timeout=10
            )

            if response.status_code == 201:
                data = response.json()
                content_id = data.get("id")
                logger.info(f"Content scheduled successfully with ID: {content_id}")
                logger.info(f"Scheduled time: {scheduled_time.isoformat()}")
                return content_id
            else:
                logger.error(f"Failed to schedule content: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            logger.error(f"Exception while scheduling content: {e}")
            return None

    def wait_for_execution(self, wait_time: int = 130):
        """
        Wait for scheduler to execute the scheduled content.

        Args:
            wait_time: Seconds to wait (default 130s = 2min 10sec for safety)
        """
        logger.info(f"Waiting {wait_time} seconds for scheduler to execute...")

        # Show countdown every 15 seconds
        for remaining in range(wait_time, 0, -15):
            logger.info(f"Time remaining: {remaining} seconds")
            time.sleep(min(15, remaining))

    def verify_published_status(self, content_id: int) -> Tuple[bool, str]:
        """
        Verify content was published successfully via API.

        Args:
            content_id: ID of the scheduled content

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            logger.info(f"Verifying published status for content ID: {content_id}")

            # Get content details via API
            response = requests.get(
                f"{self.api_base_url}/api/tiktok/schedule/{content_id}",
                timeout=10
            )

            if response.status_code != 200:
                return False, f"Failed to get content details: {response.status_code}"

            data = response.json()

            # Verify status is 'published'
            status = data.get("status")
            if status != "published":
                return False, f"Status is '{status}', expected 'published'"

            # Verify tiktok_video_id is populated
            tiktok_video_id = data.get("tiktok_video_id")
            if not tiktok_video_id:
                return False, "tiktok_video_id is not populated"

            # Verify published_at is set
            published_at = data.get("published_at")
            if not published_at:
                return False, "published_at is not set"

            logger.info(f"✓ Status: {status}")
            logger.info(f"✓ TikTok Video ID: {tiktok_video_id}")
            logger.info(f"✓ Published at: {published_at}")

            return True, "Content published successfully"

        except Exception as e:
            return False, f"Exception during verification: {e}"

    def verify_database_state(self, content_id: int) -> Tuple[bool, str]:
        """
        Verify database state directly (ScheduledContent and PublishLog).

        Args:
            content_id: ID of the scheduled content

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            logger.info(f"Verifying database state for content ID: {content_id}")

            db = get_db_session()

            try:
                # Get scheduled content record
                content = db.query(ScheduledContent).filter(
                    ScheduledContent.id == content_id
                ).first()

                if not content:
                    return False, "ScheduledContent record not found in database"

                # Verify status
                if content.status != "published":
                    return False, f"DB status is '{content.status}', expected 'published'"

                # Verify tiktok_video_id
                if not content.tiktok_video_id:
                    return False, "DB tiktok_video_id is not populated"

                # Verify published_at
                if not content.published_at:
                    return False, "DB published_at is not set"

                logger.info(f"✓ DB Status: {content.status}")
                logger.info(f"✓ DB TikTok Video ID: {content.tiktok_video_id}")
                logger.info(f"✓ DB Published at: {content.published_at}")

                # Get publish log records
                publish_logs = db.query(PublishLog).filter(
                    PublishLog.scheduled_content_id == content_id
                ).all()

                if not publish_logs:
                    return False, "No PublishLog records found"

                # Find successful attempt
                success_log = next(
                    (log for log in publish_logs if log.status == "success"),
                    None
                )

                if not success_log:
                    return False, "No successful PublishLog attempt found"

                logger.info(f"✓ PublishLog records: {len(publish_logs)}")
                logger.info(f"✓ Successful attempt: #{success_log.attempt_number}")
                logger.info(f"✓ Attempted at: {success_log.attempted_at}")

                return True, "Database state verified successfully"

            finally:
                db.close()

        except Exception as e:
            return False, f"Exception during database verification: {e}"

    def stop_services(self):
        """Stop both API server and scheduler service gracefully."""
        logger.info("Stopping services...")

        # Stop scheduler service
        if self.scheduler_process:
            try:
                logger.info("Stopping scheduler service...")
                self.scheduler_process.send_signal(signal.SIGTERM)
                self.scheduler_process.wait(timeout=10)
                logger.info("Scheduler service stopped")
            except Exception as e:
                logger.error(f"Error stopping scheduler: {e}")
                self.scheduler_process.kill()

        # Stop API server
        if self.api_process:
            try:
                logger.info("Stopping API server...")
                self.api_process.send_signal(signal.SIGTERM)
                self.api_process.wait(timeout=10)
                logger.info("API server stopped")
            except Exception as e:
                logger.error(f"Error stopping API server: {e}")
                self.api_process.kill()

    def run_e2e_test(self) -> bool:
        """
        Run the complete end-to-end test.

        Returns:
            bool: True if all steps passed, False otherwise
        """
        try:
            logger.info("=" * 80)
            logger.info("STARTING END-TO-END TEST: TikTok Scheduling & Auto-Publishing")
            logger.info("=" * 80)

            # Step 1: Start API server
            if not self.start_api_server():
                logger.error("❌ FAILED: Could not start API server")
                return False

            # Step 2: Start scheduler service
            if not self.start_scheduler_service():
                logger.error("❌ FAILED: Could not start scheduler service")
                return False

            # Step 3: Schedule content
            self.content_id = self.schedule_content()
            if not self.content_id:
                logger.error("❌ FAILED: Could not schedule content")
                return False

            # Step 4: Wait for scheduler to execute
            self.wait_for_execution()

            # Step 5: Verify published status via API
            api_success, api_message = self.verify_published_status(self.content_id)
            if not api_success:
                logger.error(f"❌ FAILED: API verification - {api_message}")
                return False

            logger.info(f"✓ API verification passed: {api_message}")

            # Step 6: Verify database state
            db_success, db_message = self.verify_database_state(self.content_id)
            if not db_success:
                logger.error(f"❌ FAILED: Database verification - {db_message}")
                return False

            logger.info(f"✓ Database verification passed: {db_message}")

            # All steps passed
            logger.info("=" * 80)
            logger.info("✓ END-TO-END TEST PASSED SUCCESSFULLY")
            logger.info("=" * 80)
            return True

        except Exception as e:
            logger.error(f"❌ FAILED: Unexpected exception - {e}")
            return False

        finally:
            # Always stop services
            self.stop_services()


def main():
    """Main entry point for E2E test."""
    runner = E2ETestRunner()
    success = runner.run_e2e_test()

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
