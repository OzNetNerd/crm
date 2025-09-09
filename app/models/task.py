from datetime import datetime
from . import db

# Many-to-many relationship tables for tasks and entities
task_companies = db.Table(
    "task_companies",
    db.Column("task_id", db.Integer, db.ForeignKey("tasks.id"), primary_key=True),
    db.Column("company_id", db.Integer, db.ForeignKey("companies.id"), primary_key=True),
)

task_contacts = db.Table(
    "task_contacts", 
    db.Column("task_id", db.Integer, db.ForeignKey("tasks.id"), primary_key=True),
    db.Column("contact_id", db.Integer, db.ForeignKey("contacts.id"), primary_key=True),
)

task_opportunities = db.Table(
    "task_opportunities",
    db.Column("task_id", db.Integer, db.ForeignKey("tasks.id"), primary_key=True), 
    db.Column("opportunity_id", db.Integer, db.ForeignKey("opportunities.id"), primary_key=True),
)


class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text, nullable=False)
    due_date = db.Column(db.Date)
    priority = db.Column(db.String(10), default="medium")  # high/medium/low
    status = db.Column(db.String(20), default="todo")  # todo/in-progress/complete
    next_step_type = db.Column(db.String(20))  # meeting/demo/call/email
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)

    # Polymorphic relationship - can link to any entity
    entity_type = db.Column(db.String(50))  # 'company', 'contact', 'opportunity'
    entity_id = db.Column(db.Integer)

    # Multi Task support
    task_type = db.Column(
        db.String(20), default="single"
    )  # 'single', 'parent', 'child'
    parent_task_id = db.Column(db.Integer, db.ForeignKey("tasks.id"))
    sequence_order = db.Column(db.Integer, default=0)  # For ordering child tasks
    dependency_type = db.Column(
        db.String(20), default="parallel"
    )  # 'sequential', 'parallel'

    @property
    def is_overdue(self):
        if not self.due_date or self.status == "complete":
            return False
        return self.due_date < datetime.utcnow().date()

    @property
    def entity_name(self):
        if not self.entity_type or not self.entity_id:
            return None

        if self.entity_type == "company":
            from .company import Company

            entity = Company.query.get(self.entity_id)
        elif self.entity_type == "contact":
            from .contact import Contact

            entity = Contact.query.get(self.entity_id)
        elif self.entity_type == "opportunity":
            from .opportunity import Opportunity

            entity = Opportunity.query.get(self.entity_id)
        else:
            return None

        return entity.name if entity else None

    # Parent-child task relationships
    parent_task = db.relationship(
        "Task", remote_side="Task.id", back_populates="child_tasks"
    )
    child_tasks = db.relationship(
        "Task",
        back_populates="parent_task",
        order_by="Task.sequence_order",
        lazy="select",
    )

    # Many-to-many relationships with entities
    related_companies = db.relationship(
        "Company",
        secondary=task_companies,
        lazy="subquery",
        backref=db.backref("related_tasks", lazy=True),
    )
    related_contacts = db.relationship(
        "Contact", 
        secondary=task_contacts,
        lazy="subquery",
        backref=db.backref("related_tasks", lazy=True),
    )
    related_opportunities = db.relationship(
        "Opportunity",
        secondary=task_opportunities, 
        lazy="subquery",
        backref=db.backref("related_tasks", lazy=True),
    )

    @property
    def opportunity_value(self):
        if self.entity_type == "opportunity" and self.entity_id:
            from .opportunity import Opportunity

            opportunity = Opportunity.query.get(self.entity_id)
            return opportunity.value if opportunity else None
        return None

    @property
    def company_name(self):
        """Get company name regardless of entity type"""
        if self.entity_type == "company" and self.entity_id:
            from .company import Company

            company = Company.query.get(self.entity_id)
            return company.name if company else None
        elif self.entity_type == "contact" and self.entity_id:
            from .contact import Contact

            contact = Contact.query.get(self.entity_id)
            return contact.company.name if contact and contact.company else None
        elif self.entity_type == "opportunity" and self.entity_id:
            from .opportunity import Opportunity

            opportunity = Opportunity.query.get(self.entity_id)
            return (
                opportunity.company.name
                if opportunity and opportunity.company
                else None
            )
        return None

    @property
    def all_company_names(self):
        """Get all related company names including primary and related"""
        names = []
        
        # Add primary company name
        primary_name = self.company_name
        if primary_name:
            names.append(primary_name)
            
        # Add related companies
        for company in self.related_companies:
            if company.name not in names:
                names.append(company.name)
                
        # Add companies from related contacts
        for contact in self.related_contacts:
            if contact.company and contact.company.name not in names:
                names.append(contact.company.name)
                
        # Add companies from related opportunities  
        for opportunity in self.related_opportunities:
            if opportunity.company and opportunity.company.name not in names:
                names.append(opportunity.company.name)
                
        return names

    @property
    def all_opportunity_names(self):
        """Get all related opportunity names including primary and related"""
        names = []
        
        # Add primary opportunity name
        primary_name = self.opportunity_name
        if primary_name:
            names.append(primary_name)
            
        # Add related opportunities
        for opportunity in self.related_opportunities:
            if opportunity.name not in names:
                names.append(opportunity.name)
                
        # Add opportunities from related contacts
        for contact in self.related_contacts:
            for opportunity in contact.opportunities:
                if opportunity.name not in names:
                    names.append(opportunity.name)
                    
        return names

    @property
    def all_contact_names(self):
        """Get all related contact names"""
        names = []
        
        # Add primary contact name if entity is contact
        if self.entity_type == "contact" and self.entity_id:
            from .contact import Contact
            contact = Contact.query.get(self.entity_id)
            if contact:
                names.append(contact.name)
        
        # Add related contacts
        for contact in self.related_contacts:
            if contact.name not in names:
                names.append(contact.name)
                
        # Add contacts from related opportunities
        for opportunity in self.related_opportunities:
            for contact in opportunity.contacts:
                if contact.name not in names:
                    names.append(contact.name)
                    
        return names

    @property
    def opportunity_name(self):
        """Get opportunity name if task is linked to an opportunity or contact with opportunities"""
        if self.entity_type == "opportunity" and self.entity_id:
            from .opportunity import Opportunity

            opportunity = Opportunity.query.get(self.entity_id)
            return opportunity.name if opportunity else None
        return None

    @property
    def opportunity_stage(self):
        """Get opportunity stage if task is linked to an opportunity"""
        if self.entity_type == "opportunity" and self.entity_id:
            from .opportunity import Opportunity

            opportunity = Opportunity.query.get(self.entity_id)
            return opportunity.stage if opportunity else None
        return None

    @property
    def stakeholder_opportunity_name(self):
        """Get primary opportunity name for contact tasks (first opportunity if multiple)"""
        if self.entity_type == "contact" and self.entity_id:
            from .contact import Contact

            contact = Contact.query.get(self.entity_id)
            if contact and contact.opportunities:
                # Return the first (primary) opportunity name
                return contact.opportunities[0].name
        elif self.entity_type == "opportunity" and self.entity_id:
            return self.opportunity_name
        return None

    @property
    def stakeholder_opportunity_value(self):
        """Get primary opportunity value for contact tasks (first opportunity if multiple)"""
        if self.entity_type == "contact" and self.entity_id:
            from .contact import Contact

            contact = Contact.query.get(self.entity_id)
            if contact and contact.opportunities:
                # Return the first (primary) opportunity value
                return contact.opportunities[0].value
        elif self.entity_type == "opportunity" and self.entity_id:
            return self.opportunity_value
        return None

    @property
    def task_type_badge(self):
        """Get appropriate badge text for task type"""
        if self.task_type == "parent":
            return "Parent"
        elif self.task_type == "child":
            return "Child"
        return "Single"

    @property
    def can_start(self):
        """Check if task can be started based on dependencies"""
        if self.task_type != "child" or self.dependency_type != "sequential":
            return True

        # For sequential child tasks, check if previous tasks are complete
        if not self.parent_task:
            return True

        # Get all child tasks with lower sequence_order
        previous_tasks = Task.query.filter(
            Task.parent_task_id == self.parent_task_id,
            Task.sequence_order < self.sequence_order,
        ).all()

        # All previous tasks must be complete
        return all(task.status == "complete" for task in previous_tasks)

    @property
    def completion_percentage(self):
        """For parent tasks, calculate completion percentage based on child tasks"""
        if self.task_type != "parent":
            return 100 if self.status == "complete" else 0

        # Force fresh query to avoid stale relationship data
        child_tasks = Task.query.filter(Task.parent_task_id == self.id).all()
        
        if not child_tasks:
            return 0

        completed_count = sum(
            1 for child in child_tasks if child.status == "complete"
        )
        return int((completed_count / len(child_tasks)) * 100)

    @property
    def next_available_child(self):
        """For parent tasks, get the next child that can be started"""
        if self.task_type != "parent":
            return None

        for child in self.child_tasks:
            if child.status != "complete" and child.can_start:
                return child
        return None

    def to_dict(self):
        """Convert task to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'description': self.description,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'priority': self.priority,
            'status': self.status,
            'next_step_type': self.next_step_type,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'entity_name': self.entity_name,
            'task_type': self.task_type,
            'parent_task_id': self.parent_task_id,
            'sequence_order': self.sequence_order,
            'dependency_type': self.dependency_type,
            'is_overdue': self.is_overdue,
            'opportunity_value': self.opportunity_value,
            'company_name': self.company_name,
            'opportunity_name': self.opportunity_name,
            'opportunity_stage': self.opportunity_stage,
            'stakeholder_opportunity_name': self.stakeholder_opportunity_name,
            'stakeholder_opportunity_value': self.stakeholder_opportunity_value,
            'task_type_badge': self.task_type_badge,
            'can_start': self.can_start,
            'completion_percentage': self.completion_percentage,
            # New multi-entity properties
            'all_company_names': self.all_company_names,
            'all_opportunity_names': self.all_opportunity_names,
            'all_contact_names': self.all_contact_names,
            'related_companies': [{'id': c.id, 'name': c.name} for c in self.related_companies],
            'related_contacts': [{'id': c.id, 'name': c.name} for c in self.related_contacts], 
            'related_opportunities': [{'id': o.id, 'name': o.name} for o in self.related_opportunities],
        }

    def __repr__(self):
        return f"<Task {self.task_type}: {self.description[:50]}>"
