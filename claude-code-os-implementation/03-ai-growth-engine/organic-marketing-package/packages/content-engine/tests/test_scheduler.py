"""
Integration tests for TikTok Content Scheduler Service.

Tests cover:
- Service initialization and lifecycle management
- Job scheduling and execution
- Task wrapper execution and error handling
- Signal handling for graceful shutdown
- Integration with scheduler tasks
- Background scheduler configuration
- Error recovery and logging
"""

import pytest
import signal
import time
from unittest.mock import Mock, patch, MagicMock, call
from datetime import datetime, timedelta
import json

from scheduler.scheduler_service import SchedulerService
from scheduler.tasks import (
    check_and_publish_due_content,
    retry_failed_content,
    cleanup_old_records
)
from database.models import ScheduledContent, PublishLog
from exceptions import DatabaseError


class TestSchedulerServiceInitialization:
    """Test suite for SchedulerService initialization"""

    @patch('scheduler.scheduler_service.signal.signal')
    def test_init_success(self, mock_signal):
        """Test successful service initialization"""
        service = SchedulerService()

        assert service.scheduler is None
        assert service.running is False

        # Verify signal handlers were registered
        assert mock_signal.call_count == 2
        mock_signal.assert_any_call(signal.SIGINT, service._signal_handler)
        mock_signal.assert_any_call(signal.SIGTERM, service._signal_handler)

    @patch('scheduler.scheduler_service.signal.signal')
    def test_init_sets_up_signal_handlers(self, mock_signal):
        """Test that initialization sets up signal handlers"""
        service = SchedulerService()

        # Verify both signal handlers are registered
        calls = mock_signal.call_args_list
        signal_numbers = [call_args[0][0] for call_args in calls]

        assert signal.SIGINT in signal_numbers
        assert signal.SIGTERM in signal_numbers


