from extensions import db

class Watchlist(db.Model):
    __tablename__ = "watchlist_entries"

    added_at = db.Column(db.DateTime, server_default=db.func.now())

user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
film_id = db.Column(db.Integer, db.ForeignKey("films.id", ondelete="CASCADE"), primary_key=True)
