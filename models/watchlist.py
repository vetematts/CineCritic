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
