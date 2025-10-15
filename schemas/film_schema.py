# schemas/film.py
from marshmallow import Schema, fields, validate

class FilmCreateSchema(Schema):
    title = fields.String(required=True, validate=validate.Length(min=1, max=150))
    release_year = fields.Integer(load_default=None)
    director = fields.String(load_default=None, validate=validate.Length(max=100))
    description = fields.String(load_default=None)

# Optional read schema (for consistent responses)
class FilmSchema(Schema):
    id = fields.Integer()
    title = fields.String()
    release_year = fields.Integer()
    director = fields.String()
    description = fields.String()
