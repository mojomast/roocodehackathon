import pytest
import tempfile
import os
import stat
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import shutil

from worker.worker import process_documentation_job
from worker.job_manager import JobManager
from worker.config import Config
from worker.logger import Logger
from worker.parser import Parser
from worker.ai_orchestrator import AIOrchestrator
from worker.patcher import Patcher
from worker.repo_manager import RepoManager

# Test database setup
TEST_DATABASE_URL = "sqlite:///./test_worker.db"

@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Create tables for testing."""
    from worker.worker import Base
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def mock_session():
    """Create mock database session."""
    mock_session = Mock()
    return mock_session

@pytest.fixture
def mock_job():
    """Create mock job object."""
    mock_job = Mock()
    mock_job.id = 1
    mock_job.status = "pending"
    mock_job.repo_url = "https://github.com/test/repo"
    mock_job.clone_path = "/tmp/test_repo"
    return mock_job

@pytest.fixture
def sample_config():
    """Sample configuration for tests."""
    return {
        'temp_dir': '/tmp/test_repos',
        'git_command': 'git',
        'log_level': 'INFO'
    }

# Unit tests for individual components

def test_config_validation():
    """Test config validation."""
    config = Config()
    # Test with missing DATABASE_URL
    assert not config.validate_required()
    # Test with DATABASE_URL present
    config.set('database_url', TEST_DATABASE_URL)
    assert config.validate_required()

def test_config_validation_empty_values():
    """Test config validation with empty values."""
    config = Config()
    config.set('database_url', '')  # Empty string should fail
    assert not config.validate_required()

    config.set('database_url', None)  # None should fail
    assert not config.validate_required()

def test_config_validation_invalid_urls():
    """Test config validation with invalid database URLs."""
    config = Config()
    invalid_urls = [
        'not-a-url',
        'invalid://scheme',
        'postgresql://user:password@host/database',  # Missing port
        '',  # Empty
        None  # None
    ]

    for invalid_url in invalid_urls:
        config.set('database_url', invalid_url)
        assert not config.validate_required() or (config.get('database_url') != invalid_url and config.get('database_url') is None)

def test_logger_initialization(sample_config):
    """Test logger initialization."""
    logger = Logger(sample_config)
    assert logger is not None
    assert len(logger.get_progress_history()) == 0

def test_logger_initialization_default_config():
    """Test logger initialization with no config."""
    logger = Logger()
    assert logger is not None
    assert len(logger.get_progress_history()) == 0
    assert logger.log_level == 'INFO'

def test_logger_progress_tracking(sample_config):
    """Test progress tracking."""
    logger = Logger(sample_config)
    logger.log_progress("Starting test", 10)
    history = logger.get_progress_history()
    assert len(history) == 1
    assert history[0]['message'] == "Starting test"
    assert history[0]['progress'] == 10

def test_logger_progress_tracking_without_percentage():
    """Test progress logging without percentage."""
    logger = Logger()
    logger.log_progress("Starting operation")
    history = logger.get_progress_history()
    assert len(history) == 1
    assert history[0]['message'] == "Starting operation"
    assert history[0]['progress'] is None

def test_logger_progress_history_rotation():
    """Test progress history rotation when maximum is exceeded."""
    config = {'max_progress_logs': 3}
    logger = Logger(config)

    # Add 5 progress entries
    for i in range(5):
        logger.log_progress(f"Step {i}", i * 20)

    history = logger.get_progress_history()
    assert len(history) == 3  # Should be capped at max
    assert history[0]['message'] == "Step 2"  # Should contain the last 3
    assert history[2]['message'] == "Step 4"

def test_logger_clear_progress_history():
    """Test clearing progress history."""
    logger = Logger()
    logger.log_progress("Step 1")
    logger.log_progress("Step 2")
    assert len(logger.get_progress_history()) == 2

    logger.clear_progress_history()
    assert len(logger.get_progress_history()) == 0

def test_logger_log_level_change():
    """Test changing log level."""
    logger = Logger()

    # Test changing to DEBUG
    logger.set_log_level('DEBUG')
    assert logger.logger.level == 10  # DEBUG level

    # Test changing to ERROR
    logger.set_log_level('ERROR')
    assert logger.logger.level == 40  # ERROR level

    # Test invalid log level
    with pytest.raises(ValueError):
        logger.set_log_level('INVALID')

def test_logger_file_logging_error_handling():
    """Test logger error handling when file logging fails."""
    config = {'log_file': '/invalid/path/that/does/not/exist/log.txt'}
    logger = Logger(config)
    # Should not raise exception, just log warning
    logger.log_progress("Test message")
    # File handler should not be added if path creation fails
    assert len(logger.logger.handlers) == 2  # Console + no file handler

def test_logger_missing_permissions_error():
    """Test logger with file that has no write permissions."""
    with tempfile.TemporaryDirectory() as temp_dir:
        log_file = os.path.join(temp_dir, 'readonly.log')
        # Create file and remove write permissions
        with open(log_file, 'w') as f:
            f.write('test')
        os.chmod(log_file, stat.S_IRUSR)  # Read-only

        config = {'log_file': log_file}
        logger = Logger(config)
        # Should handle permission error gracefully
        logger.log_progress("Test message")

def test_parser_initialization():
    """Test parser initialization."""
    parser = Parser()
    assert parser.supported_extensions is not None
    assert '.py' in parser.supported_extensions

def test_parser_parse_code(mock_session, mocker):
    """Test code parsing with mock directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test files
        test_file = os.path.join(temp_dir, "test.py")
        with open(test_file, 'w') as f:
            f.write("def hello():\n    return 'world'")

        parser = Parser()
        result = parser.parse_code(temp_dir)

        assert 'files' in result
        assert len(result['files']) > 0
        assert result['files'][0]['path'] == "test.py"
        assert result['files'][0]['type'] == 'python'