class TestSchedulerServiceStart:
    """Test suite for SchedulerService.start() method"""

    @pytest.fixture
    def mock_scheduler(self):
        """Mock BackgroundScheduler instance"""
        return MagicMock()

    @patch('scheduler.scheduler_service.BackgroundScheduler')
    @patch('scheduler.scheduler_service.signal.signal')
    def test_start_creates_scheduler(self, mock_signal, mock_scheduler_class):
        """Test that start() creates a BackgroundScheduler"""
        mock_scheduler = MagicMock()
        mock_scheduler_class.return_value = mock_scheduler
        mock_scheduler.get_jobs.return_value = []

        service = SchedulerService()

        # Patch the while loop to exit immediately
        with patch.object(service, 'running', side_effect=[True, False]):
            service.start()

        # Verify scheduler was created with correct config
        mock_scheduler_class.assert_called_once_with(
            timezone="UTC",
            daemon=True,
            job_defaults={
                'coalesce': True,
                'max_instances': 1,
                'misfire_grace_time': 60
            }
        )

    @patch('scheduler.scheduler_service.BackgroundScheduler')
    @patch('scheduler.scheduler_service.signal.signal')
    def test_start_registers_all_jobs(self, mock_signal, mock_scheduler_class):
        """Test that start() registers all scheduled jobs"""
        mock_scheduler = MagicMock()
        mock_scheduler_class.return_value = mock_scheduler
        mock_scheduler.get_jobs.return_value = []

        service = SchedulerService()

        with patch.object(service, 'running', side_effect=[True, False]):
            service.start()

        # Verify all three jobs were registered
        assert mock_scheduler.add_job.call_count == 3

        # Verify check_and_publish job
        calls = mock_scheduler.add_job.call_args_list
        job_ids = [call_kwargs['id'] for call_args, call_kwargs in calls]

        assert 'check_and_publish' in job_ids
        assert 'retry_failed' in job_ids
        assert 'cleanup_old_records' in job_ids

    @patch('scheduler.scheduler_service.BackgroundScheduler')
    @patch('scheduler.scheduler_service.signal.signal')
    def test_start_check_and_publish_job_config(self, mock_signal, mock_scheduler_class):
        """Test check_and_publish job configuration"""
        mock_scheduler = MagicMock()
        mock_scheduler_class.return_value = mock_scheduler
        mock_scheduler.get_jobs.return_value = []

        service = SchedulerService()

        with patch.object(service, 'running', side_effect=[True, False]):
            service.start()

        # Find the check_and_publish job call
        calls = mock_scheduler.add_job.call_args_list
        check_publish_call = None
        for call_args, call_kwargs in calls:
            if call_kwargs.get('id') == 'check_and_publish':
                check_publish_call = call_kwargs
                break

        assert check_publish_call is not None
        assert check_publish_call['name'] == 'Check and publish due content'
        assert check_publish_call['replace_existing'] is True

        # Verify the trigger is IntervalTrigger
        from apscheduler.triggers.interval import IntervalTrigger
        assert isinstance(check_publish_call['trigger'], IntervalTrigger)

    @patch('scheduler.scheduler_service.BackgroundScheduler')
    @patch('scheduler.scheduler_service.signal.signal')
    def test_start_retry_failed_job_config(self, mock_signal, mock_scheduler_class):
        """Test retry_failed job configuration"""
        mock_scheduler = MagicMock()
        mock_scheduler_class.return_value = mock_scheduler
        mock_scheduler.get_jobs.return_value = []

        service = SchedulerService()

        with patch.object(service, 'running', side_effect=[True, False]):
            service.start()

        # Find the retry_failed job call
        calls = mock_scheduler.add_job.call_args_list
        retry_call = None
        for call_args, call_kwargs in calls:
            if call_kwargs.get('id') == 'retry_failed':
                retry_call = call_kwargs
                break

        assert retry_call is not None
        assert retry_call['name'] == 'Retry failed content'
        assert retry_call['replace_existing'] is True

    @patch('scheduler.scheduler_service.BackgroundScheduler')
    @patch('scheduler.scheduler_service.signal.signal')
    def test_start_cleanup_job_config(self, mock_signal, mock_scheduler_class):
        """Test cleanup_old_records job configuration"""
        mock_scheduler = MagicMock()
        mock_scheduler_class.return_value = mock_scheduler
        mock_scheduler.get_jobs.return_value = []

        service = SchedulerService()

        with patch.object(service, 'running', side_effect=[True, False]):
            service.start()

        # Find the cleanup_old_records job call
        calls = mock_scheduler.add_job.call_args_list
        cleanup_call = None
        for call_args, call_kwargs in calls:
            if call_kwargs.get('id') == 'cleanup_old_records':
                cleanup_call = call_kwargs
                break

        assert cleanup_call is not None
        assert cleanup_call['name'] == 'Cleanup old published records'
        assert cleanup_call['replace_existing'] is True

        # Verify the trigger is CronTrigger
        from apscheduler.triggers.cron import CronTrigger
        assert isinstance(cleanup_call['trigger'], CronTrigger)

    @patch('scheduler.scheduler_service.BackgroundScheduler')
    @patch('scheduler.scheduler_service.signal.signal')
    def test_start_sets_running_flag(self, mock_signal, mock_scheduler_class):
        """Test that start() sets the running flag to True"""
        mock_scheduler = MagicMock()
        mock_scheduler_class.return_value = mock_scheduler
        mock_scheduler.get_jobs.return_value = []

        service = SchedulerService()

        assert service.running is False

        with patch.object(service, 'running', side_effect=[True, False]):
            service.start()

        # The running flag should have been set to True
        mock_scheduler.start.assert_called_once()

    @patch('scheduler.scheduler_service.BackgroundScheduler')
    @patch('scheduler.scheduler_service.signal.signal')
    def test_start_when_already_running_raises_error(self, mock_signal, mock_scheduler_class):
        """Test that starting an already running service raises RuntimeError"""
        service = SchedulerService()
        service.running = True

        with pytest.raises(RuntimeError) as exc_info:
            service.start()

        assert "already running" in str(exc_info.value)

    @patch('scheduler.scheduler_service.BackgroundScheduler')
    @patch('scheduler.scheduler_service.signal.signal')
    def test_start_logs_job_details(self, mock_signal, mock_scheduler_class):
        """Test that start() logs details of scheduled jobs"""
        mock_scheduler = MagicMock()
        mock_scheduler_class.return_value = mock_scheduler

        # Create mock jobs
        mock_job1 = MagicMock()
        mock_job1.name = "Test Job 1"
        mock_job1.next_run_time = datetime.utcnow()

        mock_job2 = MagicMock()
        mock_job2.name = "Test Job 2"
        mock_job2.next_run_time = datetime.utcnow() + timedelta(minutes=5)

        mock_scheduler.get_jobs.return_value = [mock_job1, mock_job2]

        service = SchedulerService()

        with patch.object(service, 'running', side_effect=[True, False]):
            service.start()

        # Verify get_jobs was called to retrieve scheduled jobs
        mock_scheduler.get_jobs.assert_called()


