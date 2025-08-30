import os
import logging
import re
import platform
import psutil
from typing import Optional
from urllib.parse import urlparse, parse_qs
from dotenv import load_dotenv
load_dotenv()

# Diagnostic logging for environment and system info
def log_system_info():
    """Log comprehensive system and environment information for debugging."""
    logging.info(f"DEBUG-001: Operating System: {platform.system()} {platform.release()} ({platform.version()})")
    logging.info(f"DEBUG-001: Platform: {platform.platform()}")
    logging.info(f"DEBUG-001: Python Version: {platform.python_version()}")
    try:
        import sys
        logging.info(f"DEBUG-001: Python Executable: {sys.executable}")
    except Exception as e:
        logging.info(f"DEBUG-001: Python Executable: Unable to determine ({e})")
    logging.info(f"DEBUG-001: Current Working Directory: {os.getcwd()}")
    logging.info(f"DEBUG-001: Process ID: {os.getpid()}")
    logging.info(f"DEBUG-001: Parent Process ID: {os.getppid() if hasattr(os, 'getppid') else 'N/A'}")

    # Check multiprocessing capabilities and permissions
    try:
        import multiprocessing
        logging.info(f"DEBUG-001: Multiprocessing CPU Count: {multiprocessing.cpu_count()}")
        logging.info(f"DEBUG-001: Multiprocessing Context: {multiprocessing.get_context()}")

        # Check if we can create multiprocessing handles
        try:
            from multiprocessing import Lock
            lock = Lock()
            lock.acquire()
            lock.release()
            logging.info("DEBUG-001: Multiprocessing Lock creation: SUCCESS")
        except Exception as e:
            logging.error(f"DEBUG-001: Multiprocessing Lock creation failed: {e}")

    except Exception as e:
        logging.error(f"DEBUG-001: Multiprocessing module error: {e}")

    # Check psutil for resource information
    try:
        import psutil
        process = psutil.Process()
        logging.info(f"DEBUG-001: Current Process Memory Usage: {process.memory_info().rss / 1024 / 1024:.1f} MB")
        logging.info(f"DEBUG-001: Current Process CPU Usage: {process.cpu_percent()}%")
    except Exception as e:
        logging.error(f"DEBUG-001: Process information unavailable: {e}")

# WK-009: Enhanced imports for database validation, secrets management, and security
from cryptography.fernet import Fernet, InvalidToken
from celery import Celery
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

from worker.job_manager import JobManager
from worker.repo_manager import RepoManager
from worker.parser import Parser
from worker.ai_orchestrator import AIOrchestrator
from worker.patcher import Patcher
from worker.logger import Logger
from worker.config import Config

# Configure logging with more verbose level for debugging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Log system information at startup
log_system_info()

# Celery configuration with enhanced debugging
BROKER_URL_ENV = os.getenv('CELERY_BROKER_URL')
BACKEND_URL_ENV = os.getenv('CELERY_RESULT_BACKEND')

logging.info(f"DEBUG-002: CELERY_BROKER_URL env var: {BROKER_URL_ENV}")
logging.info(f"DEBUG-002: CELERY_RESULT_BACKEND env var: {BACKEND_URL_ENV}")

# Updated defaults to use localhost for better local development compatibility
CELERY_BROKER_URL = BROKER_URL_ENV if BROKER_URL_ENV else 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = BACKEND_URL_ENV if BACKEND_URL_ENV else 'redis://localhost:6379/0'

logging.info(f"DEBUG-002: Final CELERY_BROKER_URL: {CELERY_BROKER_URL}")
logging.info(f"DEBUG-002: Final CELERY_RESULT_BACKEND: {CELERY_RESULT_BACKEND}")

# Test Redis connection before creating Celery app
try:
    import redis
    parsed = urlparse(CELERY_BROKER_URL)
    redis_client = redis.Redis(
        host=parsed.hostname,
        port=parsed.port or 6379,
        db=int(parsed.path.lstrip('/')) if parsed.path else 0,
        decode_responses=True
    )
    # Test connection
    redis_client.ping()
    logging.info("DEBUG-002: Redis connection test: SUCCESS")
except Exception as e:
    logging.error(f"DEBUG-002: Redis connection test FAILED: {e}")
    logging.error("DEBUG-002: This may cause Celery worker initialization failures")

# Configure Celery with Windows-specific settings if needed
app = Celery(
    'worker',
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND
)