def test_parser_parse_empty_directory():
    """Test parsing an empty directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        parser = Parser()
        result = parser.parse_code(temp_dir)

        assert 'files' in result
        assert len(result['files']) == 0

def test_parser_parse_nonexistent_directory():
    """Test parsing a non-existent directory."""
    parser = Parser()
    with pytest.raises(FileNotFoundError):
        parser.parse_code("/nonexistent/directory/path")

def test_parser_parse_with_binary_files():
    """Test parsing directory with binary and source files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create source file
        test_file = os.path.join(temp_dir, "test.py")
        with open(test_file, 'w') as f:
            f.write("def hello():\n    return 'world'")

        # Create binary file
        binary_file = os.path.join(temp_dir, "binary.exe")
        with open(binary_file, 'wb') as f:
            f.write(b'\x00\x01\x02\x03binary data')

        # Create unsupported extension
        unknown_file = os.path.join(temp_dir, "unknown.xyz")
        with open(unknown_file, 'w') as f:
            f.write("unknown content")

        parser = Parser()
        result = parser.parse_code(temp_dir)

        # Should only include supported files
        assert 'files' in result
        supported_files = [f for f in result['files'] if f['path'].endswith('.py')]
        assert len(supported_files) == 1
        assert supported_files[0]['path'] == "test.py"

def test_parser_parse_syntax_error():
    """Test parsing file with syntax errors."""
    with tempfile.TemporaryDirectory() as temp_dir:
        test_file = os.path.join(temp_dir, "syntax_error.py")
        with open(test_file, 'w') as f:
            f.write("def hello():\n    return 'world'\ndef broken_function(")  # Missing closing paren

        parser = Parser()
        result = parser.parse_code(temp_dir)

        # Should still parse, even with syntax errors
        assert 'files' in result
        assert len(result['files']) > 0

def test_parser_extract_functions_empty_file():
    """Test extracting functions from empty file."""
    parser = Parser()
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write("")  # Empty file
        temp_file = f.name

    functions = parser.extract_functions(temp_file)
    os.unlink(temp_file)

    assert isinstance(functions, list)
    assert len(functions) == 0

def test_parser_extract_functions_large_file():
    """Test extracting functions from large file."""
    parser = Parser()
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        # Create a large file with many functions
        content = ""
        for i in range(100):
            content += f"def function_{i}():\n    return {i}\n\n"
        f.write(content)
        temp_file = f.name

    functions = parser.extract_functions(temp_file)
    os.unlink(temp_file)

    assert isinstance(functions, list)
    assert len(functions) == 100

