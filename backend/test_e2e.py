import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import os
import tempfile
from unittest.mock import Mock, patch

from backend.main import app
from backend.models import Base, get_db

# Test database configuration
TEST_DATABASE_URL = "sqlite:///./test_e2e.db"

# Override environment variables for testing
os.environ["DATABASE_URL"] = TEST_DATABASE_URL
os.environ["GITHUB_CLIENT_ID"] = "test_client_id"
os.environ["GITHUB_CLIENT_SECRET"] = "test_client_secret"
os.environ["GITHUB_CALLBACK_URL"] = "http://localhost:8000/auth/github/callback"

# Create test database engine
engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# Create test session
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override get_db for tests
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="session", autouse=True)
def setup_e2e_database():
    """Create tables before E2E tests and drop after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client():
    """Create test client for E2E tests."""
    with TestClient(app) as c:
        yield c

@pytest.fixture
def auth_headers():
    """Mock authentication headers for E2E."""
    return {"X-Auth-Token": "test-e2e-token"}

# End-to-end integration tests

def test_complete_user_workflow(client, auth_headers, mocker):
    """Test complete user workflow: connect repo -> run docs -> monitor progress."""
    # Step 1: Connect repository
    repo_data = {
        "repo_url": "https://github.com/test/fixmydocs-test",
        "repo_name": "fixmydocs-test"
    }

    response = client.post("/api/repos/connect", json=repo_data, headers=auth_headers)
    assert response.status_code == 200
    connect_result = response.json()
    assert "repo_id" in connect_result

    repo_id = 1  # First repo

    # Step 2: Trigger documentation run
    trigger_data = {"repo_id": repo_id}
    with patch('backend.main.process_documentation_job'):  # Mock worker call
        response = client.post("/api/docs/run", json=trigger_data, headers=auth_headers)
        assert response.status_code == 200

    run_result = response.json()
    assert "job_id" in run_result
    job_id = run_result["job_id"]
    assert run_result["status"] == "pending"

    # Step 3: Check job status
    response = client.get(f"/api/jobs/status/{job_id}", headers=auth_headers)
    assert response.status_code == 200
    status_data = response.json()
    assert status_data["job_id"] == job_id
    assert "status" in status_data
    assert "created_at" in status_data
    assert "updated_at" in status_data

    # Step 4: Verify job appears in all jobs list
    response = client.get("/api/jobs", headers=auth_headers)
    assert response.status_code == 200
    jobs_list = response.json()
    assert len(jobs_list) >= 1
    assert any(job["job_id"] == job_id for job in jobs_list)

def test_user_authorization_workflow(client, mocker):
    """Test complete OAuth user authorization workflow."""
    # Mock httpx AsyncClient for GitHub API calls
    mock_token_response = Mock()
    mock_token_response.json.return_value = {"access_token": "test_access_token"}
    mock_token_response.raise_for_status = Mock()

    mock_user_response = Mock()
    mock_user_response.json.return_value = {
        "id": "gh123",
        "login": "testuser",
        "email": "testuser@example.com"
    }
    mock_user_response.raise_for_status = Mock()

    mock_client = Mock()
    mock_client.post.return_value = mock_token_response
    mock_client.get.return_value = mock_user_response

    mocker.patch("httpx.AsyncClient", return_value=mock_client)

    # Step 1: Initiate GitHub OAuth
    response = client.get("/api/auth/github")
    assert response.status_code == 302
    assert "github.com/login/oauth/authorize" in str(response.url)

    # Step 2: Handle callback with mock code
    response = client.get("/auth/github/callback?code=test_oauth_code")
    assert response.status_code == 302  # Redirect to frontend

def test_repository_management_workflow(client, auth_headers):
    """Test repository management workflow."""
    # Step 1: Connect multiple repositories
    repos = [
        {"repo_url": "https://github.com/test/repo1", "repo_name": "repo1"},
        {"repo_url": "https://github.com/test/repo2", "repo_name": "repo2"}
    ]

    connected_repos = []
    for repo_data in repos:
        response = client.post("/api/repos/connect", json=repo_data, headers=auth_headers)
        assert response.status_code == 200
        connected_repos.append(response.json()["repo_id"])

    # Step 2: Create jobs for multiple repos
    job_ids = []
    for repo_id in connected_repos:
        with patch('backend.main.process_documentation_job'):
            response = client.post("/api/docs/run", json={"repo_id": repo_id}, headers=auth_headers)
            assert response.status_code == 200
            job_ids.append(response.json()["job_id"])

    # Step 3: Monitor job batch status
    for job_id in job_ids:
        response = client.get(f"/api/jobs/status/{job_id}", headers=auth_headers)
        assert response.status_code == 200

    # Step 4: Verify all jobs in list
    response = client.get("/api/jobs", headers=auth_headers)
    assert response.status_code == 200
    all_jobs = response.json()
    assert len(all_jobs) >= len(job_ids)

def test_error_handling_workflow(client, auth_headers):
    """Test error handling in complete workflows."""
    # Step 1: Try to run docs on non-existent repo
    trigger_data = {"repo_id": 999}
    response = client.post("/api/docs/run", json=trigger_data, headers=auth_headers)
    assert response.status_code == 404
    assert "Repository not found" in response.json()["detail"]

    # Step 2: Try to get status of non-existent job
    response = client.get("/api/jobs/status/999", headers=auth_headers)
    assert response.status_code == 404
    assert "Job not found" in response.json()["detail"]

    # Step 3: Try to access protected endpoints without auth
    client_no_auth = TestClient(app)
    response = client_no_auth.post("/api/repos/connect", json={"repo_url": "test", "repo_name": "test"})
    assert response.status_code == 401

def test_database_integrity_workflow(client, auth_headers, mocker):
    """Test database integrity across workflow."""
    # Connect repo
    repo_data = {"repo_url": "https://github.com/test/integrity", "repo_name": "integrity"}
    response = client.post("/api/repos/connect", json=repo_data, headers=auth_headers)
    assert response.status_code == 200
    repo_id = response.json()["repo_id"]

    # Create job
    with patch('backend.main.process_documentation_job'):
        response = client.post("/api/docs/run", json={"repo_id": repo_id}, headers=auth_headers)
        assert response.status_code == 200
        job_id = response.json()["job_id"]

    # Verify database relationships
    from backend.models import User, Repo, Job
    from backend.main import SessionLocal

    db = SessionLocal()
    try:
        # Verify repo relationship
        repo = db.query(Repo).filter(Repo.id == repo_id).first()
        assert repo is not None
        assert repo.repo_url == "https://github.com/test/integrity"

        # Verify job relationship
        job = db.query(Job).filter(Job.id == job_id).first()
        assert job is not None
        assert job.repo_id == repo_id
        assert job.status == "pending"

        # Verify user association (dummy user)
        user = db.query(User).filter(User.username == "dummy_user").first()
        assert user is not None
        assert len(user.repos) >= 1

    finally:
        db.close()

def test_concurrent_jobs_workflow(client, auth_headers, mocker):
    """Test concurrent job creation and monitoring."""
    # Create multiple repos quickly
    repo_ids = []
    for i in range(3):
        repo_data = {
            "repo_url": f"https://github.com/test/concurrent{i}",
            "repo_name": f"concurrent{i}"
        }
        response = client.post("/api/repos/connect", json=repo_data, headers=auth_headers)
        repo_ids.append(response.json()["repo_id"])

    # Trigger multiple jobs
    job_ids = []
    for repo_id in repo_ids:
        with patch('backend.main.process_documentation_job'):
            response = client.post("/api/docs/run", json={"repo_id": repo_id}, headers=auth_headers)
            job_ids.append(response.json()["job_id"])

    # Verify all jobs are tracked independently
    for job_id in job_ids:
        response = client.get(f"/api/jobs/status/{job_id}", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["job_id"] == job_id

def test_github_integration_edge_cases(client, mocker):
    """Test GitHub integration edge cases in workflow."""
    # Test callback with malformed code
    response = client.get("/auth/github/callback?code=")
    assert response.status_code == 422  # Validation error

    # Test callback with non-JSON response (mock network error)
    mock_client = Mock()
    mock_client.post.side_effect = Mock(side_effect=Exception("Network error"))

    mocker.patch("httpx.AsyncClient", return_value=mock_client)

    response = client.get("/auth/github/callback?code=error_code")
    assert response.status_code == 500

    # Test callback with missing user data
    mock_token_response = Mock()
    mock_token_response.json.return_value = {"access_token": "test_token"}
    mock_token_response.raise_for_status = Mock()

    mock_user_response = Mock()
    mock_user_response.raise_for_status.side_effect = Exception("API Error")

    mock_client.post.return_value = mock_token_response
    mock_client.get.return_value = mock_user_response

    response = client.get("/auth/github/callback?code=fail_code")
    assert response.status_code == 500

def test_job_lifecycle_simulation(client, auth_headers, mocker):
    """Test complete job lifecycle from queue to completion."""
    # Step 1: Setup
    repo_data = {"repo_url": "https://github.com/test/lifecycle", "repo_name": "lifecycle"}
    response = client.post("/api/repos/connect", json=repo_data, headers=auth_headers)
    repo_id = response.json()["repo_id"]

    # Step 2: Create job (pending)
    with patch('backend.main.process_documentation_job'):
        response = client.post("/api/docs/run", json={"repo_id": repo_id}, headers=auth_headers)
        job_id = response.json()["job_id"]

    # Step 3: Simulate status progression (would be done by worker)
    from backend.models import Job
    from backend.main import SessionLocal

    db = SessionLocal()
    job = db.query(Job).filter(Job.id == job_id).first()

    # Simulate running
    job.status = "running"
    db.commit()

    response = client.get(f"/api/jobs/status/{job_id}", headers=auth_headers)
    assert response.json()["status"] == "running"

    # Simulate completion
    job.status = "completed"
    db.commit()

    response = client.get(f"/api/jobs/status/{job_id}", headers=auth_headers)
    assert response.json()["status"] == "completed"

    db.close()

    # Step 4: Verify final statistics
    response = client.get("/api/jobs", headers=auth_headers)
    jobs = response.json()
    assert len([j for j in jobs if j["status"] == "completed"]) >= 1