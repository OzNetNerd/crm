# ADR-004: Development Workflow

## Status
Accepted

## Context
Need efficient development practices that support rapid iteration while maintaining code quality.

## Decision

### Version Control
```bash
# Feature branch workflow
git checkout -b feature/add-contact-import
# Make changes
git commit -m "feat: add CSV contact import"
git push origin feature/add-contact-import
# Create PR for review
```

### Development Setup
```bash
# Simple setup
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
./run.sh  # Auto-detects free port
```

### Testing Strategy

#### Test Structure
```
tests/
├── unit/          # Fast, isolated tests
├── integration/   # Database/API tests
└── conftest.py    # Shared fixtures
```

#### Running Tests
```bash
pytest                    # Run all tests
pytest tests/unit        # Unit tests only
pytest -k test_contact   # Specific tests
pytest --cov=app        # With coverage
```

### Code Quality

#### Formatters & Linters
```bash
black app/              # Format code
flake8 app/            # Check style
mypy app/              # Type checking
```

#### Pre-commit Hooks
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    hooks:
      - id: black
  - repo: https://github.com/PyCQA/flake8
    hooks:
      - id: flake8
```

### CI/CD Pipeline

#### GitHub Actions
```yaml
name: CI
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run tests
        run: |
          pip install -r requirements.txt
          pytest
```

### Database Management

#### Migrations
```bash
alembic revision --autogenerate -m "Description"
alembic upgrade head
alembic downgrade -1
```

#### Data Seeding
```bash
python scripts/seed_data.py  # Development data
```

## Development Practices

### Commit Messages
```
feat: Add user authentication
fix: Correct email validation
docs: Update API documentation
refactor: Simplify contact queries
test: Add deal creation tests
```

### Pull Request Guidelines
- Single purpose per PR
- Include tests for new features
- Update documentation if needed
- Request review from team member

### Environment Variables
```bash
# .env (not committed)
DATABASE_URL=postgresql://user:pass@localhost/crm
SECRET_KEY=dev-secret-key
DEBUG=True
```

## Tools

### Required
- Python 3.8+
- PostgreSQL or SQLite
- Git

### Recommended
- VS Code or PyCharm
- pgAdmin or DBeaver
- Postman or HTTPie

## Consequences

### Positive
- Consistent development environment
- Automated quality checks
- Fast feedback loops
- Clear contribution process

### Negative
- Initial setup time
- Learning curve for new developers

## Notes
Keep the workflow simple. Automation should help, not hinder development speed.