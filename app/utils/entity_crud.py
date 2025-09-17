"""Simple entity CRUD utilities - generic operations."""
from flask import abort, jsonify
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
    """Create new entity - generic creation."""
    try:
        entity = model_class(**data)
        db.session.add(entity)
        db.session.commit()
        return entity
    except Exception as e:
        db.session.rollback()
        raise e


def update_entity(model_class, entity_id: int, data: dict):
    """Update existing entity."""
    entity = model_class.query.get_or_404(entity_id)

    for key, value in data.items():
        if hasattr(entity, key):
            setattr(entity, key, value)

    db.session.commit()
    return entity


def delete_entity(model_class, entity_id: int):
    """Delete entity."""
    entity = model_class.query.get_or_404(entity_id)
    db.session.delete(entity)
    db.session.commit()
    return {"message": "Deleted successfully"}