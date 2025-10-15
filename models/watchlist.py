from extensions import db

class Watchlist(db.Model):
    __tablename__ = "watchlist_entries"

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    film_id = db.Column(db.Integer, db.ForeignKey("films.id"), primary_key=True)
    added_at = db.Column(db.DateTime, server_default=db.func.now())
