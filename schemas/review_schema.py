from marshmallow import Schema, fields, validate, validates_schema, ValidationError, pre_load

# Allowed ratings: 0.5 .. 5.0 in 0.5 steps
_ALLOWED_RATINGS = [x / 2 for x in range(1, 11)]  # 0.5..5.0

class ReviewCreateSchema(Schema):
    # Only the fields the client should send; ids come from JWT + URL
    rating = fields.Float(required=True, validate=validate.OneOf(_ALLOWED_RATINGS))
    body   = fields.String(load_default=None, validate=validate.Length(max=5000))
    status = fields.String(load_default="draft", validate=validate.OneOf(["draft", "published", "flagged"]))

    @pre_load
    def _trim_strings(self, in_data, **kwargs):
        # Normalise whitespace so "   " doesn't sneak past validation
        data = dict(in_data or {})
        for key in ("body", "status"):
            val = data.get(key)
            if isinstance(val, str):
                data[key] = val.strip()
        return data

    @validates_schema
    def _status_rules(self, data, **kwargs):
        # If creating as published, body must exist
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
