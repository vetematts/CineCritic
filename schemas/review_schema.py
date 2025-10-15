# schemas/review_schema.py
from marshmallow import Schema, fields, validate, validates_schema, ValidationError

_ALLOWED_RATINGS = [x / 2 for x in range(1, 11)]  # 0.5..5.0

class ReviewCreateSchema(Schema):
    rating = fields.Float(required=True, validate=validate.OneOf(_ALLOWED_RATINGS))
    comment = fields.String(load_default=None, validate=validate.Length(max=5000))
    status = fields.String(load_default="draft", validate=validate.OneOf(["draft", "published", "flagged"]))
    user_id = fields.Integer(required=True)  # for now; will switch to current_user later
    film_id = fields.Integer(required=True)

    @validates_schema
    def _status_rules(self, data, **kwargs):
        # Simple rule: if creating as published, comment must exist
        if data.get("status") == "published" and not data.get("comment"):
            raise ValidationError({"comment": ["Comment is required when publishing."]})

class ReviewSchema(Schema):
    id = fields.Integer()
    rating = fields.Float()
    comment = fields.String(allow_none=True)
    status = fields.String()
    film_id = fields.Integer()
    user_id = fields.Integer()
    created_at = fields.DateTime()
    updated_at = fields.DateTime()
    published_at = fields.DateTime(allow_none=True)
    flagged_at = fields.DateTime(allow_none=True)
