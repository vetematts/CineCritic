"""
Controller for Film-related routes.

Handles:
  - List films (filters + pagination)
  - Get one film
  - Create a film (admin only)
  - Update a film (admin only)
  - Delete a film (admin only)
  - Manage film ↔ genre links (admin only)

Note:
  - ValidationError and IntegrityError are handled globally in utils.error_handlers.
"""

# Installed imports
from flask import Blueprint, request, abort
from flask_jwt_extended import jwt_required, get_jwt

# Local imports
from extensions import db
from models.film import Film
from models.genre import Genre
from models.film_genre import FilmGenre
from schemas.film_schema import FilmCreateSchema, FilmSchema
from schemas.genre_schema import GenreSchema

film_bp = Blueprint("films", __name__)      # url_prefix set in controllers/__init__.py

# Schemas
create_schema = FilmCreateSchema()
read_schema = FilmSchema()
read_many_schema = FilmSchema(many=True)
genres_read_many = GenreSchema(many=True)

# ========= HELPERS =========

def _require_admin():
    claims = get_jwt()
    role = claims.get("role")
    if role != "admin":
        abort(403)
    return None

# ========= LIST FILMS =========
@film_bp.get("")
def list_films():
    """List films with optional filters and pagination."""
    # parse pagination
    try:
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 20))
    except ValueError:
        return {"error": "bad_request", "detail": "page and per_page must be integers"}, 400
    page = max(1, page)
    per_page = max(1, min(per_page, 100))

    # base select
    stmt = db.select(Film)

    # filters
    title = (request.args.get("title") or "").strip()
    if title:
        stmt = stmt.where(Film.title.ilike(f"%{title}%"))

    year = request.args.get("year")
    if year is not None and year != "":
        try:
            year_int = int(year)
            stmt = stmt.where(Film.release_year == year_int)
        except ValueError:
            return {"error": "bad_request", "detail": "year must be an integer"}, 400

    director = (request.args.get("director") or "").strip()
    if director:
        stmt = stmt.where(Film.director.ilike(f"%{director}%"))

    # optional genre filter
    genre_id = request.args.get("genre_id")
    if genre_id is not None and genre_id != "":
        try:
            gid = int(genre_id)
        except ValueError:
            return {"error": "bad_request", "detail": "genre_id must be an integer"}, 400
        # join via junction table
        stmt = (
            stmt.join(FilmGenre, FilmGenre.film_id == Film.id)
                .where(FilmGenre.genre_id == gid)
        )

    # sort and paginate
    stmt = stmt.order_by(Film.title.asc())
    pager = db.paginate(stmt, page=page, per_page=per_page, error_out=False)

    return {
        "data": read_many_schema.dump(pager.items),
        "meta": {"page": page, "per_page": per_page, "total": pager.total, "pages": pager.pages}
    }, 200

# ========= GET ONE FILM =========
@film_bp.get("/<int:film_id>")
def get_film(film_id: int):
    """Fetch a single film by id."""
    f = db.session.get(Film, film_id)
    if not f:
        return {"error": "not_found", "detail": f"Film {film_id} not found"}, 404
    return read_schema.dump(f), 200

# ========= CREATE FILM =========
@film_bp.post("")
@jwt_required()
def create_film():
    """Create a film (validated by schema). Admin only."""
    err = _require_admin()
    if err: return err

    data = create_schema.load(request.get_json() or {})
    f = Film(**data)
    db.session.add(f)
    db.session.commit()
    return read_schema.dump(f), 201

# ========= UPDATE FILM =========
@film_bp.patch("/<int:film_id>")
@jwt_required()
def update_film(film_id: int):
    """Patch fields on a film. Admin only."""
    err = _require_admin()
    if err: return err

    f = db.session.get(Film, film_id)
    if not f:
        return {"error": "not_found", "detail": f"Film {film_id} not found"}, 404

    data = create_schema.load(request.get_json() or {}, partial=True)
    for k, v in data.items():
        setattr(f, k, v)

    db.session.commit()
    return read_schema.dump(f), 200

# ========= DELETE FILM =========
@film_bp.delete("/<int:film_id>")
@jwt_required()
def delete_film(film_id: int):
    """Delete a film. Admin only."""
    err = _require_admin()
    if err: return err

    f = db.session.get(Film, film_id)
    if not f:
        return {"error": "not_found", "detail": f"Film {film_id} not found"}, 404
    db.session.delete(f)
    db.session.commit()
    return "", 204


# -------------------------------
# Film ↔ Genre junction endpoints
# (pure M:N via models/film_genre)
# -------------------------------

# ========= LIST FILM GENRES =========
@film_bp.get("/<int:film_id>/genres")
def list_film_genres(film_id: int):
    """List genres attached to a film."""
    if not db.session.get(Film, film_id):
        return {"error": "not_found", "detail": f"Film {film_id} not found"}, 404

    rows = (
        db.session.query(Genre)
        .join(FilmGenre, FilmGenre.genre_id == Genre.id)
        .filter(FilmGenre.film_id == film_id)
        .order_by(Genre.name)
        .all()
    )
    return {"data": genres_read_many.dump(rows)}, 200

# ========= ATTACH GENRE =========
@film_bp.post("/<int:film_id>/genres/<int:genre_id>")
@jwt_required()
def attach_genre(film_id: int, genre_id: int):
    """Attach a genre to a film. Admin only."""
    err = _require_admin()
    if err: return err

    if not db.session.get(Film, film_id):
        return {"error": "not_found", "detail": f"Film {film_id} not found"}, 404
    if not db.session.get(Genre, genre_id):
        return {"error": "not_found", "detail": f"Genre {genre_id} not found"}, 404
    if db.session.get(FilmGenre, (film_id, genre_id)):
        return {"error": "conflict", "detail": "Genre already attached"}, 409

    db.session.add(FilmGenre(film_id=film_id, genre_id=genre_id))
    db.session.commit()
    return "", 204

# ========= DETACH GENRE =========
@film_bp.delete("/<int:film_id>/genres/<int:genre_id>")
@jwt_required()
def detach_genre(film_id: int, genre_id: int):
    """Detach a genre from a film. Admin only."""
    err = _require_admin()
    if err: return err

    row = db.session.get(FilmGenre, (film_id, genre_id))
    if not row:
        return {"error": "not_found", "detail": "Relation not found"}, 404
    db.session.delete(row)
    db.session.commit()
    return "", 204
