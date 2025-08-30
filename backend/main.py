from fastapi import FastAPI, Depends, HTTPException, status, Lifespan, Request
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timezone
from typing import Dict, Annotated
from pydantic import BaseModel # Import BaseModel
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Header, Security
from starlette.responses import RedirectResponse
import httpx # Import httpx for making HTTP requests
from contextlib import asynccontextmanager

from backend.models import Base, engine, get_db, User, Repo, Job
import os
import hmac
import hashlib

# Lifespan event handler using asynccontextmanager
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event handler that runs when the FastAPI application starts up and shuts down.
    Creates all database tables if they don't already exist during startup.
    """
    # Startup
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown (if needed in the future)

# Initialize FastAPI application
app = FastAPI(
    title="FixMyDocs Backend",
    description="Backend API for FixMyDocs, handling documentation generation and GitHub integration.",
    version="0.1.0",
    lifespan=lifespan,
)

# Database tables are now created via lifespan event handler above

# Security dependency
security = HTTPBearer()

async def verify_auth_token(x_auth_token: Annotated[str | None, Header()] = None, db: Session = Depends(get_db)):
    """
    Middleware to verify the X-Auth-Token header by validating against the database.
    Looks up the access_token in the User table. If not found, returns 401 Unauthorized.
    Returns the authenticated User object on success.
    """
    if not x_auth_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized: X-Auth-Token header missing")

    try:
        user = db.query(User).filter(User.access_token == x_auth_token).one_or_none()
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized: Invalid access token")
        
        # Optional: Check for token expiration if you add an expiry date to the user model
        # if user.token_expires_at and user.token_expires_at < datetime.now(timezone.utc):
        #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized: Token has expired")

        return user
    except SQLAlchemyError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error during token validation")

@app.get("/")
def read_root():
    """
    Root endpoint for the API.
    Returns a simple welcome message.
    """
    return {"message": "Welcome to the FixMyDocs Backend API!"}

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint to verify database connectivity.
    Returns a 200 OK response if the database is reachable, otherwise 503 Service Unavailable.
    """
    try:
        # Simple query to check database connection
        db.execute("SELECT 1")
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database connection error: {e}")

@app.get("/api/auth/github")
async def github_auth(): # This route is excluded from authentication
    """
    Redirects the user to GitHub for OAuth authentication.
    """
    github_client_id = os.getenv("GITHUB_CLIENT_ID")
    if not github_client_id:
        raise HTTPException(status_code=500, detail="GitHub Client ID not configured.")

    github_authorize_url = "https://github.com/login/oauth/authorize"
    redirect_uri = os.getenv("GITHUB_CALLBACK_URL", "http://localhost:8000/auth/github/callback") # Default for local development
    scope = "user:email" # Requesting user email access

    return RedirectResponse(
        url=f"{github_authorize_url}?client_id={github_client_id}&redirect_uri={redirect_uri}&scope={scope}",
        status_code=status.HTTP_302_FOUND
    )

@app.get("/auth/github/callback")
async def github_callback(code: str, db: Session = Depends(get_db)): # This route is excluded from authentication
    """
    Handles the GitHub OAuth callback, exchanges the code for an access token,
    fetches user data, and creates/updates the user in the database.
    """
    github_client_id = os.getenv("GITHUB_CLIENT_ID")
    github_client_secret = os.getenv("GITHUB_CLIENT_SECRET")
    if not github_client_id or not github_client_secret:
        raise HTTPException(status_code=500, detail="GitHub Client ID or Secret not configured.")

    # Exchange code for access token
    token_url = "https://github.com/login/oauth/access_token"
    headers = {"Accept": "application/json"}
    data = {
        "client_id": github_client_id,
        "client_secret": github_client_secret,
        "code": code,
        "redirect_uri": os.getenv("GITHUB_CALLBACK_URL", "http://localhost:8000/auth/github/callback")
    }

    async with httpx.AsyncClient() as client:
        token_response = await client.post(token_url, headers=headers, json=data)
        token_response.raise_for_status()
        token_data = token_response.json()
        access_token = token_data.get("access_token")

    if not access_token:
        raise HTTPException(status_code=400, detail="Failed to obtain access token from GitHub.")

    # Fetch user profile from GitHub
    user_url = "https://api.github.com/user"
    user_headers = {"Authorization": f"token {access_token}"}
    async with httpx.AsyncClient() as client:
        user_response = await client.get(user_url, headers=user_headers)
        user_response.raise_for_status()
        github_user_data = user_response.json()

    github_id = str(github_user_data.get("id"))
    username = github_user_data.get("login")
    # Handle GitHub email - may be None, so fetch if necessary
    email = github_user_data.get("email")
    if not email:
        # Fetch user emails if primary email not provided
        emails_url = "https://api.github.com/user/emails"
        async with httpx.AsyncClient() as client:
            emails_response = await client.get(emails_url, headers=user_headers)
            emails_response.raise_for_status()
            emails = emails_response.json()
            # Find primary email or use first available
            primary_email = next((e["email"] for e in emails if e.get("primary")), None)
            email = primary_email or (emails[0]["email"] if emails else None)

    # Check if essential data is available (email can be optional)
    if not github_id or not username:
        raise HTTPException(status_code=500, detail="Could not retrieve essential user data from GitHub.")

    # BE-012: Wrap user database operations in try-except for transaction rollback on failure
    try:
        # Find or create user in database
        user = db.query(User).filter(User.github_id == github_id).first()
        if not user:
            user = User(github_id=github_id, username=username, access_token=access_token, email=email)
            db.add(user)
        else:
            user.username = username
            user.access_token = access_token
            user.email = email
        db.commit()
        db.refresh(user)
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error during user creation/update: {str(e)}")

    # Redirect to frontend dashboard
    return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)

