from flask import Blueprint, request
from extensions import db
from models.film import Film
from schemas.film_schema import FilmCreateSchema

film_bp = Blueprint("films", __name__)
create_schema = FilmCreateSchema()

@film_bp.get("")
def list_films():
    films = db.session.scalars(db.select(Film).order_by(Film.title)).all()
    return {"data":[{"id":f.id,"title":f.title,"year":f.release_year,"director":f.director} for f in films]}

@film_bp.get("/<int:film_id>")
def get_film(film_id):
    f = db.session.get(Film, film_id)
    if not f:
        return {"error":"not_found","detail":f"Film {film_id} not found"}, 404
    return {"id":f.id,"title":f.title,"year":f.release_year,"director":f.director,"description":f.description}

@film_bp.post("")
def create_film():
    data = create_schema.load(request.get_json() or {})
    f = Film(**data)
    db.session.add(f); db.session.commit()
    return {"id": f.id, "title": f.title, "year": f.release_year}, 201

@film_bp.patch("/<int:film_id>")
def update_film(film_id):
    f = db.session.get(Film, film_id)
    if not f:
        return {"error":"not_found","detail":f"Film {film_id} not found"}, 404
    data = create_schema.load(request.get_json() or {}, partial=True)
    for k,v in data.items(): setattr(f, k, v)
    db.session.commit()
    return {"id": f.id, "title": f.title, "year": f.release_year}

@film_bp.delete("/<int:film_id>")
def delete_film(film_id):
    f = db.session.get(Film, film_id)
    if not f:
        return {"error":"not_found","detail":f"Film {film_id} not found"}, 404
    db.session.delete(f); db.session.commit()
    return "", 204
