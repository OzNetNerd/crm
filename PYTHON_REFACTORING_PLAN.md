# CRM Python Refactoring Plan - CLAUDE.MD Aligned

## Executive Summary

This comprehensive plan addresses ALL Python code violations of the CLAUDE.MD mandate. The codebase has significant tech debt, violations of single responsibility principle, and legacy patterns that must be eliminated to achieve a modern, maintainable Python application.

## Critical Violations Found

### 1. Single Responsibility Violations
- **BaseModel (302 lines)**: Doing 8+ different things - display names, search, serialization, metadata, modals, routes, field management, caching
- **Task Model (528 lines)**: Managing entities, hierarchies, display formatting, serialization, validation
- **Opportunity Model (502 lines)**: Similar bloat with business logic mixed with display logic
- **ConnectionManager (chatbot)**: Managing websockets AND session tracking
- **ChatHandler**: Cache management, conversation history, context gathering, AND response generation

### 2. Tech Debt & Legacy Patterns
- **Inline HTML in Python** (chatbot/main.py lines 177-294)
- **Hardcoded magic strings** everywhere (icon maps, entity types)
- **Complex nested conditions** instead of guard clauses
- **Git worktree logic** in main.py instead of using gitpython
- **Manual path construction** instead of pathlib consistently
- **LRU cache misuse** for simple metadata that rarely changes

### 3. Configuration Mixed with Logic
- **SECRET_KEY generation** inline in create_app()
- **Database path logic** complex and mixed with application initialization
- **Inline Jinja configuration** in app initialization

### 4. Function Complexity
- **websocket_endpoint**: 95+ lines doing multiple responsibilities
- **_render_modal**: 5 parameters with complex branching logic
- **_handle_form_submission**: Mixed concerns of validation, persistence, and rendering

### 5. Code Quality & Compliance Issues (Verified)
- **Ruff violations**: 40 errors (38 F401 unused imports, 1 F541 f-string, 1 F841 unused variable) - ALL auto-fixable
- **Black formatting**: 48 files need reformatting
- **MyPy type checking**: 20+ type errors (missing stubs, type mismatches in extraction_schemas.py)
- **Missing ADR documentation** for recent ULTRA DRY architecture decisions

## Refactoring Plan

### Phase 0: Immediate Compliance Fixes (PRIORITY)

This phase MUST be completed first to establish baseline code quality before any refactoring.

#### TODO List - Linting & Formatting
- [ ] **Fix all ruff violations**
  - Run: `ruff check . --fix`
  - 40 violations, all auto-fixable
  - Removes unused imports and variables

- [ ] **Apply black formatting**
  - Run: `black .`
  - 48 files need reformatting
  - Ensures consistent code style

#### TODO List - Type Checking Setup
- [ ] **Install missing type stubs**
  ```bash
  pip install types-flask types-sqlalchemy types-requests
  ```

- [ ] **Create mypy.ini configuration**
  ```ini
  [mypy]
  python_version = 3.11
  warn_return_any = True
  warn_unused_configs = True
  disallow_untyped_defs = True
  disallow_any_unimported = False
  no_implicit_optional = True
  warn_redundant_casts = True
  warn_unused_ignores = True
  warn_no_return = True
  warn_unreachable = True
  strict_equality = True

  [mypy-tests.*]
  ignore_errors = True

  [mypy-migrations.*]
  ignore_errors = True
  ```

- [ ] **Fix type errors in extraction_schemas.py**
  - Lines 164, 183, 199, 210, 226, 244
  - Incorrect list comprehension types
  - Fix return type annotations

#### TODO List - Documentation
- [ ] **Create ADR-014: ULTRA DRY Architecture Pattern**
  - Document the complete deduplication approach
  - Explain model-level route configuration
  - Detail entity handling separation

- [ ] **Create ADR-015: Python Code Standards**
  - Document linting tools (ruff, black, mypy)
  - Define code quality gates
  - Establish PR checklist

#### TODO List - Pre-commit Hooks
- [ ] **Update .pre-commit-config.yaml**
  ```yaml
  repos:
    - repo: https://github.com/astral-sh/ruff-pre-commit
      rev: v0.12.8
      hooks:
        - id: ruff
          args: [--fix]

    - repo: https://github.com/psf/black
      rev: 24.10.0
      hooks:
        - id: black

    - repo: https://github.com/pre-commit/mirrors-mypy
      rev: v1.11.2
      hooks:
        - id: mypy
          additional_dependencies: [types-flask, types-sqlalchemy]
  ```

#### Success Criteria for Phase 0
- [ ] Zero ruff violations
- [ ] All files black-formatted
- [ ] MyPy configured and passing (or errors documented)
- [ ] ADRs created for architectural decisions
- [ ] Pre-commit hooks preventing future violations

## Refactoring Plan

### Phase 1: Extract Services & Separate Concerns

#### TODO List - Service Extraction
- [ ] **Create `app/services/display_service.py`**
  - Extract all display name logic from BaseModel
  - Create DisplayNameRegistry class
  - Move icon mappings here

- [ ] **Create `app/services/search_service.py`**
  - Extract search functionality from BaseModel
  - Implement SearchEngine class with proper indexing
  - Use whoosh or similar for full-text search

- [ ] **Create `app/services/serialization_service.py`**
  - Extract to_dict, to_search_result logic
  - Create ModelSerializer class with strategy pattern
  - Use dataclasses for serialization schemas

- [ ] **Create `app/services/metadata_service.py`**
  - Extract field metadata logic
  - Remove LRU cache, use class-level caching
  - Create FieldMetadata dataclass

- [ ] **Create `app/services/entity_relationship_service.py`**
  - Extract all entity linking logic from Task model
  - Create EntityRelationshipManager class
  - Use proper junction table patterns

