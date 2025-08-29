# FixMyDocs Development Plan

## 1. Introduction
This document outlines the development plan for **FixMyDocs**, a SaaS platform designed to automatically maintain, improve, and optimize project documentation. This plan is based on an initial architectural analysis and is designed to guide the project from its current boilerplate state to a Minimum Viable Product (MVP) and beyond.

## 2. Current State
The application has a solid microservices architecture (Frontend, Backend, Worker) with recent critical bug fixes improving stability and functionality. All foundational issues have been resolved, including consistent technology stack (Celery worker, PostgreSQL database), functioning GitHub OAuth authentication, and partial UI implementation. Core implementation work continues for AI functionality and complete user workflows.

## 3. Development Phases

### Phase 1: Foundational Fixes & Environment Setup (Task: "Fix-Foundation") ✅ COMPLETED
*Goal: Stabilize the architecture and create a consistent development environment.* ✅ ACHIEVED: Critical bugs fixed, environment configured.
- [x] **Resolve Technology Inconsistencies:**
    - [x] Standardize on **Celery** for the worker. Update `worker/worker.py` and `worker/requirements.txt`.
    - [x] Align database usage. Backend uses **PostgreSQL** via SQLAlchemy and configurable DATABASE_URL.
- [x] **Environment Configuration:**
  - [x] Create `.env.template` files for backend, frontend, and worker services.
  - [x] `docker-compose.yml` already configured to use `.env` files via env_file directives.
  - **Setup Instructions:** For local development, copy each `.env.template` to `.env` in the respective service directories and populate the real values (e.g., obtain GitHub OAuth credentials, set database credentials to match docker-compose environment variables). Ensure `.env` files are ignored by git using .gitignore. For production deployments, set these environment variables securely through your hosting platform's environment configuration.
- [x] **Fix Authentication Flow:**
    - [x] GitHub OAuth flow is functional on backend with proper handler logic and database integration.
    - [x] Frontend login correctly redirects to backend OAuth endpoint.
- [x] **Fix Root Navigation:**
    - [x] `frontend/src/app/page.tsx` redirects to `/dashboard`.
- [x] **Critical Bug Fixes Applied:**
    - [x] Resolved BE-001 to BE-013, FE-001 to FE-002, WK-001 to WK-008, TS-001 to TS-003 (15 critical issues fixed).
    - [x] Improved error handling, security, database configuration, and module imports.

### Phase 2: Core Feature Implementation - MVP (Task: "Build-MVP-Core")
*Goal: Implement the core functionality for a user to connect a repository and run a documentation analysis job.*
- [ ] **Backend API Implementation:**
    - [ ] Implement `/repos/connect` to securely store repository information.
    - [ ] Implement `/docs/run` to create a job record and dispatch a task to the Celery worker.
    - [ ] Implement `/jobs/status/{job_id}` to provide real-time job status.
- [ ] **Worker Implementation:**
    - [ ] Create a Celery task to handle documentation analysis.
    - [ ] **(Simulation)** For MVP, the worker will simulate a multi-step process: cloning repo, parsing files, generating docs. It will update the job status in the database at each step. Actual AI integration will be deferred.
- [ ] **Frontend Implementation:**
    - [ ] Implement the "Connect Repository" feature on the frontend.
    - [ ] Create a UI to trigger the documentation analysis job.
    - [ ] Display job status and results on the jobs page.

### Phase 3: UI/UX & Frontend Polish (Task: "Polish-Frontend")
*Goal: Transform the frontend from a wireframe to a usable and polished interface.*
- [ ] **Implement UI Components:**
    - [ ] Build out the Dashboard, Repositories, and Jobs pages with actual data.
    - [ ] Implement loading states and user-friendly error handling.
- [ ] **Real-time Updates:**
    - [ ] Implement polling or WebSockets on the jobs page to show real-time status updates.
- [ ] **Gamification:**
    - [ ] Connect the gamification elements (points, badges) on the dashboard to backend data.

### Phase 4: Production Readiness & Deployment (Task: "Prepare-for-Prod")
*Goal: Ensure the application is secure, testable, and ready for deployment.*
- [ ] **Testing:**
    - [ ] Set up `pytest` for the backend and worker.
    - [ ] Set up Jest/React Testing Library for the frontend.
    - [ ] Write unit and integration tests for critical paths.
- [ ] **Security:**
    - [ ] Implement proper authentication and authorization middleware on the backend.
    - [ ] Add input validation to all API endpoints.
- [ ] **CI/CD:**
    - [ ] Create a GitHub Actions workflow to run tests and linting on every push.
    - [ ] Create a separate workflow for building and pushing Docker images to a registry.

## 4. Documentation Strategy
- **`README.md`:** Will be updated to reflect the final, functional application, with clear setup and run instructions.
- **`CONTRIBUTING.md`:** Will be reviewed and updated to include instructions for the finalized tech stack and testing procedures.
- **`DEVLOG.md`:** This file will be used to track progress against the phases outlined in this plan.
- **API Documentation:** The backend will use FastAPI's automatic OpenAPI/Swagger documentation generation.