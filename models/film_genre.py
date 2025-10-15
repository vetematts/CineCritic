from extensions import db

class FilmGenre(db.Model):
    __tablename__ = "film_genres"
    film_id  = db.Column(db.Integer, db.ForeignKey("films.id", ondelete="CASCADE"), primary_key=True)
    genre_id = db.Column(db.Integer, db.ForeignKey("genres.id", ondelete="CASCADE"), primary_key=True)
