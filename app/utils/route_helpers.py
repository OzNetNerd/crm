from flask import request, jsonify, redirect, url_for
from app.models import db
from app.utils.model_introspection import ModelIntrospector
from collections import defaultdict
from datetime import date


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
            return jsonify(
                {
                    "status": "success",
                    f"{self.model_class.__name__.lower()}_id": entity.id,
                }
            )
        else:
            return redirect(
                url_for(
                    f"{self.blueprint_name}.detail",
                    **{f"{self.model_class.__name__.lower()}_id": entity.id},
                )
            )

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
        if hasattr(entity, "to_dict"):
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
    from app.models import Company, Stakeholder, Opportunity

    return {
        "companies": [
            {"id": c.id, "name": c.name}
            for c in Company.query.order_by(Company.name).all()
        ],
        "contacts": [
            {"id": c.id, "name": c.name}
            for c in Stakeholder.query.order_by(Stakeholder.name).all()
        ],
        "opportunities": [
            {"id": o.id, "name": o.name}
            for o in Opportunity.query.order_by(Opportunity.name).all()
        ],
    }


class GenericAPIHandler:
    """Generic API handler to eliminate duplication in API endpoints"""

    def __init__(self, model_class, entity_name):
        self.model_class = model_class
        self.entity_name = entity_name  # e.g. 'task', 'contact', etc.

    def get_details(self, entity_id):
        """Generic get details handler with notes"""
        from app.models import Note

        try:
            entity = self.model_class.query.get_or_404(entity_id)
            notes = (
                Note.query.filter_by(entity_type=self.entity_name, entity_id=entity_id)
                .order_by(Note.created_at.desc())
                .all()
            )

            entity_data = (
                entity.to_dict() if hasattr(entity, "to_dict") else {"id": entity.id}
            )
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

    def create_entity(self, allowed_fields):
        """Generic create handler"""
        try:
            data = request.get_json()

            # Create entity with allowed fields
            entity_data = {}
            for field in allowed_fields:
                if field in data:
                    entity_data[field] = data[field]

            entity = self.model_class(**entity_data)
            db.session.add(entity)
            db.session.commit()

            # Return created entity
            if hasattr(entity, "to_dict"):
                return jsonify(entity.to_dict()), 201
            else:
                return jsonify({"status": "success", "id": entity.id}), 201

        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 400

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
            if hasattr(entity, "to_dict"):
                return jsonify(entity.to_dict())
            else:
                return jsonify({"status": "success"})

        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

    def delete_entity(self, entity_id):
        """Generic delete handler"""
        try:
            entity = self.model_class.query.get_or_404(entity_id)
            db.session.delete(entity)
            db.session.commit()

            return jsonify(
                {
                    "status": "success",
                    "message": f"{self.entity_name.title()} deleted successfully",
                }
            )

        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

    def get_list(self, field_serializer=None, order_by_field=None):
        """Generic list handler for dropdown/selection endpoints"""
        try:
            query = self.model_class.query
            if order_by_field:
                order_attr = getattr(self.model_class, order_by_field)
                query = query.order_by(order_attr)
            
            entities = query.all()
            
            if field_serializer and callable(field_serializer):
                return jsonify([field_serializer(entity) for entity in entities])
            else:
                # Default serialization - try to_dict() or basic fields
                if hasattr(entities[0] if entities else self.model_class(), "to_dict"):
                    return jsonify([entity.to_dict() for entity in entities])
                else:
                    return jsonify([{"id": entity.id, "name": getattr(entity, "name", str(entity))} for entity in entities])

        except Exception as e:
            return jsonify({"error": str(e)}), 500


class NotesAPIHandler:
    """Generic handler for notes endpoints to eliminate duplication"""

    def __init__(self, entity_model, entity_name):
        self.entity_model = entity_model
        self.entity_name = entity_name  # e.g. 'company', 'contact', 'opportunity'

    def get_notes(self, entity_id):
        """Get all notes for a specific entity"""
        from app.models import Note
        from app.utils.model_helpers import auto_serialize

        try:
            # Verify entity exists
            self.entity_model.query.get_or_404(entity_id)

            notes = (
                Note.query.filter_by(entity_type=self.entity_name, entity_id=entity_id)
                .order_by(Note.created_at.desc())
                .all()
            )

            return jsonify([
                auto_serialize(note, include_properties=['entity_name'])
                for note in notes
            ])

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    def create_note(self, entity_id):
        """Create a new note for a specific entity"""
        from app.models import Note
        from app.utils.model_helpers import auto_serialize

        try:
            # Verify entity exists
            self.entity_model.query.get_or_404(entity_id)

            data = request.get_json()
            if not data or not data.get("content"):
                return jsonify({"error": "Note content is required"}), 400

            note = Note(
                content=data["content"],
                entity_type=self.entity_name,
                entity_id=entity_id,
                is_internal=data.get("is_internal", True),
            )

            db.session.add(note)
            db.session.commit()

            return jsonify(
                auto_serialize(note, include_properties=['entity_name'])
            ), 201

        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500