def test_parser_extract_classes_syntax_error():
    """Test extracting classes from file with syntax errors."""
    parser = Parser()
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write("class BrokenClass:\n    def method(self):\n        return 'broken'\n\nclass ValidClass:\n    pass")
        temp_file = f.name

    classes = parser.extract_classes(temp_file)
    os.unlink(temp_file)

    # Should still extract the valid class
    assert isinstance(classes, list)
    valid_classes = [c for c in classes if c['name'] == 'ValidClass']
    assert len(valid_classes) == 1

def test_parser_parse_javascript():
    """Test parsing JavaScript/TypeScript files."""
    parser = Parser()
    with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
        f.write("""
        function hello(name) {
            console.log(`Hello, ${name}!`);
            return true;
        }

        const arrowFunction = (param) => {
            return param * 2;
        };
        """)
        temp_file = f.name

    functions = parser.extract_functions(temp_file)
    os.unlink(temp_file)

    assert isinstance(functions, list)
    assert len(functions) >= 1  # At least one function should be found

def test_parser_extract_functions_unsupported_language():
    """Test extracting functions from unsupported language."""
    parser = Parser()
    with tempfile.NamedTemporaryFile(mode='w', suffix='.xyz', delete=False) as f:
        f.write("some unknown language content")
        temp_file = f.name

    functions = parser.extract_functions(temp_file)
    os.unlink(temp_file)

    assert isinstance(functions, list)
    # Should return empty list for unsupported languages

def test_ai_orchestrator_initialization():
    """Test AI orchestrator setup."""
    orchestrator = AIOrchestrator()
    assert orchestrator.model_config is not None
    assert orchestrator.model_config['temperature'] == 0.1

def test_ai_orchestrator_generation(mocker):
    """Test documentation generation with mock."""
    orchestrator = AIOrchestrator()
    mock_logger = mocker.patch('logging.getLogger')

    with tempfile.TemporaryDirectory() as temp_dir:
        result = orchestrator.generate_documentation(temp_dir)
        # Should return True (placeholder implementation)
        assert result == True

def test_patcher_initialization(sample_config):
    """Test patcher initialization."""
    patcher = Patcher(sample_config)
    assert patcher.git_command == 'git'
    assert patcher.branch_prefix == 'feature/docs-'

def test_repo_manager_initialization(sample_config):
    """Test repo manager initialization."""
    repo_manager = RepoManager(sample_config)
    assert repo_manager.timeout == 300
    assert repo_manager.git_command == 'git'

def test_job_manager_start_job(mock_session, mock_job, mocker):
    """Test starting a job."""
    mock_logger = mocker.patch('logging.getLogger')
    manager = JobManager(mock_session, mock_job)

    manager.start_job()
    assert mock_session.commit.called
    assert mock_job.status == 'running'

def test_job_manager_start_job_failure(mock_session, mock_job, mocker):
    """Test job start failure."""
    mock_logger = mocker.patch('logging.getLogger')
    mock_session.commit.side_effect = Exception("DB Error")

    manager = JobManager(mock_session, mock_job)

    result = manager.start_job()
    assert result == False
    assert mock_session.rollback.called

def test_job_manager_complete_job(mock_session, mock_job, mocker):
    """Test completing a job."""
    mock_logger = mocker.patch('logging.getLogger')
    manager = JobManager(mock_session, mock_job)

    manager.complete_job()
    assert mock_session.commit.called
    assert mock_job.status == 'completed'

def test_job_manager_fail_job(mock_session, mock_job, mocker):
    """Test failing a job."""
    mock_logger = mocker.patch('logging.getLogger')
    manager = JobManager(mock_session, mock_job)

    manager.fail_job("Test error")
    assert mock_session.commit.called
    assert mock_job.status == 'failed'

def test_job_manager_update_progress(mock_session, mock_job, mocker):
    """Test updating job progress."""
    mock_logger = mocker.patch('logging.getLogger')
    manager = JobManager(mock_session, mock_job)

    result = manager.update_progress(50)
    assert result == True
    assert mock_session.commit.called

def test_job_manager_update_progress_none():
    """Test updating job progress with None value."""
    mock_session = Mock()
    mock_job = Mock()

    manager = JobManager(mock_session, mock_job)
    result = manager.update_progress(None)

    assert result == True
    mock_session.commit.assert_not_called()  # Should not commit if no progress

