import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import os

from backend.main import app
from backend.models import Base, get_db

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

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Create tables before tests and drop after."""
    Base.metadata.create_all(bind=engine)
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
    from backend.models import User
    from backend.main import SessionLocal

    db = SessionLocal()
    before_count = db.query(User).count()
    db.close()

    client.get("/auth/github/callback?code=test_code")

    # Count users after
    db = SessionLocal()
    after_count = db.query(User).count()
    db.close()

    assert after_count == before_count + 1

def test_repo_association_with_user(client, auth_headers):
    """Test repo association with dummy user."""
    # The connect endpoint creates a dummy user internally

    from backend.models import User, Repo
    from backend.main import SessionLocal

    response = client.post("/api/repos/connect", json={
        "repo_url": "https://github.com/test/repo",
        "repo_name": "test-repo"
    }, headers=auth_headers)

    assert response.status_code == 200

    db = SessionLocal()
    repo = db.query(Repo).first()
    user = db.query(User).filter(User.username == "dummy_user").first()
    db.close()

    assert repo is not None
    assert user is not None
    assert repo.user_id == user.id

def test_job_creation_and_lifecycle(client, auth_headers):
    """Test job creation and status tracking."""
    from backend.models import Job
    from backend.main import SessionLocal

    # Create repo
    client.post("/api/repos/connect", json={
        "repo_url": "https://github.com/test/repo",
        "repo_name": "test-repo"
    }, headers=auth_headers)

    # Create job
    response = client.post("/api/docs/run", json={"repo_id": 1}, headers=auth_headers)
    job_id = response.json()["job_id"]

    db = SessionLocal()
    job = db.query(Job).filter(Job.id == job_id).first()
    db.close()

    assert job is not None
    assert job.repo_id == 1
    assert job.status == "pending"

    # Test status endpoint
    status_resp = client.get(f"/api/jobs/status/{job_id}", headers=auth_headers)
    assert status_resp.status_code == 200
    assert status_resp.json()["status"] == "pending"