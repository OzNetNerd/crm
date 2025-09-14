from . import db


class BaseModel(db.Model):
    """Lightweight base class for entity metadata."""
    __abstract__ = True

    # Name-mangled attributes - singular is REQUIRED
    __display_name__ = None  # REQUIRED: "Company"
    __display_name_plural__ = None  # Optional: defaults to __tablename__.title()

    @classmethod
    def get_display_name(cls):
        """Get singular display name."""
        if not cls.__display_name__:
            raise NotImplementedError(
                f"{cls.__name__} must define __display_name__"
            )
        return cls.__display_name__

    @classmethod
    def get_display_name_plural(cls):
        """Get plural display name."""
        if cls.__display_name_plural__:
            return cls.__display_name_plural__
        # Default to titleized table name (tables are already plural)
        return cls.__tablename__.title()