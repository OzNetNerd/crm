#!/usr/bin/env python3
"""
Enhanced CRM Database Seeding Script
Creates comprehensive realistic test data for all CRM entities with:
- Deal values ranging from $10,000 to $300,000
- Mix of single tasks, multi-task workflows, and multi-entity linked tasks
- Complete coverage for all application features
"""

import random
import sys
from datetime import datetime, date, timedelta
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.models import db, Company, Stakeholder, Opportunity, Task, Note, User
from services.crm.main import create_app

# Enhanced sample data for comprehensive testing
INDUSTRIES = [
    "Technology",
    "Healthcare",
    "Finance",
    "Manufacturing",
    "Retail",
    "Education",
    "Construction",
    "Real Estate",
    "Consulting",
    "Media",
    "Automotive",
    "Energy",
    "Telecommunications",
    "Insurance",
    "Logistics",
]

# Expanded company data with more variety
COMPANY_DATA = [
    {
        "name": "GreenEnergy Solutions",
        "industry": "Technology",
        "website": "https://greenenergy.com",
    },
    {
        "name": "Quantum Analytics",
        "industry": "Technology",
        "website": "https://quantum-analytics.com",
    },
    {
        "name": "MedCore Systems",
        "industry": "Healthcare",
        "website": "https://medcore.com",
    },
    {
        "name": "FinTech Innovators",
        "industry": "Finance",
        "website": "https://fintech-innovators.com",
    },
    {
        "name": "ProManufacturing Co",
        "industry": "Manufacturing",
        "website": "https://promanufacturing.com",
    },
    {
        "name": "RetailMax Group",
        "industry": "Retail",
        "website": "https://retailmax.com",
    },
    {
        "name": "EduTech Solutions",
        "industry": "Education",
        "website": "https://edutech-solutions.com",
    },
    {
        "name": "BuildRight Construction",
        "industry": "Construction",
        "website": "https://buildright.com",
    },
    {
        "name": "Prime Properties LLC",
        "industry": "Real Estate",
        "website": "https://prime-properties.com",
    },
    {
        "name": "Strategic Consulting Partners",
        "industry": "Consulting",
        "website": "https://strategic-consulting.com",
    },
    {
        "name": "DataStream Analytics",
        "industry": "Technology",
        "website": "https://datastream.com",
    },
    {
        "name": "HealthPlus Systems",
        "industry": "Healthcare",
        "website": "https://healthplus.com",
    },
    {
        "name": "AutoTech Innovations",
        "industry": "Automotive",
        "website": "https://autotech.com",
    },
    {
        "name": "PowerGrid Solutions",
        "industry": "Energy",
        "website": "https://powergrid.com",
    },
    {
        "name": "CommLink Networks",
        "industry": "Telecommunications",
        "website": "https://commlink.com",
    },
]

CONTACT_NAMES = [
    "Sarah Johnson",
    "Michael Chen",
    "Emily Rodriguez",
    "David Thompson",
    "Lisa Wang",
    "Robert Martinez",
    "Jennifer Brown",
    "Christopher Lee",
    "Amanda Davis",
    "Mark Wilson",
    "Jessica Taylor",
    "Daniel Anderson",
    "Ashley Garcia",
    "Matthew Miller",
    "Rachel Kim",
    "James Wilson",
    "Maria Gonzalez",
    "Kevin O'Connor",
    "Nicole Smith",
    "Ryan Murphy",
    "Alex Cooper",
    "Diana Foster",
    "Tom Bradley",
    "Sophia Turner",
    "Nathan Hayes",
    "Olivia Parker",
    "Lucas Reed",
    "Emma Collins",
    "Jake Morrison",
    "Grace Bennett",
]

JOB_TITLES = [
    "CEO",
    "CTO", 
    "VP of Sales",
    "Marketing Director",
    "Operations Manager",
    "Project Manager", 
    "Business Development",
    "Product Manager",
    "IT Director",
    "CFO",
    "Sales Manager",
    "Account Manager",
    "Solutions Engineer",
    "Customer Success Manager",
    "Technical Lead",
    "Software Engineer",
    "Marketing Manager",
    "HR Manager",
    "Finance Manager"
]

