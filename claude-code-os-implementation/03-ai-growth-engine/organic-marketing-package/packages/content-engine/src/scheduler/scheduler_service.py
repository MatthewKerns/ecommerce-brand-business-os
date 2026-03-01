"""
TikTok Content Scheduler Service

This service runs as a background process that automatically executes scheduled
publishing tasks at regular intervals. It uses APScheduler to manage task execution
and includes graceful shutdown handling.

The scheduler manages three main tasks:
1. check_and_publish_due_content() - Runs every 1 minute to publish scheduled content
2. retry_failed_content() - Runs every 5 minutes to retry failed content
3. cleanup_old_records() - Runs daily to clean up old published records

Usage:
    # Start the scheduler service
    python scheduler/scheduler_service.py

    # The service will run indefinitely until stopped with SIGINT (Ctrl+C) or SIGTERM
"""
import signal
import sys
import time
from datetime import datetime
from typing import Optional

try:
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.cron import CronTrigger
    from apscheduler.triggers.interval import IntervalTrigger
except ImportError:
    print("ERROR: APScheduler is not installed. Please run: pip install APScheduler>=3.10.0")
    sys.exit(1)

from scheduler.tasks import (
    check_and_publish_due_content,
    retry_failed_content,
    cleanup_old_records
)
from logging_config import get_logger

# Initialize logger
logger = get_logger("scheduler_service")


class SchedulerService:
    """
    Background scheduler service for TikTok content publishing

    This service manages the automatic execution of publishing tasks using
    APScheduler's BackgroundScheduler. It includes graceful shutdown handling
    and comprehensive logging.

    Attributes:
        scheduler: APScheduler BackgroundScheduler instance
        running: Flag indicating if the service is running

    Example:
        >>> service = SchedulerService()
        >>> service.start()
        >>> # Service runs indefinitely until stopped
        >>> service.stop()
    """

    def __init__(self):
        """Initialize the scheduler service"""
        self.scheduler: Optional[BackgroundScheduler] = None
        self.running = False

        # Register signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        logger.info("Scheduler service initialized")

    def _signal_handler(self, signum: int, frame):
        """
        Handle shutdown signals for graceful termination

        Args:
            signum: Signal number (SIGINT or SIGTERM)
            frame: Current stack frame
        """
        signal_name = "SIGINT" if signum == signal.SIGINT else "SIGTERM"
        logger.info(f"Received {signal_name}, shutting down gracefully...")
        self.stop()
        sys.exit(0)

    def _check_and_publish_wrapper(self):
        """
        Wrapper for check_and_publish_due_content task with error handling
        """
        try:
            logger.info("Running check_and_publish_due_content task")
            processed_count = check_and_publish_due_content()
            logger.info(
                f"check_and_publish_due_content completed: "
                f"{processed_count} items processed"
            )
        except Exception as e:
            logger.error(
                f"Error in check_and_publish_due_content task: {e}",
                exc_info=True
            )

    def _retry_failed_wrapper(self):
        """
        Wrapper for retry_failed_content task with error handling
        """
        try:
            logger.info("Running retry_failed_content task")
            retry_count = retry_failed_content()
            logger.info(
                f"retry_failed_content completed: "
                f"{retry_count} items retried"
            )
        except Exception as e:
            logger.error(
                f"Error in retry_failed_content task: {e}",
                exc_info=True
            )

    def _cleanup_old_records_wrapper(self):
        """
        Wrapper for cleanup_old_records task with error handling
        """
        try:
            logger.info("Running cleanup_old_records task")
            deleted_count = cleanup_old_records(days_to_keep=30)
            logger.info(
                f"cleanup_old_records completed: "
                f"{deleted_count} records deleted"
            )
        except Exception as e:
            logger.error(
                f"Error in cleanup_old_records task: {e}",
                exc_info=True
            )

    def start(self):
        """
        Start the scheduler service and register all tasks

        This method:
        1. Creates a BackgroundScheduler instance
        2. Registers all scheduled tasks with appropriate intervals
        3. Starts the scheduler
        4. Runs indefinitely until stopped

        Scheduled tasks:
        - check_and_publish_due_content: Every 1 minute
        - retry_failed_content: Every 5 minutes
        - cleanup_old_records: Daily at 2:00 AM

        Raises:
            RuntimeError: If service is already running
        """
        if self.running:
            raise RuntimeError("Scheduler service is already running")

        logger.info("Starting scheduler service...")

        # Create scheduler
        self.scheduler = BackgroundScheduler(
            timezone="UTC",
            daemon=True,
            job_defaults={
                'coalesce': True,  # Combine missed executions into one
                'max_instances': 1,  # Only one instance of each job at a time
                'misfire_grace_time': 60  # Allow up to 60 seconds delay
            }
        )

        # Schedule check_and_publish_due_content every 1 minute
        self.scheduler.add_job(
            func=self._check_and_publish_wrapper,
            trigger=IntervalTrigger(minutes=1),
            id='check_and_publish',
            name='Check and publish due content',
            replace_existing=True
        )
        logger.info("Scheduled check_and_publish_due_content to run every 1 minute")

        # Schedule retry_failed_content every 5 minutes
        self.scheduler.add_job(
            func=self._retry_failed_wrapper,
            trigger=IntervalTrigger(minutes=5),
            id='retry_failed',
            name='Retry failed content',
            replace_existing=True
        )
        logger.info("Scheduled retry_failed_content to run every 5 minutes")

        # Schedule cleanup_old_records daily at 2:00 AM UTC
        self.scheduler.add_job(
            func=self._cleanup_old_records_wrapper,
            trigger=CronTrigger(hour=2, minute=0, timezone='UTC'),
            id='cleanup_old_records',
            name='Cleanup old published records',
            replace_existing=True
        )
        logger.info("Scheduled cleanup_old_records to run daily at 2:00 AM UTC")

        # Start the scheduler
        self.scheduler.start()
        self.running = True

        logger.info(
            "Scheduler service started successfully. "
            "Press Ctrl+C to stop."
        )

        # Log scheduled jobs
        jobs = self.scheduler.get_jobs()
        for job in jobs:
            logger.info(f"Job: {job.name} | Next run: {job.next_run_time}")

        # Run indefinitely until stopped
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received, stopping...")
            self.stop()

    def stop(self):
        """
        Stop the scheduler service gracefully

        This method:
        1. Shuts down the scheduler
        2. Waits for running jobs to complete (up to 30 seconds)
        3. Updates the running flag
        """
        if not self.running:
            logger.warning("Scheduler service is not running")
            return

        logger.info("Stopping scheduler service...")

        if self.scheduler:
            # Shutdown scheduler and wait for jobs to complete
            self.scheduler.shutdown(wait=True)
            logger.info("Scheduler shutdown complete")

        self.running = False
        logger.info("Scheduler service stopped")


def main():
    """
    Main entry point for the scheduler service

    Creates and starts the scheduler service, which runs indefinitely
    until stopped with SIGINT (Ctrl+C) or SIGTERM.
    """
    logger.info("=" * 80)
    logger.info("TikTok Content Scheduler Service")
    logger.info("=" * 80)
    logger.info(f"Started at: {datetime.utcnow().isoformat()}Z")
    logger.info("Press Ctrl+C to stop")
    logger.info("")

    try:
        # Create and start scheduler service
        service = SchedulerService()
        service.start()
    except Exception as e:
        logger.error(f"Fatal error in scheduler service: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
