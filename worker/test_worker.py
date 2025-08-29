import pytest
import tempfile
import os
from unittest.mock import Mock, patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

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

def test_logger_initialization(sample_config):
    """Test logger initialization."""
    logger = Logger(sample_config)
    assert logger is not None
    assert len(logger.get_progress_history()) == 0

def test_logger_progress_tracking(sample_config):
    """Test progress tracking."""
    logger = Logger(sample_config)
    logger.log_progress("Starting test", 10)
    history = logger.get_progress_history()
    assert len(history) == 1
    assert history[0]['message'] == "Starting test"
    assert history[0]['progress'] == 10

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

# Integration tests

@patch('worker.worker.JobManager')
@patch('worker.worker.RepoManager')
@patch('worker.worker.Parser')
@patch('worker.worker.AIOrchestrator')
@patch('worker.worker.Patcher')
@patch('worker.worker.Logger')
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