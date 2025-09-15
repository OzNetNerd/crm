# ADR-001: Clean Architecture Principles

## Status
Accepted

## Context
Starting fresh with a CRM application rebuild. Previous codebase suffered from over-engineering, unnecessary abstractions, and violation of core principles.

## Decision
We adopt these core architectural principles:

### 1. DRY (Don't Repeat Yourself)
- Single source of truth for all data and logic
- Reusable components, not duplicated code
- Configuration over code duplication

### 2. KISS (Keep It Simple, Stupid)
- Start with the simplest solution that works
- Add complexity only when proven necessary
- Prefer explicit over implicit

### 3. YAGNI (You Aren't Gonna Need It)
- Build only what's required now
- No speculative features or abstractions
- Delete unused code immediately

## Project Structure
```
crm/
├── app/           # Application code
│   ├── models/    # SQLAlchemy models
│   ├── routes/    # Flask blueprints
│   ├── forms/     # WTForms definitions
│   ├── static/    # CSS, JS, images
│   └── templates/ # Jinja2 templates
├── config/        # Configuration files
├── tests/         # Test suite
├── docs/          # Documentation
└── main.py        # Application entry point
```

## Implementation Guidelines

### Code Standards
- Python 3.8+ with type hints where beneficial
- PEP 8 compliance (enforced by Black formatter)
- Maximum line length: 88 characters
- Docstrings for public APIs only

### Dependencies
- Minimize external dependencies
- Pin versions in requirements.txt
- Regular security updates

### Error Handling
- Fail fast with clear error messages
- Log errors, don't swallow exceptions
- User-friendly error pages

## Consequences

### Positive
- Maintainable, readable codebase
- Fast development iteration
- Easy onboarding for new developers
- Predictable behavior

### Negative
- May need refactoring as requirements grow
- Less "clever" code patterns

## Notes
This ADR supersedes all previous architecture decisions. When in doubt, choose simplicity.