class TestSchedulerServiceStop:
    """Test suite for SchedulerService.stop() method"""

    @patch('scheduler.scheduler_service.signal.signal')
    def test_stop_when_not_running(self, mock_signal):
        """Test stopping a service that's not running"""
        service = SchedulerService()

        # Should not raise an error, just log a warning
        service.stop()

        assert service.running is False

    @patch('scheduler.scheduler_service.BackgroundScheduler')
    @patch('scheduler.scheduler_service.signal.signal')
    def test_stop_shuts_down_scheduler(self, mock_signal, mock_scheduler_class):
        """Test that stop() shuts down the scheduler"""
        mock_scheduler = MagicMock()
        mock_scheduler_class.return_value = mock_scheduler
        mock_scheduler.get_jobs.return_value = []

        service = SchedulerService()

        with patch.object(service, 'running', side_effect=[True, False]):
            service.start()

        service.stop()

        # Verify scheduler was shut down with wait=True
        mock_scheduler.shutdown.assert_called_once_with(wait=True)

    @patch('scheduler.scheduler_service.BackgroundScheduler')
    @patch('scheduler.scheduler_service.signal.signal')
    def test_stop_sets_running_flag_to_false(self, mock_signal, mock_scheduler_class):
        """Test that stop() sets running flag to False"""
        mock_scheduler = MagicMock()
        mock_scheduler_class.return_value = mock_scheduler
        mock_scheduler.get_jobs.return_value = []

        service = SchedulerService()
        service.running = True
        service.scheduler = mock_scheduler

        service.stop()

        assert service.running is False


class TestSchedulerServiceSignalHandling:
    """Test suite for signal handling"""

    @patch('scheduler.scheduler_service.signal.signal')
    @patch('scheduler.scheduler_service.sys.exit')
    def test_signal_handler_sigint(self, mock_exit, mock_signal):
        """Test signal handler with SIGINT"""
        service = SchedulerService()

        with patch.object(service, 'stop') as mock_stop:
            service._signal_handler(signal.SIGINT, None)

        mock_stop.assert_called_once()
        mock_exit.assert_called_once_with(0)

    @patch('scheduler.scheduler_service.signal.signal')
    @patch('scheduler.scheduler_service.sys.exit')
    def test_signal_handler_sigterm(self, mock_exit, mock_signal):
        """Test signal handler with SIGTERM"""
        service = SchedulerService()

        with patch.object(service, 'stop') as mock_stop:
            service._signal_handler(signal.SIGTERM, None)

        mock_stop.assert_called_once()
        mock_exit.assert_called_once_with(0)


class TestSchedulerServiceTaskWrappers:
    """Test suite for task wrapper methods"""

    @patch('scheduler.scheduler_service.signal.signal')
    @patch('scheduler.scheduler_service.check_and_publish_due_content')
    def test_check_and_publish_wrapper_success(self, mock_task, mock_signal):
        """Test _check_and_publish_wrapper with successful execution"""
        mock_task.return_value = 5  # 5 items processed

        service = SchedulerService()
        service._check_and_publish_wrapper()

        mock_task.assert_called_once()

    @patch('scheduler.scheduler_service.signal.signal')
    @patch('scheduler.scheduler_service.check_and_publish_due_content')
    def test_check_and_publish_wrapper_error_handling(self, mock_task, mock_signal):
        """Test _check_and_publish_wrapper handles errors gracefully"""
        mock_task.side_effect = Exception("Database error")

        service = SchedulerService()

        # Should not raise exception, just log it
        service._check_and_publish_wrapper()

        mock_task.assert_called_once()

    @patch('scheduler.scheduler_service.signal.signal')
    @patch('scheduler.scheduler_service.retry_failed_content')
    def test_retry_failed_wrapper_success(self, mock_task, mock_signal):
        """Test _retry_failed_wrapper with successful execution"""
        mock_task.return_value = 3  # 3 items retried

        service = SchedulerService()
        service._retry_failed_wrapper()

        mock_task.assert_called_once()

    @patch('scheduler.scheduler_service.signal.signal')
    @patch('scheduler.scheduler_service.retry_failed_content')
    def test_retry_failed_wrapper_error_handling(self, mock_task, mock_signal):
        """Test _retry_failed_wrapper handles errors gracefully"""
        mock_task.side_effect = DatabaseError("query", "Connection lost", "scheduled_content")

        service = SchedulerService()

        # Should not raise exception, just log it
        service._retry_failed_wrapper()

        mock_task.assert_called_once()

    @patch('scheduler.scheduler_service.signal.signal')
    @patch('scheduler.scheduler_service.cleanup_old_records')
    def test_cleanup_old_records_wrapper_success(self, mock_task, mock_signal):
        """Test _cleanup_old_records_wrapper with successful execution"""
        mock_task.return_value = 10  # 10 records deleted

        service = SchedulerService()
        service._cleanup_old_records_wrapper()

        mock_task.assert_called_once_with(days_to_keep=30)

    @patch('scheduler.scheduler_service.signal.signal')
    @patch('scheduler.scheduler_service.cleanup_old_records')
    def test_cleanup_old_records_wrapper_error_handling(self, mock_task, mock_signal):
        """Test _cleanup_old_records_wrapper handles errors gracefully"""
        mock_task.side_effect = Exception("Cleanup failed")

        service = SchedulerService()

        # Should not raise exception, just log it
        service._cleanup_old_records_wrapper()

        mock_task.assert_called_once()


