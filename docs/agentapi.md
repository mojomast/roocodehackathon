# FixMyDocs Backend API Reference for Python Agent Development

## Base Configuration
```python
import httpx
import asyncio
from typing import Dict, List, Optional

# Base URL for the FixMyDocs backend API
BASE_URL = "http://localhost:8000"  # Default for local development

# Create HTTP client with timeout
client = httpx.AsyncClient(
    base_url=BASE_URL,
    timeout=httpx.Timeout(30.0, connect=10.0)
)
```

## 1. Authentication Endpoints

### GitHub OAuth Initiation
**Endpoint:** `POST /api/auth/github`  
**Purpose:** Redirect user to GitHub for authentication  

```python
async def initiate_login():
    """
    Redirects user to GitHub OAuth login
    
    Returns:
        Dict[str, str]: Redirect URL or error
    """
    try:
        response = await client.post("api/auth/github")
        return response.json()
    except httpx.HTTPStatusError as e:
        print(f"Login initiation failed: {e.response.status_code}")
        return None
```

**Response:**  
```json
{
  "redirect_url": "https://github.com/login/oauth/authorize?client_id=...",
  "state": "random_state_value"
}
```

### OAuth Callback Processing
**Endpoint:** `GET /auth/github/callback`  
**Purpose:** Handle GitHub OAuth callback (typically handled by frontend, not worker)

## 2. Repository Management

### Connect Repository
**Endpoint:** `POST /api/repos/connect`  
**Purpose:** Link a GitHub repository to the user's account  

```python
async def connect_repository(repo_url: str, access_token: str) -> Dict[str, str]:
    """
    Connect a GitHub repository for documentation processing
    
    Args:
        repo_url (str): GitHub repository URL
        access_token (str): User's GitHub access token
        
    Returns:
        Dict[str, str]: Repository connection details
    """
    headers = {"Authorization": f"Bearer {access_token}"}
    
    data = {
        "repository_url": repo_url
    }
    
    response = await client.post("api/repos/connect", json=data, headers=headers)
    return response.json()
```

**Request Payload:**  
```json
{
  "repository_url": "https://github.com/username/repository"
}
```

**Response:**  
```json
{
  "repo_id": "123",
  "owner": "username",
  "name": "repository",
  "connected_at": "2025-08-29T20:08:44.826Z"
}
```

## 3. Job Management

### Create Documentation Job
**Endpoint:** `POST /api/docs/run`  
**Purpose:** Initiate a new documentation generation job  

```python
async def create_documentation_job(repo_id: int, access_token: str) -> Dict[str, str]:
    """
    Start a documentation generation job for a repository
    
    Args:
        repo_id (int): Repository ID from connect_repository response
        access_token (str): User's GitHub access token
        
    Returns:
        Dict[str, str]: Job details including job ID
    """
    headers = {"Authorization": f"Bearer {access_token}"}
    
    data = {
        "repo_id": repo_id
    }
    
    response = await client.post("api/docs/run", json=data, headers=headers)
    return response.json()
```

**Request Payload:**  
```json
{
  "repo_id": 123
}
```

**Response:**  
```json
{
  "job_id": "456",
  "status": "queued",
  "created_at": "2025-08-29T20:08:44.826Z",
  "repository": {
    "id": 123,
    "name": "repository",
    "owner": "username"
  }
}
```

### Get Job Status
**Endpoint:** `GET /api/jobs/status/{job_id}`  
**Purpose:** Check the current status of a documentation job  

```python
async def get_job_status(job_id: str, access_token: str) -> Dict[str, str]:
    """
    Retrieve the current status of a documentation processing job
    
    Args:
        job_id (str): Job ID from create_documentation_job response
        access_token (str): User's GitHub access token
        
    Returns:
        Dict[str, str]: Current job status and details
    """
    headers = {"Authorization": f"Bearer {access_token}"}
    
    response = await client.get(f"api/jobs/status/{job_id}", headers=headers)
    return response.json()
```

