"""
Entity management utilities for CRM
Provides reusable functions for entity relationships, stakeholder management, and teams
"""

from app.models import db, Company, Stakeholder, Opportunity, User, Task


class EntityManager:
    """Centralized entity management following DRY principles"""

    @staticmethod
    def get_all_entities_for_selection():
        """Get all entities formatted for form selection dropdowns"""
        companies = Company.query.order_by(Company.name).all()
        contacts = Stakeholder.query.order_by(Stakeholder.name).all()
        opportunities = Opportunity.query.order_by(Opportunity.name).all()

        return {
            "companies": [
                {"id": c.id, "name": c.name, "type": "company"} for c in companies
            ],
            "contacts": [
                {
                    "id": c.id,
                    "name": c.name,
                    "type": "contact",
                    "company_name": c.company.name if c.company else None,
                }
                for c in contacts
            ],
            "opportunities": [
                {
                    "id": o.id,
                    "name": o.name,
                    "type": "opportunity",
                    "company_name": o.company.name if o.company else None,
                }
                for o in opportunities
            ],
        }

    @staticmethod
    def get_entity_by_type_and_id(entity_type, entity_id):
        """Get entity object by type and ID - used across the application"""
        if entity_type == "company":
            return Company.query.get(entity_id)
        elif entity_type == "stakeholder":
            return Stakeholder.query.get(entity_id)
        elif entity_type == "opportunity":
            return Opportunity.query.get(entity_id)
        elif entity_type == "user":
            return User.query.get(entity_id)
        elif entity_type == "task":
            return Task.query.get(entity_id)
        return None

    @staticmethod
    def format_entity_for_display(entity_type, entity_id):
        """Format entity for consistent display across the app"""
        entity = EntityManager.get_entity_by_type_and_id(entity_type, entity_id)
        if not entity:
            return {"name": "Unknown", "type": entity_type, "id": entity_id}

        result = {"id": entity.id, "name": entity.name, "type": entity_type}

        # Add type-specific information
        if entity_type == "contact" and hasattr(entity, "company"):
            result["company_name"] = entity.company.name if entity.company else None
        elif entity_type == "opportunity" and hasattr(entity, "company"):
            result["company_name"] = entity.company.name if entity.company else None
            result["stage"] = getattr(entity, "stage", None)
            result["value"] = getattr(entity, "value", None)
        elif entity_type == "company" and hasattr(entity, "industry"):
            result["industry"] = entity.industry

        return result


class StakeholderManager:
    """Stakeholder management utilities following DRY principles"""

    STAKEHOLDER_ROLES = [
        ("stakeholder", "Stakeholder"),
        ("decision_maker", "Decision Maker"),
        ("influencer", "Influencer"),
        ("champion", "Champion"),
        ("gatekeeper", "Gatekeeper"),
        ("user", "End User"),
    ]

    @staticmethod
    def get_role_choices():
        """Get stakeholder role choices for forms"""
        return StakeholderManager.STAKEHOLDER_ROLES

    @staticmethod
    def assign_stakeholder(contact_id, opportunity_id, role, is_primary=False):
        """Assign a contact as stakeholder to an opportunity"""
        contact = Stakeholder.query.get(contact_id)
        if contact:
            contact.set_stakeholder_role(opportunity_id, role, is_primary)
            return True
        return False

    @staticmethod
    def get_opportunity_stakeholders(opportunity_id, include_contacts=True):
        """Get formatted stakeholders for an opportunity"""
        opportunity = Opportunity.query.get(opportunity_id)
        if not opportunity:
            return []

        stakeholders = opportunity.get_stakeholders()

        # Add additional contact information if requested
        if include_contacts:
            for stakeholder in stakeholders:
                stakeholder["display_name"] = (
                    f"{stakeholder['name']} ({stakeholder['stakeholder_role']})"
                )
                if stakeholder["is_primary"]:
                    stakeholder["display_name"] += " [Primary]"

        return stakeholders