def test_job_manager_start_job_db_rollback():
    """Test job start failure with database rollback."""
    mock_session = Mock()
    mock_session.commit.side_effect = Exception("DB connection lost")
    mock_session.rollback = Mock()

    mock_job = Mock()
    mock_job.id = 1

    manager = JobManager(mock_session, mock_job)
    result = manager.start_job()

    assert result == False
    mock_session.rollback.assert_called_once()

def test_job_manager_fail_job_with_none_error():
    """Test failing job with None error message."""
    mock_session = Mock()
    mock_session.commit.side_effect = Exception("Commit failed")
    mock_session.rollback = Mock()

    mock_job = Mock()
    mock_job.id = 1

    manager = JobManager(mock_session, mock_job)
    result = manager.fail_job(None)  # None error message

    assert result == False
    mock_session.rollback.assert_called_once()

def test_job_manager_complete_job_db_failure():
    """Test job completion with database failure."""
    mock_session = Mock()
    mock_session.commit.side_effect = Exception("Connection timeout")

    mock_job = Mock()
    mock_job.id = 1

    manager = JobManager(mock_session, mock_job)
    result = manager.complete_job()

    assert result == False
    # Should handle exception gracefully

def test_job_manager_get_job_status():
    """Test getting job status from database."""
    mock_session = Mock()
    mock_job = Mock()
    mock_job.status = 'running'

    # Refresh job from database
    mock_session.refresh.return_value = None

    manager = JobManager(mock_session, mock_job)
    status = manager.get_job_status()

    assert status == 'running'
    mock_session.refresh.assert_called_once()

def test_job_manager_cancel_job_already_completed():
    """Test canceling an already completed job."""
    mock_session = Mock()
    mock_job = Mock()
    mock_job.status = 'completed'

    manager = JobManager(mock_session, mock_job)
    result = manager.cancel_job()

    assert result == False  # Should not cancel completed job
    mock_session.commit.assert_not_called()

def test_job_manager_retry_failed_job():
    """Test retrying a failed job."""
    mock_session = Mock()
    mock_job = Mock()
    mock_job.status = 'failed'

    manager = JobManager(mock_session, mock_job)
    result = manager.retry_job()

    assert result == True
    assert mock_job.status == 'pending'
    mock_session.commit.assert_called_once()

def test_job_manager_retry_completed_job():
    """Test retrying a completed job (should fail)."""
    mock_session = Mock()
    mock_job = Mock()
    mock_job.status = 'completed'

    manager = JobManager(mock_session, mock_job)
    result = manager.retry_job()

    assert result == False  # Should not retry completed job
    mock_session.commit.assert_not_called()

def test_job_manager_validate_job_missing_id():
    """Test job validation with missing job ID."""
    mock_session = Mock()
    mock_job = Mock()
    mock_job.id = None

    manager = JobManager(mock_session, mock_job)
    result = manager.validate_job()

    assert result == False

def test_job_manager_validate_job_invalid_url():
    """Test job validation with invalid repository URL."""
    mock_session = Mock()
    mock_job = Mock()
    mock_job.id = 1
    mock_job.repo_url = 'invalid-url-without-scheme'

    manager = JobManager(mock_session, mock_job)
    result = manager.validate_job()

    assert result == False

def test_job_manager_get_job_info():
    """Test getting job information."""
    mock_session = Mock()
    mock_job = Mock()
    mock_job.id = 123
    mock_job.status = 'running'
    mock_job.repo_url = 'https://github.com/test/repo'
    mock_job.created_at = Mock()
    mock_job.created_at.isoformat.return_value = '2024-01-01T12:00:00'
    mock_job.updated_at = Mock()
    mock_job.updated_at.isoformat.return_value = '2024-01-01T13:00:00'

    manager = JobManager(mock_session, mock_job)
    info = manager.get_job_info()

    assert info['job_id'] == 123
    assert info['status'] == 'running'
    assert info['repo_url'] == 'https://github.com/test/repo'

def test_job_manager_update_error_message_db_failure():
    """Test updating error message with database failure."""
    mock_session = Mock()
    mock_session.commit.side_effect = Exception("DB Error")

    mock_job = Mock()
    mock_job.id = 1

    manager = JobManager(mock_session, mock_job)
    result = manager.update_error_message("Test error")

    assert result == False
    # Should handle exception gracefully

# Integration tests