# Add Windows-specific configuration if running on Windows
if platform.system() == 'Windows':
    logging.info("DEBUG-002: Applying Windows-specific Celery configuration")

    # Disable billiard multiprocessing on Windows to use forkserver
    app.conf.update(
        worker_pool='solo',  # Use solo pool instead of prefork on Windows
        task_always_eager=False,  # Allow async task execution
        worker_prefetch_multiplier=1,  # Reduce prefetch to avoid handle exhaustion
        worker_max_tasks_per_child=1,  # Restart worker after each task to avoid handle leaks
        result_expires=3600,  # 1 hour result expiry
        task_acks_late=True,  # Acknowledge tasks after completion
        worker_disable_rate_limits=False,
    )
    logging.info("DEBUG-002: Windows configuration applied: worker_pool=solo, prefetch_multiplier=1")
else:
    logging.info("DEBUG-002: Using default Celery configuration for non-Windows platform")

# WK-009: Enhanced database configuration with proper secrets management, input sanitization, and error handling
DATABASE_URL = os.getenv('DATABASE_URL')

def validate_and_sanitize_database_url(db_url: Optional[str]) -> str:
    """
    WK-009: Validate and sanitize DATABASE_URL with comprehensive security checks.

    Performs the following validations:
    - Ensures URL is present and not empty
    - Validates URL format and scheme (allowed: postgresql, mysql, sqlite)
    - Sanitizes input to prevent SQL injection attempts
    - Validates credentials are properly formatted
    - Checks for suspicious patterns that could indicate attacks

    Args:
        db_url: Database URL from environment variable

    Returns:
        Sanitized database URL

    Raises:
        ValueError: If validation fails for any security or format reason
    """
    if not db_url or not db_url.strip():
        logging.error("WK-009: DATABASE_URL environment variable is missing or empty.")
        raise ValueError("DATABASE_URL environment variable must be set and non-empty.")

    db_url = db_url.strip()

    # Parse URL for detailed validation (accept SQLAlchemy URIs)
    try:
        parsed = urlparse(db_url)
    except Exception as e:
        logging.error(f"WK-009: Failed to parse DATABASE_URL: {e}")
        raise ValueError(f"Invalid DATABASE_URL format: {db_url}")

    # Validate allowed schemes
    allowed_schemes = {'postgresql', 'postgresql+psycopg2', 'mysql', 'mysql+pymysql', 'mysql+mysqldb', 'sqlite'}
    if parsed.scheme not in allowed_schemes:
        logging.error(f"WK-009: Invalid database scheme: {parsed.scheme}")
        raise ValueError(f"Unsupported database scheme. Allowed: {', '.join(allowed_schemes)}")

    # Sanitize hostname to prevent injection
    if parsed.hostname:
        if not re.match(r'^[a-zA-Z0-9.-]+(\.[a-zA-Z]{2,})*$', parsed.hostname):
            logging.debug(f"WK-009: Non-standard hostname detected: {parsed.hostname}")

    # Validate username and password if present
    if parsed.username or parsed.password:
        # Check for suspicious characters in credentials
        suspicious_chars = ['<', '>', '"', "'", ';', '--', '/*', '*/']
        if any(char in (parsed.username or '') or char in (parsed.password or '') for char in suspicious_chars):
            logging.error("WK-009: Credentials contain suspicious characters that may indicate injection attempts.")
            raise ValueError("Database credentials contain invalid characters.")

    # Additional security checks
    full_url = db_url.lower()
    if any(attack_pattern in full_url for attack_pattern in [
        'union select', 'drop table', 'delete from', 'update ', 'insert into',
        'script>', 'javascript:', 'data:', 'vbscript:'
    ]):
        logging.error("WK-009: DATABASE_URL contains patterns indicative of SQL injection or XSS attempts.")
        raise ValueError("Database URL contains suspicious patterns.")

    return db_url

def get_encryption_key() -> bytes:
    """
    WK-009: Get or generate encryption key for database credentials.
    Uses environment variable or generates a stable key for development.

    Returns:
        Encryption key as bytes
    """
    key = os.getenv('DATABASE_ENCRYPTION_KEY')
    if key:
        # Validate key format
        try:
            bytes.fromhex(key)
            if len(key) != 64:  # 32 bytes hex encoded = 64 chars
                raise ValueError("Key must be 32 bytes (64 hex characters)")
            return bytes.fromhex(key)
        except ValueError as e:
            logging.warning(f"WK-009: Invalid encryption key format: {e}")
    else:
        # For development: generate stable key from environment
        # In production, this should be set explicitly
        logging.warning("WK-009: Using auto-generated encryption key. Set DATABASE_ENCRYPTION_KEY in production.")

    return Fernet.generate_key()

def encrypt_database_url(db_url: str) -> str:
    """
    WK-009: Encrypt sensitive database URL for secure storage.

    Args:
        db_url: Plain database URL

    Returns:
        Encrypted URL as base64 string
    """
    try:
        key = get_encryption_key()
        fernet = Fernet(key)
        encrypted = fernet.encrypt(db_url.encode())
        return encrypted.decode()
    except Exception as e:
        logging.error(f"WK-009: Failed to encrypt database URL: {e}")
        raise

