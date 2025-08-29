# Contributing to FixMyDocs

Thank you for your interest in contributing to FixMyDocs! This document provides guidelines and information for contributors. Whether you're fixing bugs, adding features, improving documentation, or helping with testing, your contributions are welcome and appreciated.

## Code of Conduct

This project follows a code of conduct to ensure a welcoming environment for all contributors. Please see [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) for details.

## Development Environment Setup

FixMyDocs uses a microservices architecture with Docker containerization. For detailed setup instructions, please refer to the [README.md](../README.md) at the project root.

### Quick Start (Recommended)

The easiest way to get started is using Docker Compose:

```bash
# Clone the repository
git clone https://github.com/your-username/fixmydocs.git
cd fixmydocs

# Copy environment template files
cp backend/.env.template backend/.env
cp frontend/.env.template frontend/.env
cp worker/.env.template worker/.env
cp .env.template .env

# Edit .env files with your GitHub OAuth credentials and database URL
nano backend/.env frontend/.env worker/.env .env

# Start all services
docker-compose up --build

# Access the application:
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Documentation: http://localhost:8000/docs
```

### Environment File Setup

Before starting the services, configure the following environment files:

**backend/.env:**
```env
DATABASE_URL=postgresql://user:password@db:5432/fixmydocs
GITHUB_CLIENT_ID=your_github_oauth_app_id
GITHUB_CLIENT_SECRET=your_github_oauth_app_secret
GITHUB_CALLBACK_URL=http://localhost:8000/auth/github/callback
SECRET_KEY=your-secret-key-here
```

**frontend/.env.local:**
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_GITHUB_CLIENT_ID=your_github_oauth_app_id
```

**worker/.env:**
```env
DATABASE_URL=postgresql://user:password@db:5432/fixmydocs
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
GITHUB_TOKEN=your_github_personal_access_token
```

**.env (root):**
```env
POSTGRES_DB=fixmydocs
POSTGRES_USER=user
POSTGRES_PASSWORD=password
REDIS_URL=redis://redis:6379
```

### Local Development Setup

For development work requiring local installations:

**Prerequisites:**
- Docker and Docker Compose
- Node.js (v18+) for frontend development
- Python 3.8+ for backend and worker development
- npm or yarn package manager

**Environment Requirements:**
- PostgreSQL 10.0+
- Redis 5.0+
- Git (for repository operations)

**Frontend Setup:**
```bash
cd frontend
npm install
npm run dev
```

**Build Configurations:**
- **ESLint**: Dual configuration with `.eslintrc.json` and `eslint.config.mjs` (flat config)
- **Prettier**: Configured in `.prettierrc` with single quotes, 2-space indentation
- **TypeScript**: Strict mode enabled via `tsconfig.json`
- **Jest**: Configured in `jest.config.js` with jsdom environment and path aliases

**Python Requirements:**
- **Python Version**: 3.8+ (validated via requirements.txt)
- **Backend Setup**:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

**Worker Setup:**
```bash
cd worker
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
# Dependencies include:
# - celery>=5.2.0,<6.0.0 (task queue)
# - GitPython>=3.1.0,<4.0.0 (Git operations)
# - PyGitHub>=1.54.0,<2.0.0 (GitHub API)
# - cryptography>=3.4.0,<42.0.0 (security)
python worker.py
```

> Tip (Windows): You can also create a single workspace venv at repo root (e.g., `.venv`) and install both backend and worker requirements there.

**Local Testing DB / Secrets:**
```powershell
# From repo root, PowerShell
$env:DATABASE_URL = "sqlite:///./test.db"
$env:GITHUB_WEBHOOK_SECRET = "dev_secret_change_me"
```

**Enhanced Build Commands:**
```bash
# Frontend linting and formatting
cd frontend
npm run lint    # ESLint with TypeScript rules
npm run format  # Prettier auto-formatting
npm run build   # Next.js production build

# Backend testing and quality
cd backend
python -m flake8 .  # Code style checking
python -m pytest tests/ -v --cov=. --cov-report=html

# Worker testing
cd worker
python -m pytest tests/ -v --cov=. --cov-report=html
```

## Contribution Guidelines

### Branching Strategy

We follow a feature branch workflow:

- **Main branch**: `main` - Production-ready code
- **Development branch**: `develop` - Latest development changes
- **Feature branches**: `feature/feature-name` - New features
- **Bug fix branches**: `bugfix/bug-description` - Bug fixes
- **Hotfix branches**: `hotfix/issue-description` - Critical fixes for production

### Branch Naming Convention

- Use lowercase with hyphens: `feature/add-user-authentication`
- Include issue number when applicable: `feature/123-add-user-authentication`
- Keep names descriptive but concise

### Commit Message Conventions

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**Types:**
- `feat`: New features
- `fix`: Bug fixes
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Test additions or modifications
- `chore`: Maintenance tasks

**Examples:**
```
feat: add user authentication endpoint
fix: resolve memory leak in document processor
docs: update API documentation for v2.0
refactor: simplify async job processing logic
```

### Pull Request Process

1. **Create a branch** from `develop` for your work
2. **Make changes** and write tests
3. **Run tests** to ensure everything works
4. **Update documentation** as needed
5. **Submit a pull request** targeting the `develop` branch

**Pull Request Requirements:**
- Provide a clear description of changes
- Include screenshots for UI changes
- Reference any related issues
- Ensure all CI checks pass
- Get at least one review approval before merging

**Pull Request Template:**
```markdown
## Description
Brief description of the changes made.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring
- [ ] Breaking change

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing completed
- [ ] All tests passing

## Screenshots (if applicable)
Add screenshots of any UI changes.

