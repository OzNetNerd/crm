"""
Frontend Data Contracts - ADR-017 Implementation

Type contracts and validation for configuration objects to ensure
consistent frontend-backend data communication.
"""

from typing import Dict, List, Any, TypedDict, Optional
from dataclasses import dataclass


class EntityConfigContract(TypedDict):
    """Type contract for entity configuration objects - ADR-017"""
    entity_name: str
    entity_name_singular: str  
    entity_description: str
    entity_type: str
    endpoint_name: str
    entity_buttons: List[Dict[str, str]]


class UIConfigContract(TypedDict):
    """Type contract for UI configuration objects - ADR-017"""
    show_filters: bool
    show_grouping: bool
    show_sorting: bool
    show_search: bool
    items_per_page: int
    default_view: str
    available_filters: Optional[List[str]]
    active_filters: Optional[Dict[str, Any]]
    available_sorts: Optional[List[str]]
    active_sort: Optional[Dict[str, str]]
    available_groups: Optional[List[str]]
    active_group: Optional[str]


class DropdownConfigContract(TypedDict):
    """Type contract for dropdown configuration objects - ADR-017"""
    options: List[Dict[str, Any]]
    selected_values: Optional[List[str]]
    placeholder: str
    multiple: bool
    searchable: bool


class FormConfigContract(TypedDict):
    """Type contract for form configuration objects - ADR-017"""
    fields: Dict[str, Dict[str, Any]]
    layout: Dict[str, Any]
    validation_rules: Dict[str, List[str]]
    submit_url: str
    method: str


class IndexContextContract(TypedDict):
    """Complete type contract for index page context - ADR-017"""
    # Configuration objects
    entity_config: EntityConfigContract
    ui_config: UIConfigContract
    dropdown_configs: Dict[str, DropdownConfigContract]
    
    # Simple variables
    current_page: int
    total_items: int
    has_items: bool
    group_by: str
    sort_by: str
    sort_direction: str
    show_completed: bool
    primary_filter: List[str]
    secondary_filter: List[str]
    entity_filter: List[str]
    
    # Relationship data
    relationship_labels: Dict[str, Dict[str, str]]


class FrontendContractValidator:
    """Validate configuration objects against frontend contracts - ADR-017"""
    
    @staticmethod
    def validate_entity_config(config: Dict[str, Any]) -> List[str]:
        """
        Validate entity configuration against contract
        
        Args:
            config: Entity configuration dictionary
            
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        required_fields = [
            'entity_name', 'entity_name_singular', 'entity_description',
            'entity_type', 'endpoint_name', 'entity_buttons'
        ]
        
        for field in required_fields:
            if field not in config:
                errors.append(f"Missing required field: {field}")
            elif config[field] is None:
                errors.append(f"Field {field} cannot be None")
        
        # Validate entity_buttons structure
        if 'entity_buttons' in config and isinstance(config['entity_buttons'], list):
            for i, button in enumerate(config['entity_buttons']):
                if not isinstance(button, dict):
                    errors.append(f"entity_buttons[{i}] must be a dictionary")
                elif 'title' not in button or 'url' not in button:
                    errors.append(f"entity_buttons[{i}] missing required 'title' or 'url'")
        
        return errors
    
    @staticmethod
    def validate_ui_config(config: Dict[str, Any]) -> List[str]:
        """
        Validate UI configuration against contract
        
        Args:
            config: UI configuration dictionary
            
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        required_fields = [
            'show_filters', 'show_grouping', 'show_sorting', 'show_search',
            'items_per_page', 'default_view'
        ]
        
        for field in required_fields:
            if field not in config:
                errors.append(f"Missing required field: {field}")
        
        # Validate boolean fields
        boolean_fields = ['show_filters', 'show_grouping', 'show_sorting', 'show_search']
        for field in boolean_fields:
            if field in config and not isinstance(config[field], bool):
                errors.append(f"Field {field} must be boolean")
        
        # Validate items_per_page
        if 'items_per_page' in config:
            if not isinstance(config['items_per_page'], int) or config['items_per_page'] <= 0:
                errors.append("items_per_page must be a positive integer")
        
        # Validate default_view
        if 'default_view' in config:
            valid_views = ['card', 'table', 'list']
            if config['default_view'] not in valid_views:
                errors.append(f"default_view must be one of {valid_views}")
        
        return errors
    
    @staticmethod
    def validate_dropdown_config(config: Dict[str, Any]) -> List[str]:
        """
        Validate dropdown configuration against contract
        
        Args:
            config: Dropdown configuration dictionary
            
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Validate required fields
        required_fields = ['options', 'placeholder', 'multiple', 'searchable']
        for field in required_fields:
            if field not in config:
                errors.append(f"Missing required field: {field}")
        
        # Validate options structure
        if 'options' in config:
            if not isinstance(config['options'], list):
                errors.append("options must be a list")
            else:
                for i, option in enumerate(config['options']):
                    if not isinstance(option, dict):
                        errors.append(f"options[{i}] must be a dictionary")
                    elif 'value' not in option or 'label' not in option:
                        errors.append(f"options[{i}] missing required 'value' or 'label'")
        
        # Validate boolean fields
        boolean_fields = ['multiple', 'searchable']
        for field in boolean_fields:
            if field in config and not isinstance(config[field], bool):
                errors.append(f"Field {field} must be boolean")
        
        return errors
    
    @staticmethod
    def validate_index_context(context: Dict[str, Any]) -> List[str]:
        """
        Validate entire index context against contract
        
        Args:
            context: Complete index context dictionary
            
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Validate entity_config
        if 'entity_config' in context:
            entity_errors = FrontendContractValidator.validate_entity_config(
                context['entity_config']
            )
            errors.extend([f"entity_config.{error}" for error in entity_errors])
        else:
            errors.append("Missing required entity_config")
        
        # Validate ui_config
        if 'ui_config' in context:
            ui_errors = FrontendContractValidator.validate_ui_config(
                context['ui_config']
            )
            errors.extend([f"ui_config.{error}" for error in ui_errors])
        else:
            errors.append("Missing required ui_config")
        
        # Validate dropdown_configs
        if 'dropdown_configs' in context:
            if isinstance(context['dropdown_configs'], dict):
                for key, dropdown_config in context['dropdown_configs'].items():
                    dropdown_errors = FrontendContractValidator.validate_dropdown_config(
                        dropdown_config
                    )
                    errors.extend([f"dropdown_configs.{key}.{error}" for error in dropdown_errors])
            else:
                errors.append("dropdown_configs must be a dictionary")
        
        # Validate simple variables
        simple_fields = {
            'current_page': int,
            'total_items': int,
            'has_items': bool,
            'group_by': str,
            'sort_by': str,
            'sort_direction': str,
            'show_completed': bool
        }
        
        for field, expected_type in simple_fields.items():
            if field in context:
                if not isinstance(context[field], expected_type):
                    errors.append(f"Field {field} must be {expected_type.__name__}")
            else:
                errors.append(f"Missing required field: {field}")
        
        # Validate filter arrays
        filter_fields = ['primary_filter', 'secondary_filter', 'entity_filter']
        for field in filter_fields:
            if field in context:
                if not isinstance(context[field], list):
                    errors.append(f"Field {field} must be a list")
                elif not all(isinstance(item, str) for item in context[field]):
                    errors.append(f"All items in {field} must be strings")
        
        return errors
    
    @staticmethod
    def validate_and_report(context: Dict[str, Any], context_name: str = "context") -> bool:
        """
        Validate context and print detailed report
        
        Args:
            context: Context dictionary to validate
            context_name: Name for reporting purposes
            
        Returns:
            True if valid, False if validation errors found
        """
        errors = FrontendContractValidator.validate_index_context(context)
        
        if errors:
            print(f"❌ Validation failed for {context_name}:")
            for error in errors:
                print(f"  - {error}")
            return False
        else:
            print(f"✅ {context_name} passed all validation checks")
            return True