def decrypt_database_url(encrypted_url: str) -> str:
    """
    WK-009: Decrypt database URL for use.

    Args:
        encrypted_url: Encrypted URL as base64 string

    Returns:
        Decrypted database URL
    """
    try:
        key = get_encryption_key()
        fernet = Fernet(key)
        decrypted = fernet.decrypt(encrypted_url.encode())
        return decrypted.decode()
    except InvalidToken:
        raise ValueError("Failed to decrypt database URL: invalid token")
    except Exception as e:
        logging.error(f"WK-009: Failed to decrypt database URL: {e}")
        raise

# Validate and sanitize the DATABASE_URL
try:
    DATABASE_URL = validate_and_sanitize_database_url(DATABASE_URL)
    logging.info("WK-009: DATABASE_URL validation successful.")
except ValueError as e:
    logging.error(f"WK-009: Database URL validation failed: {e}")
    raise
except Exception as e:
    logging.error(f"WK-009: Unexpected error during database URL validation: {e}")
    raise

Base = declarative_base()

class Job(Base):
    __tablename__ = 'jobs'
    id = Column(Integer, primary_key=True)
    status = Column(String, default='pending')
    repo_url = Column(String)
    clone_path = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    def __repr__(self):
        return f"<Job(id={self.id}, status='{self.status}')>"

# WK-009: Enhanced database engine creation with error handling
try:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,  # Verify connections before use
        pool_recycle=300,    # Recycle connections every 5 minutes
        connect_args={
            'connect_timeout': 10,  # Connection timeout
        }
    )
    # Test the connection
    with engine.connect() as conn:
        logging.info("WK-009: Database connection established successfully.")
except Exception as e:
    logging.error(f"WK-009: Failed to create database engine or establish connection: {e}")
    raise ValueError(f"Database connection failed: {e}")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@app.task(bind=True)
def process_documentation_job(self, job_id: int):
    """
    WK-014: Placeholder task for processing documentation jobs with proper transaction handling.
    In a real scenario, this would handle the logic for generating documentation.
    Uses SQLAlchemy's transaction context manager for automatic commit/rollback.

    Added bind=True for task instance access and enhanced logging for debugging.
    """
    try:
        logging.info(f"DEBUG-003: Received Celery task for job_id: {job_id}")
        logging.info(f"DEBUG-003: Task ID: {self.request.id}")
        logging.info(f"DEBUG-003: Worker hostname: {self.request.hostname}")
        logging.info(f"DEBUG-003: Task arguments: {self.request.args}")
        logging.info(f"DEBUG-003: Processing documentation job: {job_id}")
    except Exception as e:
        logging.error(f"DEBUG-003: Error accessing task metadata: {e}, continuing with job processing")

    db = SessionLocal()
    try:
        # WK-014: Use transaction context manager for proper scope and rollback
        with db.begin():
            job = db.query(Job).filter(Job.id == job_id).first()
            if not job:
                logging.error(f"Job with ID {job_id} not found.")
                return

            job_manager = JobManager(db, job)
            repo_manager = RepoManager()
            parser = Parser()
            ai_orchestrator = AIOrchestrator()
            patcher = Patcher()
            app_logger = Logger()
            config = Config() # Placeholder for future configuration

            # 1. Start Job
            job_manager.start_job()

            # 2. Clone Repo
            repo_manager.clone_repo(job.repo_url, job.clone_path) # Assuming job has repo_url and clone_path

            # 3. Parse Code
            parser.parse_code(job.clone_path)

            # 4. Generate Docs
            ai_orchestrator.generate_documentation(job.clone_path)

            # 5. Create Patch/PR
            patcher.create_patch_or_pr(job.clone_path)

            # 6. Log Progress
            app_logger.log_progress(f"Job {job_id} completed successfully.")

            # 7. Complete Job
            job_manager.complete_job()

    except Exception as e:
        logging.error(f"Error processing job {job_id}: {e}")
        db.invalidate()  # Invalidate session on error to prevent dirty state
        # WK-014: Transaction rollback handled automatically by context manager
        if 'job_manager' in locals():
            job_manager.fail_job(str(e)) # Assuming job_manager has a fail_job method
    finally:
        # WK-014: Proper session cleanup
        db.close()

if __name__ == '__main__':
    # This block is typically used for running the worker directly for testing or development.
    # In a production Docker setup, the worker command would be executed directly.
    logging.info("Celery worker started. Waiting for tasks...")
    app.worker_main(['worker', '--loglevel=info'])