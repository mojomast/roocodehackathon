# FixMyDocs - AI-Powered Documentation Agent

FixMyDocs is a SaaS documentation agent that connects to GitHub repositories and automatically generates Pull Requests to improve documentation, including READMEs, docstrings, and inline comments. This project was built for the Roo Code Hackathon by Team Yugoslavia.

## 🚀 Project Status

The project is fully functional with a complete microservices architecture including a Next.js frontend, Python FastAPI backend, and Python AI worker. All critical bugs have been resolved, and all major features are implemented and working.

### ✅ Implemented Features

- **GitHub OAuth Authentication**: Complete OAuth2 flow for user login via GitHub
- **Repository Documentation**: GitHub repository integration for documentation analysis and improvement
- **Job Management**: End-to-end job processing pipeline for documentation tasks
- **Worker Processing**: AI-powered documentation generation with Celery-based task queuing
- **Database Integration**: PostgreSQL database with SQLAlchemy ORM for data persistence
- **API Endpoints**: Comprehensive REST API for repository management, job processing, and authentication
- **Security Features**: XSS prevention, authentication middleware, and input validation
- **Testing Infrastructure**: Pytest for backend/worker, Jest for frontend with comprehensive test suites
- **Docker Containerization**: Full containerization with Docker Compose for development and production

- **Frontend**: Complete UI with React error boundaries, SEO optimization, and real-time data display
- **Backend**: Production-ready API with GitHub OAuth, repository management, and job orchestration
- **Worker**: Functional AI documentation pipeline with repository cloning, code analysis, and PR creation

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

    **User Management:**
    - `GET /api/user/profile` - Get current user profile information
    - `PUT /api/user/preferences` - Update user preferences

    **Health Checks:**
    - `GET /health` - Service health check endpoint

For detailed API documentation including Python examples for the worker agent integration, see [Agent API Reference](docs/agentapi.md).

### 3. Worker (Python AI Agent)
-   **Framework**: Celery for background task processing.
-   **Location**: `/worker`
-   **Core Modules**:
    -   `worker.py`: Listens for and executes documentation jobs from the queue.
    -   `job_manager.py`: Manages the lifecycle of a job.
    -   `repo_manager.py`: Handles safe cloning and management of repositories.
    -   `parser.py`: Responsible for parsing code (e.g., using Python's AST).
    -   `ai_orchestrator.py`: Integrates with an LLM to generate documentation.
    -   `patcher.py`: Creates commits and pull requests.
    -   `logger.py`: Logs updates to `DEVLOG.md`.

## 🛠️ Getting Started

1.  **Prerequisites**: Docker and Docker Compose must be installed.
2.  **Environment Variables**: Copy the `.env.template` files in `/backend`, `/frontend`, and `/worker` to `.env` files and populate them with the necessary credentials (e.g., GitHub OAuth App credentials, database connection string).
3.  **Development vs Production**:
    -   **Development**: Use default localhost URIs in `.env` files (e.g., `http://localhost:8000` for API URL). This setup runs all services locally via Docker Compose.
    -   **Production**: Update `.env` files with production URIs (e.g., production GitHub OAuth callback URL, external database URL). Use individual Docker builds with the provided `infra/` Dockerfiles.
4.  **Build and Run**:
    ```bash
    # Development (all services)
    docker-compose up --build

    # Production (build individual services)
    docker build -f infra/backend.Dockerfile -t fixmydocs-backend .
    docker build -f infra/frontend.Dockerfile -t fixmydocs-frontend .
    docker build -f infra/worker.Dockerfile -t fixmydocs-worker .
    ```
5.  **Access**:
    -   Frontend: `http://localhost:3000`
    -   Backend API Docs: `http://localhost:8000/docs`
