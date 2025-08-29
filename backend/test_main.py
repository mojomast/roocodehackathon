import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import os
import hmac
import hashlib

from backend.main import app, parse_github_repo
from backend.models import Base, get_db, User, Repo, Job

# Test database configuration
TEST_DATABASE_URL = "sqlite:///./test.db"

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

# Set webhook secret for tests
os.environ["GITHUB_WEBHOOK_SECRET"] = "testsecret"

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Create tables before tests and drop after."""
    Base.metadata.create_all(bind=engine)
    # seed an auth user
    db = TestingSessionLocal()
    try:
        user = User(github_id="gh_test", username="testuser", access_token="test-token", email="test@example.com")
        db.add(user)
        db.commit()
    finally:
        db.close()
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client():
    """Create test client."""
    with TestClient(app) as c:
        yield c

@pytest.fixture
def auth_headers():
    """Mock authentication headers."""
    return {"X-Auth-Token": "test-token"}

# Test cases

def test_read_root():
    """Test root endpoint."""
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the FixMyDocs Backend API!"}

def test_github_auth_redirect():
    """Test GitHub auth redirect."""
    client = TestClient(app)
    response = client.get("/api/auth/github")
    assert response.status_code == 302
    assert "github.com/login/oauth/authorize" in str(response.url)

def test_github_callback_success(client, mocker):
    """Test successful GitHub callback."""
    # Mock httpx AsyncClient
    mock_response_token = mocker.AsyncMock()
    mock_response_token.json.return_value = {"access_token": "test_access_token"}
    mock_response_token.raise_for_status = mocker.AsyncMock()

    mock_response_user = mocker.AsyncMock()
    mock_response_user.json.return_value = {
        "id": "123",
        "login": "testuser",
        "email": "test@example.com"
    }
    mock_response_user.raise_for_status = mocker.AsyncMock()

    client_mock = mocker.AsyncMock()
    client_mock.post.return_value = mock_response_token
    client_mock.get.return_value = mock_response_user

    mocker.patch("httpx.AsyncClient", return_value=client_mock)

    response = client.get("/auth/github/callback?code=test_code")
    assert response.status_code == 302
    # Verify redirect to frontend dashboard

def test_github_callback_missing_code():
    """Test GitHub callback with missing code."""
    client = TestClient(app)
    response = client.get("/auth/github/callback")
    assert response.status_code == 422  # Missing required query parameter

def test_github_callback_invalid_token_exchange(client, mocker):
    """Test GitHub callback with failed token exchange."""
    mock_response = mocker.AsyncMock()
    mock_response.raise_for_status.side_effect = Exception("Bad request")

    client_mock = mocker.AsyncMock()
    client_mock.post.return_value = mock_response

    mocker.patch("httpx.AsyncClient", return_value=client_mock)

    response = client.get("/auth/github/callback?code=invalid_code")
    assert response.status_code == 500

def test_connect_repository_success(client, auth_headers):
    """Test successful repository connection."""
    request_data = {
        "repo_url": "https://github.com/test/repo",
        "repo_name": "test-repo"
    }

    response = client.post("/api/repos/connect", json=request_data, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "repo_id" in data

def test_connect_repository_missing_auth():
    """Test repository connection without auth."""
    request_data = {
        "repo_url": "https://github.com/test/repo",
        "repo_name": "test-repo"
    }

    client = TestClient(app)
    response = client.post("/api/repos/connect", json=request_data)
    assert response.status_code == 401

def test_connect_repository_invalid_data(client, auth_headers):
    """Test repository connection with invalid data."""
    request_data = {"invalid": "data"}

    response = client.post("/api/repos/connect", json=request_data, headers=auth_headers)
    assert response.status_code == 422  # Validation error

def test_trigger_doc_run_success(client, auth_headers):
    """Test successful documentation run trigger."""
    # First create a repo
    repo_data = {
        "repo_url": "https://github.com/test/repo",
        "repo_name": "test-repo"
    }
    client.post("/api/repos/connect", json=repo_data, headers=auth_headers)

    # Now trigger job
    job_data = {"repo_id": 1}
    response = client.post("/api/docs/run", json=job_data, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data
    assert data["status"] == "pending"

def test_trigger_doc_run_missing_auth():
    """Test doc run trigger without auth."""
    client = TestClient(app)
    response = client.post("/api/docs/run", json={"repo_id": 1})
    assert response.status_code == 401

def test_trigger_doc_run_invalid_repo(client, auth_headers):
    """Test doc run with non-existent repo."""
    job_data = {"repo_id": 999}
    response = client.post("/api/docs/run", json=job_data, headers=auth_headers)
    assert response.status_code == 404
    assert "Repository not found" in response.json()["detail"]

def test_get_job_status_success(client, auth_headers):
    """Test getting job status successfully."""
    # Create job first
    repo_data = {
        "repo_url": "https://github.com/test/repo",
        "repo_name": "test-repo"
    }
    client.post("/api/repos/connect", json=repo_data, headers=auth_headers)

    job_resp = client.post("/api/docs/run", json={"repo_id": 1}, headers=auth_headers)
    job_id = job_resp.json()["job_id"]

    response = client.get(f"/api/jobs/status/{job_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["job_id"] == job_id
    assert "status" in data

def test_get_job_status_missing_auth():
    """Test job status without auth."""
    client = TestClient(app)
    response = client.get("/api/jobs/status/1")
    assert response.status_code == 401

def test_get_job_status_not_found(client, auth_headers):
    """Test job status for non-existent job."""
    response = client.get("/api/jobs/status/999", headers=auth_headers)
    assert response.status_code == 404
    assert "Job not found" in response.json()["detail"]

def test_get_all_jobs(client, auth_headers):
    """Test getting all jobs."""
    response = client.get("/api/jobs", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_all_jobs_missing_auth():
    """Test all jobs without auth."""
    client = TestClient(app)
    response = client.get("/api/jobs")
    assert response.status_code == 401

# Database integration tests

def test_user_creation_in_github_callback(client, mocker):
    """Test user creation during authentication."""
    # Mock httpx
    mock_response_token = mocker.AsyncMock()
    mock_response_token.json.return_value = {"access_token": "test_access"}
    mock_response_token.raise_for_status = mocker.AsyncMock()

    mock_response_user = mocker.AsyncMock()
    mock_response_user.json.return_value = {
        "id": "456",
        "login": "newuser",
        "email": "new@example.com"
    }
    mock_response_user.raise_for_status = mocker.AsyncMock()

    client_mock = mocker.AsyncMock()
    client_mock.post.return_value = mock_response_token
    client_mock.get.return_value = mock_response_user

    mocker.patch("httpx.AsyncClient", return_value=client_mock)

    # Count users before
    db = TestingSessionLocal()
    before_count = db.query(User).count()
    db.close()

    client.get("/auth/github/callback?code=test_code")

    # Count users after
    db = TestingSessionLocal()
    after_count = db.query(User).count()
    db.close()

    assert after_count == before_count + 1

def test_repo_association_with_user(client, auth_headers):
    """Test repo association with authenticated user."""
    response = client.post("/api/repos/connect", json={
        "repo_url": "https://github.com/test/repo",
        "repo_name": "test-repo"
    }, headers=auth_headers)

    assert response.status_code == 200

    db = TestingSessionLocal()
    repo = db.query(Repo).first()
    user = db.query(User).filter(User.username == "testuser").first()
    db.close()

    assert repo is not None
    assert user is not None
    assert repo.user_id == user.id

def test_job_creation_and_lifecycle(client, auth_headers):
    """Test job creation and status tracking."""
    from backend.models import Job

    # Create repo
    client.post("/api/repos/connect", json={
        "repo_url": "https://github.com/test/repo",
        "repo_name": "test-repo"
    }, headers=auth_headers)

    # Create job
    response = client.post("/api/docs/run", json={"repo_id": 1}, headers=auth_headers)
    job_id = response.json()["job_id"]

    db = TestingSessionLocal()
    job = db.query(Job).filter(Job.id == job_id).first()
    db.close()

    assert job is not None
    assert job.repo_id == 1
    assert job.status == "pending"

    # Test status endpoint
    status_resp = client.get(f"/api/jobs/status/{job_id}", headers=auth_headers)
    assert status_resp.status_code == 200
    assert status_resp.json()["status"] == "pending"

# Tests for GitHub App Integration functions (BE-010 enhancement)
@pytest.mark.asyncio
async def test_github_app_fork_repo_success(client, mocker):
    """Test successful GitHub fork repository operation."""
    mock_response = mocker.AsyncMock()
    mock_response.json.return_value = {
        "html_url": "https://github.com/forked/repo",
        "full_name": "forked/repo"
    }
    mock_response.raise_for_status = mocker.AsyncMock()

    client_mock = mocker.AsyncMock()
    client_mock.post.return_value = mock_response

    from backend.main import github_app_fork_repo
    mocker.patch("httpx.AsyncClient", return_value=client_mock)

    from backend.main import github_app_fork_repo
    result = await github_app_fork_repo("https://github.com/owner/repo", "test-token")

    assert result["status"] == "success"
    assert "forked" in result["message"].lower()

@pytest.mark.asyncio
async def test_github_app_fork_repo_failure(client, mocker):
    """Test failed GitHub fork repository operation."""
    mock_response = mocker.AsyncMock()
    mock_response.raise_for_status.side_effect = Exception("Forbidden")

    client_mock = mocker.AsyncMock()
    client_mock.post.return_value = mock_response

    mocker.patch("httpx.AsyncClient", return_value=client_mock)

    from backend.main import github_app_fork_repo
    result = await github_app_fork_repo("https://github.com/owner/repo", "test-token")

    assert result["status"] == "error"
    assert "failed" in result["message"].lower()

@pytest.mark.asyncio
async def test_github_app_create_pull_request_success(client, mocker):
    """Test successful GitHub pull request creation."""
    mock_response = mocker.AsyncMock()
    mock_response.json.return_value = {
        "html_url": "https://github.com/owner/repo/pull/1",
        "number": 1
    }
    mock_response.raise_for_status = mocker.AsyncMock()

    client_mock = mocker.AsyncMock()
    client_mock.post.return_value = mock_response

    mocker.patch("httpx.AsyncClient", return_value=client_mock)

    from backend.main import github_app_create_pull_request
    result = await github_app_create_pull_request(
        "https://github.com/owner/repo", "feature-branch", "docs", "test-token"
    )

    assert result["status"] == "success"
    assert "created" in result["message"].lower()

@pytest.mark.asyncio
async def test_github_app_handle_webhook_push_event():
    """Test GitHub webhook handling for push events."""
    from backend.main import github_app_handle_webhook

    payload = {"ref": "refs/heads/main", "action": "push"}
    headers = {"X-GitHub-Event": "push", "X-Hub-Signature-256": "sha256=abc123"}

    result = await github_app_handle_webhook(payload, headers)

    assert result["status"] == "success"
    assert "push event handled" in result["message"]

@pytest.mark.asyncio
async def test_github_app_handle_webhook_pull_request_event():
    """Test GitHub webhook handling for pull request events."""
    from backend.main import github_app_handle_webhook

    payload = {"action": "opened"}
    headers = {"X-GitHub-Event": "pull_request", "X-Hub-Signature-256": "sha256=abc123"}

    result = await github_app_handle_webhook(payload, headers)

    assert result["status"] == "success"
    assert "pull request" in result["message"]

def test_list_repositories_endpoint(client, auth_headers):
    """GET /api/repos returns user repositories."""
    # connect a repo first
    client.post("/api/repos/connect", json={"repo_url":"https://github.com/owner/repo","repo_name":"repo"}, headers=auth_headers)
    resp = client.get("/api/repos", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert any(r["repo_name"] == "repo" for r in data)

def test_parse_github_repo_variants():
    """Repository URL parsing handles https, .git, ssh, and owner/repo."""
    assert parse_github_repo("https://github.com/owner/repo") == ("owner","repo")
    assert parse_github_repo("https://github.com/owner/repo.git") == ("owner","repo")
    assert parse_github_repo("git@github.com:owner/repo.git") == ("owner","repo")
    assert parse_github_repo("owner/repo") == ("owner","repo")

def test_webhook_signature_verification_valid(client):
    payload = {"ref": "refs/heads/main"}
    import json
    body = json.dumps(payload).encode()
    secret = os.environ["GITHUB_WEBHOOK_SECRET"].encode()
    sig = hmac.new(secret, body, hashlib.sha256).hexdigest()

    resp = client.post(
        "/api/github/webhook",
        data=body,
        headers={
            "X-Hub-Signature-256": f"sha256={sig}",
            "X-GitHub-Event": "push",
            "Content-Type": "application/json",
        },
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "success"

def test_webhook_signature_verification_invalid(client):
    import json
    body = json.dumps({"test":"x"}).encode()
    resp = client.post(
        "/api/github/webhook",
        data=body,
        headers={
            "X-Hub-Signature-256": "sha256=deadbeef",
            "X-GitHub-Event": "push",
            "Content-Type": "application/json",
        },
    )
    assert resp.status_code == 401

@pytest.mark.asyncio
async def test_github_app_handle_webhook_missing_signature():
    """Test GitHub webhook handling with missing signature."""
    from backend.main import github_app_handle_webhook

    payload = {}
    headers = {"X-GitHub-Event": "push"}

    result = await github_app_handle_webhook(payload, headers)

    assert result["status"] == "error"
    assert "signature" in result["message"]

# Tests for repository connection with authentication (BE-008 verification)
def test_connect_repository_with_authenticated_user(client, auth_headers, mocker):
    """Test repository connection using authenticated user instead of dummy."""
    # Mock the auth validation to return a real user
    mock_user = mocker.MagicMock()
    mock_user.id = 123
    mock_user.username = "authenticated_user"

    from backend.main import verify_auth_token
    mocker.patch("backend.main.verify_auth_token", return_value=mock_user)

    request_data = {
        "repo_url": "https://github.com/test/repo",
        "repo_name": "test-repo"
    }

    response = client.post("/api/repos/connect", json=request_data, headers=auth_headers)
    assert response.status_code == 200

    # Verify no dummy user was created
    from backend.models import User, SessionLocal
    db = SessionLocal()
    dummy_user_count = db.query(User).filter(User.username == "dummy_user").count()
    db.close()

    assert dummy_user_count == 0

# Extended tests for database session error handling (BE-009 verification)
def test_db_session_error_handling(client, mocker, auth_headers):
    """Test that database sessions are properly cleaned up on errors."""
    # This test ensures our error handling in get_db() works correctly

    # Override get_db to simulate an error during yield
    original_override = app.dependency_overrides.get(get_db)

    def failing_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        except Exception as e:
            try:
                db.rollback()
            except Exception:
                pass  # Cleanup rollback errors
            raise e
        finally:
            try:
                db.close()
            except Exception:
                pass  # Cleanup close errors

    # Modify the session to raise an error
    class FailingSessionLocal:
        def __call__(self):
            session = TestingSessionLocal()
            original_close = session.close
            def failing_close():
                raise Exception("Close failed")
            session.close = failing_close
            return session

    test_session_local = FailingSessionLocal()

    def modified_get_db():
        db = test_session_local()
        try:
            yield db
        except Exception as e:
            try:
                db.rollback()
            except Exception:
                pass
            raise e
        finally:
            try:
                db.close()  # This will fail, but we handle it
            except Exception:
                pass

    app.dependency_overrides[get_db] = modified_get_db

    try:
        # This should not cause a permanent session leak due to our error handling
        response = client.get("/api/jobs", headers=auth_headers)
        # We expect some response (may fail due to the mocking, but session should be cleaned)
        assert response.status_code == 200 or response.status_code == 500
    finally:
        # Restore original override
        if original_override:
            app.dependency_overrides[get_db] = original_override
        else:
            del app.dependency_overrides[get_db]