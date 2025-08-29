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

# Start all services
docker-compose up --build

# Access the application:
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
```

### Local Development Setup

For development work requiring local installations:

**Prerequisites:**
- Docker and Docker Compose
- Node.js (v18+) for frontend development
- Python 3.8+ for backend development

**Frontend Setup:**
```bash
cd frontend
npm install
npm run dev
```

**Backend Setup:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

**Worker Setup:**
```bash
cd worker
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python worker.py
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

-   **Worker**: Celery
-   **Database**: PostgreSQL
-   **Backend/Worker Testing**: Pytest
-   **Frontend Testing**: Jest/React Testing Library

### Current Testing Structure

-   **Unit Tests**: Individual component/function testing
-   **Integration Tests**: Service-to-service communication testing
-   **End-to-End Tests**: Full user workflow testing

### Running Tests

To ensure code quality, run the following commands:

```bash
# Run all linting checks
npm run lint # For frontend
# Add backend/worker linting command if available

# Run all tests
# Frontend tests
cd frontend
npm test

# Backend tests
cd backend
pytest

# Worker tests
cd worker
pytest
```

### Test Coverage

Maintain minimum test coverage of 80% for new code. Run coverage reports:

```bash
# Frontend coverage
cd frontend
npm run test:coverage

# Backend coverage
cd backend
coverage run -m pytest
coverage report

# Worker coverage
cd worker
coverage run -m pytest
coverage report
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