class RepoConnectRequest(BaseModel):
    repo_url: str
    repo_name: str # Assuming repo_name is also part of the details

@app.post("/api/repos/connect")
async def connect_repository(request: RepoConnectRequest, user: User = Depends(verify_auth_token), db: Session = Depends(get_db)):
    """
    Connects a new repository to the system.
    Accepts repository URL and name, creates a Repo record, and returns its ID.
    Uses the authenticated user for association instead of dummy user.
    """
    new_repo = Repo(user_id=user.id, repo_url=request.repo_url, repo_name=request.repo_name, status="connected")
    db.add(new_repo)
    db.commit()
    db.refresh(new_repo)

    return {"message": f"Repository {request.repo_name} connected successfully", "repo_id": new_repo.id}

# Placeholder for Celery task dispatch
# In a real scenario, you would import and call the Celery task here
def process_documentation_job(job_id: int):
    """
    Placeholder function to simulate dispatching a job to Celery worker.
    """
    print(f"Dispatching job {job_id} to Celery worker...")
    # TODO: Integrate with actual Celery task: process_documentation_job.delay(job_id)

class JobCreateRequest(BaseModel):
    repo_id: int

@app.post("/api/docs/run", dependencies=[Depends(verify_auth_token)])
async def trigger_documentation_run(request: JobCreateRequest, db: Session = Depends(get_db)):
    """
    Triggers a documentation generation run for a given repository.
    Accepts a repository ID, creates a Job record, and dispatches a task to the Celery worker.
    """
    repo = db.query(Repo).filter(Repo.id == request.repo_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")

    new_job = Job(repo_id=request.repo_id, status="pending", created_at=datetime.now(timezone.utc))
    db.add(new_job)
    db.commit()
    db.refresh(new_job)

    # Dispatch task to Celery worker
    process_documentation_job(new_job.id) # Call the placeholder function

    return {"message": "Documentation run triggered", "job_id": new_job.id, "status": "pending"}

@app.get("/api/jobs/status/{job_id}", dependencies=[Depends(verify_auth_token)])
async def get_job_status(job_id: int, db: Session = Depends(get_db)):
    """
    Retrieves the current status of a documentation job.
    """
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return {"job_id": job.id, "status": job.status, "created_at": job.created_at, "updated_at": job.updated_at}

@app.get("/api/jobs", dependencies=[Depends(verify_auth_token)])
async def get_all_jobs(db: Session = Depends(get_db)):
    """
    Retrieves a list of all documentation jobs.
    """
    jobs = db.query(Job).all()
    return [{"job_id": job.id, "repo_id": job.repo_id, "status": job.status, "created_at": job.created_at, "updated_at": job.updated_at} for job in jobs]

# GitHub App Integration Stubs
# These functions would interact with the GitHub API for operations like:
# - Forking a repository
# - Creating a pull request with generated documentation
# - Handling webhooks from GitHub (e.g., push events, PR events)

async def github_app_fork_repo(repo_url: str, access_token: str) -> Dict:
    """
    Forks a GitHub repository using the GitHub API with httpx.
    Parses the repository URL to extract owner/repo, then makes a POST request to create a fork.
    """
    # Parse repository from URL robustly
    owner, repo_name = parse_github_repo(repo_url)
    if not owner or not repo_name:
        return {"status": "error", "message": "Invalid repository URL format"}

    fork_url = f"https://api.github.com/repos/{owner}/{repo_name}/forks"
    headers = {
        "Authorization": f"token {access_token}",
        "Accept": "application/vnd.github+json"
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(fork_url, headers=headers)
            response.raise_for_status()
            forked_repo = response.json()
            return {
                "status": "success",
                "message": f"Repository forked to {forked_repo.get('html_url')}",
                "forked_repo": forked_repo
            }
        except httpx.HTTPStatusError as e:
            return {"status": "error", "message": f"Fork failed: {e.response.status_code} - {e.response.text}"}
        except Exception as e:
            return {"status": "error", "message": f"Error forking repository: {str(e)}"}

async def github_app_create_pull_request(repo_url: str, branch_name: str, commit_message: str, access_token: str) -> Dict:
    """
    Creates a pull request using the GitHub API with httpx.
    Creates a PR from the specified branch to the default branch with the commit message as body.
    """
    # Parse repository
    owner, repo_name = parse_github_repo(repo_url)
    if not owner or not repo_name:
        return {"status": "error", "message": "Invalid repository URL format"}

    pulls_url = f"https://api.github.com/repos/{owner}/{repo_name}/pulls"
    headers = {
        "Authorization": f"token {access_token}",
        "Accept": "application/vnd.github+json"
    }
    pr_data = {
        "title": f"Add generated documentation ({branch_name})",
        "head": branch_name,
        "base": "main",  # Assume default branch is main
        "body": commit_message
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(pulls_url, headers=headers, json=pr_data)
            response.raise_for_status()
            pr_info = response.json()
            return {
                "status": "success",
                "message": f"Pull request created: {pr_info.get('html_url')}",
                "pull_request": pr_info
            }
        except httpx.HTTPStatusError as e:
            return {"status": "error", "message": f"PR creation failed: {e.response.status_code} - {e.response.text}"}
        except Exception as e:
            return {"status": "error", "message": f"Error creating PR: {str(e)}"}

async def github_app_handle_webhook(payload: Dict, headers: Dict) -> Dict:
    """
    Handles basic GitHub webhook events using httpx for any additional API calls if needed.
    Verifies event type and returns appropriate response. For actual signature verification,
    additional crypto libraries and webhook secret would be required.
    """
    event_type = headers.get("X-GitHub-Event", "unknown")
    signature = headers.get("X-Hub-Signature-256", "")

    print(f"Handling GitHub webhook event: {event_type}")
    if not signature:
        return {"status": "error", "message": "Missing webhook signature"}

    # For basic functionality, assume signature is valid and process the event
    if event_type == "push":
        # Example: could check if push is to docs branch, trigger rebuild
        branch = payload.get("ref", "").split("/")[-1]
        return {"status": "success", "message": f"Push event handled for branch {branch}"}
    elif event_type == "pull_request":
        action = payload.get("action")
        return {"status": "success", "message": f"Pull request {action} event handled"}
    else:
        return {"status": "success", "message": f"Unknown event {event_type} received (basic handling)"}

def parse_github_repo(repo_url: str) -> tuple[str | None, str | None]:
    """
    Normalize and parse a GitHub repo URL into (owner, repo).
    Supports:
    - https://github.com/owner/repo[.git]
    - http(s)://github.com/owner/repo/
    - git@github.com:owner/repo[.git]
    - owner/repo
    """
    try:
        url = repo_url.strip()
        # Remove trailing .git
        if url.endswith('.git'):
            url = url[:-4]

        # SSH form
        if url.startswith('git@github.com:'):
            rest = url.split(':', 1)[1]
            parts = rest.split('/')
            if len(parts) >= 2:
                return parts[0], parts[1]

        # Full HTTPS URL
        if 'github.com' in url:
            parts = [p for p in url.split('/') if p]
            # Find index of 'github.com'
            if 'github.com' in parts:
                idx = parts.index('github.com')
                tail = parts[idx + 1:]
            else:
                # Might be already just owner/repo
                tail = parts[-2:]
            tail = [p for p in tail if p]
            if len(tail) >= 2:
                return tail[0], tail[1]

        # owner/repo form
        parts = [p for p in url.split('/') if p]
        if len(parts) == 2 and all(parts):
            return parts[0], parts[1]
    except Exception:
        pass
    return None, None

@app.get("/api/repos", dependencies=[Depends(verify_auth_token)])
async def list_repositories(user: User = Depends(verify_auth_token), db: Session = Depends(get_db)):
    """
    Returns repositories connected by the authenticated user.
    """
    repos = db.query(Repo).filter(Repo.user_id == user.id).all()
    return [
        {
            "id": r.id,
            "repo_url": r.repo_url,
            "repo_name": r.repo_name,
            "status": r.status,
        }
        for r in repos
    ]

@app.post("/api/github/webhook")
async def github_webhook(request: Request):
    """
    GitHub webhook endpoint with HMAC SHA256 signature verification.
    """
    webhook_secret = os.getenv("GITHUB_WEBHOOK_SECRET")
    if not webhook_secret:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Webhook secret not configured")

    raw_body = await request.body()
    signature_header = request.headers.get("X-Hub-Signature-256")
    if not signature_header:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="X-Hub-Signature-256 header is missing")

    expected_signature = f"sha256={hmac.new(webhook_secret.encode(), raw_body, hashlib.sha256).hexdigest()}"

    if not hmac.compare_digest(expected_signature, signature_header):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid webhook signature")

    payload = await request.json()
    result = await github_app_handle_webhook(payload, dict(request.headers))
    return result