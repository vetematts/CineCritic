"""Genre model:

Represents film genres.

Attributes:
id (int): The primary key identifier for the genre.
- name (str): The unique name of the genre.

Constraints:
- name is unique and cannot be null.

Relationships:
- films (list of Film): The films associated with this genre via the film_genres junction table.
"""

from extensions import db

class Genre(db.Model):
    __tablename__ = "genres"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    # ========== Relationships ==========
    films = db.relationship("Film", secondary="film_genres", back_populates="genres")