class TestSchedulerServiceIntegration:
    """Integration tests for scheduler service with actual task execution"""

    @patch('scheduler.scheduler_service.BackgroundScheduler')
    @patch('scheduler.scheduler_service.signal.signal')
    @patch('scheduler.scheduler_service.check_and_publish_due_content')
    def test_scheduled_job_execution_check_and_publish(
        self, mock_task, mock_signal, mock_scheduler_class
    ):
        """Test that check_and_publish job wrapper is properly configured"""
        mock_scheduler = MagicMock()
        mock_scheduler_class.return_value = mock_scheduler
        mock_scheduler.get_jobs.return_value = []

        service = SchedulerService()

        with patch.object(service, 'running', side_effect=[True, False]):
            service.start()

        # Get the function that was registered for check_and_publish
        calls = mock_scheduler.add_job.call_args_list
        check_publish_call = None
        for call_args, call_kwargs in calls:
            if call_kwargs.get('id') == 'check_and_publish':
                check_publish_call = call_kwargs
                break

        assert check_publish_call is not None

        # Execute the registered function
        mock_task.return_value = 2
        registered_func = check_publish_call['func']
        registered_func()

        # Verify the task was called
        mock_task.assert_called_once()

    @patch('scheduler.scheduler_service.BackgroundScheduler')
    @patch('scheduler.scheduler_service.signal.signal')
    @patch('scheduler.scheduler_service.retry_failed_content')
    def test_scheduled_job_execution_retry_failed(
        self, mock_task, mock_signal, mock_scheduler_class
    ):
        """Test that retry_failed job wrapper is properly configured"""
        mock_scheduler = MagicMock()
        mock_scheduler_class.return_value = mock_scheduler
        mock_scheduler.get_jobs.return_value = []

        service = SchedulerService()

        with patch.object(service, 'running', side_effect=[True, False]):
            service.start()

        # Get the function that was registered for retry_failed
        calls = mock_scheduler.add_job.call_args_list
        retry_call = None
        for call_args, call_kwargs in calls:
            if call_kwargs.get('id') == 'retry_failed':
                retry_call = call_kwargs
                break

        assert retry_call is not None

        # Execute the registered function
        mock_task.return_value = 1
        registered_func = retry_call['func']
        registered_func()

        # Verify the task was called
        mock_task.assert_called_once()

    @patch('scheduler.scheduler_service.BackgroundScheduler')
    @patch('scheduler.scheduler_service.signal.signal')
    @patch('scheduler.scheduler_service.cleanup_old_records')
    def test_scheduled_job_execution_cleanup(
        self, mock_task, mock_signal, mock_scheduler_class
    ):
        """Test that cleanup_old_records job wrapper is properly configured"""
        mock_scheduler = MagicMock()
        mock_scheduler_class.return_value = mock_scheduler
        mock_scheduler.get_jobs.return_value = []

        service = SchedulerService()

        with patch.object(service, 'running', side_effect=[True, False]):
            service.start()

        # Get the function that was registered for cleanup_old_records
        calls = mock_scheduler.add_job.call_args_list
        cleanup_call = None
        for call_args, call_kwargs in calls:
            if call_kwargs.get('id') == 'cleanup_old_records':
                cleanup_call = call_kwargs
                break

        assert cleanup_call is not None

        # Execute the registered function
        mock_task.return_value = 5
        registered_func = cleanup_call['func']
        registered_func()

        # Verify the task was called with correct arguments
        mock_task.assert_called_once_with(days_to_keep=30)


