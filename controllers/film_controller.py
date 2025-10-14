from flask import Blueprint, request
from extensions import db
from models.film import Film

film_bp = Blueprint("films", __name__)

@film_bp.get("")
def list_films():
    films = db.session.scalars(db.select(Film).order_by(Film.title)).all()
    return {"data":[{"id":f.id,"title":f.title,"year":f.release_year} for f in films]}

@film_bp.post("")
def create_film():
    j = request.get_json() or {}
    f = Film(title=j.get("title"), release_year=j.get("release_year"), director=j.get("director"))
    db.session.add(f); db.session.commit()
    return {"id": f.id, "title": f.title}, 201
