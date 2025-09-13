"""Centralized formatting utilities for consistent data display."""

from datetime import datetime, date
from typing import Optional, Union, Any, Dict


class DisplayFormatter:
    """Centralized formatter for consistent data display across the application."""
    
    # Default format strings
    DATE_FORMAT = '%d/%m/%y'
    DATETIME_FORMAT = '%d/%m/%y %H:%M'
    DATETIME_LONG_FORMAT = '%B %d, %Y'
    CURRENCY_SYMBOL = '$'
    
    @classmethod
    def format_date(cls, date_value: Optional[Union[date, datetime]], format_str: Optional[str] = None) -> str:
        """Format date with fallback for None values."""
        if not date_value:
            return ''
        
        if isinstance(date_value, datetime):
            date_value = date_value.date()
            
        return date_value.strftime(format_str or cls.DATE_FORMAT)
    
    @classmethod
    def format_datetime(cls, datetime_value: Optional[datetime], format_str: Optional[str] = None) -> str:
        """Format datetime with fallback for None values."""
        if not datetime_value:
            return ''
            
        return datetime_value.strftime(format_str or cls.DATETIME_FORMAT)
    
    @classmethod
    def format_datetime_long(cls, datetime_value: Optional[datetime]) -> str:
        """Format datetime in long format."""
        if not datetime_value:
            return ''
            
        return datetime_value.strftime(cls.DATETIME_LONG_FORMAT)
    
    @classmethod
    def format_currency(cls, amount: Optional[Union[int, float]], symbol: str = None, show_zero: bool = True) -> str:
        """Format currency with proper comma separators."""
        if amount is None:
            return '' if not show_zero else f'{symbol or cls.CURRENCY_SYMBOL}0'
        
        if amount == 0 and not show_zero:
            return ''
            
        return f'{symbol or cls.CURRENCY_SYMBOL}{amount:,.0f}'
    
    @classmethod
    def format_percentage(cls, value: Optional[float], decimals: int = 1) -> str:
        """Format percentage values."""
        if value is None:
            return '0%'
            
        return f'{value * 100:.{decimals}f}%'
    
    @classmethod
    def format_number(cls, number: Optional[Union[int, float]], decimals: int = 0) -> str:
        """Format numbers with comma separators."""
        if number is None:
            return '0'
            
        return f'{number:,.{decimals}f}'
    
    @classmethod
    def format_days_old(cls, created_at: Optional[datetime]) -> str:
        """Calculate and format days since creation."""
        if not created_at:
            return '0'
            
        days = (datetime.utcnow() - created_at).days
        return str(days)
    
    @classmethod
    def format_metadata_parts(cls, parts: list) -> str:
        """Join metadata parts with bullet separators."""
        return ' • '.join(str(part) for part in parts if part)


def create_display_dict(obj: Any, field_configs: Dict[str, Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Create a display dictionary with formatted fields for template use.
    
    Args:
        obj: Model instance to format
        field_configs: Optional field-specific formatting configs
        
    Returns:
        Dictionary with original fields plus formatted display fields
    """
    if not obj:
        return {}
    
    display_data = {}
    field_configs = field_configs or {}
    
    # Copy all original attributes
    for attr in dir(obj):
        if not attr.startswith('_') and not callable(getattr(obj, attr)):
            try:
                value = getattr(obj, attr)
                # Skip SQLAlchemy internal attributes
                if not str(type(value)).startswith('<sqlalchemy'):
                    display_data[attr] = value
            except:
                continue
    
    # Add formatted versions of common fields
    formatter = DisplayFormatter()
    
    # Date fields
    for field_name in ['created_at', 'updated_at', 'due_date', 'expected_close_date', 'close_date', 'completed_at']:
        if hasattr(obj, field_name):
            raw_value = getattr(obj, field_name)
            if raw_value:
                config = field_configs.get(field_name, {})
                format_str = config.get('format')
                
                if isinstance(raw_value, datetime):
                    display_data[f'{field_name}_formatted'] = formatter.format_datetime(raw_value, format_str)
                    display_data[f'{field_name}_date_formatted'] = formatter.format_date(raw_value, format_str)
                    display_data[f'{field_name}_long'] = formatter.format_datetime_long(raw_value)
                else:
                    display_data[f'{field_name}_formatted'] = formatter.format_date(raw_value, format_str)
            else:
                display_data[f'{field_name}_formatted'] = ''
                display_data[f'{field_name}_date_formatted'] = ''
                display_data[f'{field_name}_long'] = ''
    
    # Currency fields
    for field_name in ['value', 'amount', 'opportunity_value']:
        if hasattr(obj, field_name):
            raw_value = getattr(obj, field_name)
            config = field_configs.get(field_name, {})
            symbol = config.get('symbol', '$')
            display_data[f'{field_name}_formatted'] = formatter.format_currency(raw_value, symbol)
    
    # Special calculated fields
    if hasattr(obj, 'created_at'):
        display_data['days_old'] = formatter.format_days_old(getattr(obj, 'created_at'))
    
    return display_data