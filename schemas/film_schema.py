from datetime import date
from marshmallow import Schema, fields, validate, pre_load, ValidationError

CURRENT_YEAR = date.today().year

class FilmCreateSchema(Schema):
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
    def normalize_strings(self, in_data, **kwargs):
        # Trim string fields if they exist
        for key in ("title", "director", "description"):
            val = in_data.get(key)
            if isinstance(val, str):
                in_data[key] = val.strip()
        return in_data


class FilmSchema(Schema):
    # Explicit dump_only so clients can’t set id
    id = fields.Integer(dump_only=True)
    title = fields.String()
    release_year = fields.Integer()
    director = fields.String()
    description = fields.String()
