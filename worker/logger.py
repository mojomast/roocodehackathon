"""
Logger Module

This module provides the Logger class for centralized logging
and progress tracking in the documentation generation system.
"""

import logging
import logging.handlers
from typing import Optional, Dict
import os


class Logger:
    """
    Centralized logging and progress tracking for documentation generation.

    This class provides structured logging with different levels,
    progress tracking capabilities, and integration with external monitoring systems.
    """

    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize Logger with configuration.

        Args:
            config (Optional[Dict]): Configuration for logging including file paths, formats, etc.
        """
        self.config = config or {}
        self.log_level = self.config.get('level', 'INFO').upper()
        self.log_file = self.config.get('log_file', 'worker.log')
        self.log_format = self.config.get('format',
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        # Create logger
        self.logger = logging.getLogger('DocGenerator')
        self.logger.setLevel(getattr(logging, self.log_level, logging.INFO))

        # Remove existing handlers to avoid duplicates
        self.logger.handlers = []

        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(self.logger.level)
        console_formatter = logging.Formatter(self.log_format)
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)

        # Create file handler if specified
        if self.log_file:
            self._setup_file_handler()

        # Progress tracking
        self.progress_logs = []
        self.max_progress_logs = self.config.get('max_progress_logs', 100)

    def _setup_file_handler(self):
        """Set up file handler for persistent logging."""
        try:
            # Create log directory if it doesn't exist
            log_dir = os.path.dirname(self.log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir)

            # Rotating file handler
            file_handler = logging.handlers.RotatingFileHandler(
                self.log_file,
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5
            )
            file_handler.setLevel(self.logger.level)

            formatter = logging.Formatter(self.log_format)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

        except Exception as e:
            print(f"Warning: Failed to setup file logging: {e}")

    def log_progress(self, message: str, progress: Optional[int] = None) -> None:
        """
        Log progress information with optional progress percentage.

        This method tracks and logs progress information for long-running
        operations, storing the log entries for potential monitoring.

        Args:
            message (str): Progress message to log
            progress (Optional[int]): Progress percentage (0-100)
        """
        try:
            log_message = message
            if progress is not None:
                log_message = f"[Progress: {progress}%] {message}"

            self.logger.info(log_message)

            # Store progress log entry
            progress_entry = {
                'timestamp': self._get_current_timestamp(),
                'message': message,
                'progress': progress
            }

            self.progress_logs.append(progress_entry)

            # Limit the number of stored progress logs
            if len(self.progress_logs) > self.max_progress_logs:
                self.progress_logs = self.progress_logs[-self.max_progress_logs:]

        except Exception as e:
            print(f"Warning: Failed to log progress: {e}")

    def get_progress_history(self) -> list:
        """
        Get the history of progress logs.

        Returns:
            list: List of progress log entries
        """
        return self.progress_logs.copy()

    def clear_progress_history(self) -> None:
        """Clear the progress history."""
        self.progress_logs.clear()
        self.logger.info("Progress history cleared")

    def log_job_start(self, job_id: str) -> None:
        """
        Log the start of a job.

        Args:
            job_id (str): ID of the job starting
        """
        self.log_progress(f"Job {job_id} started", 0)
        self.logger.info(f"=== Job {job_id} Started ===")

    def log_job_complete(self, job_id: str) -> None:
        """
        Log the completion of a job.

        Args:
            job_id (str): ID of the job completing
        """
        self.log_progress(f"Job {job_id} completed successfully", 100)
        self.logger.info(f"✓ Job {job_id} Completed")

    def log_job_error(self, job_id: str, error: str) -> None:
        """
        Log an error in a job.

        Args:
            job_id (str): ID of the job with error
            error (str): Error description
        """
        self.logger.error(f"✗ Job {job_id} failed: {error}")

    def log_stage(self, stage_name: str, job_id: str = None) -> None:
        """
        Log the start of a processing stage.

        Args:
            stage_name (str): Name of the processing stage
            job_id (str, optional): Associated job ID
        """
        prefix = f"Job {job_id}: " if job_id else ""
        self.logger.info(f"{prefix}--- {stage_name} ---")

    def set_log_level(self, level: str) -> None:
        """
        Set the logging level.

        Args:
            level (str): New logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        try:
            numeric_level = getattr(logging, level.upper(), None)
            if numeric_level is None:
                raise ValueError(f"Invalid log level: {level}")

            self.logger.setLevel(numeric_level)
            for handler in self.logger.handlers:
                handler.setLevel(numeric_level)

            self.logger.info(f"Log level changed to {level.upper()}")

        except Exception as e:
            print(f"Error setting log level: {e}")

    def _get_current_timestamp(self) -> str:
        """Get current timestamp as string."""
        from datetime import datetime
        return datetime.utcnow().isoformat()

    def get_logger(self):
        """
        Get the underlying logger instance for advanced use cases.

        Returns:
            logging.Logger: The configured logger instance
        """
        return self.logger