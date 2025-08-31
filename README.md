# FixMyDocs - AI-Powered Documentation Agent

FixMyDocs is a SaaS documentation agent that connects to GitHub repositories and automatically generates Pull Requests to improve documentation, including READMEs, docstrings, and inline comments. This project was built for the Roo Code Hackathon by Team Yugoslavia.

## 🚀 Project Status

The project is fully functional with a complete microservices architecture including a Next.js frontend, Python FastAPI backend, and Python AI worker. All critical bugs have been resolved, and all major features are implemented and working. All 67 documented issues have been resolved, and the application is now production-ready.

### ✅ Implemented Features

- **Multi-Provider LLM Support**: Integrates with both OpenAI and Anthropic models for flexible AI-powered code analysis.
- **Advanced Code Analysis**: Utilizes an AST-based engine for in-depth analysis of Python and JavaScript code.
- **Automated Pull Requests**: Generates detailed pull requests with comprehensive summaries of documentation changes.
- **GitHub OAuth Authentication**: Complete OAuth2 flow for user login via GitHub.
- **Repository Documentation**: GitHub repository integration for documentation analysis and improvement.
- **Job Management**: End-to-end job processing pipeline for documentation tasks.
- **Worker Processing**: AI-powered documentation generation with Celery-based task queuing.
- **Database Integration**: PostgreSQL database with SQLAlchemy ORM for data persistence.
- **API Endpoints**: Comprehensive REST API for repository management, job processing, and authentication.
- **Security Features**: XSS prevention, authentication middleware, and input validation.
- **Testing Infrastructure**: Pytest for backend/worker, Jest for frontend with comprehensive test suites.
- **Docker Containerization**: Full containerization with Docker Compose for development and production.
- **API Key Management**: Securely manage API keys for programmatic access.
- **OpenRouter Support**: Integration with OpenRouter for a wider selection of LLM providers.
- **Model Selection**: Users can select specific providers and models for documentation jobs.

## 🏛️ Architecture

The application is designed with a microservices architecture, containerized with Docker.

### 1. Frontend (Next.js 14)
-   **Framework**: Next.js 14 with Tailwind CSS.
-   **Location**: `/frontend`
-   **Key Pages**:
    -   `/login`: Handles GitHub OAuth redirection.
    -   `/dashboard`: Displays an overview and job statistics.
    -   `/repos`: Allows users to connect and manage their repositories.
    -   `/jobs`: Tracks the status of documentation generation jobs.
    -   `/keys`: Manage your API keys.

### 2. Backend (Python FastAPI)
-   **Framework**: FastAPI with PostgreSQL (via SQLAlchemy).
-   **Location**: `/backend`
-   **Core API Endpoints**:

    **Authentication:**
    - `POST /api/auth/github` - Initiates GitHub OAuth2 login flow
    - `GET /auth/github/callback` - OAuth callback handler for GitHub login

    **Repository Management:**
    - `POST /api/repos/connect` - Connect a GitHub repository for analysis
    - `GET /api/repos` - List user's connected repositories
    - `DELETE /api/repos/{id}` - Disconnect a repository

    **Job Management:**
    - `POST /api/jobs` - Create and start a documentation analysis job
    - `GET /api/jobs` - List all job statuses for user
    - `GET /api/jobs/{id}` - Get detailed job status and results
    - `GET /api/jobs/status/{id}` - Check specific job status (polling endpoint)
    
        **API Key Management:**
        - `GET /api/keys` - List all API keys for the user
        - `POST /api/keys` - Create a new API key
        - `DELETE /api/keys/{id}` - Revoke an API key

    **User Management:**
    - `GET /api/user/profile` - Get current user profile information
    - `PUT /api/user/preferences` - Update user preferences

    **Health Checks:**
    - `GET /health` - Service health check endpoint

    **GitHub Webhook:**
    - `POST /api/github/webhook` - Receives GitHub events. Requests must include `X-Hub-Signature-256` and will be verified via HMAC SHA-256 with `GITHUB_WEBHOOK_SECRET`. Invalid signatures return 401.

For detailed API documentation including Python examples for the worker agent integration, see [Agent API Reference](docs/agentapi.md).

## 📚 Documentation

This project maintains comprehensive documentation for all components:

| File | Purpose | Audience |
|------|---------|----------|
| [`docs/API.md`](docs/API.md) | Complete REST API reference with endpoints, examples, and authentication | Backend/frontend developers, API consumers |
| [`docs/agentapi.md`](docs/agentapi.md) | Python worker integration guide with code examples | Python developers, worker integrators |
| [`docs/CONTRIBUTING.md`](docs/CONTRIBUTING.md) | Development setup, testing, and contribution guidelines | All contributors |
| [`docs/DEVLOG.md`](docs/DEVLOG.md) | Project development milestones and feature implementations | Team members, stakeholders |

