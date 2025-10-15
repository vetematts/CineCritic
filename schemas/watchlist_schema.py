from marshmallow import Schema, fields

class WatchlistEntrySchema(Schema):
    user_id = fields.Int(dump_only=True)
    film_id = fields.Int(required=True)
    added_at = fields.DateTime(dump_only=True)