class TeamManager:
    """Team management utilities following DRY principles"""

    TEAM_ROLES = [
        ("account_manager", "Account Manager"),
        ("sales_rep", "Sales Representative"),
        ("sales_engineer", "Sales Engineer"),
        ("solution_architect", "Solution Architect"),
        ("project_manager", "Project Manager"),
        ("support_rep", "Support Representative"),
        ("implementation_specialist", "Implementation Specialist"),
    ]

    ACCESS_LEVELS = [
        ("read", "Read Only"),
        ("write", "Read & Write"),
        ("admin", "Administrator"),
    ]

    @staticmethod
    def get_role_choices():
        """Get team role choices for forms"""
        return TeamManager.TEAM_ROLES

    @staticmethod
    def get_access_level_choices():
        """Get access level choices for forms"""
        return TeamManager.ACCESS_LEVELS

    @staticmethod
    def assign_company_team_member(
        company_id, user_id, role, is_primary=False, access_level="read"
    ):
        """Assign user to company team"""
        from app.models import CompanyTeam

        team_member = CompanyTeam(
            company_id=company_id,
            user_id=user_id,
            role=role,
            is_primary=is_primary,
            access_level=access_level,
        )
        db.session.add(team_member)
        db.session.commit()
        return team_member

    @staticmethod
    def assign_opportunity_team_member(
        opportunity_id, user_id, role, is_primary=False, access_level="read"
    ):
        """Assign user to opportunity team"""
        from app.models import OpportunityTeam

        team_member = OpportunityTeam(
            opportunity_id=opportunity_id,
            user_id=user_id,
            role=role,
            is_primary=is_primary,
            access_level=access_level,
        )
        db.session.add(team_member)
        db.session.commit()
        return team_member

    @staticmethod
    def get_opportunity_full_team(opportunity_id, include_company_team=True):
        """Get full team for opportunity with inheritance from company"""
        opportunity = Opportunity.query.get(opportunity_id)
        if not opportunity:
            return []

        return opportunity.get_full_team()


class TaskEntityManager:
    """Task entity linking utilities following DRY principles"""

    @staticmethod
    def link_task_to_entities(task_id, entities):
        """Link a task to multiple entities

        Args:
            task_id: The task ID
            entities: List of dicts with 'type' and 'id' keys
        """
        task = Task.query.get(task_id)
        if not task:
            return False

        # Validate entities exist
        validated_entities = []
        for entity in entities:
            entity_obj = EntityManager.get_entity_by_type_and_id(
                entity["type"], entity["id"]
            )
            if entity_obj:
                validated_entities.append(entity)

        if validated_entities:
            task.set_linked_entities(validated_entities)
            return True
        return False

    @staticmethod
    def get_tasks_for_entity(entity_type, entity_id, status_filter=None):
        """Get all tasks linked to a specific entity"""
        query = """
            SELECT DISTINCT t.id, t.description, t.status, t.priority, t.due_date, t.task_type
            FROM tasks t
            JOIN task_entities te ON t.id = te.task_id
            WHERE te.entity_type = :entity_type AND te.entity_id = :entity_id
        """
        params = {"entity_type": entity_type, "entity_id": entity_id}

        if status_filter:
            query += " AND t.status = :status"
            params["status"] = status_filter

        query += " ORDER BY t.due_date ASC, t.created_at DESC"

        results = db.session.execute(db.text(query), params).fetchall()
        return [
            {
                "id": row[0],
                "description": row[1],
                "status": row[2],
                "priority": row[3],
                "due_date": row[4].isoformat() if row[4] else None,
                "task_type": row[5],
            }
            for row in results
        ]


# Convenience functions for backward compatibility and ease of use
def get_entities_for_forms():
    """Convenience function for getting entities for form dropdowns"""
    return EntityManager.get_all_entities_for_selection()


def assign_stakeholder_role(contact_id, opportunity_id, role, is_primary=False):
    """Convenience function for assigning stakeholder roles"""
    return StakeholderManager.assign_stakeholder(
        contact_id, opportunity_id, role, is_primary
    )


def get_entity_tasks(entity_type, entity_id, status_filter=None):
    """Convenience function for getting entity tasks"""
    return TaskEntityManager.get_tasks_for_entity(entity_type, entity_id, status_filter)
