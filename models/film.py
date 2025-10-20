"""Film model definition.

Represents a film in the CineCritic database. Each film can have multiple reviews,
be linked to multiple genres, and appear in users’ watchlists.

Constraints:
    - Unique combination of title and release year.
Relationships:
    - One-to-many with Review (deletes cascade).
    - Many-to-many with Genre via film_genres.
    - One-to-many with Watchlist entries (deletes cascade).
"""
from extensions import db

class Film(db.Model):
    __tablename__ = "films"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    release_year = db.Column(db.Integer)
    director = db.Column(db.String(100))
    description = db.Column(db.Text)

    # ========== Relationships ==========
    reviews = db.relationship("Review", back_populates="film", cascade="all, delete-orphan")
    genres = db.relationship("Genre", secondary="film_genres", back_populates="films")
    watchlist_entries = db.relationship("Watchlist", back_populates="film", cascade="all, delete-orphan")

    __table_args__ = (
        db.UniqueConstraint("title", "release_year", name="uq_film_title_year"),
    )
