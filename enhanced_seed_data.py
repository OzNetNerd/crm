#!/usr/bin/env python3
"""
Enhanced CRM Database Seeding Script - Clean Single Source of Truth Architecture
Creates realistic data with proper stakeholder MEDDPICC roles and account team assignments
"""

import random
from datetime import datetime, date, timedelta

from app.models import (
    db, Company, Stakeholder, Opportunity, Task, Note, User,
    CompanyAccountTeam, OpportunityAccountTeam
)
from main import create_app


def get_meddpicc_roles():
    """Get available MEDDPICC role definitions"""
    return [
        'decision_maker', 'economic_buyer', 'influencer', 
        'champion', 'gatekeeper', 'user', 'technical_buyer'
    ]


def create_users():
    """Create account team members with realistic job titles"""
    print("Creating account team members...")
    
    users_data = [
        {'name': 'Sarah Johnson', 'email': 'sarah.johnson@company.com', 'job_title': 'Account Manager'},
        {'name': 'Michael Chen', 'email': 'michael.chen@company.com', 'job_title': 'Sales Representative'},
        {'name': 'Emily Rodriguez', 'email': 'emily.rodriguez@company.com', 'job_title': 'Solutions Engineer'},
        {'name': 'David Thompson', 'email': 'david.thompson@company.com', 'job_title': 'Technical Architect'},
        {'name': 'Lisa Wang', 'email': 'lisa.wang@company.com', 'job_title': 'Customer Success Manager'},
        {'name': 'Robert Martinez', 'email': 'robert.martinez@company.com', 'job_title': 'Sales Engineer'},
        {'name': 'Jennifer Brown', 'email': 'jennifer.brown@company.com', 'job_title': 'Account Executive'},
        {'name': 'Christopher Lee', 'email': 'christopher.lee@company.com', 'job_title': 'Implementation Specialist'},
        {'name': 'Amanda Davis', 'email': 'amanda.davis@company.com', 'job_title': 'Support Manager'},
        {'name': 'Mark Wilson', 'email': 'mark.wilson@company.com', 'job_title': 'Business Development Rep'}
    ]
    
    users = []
    for user_data in users_data:
        user = User(**user_data)
        db.session.add(user)
        users.append(user)
    
    db.session.commit()
    print(f"✅ Created {len(users)} account team members")
    return users


def create_companies():
    """Create sample companies"""
    print("Creating sample companies...")
    
    company_data = [
        {'name': 'GreenEnergy Solutions', 'industry': 'Technology', 'website': 'https://greenenergy.com'},
        {'name': 'Quantum Analytics', 'industry': 'Technology', 'website': 'https://quantum-analytics.com'},
        {'name': 'MedCore Systems', 'industry': 'Healthcare', 'website': 'https://medcore.com'},
        {'name': 'FinTech Innovators', 'industry': 'Finance', 'website': 'https://fintech-innovators.com'},
        {'name': 'ProManufacturing Co', 'industry': 'Manufacturing', 'website': 'https://promanufacturing.com'},
        {'name': 'RetailMax Group', 'industry': 'Retail', 'website': 'https://retailmax.com'},
        {'name': 'EduTech Solutions', 'industry': 'Education', 'website': 'https://edutech-solutions.com'},
        {'name': 'BuildRight Construction', 'industry': 'Construction', 'website': 'https://buildright.com'},
        {'name': 'Prime Properties LLC', 'industry': 'Real Estate', 'website': 'https://prime-properties.com'},
        {'name': 'Strategic Consulting Partners', 'industry': 'Consulting', 'website': 'https://strategic-consulting.com'}
    ]
    
    companies = []
    for data in company_data:
        company = Company(**data)
        db.session.add(company)
        companies.append(company)
    
    db.session.commit()
    print(f"✅ Created {len(companies)} companies")
    return companies