DEPARTMENTS = [
    "sales",
    "engineering", 
    "marketing",
    "support",
    "operations",
    "finance",
    "hr"
]

# Enhanced job titles for stakeholders and team members
STAKEHOLDER_JOB_TITLES = [
    "CEO",
    "CTO",
    "VP of Sales",
    "Marketing Director", 
    "Operations Manager",
    "IT Director",
    "CFO",
    "VP Engineering",
    "Head of Product",
    "Chief Revenue Officer"
]

TEAM_JOB_TITLES = [
    "Sales Manager",
    "Account Manager", 
    "Solutions Engineer",
    "Customer Success Manager",
    "Technical Lead",
    "Software Engineer",
    "Marketing Manager",
    "HR Manager",
    "Finance Manager",
    "Business Development Manager"
]

# Team member names for seeding User model
TEAM_MEMBER_NAMES = [
    "Alex Johnson",
    "Sarah Martinez",
    "Mike Thompson",
    "Lisa Chen",
    "David Rodriguez",
    "Emma Wilson",
    "Ryan Davis",
    "Kate Anderson",
    "Tom Foster",
    "Nina Garcia",
    "Chris Parker",
    "Amy Taylor",
]

# Enhanced opportunity templates for varied deal sizes
OPPORTUNITY_TEMPLATES = [
    "Enterprise CRM Implementation",
    "Cloud Infrastructure Migration",
    "Digital Transformation Initiative",
    "Custom Software Development",
    "Data Analytics Platform",
    "Mobile App Development",
    "Security Assessment & Implementation",
    "Training & Consulting Program",
    "System Integration Project",
    "Software License Renewal",
    "Business Process Automation",
    "E-commerce Platform Upgrade",
    "Customer Portal Development",
    "API Integration Services",
    "Compliance & Audit Services",
]

# Enhanced task templates for comprehensive testing
TASK_TEMPLATES = [
    "Send revised proposal to {}",
    "Schedule follow-up call with {}",
    "Prepare demo presentation for {}",
    "Research {}'s competitors and market position",
    "Draft contract terms for {}",
    "Conduct needs assessment with {}",
    "Send project timeline to {}",
    "Review budget requirements with {}",
    "Prepare technical documentation for {}",
    "Schedule stakeholder meeting with {}",
    "Create pricing strategy for {}",
    "Analyze ROI projections for {}",
    "Develop implementation roadmap for {}",
    "Coordinate team resources for {}",
    "Document risk assessment for {}",
]

# Multi-task workflow templates
PARENT_TASK_TEMPLATES = [
    "Complete enterprise onboarding for {}",
    "Execute full sales cycle for {}",
    "Deliver comprehensive discovery for {}",
    "Implement solution rollout for {}",
    "Conduct quarterly business review with {}",
    "Manage contract renewal process for {}",
    "Lead digital transformation for {}",
    "Oversee compliance implementation for {}",
    "Execute competitive analysis for {}",
    "Manage vendor evaluation for {}",
]

