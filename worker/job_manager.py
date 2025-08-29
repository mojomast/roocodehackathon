"""
Job Manager Module

This module provides the JobManager class that handles the lifecycle
and state management of documentation jobs.
"""

import logging
from typing import Optional
from datetime import datetime


class JobManager:
    """
    Manages the lifecycle and state of documentation generation jobs.

    This class handles job status updates, error handling, and
    coordination between different stages of the documentation process.
    """

    def __init__(self, db_session, job):
        """
        Initialize JobManager with database session and job instance.

        Args:
            db_session: SQLAlchemy database session
            job: Job model instance
        """
        self.db = db_session
        self.job = job
        self.logger = logging.getLogger(__name__)

    def start_job(self) -> bool:
        """
        Mark the job as started and update relevant fields.

        Returns:
            bool: True if successfully started, False otherwise
        """
        try:
            self.logger.info(f"Starting job {self.job.id}")
            self.job.status = 'running'
            self.job.updated_at = datetime.utcnow()
            self.db.commit()
            return True
        except Exception as e:
            self.logger.error(f"Failed to start job {self.job.id}: {e}")
            self.db.rollback()
            return False

    def complete_job(self) -> bool:
        """
        Mark the job as completed successfully and update relevant fields.

        Returns:
            bool: True if successfully completed, False otherwise
        """
        try:
            self.logger.info(f"Completing job {self.job.id}")
            self.job.status = 'completed'
            self.job.updated_at = datetime.utcnow()
            self.db.commit()
            return True
        except Exception as e:
            self.logger.error(f"Failed to complete job {self.job.id}: {e}")
            self.db.rollback()
            return False

    def fail_job(self, error_message: str) -> bool:
        """
        Mark the job as failed with the provided error message.

        Args:
            error_message (str): Description of the error that occurred

        Returns:
            bool: True if successfully marked as failed, False otherwise
        """
        try:
            self.logger.error(f"Failing job {self.job.id} with error: {error_message}")
            self.job.status = 'failed'
            self.job.updated_at = datetime.utcnow()
            # TODO: Add error_message field to Job model if needed for persistence
            self.db.commit()
            return True
        except Exception as e:
            self.logger.error(f"Failed to mark job {self.job.id} as failed: {e}")
            self.db.rollback()
            return False

    def update_progress(self, progress: Optional[int] = None) -> bool:
        """
        Update job progress (optional additional functionality).

        Args:
            progress (Optional[int]): Progress percentage (0-100)

        Returns:
            bool: True if successfully updated, False otherwise
        """
        try:
            if progress is not None:
                self.logger.info(f"Job {self.job.id} progress: {progress}%")
                # TODO: Add progress field to Job model if needed
                self.job.updated_at = datetime.utcnow()
                self.db.commit()
            return True
        except Exception as e:
            self.logger.error(f"Failed to update progress for job {self.job.id}: {e}")
            self.db.rollback()
            return False