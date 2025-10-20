"""
Watchlist model:

Represents the association table that links users and films
for a personal watchlist.

Attributes:
    user_id (int): Foreign key to User, part of composite primary key.
    film_id (int): Foreign key to Film, part of composite primary key.
    added_at (datetime): Timestamp when the film was added to the watchlist.

Constraints:
    - Composite primary key of (user_id, film_id) ensures uniqueness.
    - CASCADE delete: removing a user or film automatically removes associated watchlist entries.

Relationships:
    - Each watchlist entry belongs to one user and one film.
    - Relationships are defined in User and Film models via back_populates.
"""

from extensions import db

class Watchlist(db.Model):
    __tablename__ = "watchlist_entries"

    # composite primary key (both must be primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True, nullable=False)
    film_id = db.Column(db.Integer, db.ForeignKey("films.id", ondelete="CASCADE"), primary_key=True, nullable=False)

    added_at = db.Column(db.DateTime, server_default=db.func.now())

    # ========== Relationships ==========
    user = db.relationship("User", back_populates="watchlist_entries")
    film = db.relationship("Film", back_populates="watchlist_entries")
