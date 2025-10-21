"""
Controller for the current user's watchlist.

Handles:
  - List watchlist entries (with pagination)
  - Add a film to the watchlist
  - Remove a film from the watchlist

Note:
  - ValidationError and IntegrityError are handled globally in utils.error_handlers.
"""

# Installed imports
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

# Local imports
from extensions import db
from models.watchlist import Watchlist
from models.film import Film
from schemas.watchlists_schema import WatchlistEntrySchema

watchlist_bp = Blueprint("watchlist", __name__)     # url_prefix set in controllers/__init__.py

# Schemas
schema = WatchlistEntrySchema()
read_many = WatchlistEntrySchema(many=True)

# -------------------------------
# Watchlist for current user
# -------------------------------

def _current_user_id():
    ident = get_jwt_identity()
    if isinstance(ident, dict):
        return ident["id"]
    return int(ident)

 # ========= LIST WATCHLIST =========
@watchlist_bp.get("")
@jwt_required()
def list_watchlist():
    """List the current user's watchlist entries (supports ?page & ?per_page)."""
    user_id = _current_user_id()

    # pagination guards
    try:
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 20))
    except ValueError:
        return {"error": "bad_request", "detail": "page and per_page must be integers"}, 400
    page = max(1, page)
    per_page = max(1, min(100, per_page))

    base = db.select(Watchlist).where(Watchlist.user_id == user_id)
    total = db.session.scalar(db.select(db.func.count()).select_from(base.subquery()))
    rows = db.session.scalars(
        base.order_by(Watchlist.added_at.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
    ).all()

    return {
        "data": read_many.dump(rows),
        "meta": {"page": page, "per_page": per_page, "total": total}
    }, 200


 # ========= ADD TO WATCHLIST =========
@watchlist_bp.post("")
@jwt_required()
def add_to_watchlist():
    """Add a film to the current user's watchlist."""
    user_id = _current_user_id()
    payload = request.get_json() or {}

    # basic input check
    film_id = payload.get("film_id")
    if not isinstance(film_id, int):
        return {"error": "bad_request", "detail": "film_id must be an integer"}, 400

    # existence + uniqueness
    if not db.session.get(Film, film_id):
        return {"error": "not_found", "detail": f"Film {film_id} not found"}, 404
    if db.session.get(Watchlist, (user_id, film_id)):
        return {"error": "conflict", "detail": "Already in watchlist"}, 409

    entry = Watchlist(user_id=user_id, film_id=film_id)
    db.session.add(entry)
    db.session.commit()
    return schema.dump(entry), 201


 # ========= REMOVE FROM WATCHLIST =========
@watchlist_bp.delete("/<int:film_id>")
@jwt_required()
def remove_from_watchlist(film_id: int):
    """Remove a film from the current user's watchlist."""
    user_id = _current_user_id()
    entry = db.session.get(Watchlist, (user_id, film_id))
    if not entry:
        return {"error": "not_found", "detail": "Not in watchlist"}, 404
    db.session.delete(entry)
    db.session.commit()
    return "", 204
