# models/film.py
from extensions import db

class Film(db.Model):
    __tablename__ = "films"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    release_year = db.Column(db.Integer)
    director = db.Column(db.String(100))
    description = db.Column(db.Text)
    __table_args__ = (db.UniqueConstraint("title", "release_year", name="uq_film_title_year"),)