class EntityFilterManager:
    """Universal filtering and sorting handler for all entities"""
    
    def __init__(self, model_class, entity_name):
        self.model_class = model_class
        self.entity_name = entity_name
        
    def get_filtered_context(self, custom_filters=None, custom_sorting=None, custom_grouper=None, joins=None):
        """Generic filtered context builder"""
        # Get filter parameters
        group_by = request.args.get("group_by", "default")
        sort_by = request.args.get("sort_by", "name")
        sort_direction = request.args.get("sort_direction", "asc")
        
        # Parse filter arrays
        primary_filter = self._parse_filter_param("primary_filter")
        secondary_filter = self._parse_filter_param("secondary_filter")
        entity_filter = self._parse_filter_param("entity_filter")
        
        # Additional filters
        show_completed = request.args.get("show_completed", "false").lower() == "true"
        priority_filter = self._parse_filter_param("priority_filter")
        
        # Start with base query
        query = self.model_class.query
        
        # Apply joins if provided
        if joins:
            for join_model in joins:
                query = query.join(join_model)
        
        # Apply custom filters
        if custom_filters:
            query = custom_filters(query, {
                'primary_filter': primary_filter,
                'secondary_filter': secondary_filter,
                'entity_filter': entity_filter,
                'show_completed': show_completed,
                'priority_filter': priority_filter
            })
        
        # Apply custom sorting or default sorting
        if custom_sorting:
            query = custom_sorting(query, sort_by, sort_direction)
        else:
            query = self._apply_default_sorting(query, sort_by, sort_direction)
        
        filtered_entities = query.all()
        
        # Group entities
        grouper = EntityGrouper(self.model_class, self.entity_name)
        grouped_entities = grouper.group_by_field(filtered_entities, group_by, custom_grouper)
        
        return {
            f"grouped_{self.entity_name}s": grouped_entities,
            "grouped_entities": grouped_entities,  # Universal key
            "group_by": group_by,
            "total_count": len(filtered_entities),
            "sort_by": sort_by,
            "sort_direction": sort_direction,
            "primary_filter": primary_filter,
            "secondary_filter": secondary_filter,
            "entity_filter": entity_filter,
            "show_completed": show_completed,
            "priority_filter": priority_filter,
            "today": date.today(),
        }
    
    def _parse_filter_param(self, param_name):
        """Parse comma-separated filter parameters"""
        param_value = request.args.get(param_name)
        if not param_value:
            return []
        return [p.strip() for p in param_value.split(",") if p.strip()]
    
    def _apply_default_sorting(self, query, sort_by, sort_direction):
        """Apply default sorting logic"""
        # Try to get the sort field from the model
        if hasattr(self.model_class, sort_by):
            sort_field = getattr(self.model_class, sort_by)
            if sort_direction == "desc":
                return query.order_by(sort_field.desc())
            else:
                return query.order_by(sort_field.asc())
        
        # Fallback to name or id
        if hasattr(self.model_class, 'name'):
            return query.order_by(self.model_class.name.asc())
        else:
            return query.order_by(self.model_class.id.asc())
    
    def get_content_context(self, custom_filters=None, custom_sorting=None, custom_grouper=None, joins=None):
        """Get context for /content HTMX endpoints"""
        context = self.get_filtered_context(custom_filters, custom_sorting, custom_grouper, joins)
        
        # Add universal template configuration
        # Plural mapping for proper English (only irregular plurals)
        plural_map = {
            'opportunity': 'opportunities',
            'company': 'companies', 
            'category': 'categories',
            'activity': 'activities',
            'entity': 'entities',
            'priority': 'priorities',
            'industry': 'industries'
        }
        
        entity_plural = plural_map.get(self.entity_name, f"{self.entity_name}s")
        
        context.update({
            'entity_type': self.entity_name,
            'entity_name_singular': self.entity_name,
            'entity_name_plural': entity_plural,
            'card_config': ModelIntrospector.get_card_config(self.model_class),
            'model_class': self.model_class
        })
        
        return context


class EntityGrouper:
    """Universal grouping handler for all entities"""
    
    def __init__(self, model_class, entity_name):
        self.model_class = model_class
        self.entity_name = entity_name
        
        # Plural mapping for proper English (only irregular plurals)
        self.plural_map = {
            'opportunity': 'opportunities',
            'company': 'companies', 
            'category': 'categories',
            'activity': 'activities',
            'entity': 'entities',
            'priority': 'priorities',
            'industry': 'industries'
        }
    
    def group_by_field(self, entities, group_by, custom_grouper=None):
        """Group entities by specified field with support for custom grouper function"""
        
        # Use custom grouper if provided
        if custom_grouper:
            result = custom_grouper(entities, group_by)
            if result is not None:
                return result
        
        # Default grouping logic
        grouped = defaultdict(list)
        
        # Generic field-based grouping
        if hasattr(self.model_class, group_by):
            for entity in entities:
                field_value = getattr(entity, group_by, None)
                key = str(field_value) if field_value is not None else "Other"
                grouped[key].append(entity)
            
            # Return sorted groups
            result = []
            for key in sorted(grouped.keys()):
                if grouped[key]:
                    result.append({
                        "key": key,
                        "label": key.replace("_", " ").replace("-", " ").title(),
                        "entities": grouped[key],
                        "count": len(grouped[key])
                    })
            return result
        
        # Fallback: return all entities in one group
        return [{
            "key": "all",
            "label": f"All {self.plural_map.get(self.entity_name, f'{self.entity_name}s').title()}",
            "entities": entities,
            "count": len(entities)
        }]
