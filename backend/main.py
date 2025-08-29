from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Dict, Annotated
from pydantic import BaseModel # Import BaseModel
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Header, Security
from starlette.responses import RedirectResponse
import httpx # Import httpx for making HTTP requests

from backend.models import Base, engine, get_db, User, Repo, Job
import os

# Initialize FastAPI application
app = FastAPI(
    title="FixMyDocs Backend",
    description="Backend API for FixMyDocs, handling documentation generation and GitHub integration.",
    version="0.1.0",
)

# Create database tables on startup
@app.on_event("startup")
def on_startup():
    """
    Event handler that runs when the FastAPI application starts up.
    Creates all database tables if they don't already exist.
    """
    Base.metadata.create_all(bind=engine)

# Security dependency
security = HTTPBearer()

async def verify_auth_token(x_auth_token: Annotated[str | None, Header()] = None):
    """
    Middleware to verify the X-Auth-Token header.
    For now, it accepts any value. If not present, it returns 401 Unauthorized.
    """
    if x_auth_token is None:
        raise HTTPException(status_code=401, detail="Unauthorized: X-Auth-Token header missing")
    # In a real application, you would validate the token here (e.g., against a database, JWT verification)
    return x_auth_token

@app.get("/")
def read_root():
    """
    Root endpoint for the API.
    Returns a simple welcome message.
    """
    return {"message": "Welcome to the FixMyDocs Backend API!"}

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
    email = github_user_data.get("email") # GitHub might not always provide email directly

    if not github_id or not username:
        raise HTTPException(status_code=500, detail="Could not retrieve essential user data from GitHub.")

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

    # Redirect to frontend dashboard
    return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)

class RepoConnectRequest(BaseModel):
    repo_url: str
    repo_name: str # Assuming repo_name is also part of the details

@app.post("/api/repos/connect", dependencies=[Depends(verify_auth_token)])
async def connect_repository(request: RepoConnectRequest, db: Session = Depends(get_db)):
    """
    Connects a new repository to the system.
    Accepts repository URL and name, creates a Repo record, and returns its ID.
    """
    # For now, let's create a dummy user if they don't exist
    # TODO: Replace with actual user authentication and association
    dummy_user = db.query(User).filter(User.username == "dummy_user").first()
    if not dummy_user:
        dummy_user = User(github_id="dummy_github_id", username="dummy_user", access_token="dummy_token")
        db.add(dummy_user)
        db.commit()
        db.refresh(dummy_user)

    new_repo = Repo(user_id=dummy_user.id, repo_url=request.repo_url, repo_name=request.repo_name, status="connected")
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

    new_job = Job(repo_id=request.repo_id, status="pending", created_at=datetime.utcnow())
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

def github_app_fork_repo(repo_url: str) -> Dict:
    """
    Placeholder for forking a GitHub repository via the GitHub App.
    """
    print(f"STUB: Forking repository: {repo_url}")
    return {"status": "success", "message": "Repository forked (stub)"}

def github_app_create_pull_request(repo_url: str, branch_name: str, commit_message: str) -> Dict:
    """
    Placeholder for creating a pull request with generated documentation.
    """
    print(f"STUB: Creating PR for {repo_url} on branch {branch_name} with message: {commit_message}")
    return {"status": "success", "message": "Pull request created (stub)"}

def github_app_handle_webhook(payload: Dict, headers: Dict) -> Dict:
    """
    Placeholder for handling GitHub webhook events.
    """
    print("STUB: Handling GitHub webhook event.")
    # In a real scenario, verify signature, parse payload, and dispatch to appropriate handlers
    return {"status": "success", "message": "Webhook handled (stub)"}