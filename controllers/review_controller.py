# controllers/review_controller.py
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models.film import Film
from models.review import Review
from schemas.review_schema import ReviewCreateSchema, ReviewSchema

review_bp = Blueprint("reviews", __name__)  # mounted at /films/<int:film_id>/reviews

create_schema = ReviewCreateSchema()
read_schema = ReviewSchema()
read_many = ReviewSchema(many=True)

# GET /films/<film_id>/reviews  → list published by default (?status=all to include drafts/flagged later)
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
@jwt_required()
def create_review(film_id: int):
    # lock film_id to path and user_id to JWT identity
    payload = request.get_json() or {}
    payload["film_id"] = film_id
    ident = get_jwt_identity()            # {"id": ..., "role": ...}
    payload["user_id"] = ident["id"]      # do NOT accept from client

    data = create_schema.load(payload)

    # enforce one review per user-film (also enforced by DB unique)
    exists = db.session.scalar(
        db.select(Review).where(
            Review.film_id == data["film_id"],
            Review.user_id == data["user_id"]
        )
    )
    if exists:
        return {"error": "conflict", "detail": "You have already reviewed this film."}, 409

    r = Review(**data)
    if r.status == "published":
        r.published_at = db.func.now()

    db.session.add(r)
    db.session.commit()
    return read_schema.dump(r), 201

# PATCH /films/<film_id>/reviews/<review_id> → update rating/comment/status
@review_bp.patch("/<int:review_id>")
@jwt_required()
def update_review(film_id: int, review_id: int):
    r = db.session.get(Review, review_id)
    if not r:
        return {"error": "not_found", "detail": f"Review {review_id} not found"}, 404
    if r.film_id != film_id:
        return {"error": "not_found", "detail": "Review does not belong to this film"}, 404

    ident = get_jwt_identity()
    if ident["role"] != "admin" and r.user_id != ident["id"]:
        return {"error": "forbidden", "detail": "Not your review"}, 403

    body = request.get_json() or {}

    # light validation without reusing the full create schema
    if "rating" in body and body["rating"] not in [x / 2 for x in range(1, 11)]:
        return {"error": "bad_request", "detail": "Invalid rating value."}, 400
    if "status" in body and body["status"] not in ["draft", "published", "flagged"]:
        return {"error": "bad_request", "detail": "Invalid status."}, 400

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

# POST /films/<film_id>/reviews/<review_id>/flag → mark for moderation (any logged-in user can flag)
@review_bp.post("/<int:review_id>/flag")
@jwt_required()
def flag_review(film_id: int, review_id: int):
    r = db.session.get(Review, review_id)
    if not r:
        return {"error": "not_found", "detail": f"Review {review_id} not found"}, 404
    if r.film_id != film_id:
        return {"error": "not_found", "detail": "Review does not belong to this film"}, 404

    r.status = "flagged"
    r.flagged_at = db.func.now()
    db.session.commit()
    return read_schema.dump(r), 200

# POST /films/<film_id>/reviews/<review_id>/publish → convenience for author/admin
@review_bp.post("/<int:review_id>/publish")
@jwt_required()
def publish_review(film_id: int, review_id: int):
    r = db.session.get(Review, review_id)
    if not r:
        return {"error": "not_found", "detail": f"Review {review_id} not found"}, 404
    if r.film_id != film_id:
        return {"error": "not_found", "detail": "Review does not belong to this film"}, 404

    ident = get_jwt_identity()
    if ident["role"] != "admin" and r.user_id != ident["id"]:
        return {"error": "forbidden", "detail": "Not your review"}, 403

    r.status = "published"
    r.published_at = db.func.now()
    db.session.commit()
    return read_schema.dump(r), 200
