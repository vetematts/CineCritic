# controllers/review_controller.py
from flask import Blueprint, request
from extensions import db
from models.film import Film
from models.review import Review
from schemas.review_schema import ReviewCreateSchema, ReviewSchema

review_bp = Blueprint("reviews", __name__)  # registered with url_prefix in controllers/__init__.py

create_schema = ReviewCreateSchema()
read_schema = ReviewSchema()
read_many = ReviewSchema(many=True)

# GET /films/<film_id>/reviews  → list published by default (add ?status=all to see drafts once auth added)
@review_bp.get("")
def list_reviews(film_id: int):
    # ensure film exists
    if not db.session.get(Film, film_id):
        return {"error": "not_found", "detail": f"Film {film_id} not found"}, 404

    status = request.args.get("status", "published")
    stmt = db.select(Review).where(Review.film_id == film_id)
    if status != "all":
        stmt = stmt.where(Review.status == "published")
    rows = db.session.scalars(stmt.order_by(Review.created_at.desc())).all()
    return {"data": read_many.dump(rows)}, 200

# POST /films/<film_id>/reviews  → create draft or published
@review_bp.post("")
def create_review(film_id: int):
    payload = request.get_json() or {}
    payload["film_id"] = film_id  # lock to path variable
    data = create_schema.load(payload)

    # enforce one review per user-film (also enforced by DB unique)
    exists = db.session.scalar(
        db.select(Review).where(Review.film_id == data["film_id"], Review.user_id == data["user_id"])
    )
    if exists:
        return {"error": "conflict", "detail": "You have already reviewed this film."}, 409

    r = Review(**data)
    if r.status == "published":
        r.published_at = db.func.now()

    db.session.add(r)
    db.session.commit()
    return read_schema.dump(r), 201

# PATCH /reviews/<review_id>  → update rating/comment/status (basic flow without auth)
@review_bp.patch("/<int:review_id>")
def update_review(review_id: int):
    r = db.session.get(Review, review_id)
    if not r:
        return {"error": "not_found", "detail": f"Review {review_id} not found"}, 404

    body = request.get_json() or {}
    # very light validation reuse
    if "rating" in body and body["rating"] not in [x / 2 for x in range(1, 11)]:
        return {"error": "bad_request", "detail": "Invalid rating value."}, 400
    if "status" in body and body["status"] not in ["draft", "published", "flagged"]:
        return {"error": "bad_request", "detail": "Invalid status."}, 400

    # naive workflow rules (tighten once auth is in)
    prev = r.status
    for k in ("rating", "comment", "status"):
        if k in body:
            setattr(r, k, body[k])

    if prev != "published" and r.status == "published" and not r.published_at:
        r.published_at = db.func.now()
    if r.status != "flagged":
        r.flagged_at = None

    db.session.commit()
    return read_schema.dump(r), 200

# POST /reviews/<review_id>/flag  → mark for moderation
@review_bp.post("/<int:review_id>/flag")
def flag_review(review_id: int):
    r = db.session.get(Review, review_id)
    if not r:
        return {"error": "not_found", "detail": f"Review {review_id} not found"}, 404
    r.status = "flagged"
    r.flagged_at = db.func.now()
    db.session.commit()
    return read_schema.dump(r), 200

# POST /reviews/<review_id>/publish  → convenience endpoint
@review_bp.post("/<int:review_id>/publish")
def publish_review(review_id: int):
    r = db.session.get(Review, review_id)
    if not r:
        return {"error": "not_found", "detail": f"Review {review_id} not found"}, 404
    r.status = "published"
    r.published_at = db.func.now()
    db.session.commit()
    return read_schema.dump(r), 200
