# controllers/genre_controller.py
from flask import Blueprint, request
from extensions import db
from models.genre import Genre
from marshmallow import ValidationError
from schemas.genre_schema import GenreCreateSchema, GenreSchema

genre_bp = Blueprint("genres", __name__)  # url_prefix is set when registering the blueprint

# Schemas
create_schema = GenreCreateSchema()
read_schema = GenreSchema()
read_many_schema = GenreSchema(many=True)

@genre_bp.get("")
def list_genres():
    """GET /genres — list all genres."""
    rows = db.session.scalars(db.select(Genre).order_by(Genre.name)).all()
    return {"data": read_many_schema.dump(rows)}, 200

@genre_bp.post("")
def create_genre():
    """POST /genres — create a genre."""
    payload = request.get_json() or {}
    data = create_schema.load(payload)  # validates { "name": "..." }
    g = Genre(**data)
    db.session.add(g)
    db.session.commit()
    return read_schema.dump(g), 201

@genre_bp.delete("/<int:genre_id>")
def delete_genre(genre_id: int):
    """DELETE /genres/<genre_id> — delete a genre."""
    g = db.session.get(Genre, genre_id)
    if not g:
        return {"error": "not_found", "detail": f"Genre {genre_id} not found"}, 404
    db.session.delete(g)
    db.session.commit()
    return "", 204
