from flask import request, jsonify, redirect, url_for
from crm.models import db


class BaseRouteHandler:
    """Generic route handler to eliminate duplication across entity routes"""
    
    def __init__(self, model_class, blueprint_name):
        self.model_class = model_class
        self.blueprint_name = blueprint_name
    
    def handle_create(self, **creation_kwargs):
        """Generic create handler for entities"""
        data = request.get_json() if request.is_json else request.form
        
        # Create entity with provided kwargs (allows custom field mapping)
        entity_data = {}
        for key, value in creation_kwargs.items():
            if callable(value):
                # If value is a function, call it with data
                result = value(data)
                # Handle validation errors returned as tuples (jsonify response, status_code)
                if isinstance(result, tuple):
                    return result
                entity_data[key] = result
            else:
                # If value is a string, use it as the field name from data
                entity_data[key] = data.get(value)
        
        # Create the entity
        entity = self.model_class(**entity_data)
        
        db.session.add(entity)
        db.session.commit()
        
        if request.is_json:
            return jsonify({"status": "success", f"{self.model_class.__name__.lower()}_id": entity.id})
        else:
            return redirect(url_for(f"{self.blueprint_name}.detail", **{f"{self.model_class.__name__.lower()}_id": entity.id}))
    
    def handle_update(self, entity_id, allowed_fields):
        """Generic update handler for entities"""
        entity = self.model_class.query.get_or_404(entity_id)
        data = request.get_json()
        
        # Update allowed fields
        for field in allowed_fields:
            if field in data:
                setattr(entity, field, data[field])
        
        db.session.commit()
        
        # Use to_dict() if available, otherwise return basic response
        if hasattr(entity, 'to_dict'):
            return jsonify(entity.to_dict())
        else:
            return jsonify({"status": "success"})


def parse_date_field(data, field_name):
    """Helper to parse date fields consistently"""
    from datetime import datetime
    
    date_value = data.get(field_name)
    if not date_value or date_value == "":
        return None
    elif isinstance(date_value, str):
        try:
            return datetime.strptime(date_value, "%Y-%m-%d").date()
        except (ValueError, TypeError):
            return None
    return date_value


def parse_int_field(data, field_name, default=None):
    """Helper to parse integer fields consistently"""
    value = data.get(field_name, default)
    if value is None:
        return default
    if isinstance(value, str):
        try:
            return int(value)
        except (ValueError, TypeError):
            return default
    return value


def get_entity_data_for_forms():
    """Get entity data commonly needed for forms"""
    from crm.models import Company, Contact, Opportunity
    
    return {
        'companies': [{"id": c.id, "name": c.name} for c in Company.query.order_by(Company.name).all()],
        'contacts': [{"id": c.id, "name": c.name} for c in Contact.query.order_by(Contact.name).all()],
        'opportunities': [{"id": o.id, "name": o.name} for o in Opportunity.query.order_by(Opportunity.name).all()]
    }


class GenericAPIHandler:
    """Generic API handler to eliminate duplication in API endpoints"""
    
    def __init__(self, model_class, entity_name):
        self.model_class = model_class
        self.entity_name = entity_name  # e.g. 'task', 'contact', etc.
    
    def get_details(self, entity_id):
        """Generic get details handler with notes"""
        from crm.models import Note
        
        try:
            entity = self.model_class.query.get_or_404(entity_id)
            notes = (
                Note.query.filter_by(entity_type=self.entity_name, entity_id=entity_id)
                .order_by(Note.created_at.desc())
                .all()
            )

            entity_data = entity.to_dict() if hasattr(entity, 'to_dict') else {"id": entity.id}
            entity_data["notes"] = [
                {
                    "id": note.id,
                    "content": note.content,
                    "is_internal": note.is_internal,
                    "created_at": note.created_at.isoformat(),
                }
                for note in notes
            ]
            return jsonify(entity_data)

        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    def update_entity(self, entity_id, allowed_fields):
        """Generic update handler"""
        try:
            entity = self.model_class.query.get_or_404(entity_id)
            data = request.get_json()

            # Update allowed fields
            for field in allowed_fields:
                if field in data:
                    setattr(entity, field, data[field])

            db.session.commit()

            # Use to_dict() if available, otherwise return basic response
            if hasattr(entity, 'to_dict'):
                return jsonify(entity.to_dict())
            else:
                return jsonify({"status": "success"})

        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500