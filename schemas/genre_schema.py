from marshmallow import Schema, fields, validate, pre_load

class GenreCreateSchema(Schema):
    """
    Schema for validating and cleaning incoming data to create a genre.
    Ensures the name is present, trimmed of whitespace, and within length limits.
    """
    name = fields.String(required=True, validate=validate.Length(min=1, max=50))

    @pre_load
    def strip_name(self, data, **kwargs):
        if 'name' in data and isinstance(data['name'], str):
            data['name'] = data['name'].strip()
        return data

class GenreSchema(Schema):
    """
    Schema for serialising genre data for output, including id and name.
    """
    id = fields.Integer(dump_only=True)
    name = fields.String()