@patch('worker.worker.JobManager')
@patch('worker.worker.RepoManager')
@patch('worker.worker.Parser')
@patch('worker.worker.AIOrchestrator')
@patch('worker.worker.Patcher')
@patch('worker.worker.Logger')
# Enhanced integration tests with error scenarios

@patch('worker.worker.Config')
def test_process_documentation_job_success(mock_config, mock_logger_cls, mock_patcher_cls, mock_ai_cls, mock_parser_cls, mock_repo_cls, mock_job_manager_cls, mocker):
    """Test successful processing of documentation job."""
    # Mock components
    mock_config_instance = Mock()
    mock_config.return_value = mock_config_instance

    mock_logger_instance = Mock()
    mock_logger_cls.return_value = mock_logger_instance

    mock_job_manager_instance = Mock()
    mock_job_manager_cls.return_value = mock_job_manager_instance

    mock_repo_instance = Mock()
    mock_repo_cls.return_value = mock_repo_instance

    mock_parser_instance = Mock()
    mock_parser_cls.return_value = mock_parser_instance

    mock_ai_instance = Mock()
    mock_ai_cls.return_value = mock_ai_instance

    mock_patcher_instance = Mock()
    mock_patcher_cls.return_value = mock_patcher_instance

    # Mock database session
    mock_session = Mock()
    mock_job = Mock()
    mock_job.id = 1
    mock_session.query.return_value.filter.return_value.first.return_value = mock_job

    # Mock SessionLocal
    mocker.patch('worker.worker.SessionLocal', return_value=mock_session)

    # Mock environment
    mocker.patch.dict(os.environ, {
        'DATABASE_URL': TEST_DATABASE_URL,
        'CELERY_BROKER_URL': 'redis://test:6379/0'
    })

    # Call the function
    process_documentation_job(1)

    # Verify components were instantiated
    mock_job_manager_cls.assert_called_once_with(mock_session, mock_job)
    mock_repo_cls.assert_called_once()
    mock_parser_cls.assert_called_once()
    mock_ai_cls.assert_called_once()
    mock_patcher_cls.assert_called_once()
    mock_logger_cls.assert_called_once()
    mock_config.assert_called_once()

    # Verify method calls
    mock_job_manager_instance.start_job.assert_called_once()
    mock_repo_instance.clone_repo.assert_called_once()
    mock_parser_instance.parse_code.assert_called_once()
    mock_ai_instance.generate_documentation.assert_called_once()
    mock_patcher_instance.create_patch_or_pr.assert_called_once()
    mock_logger_instance.log_progress.assert_called_once()
    mock_job_manager_instance.complete_job.assert_called_once()

@patch('worker.worker.Config')
def test_process_documentation_job_missing_environment_variables(mock_config, mock_logger_cls, mock_patcher_cls, mock_ai_cls, mock_parser_cls, mock_repo_cls, mock_job_manager_cls, mocker):
    """Test processing job with missing environment variables."""
    # Mock components
    mock_config_instance = Mock()
    mock_config.return_value = mock_config_instance

    mock_job_manager_instance = Mock()
    mock_job_manager_cls.return_value = mock_job_manager_instance

    # Mock database session
    mock_session = Mock()
    mock_job = Mock()
    mock_job.id = 1
    mock_session.query.return_value.filter.return_value.first.return_value = mock_job

    # Mock SessionLocal
    mocker.patch('worker.worker.SessionLocal', return_value=mock_session)

    # Mock empty environment (no CELERY_BROKER_URL, etc.)
    mocker.patch.dict(os.environ, {}, clear=True)

    # Call the function
    with pytest.raises(KeyError):
        process_documentation_job(1)

