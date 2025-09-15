# Architecture Decision Records (ADRs)

## Overview
This directory contains the architectural decisions for the CRM application. Each ADR documents a significant decision that affects the structure, dependencies, or development approach.

## Active ADRs

| ADR | Title | Status | Summary |
|-----|-------|--------|---------|
| [ADR-001](ADR-001-clean-architecture-principles.md) | Clean Architecture Principles | Accepted | Core principles: DRY, KISS, YAGNI. Simple project structure. |
| [ADR-002](ADR-002-data-layer-architecture.md) | Data Layer Architecture | Accepted | PostgreSQL/SQLite, SQLAlchemy ORM, Alembic migrations. |
| [ADR-003](ADR-003-frontend-architecture.md) | Frontend Architecture | Accepted | Server-side rendering with Jinja2, Tailwind CSS, HTMX. |
| [ADR-004](ADR-004-development-workflow.md) | Development Workflow | Accepted | Git workflow, testing strategy, CI/CD, code quality tools. |

## ADR Format

Each ADR follows this simple structure:

- **Status**: Accepted/Rejected/Superseded
- **Context**: Why we need to make this decision
- **Decision**: What we're going to do
- **Consequences**: What happens as a result

## Principles

1. **Keep ADRs concise** - One page maximum
2. **Document decisions, not tutorials** - Link to external docs for how-to
3. **Focus on the "why"** - The decision rationale is most important
4. **Update status when things change** - Mark as superseded with reference to new ADR

## Making Changes

To propose a new architectural decision:

1. Create a new ADR file: `ADR-005-your-topic.md`
2. Follow the format of existing ADRs
3. Submit PR for team review
4. Update this README once accepted

## Questions?

For questions about these architectural decisions, please open an issue or contact the development team.