#!/usr/bin/env python3
"""
Fixed CRM Database Seeding Script
Creates tasks using new multi-entity linking system
"""

import random
from datetime import datetime, date, timedelta

from app.models import db, Company, Contact, Opportunity, Task, Note
from main import create_app


def create_sample_tasks_with_multi_entity_linking():
    """Create tasks using the new multi-entity linking system"""
    print("Creating sample tasks with multi-entity linking...")
    
    # Get existing entities
    companies = Company.query.all()
    contacts = Contact.query.all()  
    opportunities = Opportunity.query.all()
    
    if not companies or not contacts or not opportunities:
        print("❌ Missing base entities - run main seed script first")
        return
    
    # Sample task descriptions
    task_descriptions = [
        "Follow up on proposal submission",
        "Schedule demo meeting",
        "Prepare contract documents",
        "Send product information",
        "Review technical requirements",
        "Coordinate implementation timeline",
        "Update pricing proposal",
        "Conduct discovery call"
    ]
    
    # Create single tasks with multiple entity links
    for i in range(20):
        task = Task(
            description=random.choice(task_descriptions),
            due_date=date.today() + timedelta(days=random.randint(1, 30)),
            priority=random.choice(['low', 'medium', 'high']),
            status=random.choice(['todo', 'in-progress']),
            task_type='single'
        )
        
        db.session.add(task)
        db.session.flush()  # Get task ID
        
        # Link to random entities (1-3 entities per task)
        num_links = random.randint(1, 3)
        linked_entities = []
        
        # Always include at least one company
        company = random.choice(companies)
        linked_entities.append({'type': 'company', 'id': company.id})
        
        if num_links > 1:
            # Add opportunity or contact
            if random.choice([True, False]) and opportunities:
                opp = random.choice(opportunities)
                linked_entities.append({'type': 'opportunity', 'id': opp.id})
            else:
                contact = random.choice(contacts)
                linked_entities.append({'type': 'contact', 'id': contact.id})
        
        if num_links > 2:
            # Add another entity type
            contact = random.choice(contacts)
            linked_entities.append({'type': 'contact', 'id': contact.id})
        
        # Set linked entities
        task.set_linked_entities(linked_entities)
        
        print(f"✅ Created task: {task.description[:30]}... with {len(linked_entities)} entity links")
    
    db.session.commit()
    print(f"✅ Created 20 multi-entity linked tasks")


def main():
    """Main seeding function"""
    print("🌱 Starting fixed CRM data seeding")
    
    app = create_app()
    
    with app.app_context():
        create_sample_tasks_with_multi_entity_linking()
    
    print("🎉 Fixed seeding completed!")


if __name__ == "__main__":
    main()