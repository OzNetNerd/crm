"""Modern entity CRUD utilities with safe deletion."""
from typing import Dict, List, Tuple, Any
from flask import abort, jsonify
from sqlalchemy import inspect
from sqlalchemy.orm import relationship
from app.models import db, MODEL_REGISTRY


def get_model_by_table_name(table_name: str):
    """Get model class from table name."""
    return next((model for model in MODEL_REGISTRY.values() if model.__tablename__ == table_name), None)


def get_entity_list(table_name: str):
    """Get list of entities."""
    model = get_model_by_table_name(table_name)
    if not model:
        abort(404)

    sort_field = model.get_default_sort_field()
    entities = model.query.order_by(getattr(model, sort_field)).all()
    return jsonify([entity.to_dict() for entity in entities])


def get_entity_detail(table_name: str, entity_id: int):
    """Get single entity details."""
    model = get_model_by_table_name(table_name)
    if not model:
        abort(404)

    entity = model.query.get_or_404(entity_id)
    return jsonify(entity.to_dict())


def create_entity(model_class, data: dict):
    """Create new entity with proper error handling."""
    try:
        entity = model_class(**data)
        db.session.add(entity)
        db.session.commit()
        return entity
    except Exception as e:
        db.session.rollback()
        raise e


def update_entity(model_class, entity_id: int, data: dict):
    """Update existing entity with validation."""
    entity = model_class.query.get_or_404(entity_id)

    for key, value in data.items():
        if hasattr(entity, key):
            setattr(entity, key, value)

    try:
        db.session.commit()
        return entity
    except Exception as e:
        db.session.rollback()
        raise e


def get_deletion_impact(model_class, entity_id: int) -> Dict[str, Any]:
    """Analyze deletion impact for an entity."""
    entity = model_class.query.get_or_404(entity_id)
    inspector = inspect(model_class)
    impact = {
        "entity": f"{model_class.__display_name__} '{entity}' (ID: {entity_id})",
        "will_cascade": [],
        "dependent_entities": [],
        "safe_to_delete": True
    }

    # Check relationships that will cascade
    for rel_name, rel in inspector.relationships.items():
        if hasattr(entity, rel_name):
            related_items = getattr(entity, rel_name)

            # Handle single relationships
            if not isinstance(related_items, list):
                related_items = [related_items] if related_items else []

            if related_items:
                # Check if this relationship will cascade
                fk_columns = rel.local_columns if rel.direction.name == 'ONETOMANY' else rel.remote_side

                cascades = any(
                    fk.foreign_keys and
                    any(fk_constraint.ondelete == 'CASCADE' for fk_constraint in fk.foreign_keys)
                    for fk in fk_columns
                )

                if cascades:
                    impact["will_cascade"].append({
                        "relationship": rel_name,
                        "count": len(related_items),
                        "items": [str(item) for item in related_items[:5]]  # Sample
                    })
                else:
                    impact["dependent_entities"].append({
                        "relationship": rel_name,
                        "count": len(related_items),
                        "items": [str(item) for item in related_items[:5]]
                    })
                    impact["safe_to_delete"] = False

    return impact


def delete_entity_safe(model_class, entity_id: int) -> Dict[str, Any]:
    """Delete entity with cascade awareness and safety checks."""
    try:
        # Get deletion impact first
        impact = get_deletion_impact(model_class, entity_id)

        # If not safe to delete due to non-cascading dependencies, return error
        if not impact["safe_to_delete"]:
            return {
                "success": False,
                "error": "Cannot delete entity with dependencies",
                "impact": impact
            }

        # Proceed with deletion
        entity = model_class.query.get_or_404(entity_id)
        db.session.delete(entity)
        db.session.commit()

        return {
            "success": True,
            "message": "Deleted successfully",
            "impact": impact
        }

    except Exception as e:
        db.session.rollback()
        return {
            "success": False,
            "error": str(e),
            "impact": None
        }


def delete_entity(model_class, entity_id: int):
    """Modern deletion with full safety and impact analysis."""
    result = delete_entity_safe(model_class, entity_id)

    if not result["success"]:
        abort(400, description=result["error"])

    return {"message": result["message"], "impact": result["impact"]}