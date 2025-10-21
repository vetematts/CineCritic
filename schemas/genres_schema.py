"""
Genre schemas.

Defines schemas for creating and serialising Genre objects.

- GenreCreateSchema: Validates input when creating a genre, including trimming and length rules.
- GenreSchema: Serialises Genre objects for output, including id and name.
"""
from marshmallow import Schema, fields, validate, pre_load

class GenreCreateSchema(Schema):
    """Schema for creating a genre.

    - Validates user submitted fields:
    - name: Required string, trimmed, 1–50 characters.
    """
    name = fields.String(required=True, validate=validate.Length(min=1, max=50))

    @pre_load
    def strip_name(self, data, **kwargs):
        if 'name' in data and isinstance(data['name'], str):
            data['name'] = data['name'].strip()
        return data


class GenreSchema(Schema):
    """Schema for serialising Genre objects.

    Includes:
    - id (int): Database identifier.
    - name (str): Genre name.
    """
    id = fields.Integer(dump_only=True)
    name = fields.String()
