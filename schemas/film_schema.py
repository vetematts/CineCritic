"""
Film schemas.

Defines schemas for creating and serialising Film objects.

- FilmCreateSchema: Validates input when creating a film, ensuring title, release year,
  director, and description follow length/range rules. Trims whitespace before validation.
- FilmSchema: Serialises Film objects for output, including id and descriptive fields.
"""

from datetime import date
from marshmallow import Schema, fields, validate, pre_load, ValidationError

CURRENT_YEAR = date.today().year

class FilmCreateSchema(Schema):
    """
    Schema for validating input when creating a new Film.

    Fields:
      - title: required, 1–150 characters
      - release_year: optional, >= 1888 and <= next year
      - director: optional, max 100 characters
      - description: optional text
    """
    title = fields.String(
        required=True,
        validate=validate.Length(min=1, max=150)
    )
    release_year = fields.Integer(
        allow_none=True,
        load_default=None,
        validate=validate.Range(min=1888, max=CURRENT_YEAR + 1)
    )
    director = fields.String(
        allow_none=True,
        load_default=None,
        validate=validate.Length(max=100)
    )
    description = fields.String(
        allow_none=True,
        load_default=None
    )

    @pre_load
    def normalise_strings(self, in_data, **kwargs):
        # Trim string fields if they exist
        for key in ("title", "director", "description"):
            val = in_data.get(key)
            if isinstance(val, str):
                in_data[key] = val.strip()
        return in_data


class FilmSchema(Schema):
    """
    Schema for serializing Film objects in API responses.

    Fields:
      - id (read-only)
      - title
      - release_year
      - director
      - description
    """
    # Explicit dump_only so clients can’t set id
    id = fields.Integer(dump_only=True)
    title = fields.String()
    release_year = fields.Integer()
    director = fields.String()
    description = fields.String()
