from flask import request, jsonify, redirect, url_for
from app.models import db
from .model_introspection import ModelIntrospector
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
        """Generic create handler with duplicate checking"""
        try:
            data = request.get_json()

            # Check for duplicates before creating
            duplicate_error = self._check_duplicates(data)
            if duplicate_error:
                return duplicate_error

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

    def create_entity_from_data(self, data, allowed_fields):
        """Generic create handler for form data with duplicate checking"""
        try:
            # Check for duplicates before creating
            duplicate_error = self._check_duplicates(data)
            if duplicate_error:
                # Convert JSON response to structured error for form handling
                error_response, status_code = duplicate_error
                error_data = error_response.get_json()
                return {
                    'success': False,
                    'error': error_data.get('error'),
                    'field': error_data.get('field'),
                    'type': error_data.get('type'),
                    'status_code': status_code
                }

            # Create entity with allowed fields
            entity_data = {}
            for field in allowed_fields:
                if field in data:
                    entity_data[field] = data[field]

            entity = self.model_class(**entity_data)
            db.session.add(entity)
            db.session.commit()

            return {
                'success': True,
                'entity': entity,
                'entity_id': entity.id
            }

        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': str(e),
                'status_code': 400
            }

    def _check_duplicates(self, data):
        """Check for duplicate entities based on unique fields"""
        # Define which fields should be unique for each entity type
        unique_fields = {
            'Company': ['name'],  # Company names should be unique
            'Stakeholder': ['email'],  # Stakeholder emails should be unique
            'Opportunity': [],  # Opportunities can have duplicate names (different companies)
            'Task': []  # Tasks can have duplicate descriptions
        }

        entity_name = self.model_class.__name__
        fields_to_check = unique_fields.get(entity_name, [])

        for field in fields_to_check:
            if field in data and data[field]:
                # Check if entity with this field value already exists
                existing = self.model_class.query.filter(
                    getattr(self.model_class, field).ilike(data[field])
                ).first()

                if existing:
                    field_label = field.replace('_', ' ').title()
                    return jsonify({
                        "error": f"A {entity_name.lower()} with this {field_label.lower()} already exists.",
                        "field": field,
                        "type": "duplicate"
                    }), 409

        return None

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
        from app.utils.core.model_helpers import auto_serialize

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
        from app.utils.core.model_helpers import auto_serialize

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

    def __init__(self, model_class, entity_name, entity_handler=None):
        self.model_class = model_class
        self.entity_name = entity_name
        self.entity_handler = entity_handler
        
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
        
        # Group entities using the same handler as the routes for DRY consistency
        grouper = EntityGrouper(self.model_class, self.entity_name, self.entity_handler)
        grouped_entities = grouper.group_by_field(filtered_entities, group_by, custom_grouper)
        
        # Get proper plural from model metadata instead of string manipulation
        from app.utils.model_registry import ModelRegistry
        try:
            metadata = ModelRegistry.get_model_metadata(self.model_class.__name__.lower())
            entity_plural = metadata.display_name_plural.lower().replace(' ', '_')
        except:
            entity_plural = f"{self.entity_name}s"  # Fallback only if metadata fails

        return {
            f"grouped_{entity_plural}": grouped_entities,
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
        """Parse multiple parameter values and comma-separated filter parameters"""
        param_values = request.args.getlist(param_name)
        if not param_values:
            return []
        # Handle both multiple parameters AND comma-separated values
        all_values = []
        for value in param_values:
            if ',' in value:
                # Handle comma-separated values within single parameter
                all_values.extend([p.strip() for p in value.split(",") if p.strip()])
            else:
                # Handle individual parameter values
                if value.strip():
                    all_values.append(value.strip())
        return all_values
    
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
        # Use model config for plural names - NO string manipulation
        entity_plural = self.model_class.__entity_config__.get('display_name', self.entity_name)
        
        context.update({
            'entity_type': self.entity_name,
            'entity_name_singular': self.entity_name,
            'entity_name_plural': entity_plural,
            'card_config': ModelIntrospector.get_card_config(self.model_class),
            'model_class': self.model_class
        })
        
        return context


class EntityGrouper:
    """Universal grouping handler for all entities - DRY version using MetadataDrivenHandler"""

    def __init__(self, model_class, entity_name, entity_handler=None):
        self.model_class = model_class
        self.entity_name = entity_name

        # Use MetadataDrivenHandler for DRY field resolution
        if entity_handler is None:
            from app.utils.core.entity_handlers import MetadataDrivenHandler
            self.handler = MetadataDrivenHandler(model_class)
        else:
            self.handler = entity_handler

    def group_by_field(self, entities, group_by, custom_grouper=None):
        """Group entities by specified field using MetadataDrivenHandler mapping - DRY approach"""

        # Use custom grouper if provided
        if custom_grouper:
            result = custom_grouper(entities, group_by)
            if result is not None:
                return result

        # Get group mapping from MetadataDrivenHandler (DRY - no duplicate logic)
        group_mapping = self.handler.get_group_mapping()
        group_config = group_mapping.get(group_by)

        if not group_config:
            # Fallback: return all entities in one group
            return [{
                "key": "all",
                "label": f"All {self.model_class.__entity_config__.get('display_name', self.entity_name).title()}",
                "entities": entities,
                "count": len(entities)
            }]

        # Use the same grouping logic as UniversalEntityManager for consistency
        grouped = defaultdict(list)
        field_name = group_config.get('field', group_by)
        default_value = group_config.get('default_value', 'Other')

        for entity in entities:
            # Handle relationship fields (e.g., company.name)
            if '.' in field_name:
                obj = entity
                for attr in field_name.split('.'):
                    obj = getattr(obj, attr, None) if obj else None
                field_value = obj
            else:
                # Direct field access
                field_value = getattr(entity, field_name, None)

            # Determine group key
            if field_value is not None:
                # Handle value-based groupings (e.g., deal value ranges)
                if 'value_ranges' in group_config:
                    group_key = self._get_value_range_group(field_value, group_config['value_ranges'])
                else:
                    group_key = str(field_value)
            else:
                group_key = default_value

            grouped[group_key].append(entity)

        # Build result using specified order or alphabetical
        result = []
        order = group_config.get('order', [])

        if order:
            # Use specified order
            for key in order:
                if key in grouped and grouped[key]:
                    result.append({
                        "key": key,
                        "label": self._format_group_label(key, group_config),
                        "entities": grouped[key],
                        "count": len(grouped[key])
                    })
        else:
            # Use alphabetical order
            for key in sorted(grouped.keys()):
                if grouped[key]:
                    result.append({
                        "key": key,
                        "label": self._format_group_label(key, group_config),
                        "entities": grouped[key],
                        "count": len(grouped[key])
                    })

        return result

    def _get_value_range_group(self, value: float, value_ranges: list) -> str:
        """Determine which value range group a numeric value belongs to."""
        for min_value, group_key, label in value_ranges:
            if value >= min_value:
                return group_key
        return 'Other'

    def _format_group_label(self, key: str, group_config: dict) -> str:
        """Format group label for display."""
        if key and '-' in key:
            return key.replace('-', ' ').title()
        return str(key).title() if key else 'Other'
