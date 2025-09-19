"""Dropdown configuration builders - DRY and reusable."""

from dataclasses import dataclass
from typing import Dict, Any, List, Optional


@dataclass
class DropdownConfig:
    """Configuration for a dropdown.

    Attributes:
        name: Field name for the dropdown.
        options: List of option dictionaries.
        current_value: Currently selected value.
        placeholder: Placeholder text.
        multiple: Whether multiple selection is allowed.
        searchable: Whether the dropdown is searchable.
        label: Display label for the dropdown.
    """

    name: str
    options: List[Dict[str, str]]
    current_value: str = ""
    placeholder: str = ""
    multiple: bool = False
    searchable: bool = False
    label: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for template consumption.

        Returns:
            Dictionary representation of the dropdown config.
        """
        return {
            "name": self.name,
            "options": self.options,
            "current_value": self.current_value,
            "placeholder": self.placeholder,
            "multiple": self.multiple,
            "searchable": self.searchable,
            "label": self.label,
        }


class DropdownBuilder:
    """Builder for dropdown configurations."""

    @staticmethod
    def build_filter_dropdowns(
        metadata: Dict[str, Any], request_args: Dict[str, Any]
    ) -> Dict[str, Dict[str, Any]]:
        """Build filter dropdowns for fields with choices.

        Args:
            metadata: Field metadata dictionary.
            request_args: Request arguments dictionary.

        Returns:
            Dictionary of dropdown configurations keyed by filter name.
        """
        dropdowns = {}

        for field_name, field_info in metadata.items():
            if not (field_info.get("filterable") and field_info.get("choices")):
                continue

            options = [{"value": "", "label": f'All {field_info["label"]}'}]
            options.extend(
                [
                    {"value": val, "label": data.get("label", val)}
                    for val, data in field_info["choices"].items()
                ]
            )

            config = DropdownConfig(
                name=field_name,
                options=options,
                current_value=request_args.get(field_name, ""),
                placeholder=f'All {field_info["label"]}',
                label=field_info["label"],
                searchable=(
                    field_name == "industry" or len(options) > 8
                ),  # Make Industry and large lists searchable
            )

            dropdowns[f"filter_{field_name}"] = config.to_dict()

        return dropdowns

    @staticmethod
    def build_group_dropdown(
        metadata: Dict[str, Any], request_args: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Build group-by dropdown if groupable fields exist.

        Args:
            metadata: Field metadata dictionary.
            request_args: Request arguments dictionary.

        Returns:
            Dropdown configuration or None if no groupable fields.
        """
        options = [
            {"value": name, "label": info["label"]}
            for name, info in metadata.items()
            if info.get("groupable")
        ]

        if not options:
            return None

        config = DropdownConfig(
            name="group_by",
            options=options,
            current_value=request_args.get("group_by", ""),
            placeholder="Group by...",
            searchable=False,
            label="Group By",
        )

        return config.to_dict()

    @staticmethod
    def build_sort_dropdown(
        metadata: Dict[str, Any], request_args: Dict[str, Any], default_sort: str
    ) -> Dict[str, Any]:
        """Build sort-by dropdown with all sortable fields.

        Args:
            metadata: Field metadata dictionary.
            request_args: Request arguments dictionary.
            default_sort: Default sort field.

        Returns:
            Sort dropdown configuration.
        """
        options = [
            {"value": name, "label": info["label"]}
            for name, info in metadata.items()
            if info.get("sortable")
        ]

        # Ensure ID is always sortable
        if not any(opt["value"] == "id" for opt in options):
            options.append({"value": "id", "label": "ID"})

        config = DropdownConfig(
            name="sort_by",
            options=options,
            current_value=request_args.get("sort_by", default_sort),
            placeholder="Sort by...",
            searchable=False,
            label="Sort By",
        )

        return config.to_dict()

    @staticmethod
    def build_direction_dropdown(request_args: Dict[str, Any]) -> Dict[str, Any]:
        """Build sort direction dropdown.

        Args:
            request_args: Request arguments dictionary.

        Returns:
            Direction dropdown configuration.
        """
        config = DropdownConfig(
            name="sort_direction",
            options=[
                {"value": "asc", "label": "Ascending"},
                {"value": "desc", "label": "Descending"},
            ],
            current_value=request_args.get("sort_direction", "asc"),
            placeholder="Order",
            label="Order",
        )

        return config.to_dict()

    @classmethod
    def build_all(
        cls, model: type, request_args: Dict[str, Any]
    ) -> Dict[str, Dict[str, Any]]:
        """Build all dropdown configurations for entity UI.

        Args:
            model: SQLAlchemy model class.
            request_args: Request arguments dictionary.

        Returns:
            Dictionary of all dropdown configurations.
        """
        from app.services import MetadataService

        metadata = MetadataService.get_field_metadata(model)
        dropdowns = {}

        # Add filter dropdowns
        dropdowns.update(cls.build_filter_dropdowns(metadata, request_args))

        # Add group dropdown if applicable
        if group_dropdown := cls.build_group_dropdown(metadata, request_args):
            dropdowns["group_by"] = group_dropdown

        # Add sort dropdowns
        default_sort = MetadataService.get_default_sort_field(model)
        dropdowns["sort_by"] = cls.build_sort_dropdown(
            metadata, request_args, default_sort
        )
        dropdowns["sort_direction"] = cls.build_direction_dropdown(request_args)

        return dropdowns

    @classmethod
    def get_dropdown_options(
        cls, dropdown_type: str, entity_type: str = None
    ) -> List[Dict[str, str]]:
        """Get options for a specific dropdown type.

        Args:
            dropdown_type: The type of dropdown (sort_by, group_by, etc.)
            entity_type: Optional entity type for context-specific dropdowns.

        Returns:
            List of option dictionaries with value and label keys.
        """
        from app.services import MetadataService
        from app.models import MODEL_REGISTRY

        # For sort_by and group_by, we need the entity type from the current page context
        if dropdown_type == "sort_by" and entity_type:
            model = MODEL_REGISTRY.get(entity_type)
            if model:
                metadata = MetadataService.get_field_metadata(model)
                options = [
                    {"value": name, "label": info["label"]}
                    for name, info in metadata.items()
                    if info.get("sortable")
                ]
                # Ensure ID is always sortable
                if not any(opt["value"] == "id" for opt in options):
                    options.append({"value": "id", "label": "ID"})
                return options

        elif dropdown_type == "group_by" and entity_type:
            model = MODEL_REGISTRY.get(entity_type)
            if model:
                metadata = MetadataService.get_field_metadata(model)
                return [
                    {"value": name, "label": info["label"]}
                    for name, info in metadata.items()
                    if info.get("groupable")
                ]

        elif dropdown_type == "sort_direction":
            return [
                {"value": "asc", "label": "Ascending"},
                {"value": "desc", "label": "Descending"},
            ]

        # For filter dropdowns, extract field name
        elif dropdown_type.startswith("filter_") and entity_type:
            field_name = dropdown_type[7:]  # Remove "filter_" prefix
            model = MODEL_REGISTRY.get(entity_type)
            if model:
                metadata = MetadataService.get_field_metadata(model)
                field_info = metadata.get(field_name)
                if field_info and field_info.get("choices"):
                    options = [{"value": "", "label": f'All {field_info["label"]}'}]
                    options.extend(
                        [
                            {"value": val, "label": data.get("label", val)}
                            for val, data in field_info["choices"].items()
                        ]
                    )
                    return options

        return []
