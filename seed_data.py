#!/usr/bin/env python3
"""
CRM Database Seeding Script
Creates realistic test data for all CRM entities
"""

import random
from datetime import datetime, date, timedelta

from app.models import db, Company, Contact, Opportunity, Task, Note
from main import create_app

# Sample data for realistic seeding
INDUSTRIES = [
    'Technology', 'Healthcare', 'Finance', 'Manufacturing', 'Retail',
    'Education', 'Construction', 'Real Estate', 'Consulting', 'Media'
]

COMPANY_DATA = [
    {'name': 'GreenEnergy Solutions', 'industry': 'Technology', 'website': 'https://greenenergy.com'},
    {'name': 'Quantum Analytics', 'industry': 'Technology', 'website': 'https://quantum-analytics.com'},
    {'name': 'MedCore Systems', 'industry': 'Healthcare', 'website': 'https://medcore.com'},
    {'name': 'FinTech Innovators', 'industry': 'Finance', 'website': 'https://fintech-innovators.com'},
    {'name': 'ProManufacturing Co', 'industry': 'Manufacturing', 'website': 'https://promanufacturing.com'},
    {'name': 'RetailMax Group', 'industry': 'Retail', 'website': 'https://retailmax.com'},
    {'name': 'EduTech Solutions', 'industry': 'Education', 'website': 'https://edutech-solutions.com'},
    {'name': 'BuildRight Construction', 'industry': 'Construction', 'website': 'https://buildright.com'},
    {'name': 'Prime Properties LLC', 'industry': 'Real Estate', 'website': 'https://prime-properties.com'},
    {'name': 'Strategic Consulting Partners', 'industry': 'Consulting', 'website': 'https://strategic-consulting.com'},
]

CONTACT_NAMES = [
    'Sarah Johnson', 'Michael Chen', 'Emily Rodriguez', 'David Thompson', 'Lisa Wang',
    'Robert Martinez', 'Jennifer Brown', 'Christopher Lee', 'Amanda Davis', 'Mark Wilson',
    'Jessica Taylor', 'Daniel Anderson', 'Ashley Garcia', 'Matthew Miller', 'Rachel Kim',
    'James Wilson', 'Maria Gonzalez', 'Kevin O\'Connor', 'Nicole Smith', 'Ryan Murphy'
]

ROLES = [
    'CEO', 'CTO', 'VP of Sales', 'Marketing Director', 'Operations Manager',
    'Project Manager', 'Business Development', 'Product Manager', 'IT Director', 'CFO'
]

OPPORTUNITY_TEMPLATES = [
    'CRM Software Implementation',
    'Cloud Migration Project',
    'Digital Marketing Campaign',
    'Website Redesign',
    'Data Analytics Platform',
    'Mobile App Development',
    'Security Assessment',
    'Training Program',
    'Consulting Engagement',
    'Software License Renewal'
]

TASK_TEMPLATES = [
    'Send revised proposal to {}',
    'Schedule follow-up call with {}',
    'Prepare demo presentation for {}',
    'Research {}\'s competitors',
    'Draft contract terms for {}',
    'Conduct needs assessment with {}',
    'Send project timeline to {}',
    'Review budget requirements with {}',
    'Prepare technical documentation for {}',
    'Schedule stakeholder meeting with {}'
]

STAGES = ['prospect', 'qualified', 'proposal', 'negotiation', 'closed']
PRIORITIES = ['high', 'medium', 'low']
STATUSES = ['todo', 'in-progress', 'complete']
NEXT_STEP_TYPES = ['meeting', 'demo', 'call', 'email']

def create_companies():
    """Create sample companies"""
    companies = []
    for company_data in COMPANY_DATA:
        company = Company(
            name=company_data['name'],
            industry=company_data['industry'],
            website=company_data['website']
        )
        companies.append(company)
        db.session.add(company)
    
    db.session.commit()
    print(f"Created {len(companies)} companies")
    return companies

def create_contacts(companies):
    """Create sample contacts for companies"""
    contacts = []
    used_names = set()
    
    for company in companies:
        # Create 2-3 contacts per company
        num_contacts = random.randint(2, 3)
        
        for i in range(num_contacts):
            # Ensure unique names
            available_names = [name for name in CONTACT_NAMES if name not in used_names]
            if not available_names:
                break
                
            name = random.choice(available_names)
            used_names.add(name)
            
            # Generate email from name
            email_name = name.lower().replace(' ', '.')
            domain = company.website.replace('https://', '') if company.website else 'example.com'
            email = f"{email_name}@{domain}"
            
            contact = Contact(
                name=name,
                role=random.choice(ROLES),
                email=email,
                phone=f"+1-{random.randint(100,999)}-{random.randint(100,999)}-{random.randint(1000,9999)}",
                company_id=company.id
            )
            contacts.append(contact)
            db.session.add(contact)
    
    db.session.commit()
    print(f"Created {len(contacts)} contacts")
    return contacts

