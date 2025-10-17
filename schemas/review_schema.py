# schemas/review_schema.py
from marshmallow import Schema, fields, validate, validates_schema, ValidationError, pre_load

# Allowed ratings: 0.5 .. 5.0 in 0.5 steps
_ALLOWED_RATINGS = [x / 2 for x in range(1, 11)]  # 0.5..5.0

class ReviewCreateSchema(Schema):
    rating = fields.Float(required=True, validate=validate.OneOf(_ALLOWED_RATINGS))
    body = fields.String(load_default=None, validate=validate.Length(max=5000))
    status = fields.String(load_default="draft", validate=validate.OneOf(["draft", "published", "flagged"]))
    # For now these are passed in; later you can infer user_id from JWT and take film_id from the URL
    user_id = fields.Integer(required=True)
    film_id = fields.Integer(required=True)

    @pre_load
    def _trim_strings(self, in_data, **kwargs):
        # Normalise whitespace so "   " doesn't sneak past validation
        for key in ("body", "status"):
            val = in_data.get(key)
            if isinstance(val, str):
                in_data[key] = val.strip()
        return in_data

    @validates_schema
    def _status_rules(self, data, **kwargs):
        # Simple rule: if creating as published, body must exist
        if data.get("status") == "published" and not data.get("body"):
            raise ValidationError({"body": ["Body is required when publishing."]})


class ReviewSchema(Schema):
    # Server-managed fields are output-only
    id = fields.Integer(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    published_at = fields.DateTime(allow_none=True, dump_only=True)
    flagged_at = fields.DateTime(allow_none=True, dump_only=True)

    # Regular fields
    rating = fields.Float()
    body = fields.String(allow_none=True)
    status = fields.String()
    film_id = fields.Integer()
    user_id = fields.Integer()
