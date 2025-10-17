from marshmallow import Schema, fields, validate, pre_load

class GenreCreateSchema(Schema):
    name = fields.String(required=True, validate=validate.Length(min=1, max=50))

    @pre_load
    def strip_name(self, data, **kwargs):
        if 'name' in data and isinstance(data['name'], str):
            data['name'] = data['name'].strip()
        return data

class GenreSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String()