## Additional Notes
Any additional context or information for reviewers.
```

## Testing Guidelines

Comprehensive testing is crucial for maintaining code quality. This section outlines the testing framework and how to run tests.

### Technology Stack

-   **Worker**: Celery with Redis broker for asynchronous task processing
-   **Database**: PostgreSQL with SQLAlchemy ORM for data persistence
-   **Backend/Worker Testing**: Pytest with coverage reporting and HTML outputs
-   **Frontend Testing**: Jest/React Testing Library with jsdom environment, integrated with Next.js
-   **E2E Testing**: Docker-based integration tests for full pipeline validation
-   **CI/CD**: GitHub Actions with automated linting, testing, and deployment
-   **Code Quality**: ESLint with TypeScript support, Prettier for consistent formatting

### Current Testing Structure

-   **Unit Tests**: Individual component/function testing with isolated dependencies
-   **Integration Tests**: Service-to-service communication testing with actual databases
-   **End-to-End Tests**: Full user workflow testing from frontend to backend to worker
-   **Frontend Mocking**: MSW (Mock Service Worker) for API endpoint simulation

### Running Tests

To ensure code quality, run the following commands:

```bash
# Run all Docker-based tests (recommended)
docker-compose -f docker-compose.yml -f docker-compose.test.yml up --build --abort-on-container-exit

# Or run tests locally (requires local setup)

# Frontend tests - Next.js integrated Jest with jsdom
cd frontend
npm run lint                         # ESLint checking with TypeScript rules
npm test -- --watchAll=false --coverage  # Jest tests with coverage reporting
npm test -- --testPathPattern=ErrorBoundary.test.js  # Specific component test
npm test -- --testPathPattern=dashboard.test.js    # Page integration tests

# Backend tests - Pytest with coverage
cd backend
python -m pytest tests/ -v --cov=. --cov-report=html  # All backend tests with HTML coverage
python -m pytest test_main.py -v                    # Main API endpoint tests
python -m pytest test_e2e.py -v                     # End-to-end integration tests

# Worker tests - Python testing focused on AI worker logic
cd worker
python -m pytest tests/ -v --cov=. --cov-report=html  # Comprehensive worker testing
python -m pytest test_worker.py -v                   # Worker task execution tests

# Test Coverage Reports
# View HTML coverage reports in your browser after running tests:
# - backend/htmlcov/index.html (Backend coverage)
# - worker/htmlcov/index.html (Worker coverage)
# - Frontend coverage available in terminal output
```

### Test Coverage

Maintain minimum test coverage of 80% for new code. Current test structure includes:

**Frontend Tests:**
- Component tests with React Testing Library
- Page integration tests
- Mock server setup for API calls
- Jest configuration with jsdom environment

**Backend Tests:**
- API endpoint unit tests
- Database model tests
- Authentication middleware tests
- Integration tests with test database

**Worker Tests:**
- Celery task processing tests
- Repository management tests
- AI orchestration mock tests
- Logging and error handling tests

**E2E Tests:**
- Full user workflow testing
- API to worker pipeline validation
- Docker-based environment testing

Run coverage reports:

```bash
# Frontend coverage
cd frontend
npm test -- --coverage --coverageDirectory=coverage

# Backend coverage
cd backend
python -m pytest --cov=app --cov-report=html --cov-report=term

# Worker coverage
cd worker
python -m pytest --cov=. --cov-report=html --cov-report=term

# View HTML coverage reports
# open backend/htmlcov/index.html
# open frontend/coverage/lcov-report/index.html
```

## Documentation Guidelines

Good documentation is essential for maintainability and onboarding. Follow these guidelines:

### Code Documentation

- **Frontend (TypeScript/JavaScript)**: Use JSDoc comments for functions and classes
```typescript
/**
 * Processes a document for analysis
 * @param documentId - Unique identifier for the document
 * @param options - Processing configuration options
 * @returns Promise resolving to processed document data
 */
async function processDocument(documentId: string, options: ProcessOptions): Promise<DocumentResult> {
  // Implementation
}
```

- **Backend (Python)**: Use docstrings for functions, classes, and modules
```python
def process_document(document_id: str, options: ProcessOptions) -> DocumentResult:
    """
    Process a document for analysis.

    Args:
        document_id: Unique identifier for the document
        options: Processing configuration options

    Returns:
        Processed document data
    """
    # Implementation
```

- **Inline Comments**: Add comments for complex logic, not obvious code
```typescript
// Calculate document complexity score based on multiple factors
const complexityScore = calculateComplexity(textMetrics, structureAnalysis);
```

### Configuration File Standards

All build and configuration files follow project standards:

- **`.eslintrc.json`**: Primary ESLint rules for code quality and consistency
- **`eslint.config.mjs`**: Flat config format for advanced ESLint features
- **`.prettierrc`**: Code formatting rules (single quotes, 2-space indentation, etc.)
- **`jest.config.js`**: Next.js-integrated testing configuration with jsdom environment
- **`tsconfig.json`**: TypeScript compiler options with strict type checking
- **`requirements.txt`**: Python dependencies with pinned versions for security

### README and Documentation Updates

- Update README.md when adding new features or changing setup instructions
- Keep API documentation current with code changes
- Add examples for new functionality
- Review and update existing documentation regularly

### Documentation Standards

- Use Markdown for all documentation files
- Include table of contents for files longer than 3 sections
- Use consistent formatting and heading structure
- Test all code examples before committing

## Getting Help

- **Issues**: Use GitHub Issues for bugs, feature requests, and general questions
- **Discussions**: Use GitHub Discussions for longer-form conversations
- **Documentation**: Check existing docs and README first

## Recognition

Contributors will be acknowledged in:
- Repository's contributor list (if public)
- Release notes for significant contributions
- Hackathon recognition events

Thank you for contributing to FixMyDocs and helping make documentation management better for developers everywhere!