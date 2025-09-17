# ADR-015: Python Code Standards and Quality Gates

## Status
Accepted

## Date
2025-01-17

## Context

The Python codebase requires consistent quality standards to maintain:
- Code readability and maintainability
- Type safety and error prevention
- Consistent formatting across the team
- Automated quality enforcement
- Alignment with CLAUDE.md principles

## Decision

We adopt a comprehensive Python code quality framework using industry-standard tools and strict enforcement through pre-commit hooks and CI/CD pipelines.

## Standards and Tools

### 1. Code Formatting - Black
**Tool**: Black (v24.10.0+)
**Configuration**: Default settings with line length 88
**Enforcement**: Pre-commit hook + CI check

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 24.10.0
    hooks:
      - id: black
```

### 2. Linting - Ruff
**Tool**: Ruff (v0.12.8+)
**Configuration**: Comprehensive rule set
**Enforcement**: Pre-commit hook with auto-fix

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.12.8
    hooks:
      - id: ruff
        args: [--fix]
```

**Key Rules**:
- F401: Remove unused imports
- F841: Remove unused variables
- F541: Fix f-string placeholders
- E501: Line too long (handled by Black)

### 3. Type Checking - MyPy
**Tool**: MyPy (v1.11.2+)
**Configuration**: mypy.ini with gradual typing
**Enforcement**: Pre-commit hook + CI check

```ini
[mypy]
python_version = 3.11
warn_return_any = True
warn_unused_configs = True
no_implicit_optional = True
warn_redundant_casts = True
warn_unused_ignores = True
warn_no_return = True
warn_unreachable = True
strict_equality = True
```

### 4. Code Principles (from CLAUDE.md)

#### MANDATORY Rules
1. **Use standard library**: NEVER create custom implementations
2. **Single responsibility**: Functions do ONE thing well
3. **No excessive returns**: Functions NEVER return 4+ values
4. **Fail loudly**: ALWAYS raise clear exceptions, no silent failures
5. **Modern Python**: Use dataclasses, enums, pathlib, typing
6. **No quick fixes**: Think long-term, avoid technical debt

#### Code Organization
- **Max file length**: 300 lines (split larger files)
- **Max function length**: 50 lines
- **Max function parameters**: 3 (use dataclasses for more)
- **Max class methods**: 10-15 (split large classes)

### 5. Import Organization
```python
# Standard library
import os
import sys
from pathlib import Path
from typing import Dict, List

# Third-party libraries
from flask import Flask, Blueprint
from sqlalchemy import Column

# Local imports
from app.models import BaseModel
from app.services import SearchService
```

### 6. Type Hints
**Required for**:
- All function signatures
- Class method signatures
- Return types (except __init__)

```python
def process_data(
    input_data: Dict[str, Any],
    options: ProcessOptions
) -> ProcessResult:
    """Process data with given options."""
```

### 7. Documentation Standards
**Docstrings**: Google style
```python
def calculate_metrics(data: List[float]) -> MetricResult:
    """
    Calculate statistical metrics from data.

    Args:
        data: List of numeric values to analyze.

    Returns:
        MetricResult containing mean, median, and std deviation.

    Raises:
        ValueError: If data is empty or contains non-numeric values.
    """
```

## Quality Gates

### Pre-commit Checks (BLOCKING)
1. ✅ Ruff - No violations
2. ✅ Black - All files formatted
3. ✅ MyPy - No type errors (or documented suppressions)

### CI/CD Checks (BLOCKING)
1. ✅ All pre-commit checks pass
2. ✅ Unit tests pass (80% coverage minimum)
3. ✅ Integration tests pass
4. ✅ No security vulnerabilities (via safety/bandit)

### PR Review Checklist
- [ ] Follows single responsibility principle
- [ ] No functions with 4+ return values
- [ ] Uses standard library over custom code
- [ ] Has proper error handling (no silent failures)
- [ ] Includes type hints
- [ ] Has docstrings for public functions
- [ ] No code duplication (DRY principle)
- [ ] Follows CLAUDE.md principles

## Migration Strategy

### Phase 0: Immediate Compliance (Day 1-2)
- [x] Fix all ruff violations (40 errors)
- [x] Apply black formatting (48 files)
- [x] Configure mypy.ini
- [x] Create this ADR

### Phase 1: Type Hints (Week 1)
- [ ] Add type hints to all new code
- [ ] Gradually add to existing code
- [ ] Fix mypy errors in critical paths

### Phase 2: Refactoring (Week 2-4)
- [ ] Split files over 300 lines
- [ ] Refactor functions over 50 lines
- [ ] Extract services from models
- [ ] Implement proper error handling

## Consequences

### Positive
- **Consistent codebase**: Same style everywhere
- **Fewer bugs**: Type checking catches errors early
- **Easier reviews**: Automated formatting
- **Better maintainability**: Clear standards
- **Rapid development**: No style debates

### Negative
- **Learning curve**: New developers need tool familiarity
- **Initial setup time**: Configuration and migration
- **Stricter requirements**: May slow initial development
- **Tool dependencies**: Must maintain tool versions

## Metrics

### Before Standards
- 40 linting violations
- 48 files needing reformatting
- 20+ type errors
- Inconsistent import ordering
- Mixed formatting styles

### After Standards
- 0 linting violations
- 100% black-formatted
- Type hints in all new code
- Consistent imports
- Uniform code style

## Exceptions

Allowed suppressions with justification:
```python
# mypy: ignore-errors  # Third-party library without stubs
# fmt: skip  # Specific formatting for readability
# noqa: F401  # Import for side effects
```

## Related ADRs
- ADR-001: Clean Architecture Principles
- ADR-014: ULTRA DRY Architecture Pattern

## References
- [Black Documentation](https://black.readthedocs.io/)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [MyPy Documentation](https://mypy.readthedocs.io/)
- [PEP 8 Style Guide](https://pep8.org/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)