"""
Base Form Classes and Validation Mixins

Provides shared validation methods for forms.
Simple, direct, no unnecessary abstractions.
"""

import json
from flask_wtf import FlaskForm


class BaseForm(FlaskForm):
    """Base form class with common validation methods"""

    def validate_linked_entities_json(self, field):
        """Validate linked_entities JSON field format"""
        if field.data:
            try:
                entities = json.loads(field.data)
                if not isinstance(entities, list):
                    raise ValueError("Linked entities must be a list")

                for entity in entities:
                    if (
                        not isinstance(entity, dict)
                        or "type" not in entity
                        or "id" not in entity
                    ):
                        raise ValueError(
                            "Each linked entity must have 'type' and 'id' fields"
                        )

            except json.JSONDecodeError:
                raise ValueError("Invalid JSON format for linked entities")
            except ValueError as e:
                field.errors.append(str(e))
                return False
        return True

    def validate_parent_task_relationship(self, parent_task_id_field, task_type_field):
        """Validation for parent-child task relationships"""
        if task_type_field.data == "child" and not parent_task_id_field.data:
            parent_task_id_field.errors.append(
                "Parent task is required for child tasks"
            )
            return False
        return True

    def validate_multi_task_children(self, child_tasks_field, min_children=2):
        """Validation for multi-task child requirements"""
        if len(child_tasks_field.data) < min_children:
            child_tasks_field.errors.append(
                f"Multi Tasks must have at least {min_children} child tasks"
            )
            return False
        return True

    def get_field_layout(self):
        """
        Return field layout configuration for consistent rendering across view and edit modes.

        Layout types supported:
        - single: Single field on its own row
        - inline-2col: Two fields side by side
        - inline-3col: Three fields side by side

        Returns a list of layout dictionaries, e.g.:
        [
            {'type': 'inline-2col', 'fields': ['name', 'industry']},
            {'type': 'single', 'field': 'comments'}
        ]

        Default implementation returns all fields as single rows.
        """
        if hasattr(self, 'get_display_fields'):
            # Use existing display fields if defined
            fields = self.get_display_fields()
            return [{'type': 'single', 'field': field} for field in fields]
        else:
            # Return all non-hidden fields as single rows
            fields = []
            for field in self:
                if field.name not in ['csrf_token', 'submit'] and field.type != 'HiddenField':
                    fields.append({'type': 'single', 'field': field.name})
            return fields
