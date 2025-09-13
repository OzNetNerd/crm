"""
Template Functions for Dynamic Card System

Makes CardConfigBuilder available to Jinja templates.
"""

from app.utils.cards.config_builder import CardConfigBuilder


def build_dynamic_card_config(entity_type, entity):
    """Build card configuration dynamically from model metadata."""
    return CardConfigBuilder.build_card_config(entity_type, entity)


def register_template_functions(app):
    """Register template functions with Flask app."""
    app.jinja_env.globals['build_dynamic_card_config'] = build_dynamic_card_config