def create_stakeholders_with_meddpicc(companies):
    """Create stakeholders with job titles and MEDDPICC roles"""
    print("Creating stakeholders with MEDDPICC roles...")
    
    stakeholder_templates = [
        {'name': 'Nathan Hayes', 'job_title': 'Chief Technology Officer', 'email': 'n.hayes@{domain}'},
        {'name': 'Rachel Kim', 'job_title': 'VP of Operations', 'email': 'r.kim@{domain}'},
        {'name': 'James Wilson', 'job_title': 'Director of IT', 'email': 'j.wilson@{domain}'},
        {'name': 'Maria Gonzalez', 'job_title': 'Chief Financial Officer', 'email': 'm.gonzalez@{domain}'},
        {'name': 'Kevin O\'Connor', 'job_title': 'Head of Procurement', 'email': 'k.oconnor@{domain}'},
        {'name': 'Nicole Smith', 'job_title': 'Senior Manager', 'email': 'n.smith@{domain}'},
        {'name': 'Ryan Murphy', 'job_title': 'Technical Lead', 'email': 'r.murphy@{domain}'},
        {'name': 'Alex Cooper', 'job_title': 'VP of Engineering', 'email': 'a.cooper@{domain}'},
        {'name': 'Diana Foster', 'job_title': 'Operations Manager', 'email': 'd.foster@{domain}'},
        {'name': 'Tom Bradley', 'job_title': 'IT Manager', 'email': 't.bradley@{domain}'}
    ]
    
    # MEDDPICC role mappings based on job titles
    job_title_meddpicc_mapping = {
        'Chief Technology Officer': ['decision_maker', 'technical_buyer'],
        'VP of Operations': ['decision_maker', 'influencer'],
        'Director of IT': ['technical_buyer', 'influencer'],
        'Chief Financial Officer': ['economic_buyer', 'decision_maker'],
        'Head of Procurement': ['gatekeeper', 'influencer'],
        'Senior Manager': ['influencer', 'user'],
        'Technical Lead': ['technical_buyer', 'user'],
        'VP of Engineering': ['decision_maker', 'technical_buyer'],
        'Operations Manager': ['user', 'influencer'],
        'IT Manager': ['technical_buyer', 'gatekeeper']
    }
    
    stakeholders = []
    for i, company in enumerate(companies):
        # Create 2-3 stakeholders per company
        num_stakeholders = random.randint(2, 3)
        company_stakeholders = random.sample(stakeholder_templates, num_stakeholders)
        
        domain = company.website.replace('https://', '').replace('http://', '') if company.website else f"{company.name.lower().replace(' ', '')}.com"
        
        for template in company_stakeholders:
            stakeholder = Stakeholder(
                name=template['name'],
                job_title=template['job_title'],
                email=template['email'].format(domain=domain),
                phone=f"+1 (555) {random.randint(100,999)}-{random.randint(1000,9999)}",
                company_id=company.id
            )
            db.session.add(stakeholder)
            db.session.flush()  # Get stakeholder ID
            
            # Assign MEDDPICC roles based on job title
            meddpicc_roles = job_title_meddpicc_mapping.get(template['job_title'], ['user'])
            for role in meddpicc_roles:
                stakeholder.add_meddpicc_role(role)
            
            stakeholders.append(stakeholder)
            print(f"  ✅ Created {stakeholder.name} ({stakeholder.job_title}) with roles: {', '.join(meddpicc_roles)}")
    
    db.session.commit()
    print(f"✅ Created {len(stakeholders)} stakeholders with MEDDPICC roles")
    return stakeholders


def assign_account_teams(users, companies):
    """Assign account team members to companies"""
    print("Assigning account team members to companies...")
    
    assignments_count = 0
    for company in companies:
        # Assign 2-4 team members per company
        num_assignments = random.randint(2, 4)
        assigned_users = random.sample(users, num_assignments)
        
        for user in assigned_users:
            assignment = CompanyAccountTeam(
                user_id=user.id,
                company_id=company.id
            )
            db.session.add(assignment)
            assignments_count += 1
            print(f"  ✅ Assigned {user.name} ({user.job_title}) to {company.name}")
    
    db.session.commit()
    print(f"✅ Created {assignments_count} account team assignments")