# Subtask templates for parent tasks
SUBTASK_TEMPLATES = {
    "Complete enterprise onboarding for {}": [
        "Schedule executive kickoff call with {}",
        "Send comprehensive welcome package to {}",
        "Set up enterprise accounts and permissions for {}",
        "Conduct detailed orientation session with {}",
        "Establish success metrics and KPIs for {}",
        "Create implementation timeline for {}",
    ],
    "Execute full sales cycle for {}": [
        "Qualify enterprise opportunity with {}",
        "Conduct stakeholder mapping for {}",
        "Present comprehensive solution to {}",
        "Address technical and business objections from {}",
        "Negotiate contract terms with {}",
        "Execute final contract signing with {}",
    ],
    "Deliver comprehensive discovery for {}": [
        "Plan discovery workshop agenda for {}",
        "Conduct current state assessment with {}",
        "Document technical requirements for {}",
        "Identify integration touchpoints for {}",
        "Analyze data migration needs for {}",
        "Prepare discovery findings report for {}",
    ],
    "Implement solution rollout for {}": [
        "Develop implementation strategy for {}",
        "Configure production environment for {}",
        "Execute user training programs for {}",
        "Perform system integration testing for {}",
        "Coordinate go-live activities for {}",
        "Monitor post-launch performance for {}",
    ],
    "Conduct quarterly business review with {}": [
        "Analyze performance metrics for {}",
        "Prepare QBR presentation materials for {}",
        "Schedule QBR session with {}",
        "Present findings and recommendations to {}",
        "Document action items and next steps for {}",
        "Follow up on QBR commitments with {}",
    ],
    "Manage contract renewal process for {}": [
        "Review current contract performance with {}",
        "Analyze usage and ROI metrics for {}",
        "Prepare renewal proposal for {}",
        "Schedule renewal discussion with {}",
        "Negotiate updated terms with {}",
        "Execute contract renewal with {}",
    ],
    "Lead digital transformation for {}": [
        "Assess current digital maturity for {}",
        "Define transformation roadmap for {}",
        "Identify technology requirements for {}",
        "Plan change management strategy for {}",
        "Execute pilot program with {}",
        "Scale transformation initiatives for {}",
    ],
    "Oversee compliance implementation for {}": [
        "Conduct compliance gap analysis for {}",
        "Develop compliance framework for {}",
        "Implement security controls for {}",
        "Train compliance team at {}",
        "Execute compliance audit for {}",
        "Maintain ongoing compliance for {}",
    ],
    "Execute competitive analysis for {}": [
        "Research competitive landscape for {}",
        "Analyze competitor strengths and weaknesses for {}",
        "Develop competitive positioning for {}",
        "Create competitive battlecards for {}",
        "Train sales team on competitive strategy for {}",
        "Monitor competitive threats for {}",
    ],
    "Manage vendor evaluation for {}": [
        "Define vendor selection criteria for {}",
        "Research potential vendors for {}",
        "Conduct vendor presentations for {}",
        "Analyze vendor proposals for {}",
        "Make vendor recommendation to {}",
        "Negotiate vendor contract for {}",
    ],
}

# Dynamic choices from model metadata - removed hardcoded lists

def get_opportunity_stages():
    """Get opportunity stages from model metadata"""
    from app.models import Opportunity
    from app.utils.core.model_introspection import ModelIntrospector
    return [choice[0] for choice in ModelIntrospector.get_field_choices(Opportunity, 'stage')]

def get_task_priorities():
    """Get task priorities from model metadata"""
    from app.models import Task
    from app.utils.core.model_introspection import ModelIntrospector
    return [choice[0] for choice in ModelIntrospector.get_field_choices(Task, 'priority')]

def get_task_statuses():
    """Get task statuses from model metadata"""
    from app.models import Task
    from app.utils.core.model_introspection import ModelIntrospector
    return [choice[0] for choice in ModelIntrospector.get_field_choices(Task, 'status')]

def get_next_step_types():
    """Get next step types from model metadata"""
    from app.models import Task
    from app.utils.core.model_introspection import ModelIntrospector
    return [choice[0] for choice in ModelIntrospector.get_field_choices(Task, 'next_step_type')]

def get_dependency_types():
    """Get dependency types from model metadata"""
    from app.models import Task
    from app.utils.core.model_introspection import ModelIntrospector
    return [choice[0] for choice in ModelIntrospector.get_field_choices(Task, 'dependency_type')]


def generate_deal_value():
    """Generate deal values between $10,000 and $300,000 with realistic distribution"""
    # 30% small deals ($10K-$50K), 50% medium deals ($50K-$150K), 20% large deals ($150K-$300K)
    tier = random.choices(["small", "medium", "large"], weights=[30, 50, 20])[0]

    if tier == "small":
        return random.randint(10000, 50000)
    elif tier == "medium":
        return random.randint(50000, 150000)
    else:
        return random.randint(150000, 300000)


def create_companies():
    """Create sample companies with enhanced data"""
    companies = []
    for company_data in COMPANY_DATA:
        company = Company(
            name=company_data["name"],
            industry=company_data["industry"],
            website=company_data["website"],
        )
        companies.append(company)
        db.session.add(company)

    db.session.commit()
    print(f"Created {len(companies)} companies")
    return companies


