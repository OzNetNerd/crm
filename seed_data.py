#!/usr/bin/env python3
"""
Seed data script for CRM application.

Populates the database with comprehensive sample data including all fields,
relationships, and association tables to ensure proper UI and form display.
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta, date
import random

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from app.main import create_app
from app.models import (
    db,
    Company,
    Stakeholder,
    Opportunity,
    Task,
    User,
    Note,
    CompanyAccountTeam,
    OpportunityAccountTeam
)


def seed_users():
    """Create sample users with all fields populated."""
    users_data = [
        {
            "name": "Admin User",
            "email": "admin@crm.com",
            "job_title": "System Administrator",
            "department": "operations",
        },
        {
            "name": "Sarah Mitchell",
            "email": "sarah.mitchell@crm.com",
            "job_title": "Sales Manager",
            "department": "sales",
        },
        {
            "name": "Michael Johnson",
            "email": "michael.j@crm.com",
            "job_title": "Account Executive",
            "department": "sales",
        },
        {
            "name": "Emily Chen",
            "email": "emily.chen@crm.com",
            "job_title": "Senior Sales Rep",
            "department": "sales",
        },
        {
            "name": "David Wilson",
            "email": "david.w@crm.com",
            "job_title": "Customer Success Manager",
            "department": "support",
        },
        {
            "name": "Lisa Thompson",
            "email": "lisa.t@crm.com",
            "job_title": "Technical Lead",
            "department": "engineering",
        },
        {
            "name": "Robert Martinez",
            "email": "robert.m@crm.com",
            "job_title": "Marketing Manager",
            "department": "marketing",
        },
    ]

    users = []
    base_time = datetime.now() - timedelta(days=400)

    for i, user_data in enumerate(users_data):
        created_at = base_time + timedelta(days=random.randint(0, 100))
        user = User(created_at=created_at, **user_data)
        users.append(user)
        db.session.add(user)

    db.session.commit()
    print(f"✓ Created {len(users)} users with departments")
    return users


def seed_companies():
    """Create sample companies with all fields populated."""
    companies_data = [
        {
            "name": "TechCorp Solutions",
            "industry": "technology",
            "website": "https://techcorp.com",
            "size": "medium",
            "phone": "+1-555-0101",
            "address": "123 Tech Street, San Francisco, CA 94105",
            "core_rep": "Alice Anderson",
            "core_sc": "Bob Brown",
            "comments": "Leading software development company. Strong technical team, expanding rapidly. Key decision maker is CTO John Smith.",
        },
        {
            "name": "HealthFirst Medical",
            "industry": "healthcare",
            "website": "https://healthfirst.com",
            "size": "large",
            "phone": "+1-555-0102",
            "address": "456 Medical Ave, Boston, MA 02101",
            "core_rep": "Charlie Chen",
            "core_sc": "Diana Davis",
            "comments": "Premier healthcare provider with 15 locations. Budget cycle starts in Q3. Very process-oriented procurement.",
        },
        {
            "name": "GreenEnergy Inc",
            "industry": "energy",
            "website": "https://greenenergy.com",
            "size": "startup",
            "phone": "+1-555-0103",
            "address": "789 Solar Rd, Austin, TX 78701",
            "core_rep": "Eve Evans",
            "core_sc": "Frank Foster",
            "comments": "Renewable energy startup with innovative solar tech. Fast-moving, founder-led decisions. High growth potential.",
        },
        {
            "name": "RetailMax",
            "industry": "retail",
            "website": "https://retailmax.com",
            "size": "enterprise",
            "phone": "+1-555-0104",
            "address": "321 Commerce Blvd, Chicago, IL 60601",
            "core_rep": "Grace Green",
            "core_sc": "Henry Harris",
            "comments": "National retail chain with 500+ stores. Complex approval process. Need enterprise-level support.",
        },
        {
            "name": "EduTech Academy",
            "industry": "education",
            "website": "https://edutech.edu",
            "size": "small",
            "phone": "+1-555-0105",
            "address": "654 Learning Lane, Seattle, WA 98101",
            "core_rep": "Ivy Ingram",
            "core_sc": "Jack Jackson",
            "comments": "Online education platform targeting K-12. Price-sensitive but values quality. Decision by committee.",
        },
        {
            "name": "FinanceCore Banking",
            "industry": "finance",
            "website": "https://financecore.com",
            "size": "large",
            "phone": "+1-555-0106",
            "address": "999 Wall Street, New York, NY 10005",
            "core_rep": "Kevin Kumar",
            "core_sc": "Laura Lee",
            "comments": "Regional bank with strict compliance requirements. Long sales cycle but high value deals.",
        },
        {
            "name": "Manufacturing Plus",
            "industry": "manufacturing",
            "website": "https://mfgplus.com",
            "size": "medium",
            "phone": "+1-555-0107",
            "address": "555 Factory Drive, Detroit, MI 48201",
            "core_rep": "Mark Miller",
            "core_sc": "Nancy Nelson",
            "comments": "Auto parts manufacturer. Cost-focused, needs ROI justification. Prefer quarterly payment terms.",
        },
        {
            "name": "ConsultPro Services",
            "industry": "consulting",
            "website": "https://consultpro.com",
            "size": "small",
            "phone": "+1-555-0108",
            "address": "777 Advisory Ave, Washington, DC 20001",
            "core_rep": "Oliver O'Brien",
            "core_sc": "Patricia Park",
            "comments": "Management consulting firm. Tech-savvy early adopters. Good reference customer potential.",
        },
    ]

    companies = []
    base_time = datetime.now() - timedelta(days=365)

    for i, company_data in enumerate(companies_data):
        created_at = base_time + timedelta(days=random.randint(0, 365))
        updated_at = created_at + timedelta(days=random.randint(0, 30))
        company = Company(created_at=created_at, updated_at=updated_at, **company_data)
        companies.append(company)
        db.session.add(company)

    db.session.commit()
    print(f"✓ Created {len(companies)} companies with comments")
    return companies


def seed_stakeholders(companies, users):
    """Create sample stakeholders with all fields populated."""
    stakeholders_data = [
        # TechCorp Solutions stakeholders
        {
            "name": "John Smith",
            "email": "john.smith@techcorp.com",
            "job_title": "CTO",
            "phone": "+1-555-1001",
            "company_idx": 0,
            "comments": "Technical decision maker. Former Google engineer. Prefers detailed technical discussions.",
            "meddpicc_roles": ["economic_buyer", "decision_maker"],
        },
        {
            "name": "Amanda Williams",
            "email": "amanda.w@techcorp.com",
            "job_title": "VP Engineering",
            "phone": "+1-555-1011",
            "company_idx": 0,
            "comments": "Reports to CTO. Manages dev team of 50+. Focus on scalability.",
            "meddpicc_roles": ["influencer", "champion"],
        },
        # HealthFirst Medical stakeholders
        {
            "name": "Sarah Johnson",
            "email": "sarah.j@healthfirst.com",
            "job_title": "VP Operations",
            "phone": "+1-555-1002",
            "company_idx": 1,
            "comments": "Oversees all hospital operations. MBA from Wharton. Very data-driven.",
            "meddpicc_roles": ["decision_maker", "influencer"],
        },
        {
            "name": "Dr. Robert Lee",
            "email": "robert.lee@healthfirst.com",
            "job_title": "Chief Medical Officer",
            "phone": "+1-555-1012",
            "company_idx": 1,
            "comments": "Final say on all medical technology purchases. Needs clinical evidence.",
            "meddpicc_roles": ["economic_buyer"],
        },
        # GreenEnergy Inc stakeholders
        {
            "name": "Mike Chen",
            "email": "mike.chen@greenenergy.com",
            "job_title": "Founder & CEO",
            "phone": "+1-555-1003",
            "company_idx": 2,
            "comments": "Serial entrepreneur. Quick decision maker. Values innovation and speed.",
            "meddpicc_roles": ["economic_buyer", "decision_maker", "champion"],
        },
        {
            "name": "Jessica Taylor",
            "email": "jessica.t@greenenergy.com",
            "job_title": "Head of Engineering",
            "phone": "+1-555-1013",
            "company_idx": 2,
            "comments": "MIT graduate. Building team rapidly. Needs flexible solutions.",
            "meddpicc_roles": ["influencer", "user"],
        },
        # RetailMax stakeholders
        {
            "name": "Lisa Rodriguez",
            "email": "lisa.r@retailmax.com",
            "job_title": "Director of IT",
            "phone": "+1-555-1004",
            "company_idx": 3,
            "comments": "15 years at company. Risk-averse. Needs extensive documentation.",
            "meddpicc_roles": ["influencer"],
        },
        {
            "name": "Thomas Anderson",
            "email": "thomas.a@retailmax.com",
            "job_title": "CFO",
            "phone": "+1-555-1014",
            "company_idx": 3,
            "comments": "Controls all major purchasing decisions. Focus on TCO and ROI.",
            "meddpicc_roles": ["economic_buyer"],
        },
        {
            "name": "Maria Garcia",
            "email": "maria.g@retailmax.com",
            "job_title": "VP Store Operations",
            "phone": "+1-555-1024",
            "company_idx": 3,
            "comments": "End user advocate. Needs simple, reliable solutions for store staff.",
            "meddpicc_roles": ["user", "influencer"],
        },
        # EduTech Academy stakeholders
        {
            "name": "David Wilson",
            "email": "d.wilson@edutech.edu",
            "job_title": "Head of Product",
            "phone": "+1-555-1005",
            "company_idx": 4,
            "comments": "Former teacher turned product manager. Student-focused mindset.",
            "meddpicc_roles": ["champion", "influencer"],
        },
        {
            "name": "Jennifer Brown",
            "email": "jennifer.b@edutech.edu",
            "job_title": "CEO",
            "phone": "+1-555-1015",
            "company_idx": 4,
            "comments": "Ed-tech veteran. Well-connected in education sector. Visionary leader.",
            "meddpicc_roles": ["economic_buyer", "decision_maker"],
        },
    ]

    stakeholders = []
    base_time = datetime.now() - timedelta(days=300)

    for i, stakeholder_data in enumerate(stakeholders_data):
        created_at = base_time + timedelta(days=random.randint(0, 300))
        updated_at = created_at + timedelta(days=random.randint(0, 60))
        last_contacted = created_at + timedelta(days=random.randint(1, 120))

        company_idx = stakeholder_data.pop("company_idx")
        meddpicc_roles = stakeholder_data.pop("meddpicc_roles")

        stakeholder = Stakeholder(
            company_id=companies[company_idx].id,
            created_at=created_at,
            updated_at=updated_at,
            last_contacted=last_contacted,
            **stakeholder_data,
        )
        stakeholders.append(stakeholder)
        db.session.add(stakeholder)
        db.session.flush()  # Get ID for relationships

        # Assign MEDDPICC roles
        for role in meddpicc_roles:
            stakeholder.add_meddpicc_role(role)

        # Assign relationship owners (sales team members)
        sales_users = [u for u in users if u.department == "sales"]
        num_owners = random.randint(1, min(2, len(sales_users)))
        selected_users = random.sample(sales_users, num_owners)
        for user in selected_users:
            stakeholder.assign_relationship_owner(user.id)

    db.session.commit()
    print(f"✓ Created {len(stakeholders)} stakeholders with comments and roles")
    return stakeholders


def seed_opportunities(companies):
    """Create sample opportunities with all fields populated."""
    opportunities_data = [
        {
            "name": "Enterprise Software License Deal",
            "value": 150000,
            "probability": 75,
            "stage": "proposal",
            "priority": "high",
            "company_idx": 0,
            "comments": "Q4 budget available. Competing against Microsoft. Need to emphasize our integration capabilities.",
        },
        {
            "name": "Healthcare System Platform Upgrade",
            "value": 500000,
            "probability": 60,
            "stage": "negotiation",
            "priority": "high",
            "company_idx": 1,
            "comments": "Multi-year contract potential. Compliance requirements are critical. Legal review in progress.",
        },
        {
            "name": "Solar Panel Monitoring System",
            "value": 75000,
            "probability": 90,
            "stage": "closed-won",
            "priority": "medium",
            "company_idx": 2,
            "comments": "Verbal confirmation received. Contract signing next week. Upsell opportunity for analytics add-on.",
        },
        {
            "name": "Retail POS System Modernization",
            "value": 250000,
            "probability": 45,
            "stage": "discovery",
            "priority": "medium",
            "company_idx": 3,
            "comments": "Early stage discussions. Budget not confirmed. Need executive sponsor buy-in.",
        },
        {
            "name": "Learning Management Platform",
            "value": 100000,
            "probability": 80,
            "stage": "proposal",
            "priority": "high",
            "company_idx": 4,
            "comments": "Pilot was successful. Expanding to full deployment. Payment terms under discussion.",
        },
        {
            "name": "TechCorp Cloud Migration",
            "value": 200000,
            "probability": 30,
            "stage": "qualification",
            "priority": "low",
            "company_idx": 0,
            "comments": "Exploratory discussions. Timeline uncertain. Keep warm for next fiscal year.",
        },
        {
            "name": "FinanceCore Security Suite",
            "value": 350000,
            "probability": 65,
            "stage": "proposal",
            "priority": "high",
            "company_idx": 5,
            "comments": "Urgent need due to recent security audit. Fast-track approval process initiated.",
        },
        {
            "name": "Manufacturing ERP Integration",
            "value": 180000,
            "probability": 50,
            "stage": "discovery",
            "priority": "medium",
            "company_idx": 6,
            "comments": "Replacing legacy system. Change management will be critical. Phased rollout planned.",
        },
        {
            "name": "ConsultPro Analytics Platform",
            "value": 60000,
            "probability": 85,
            "stage": "negotiation",
            "priority": "medium",
            "company_idx": 7,
            "comments": "Standard package with customizations. Reference customer agreement included.",
        },
    ]

    opportunities = []
    base_time = datetime.now() - timedelta(days=180)

    for i, opp_data in enumerate(opportunities_data):
        created_at = base_time + timedelta(days=random.randint(0, 180))
        expected_close_date = created_at + timedelta(days=random.randint(30, 120))
        updated_at = created_at + timedelta(days=random.randint(0, 30))

        company_idx = opp_data.pop("company_idx")

        opportunity = Opportunity(
            company_id=companies[company_idx].id,
            created_at=created_at,
            updated_at=updated_at,
            expected_close_date=expected_close_date.date(),
            **opp_data,
        )
        opportunities.append(opportunity)
        db.session.add(opportunity)

    db.session.commit()
    print(f"✓ Created {len(opportunities)} opportunities with comments")
    return opportunities


def seed_tasks(companies, opportunities, stakeholders):
    """Create sample tasks with all fields including parent-child relationships."""
    tasks_data = [
        # Parent task with children
        {
            "description": "Complete Q4 Sales Campaign for TechCorp",
            "priority": "high",
            "status": "in_progress",
            "next_step_type": "meeting",
            "task_type": "parent",
            "comments": "Critical for year-end targets. CEO visibility.",
            "due_days": 15,
            "children": [
                {
                    "description": "Prepare technical demo for TechCorp team",
                    "priority": "high",
                    "status": "complete",
                    "next_step_type": "demo",
                    "due_days": 3,
                    "comments": "Include integration scenarios",
                },
                {
                    "description": "Send follow-up proposal with pricing",
                    "priority": "high",
                    "status": "in_progress",
                    "next_step_type": "email",
                    "due_days": 5,
                    "comments": "Include volume discounts",
                },
                {
                    "description": "Schedule executive meeting",
                    "priority": "medium",
                    "status": "todo",
                    "next_step_type": "call",
                    "due_days": 10,
                    "comments": "CEO to CEO discussion needed",
                },
            ],
        },
        # Standalone tasks
        {
            "description": "Follow up with HealthFirst on contract terms",
            "priority": "high",
            "status": "todo",
            "next_step_type": "email",
            "comments": "Legal team has approved our standard terms",
            "due_days": 2,
        },
        {
            "description": "Conduct technical assessment for RetailMax",
            "priority": "medium",
            "status": "todo",
            "next_step_type": "meeting",
            "comments": "Need to review their current infrastructure",
            "due_days": 7,
        },
        {
            "description": "Send GreenEnergy implementation plan",
            "priority": "high",
            "status": "complete",
            "next_step_type": "email",
            "comments": "Completed last week. Waiting for feedback.",
            "due_days": -5,
        },
        {
            "description": "Prepare ROI analysis for FinanceCore",
            "priority": "high",
            "status": "in_progress",
            "next_step_type": "email",
            "comments": "CFO requested detailed 3-year projection",
            "due_days": 4,
        },
        # Another parent task
        {
            "description": "Onboard EduTech Academy as new customer",
            "priority": "medium",
            "status": "todo",
            "next_step_type": "meeting",
            "task_type": "parent",
            "comments": "Standard onboarding process",
            "due_days": 20,
            "children": [
                {
                    "description": "Setup initial account configuration",
                    "priority": "medium",
                    "status": "todo",
                    "next_step_type": "email",
                    "due_days": 12,
                    "comments": "Get IT requirements first",
                },
                {
                    "description": "Schedule training session",
                    "priority": "low",
                    "status": "todo",
                    "next_step_type": "call",
                    "due_days": 15,
                    "comments": "2-hour virtual session",
                },
            ],
        },
        {
            "description": "Review Manufacturing Plus requirements document",
            "priority": "low",
            "status": "complete",
            "next_step_type": "email",
            "comments": "Completed and sent feedback yesterday",
            "due_days": -1,
        },
        {
            "description": "Call ConsultPro to discuss expansion",
            "priority": "medium",
            "status": "todo",
            "next_step_type": "call",
            "comments": "They want to add 10 more licenses",
            "due_days": 3,
        },
    ]

    tasks = []
    base_time = datetime.now() - timedelta(days=60)

    for task_data in tasks_data:
        created_at = base_time + timedelta(days=random.randint(0, 60))
        due_days = task_data.pop("due_days")
        due_date = created_at + timedelta(days=due_days)
        updated_at = created_at + timedelta(days=random.randint(0, 15))

        children_data = task_data.pop("children", [])

        # Set completed_at for completed tasks
        completed_at = None
        if task_data.get("status") == "complete":
            completed_at = updated_at + timedelta(days=random.randint(1, 5))

        # Create parent task
        parent_task = Task(
            created_at=created_at,
            updated_at=updated_at,
            due_date=due_date.date(),
            completed_at=completed_at,
            dependency_type="sequential" if children_data else "parallel",
            **task_data
        )
        tasks.append(parent_task)
        db.session.add(parent_task)
        db.session.flush()  # Get ID for children

        # Create child tasks
        for idx, child_data in enumerate(children_data):
            child_due_days = child_data.pop("due_days")
            child_due_date = created_at + timedelta(days=child_due_days)
            child_created_at = created_at + timedelta(days=idx)

            child_completed_at = None
            if child_data.get("status") == "complete":
                child_completed_at = child_created_at + timedelta(days=random.randint(1, 3))

            child_task = Task(
                created_at=child_created_at,
                updated_at=child_created_at + timedelta(days=random.randint(0, 5)),
                due_date=child_due_date.date(),
                completed_at=child_completed_at,
                task_type="child",
                parent_task_id=parent_task.id,
                sequence_order=idx,
                dependency_type="sequential",
                **child_data
            )
            tasks.append(child_task)
            db.session.add(child_task)

    db.session.commit()
    print(f"✓ Created {len(tasks)} tasks with parent-child relationships")
    return tasks


def seed_notes(companies, stakeholders, opportunities, tasks):
    """Create sample notes attached to various entities."""
    notes_data = [
        {
            "content": "Initial meeting went well. They're interested in our integration capabilities. Need to follow up with technical documentation.",
            "is_internal": True,
            "entity_type": "company",
            "entity_idx": 0,
            "days_ago": 10,
        },
        {
            "content": "Budget approval expected by end of month. CFO is supportive.",
            "is_internal": True,
            "entity_type": "opportunity",
            "entity_idx": 0,
            "days_ago": 5,
        },
        {
            "content": "Prefers morning meetings. Very technical, appreciates detailed discussions.",
            "is_internal": True,
            "entity_type": "stakeholder",
            "entity_idx": 0,
            "days_ago": 15,
        },
        {
            "content": "Customer confirmed receipt of proposal. Will review internally and get back to us next week.",
            "is_internal": False,
            "entity_type": "opportunity",
            "entity_idx": 1,
            "days_ago": 3,
        },
        {
            "content": "Task delayed due to customer availability. Rescheduled for next week.",
            "is_internal": True,
            "entity_type": "task",
            "entity_idx": 1,
            "days_ago": 2,
        },
        {
            "content": "Competitor is also bidding. We need to emphasize our superior support and training.",
            "is_internal": True,
            "entity_type": "opportunity",
            "entity_idx": 3,
            "days_ago": 8,
        },
        {
            "content": "Has strong influence over technical decisions. Former colleague of our CTO.",
            "is_internal": True,
            "entity_type": "stakeholder",
            "entity_idx": 2,
            "days_ago": 20,
        },
        {
            "content": "Compliance requirements are their top priority. Need to provide security documentation.",
            "is_internal": True,
            "entity_type": "company",
            "entity_idx": 1,
            "days_ago": 12,
        },
        {
            "content": "Successfully completed POC. Customer is impressed with performance metrics.",
            "is_internal": False,
            "entity_type": "opportunity",
            "entity_idx": 2,
            "days_ago": 1,
        },
        {
            "content": "Quarterly business review scheduled for next month. Prepare upsell opportunities.",
            "is_internal": True,
            "entity_type": "company",
            "entity_idx": 3,
            "days_ago": 7,
        },
    ]

    notes = []
    base_time = datetime.now()

    for note_data in notes_data:
        days_ago = note_data.pop("days_ago")
        created_at = base_time - timedelta(days=days_ago)

        entity_idx = note_data.pop("entity_idx")
        entity_type = note_data["entity_type"]

        # Map entity type to actual entity
        if entity_type == "company":
            entity_id = companies[entity_idx].id
        elif entity_type == "stakeholder":
            entity_id = stakeholders[entity_idx].id
        elif entity_type == "opportunity":
            entity_id = opportunities[entity_idx].id
        elif entity_type == "task":
            entity_id = tasks[entity_idx].id

        note = Note(
            created_at=created_at,
            entity_id=entity_id,
            **note_data
        )
        notes.append(note)
        db.session.add(note)

    db.session.commit()
    print(f"✓ Created {len(notes)} notes for various entities")
    return notes


def seed_company_account_teams(companies, users):
    """Assign users to company account teams."""
    assignments = []
    sales_users = [u for u in users if u.department in ["sales", "support"]]

    for company in companies:
        # Each company gets 2-3 team members
        num_members = random.randint(2, min(3, len(sales_users)))
        selected_users = random.sample(sales_users, num_members)

        for user in selected_users:
            assignment = CompanyAccountTeam(
                company_id=company.id,
                user_id=user.id,
                created_at=company.created_at + timedelta(days=random.randint(1, 30))
            )
            assignments.append(assignment)
            db.session.add(assignment)

    db.session.commit()
    print(f"✓ Created {len(assignments)} company account team assignments")
    return assignments


def seed_opportunity_account_teams(opportunities, users):
    """Assign users to opportunity account teams."""
    assignments = []
    sales_users = [u for u in users if u.department == "sales"]

    for opportunity in opportunities:
        # Each opportunity gets 1-2 team members
        num_members = random.randint(1, min(2, len(sales_users)))
        selected_users = random.sample(sales_users, num_members)

        for user in selected_users:
            assignment = OpportunityAccountTeam(
                opportunity_id=opportunity.id,
                user_id=user.id,
                created_at=opportunity.created_at + timedelta(days=random.randint(1, 15))
            )
            assignments.append(assignment)
            db.session.add(assignment)

    db.session.commit()
    print(f"✓ Created {len(assignments)} opportunity account team assignments")
    return assignments


def seed_stakeholder_opportunities(stakeholders, opportunities):
    """Link stakeholders to opportunities."""
    # Group stakeholders and opportunities by company
    company_stakeholders = {}
    company_opportunities = {}

    for s in stakeholders:
        if s.company_id not in company_stakeholders:
            company_stakeholders[s.company_id] = []
        company_stakeholders[s.company_id].append(s)

    for o in opportunities:
        if o.company_id not in company_opportunities:
            company_opportunities[o.company_id] = []
        company_opportunities[o.company_id].append(o)

    links = 0
    # Link stakeholders to opportunities within the same company
    for company_id in company_stakeholders:
        if company_id in company_opportunities:
            for stakeholder in company_stakeholders[company_id]:
                # Link to 1-2 opportunities from same company
                num_opps = random.randint(1, min(2, len(company_opportunities[company_id])))
                selected_opps = random.sample(company_opportunities[company_id], num_opps)

                for opp in selected_opps:
                    stakeholder.opportunities.append(opp)
                    links += 1

    db.session.commit()
    print(f"✓ Created {links} stakeholder-opportunity relationships")


def seed_task_entities(tasks, companies, opportunities, stakeholders):
    """Link tasks to various entities."""
    links = []

    for task in tasks:
        # Skip child tasks - they inherit parent's entities
        if task.task_type == "child":
            continue

        # Add 1-3 entity links per task
        num_links = random.randint(1, 3)

        # Prioritize linking to opportunities
        if opportunities and random.random() > 0.3:
            opp = random.choice(opportunities)
            task.add_linked_entity("opportunity", opp.id)
            links.append(("opportunity", opp.id))
            num_links -= 1

        # Link to companies
        if companies and num_links > 0 and random.random() > 0.4:
            company = random.choice(companies)
            task.add_linked_entity("company", company.id)
            links.append(("company", company.id))
            num_links -= 1

        # Link to stakeholders
        if stakeholders and num_links > 0 and random.random() > 0.5:
            stakeholder = random.choice(stakeholders)
            task.add_linked_entity("contact", stakeholder.id)
            links.append(("contact", stakeholder.id))

    db.session.commit()
    print(f"✓ Created {len(links)} task-entity relationships")
    return links


def main():
    """Main seeding function with comprehensive data."""
    app = create_app()

    with app.app_context():
        print("🌱 Seeding database with comprehensive sample data...")

        # Import models to ensure they're registered
        from app.models import CompanyAccountTeam, OpportunityAccountTeam

        # Clear existing data in correct order (respecting foreign keys)
        print("🧹 Clearing existing data...")

        # Clear junction tables first
        db.session.execute(db.text("DELETE FROM task_entities"))
        db.session.execute(db.text("DELETE FROM stakeholder_opportunities"))
        db.session.execute(db.text("DELETE FROM stakeholder_relationship_owners"))
        db.session.execute(db.text("DELETE FROM stakeholder_meddpicc_roles"))
        db.session.execute(db.text("DELETE FROM company_account_teams"))
        db.session.execute(db.text("DELETE FROM opportunity_account_teams"))

        # Clear main tables
        Note.query.delete()
        Task.query.delete()
        Opportunity.query.delete()
        Stakeholder.query.delete()
        Company.query.delete()
        User.query.delete()

        db.session.commit()
        print("✓ Cleared all existing data")

        # Seed data in correct order
        users = seed_users()
        companies = seed_companies()
        stakeholders = seed_stakeholders(companies, users)
        opportunities = seed_opportunities(companies)
        tasks = seed_tasks(companies, opportunities, stakeholders)
        notes = seed_notes(companies, stakeholders, opportunities, tasks)

        # Seed relationship tables
        seed_company_account_teams(companies, users)
        seed_opportunity_account_teams(opportunities, users)
        seed_stakeholder_opportunities(stakeholders, opportunities)
        seed_task_entities(tasks, companies, opportunities, stakeholders)

        print("\n🎉 Database seeded successfully with comprehensive data!")
        print(f"   {len(users)} users (with departments)")
        print(f"   {len(companies)} companies (with comments)")
        print(f"   {len(stakeholders)} stakeholders (with comments & MEDDPICC roles)")
        print(f"   {len(opportunities)} opportunities (with comments)")
        print(f"   {len(tasks)} tasks (with parent-child relationships)")
        print(f"   {len(notes)} notes")
        print("\n✅ All relationship tables populated:")
        print("   - Company account teams")
        print("   - Opportunity account teams")
        print("   - Stakeholder-opportunity links")
        print("   - Task-entity links")
        print("   - MEDDPICC roles")
        print("   - Relationship owners")


if __name__ == "__main__":
    main()