For questions about specific documentation files, refer to their contents or check the [Contributing Guide](docs/CONTRIBUTING.md) for development setup and testing information.

### 3. Worker (Python AI Agent)
-   **Framework**: Celery for background task processing.
-   **Location**: `/worker`
-   **Core Modules**:
    -   `worker.py`: Listens for and executes documentation jobs from the queue.
    -   `job_manager.py`: Manages the lifecycle of a job.
    -   `repo_manager.py`: Handles safe cloning and management of repositories.
    -   `CodeAnalyzer` (`parser.py`): A modular, AST-based parser for Python and JavaScript that provides deep code analysis.
    -   `AIOrchestrator` (`ai_orchestrator.py`): A flexible interface supporting multiple LLM providers, including OpenAI and Anthropic, for generating high-quality documentation.
    -   `Patcher` (`patcher.py`): An enhanced module for creating and managing GitHub pull requests with detailed, automated summaries.
    -   `logger.py`: Logs updates to `DEVLOG.md`.

## 🛠️ Getting Started

1.  **Prerequisites**: Docker and Docker Compose must be installed.
2.  **Environment Variables**: Copy the `.env.template` files in `/backend`, `/frontend`, and `/worker` to `.env` files and populate them with the necessary credentials (e.g., GitHub OAuth App credentials, database connection string).
3.  **Development vs Production**:
    -   **Development**: Use default localhost URIs in `.env` files (e.g., `http://localhost:8000` for API URL). This setup runs all services locally via Docker Compose.
    -   **Production**: Update `.env` files with production URIs (e.g., production GitHub OAuth callback URL, external database URL). Use individual Docker builds with the provided `infra/` Dockerfiles.
4.  **Python Virtual Environment (optional but recommended)**:
    ```powershell
    # From repo root on Windows PowerShell
    python -m venv .venv
    .\.venv\Scripts\Activate.ps1
    python -m pip install -U pip
    pip install -r backend\requirements.txt -r worker\requirements.txt
    ```

5.  **Build and Run**:
    ```bash
    # Development (all services)
    docker-compose up --build

    # Production (build individual services)
    docker build -f infra/backend.Dockerfile -t fixmydocs-backend .
    docker build -f infra/frontend.Dockerfile -t fixmydocs-frontend .
    docker build -f infra/worker.Dockerfile -t fixmydocs-worker .
    ```
6.  **Access**:
    -   Frontend: `http://localhost:3000`
    -   Backend API Docs: `http://localhost:8000/docs`

## 🔒 Security & Webhooks

- Webhook endpoint: `POST /api/github/webhook`
- Required header: `X-Hub-Signature-256`
- Secret: set `GITHUB_WEBHOOK_SECRET` in backend `.env`

Example backend `.env` additions:
```env
GITHUB_WEBHOOK_SECRET=dev_secret_change_me
```

Local test (example):
```
echo -n '{"zen":"Keep it logically awesome."}' > payload.json
# Compute HMAC using your secret and send with header (pseudo, compute signature in your tool)
```

## Note for the Team

Hey everyone,

I've gotten the application to a stable state where the frontend, backend, and worker services are all running and communicating correctly. The recent CORS and database migration issues have been resolved.

I have to head out to jam with my band, but I wanted to leave some notes on where I left off and what's next. Please keep hacking on this!

**Where I left off:**
*   The application is fully running. You can access the frontend at `http://localhost:3000`.
*   The database migration race condition has been fixed by ensuring transactions are committed in the `backend/migrate.py` script.

**What's left to do:**
*   Please refer to the `IMPROVEMENT_BACKLOG.md` for the next steps. The key items are:
    *   Job cancellation and idempotency
    *   Unify Job schema across backend and worker
    *   Robust OAuth state/PKCE and session separation from GitHub token
    *   Error reporting and traceability
    *   Rate limiting and basic abuse protection
    *   Parser hardening for non-Python repos
    *   Frontend performance and config cleanup
    *   Accessibility and SEO improvements
    *   Developer experience enhancements
    *   Documentation accuracy updates
    *   Health checks for all services and graceful shutdown for worker
    *   Observability: request/job metrics and traces; error budgets
    *   CI: run linters, type-checkers, unit/integration tests; artifact build
    *   Containers: resource caps and minimal images
