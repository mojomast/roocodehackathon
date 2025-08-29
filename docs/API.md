# FixMyDocs API Reference

This document provides comprehensive API documentation for the FixMyDocs application, a SaaS documentation improvement agent.

## Base URL

```
https://api.fixmydocs.com
```

For local development:
```
http://localhost:8000
```

## Authentication

All API requests require authentication using GitHub OAuth2. The application uses session-based authentication after OAuth completion.

### OAuth Flow

1. `GET /auth/github` - Redirects to GitHub OAuth authorization
2. `GET /auth/github/callback` - Handles OAuth callback and creates user session
3. User session maintained via HTTP cookies

## Core Endpoints

### Repository Management

#### Connect Repository
**POST** `/api/repos/connect`

Connects a GitHub repository for documentation analysis.

**Request Body:**
```json
{
  "repository_url": "https://github.com/username/repository-name",
  "permissions": {
    "contents": "read",
    "pull_requests": "write"
  }
}
```

**Response (200):**
```json
{
  "id": 123,
  "github_id": "MDEwOlJlcG9zaXRvcnkxMjM0NTY3ODk=",
  "name": "username/repository-name",
  "status": "connected",
  "connected_at": "2025-08-29T21:30:00Z"
}
```

**Error Responses:**
- `400 Bad Request` - Invalid repository URL or missing permissions
- `401 Unauthorized` - User not authenticated
- `409 Conflict` - Repository already connected
- `422 Unprocessable Entity` - GitHub API error

#### List Connected Repositories
**GET** `/api/repos`

Returns all repositories connected by the authenticated user.

**Query Parameters:**
- `limit` (optional): Number of results to return (default: 20, max: 100)
- `offset` (optional): Pagination offset (default: 0)

**Response (200):**
```json
{
  "repositories": [
    {
      "id": 123,
      "name": "username/repository-name",
      "status": "connected",
      "last_job_id": 456,
      "connected_at": "2025-08-29T21:30:00Z",
      "updated_at": "2025-08-29T21:45:00Z"
    }
  ],
  "total": 1,
  "has_more": false
}
```

#### Disconnect Repository
**DELETE** `/api/repos/{id}`

Disconnects a repository from the user's account.

**Response (204):** No Content

**Error Responses:**
- `404 Not Found` - Repository not found or not owned by user

### Job Management

#### Create Documentation Job
**POST** `/api/jobs`

Initiates a new documentation analysis job for a connected repository.

**Request Body:**
```json
{
  "repository_id": 123,
  "job_type": "docstring_generation", // or "readme_update", "inline_comments"
  "options": {
    "target_files": ["*.py", "*.js"],
    "exclude_patterns": ["tests/", "*.test.*"],
    "documentation_style": "google"
  }
}
```

**Response (201):**
```json
{
  "id": 456,
  "repository_id": 123,
  "status": "pending",
  "job_type": "docstring_generation",
  "created_at": "2025-08-29T21:30:00Z",
  "started_at": null,
  "completed_at": null
}
```

**Error Responses:**
- `400 Bad Request` - Invalid job parameters
- `404 Not Found` - Repository not found

#### List Jobs
**GET** `/api/jobs`

Returns all jobs for the authenticated user.

**Query Parameters:**
- `status` (optional): Filter by status (`pending`, `running`, `completed`, `failed`)
- `repository_id` (optional): Filter by repository
- `limit` (optional): Number of results (default: 20)
- `offset` (optional): Pagination offset (default: 0)

**Response (200):**
```json
{
  "jobs": [
    {
      "id": 456,
      "repository_id": 123,
      "repository_name": "username/repo",
      "status": "completed",
      "job_type": "docstring_generation",
      "progress": 100,
      "created_at": "2025-08-29T21:30:00Z",
      "completed_at": "2025-08-29T21:45:00Z",
      "pull_request_url": "https://github.com/username/repo/pull/42"
    }
  ],
  "total": 1,
  "has_more": false
}
```

#### Get Job Details
**GET** `/api/jobs/{id}`

Returns detailed information about a specific job.

