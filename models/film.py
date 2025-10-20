from extensions import db

class Film(db.Model):
    __tablename__ = "films"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    release_year = db.Column(db.Integer)
    director = db.Column(db.String(100))
    description = db.Column(db.Text)

    # --- relationships ---
    reviews = db.relationship("Review", back_populates="film", cascade="all, delete-orphan")
    genres = db.relationship("Genre", secondary="film_genres", back_populates="films")
    watchlist_entries = db.relationship("Watchlist", back_populates="film", cascade="all, delete-orphan")

    __table_args__ = (
        db.UniqueConstraint("title", "release_year", name="uq_film_title_year"),
    )