**Response:**  
```json
{
  "job_id": "456",
  "status": "processing",  # Can be: "queued", "processing", "completed", "failed"
  "progress": {
    "stage": "parsing_code",
    "percentage": 75,
    "timestamp": "2025-08-29T20:10:44.826Z"
  },
  "repository": {
    "id": 123,
    "name": "repository",
    "owner": "username"
  },
  "started_at": "2025-08-29T20:09:44.826Z",
  "updated_at": "2025-08-29T20:10:44.826Z"
}
```

### List User Jobs
**Endpoint:** `GET /api/jobs`  
**Purpose:** Get all jobs for the authenticated user  

```python
async def list_user_jobs(access_token: str) -> Dict[str, list]:
    """
    Retrieve all documentation jobs for the current user
    
    Args:
        access_token (str): User's GitHub access token
        
    Returns:
        Dict[str, list]: List of all user jobs
    """
    headers = {"Authorization": f"Bearer {access_token}"}
    
    response = await client.get("api/jobs", headers=headers)
    return response.json()
```

**Response:**  
```json
{
  "jobs": [
    {
      "job_id": "456",
      "status": "completed",
      "repository": {
        "id": 123,
        "name": "repository",
        "owner": "username"
      },
      "created_at": "2025-08-29T20:08:44.826Z",
      "completed_at": "2025-08-29T20:15:44.826Z"
    }
  ],
  "total_jobs": 1
}
```

## Error Handling

```python
async def handle_api_errors(func):
    """
    Decorator for consistent error handling across API calls
    
    Args:
        func: Function to wrap with error handling
        
    Returns:
        Function result or None on error
    """
    try:
        return await func
    except httpx.HTTPStatusError as e:
        print(f"HTTP Error {e.response.status_code}: {e.response.text}")
        return None
    except httpx.ConnectError:
        print("Connection failed. Backend may not be running.")
        return None
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return None
```

## Complete Worker Integration Example

```python
import asyncio
from typing import Dict

class FixMyDocsWorker:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=httpx.Timeout(30.0, connect=10.0)
        )
    
    async def process_job(self, repo_id: int, access_token: str) -> Dict[str, str]:
        """Main workflow for processing a documentation job"""
        
        # Start job
        job_details = await self.create_documentation_job(repo_id, access_token)
        if not job_details:
            return {"error": "Failed to create job"}
        
        job_id = job_details["job_id"]
        
        # Monitor progress
        while True:
            status = await self.get_job_status(job_id, access_token)
            if not status:
                return {"error": "Failed to get job status"}
            
            if status["status"] in ["completed", "failed"]:
                break
                
            await asyncio.sleep(5)  # Wait 5 seconds before checking again
        
        return status
    
    async def create_documentation_job(self, repo_id: int, access_token: str):
        """Concrete implementation of create_documentation_job"""
        # ... implementation from above ...
    
    async def get_job_status(self, job_id: str, access_token: str):
        """Concrete implementation of get_job_status"""
        # ... implementation from above ...
```

## Environment Configuration

Required environment variables for production:
- `BACKEND_BASE_URL`: Base URL for the FixMyDocs backend
- `GITHUB_ACCESS_TOKEN`: GitHub access token for authenticated requests

## Notes for Development

1. **Authentication**: Always include the GitHub access token in the `Authorization: Bearer <token>` header for authenticated endpoints.
2. **Error Handling**: Implement retry logic for network failures and exponential backoff for rate limits.
3. **Async Operations**: Use async/await for all API calls to prevent blocking the worker queue.
4. **Job Monitoring**: Poll the job status endpoint periodically to track progress and handle failures gracefully.
5. **Cleanup**: Close the HTTP client properly when shutting down the worker.

This API documentation provides everything needed for the Python worker to integrate seamlessly with the FixMyDocs backend.