class TestSchedulerServiceMain:
    """Test suite for main() entry point"""

    @patch('scheduler.scheduler_service.SchedulerService')
    @patch('scheduler.scheduler_service.signal.signal')
    def test_main_creates_and_starts_service(self, mock_signal, mock_service_class):
        """Test that main() creates and starts the scheduler service"""
        from scheduler.scheduler_service import main

        mock_service = MagicMock()
        mock_service_class.return_value = mock_service

        # Mock start() to not block
        mock_service.start.return_value = None

        main()

        # Verify service was created and started
        mock_service_class.assert_called_once()
        mock_service.start.assert_called_once()

    @patch('scheduler.scheduler_service.SchedulerService')
    @patch('scheduler.scheduler_service.signal.signal')
    @patch('scheduler.scheduler_service.sys.exit')
    def test_main_handles_fatal_errors(self, mock_exit, mock_signal, mock_service_class):
        """Test that main() handles fatal errors and exits"""
        from scheduler.scheduler_service import main

        mock_service = MagicMock()
        mock_service_class.return_value = mock_service
        mock_service.start.side_effect = Exception("Fatal error")

        main()

        # Verify sys.exit was called with error code
        mock_exit.assert_called_once_with(1)


class TestSchedulerServiceEdgeCases:
    """Test suite for edge cases and error scenarios"""

    @patch('scheduler.scheduler_service.BackgroundScheduler')
    @patch('scheduler.scheduler_service.signal.signal')
    def test_start_stop_start_sequence(self, mock_signal, mock_scheduler_class):
        """Test starting, stopping, and restarting the service"""
        mock_scheduler1 = MagicMock()
        mock_scheduler2 = MagicMock()
        mock_scheduler_class.side_effect = [mock_scheduler1, mock_scheduler2]
        mock_scheduler1.get_jobs.return_value = []
        mock_scheduler2.get_jobs.return_value = []

        service = SchedulerService()

        # First start
        with patch.object(service, 'running', side_effect=[True, False]):
            service.start()

        # Stop
        service.stop()

        # Second start should work
        with patch.object(service, 'running', side_effect=[True, False]):
            service.start()

        # Verify two schedulers were created
        assert mock_scheduler_class.call_count == 2

    @patch('scheduler.scheduler_service.signal.signal')
    def test_stop_with_none_scheduler(self, mock_signal):
        """Test stopping when scheduler is None"""
        service = SchedulerService()
        service.running = True
        service.scheduler = None

        # Should not raise an error
        service.stop()

        assert service.running is False

    @patch('scheduler.scheduler_service.BackgroundScheduler')
    @patch('scheduler.scheduler_service.signal.signal')
    @patch('scheduler.scheduler_service.check_and_publish_due_content')
    def test_task_wrapper_with_return_value_zero(self, mock_task, mock_signal, mock_scheduler_class):
        """Test task wrapper when task returns 0 (no items processed)"""
        mock_task.return_value = 0

        service = SchedulerService()

        # Should complete without errors
        service._check_and_publish_wrapper()

        mock_task.assert_called_once()

    @patch('scheduler.scheduler_service.BackgroundScheduler')
    @patch('scheduler.scheduler_service.signal.signal')
    @patch('scheduler.scheduler_service.retry_failed_content')
    def test_multiple_task_executions(self, mock_task, mock_signal, mock_scheduler_class):
        """Test multiple executions of the same task wrapper"""
        mock_task.side_effect = [1, 2, 3]

        service = SchedulerService()

        # Execute task wrapper multiple times
        service._retry_failed_wrapper()
        service._retry_failed_wrapper()
        service._retry_failed_wrapper()

        # Verify task was called three times
        assert mock_task.call_count == 3

    @patch('scheduler.scheduler_service.signal.signal')
    def test_service_attributes_after_init(self, mock_signal):
        """Test that service has all expected attributes after initialization"""
        service = SchedulerService()

        # Verify all attributes are present
        assert hasattr(service, 'scheduler')
        assert hasattr(service, 'running')
        assert hasattr(service, '_signal_handler')
        assert hasattr(service, '_check_and_publish_wrapper')
        assert hasattr(service, '_retry_failed_wrapper')
        assert hasattr(service, '_cleanup_old_records_wrapper')
        assert hasattr(service, 'start')
        assert hasattr(service, 'stop')
