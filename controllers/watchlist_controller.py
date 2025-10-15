from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models.watchlist import Watchlist
from models.film import Film
from schemas.watchlist_schema import WatchlistEntrySchema

watchlist_bp = Blueprint("watchlist", __name__, url_prefix="/users/me/watchlist")

schema = WatchlistEntrySchema()
read_many = WatchlistEntrySchema(many=True)

@watchlist_bp.get("")
@jwt_required()
def list_watchlist():
    ident = get_jwt_identity()
    rows = db.session.scalars(
        db.select(Watchlist).where(Watchlist.user_id == ident["id"])
    ).all()
    return {"data": read_many.dump(rows)}, 200

@watchlist_bp.post("")
@jwt_required()
def add_to_watchlist():
    ident = get_jwt_identity()
    payload = request.get_json() or {}
    film_id = payload.get("film_id")
    if not db.session.get(Film, film_id):
        return {"error": "not_found", "detail": f"Film {film_id} not found"}, 404

    if db.session.get(Watchlist, (ident["id"], film_id)):
        return {"error": "conflict", "detail": "Already in watchlist"}, 409

    entry = Watchlist(user_id=ident["id"], film_id=film_id)
    db.session.add(entry)
    db.session.commit()
    return schema.dump(entry), 201

@watchlist_bp.delete("/<int:film_id>")
@jwt_required()
def remove_from_watchlist(film_id):
    ident = get_jwt_identity()
    entry = db.session.get(Watchlist, (ident["id"], film_id))
    if not entry:
        return {"error": "not_found", "detail": "Not in watchlist"}, 404
    db.session.delete(entry)
    db.session.commit()
    return "", 204
