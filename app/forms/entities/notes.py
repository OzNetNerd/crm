"""
Notes Forms

Simple note form using standard WTForms.
"""

from wtforms import TextAreaField, SelectField
from wtforms.validators import DataRequired, Length
from ..base.base_forms import BaseForm


class NoteForm(BaseForm):
    """Note form with direct field definitions"""

    content = TextAreaField(
        "Note Content",
        validators=[DataRequired(), Length(min=1, max=2000)],
        render_kw={"placeholder": "Enter your note...", "rows": 4},
    )

    is_internal = SelectField(
        "Note Type",
        choices=[("1", "Internal Note"), ("0", "Client-Facing Note")],
        default="1",
        coerce=lambda x: x == "1",
    )
