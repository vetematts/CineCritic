"""
Watchlist schema.

Defines schema for serialising and validating watchlist entries.

- WatchlistEntrySchema: Ensures film_id is provided
- user_id is server-assigned, and added_at is auto-generated.
"""

from marshmallow import Schema, fields, validate

class WatchlistEntrySchema(Schema):
    """Schema for a watchlist entry.

    Fields:
    - user_id: Managed by the server (from JWT/session).
    - film_id: Required; must be a positive integer.
    - added_at: Timestamp set automatically by the server.
    """
    user_id = fields.Int(dump_only=True)
    film_id = fields.Int(required=True, validate=validate.Range(min=1))
    added_at = fields.DateTime(dump_only=True)
