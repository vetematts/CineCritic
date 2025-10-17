# Installed imports
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

# Local imports
from extensions import db
from models.film import Film
from models.review import Review
from schemas.review_schema import ReviewCreateSchema, ReviewSchema

review_bp = Blueprint("reviews", __name__)      # url_prefix set in controllers/__init__.py

# Schemas
create_schema = ReviewCreateSchema()
read_schema = ReviewSchema()
read_many = ReviewSchema(many=True)


# -------------------------------------------------
# GET /films/<film_id>/reviews
# - default: published only
# - ?status=published|all
# - pagination: ?page=1&per_page=20 (1..100)
# -------------------------------------------------
@review_bp.get("")
def list_reviews(film_id: int):
    # ensure film exists
    if not db.session.get(Film, film_id):
        return {"error": "not_found", "detail": f"Film {film_id} not found"}, 404

    status = request.args.get("status", "published")
    if status not in {"published", "all"}:
        return {"error": "bad_request", "detail": "status must be 'published' or 'all'."}, 400

    # pagination guards
    try:
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 20))
    except ValueError:
        return {"error": "bad_request", "detail": "page and per_page must be integers"}, 400
    page = max(1, page)
    per_page = max(1, min(100, per_page))

    q = db.select(Review).where(Review.film_id == film_id)
    if status == "published":
        q = q.where(Review.status == "published")

    # total count for meta
    total = db.session.scalar(db.select(db.func.count()).select_from(q.subquery()))
    rows = db.session.scalars(
        q.order_by(Review.created_at.desc())
         .offset((page - 1) * per_page)
         .limit(per_page)
    ).all()

    return {
        "data": read_many.dump(rows),
        "meta": {"page": page, "per_page": per_page, "total": total}
    }, 200


# -------------------------------------------------
# POST /films/<film_id>/reviews
# - create draft or published
# - user_id comes from JWT, not the body
# -------------------------------------------------
@review_bp.post("")
@jwt_required()
def create_review(film_id: int):
    # lock film_id to path and user_id to JWT identity
    payload = request.get_json() or {}
    payload["film_id"] = film_id
    ident = get_jwt_identity()            # {"id": ..., "role": ...}
    payload["user_id"] = ident["id"]      # do NOT accept from client

    data = create_schema.load(payload)

    # enforce one review per user-film (DB unique also enforces)
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

    # Optional Location header could be added by your framework setup
    return read_schema.dump(r), 201


# -------------------------------------------------
# PATCH /films/<film_id>/reviews/<review_id>
# - partial updates via schema (keeps rules consistent)
# - author or admin only
# - guard status transitions
# -------------------------------------------------
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

    # status transition rules
    next_status = body.get("status")
    if r.status == "published" and next_status == "draft":
        return {"error": "unprocessable_entity", "detail": "Cannot revert published to draft."}, 422
    if next_status == "published" and not (body.get("body") or r.body):
        return {"error": "bad_request", "detail": "Body required when publishing."}, 400

    # use schema for validation in one place
    data = create_schema.load(body, partial=True)
    for k, v in data.items():
        setattr(r, k, v)

    # timestamps
    if r.status == "published" and not r.published_at:
        r.published_at = db.func.now()
    if r.status != "flagged":
        r.flagged_at = None

    db.session.commit()
    return read_schema.dump(r), 200


# -------------------------------------------------
# POST /films/<film_id>/reviews/<review_id>/flag
# - any logged-in user can flag
# -------------------------------------------------
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


# -------------------------------------------------
# POST /films/<film_id>/reviews/<review_id>/publish
# - author or admin only
# -------------------------------------------------
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

    if not r.body:
        return {"error": "bad_request", "detail": "Body required when publishing."}, 400

    r.status = "published"
    r.published_at = db.func.now()
    db.session.commit()
    return read_schema.dump(r), 200