def create_opportunities_with_stakeholders(companies, stakeholders):
    """Create opportunities and assign stakeholders"""
    print("Creating opportunities with stakeholder assignments...")
    
    opportunity_templates = [
        'System Integration Project', 'Cloud Migration Initiative', 'Digital Transformation',
        'Security Upgrade Program', 'Analytics Platform Implementation', 'Process Automation',
        'Infrastructure Modernization', 'Software License Renewal', 'Custom Development Project',
        'Consulting Services Engagement'
    ]
    
    stages = ['prospect', 'qualified', 'proposal', 'negotiation', 'closed']
    
    opportunities = []
    for company in companies:
        # Create 1-2 opportunities per company
        num_opps = random.randint(1, 2)
        
        for i in range(num_opps):
            opportunity = Opportunity(
                name=f"{random.choice(opportunity_templates)} - {company.name}",
                company_id=company.id,
                value=random.randint(10000, 300000),
                probability=random.randint(10, 90),
                stage=random.choice(stages),
                expected_close_date=date.today() + timedelta(days=random.randint(30, 180))
            )
            db.session.add(opportunity)
            db.session.flush()  # Get opportunity ID
            
            # Assign stakeholders from this company to the opportunity
            company_stakeholders = [s for s in stakeholders if s.company_id == company.id]
            num_stakeholder_assignments = random.randint(1, len(company_stakeholders))
            assigned_stakeholders = random.sample(company_stakeholders, num_stakeholder_assignments)
            
            for stakeholder in assigned_stakeholders:
                db.session.execute(
                    db.text("""
                        INSERT INTO stakeholder_opportunities (stakeholder_id, opportunity_id, created_at)
                        VALUES (:stakeholder_id, :opportunity_id, :created_at)
                    """),
                    {
                        "stakeholder_id": stakeholder.id,
                        "opportunity_id": opportunity.id,
                        "created_at": datetime.utcnow()
                    }
                )
            
            opportunities.append(opportunity)
            print(f"  ✅ Created {opportunity.name} with {len(assigned_stakeholders)} stakeholders")
    
    db.session.commit()
    print(f"✅ Created {len(opportunities)} opportunities with stakeholder assignments")
    return opportunities


def assign_relationship_owners(users, stakeholders):
    """Assign relationship owners to stakeholders"""
    print("Assigning relationship owners to stakeholders...")
    
    assignments_count = 0
    for stakeholder in stakeholders:
        # Each stakeholder has 1-2 relationship owners
        num_owners = random.randint(1, 2)
        owners = random.sample(users, num_owners)
        
        for owner in owners:
            stakeholder.assign_relationship_owner(owner.id)
            assignments_count += 1
            print(f"  ✅ {owner.name} owns relationship with {stakeholder.name}")
    
    print(f"✅ Created {assignments_count} relationship ownership assignments")


def create_sample_tasks(companies, opportunities, stakeholders, users):
    """Create sample tasks with multi-entity linking"""
    print("Creating sample tasks with multi-entity linking...")
    
    task_descriptions = [
        "Follow up on proposal submission",
        "Schedule demo meeting", 
        "Prepare contract documents",
        "Send product information",
        "Review technical requirements",
        "Coordinate implementation timeline",
        "Update pricing proposal",
        "Conduct discovery call",
        "Analyze stakeholder requirements",
        "Prepare executive presentation"
    ]
    
    tasks = []
    for i in range(25):
        task = Task(
            description=random.choice(task_descriptions),
            due_date=date.today() + timedelta(days=random.randint(1, 30)),
            priority=random.choice(['low', 'medium', 'high']),
            status=random.choice(['todo', 'in-progress', 'complete']),
            task_type='single'
        )
        db.session.add(task)
        db.session.flush()  # Get task ID
        
        # Link task to random entities (1-3 per task)
        entity_types = [
            ('company', random.choice(companies).id),
            ('opportunity', random.choice(opportunities).id),
            ('stakeholder', random.choice(stakeholders).id),
            ('user', random.choice(users).id)
        ]
        
        num_links = random.randint(1, 3)
        selected_entities = random.sample(entity_types, num_links)
        
        linked_entities = []
        for entity_type, entity_id in selected_entities:
            linked_entities.append({'type': entity_type, 'id': entity_id})
        
        task.set_linked_entities(linked_entities)
        tasks.append(task)
    
    print(f"✅ Created {len(tasks)} tasks with multi-entity linking")
    return tasks


def main():
    """Main seeding function"""
    print("🌱 Starting enhanced CRM data seeding with single source of truth architecture")
    
    app = create_app()
    
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Seed data in proper order
        users = create_users()
        companies = create_companies()
        stakeholders = create_stakeholders_with_meddpicc(companies)
        
        assign_account_teams(users, companies)
        opportunities = create_opportunities_with_stakeholders(companies, stakeholders)
        assign_relationship_owners(users, stakeholders)
        
        create_sample_tasks(companies, opportunities, stakeholders, users)
    
    print("\n🎉 Enhanced seeding completed successfully!")
    print(f"📊 Summary:")
    print(f"   - {len(companies)} companies")
    print(f"   - {len(users)} account team members")
    print(f"   - {len(stakeholders)} stakeholders with MEDDPICC roles")
    print(f"   - {len(opportunities)} opportunities")
    print(f"   - Account team assignments with inheritance")
    print(f"   - Stakeholder relationship ownership mapping")
    print(f"   - Multi-entity task linking")


if __name__ == "__main__":
    main()