"""FilmGenre model definition.

Contains the FilmGenre junction table that represents the many-to-many
relationship between films and genres.

Junction table linking films and genres.

Attributes:
- film_id (int): Foreign key to Film.
- genre_id (int): Foreign key to Genre.

Constraints:
- Composite primary key of (film_id, genre_id) to ensure uniqueness.
- CASCADE delete: removing a film or genre deletes associated links.

Relationships:
- Relationships are defined in Film and Genre models via back_populates
"""

from extensions import db

class FilmGenre(db.Model):
    __tablename__ = "film_genres"
    film_id  = db.Column(db.Integer, db.ForeignKey("films.id", ondelete="CASCADE"), primary_key=True)
    genre_id = db.Column(db.Integer, db.ForeignKey("genres.id", ondelete="CASCADE"), primary_key=True)