def create_opportunities(companies, contacts):
    """Create sample opportunities"""
    opportunities = []
    
    for company in companies:
        # Create 1-2 opportunities per company
        num_opps = random.randint(1, 2)
        
        company_contacts = [c for c in contacts if c.company_id == company.id]
        
        for i in range(num_opps):
            opportunity = Opportunity(
                name=f"{random.choice(OPPORTUNITY_TEMPLATES)} - {company.name}",
                value=Decimal(random.randint(5000, 500000)),  # $5,000 to $500,000
                probability=random.randint(10, 90),
                expected_close_date=date.today() + timedelta(days=random.randint(30, 180)),
                stage=random.choice(STAGES),
                company_id=company.id,
                created_at=datetime.now() - timedelta(days=random.randint(1, 90))
            )
            
            # Associate with 1-2 contacts from the company
            num_contacts = min(random.randint(1, 2), len(company_contacts))
            selected_contacts = random.sample(company_contacts, num_contacts)
            opportunity.contacts.extend(selected_contacts)
            
            opportunities.append(opportunity)
            db.session.add(opportunity)
    
    db.session.commit()
    print(f"Created {len(opportunities)} opportunities")
    return opportunities

def create_tasks(companies, contacts, opportunities):
    """Create sample tasks"""
    tasks = []
    entities = []
    
    # Collect all entities for task assignment
    for company in companies:
        entities.append(('company', company.id, company.name))
    for contact in contacts:
        entities.append(('contact', contact.id, contact.name))
    for opportunity in opportunities:
        entities.append(('opportunity', opportunity.id, opportunity.name))
    
    # Create tasks
    for i in range(50):  # Create 50 tasks total
        entity_type, entity_id, entity_name = random.choice(entities)
        
        # Choose task template and format with entity name
        template = random.choice(TASK_TEMPLATES)
        description = template.format(entity_name)
        
        # Determine due date - some overdue, some current, some future
        days_offset = random.choice([
            random.randint(-30, -1),  # Overdue (30%)
            random.randint(-30, -1),
            random.randint(-30, -1),
            random.randint(1, 30),    # Future (70%)
            random.randint(1, 30),
            random.randint(1, 30),
            random.randint(1, 30),
            random.randint(1, 30),
            random.randint(1, 30),
            random.randint(1, 30)
        ])
        
        due_date = date.today() + timedelta(days=days_offset)
        
        # Status based on due date
        if days_offset < -7:  # Very overdue tasks are more likely to be in progress
            status = random.choice(['todo', 'in-progress', 'in-progress'])
        elif days_offset < 0:  # Overdue tasks
            status = random.choice(['todo', 'in-progress'])
        else:  # Future tasks
            status = random.choice(['todo', 'todo', 'in-progress', 'complete'])
        
        task = Task(
            description=description,
            due_date=due_date,
            priority=random.choice(PRIORITIES),
            status=status,
            next_step_type=random.choice(NEXT_STEP_TYPES),
            entity_type=entity_type,
            entity_id=entity_id,
            created_at=datetime.now() - timedelta(days=random.randint(1, 60))
        )
        
        # Set completed_at for completed tasks
        if status == 'complete':
            task.completed_at = datetime.now() - timedelta(days=random.randint(1, 30))
        
        tasks.append(task)
        db.session.add(task)
    
    db.session.commit()
    print(f"Created {len(tasks)} tasks")
    return tasks

def create_notes(companies, contacts, opportunities, tasks):
    """Create sample notes"""
    notes = []
    entities = []
    
    # Collect all entities for note attachment
    for company in companies:
        entities.append(('company', company.id))
    for contact in contacts:
        entities.append(('contact', contact.id))
    for opportunity in opportunities:
        entities.append(('opportunity', opportunity.id))
    for task in tasks:
        entities.append(('task', task.id))
    
    note_templates = [
        "Initial contact made. Showed strong interest in our solution.",
        "Follow-up call completed. Discussed technical requirements in detail.",
        "Demo presentation went well. Client impressed with features.",
        "Budget discussion - within their range. Moving to next phase.",
        "Stakeholder meeting scheduled for next week.",
        "Competitor comparison requested. Preparing competitive analysis.",
        "Technical questions answered. Waiting for decision.",
        "Contract terms reviewed. Minor revisions requested.",
        "Project timeline approved. Ready to proceed.",
        "Internal meeting completed. All team members aligned."
    ]
    
    # Create 30 notes across various entities
    for i in range(30):
        entity_type, entity_id = random.choice(entities)
        
        note = Note(
            content=random.choice(note_templates),
            is_internal=random.choice([True, False]),
            entity_type=entity_type,
            entity_id=entity_id,
            created_at=datetime.now() - timedelta(days=random.randint(1, 30))
        )
        
        notes.append(note)
        db.session.add(note)
    
    db.session.commit()
    print(f"Created {len(notes)} notes")
    return notes

def seed_database():
    """Main seeding function"""
    print("Starting database seeding...")
    
    # Clear existing data
    print("Clearing existing data...")
    Note.query.delete()
    Task.query.delete()
    # Clear many-to-many relationships
    db.session.execute(db.text("DELETE FROM contact_opportunities"))
    Opportunity.query.delete()
    Contact.query.delete()
    Company.query.delete()
    db.session.commit()
    print("Existing data cleared")
    
    # Create new data
    companies = create_companies()
    contacts = create_contacts(companies)
    opportunities = create_opportunities(companies, contacts)
    tasks = create_tasks(companies, contacts, opportunities)
    notes = create_notes(companies, contacts, opportunities, tasks)
    
    print("\n=== SEEDING COMPLETE ===")
    print(f"Companies: {len(companies)}")
    print(f"Contacts: {len(contacts)}")
    print(f"Opportunities: {len(opportunities)}")
    print(f"Tasks: {len(tasks)}")
    print(f"Notes: {len(notes)}")
    print("\nYour CRM is now populated with realistic test data!")

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        seed_database()