# FixMyDocs Development Plan

## 1. Introduction
This document outlines the development plan for **FixMyDocs**, a SaaS platform designed to automatically maintain, improve, and optimize project documentation. This plan is based on an initial architectural analysis and is designed to guide the project from its current boilerplate state to a Minimum Viable Product (MVP) and beyond.

## 2. Current State
The application is a well-structured boilerplate with a microservices architecture (Frontend, Backend, Worker). However, it is non-functional and requires significant implementation work. Key issues include technology stack inconsistencies (RQ vs. Celery), database mismatches (SQLite vs. PostgreSQL), broken authentication, and incomplete UI.

## 3. Development Phases

### Phase 1: Foundational Fixes & Environment Setup (Task: "Fix-Foundation")
*Goal: Stabilize the architecture and create a consistent development environment.*
- [ ] **Resolve Technology Inconsistencies:**
    - [ ] Standardize on **Celery** for the worker. Update `worker/worker.py` and `worker/requirements.txt`.
    - [ ] Align database usage. Modify backend to use **PostgreSQL** to match `docker-compose.yml`.
- [ ] **Environment Configuration:**
    - [ ] Create `.env.template` files for backend, frontend, and worker services.
    - [ ] Update `docker-compose.yml` to use `.env` files for configuration.
- [ ] **Fix Authentication Flow:**
    - [ ] Implement a basic, functioning GitHub OAuth flow on the backend.
    - [ ] Correct the frontend login link to point to the new, valid authentication route.
- [ ] **Fix Root Navigation:**
    - [ ] Update `frontend/src/app/page.tsx` to redirect to the `/dashboard` or `/login` page.

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