def create_contacts(companies):
    """Create sample stakeholders for companies with better distribution"""
    contacts = []
    used_names = set()

    for company in companies:
        # Create 1-2 contacts per company to avoid complex relationships
        num_contacts = random.randint(1, 2)

        for i in range(num_contacts):
            # Ensure unique names
            available_names = [name for name in CONTACT_NAMES if name not in used_names]
            if not available_names:
                break

            name = random.choice(available_names)
            used_names.add(name)

            # Generate realistic email from name and company
            email_name = name.lower().replace(" ", ".")
            domain = (
                company.website.replace("https://", "")
                if company.website
                else "example.com"
            )
            email = f"{email_name}@{domain}"

            # Some contacts may be missing phone/email for testing filter scenarios
            has_email = random.random() > 0.1  # 90% have email
            has_phone = random.random() > 0.2  # 80% have phone

            contact = Stakeholder(
                name=name,
                job_title=random.choice(STAKEHOLDER_JOB_TITLES),
                email=email if has_email else None,
                phone=(
                    f"+1-{random.randint(100,999)}-{random.randint(100,999)}-{random.randint(1000,9999)}"
                    if has_phone
                    else None
                ),
                company_id=company.id,
            )
            contacts.append(contact)
            db.session.add(contact)

    db.session.commit()
    print(f"Created {len(contacts)} contacts")
    return contacts


def create_team_members():
    """Create team members (Users) with job titles for grouping functionality"""
    team_members = []
    
    for name in TEAM_MEMBER_NAMES:
        # Generate realistic email from name
        email_name = name.lower().replace(" ", ".")
        email = f"{email_name}@company.com"
        
        team_member = User(
            name=name,
            email=email,
            job_title=random.choice(TEAM_JOB_TITLES),
            department=random.choice(DEPARTMENTS)
        )
        team_members.append(team_member)
        db.session.add(team_member)
    
    db.session.commit()
    print(f"Created {len(team_members)} team members")
    return team_members


def create_opportunities(companies, contacts):
    """Create opportunities with comprehensive deal value range"""
    opportunities = []

    for company in companies:
        # Create 1-2 opportunities per company to simplify relationships
        num_opps = random.randint(1, 2)

        company_contacts = [c for c in contacts if c.company_id == company.id]

        for i in range(num_opps):
            # Generate deal value in the specified range
            deal_value = generate_deal_value()
            
            # Generate priority based on deal value
            if deal_value >= 100000:
                priority = 'high' 
            elif deal_value >= 50000:
                priority = 'medium'
            else:
                priority = 'low'

            opportunity = Opportunity(
                name=f"{random.choice(OPPORTUNITY_TEMPLATES)} - {company.name}",
                value=deal_value,
                probability=random.randint(10, 95),
                priority=priority,
                expected_close_date=date.today()
                + timedelta(days=random.randint(15, 365)),
                stage=random.choice(get_opportunity_stages()),
                company_id=company.id,
                created_at=datetime.now() - timedelta(days=random.randint(1, 120)),
            )

            # Associate with 1 stakeholder from the company  
            if company_contacts:
                selected_contact = random.choice(company_contacts)
                opportunity.stakeholders.append(selected_contact)

            opportunities.append(opportunity)
            db.session.add(opportunity)

    db.session.commit()
    print(
        f"Created {len(opportunities)} opportunities with values ranging ${min(opp.value for opp in opportunities):,} to ${max(opp.value for opp in opportunities):,}"
    )
    return opportunities


