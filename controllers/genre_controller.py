# Installed imports
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

# Local imports
from extensions import db
from models.genre import Genre
from schemas.genre_schema import GenreCreateSchema, GenreSchema

genre_bp = Blueprint("genres", __name__)  # url_prefix set in controllers/__init__.py

# Schemas
create_schema = GenreCreateSchema()
read_schema = GenreSchema()
read_many = GenreSchema(many=True)

# ---- helpers ---------------------------------------------------
# -------------------------------
# Genre CRUD
# -------------------------------

def _require_admin():
    ident = get_jwt_identity()
    if not ident or ident.get("role") != "admin":
        return {"error": "forbidden", "detail": "Admin only"}, 403
    return None

# ---- routes ----------------------------------------------------

@genre_bp.get("")
def list_genres():
    rows = db.session.scalars(db.select(Genre).order_by(Genre.name)).all()
    return {"data": read_many.dump(rows)}, 200

@genre_bp.post("")
@jwt_required()
def create_genre():
    err = _require_admin()
    if err:
        return err
    payload = request.get_json() or {}
    data = create_schema.load(payload)
    g = Genre(**data)
    db.session.add(g)
    db.session.commit()
    return read_schema.dump(g), 201

@genre_bp.delete("/<int:genre_id>")
@jwt_required()
def delete_genre(genre_id: int):
    err = _require_admin()
    if err:
        return err
    g = db.session.get(Genre, genre_id)
    if not g:
        return {"error": "not_found", "detail": f"Genre {genre_id} not found"}, 404
    db.session.delete(g)
    db.session.commit()
    return "", 204