@patch('worker.worker.Config')
def test_process_documentation_job_large_repository_timeout(mock_config, mock_logger_cls, mock_patcher_cls, mock_ai_cls, mock_parser_cls, mock_repo_cls, mock_job_manager_cls, mocker):
    """Test processing job with large repository that causes timeouts."""
    # Mock components
    mock_config_instance = Mock()
    mock_config.return_value = mock_config_instance

    mock_logger_instance = Mock()
    mock_logger_cls.return_value = mock_logger_instance

    mock_job_manager_instance = Mock()
    mock_job_manager_cls.return_value = mock_job_manager_instance

    mock_repo_instance = Mock()
    mock_repo_instance.clone_repo.side_effect = TimeoutError("Clone timeout: repository too large")
    mock_repo_cls.return_value = mock_repo_instance

    # Mock other components that won't be reached
    mock_parser_cls.return_value = Mock()
    mock_ai_cls.return_value = Mock()
    mock_patcher_cls.return_value = Mock()

    # Mock database session
    mock_session = Mock()
    mock_job = Mock()
    mock_job.id = 1
    mock_session.query.return_value.filter.return_value.first.return_value = mock_job

    # Mock SessionLocal
    mocker.patch('worker.worker.SessionLocal', return_value=mock_session)

    # Mock environment
    mocker.patch.dict(os.environ, {
        'DATABASE_URL': TEST_DATABASE_URL,
        'CELERY_BROKER_URL': 'redis://test:6379/0'
    })

    # Call the function
    process_documentation_job(1)

    # Verify failure was logged and job was failed
    mock_job_manager_instance.fail_job.assert_called_once()

@patch('worker.worker.Config')
def test_process_documentation_job_ai_service_unavailable(mock_config, mock_logger_cls, mock_patcher_cls, mock_ai_cls, mock_parser_cls, mock_repo_cls, mock_job_manager_cls, mocker):
    """Test processing job when AI service is unavailable."""
    # Mock components
    mock_config_instance = Mock()
    mock_config.return_value = mock_config_instance

    mock_logger_instance = Mock()
    mock_logger_cls.return_value = mock_logger_instance

    mock_job_manager_instance = Mock()
    mock_job_manager_cls.return_value = mock_job_manager_instance

    mock_repo_instance = Mock()
    mock_repo_cls.return_value = mock_repo_instance

    mock_parser_instance = Mock()
    mock_parser_cls.return_value = mock_parser_instance

    mock_ai_instance = Mock()
    mock_ai_instance.generate_documentation.side_effect = ConnectionError("AI service unavailable")
    mock_ai_cls.return_value = mock_ai_instance

    mock_patcher_cls.return_value = Mock()

    # Mock database session
    mock_session = Mock()
    mock_job = Mock()
    mock_job.id = 1
    mock_session.query.return_value.filter.return_value.first.return_value = mock_job

    # Mock SessionLocal
    mocker.patch('worker.worker.SessionLocal', return_value=mock_session)

    # Mock environment
    mocker.patch.dict(os.environ, {
        'DATABASE_URL': TEST_DATABASE_URL,
        'CELERY_BROKER_URL': 'redis://test:6379/0'
    })

    # Call the function
    process_documentation_job(1)

    # Verify AI was attempted but failed
    mock_ai_instance.generate_documentation.assert_called_once()
    mock_job_manager_instance.fail_job.assert_called_once()

@patch('worker.worker.JobManager')
@patch('worker.worker.RepoManager')
@patch('worker.worker.Parser')
@patch('worker.worker.AIOrchestrator')
@patch('worker.worker.Patcher')
@patch('worker.worker.Logger')
@patch('worker.worker.Config')
def test_process_documentation_job_job_not_found(mock_config, mock_logger_cls, mock_patcher_cls, mock_ai_cls, mock_parser_cls, mock_repo_cls, mock_job_manager_cls, mocker):
    """Test job processing when job is not found."""
    # Mock database session
    mock_session = Mock()
    mock_session.query.return_value.filter.return_value.first.return_value = None

    # Mock SessionLocal
    mocker.patch('worker.worker.SessionLocal', return_value=mock_session)

    # Mock logging
    mocker.patch('logging.getLogger')

    # Mock environment
    mocker.patch.dict(os.environ, {
        'DATABASE_URL': TEST_DATABASE_URL,
        'CELERY_BROKER_URL': 'redis://test:6379/0'
    })

    # Call the function
    process_documentation_job(999)

    # Verify no components were instantiated (early return)
    mock_job_manager_cls.assert_not_called()

