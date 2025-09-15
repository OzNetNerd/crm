# ADR-002: Data Layer Architecture

## Status
Accepted

## Context
Need a robust, simple data layer for CRM operations including contacts, deals, activities, and reporting.

## Decision

### Database
- **PostgreSQL** for production (robust, scalable)
- **SQLite** for development (zero setup)
- Connection string from environment variable

### ORM Strategy
- **SQLAlchemy 2.0** with declarative models
- **Direct ORM usage** - no repository pattern
- **Alembic** for migrations

### Model Design
```python
# Simple, explicit models
class Contact(db.Model):
    __tablename__ = 'contacts'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True)
    company = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    deals = relationship('Deal', back_populates='contact')
```

### Key Patterns

#### 1. Model Organization
- One file per major entity
- Shared base model for common fields
- Clear, explicit relationships

#### 2. Query Patterns
```python
# Simple, readable queries
contacts = Contact.query.filter_by(status='active').all()
deal = Deal.query.get_or_404(deal_id)
```

#### 3. Data Validation
- Model-level constraints (nullable, unique)
- Form validation for user input
- Database constraints as last defense

#### 4. Migrations
```bash
alembic revision --autogenerate -m "Add contact table"
alembic upgrade head
```

## Implementation Rules

### Do's
- Use database transactions for multi-step operations
- Index foreign keys and commonly queried fields
- Keep models focused on data structure

### Don'ts
- No business logic in models
- No custom query builders
- No unnecessary abstraction layers

## Schema Overview
```
contacts ←→ deals ←→ activities
    ↓         ↓          ↓
  notes    stages    attachments
```

## Consequences

### Positive
- Simple, predictable data access
- Leverages SQLAlchemy's power
- Easy to test and debug
- Standard Python patterns

### Negative
- Direct ORM coupling (acceptable trade-off)
- Manual optimization when needed

## Notes
Keep models thin. Business logic belongs in service layer or route handlers.