"""
Dynamic Configuration Generation - ADR-016 Implementation

Generate configuration objects dynamically from metadata, eliminating
manual configuration definitions and following DRY principles.
"""

from typing import Dict, List, Any, Optional
from .model_registry import ModelRegistry
from .context_builders import FormConfig, DropdownConfig
from .model_metadata import FieldType


class DynamicConfigGenerator:
    """Generate configuration objects dynamically from metadata - ADR-016"""
    
    @staticmethod
    def generate_form_config(model_name: str, 
                           context: Dict[str, Any] = None) -> FormConfig:
        """
        Generate form configuration from model metadata - ADR-016
        
        Args:
            model_name: Name of the model
            context: Additional context for form generation
            
        Returns:
            FormConfig object with complete form definition
        """
        metadata = ModelRegistry.get_model_metadata(model_name)
        
        # Generate field configurations
        fields = {}
        for field_name, field_meta in metadata.fields.items():
            if field_name in metadata.get_form_fields():
                fields[field_name] = {
                    'type': field_meta.field_type.value,
                    'label': field_meta.display_name,
                    'placeholder': field_meta.placeholder,
                    'required': field_meta.required,
                    'help_text': field_meta.help_text,
                    'widget': field_meta.widget,
                    'widget_attrs': field_meta.widget_attrs
                }
                
                # Add choices if applicable
                if field_meta.choices:
                    fields[field_name]['choices'] = field_meta.choices
                
                # Add validation rules
                validation_rules = []
                if field_meta.required:
                    validation_rules.append('required')
                if field_meta.max_length:
                    validation_rules.append(f'max_length:{field_meta.max_length}')
                    
                fields[field_name]['validation'] = validation_rules
        
        # Generate layout from metadata
        layout = metadata.form_layout or DynamicConfigGenerator._default_layout(fields)
        
        return FormConfig(
            fields=fields,
            layout=layout,
            validation_rules={name: field.get('validation', []) 
                            for name, field in fields.items()},
            submit_url=f'/api/{metadata.api_endpoint}',
            method='POST'
        )
    
    @staticmethod
    def generate_table_config(model_name: str) -> Dict[str, Any]:
        """
        Generate table configuration from model metadata - ADR-016
        
        Args:
            model_name: Name of the model
            
        Returns:
            Dict with complete table configuration
        """
        metadata = ModelRegistry.get_model_metadata(model_name)
        
        columns = []
        for field_name in metadata.list_fields:
            field_meta = metadata.fields[field_name]
            columns.append({
                'key': field_name,
                'title': field_meta.display_name,
                'sortable': field_meta.sortable,
                'type': field_meta.field_type.value,
                'formatter': DynamicConfigGenerator._get_field_formatter(field_meta)
            })
        
        return {
            'columns': columns,
            'sortable': True,
            'filterable': True,
            'searchable': True,
            'pagination': {
                'enabled': True,
                'per_page': metadata.list_per_page
            },
            'actions': DynamicConfigGenerator._generate_table_actions(metadata)
        }
    
    @staticmethod
    def generate_filter_configs(model_name: str) -> Dict[str, DropdownConfig]:
        """
        Generate filter dropdown configurations from model metadata
        
        Args:
            model_name: Name of the model
            
        Returns:
            Dict of DropdownConfig objects for filtering
        """
        metadata = ModelRegistry.get_model_metadata(model_name)
        filter_configs = {}
        
        for field_name in metadata.list_filters:
            if field_name in metadata.fields:
                field_meta = metadata.fields[field_name]
                
                # Generate options based on field type
                options = DynamicConfigGenerator._generate_filter_options(field_meta)
                
                filter_configs[f"{field_name}_filter"] = DropdownConfig(
                    options=options,
                    placeholder=f"Filter by {field_meta.display_name}",
                    multiple=True,
                    searchable=len(options) > 10
                )
        
        return filter_configs
    
    @staticmethod
    def generate_sort_config(model_name: str) -> DropdownConfig:
        """
        Generate sort dropdown configuration from model metadata
        
        Args:
            model_name: Name of the model
            
        Returns:
            DropdownConfig for sorting options
        """
        metadata = ModelRegistry.get_model_metadata(model_name)
        
        options = []
        for field_name, field_meta in metadata.fields.items():
            if field_meta.sortable:
                options.extend([
                    {'value': f"{field_name}:asc", 'label': f"{field_meta.display_name} (A-Z)"},
                    {'value': f"{field_name}:desc", 'label': f"{field_meta.display_name} (Z-A)"}
                ])
        
        return DropdownConfig(
            options=options,
            placeholder="Sort by...",
            multiple=False,
            searchable=True
        )
    
    @staticmethod
    def generate_group_config(model_name: str) -> DropdownConfig:
        """
        Generate grouping dropdown configuration from model metadata
        
        Args:
            model_name: Name of the model
            
        Returns:
            DropdownConfig for grouping options
        """
        metadata = ModelRegistry.get_model_metadata(model_name)
        
        options = [{'value': '', 'label': 'No Grouping'}]
        for field_name, field_meta in metadata.fields.items():
            if field_meta.filterable and field_name != 'id':
                options.append({
                    'value': field_name,
                    'label': f"Group by {field_meta.display_name}"
                })
        
        return DropdownConfig(
            options=options,
            placeholder="Group by...",
            multiple=False,
            searchable=False
        )
    
    @staticmethod
    def _default_layout(fields: Dict[str, Any]) -> Dict[str, Any]:
        """Generate default form layout"""
        field_names = list(fields.keys())
        
        if len(field_names) <= 5:
            return {
                'layout': 'vertical',
                'sections': [
                    {
                        'title': 'Information',
                        'fields': field_names
                    }
                ]
            }
        else:
            return {
                'layout': 'vertical',
                'sections': [
                    {
                        'title': 'Basic Information',
                        'fields': field_names[:5]
                    },
                    {
                        'title': 'Additional Details',
                        'fields': field_names[5:]
                    }
                ]
            }
    
    @staticmethod
    def _get_field_formatter(field_meta) -> Optional[str]:
        """Get appropriate formatter for field type"""
        formatter_map = {
            FieldType.DATETIME: 'datetime',
            FieldType.DATE: 'date',
            FieldType.DECIMAL: 'currency',
            FieldType.BOOLEAN: 'yes_no',
            FieldType.FOREIGN_KEY: 'relation'
        }
        return formatter_map.get(field_meta.field_type)
    
    @staticmethod
    def _generate_table_actions(metadata) -> List[Dict[str, Any]]:
        """Generate table action buttons from metadata"""
        actions = []
        
        # Standard CRUD actions based on permissions
        if 'read' in metadata.permissions.get('allowed', ['read', 'update', 'delete']):
            actions.append({
                'title': 'View',
                'class': 'btn-outline-primary',
                'url_template': f"/{metadata.api_endpoint}/{{id}}",
                'icon': 'eye'
            })
        
        if 'update' in metadata.permissions.get('allowed', ['read', 'update', 'delete']):
            actions.append({
                'title': 'Edit',
                'class': 'btn-outline-secondary',
                'url_template': f"/{metadata.api_endpoint}/{{id}}/edit",
                'icon': 'edit'
            })
        
        if 'delete' in metadata.permissions.get('allowed', ['read', 'update', 'delete']):
            actions.append({
                'title': 'Delete',
                'class': 'btn-outline-danger',
                'url_template': f"/{metadata.api_endpoint}/{{id}}/delete",
                'icon': 'trash',
                'confirm': f"Are you sure you want to delete this {metadata.display_name.lower()}?"
            })
        
        return actions
    
    @staticmethod
    def _generate_filter_options(field_meta) -> List[Dict[str, Any]]:
        """Generate filter options based on field type"""
        if field_meta.choices:
            return [{'value': value, 'label': label} for value, label in field_meta.choices]
        
        # For boolean fields
        if field_meta.field_type == FieldType.BOOLEAN:
            return [
                {'value': 'true', 'label': 'Yes'},
                {'value': 'false', 'label': 'No'}
            ]
        
        # For status-like fields
        if 'status' in field_meta.name.lower():
            return [
                {'value': 'active', 'label': 'Active'},
                {'value': 'inactive', 'label': 'Inactive'},
                {'value': 'pending', 'label': 'Pending'}
            ]
        
        # Default to empty - would be populated from database in real implementation
        return []


class FormFieldFactory:
    """Factory for creating form field instances"""
    
    @staticmethod
    def create_field(field_class_name: str, **kwargs):
        """
        Create form field instance
        
        This would integrate with whatever form library is being used
        (WTForms, Django Forms, etc.)
        """
        # Placeholder - would create actual form field instances
        return {
            'type': field_class_name,
            'config': kwargs
        }