#### TODO List - Configuration Extraction
- [ ] **Create `app/config.py`**
  - Move all configuration from main.py
  - Use environment variables properly with python-decouple
  - Create Config dataclass with validation

- [ ] **Create `app/database_config.py`**
  - Extract database path logic from main.py
  - Use gitpython for worktree detection
  - Create DatabaseConfig class

### Phase 2: Model Refactoring

#### TODO List - Model Cleanup
- [ ] **Refactor BaseModel**
  - Remove ALL business logic
  - Keep ONLY database column definitions
  - Max 50 lines per model base class

- [ ] **Split Task Model**
  - Create TaskHierarchyMixin for parent/child logic
  - Create TaskProgressMixin for completion tracking
  - Create TaskDisplayMixin for formatting
  - Core Task model under 100 lines

- [ ] **Split Opportunity Model**
  - Create OpportunityMetricsMixin for calculations
  - Create OpportunityStageMixin for pipeline logic
  - Core model under 100 lines

- [ ] **Create Model Mixins**
  - TimestampMixin (created_at, updated_at)
  - SoftDeleteMixin (deleted_at pattern)
  - AuditMixin (created_by, updated_by)

### Phase 3: Chatbot Service Refactoring

#### TODO List - Chatbot Cleanup
- [ ] **Extract HTML from Python**
  - Move chat widget HTML to templates/chat_widget.html
  - Use proper Jinja2 template rendering
  - Remove ALL inline HTML

- [ ] **Split ConnectionManager**
  - Create WebSocketManager (connection handling only)
  - Create SessionManager (session tracking only)
  - Use dependency injection

- [ ] **Refactor websocket_endpoint**
  - Extract message processing to MessageProcessor class
  - Extract streaming logic to StreamHandler class
  - Main endpoint under 30 lines

- [ ] **Create ChatbotService class**
  - Consolidate all chatbot logic
  - Use proper async patterns
  - Implement circuit breaker for Ollama failures

### Phase 4: Route & Form Refactoring

#### TODO List - Route Cleanup
- [ ] **Simplify modal routes**
  - Create ModalService class
  - Reduce _render_modal parameters to 3 max
  - Use dataclasses for modal configuration

- [ ] **Extract form handling**
  - Create FormProcessor class
  - Separate validation from persistence
  - Use form dataclasses

### Phase 5: Use Standard Library & Modern Python

#### TODO List - Modernization
- [ ] **Replace custom implementations**
  - Use pathlib everywhere (no os.path)
  - Use dataclasses for all DTOs
  - Use enum.Enum for all status/type fields
  - Use typing.Protocol for interfaces

- [ ] **Add proper exception handling**
  - Create custom exception hierarchy
  - No silent failures
  - Fail loudly with clear messages

- [ ] **Use modern async patterns**
  - Replace synchronous DB calls with async
  - Use asyncio properly in chatbot
  - Implement proper connection pooling

### Phase 6: Testing & Documentation

#### TODO List - Quality Assurance
- [ ] **Add comprehensive tests**
  - Unit tests for all services
  - Integration tests for routes
  - Use pytest fixtures properly

- [ ] **Add type hints everywhere**
  - Full typing coverage
  - Use mypy for type checking
  - No Any types without justification

- [ ] **Document service interfaces**
  - Use docstrings with Google style
  - Add ADRs for major decisions
  - Create service documentation

## Implementation Priority

### Immediate (Day 1-2): Compliance & Quality Gates
1. Fix all ruff violations (Phase 0)
2. Apply black formatting (Phase 0)
3. Configure mypy and fix critical type errors (Phase 0)
4. Create ADR documentation (Phase 0)
5. Update pre-commit hooks (Phase 0)

### Week 1: Critical Foundation
1. Extract configuration (Phase 1)
2. Create service layer structure
3. Extract display and search services

### Week 2: Model Refactoring
1. Refactor BaseModel
2. Split Task and Opportunity models
3. Create model mixins

### Week 3: Chatbot Cleanup
1. Extract HTML templates
2. Split ConnectionManager
3. Refactor websocket endpoint

### Week 4: Routes & Forms
1. Simplify modal handling
2. Extract form processing
3. Clean up route logic

### Week 5: Modernization
1. Replace custom implementations
2. Add proper exception handling
3. Implement async patterns

### Week 6: Quality & Polish
1. Add comprehensive tests
2. Complete type hints
3. Documentation

## Success Metrics

### Quantitative Goals
- [ ] No file over 300 lines
- [ ] No function over 50 lines
- [ ] No function with 4+ parameters
- [ ] 100% type hint coverage
- [ ] 80%+ test coverage
- [ ] Zero inline HTML/CSS/JS in Python

### Qualitative Goals
- [ ] Single responsibility for all classes
- [ ] Clear separation of concerns
- [ ] Fail loudly, no silent errors
- [ ] Modern Python patterns only
- [ ] Standard library over custom code
- [ ] Maintainable and extensible

## Anti-Patterns to Eliminate

1. **NEVER** mix configuration with logic
2. **NEVER** use magic strings - use enums
3. **NEVER** have functions doing multiple things
4. **NEVER** silently catch exceptions
5. **NEVER** use mutable default arguments
6. **NEVER** mix display logic with business logic
7. **NEVER** hardcode values that should be configured
8. **NEVER** use complex nested conditions
9. **NEVER** create God objects (classes doing everything)
10. **NEVER** ignore CLAUDE.MD principles

## Final Notes

This plan prioritizes:
- **Rapid progress** over preserving existing code
- **Clean architecture** over quick fixes
- **Long-term maintainability** over short-term convenience
- **Modern patterns** over legacy compatibility
- **Failing loudly** over defensive programming

Every change must align with CLAUDE.MD principles. No compromises.