@dataclass
class JavaScriptConfig:
    """Configuration object specifically for JavaScript consumption"""
    entity: Dict[str, Any]
    ui: Dict[str, Any]
    dropdowns: Dict[str, Any]
    request_params: Dict[str, Any]
    api_endpoints: Dict[str, str]
    csrf_token: str = None
    
    def to_json_safe(self) -> Dict[str, Any]:
        """Convert to JSON-safe dictionary for JavaScript"""
        return {
            'entity': self.entity,
            'ui': self.ui,
            'dropdowns': self.dropdowns,
            'requestParams': self.request_params,  # camelCase for JS
            'apiEndpoints': self.api_endpoints,     # camelCase for JS
            'csrfToken': self.csrf_token           # camelCase for JS
        }


class ContextTransformer:
    """Transform server context to different frontend formats"""
    
    @staticmethod
    def to_javascript_config(context: Dict[str, Any]) -> JavaScriptConfig:
        """
        Transform server context to JavaScript-friendly configuration
        
        Args:
            context: Server-side context dictionary
            
        Returns:
            JavaScriptConfig object ready for JSON serialization
        """
        # Extract request parameters
        request_params = {
            'groupBy': context.get('group_by', ''),
            'sortBy': context.get('sort_by', ''),
            'sortDirection': context.get('sort_direction', 'asc'),
            'showCompleted': context.get('show_completed', False),
            'primaryFilter': context.get('primary_filter', []),
            'secondaryFilter': context.get('secondary_filter', []),
            'entityFilter': context.get('entity_filter', []),
            'currentPage': context.get('current_page', 1)
        }
        
        # Extract API endpoints
        entity_config = context.get('entity_config', {})
        api_endpoints = {
            'list': f"/api/{entity_config.get('endpoint_name', '')}",
            'create': f"/api/{entity_config.get('endpoint_name', '')}",
            'update': f"/api/{entity_config.get('endpoint_name', '')}/{{id}}",
            'delete': f"/api/{entity_config.get('endpoint_name', '')}/{{id}}"
        }
        
        return JavaScriptConfig(
            entity=context.get('entity_config', {}),
            ui=context.get('ui_config', {}),
            dropdowns=context.get('dropdown_configs', {}),
            request_params=request_params,
            api_endpoints=api_endpoints
        )