@patch('worker.worker.JobManager')
@patch('worker.worker.RepoManager')
@patch('worker.worker.Parser')
@patch('worker.worker.AIOrchestrator')
@patch('worker.worker.Patcher')
@patch('worker.worker.Logger')
@patch('worker.worker.Config')
def test_process_documentation_job_clone_failure(mock_config, mock_logger_cls, mock_patcher_cls, mock_ai_cls, mock_parser_cls, mock_repo_cls, mock_job_manager_cls, mocker):
    """Test job processing when repo clone fails."""
    # Mock components
    mock_config_instance = Mock()
    mock_config.return_value = mock_config_instance

    mock_job_manager_instance = Mock()
    mock_job_manager_cls.return_value = mock_job_manager_instance

    mock_repo_instance = Mock()
    mock_repo_instance.clone_repo.return_value = False  # Clone fails
    mock_repo_cls.return_value = mock_repo_instance

    # Mock other components that won't be reached
    mock_parser_cls.return_value = Mock()
    mock_ai_cls.return_value = Mock()
    mock_patcher_cls.return_value = Mock()
    mock_logger_cls.return_value = Mock()

    # Mock database session
    mock_session = Mock()
    mock_job = Mock()
    mock_job.id = 1
    mock_session.query.return_value.filter.return_value.first.return_value = mock_job

    # Mock SessionLocal
    mocker.patch('worker.worker.SessionLocal', return_value=mock_session)

    # Mock logging
    mocker.patch('logging.getLogger')

    # Mock environment
    mocker.patch.dict(os.environ, {
        'DATABASE_URL': TEST_DATABASE_URL,
        'CELERY_BROKER_URL': 'redis://test:6379/0'
    })

    # Call the function
    process_documentation_job(1)

    # Verify clone was attempted but failed
    mock_job_manager_instance.start_job.assert_called_once()
    mock_job_manager_instance.fail_job.assert_called_once()  # Should fail due to clone failure
    mock_repo_instance.clone_repo.assert_called_once()

    # Verify later stages were not reached
    mock_parser_cls.return_value.parse_code.assert_not_called()
    mock_ai_cls.return_value.generate_documentation.assert_not_called()
    mock_patcher_cls.return_value.create_patch_or_pr.assert_not_called()

def test_repo_manager_cleanup_temp_repos():
    """Test repository cleanup functionality."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create some fake repo directories
        for i in range(3):
            repo_dir = os.path.join(temp_dir, f"repo-{i}")
            os.makedirs(repo_dir)
            # Add modification time variation
            os.utime(repo_dir, times=(i * 1000, i * 1000))

        # Set up repo manager with temp directory
        config = {'temp_dir': temp_dir, 'git_command': 'git'}
        repo_manager = RepoManager(config)

        # Perform cleanup (keep only 2)
        cleaned = repo_manager.cleanup_temp_repos(keep_last_n=2)

        # Should have cleaned 1 repository
        assert cleaned == 1

def test_repo_manager_validate_repository_valid():
    """Test repository validation for valid repo."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create .git directory
        os.makedirs(os.path.join(temp_dir, '.git'))

        # Create some source files
        with open(os.path.join(temp_dir, 'test.py'), 'w') as f:
            f.write("# Python file")

        with open(os.path.join(temp_dir, 'test.js'), 'w') as f:
            f.write("console.log('JS file');")

        # Create README
        with open(os.path.join(temp_dir, 'README.md'), 'w') as f:
            f.write("# Test Repository")

        repo_manager = RepoManager()
        result = repo_manager.validate_repository(temp_dir)

        assert result['valid'] == True
        assert result['source_files_count'] == 2
        assert result['has_readme'] == True

def test_repo_manager_validate_repository_invalid():
    """Test repository validation for invalid repo."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # No .git directory
        repo_manager = RepoManager()
        result = repo_manager.validate_repository(temp_dir)

        assert result['valid'] == False
        assert result['error'] == 'Not a git repository'

def test_repo_manager_generate_temp_path():
    """Test temporary path generation."""
    repo_manager = RepoManager()
    path = repo_manager._generate_temp_path("https://github.com/test/repo")

    # Should include repo name and hash
    assert "repo-test" in path
    assert len(path) > len("/tmp/repos/") + 10  # At least some hash

def test_patcher_stage_documentation_files(mocker):
    """Test staging documentation files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)

        # Create git repo structure
        os.makedirs('.git')

        # Create some files
        with open('test.py', 'w') as f:
            f.write("# Test file")

        with open('README.md', 'w') as f:
            f.write("# Documentation")

        # Mock subprocess
        mock_run = mocker.patch('subprocess.run')
        mock_run.return_value = Mock()

        patcher = Patcher()
        result = patcher._stage_documentation_files()

        assert result == True
        # Should have called git add for documentation files
        assert mock_run.called