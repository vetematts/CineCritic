from marshmallow import Schema, fields, validate

class GenreCreateSchema(Schema):
    name = fields.String(required=True, validate=validate.Length(min=1, max=50))

class GenreSchema(Schema):
    id = fields.Integer()
    name = fields.String()
