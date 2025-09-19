#!/usr/bin/env python3
"""
Seed data script for CRM application.

Populates the database with sample companies, stakeholders, opportunities, and tasks
including the new created_at field for companies.
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import random

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from app.main import create_app
from app.models import db, Company, Stakeholder, Opportunity, Task, User


def seed_companies():
    """Create sample companies with created_at timestamps."""
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
            "comments": "Leading software development company",
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
            "comments": "Premier healthcare provider",
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
            "comments": "Renewable energy solutions",
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
            "comments": "National retail chain",
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
            "comments": "Online education platform",
        },
    ]

    companies = []
    base_time = datetime.now() - timedelta(days=365)  # Start a year ago

    for i, company_data in enumerate(companies_data):
        # Spread creation times over the past year
        created_at = base_time + timedelta(days=random.randint(0, 365))

        company = Company(created_at=created_at, **company_data)
        companies.append(company)
        db.session.add(company)

    db.session.commit()
    print(f"✓ Created {len(companies)} companies")
    return companies


def seed_stakeholders(companies, users):
    """Create sample stakeholders linked to companies with relationship owners."""
    stakeholders_data = [
        {
            "name": "John Smith",
            "email": "john.smith@techcorp.com",
            "job_title": "CTO",
            "phone": "+1-555-1001",
        },
        {
            "name": "Sarah Johnson",
            "email": "sarah.j@healthfirst.com",
            "job_title": "VP Operations",
            "phone": "+1-555-1002",
        },
        {
            "name": "Mike Chen",
            "email": "mike.chen@greenenergy.com",
            "job_title": "Founder",
            "phone": "+1-555-1003",
        },
        {
            "name": "Lisa Rodriguez",
            "email": "lisa.r@retailmax.com",
            "job_title": "Director of Sales",
            "phone": "+1-555-1004",
        },
        {
            "name": "David Wilson",
            "email": "d.wilson@edutech.edu",
            "job_title": "Head of Product",
            "phone": "+1-555-1005",
        },
    ]

    stakeholders = []
    base_time = datetime.now() - timedelta(days=300)

    meddpicc_roles = [
        ['economic_buyer', 'decision_maker'],
        ['champion', 'influencer'],
        ['user'],
        ['decision_maker', 'influencer'],
        ['champion', 'user']
    ]

    for i, stakeholder_data in enumerate(stakeholders_data):
        created_at = base_time + timedelta(days=random.randint(0, 300))

        stakeholder = Stakeholder(
            company=companies[i % len(companies)],
            created_at=created_at,
            **stakeholder_data,
        )
        stakeholders.append(stakeholder)
        db.session.add(stakeholder)
        db.session.flush()  # Get ID for relationships

        # Assign MEDDPICC roles
        for role in meddpicc_roles[i]:
            stakeholder.add_meddpicc_role(role)

        # Assign relationship owners (random selection of users)
        num_owners = random.randint(1, min(2, len(users)))
        selected_users = random.sample(users, num_owners)
        for user in selected_users:
            stakeholder.assign_relationship_owner(user.id)

    db.session.commit()
    print(f"✓ Created {len(stakeholders)} stakeholders with roles and owners")
    return stakeholders


def seed_opportunities(companies):
    """Create sample opportunities linked to companies."""
    opportunities_data = [
        {
            "name": "Software License Deal",
            "value": 150000,
            "probability": 75,
            "stage": "proposal",
            "priority": "high",
        },
        {
            "name": "Healthcare System Upgrade",
            "value": 500000,
            "probability": 60,
            "stage": "negotiation",
            "priority": "high",
        },
        {
            "name": "Solar Panel Installation",
            "value": 75000,
            "probability": 90,
            "stage": "closed_won",
            "priority": "medium",
        },
        {
            "name": "Retail POS System",
            "value": 250000,
            "probability": 45,
            "stage": "discovery",
            "priority": "medium",
        },
        {
            "name": "Learning Management System",
            "value": 100000,
            "probability": 80,
            "stage": "proposal",
            "priority": "low",
        },
    ]

    opportunities = []
    base_time = datetime.now() - timedelta(days=180)

    for i, opp_data in enumerate(opportunities_data):
        created_at = base_time + timedelta(days=random.randint(0, 180))
        expected_close_date = created_at + timedelta(days=random.randint(30, 120))

        opportunity = Opportunity(
            company=companies[i % len(companies)],
            created_at=created_at,
            expected_close_date=expected_close_date.date(),
            **opp_data,
        )
        opportunities.append(opportunity)
        db.session.add(opportunity)

    db.session.commit()
    print(f"✓ Created {len(opportunities)} opportunities")
    return opportunities


def seed_tasks():
    """Create sample tasks."""
    tasks_data = [
        {"description": "Follow up on proposal", "priority": "high", "status": "todo"},
        {
            "description": "Schedule demo meeting",
            "priority": "medium",
            "status": "in_progress",
        },
        {
            "description": "Send contract for review",
            "priority": "high",
            "status": "todo",
        },
        {
            "description": "Conduct technical assessment",
            "priority": "low",
            "status": "complete",
        },
        {
            "description": "Prepare implementation plan",
            "priority": "medium",
            "status": "todo",
        },
    ]

    tasks = []
    base_time = datetime.now() - timedelta(days=60)

    for i, task_data in enumerate(tasks_data):
        created_at = base_time + timedelta(days=random.randint(0, 60))
        due_date = created_at + timedelta(days=random.randint(1, 30))

        task = Task(created_at=created_at, due_date=due_date.date(), **task_data)
        tasks.append(task)
        db.session.add(task)

    db.session.commit()
    print(f"✓ Created {len(tasks)} tasks")
    return tasks


def seed_users():
    """Create sample users."""
    users_data = [
        {
            "name": "Admin User",
            "email": "admin@crm.com",
            "job_title": "System Administrator",
        },
        {
            "name": "Sales Manager",
            "email": "sales@crm.com",
            "job_title": "Sales Manager",
        },
        {
            "name": "Account Executive",
            "email": "ae@crm.com",
            "job_title": "Account Executive",
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
    print(f"✓ Created {len(users)} users")
    return users


def main():
    """Main seeding function."""
    app = create_app()

    with app.app_context():
        print("🌱 Seeding database with sample data...")

        # Clear existing data
        for table in [Task, Opportunity, Stakeholder, Company, User]:
            table.query.delete()
        db.session.commit()
        print("✓ Cleared existing data")

        # Seed new data with created_at fields
        users = seed_users()
        companies = seed_companies()
        stakeholders = seed_stakeholders(companies, users)
        opportunities = seed_opportunities(companies)
        tasks = seed_tasks()

        print("\n🎉 Database seeded successfully!")
        print(f"   {len(companies)} companies")
        print(f"   {len(stakeholders)} stakeholders")
        print(f"   {len(opportunities)} opportunities")
        print(f"   {len(tasks)} tasks")
        print(f"   {len(users)} users")
        print("\n   All entities now have 'Created' timestamps!")


if __name__ == "__main__":
    main()
