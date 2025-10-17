from marshmallow import Schema, fields, validate

class WatchlistEntrySchema(Schema):
    # user_id is managed by the server (from JWT/session)
    user_id = fields.Int(dump_only=True)

    # film_id must always be provided and valid
    film_id = fields.Int(required=True, validate=validate.Range(min=1))

    # server sets this automatically
    added_at = fields.DateTime(dump_only=True)
