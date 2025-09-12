"""Centralized pluralization utilities for consistent text handling across the application."""


class PluralUtils:
    """Centralized plural mapping utility"""
    
    # Master plural mapping - single source of truth
    PLURAL_MAP = {
        'opportunity': 'opportunities',
        'company': 'companies', 
        'category': 'categories',
        'activity': 'activities',
        'entity': 'entities',
        'priority': 'priorities',
        'industry': 'industries',
        'stakeholder': 'stakeholders',
        'task': 'tasks',
        'note': 'notes',
        'team_member': 'team members'
    }
    
    @classmethod
    def pluralize(cls, word, count=None):
        """
        Convert singular word to plural form
        
        Args:
            word: Singular word to pluralize
            count: Optional count to determine if plural is needed
            
        Returns:
            Plural form of the word
        """
        if count is not None and count == 1:
            return word
            
        return cls.PLURAL_MAP.get(word, f"{word}s")
    
    @classmethod
    def pluralized_count(cls, count, singular, plural=None, short=False, show_zero=False):
        """
        Format count with appropriate singular/plural form
        
        Args:
            count: The count number
            singular: Singular form of the word
            plural: Optional explicit plural form
            short: Whether to use short forms (e.g., 'opp' for 'opportunity')
            show_zero: Whether to show when count is 0
            
        Returns:
            Formatted string like "5 opportunities" or "1 opportunity"
        """
        if count == 0 and not show_zero:
            return ""
            
        display_singular = singular
        
        if plural:
            display_plural = plural
        else:
            display_plural = cls.pluralize(singular)
        
        # Handle short forms
        if short:
            if singular == 'opportunity':
                display_singular = 'opp'
                display_plural = 'opps'
        
        word_form = display_singular if count == 1 else display_plural
        return f"{count} {word_form}"