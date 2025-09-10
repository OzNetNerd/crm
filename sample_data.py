#!/usr/bin/env python3

from datetime import datetime, date, timedelta
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import create_app
from app.models import db, Company, Contact, Opportunity, Task, Note


def create_sample_data():
    """Create sample data for testing the CRM application"""

    app = create_app()
    with app.app_context():
        # Clear existing data
        db.drop_all()
        db.create_all()

        # Create sample companies
        companies = [
            Company(
                name="TechCorp Solutions",
                industry="Technology",
                website="https://techcorp.example.com",
            ),
            Company(
                name="GreenEnergy Inc",
                industry="Renewable Energy",
                website="https://greenenergy.example.com",
            ),
            Company(
                name="DataFlow Systems",
                industry="Data Analytics",
                website="https://dataflow.example.com",
            ),
            Company(name="CloudFirst Technologies", industry="Cloud Computing"),
            Company(
                name="FinanceMax Ltd",
                industry="Financial Services",
                website="https://financemax.example.com",
            ),
        ]

        for company in companies:
            db.session.add(company)

        db.session.commit()

        # Create sample contacts
        contacts = [
            Contact(
                name="John Smith",
                role="CEO",
                email="john.smith@techcorp.example.com",
                phone="+1-555-0101",
                company_id=1,
            ),
            Contact(
                name="Sarah Johnson",
                role="CTO",
                email="sarah.johnson@techcorp.example.com",
                phone="+1-555-0102",
                company_id=1,
            ),
            Contact(
                name="Mike Chen",
                role="VP Sales",
                email="mike.chen@greenenergy.example.com",
                phone="+1-555-0201",
                company_id=2,
            ),
            Contact(
                name="Lisa Rodriguez",
                role="Product Manager",
                email="lisa.rodriguez@dataflow.example.com",
                phone="+1-555-0301",
                company_id=3,
            ),
            Contact(
                name="David Kim",
                role="Engineering Lead",
                email="david.kim@cloudfirst.example.com",
                company_id=4,
            ),
            Contact(
                name="Emma Wilson",
                role="CFO",
                email="emma.wilson@financemax.example.com",
                phone="+1-555-0501",
                company_id=5,
            ),
        ]

        for contact in contacts:
            db.session.add(contact)

        db.session.commit()

        # Create sample opportunities
        opportunities = [
            Opportunity(
                name="TechCorp Platform Integration",
                company_id=1,
                value=150000.00,
                probability=75,
                expected_close_date=date.today() + timedelta(days=30),
                stage="negotiation",
            ),
            Opportunity(
                name="GreenEnergy Analytics Dashboard",
                company_id=2,
                value=85000.00,
                probability=60,
                expected_close_date=date.today() + timedelta(days=45),
                stage="proposal",
            ),
            Opportunity(
                name="DataFlow Cloud Migration",
                company_id=3,
                value=225000.00,
                probability=40,
                expected_close_date=date.today() + timedelta(days=60),
                stage="qualified",
            ),
            Opportunity(
                name="CloudFirst Consulting Services",
                company_id=4,
                value=75000.00,
                probability=90,
                expected_close_date=date.today() + timedelta(days=15),
                stage="negotiation",
            ),
            Opportunity(
                name="FinanceMax Security Audit",
                company_id=5,
                value=50000.00,
                probability=25,
                expected_close_date=date.today() + timedelta(days=90),
                stage="prospect",
            ),
        ]

        for opportunity in opportunities:
            db.session.add(opportunity)

        db.session.commit()

        # Link contacts to opportunities (many-to-many)
        opportunities[0].contacts.extend(
            [contacts[0], contacts[1]]
        )  # TechCorp opp with John & Sarah
        opportunities[1].contacts.append(contacts[2])  # GreenEnergy with Mike
        opportunities[2].contacts.append(contacts[3])  # DataFlow with Lisa
        opportunities[3].contacts.append(contacts[4])  # CloudFirst with David
        opportunities[4].contacts.append(contacts[5])  # FinanceMax with Emma

        db.session.commit()

        # Create sample tasks
        today = date.today()
        tasks = [
            # Overdue tasks
            Task(
                description="Follow up on TechCorp contract terms",
                due_date=today - timedelta(days=2),
                priority="high",
                status="todo",
                next_step_type="call",
                entity_type="opportunity",
                entity_id=1,
            ),
            Task(
                description="Send revised proposal to GreenEnergy",
                due_date=today - timedelta(days=1),
                priority="medium",
                status="in-progress",
                next_step_type="email",
                entity_type="opportunity",
                entity_id=2,
            ),
            # Today's tasks
            Task(
                description="Prepare demo for DataFlow team",
                due_date=today,
                priority="high",
                status="todo",
                next_step_type="demo",
                entity_type="opportunity",
                entity_id=3,
            ),
            Task(
                description="Schedule call with CloudFirst engineering team",
                due_date=today,
                priority="medium",
                status="todo",
                next_step_type="meeting",
                entity_type="contact",
                entity_id=5,
            ),
            # This week's tasks
            Task(
                description="Review FinanceMax security requirements",
                due_date=today + timedelta(days=2),
                priority="low",
                status="todo",
                entity_type="company",
                entity_id=5,
            ),
            Task(
                description="Update CRM with latest contact information",
                due_date=today + timedelta(days=3),
                priority="low",
                status="todo",
            ),
            # Next week's tasks
            Task(
                description="Quarterly business review with TechCorp",
                due_date=today + timedelta(days=8),
                priority="medium",
                status="todo",
                next_step_type="meeting",
                entity_type="company",
                entity_id=1,
            ),
            # Completed today
            Task(
                description="Research GreenEnergy's competitors",
                due_date=today - timedelta(days=1),
                priority="medium",
                status="complete",
                completed_at=datetime.utcnow(),
                entity_type="company",
                entity_id=2,
            ),
        ]

        for task in tasks:
            db.session.add(task)

        db.session.commit()

        # Create sample notes
        notes = [
            Note(
                content="Initial meeting went very well. They're interested in our platform integration capabilities and want to see a demo next week.",
                is_internal=True,
                entity_type="opportunity",
                entity_id=1,
            ),
            Note(
                content="Client expressed concerns about pricing. Need to prepare a more competitive proposal with flexible payment terms.",
                is_internal=True,
                entity_type="opportunity",
                entity_id=2,
            ),
            Note(
                content="Technical requirements discussion: They need cloud-native solution with 99.9% uptime guarantee.",
                is_internal=False,
                entity_type="opportunity",
                entity_id=3,
            ),
            Note(
                content="David mentioned they're evaluating 3 vendors. We need to differentiate on support and implementation timeline.",
                is_internal=True,
                entity_type="contact",
                entity_id=5,
            ),
            Note(
                content="Compliance requirements are very strict. Need to involve our security team in the next meeting.",
                is_internal=True,
                entity_type="company",
                entity_id=5,
            ),
        ]

        for note in notes:
            db.session.add(note)

        db.session.commit()

        print("Sample data created successfully!")
        print("Created:")
        print(f"  - {len(companies)} companies")
        print(f"  - {len(contacts)} contacts")
        print(f"  - {len(opportunities)} opportunities")
        print(f"  - {len(tasks)} tasks")
        print(f"  - {len(notes)} notes")


if __name__ == "__main__":
    create_sample_data()
