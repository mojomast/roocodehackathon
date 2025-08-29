# FixMyDocs - AI-Powered Documentation Agent

FixMyDocs is a SaaS documentation agent that connects to GitHub repositories and automatically generates Pull Requests to improve documentation, including READMEs, docstrings, and inline comments. This project was built for the Roo Code Hackathon by Team Yugoslavia.

## 🚀 Project Status

The project has a solid architectural foundation with a Next.js frontend, a Python FastAPI backend, and a Python AI worker. The core components are integrated, but the primary AI functionality is still at a placeholder stage.

-   **Frontend**: UI is built and connected to the backend API.
-   **Backend**: User authentication via GitHub OAuth2 is fully functional. API endpoints for managing repositories and jobs are in place.
-   **Worker**: The modular structure for the AI agent is built, but the core logic (code analysis, documentation generation, PR creation) needs to be implemented.

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
-   **Core Endpoints**:
    -   `POST /api/auth/github`: Initiates the GitHub OAuth flow.
    -   `GET /auth/github/callback`: Handles the OAuth callback and user creation.
    -   `POST /api/repos/connect`: Connects a new repository for a user.
    -   `POST /api/docs/run`: Triggers a new documentation job.
    -   `GET /api/jobs/status/{id}`: Checks the status of a specific job.

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
3.  **Build and Run**:
    ```bash
    docker-compose up --build
    ```
4.  **Access**:
    -   Frontend: `http://localhost:3000`
    -   Backend API Docs: `http://localhost:8000/docs`

## 🔮 Next Steps

The immediate priority is to implement the core logic within the AI worker modules.

1.  **Implement `repo_manager.py`**: Add functionality to safely clone GitHub repositories into a temporary workspace.
2.  **Implement `parser.py`**: Develop the code parser to extract functions, classes, and existing docstrings.
3.  **Implement `ai_orchestrator.py`**: Integrate with a Large Language Model (LLM) to generate documentation based on the parsed code.
4.  **Implement `patcher.py`**: Build the functionality to create a new branch, commit the changes, and open a pull request on GitHub.
5.  **Update `DEVLOG.md`**: Ensure all significant changes are logged in `docs/DEVLOG.md`.