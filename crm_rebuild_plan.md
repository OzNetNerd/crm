# CRM Database Schema Rebuild Plan - Single Source of Truth with MEDDPICC & Relationship Ownership

## Phase 1: Commit Current Work & Clean Slate ✅

1. ✅ Commit all existing changes with comprehensive message
2. 🔄 Delete existing database completely  
3. 🔄 Start fresh with proper single source of truth design

## Phase 2: Enhanced Core Entity Tables

### Users (Account Team Members)

```sql
Users: id, name, email, job_title, created_at
# job_title = "Account Manager", "Sales Rep", "Solutions Engineer", etc.
# Single source of truth for internal team member's role
```

### Companies

```sql
Companies: id, name, industry, website
# No changes needed - already clean
```

### Stakeholders (Customer Contacts)

```sql
Stakeholders: id, name, job_title, email, phone, company_id, created_at
# job_title = "VP Sales", "CTO", "Procurement Manager" (their actual job)
# Consistent naming with Users.job_title
```

### Stakeholder MEDDPICC Roles (Many-to-Many)

```sql
StakeholderMeddpiccRoles: stakeholder_id, meddpicc_role, created_at
# meddpicc_role = "decision_maker", "economic_buyer", "influencer", "champion", "gatekeeper", "user", "technical_buyer"
# Stakeholders can have multiple MEDDPICC roles
```

### Relationship Ownership Mapping

```sql
StakeholderRelationshipOwners: stakeholder_id, user_id, created_at
# Maps which account team member(s) own relationships with which stakeholder(s)
# Many-to-many: complex relationship ownership patterns supported
```

### Opportunities & Tasks (No Changes)

```sql
Opportunities: id, name, value, probability, expected_close_date, stage, company_id, created_at
Tasks: id, description, due_date, priority, status, next_step_type, created_at, completed_at, task_type, parent_task_id, sequence_order, dependency_type
```

## Phase 3: Clean Assignment Tables (Pure Relationships)

### Company Account Teams

```sql
CompanyAccountTeams: user_id, company_id, created_at
# Pure assignment - job_title comes from Users.job_title via JOIN
```

### Opportunity Account Teams  

```sql
OpportunityAccountTeams: user_id, opportunity_id, created_at
# Pure assignment - job_title comes from Users.job_title via JOIN
# Opportunities inherit company assignments + get specific additions
```

### Stakeholder Opportunities

```sql
StakeholderOpportunities: stakeholder_id, opportunity_id, created_at
# Pure assignment - MEDDPICC roles come from StakeholderMeddpiccRoles via JOIN
```

### Task Entities (Multi-Entity Linking)

```sql
TaskEntities: task_id, entity_type, entity_id, created_at
# Links tasks to: companies, opportunities, stakeholders, users
# Handles all task assignments including account team members
```

## Phase 4: Complete Code Refactor

- Rename Contact → Stakeholder throughout entire codebase
- Update all model classes, imports, and relationships  
- Fix all route references, forms, and validation
- Update templates with consistent terminology
- Remove all redundant role/access_level fields from assignment tables
- Update entity helpers and utilities with new structure

## Phase 5: Bidirectional Views & Relationship Management UI

- **User detail pages**: Show all assigned companies/opportunities + owned stakeholder relationships
- **Stakeholder detail pages**: Show job_title, MEDDPICC roles, opportunities, relationship owners
- **Company pages**: Show account team members with job_titles (via JOIN)
- **Opportunity pages**: Show full account team (inherited + specific) + stakeholders with MEDDPICC context
- **Relationship ownership management**: Interface to assign/reassign stakeholder relationship ownership

## Phase 6: Enhanced Seed Script with Realistic Data

- Create sample users with realistic job_titles
- Assign users to companies and opportunities with inheritance
- Create stakeholders with job_titles and multiple MEDDPICC roles  
- Map relationship ownership between users and stakeholders
- Link stakeholders to opportunities
- Create tasks linked to multiple entity types including users and stakeholders

## Key Benefits Achieved

✅ **True Single Source of Truth**: job_title stored once per person, MEDDPICC roles managed separately  
✅ **MEDDPICC Support**: Full multi-role MEDDPICC mapping per stakeholder
✅ **Relationship Ownership**: Clear mapping of who owns which stakeholder relationships
✅ **Clean Assignments**: Pure relationship tables with no redundant data
✅ **Consistent Terminology**: "Account Team" vs "Stakeholders" with "job_title" for both
✅ **Bidirectional Visibility**: Easy queries and UI navigation in all directions
✅ **Flexible Task Linking**: Tasks can link to any entity type via existing proven system

## Progress Tracking

- [x] Phase 1: Commit and clean slate preparation
- [ ] Phase 2: Enhanced core entity tables
- [ ] Phase 3: Clean assignment tables  
- [ ] Phase 4: Complete code refactor
- [ ] Phase 5: Bidirectional views & relationship management UI
- [ ] Phase 6: Enhanced seed script with realistic data
