# Installed imports
from flask import Blueprint, request
from sqlalchemy.exc import IntegrityError
from marshmallow import ValidationError
from flask_jwt_extended import jwt_required, get_jwt_identity

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

# --- helpers ----------------------------------------------------

def _require_admin():
    ident = get_jwt_identity()
    if not ident or ident.get("role") != "admin":
        return {"error": "forbidden", "detail": "Admin only"}, 403
    return None

# -------------------------------
# Film CRUD
# -------------------------------

@film_bp.get("")
def list_films():
    """List films ordered by title."""
    rows = db.session.scalars(db.select(Film).order_by(Film.title)).all()
    return {"data": read_many_schema.dump(rows)}, 200


@film_bp.get("/<int:film_id>")
def get_film(film_id: int):
    """Fetch a single film by id."""
    f = db.session.get(Film, film_id)
    if not f:
        return {"error": "not_found", "detail": f"Film {film_id} not found"}, 404
    return read_schema.dump(f), 200


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