**Response (200):**
```json
{
  "id": 456,
  "repository_id": 123,
  "repository_name": "username/repo",
  "status": "completed",
  "job_type": "docstring_generation",
  "progress": 100,
  "options": {
    "target_files": ["*.py"],
    "documentation_style": "google"
  },
  "results": {
    "files_processed": 15,
    "changes_made": 23,
    "pull_request_number": 42,
    "pull_request_url": "https://github.com/username/repo/pull/42"
  },
  "logs": [
    "2025-08-29T21:31:00Z: Starting repository clone",
    "2025-08-29T21:32:00Z: Parsing completed",
    "2025-08-29T21:44:00Z: Pull request created"
  ],
  "created_at": "2025-08-29T21:30:00Z",
  "started_at": "2025-08-29T21:31:00Z",
  "completed_at": "2025-08-29T21:45:00Z"
}
```

#### Get Job Status (Polling)
**GET** `/api/jobs/status/{id}`

Lightweight endpoint for polling job status.

**Response (200):**
```json
{
  "id": 456,
  "status": "running",
  "progress": 65,
  "current_step": "Generating documentation",
  "updated_at": "2025-08-29T21:40:00Z"
}
```

**Error Responses:**
- `404 Not Found` - Job not found

### User Management

#### Get User Profile
**GET** `/api/user/profile`

Returns the current user's profile information.

**Response (200):**
```json
{
  "id": 789,
  "github_id": 987654321,
  "login": "githubuser",
  "name": "GitHub User",
  "email": "user@example.com",
  "avatar_url": "https://avatars.githubusercontent.com/u/987654321?v=4",
  "created_at": "2025-08-29T21:00:00Z"
}
```

#### Update User Preferences
**PUT** `/api/user/preferences`

Updates user preferences and settings.

**Request Body:**
```json
{
  "preferred_documentation_style": "google",
  "notification_settings": {
    "email_on_completion": true,
    "github_notifications": true
  },
  "webhook_urls": [
    "https://example.com/webhook"
  ]
}
```

**Response (200):**
```json
{
  "message": "Preferences updated successfully"
}
```

### Health Check

#### Service Health
**GET** `/health`

Returns the health status of the service.

**Response (200):**
```json
{
  "status": "healthy",
  "timestamp": "2025-08-29T21:30:00Z",
  "version": "1.0.0",
  "services": {
    "database": "healthy",
    "worker_queue": "healthy",
    "github_api": "healthy"
  }
}
```

### Error Handling

All endpoints return consistent error responses:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      "field": "specific_field_error"
    }
  },
  "timestamp": "2025-08-29T21:30:00Z"
}
```

### Rate Limiting

- **Authenticated Requests**: 1000 requests per hour
- **Public Endpoints**: 100 requests per hour

Rate limit headers are included in all responses:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 995
X-RateLimit-Reset: 1630274400
```

### Pagination

List endpoints support pagination using query parameters:
- `limit`: Number of items to return (max 100)
- `offset`: Starting offset for results

Response includes pagination metadata:
```json
{
  "data": [...],
  "total": 150,
  "has_more": true,
  "next_offset": 20
}
```

## Job Lifecycle

Documentation jobs progress through the following states:

1. **pending** - Job created, waiting for worker
2. **running** - Worker has started processing
   - Sub-steps: cloning, parsing, analyzing, generating, creating PR
3. **completed** - Job finished successfully
4. **failed** - Job failed with error

Jobs can be monitored using the `/api/jobs/status/{id}` endpoint for real-time updates.

## GitHub App Integration

The application integrates with GitHub through OAuth2 and GitHub Apps:

### OAuth Permissions
- `read:user` - Access user profile information
- `repo` - Access repositories

### Repository Access
- Requires repository URL input
- Validates repository existence and user access
- Creates and manages pull requests on behalf of users

### Pull Request Management
- Creates branches with systematic naming (`fixmydocs/docs-{timestamp}`)
- Commits documentation changes with descriptive messages
- Provides clean diffs for review
- Includes job execution details in PR descriptions

## Security Considerations

### Authentication
- Session-based authentication with secure cookies
- HTTPS required for production
- Token expiration and refresh mechanisms

### Input Validation
- Repository URLs validated against GitHub patterns
- File paths sanitized to prevent directory traversal
- All user inputs validated and sanitized

### Rate Limiting
- Protects against abuse
- Graduated rate limits based on user type
- Burst protection for heavy usage periods

---

For additional information, see the [Agent API Reference](agentapi.md) for worker-specific integrations.