def create_comprehensive_tasks(companies, contacts, opportunities):
    """Create comprehensive mix of single, multi, and multi-entity linked tasks"""
    tasks = []
    entities = []

    # Collect all entities for task assignment
    for company in companies:
        entities.append(("company", company.id, company.name))
    for contact in contacts:
        entities.append(("stakeholder", contact.id, contact.name))
    for opportunity in opportunities:
        entities.append(("opportunity", opportunity.id, opportunity.name))

    # 1. Create single tasks (40% of total - 40 tasks)
    print("Creating single tasks...")
    single_task_count = 40
    for i in range(single_task_count):
        entity_type, entity_id, entity_name = random.choice(entities)

        template = random.choice(TASK_TEMPLATES)
        description = template.format(entity_name)

        # Realistic date distribution
        days_offset = random.choices(
            [
                random.randint(-45, -1),  # Overdue (20%)
                random.randint(0, 0),  # Due today (5%)
                random.randint(1, 7),  # This week (25%)
                random.randint(8, 30),  # This month (30%)
                random.randint(31, 90),  # Later (20%)
            ],
            weights=[20, 5, 25, 30, 20],
        )[0]

        due_date = date.today() + timedelta(days=days_offset)

        # Status based on due date for realism
        if days_offset < -15:
            status = random.choice(["in-progress", "complete"])
        elif days_offset < 0:
            status = random.choice(["todo", "in-progress", "in-progress"])
        else:
            status = random.choice(["todo", "todo", "in-progress", "complete"])

        task = Task(
            description=description,
            due_date=due_date,
            priority=random.choice(get_task_priorities()),
            status=status,
            next_step_type=random.choice(get_next_step_types()),
            task_type="single",
            created_at=datetime.now() - timedelta(days=random.randint(1, 90)),
        )

        if status == "complete":
            task.completed_at = datetime.now() - timedelta(days=random.randint(1, 30))

        tasks.append(task)
        db.session.add(task)

    db.session.flush()

    # 2. Create multi-entity linked tasks (20% of total - 20 tasks)
    print("Creating multi-entity linked tasks...")
    multi_entity_task_count = 20
    for i in range(multi_entity_task_count):
        # Pick a primary entity for the task description
        primary_entity_type, primary_entity_id, primary_entity_name = random.choice(
            entities
        )

        template = random.choice(TASK_TEMPLATES)
        description = template.format(primary_entity_name)

        # Create task with primary entity
        task = Task(
            description=description,
            due_date=date.today() + timedelta(days=random.randint(-30, 60)),
            priority=random.choice(get_task_priorities()),
            status=random.choice(get_task_statuses()),
            next_step_type=random.choice(get_next_step_types()),
            task_type="single",
            created_at=datetime.now() - timedelta(days=random.randint(1, 60)),
        )

        if task.status == "complete":
            task.completed_at = datetime.now() - timedelta(days=random.randint(1, 20))

        tasks.append(task)
        db.session.add(task)
        db.session.flush()  # Get task ID

        # Link to 2-4 additional entities using the junction table system
        num_links = random.randint(2, 4)
        available_entities = [
            e
            for e in entities
            if not (e[0] == primary_entity_type and e[1] == primary_entity_id)
        ]
        selected_entities = random.sample(
            available_entities, min(num_links, len(available_entities))
        )

        for link_entity_type, link_entity_id, _ in selected_entities:
            task.add_linked_entity(link_entity_type, link_entity_id)

    # 3. Create parent-child task workflows (40% of total - 12 parent tasks with children)
    print("Creating multi-task workflows...")
    parent_task_count = 12
    for i in range(parent_task_count):
        entity_type, entity_id, entity_name = random.choice(entities)

        # Choose parent task template
        parent_template = random.choice(PARENT_TASK_TEMPLATES)
        parent_description = parent_template.format(entity_name)

        # Parent task timeline
        parent_days_offset = random.randint(10, 120)
        parent_due_date = date.today() + timedelta(days=parent_days_offset)

        dependency_type = random.choice(get_dependency_types())
        parent_status = random.choice([s for s in get_task_statuses() if s != "complete"])

        parent_task = Task(
            description=parent_description,
            due_date=parent_due_date,
            priority=random.choice(get_task_priorities()),
            status=parent_status,
            next_step_type=random.choice(get_next_step_types()),
            task_type="parent",
            dependency_type=dependency_type,
            created_at=datetime.now() - timedelta(days=random.randint(1, 45)),
        )

        tasks.append(parent_task)
        db.session.add(parent_task)
        db.session.flush()  # Get parent task ID

        # Add multi-entity links to parent task (2-3 entities)
        num_links = random.randint(2, 3)
        selected_entities = random.sample(entities, min(num_links, len(entities)))
        for link_entity_type, link_entity_id, _ in selected_entities:
            parent_task.add_linked_entity(link_entity_type, link_entity_id)

        # Create child tasks
        if parent_template in SUBTASK_TEMPLATES:
            child_templates = SUBTASK_TEMPLATES[parent_template]
            num_children = random.randint(4, len(child_templates))
            selected_child_templates = random.sample(child_templates, num_children)

            for j, child_template in enumerate(selected_child_templates):
                child_description = child_template.format(entity_name)

                # Child task scheduling based on dependency type
                if dependency_type == "sequential":
                    # Sequential: stagger child tasks over time
                    days_per_task = max(1, parent_days_offset // (num_children + 1))
                    child_days_offset = days_per_task * (j + 1)
                else:
                    # Parallel: children can run concurrently
                    child_days_offset = random.randint(1, parent_days_offset - 5)

                child_due_date = date.today() + timedelta(
                    days=max(1, child_days_offset)
                )

                # Child status based on parent status and sequence
                if parent_status == "in-progress":
                    if dependency_type == "sequential" and j < num_children // 2:
                        child_status = random.choice([s for s in get_task_statuses() if s in ["complete", "in-progress"]])
                    else:
                        child_status = random.choice([s for s in get_task_statuses() if s in ["todo", "in-progress"]])
                else:
                    child_status = [s for s in get_task_statuses() if s == "todo"][0]

                child_task = Task(
                    description=child_description,
                    due_date=child_due_date,
                    priority=parent_task.priority,  # Inherit parent priority
                    status=child_status,
                    next_step_type=random.choice(get_next_step_types()),
                    task_type="child",
                    parent_task_id=parent_task.id,
                    sequence_order=j + 1,
                    dependency_type=dependency_type,
                    created_at=datetime.now() - timedelta(days=random.randint(1, 45)),
                )

                if child_status == "complete":
                    child_task.completed_at = datetime.now() - timedelta(
                        days=random.randint(1, 20)
                    )

                tasks.append(child_task)
                db.session.add(child_task)
                db.session.flush()

                # Child tasks inherit some parent entity links
                inheritance_entities = random.sample(
                    selected_entities, random.randint(1, len(selected_entities))
                )
                for link_entity_type, link_entity_id, _ in inheritance_entities:
                    child_task.add_linked_entity(link_entity_type, link_entity_id)

    db.session.commit()

    # Calculate task distribution
    single_tasks = [t for t in tasks if t.task_type == "single"]
    parent_tasks = [t for t in tasks if t.task_type == "parent"]
    child_tasks = [t for t in tasks if t.task_type == "child"]
    multi_entity_tasks = [
        t for t in tasks if t.task_type == "single" and len(t.linked_entities) > 1
    ]

    print(f"Created {len(tasks)} total tasks:")
    print(f"  - {len(single_tasks)} single tasks")
    print(f"  - {len(multi_entity_tasks)} multi-entity linked tasks")
    print(f"  - {len(parent_tasks)} parent tasks with {len(child_tasks)} children")
    print(
        f"  - Task priority distribution: {[t.priority for t in tasks].count('high')} high, {[t.priority for t in tasks].count('medium')} medium, {[t.priority for t in tasks].count('low')} low"
    )

    return tasks


def create_notes(companies, contacts, opportunities, tasks):
    """Create comprehensive notes for testing"""
    notes = []
    entities = []

    # Collect all entities
    for company in companies:
        entities.append(("company", company.id))
    for contact in contacts:
        entities.append(("stakeholder", contact.id))
    for opportunity in opportunities:
        entities.append(("opportunity", opportunity.id))
    for task in tasks[:20]:  # Limit to first 20 tasks to avoid too many notes
        entities.append(("task", task.id))

    note_templates = [
        "Initial discovery call completed. Strong alignment with our solution capabilities.",
        "Follow-up meeting scheduled. Decision maker will be present next week.",
        "Demo presentation delivered. Technical team was impressed with platform features.",
        "Budget discussion progressing well. Numbers are within their approved range.",
        "Stakeholder alignment meeting planned. Need to address procurement concerns.",
        "Competitive analysis completed. We have clear differentiation advantages.",
        "Technical evaluation in progress. Awaiting security team sign-off.",
        "Contract negotiation initiated. Legal teams are reviewing terms.",
        "Implementation timeline discussed. Go-live target set for next quarter.",
        "Internal champion identified. Will help drive decision process forward.",
        "Risk assessment completed. Mitigation strategies documented.",
        "ROI analysis presented. Payback period within client expectations.",
        "Pilot program proposal submitted. Awaiting approval from executive team.",
        "Training requirements defined. Custom program to be developed.",
        "Integration planning session completed. Technical requirements documented.",
    ]

    # Create 2-3 notes for each entity type
    notes_per_entity_type = {"company": 2, "stakeholder": 1, "opportunity": 3, "task": 1}

    for entity_type, entity_id in entities:
        target_count = notes_per_entity_type.get(entity_type, 1)

        for _ in range(target_count):
            note = Note(
                content=random.choice(note_templates),
                is_internal=random.choice([True, False]),
                entity_type=entity_type,
                entity_id=entity_id,
                created_at=datetime.now() - timedelta(days=random.randint(1, 60)),
            )

            notes.append(note)
            db.session.add(note)

    db.session.commit()
    print(f"Created {len(notes)} notes across all entity types")
    return notes


def seed_database():
    """Main seeding function with comprehensive data generation"""
    print("=== ENHANCED CRM DATABASE SEEDING ===")
    print("Creating comprehensive test data with:")
    print("- Deal values: $10,000 to $300,000")
    print("- Mixed task types: single, multi-entity linked, parent-child workflows")
    print("- Complete entity coverage for all filtering scenarios")
    print()

    # Clear existing data
    print("Clearing existing data...")
    Note.query.delete()
    # Clear task entity relationships (table may not exist in fresh db)  
    try:
        db.session.execute(db.text("DELETE FROM task_entities"))
    except Exception:
        pass  # Table doesn't exist in fresh database
    Task.query.delete()
    # Clear contact-opportunity relationships (table may not exist in fresh db)
    try:
        db.session.execute(db.text("DELETE FROM contact_opportunities"))
    except Exception:
        pass  # Table doesn't exist in fresh database
    Opportunity.query.delete()
    Stakeholder.query.delete()
    Company.query.delete()
    User.query.delete()
    db.session.commit()
    print("Existing data cleared")
    print()

    # Create comprehensive test data
    companies = create_companies()
    db.session.flush()  # Ensure companies have IDs
    
    contacts = create_contacts(companies)
    db.session.flush()  # Ensure contacts have IDs
    
    team_members = create_team_members()
    db.session.flush()  # Ensure team members have IDs
    
    opportunities = create_opportunities(companies, contacts)
    db.session.flush()  # Ensure opportunities have IDs
    
    tasks = create_comprehensive_tasks(companies, contacts, opportunities)
    db.session.flush()  # Ensure tasks have IDs
    
    notes = create_notes(companies, contacts, opportunities, tasks)

    print()
    print("=== SEEDING COMPLETE ===")
    print("Database Statistics:")
    print(f"📊 Companies: {len(companies)}")
    print(f"👥 Contacts: {len(contacts)}")
    print(f"🏢 Team Members: {len(team_members)}")
    print(f"💰 Opportunities: {len(opportunities)}")
    print(f"✅ Tasks: {len(tasks)}")
    print(f"📝 Notes: {len(notes)}")
    print()

    # Detailed opportunity analysis
    opportunity_values = [opp.value for opp in opportunities]
    print("Opportunity Analysis:")
    print(
        f"💎 Deal Value Range: ${min(opportunity_values):,} to ${max(opportunity_values):,}"
    )
    print(
        f"💵 Average Deal Size: ${sum(opportunity_values) // len(opportunity_values):,}"
    )
    print(f"📈 Total Pipeline Value: ${sum(opportunity_values):,}")
    print()

    # Task type distribution
    task_types = {}
    for task in tasks:
        task_types[task.task_type] = task_types.get(task.task_type, 0) + 1

    print("Task Distribution:")
    for task_type, count in task_types.items():
        print(f"🔧 {task_type.title()} Tasks: {count}")

    # Multi-entity task analysis
    multi_entity_count = sum(1 for task in tasks if len(task.linked_entities) > 1)
    print(f"🔗 Multi-Entity Linked Tasks: {multi_entity_count}")
    print()

    print("🎉 Your CRM is now populated with comprehensive, realistic test data!")
    print(
        "🚀 All entity types, filtering scenarios, and task workflows are ready for testing!"
    )


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        seed_database()
