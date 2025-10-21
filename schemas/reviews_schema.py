"""
Review schemas.

Defines schemas for creating and serialising Review objects.

- ReviewCreateSchema: Validates input when creating a review, including rating, body text, and status rules.
- ReviewSchema: Serializes Review objects for output, including server-managed fields.
"""
from marshmallow import Schema, fields, validate, validates_schema, ValidationError, pre_load

# Allowed ratings: 0.5 .. 5.0 in 0.5 steps
_ALLOWED_RATINGS = [x / 2 for x in range(1, 11)]  # 0.5..5.0

class ReviewCreateSchema(Schema):
    """Schema for creating a review.

    Validates user submitted fields:
    - rating: Must be between 0.5 and 5.0 in 0.5 increments.
    - body: Optional text, max 5000 chars.
    - status: One of 'draft', 'published', or 'flagged'.
    Enforces that published reviews must include a body.
    """
    # Only the fields the user should send; ids come from JWT + URL
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
    """Schema for serialising Review objects.

    Includes both user provided fields and server-managed metadata:
    - id, created_at, updated_at
    - published_at, flagged_at
    - rating, body, status, film_id, user_id
    """
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
