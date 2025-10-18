"""
Controller for Review-related routes and logic.
Handles all CRUD operations and state changes for reviews:
    - List reviews for a film
    - Get one review
    - Create a new review
    - Update an existing review
    - Delete a review
    - Publish or flag a review

Note:
    - IntegrityError and ValidationError are handled globally in utils.error_handlers.
"""
# Installed imports
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import Schema, fields, validate, ValidationError

# Local imports
from extensions import db
from models.review import Review
from models.film import Film
from schemas.review_schema import ReviewCreateSchema, ReviewSchema

review_bp = Blueprint("reviews", __name__)    # url_prefix set in controllers/__init__.py

# Schemas
create_schema = ReviewCreateSchema()
read_schema = ReviewSchema()
read_many = ReviewSchema(many=True)

# Update schema (do NOT allow film_id/user_id edits on PATCH)
class ReviewUpdateSchema(Schema):
    rating = fields.Float(validate=validate.OneOf([x / 2 for x in range(1, 11)]))  # 0.5..5.0
    body = fields.String(allow_none=True, validate=validate.Length(max=5000))
    status = fields.String(validate=validate.OneOf(["draft", "published", "flagged"]))

update_schema = ReviewUpdateSchema()


# -------------------------------
# Helpers
# -------------------------------
def _current_user():
    """Return {'id': int, 'role': 'user'|'admin'} or None."""
    try:
        return get_jwt_identity()
    except Exception:
        return None

def _is_admin(identity):
    return bool(identity and identity.get("role") == "admin")

def _ensure_film_or_404(film_id):
    if not db.session.get(Film, film_id):
        return {"error": "not_found", "detail": f"Film {film_id} not found"}, 404
    return None


# ========= LIST REVIEWS =========
# GET /films/<film_id>/reviews
@review_bp.get("")
def list_reviews(film_id: int):
    # 404 if film missing
    err = _ensure_film_or_404(film_id)
    if err:
        return err

    # pagination
    try:
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 20))
    except ValueError:
        return {"error": "bad_request", "detail": "page and per_page must be integers"}, 400
    page = max(1, page)
    per_page = max(1, min(per_page, 100))

    # Only published reviews are public
    stmt = (
        db.select(Review)
        .where(Review.film_id == film_id, Review.status == "published")
        .order_by(Review.created_at.desc())
    )
    pager = db.paginate(stmt, page=page, per_page=per_page, error_out=False)

    return {
        "data": read_many.dump(pager.items),
        "meta": {"page": page, "per_page": per_page, "total": pager.total, "pages": pager.pages},
    }, 200


# ========= CREATE NEW REVIEW =========
# POST /films/<film_id>/reviews
@review_bp.post("")
@jwt_required()
def create_review(film_id: int):
    # 404 if film missing
    err = _ensure_film_or_404(film_id)
    if err:
        return err

    ident = _current_user()
    data = create_schema.load(request.get_json() or {})

    # Enforce ownership + film from context (don’t trust body)
    new_review = Review(
        film_id=film_id,
        user_id=ident["id"],
        rating=data["rating"],
        body=data.get("body"),
        status=data.get("status", "draft"),
    )

    # If creating as published, set published_at
    if new_review.status == "published":
        new_review.published_at = db.func.now()

    try:
        db.session.add(new_review)
        db.session.commit()
    except Exception as e:
        # rely on global error handlers for IntegrityError, etc., if configured
        db.session.rollback()
        raise e

    return read_schema.dump(new_review), 201


# ========= GET ONE REVIEW =========
# GET /films/<film_id>/reviews/<review_id>
@review_bp.get("/<int:review_id>")
def get_review(film_id: int, review_id: int):
    err = _ensure_film_or_404(film_id)
    if err:
        return err

    r = db.session.get(Review, review_id)
    if not r or r.film_id != film_id:
        return {"error": "not_found", "detail": "Review not found"}, 404

    ident = _current_user()
    if r.status != "published":
        # allow if owner or admin
        if not ident or (ident["id"] != r.user_id and not _is_admin(ident)):
            return {"error": "forbidden", "detail": "Not allowed to view this review"}, 403

    return read_schema.dump(r), 200


# ========= UPDATE REVIEW =========
# PATCH /films/<film_id>/reviews/<review_id>
@review_bp.patch("/<int:review_id>")
@jwt_required()
def update_review(film_id: int, review_id: int):
    err = _ensure_film_or_404(film_id)
    if err:
        return err

    r = db.session.get(Review, review_id)
    if not r or r.film_id != film_id:
        return {"error": "not_found", "detail": "Review not found"}, 404

    ident = _current_user()
    if ident["id"] != r.user_id and not _is_admin(ident):
        return {"error": "forbidden", "detail": "Only the author or admin can edit"}, 403

    payload = request.get_json() or {}
    data = update_schema.load(payload, partial=True)

    # Don’t allow changing film_id/user_id even if sent
    if "film_id" in payload or "user_id" in payload:
        return {"error": "bad_request", "detail": "film_id and user_id cannot be changed"}, 400

    # Apply allowed fields
    for k in ("rating", "body", "status"):
        if k in data:
            setattr(r, k, data[k])

    # Status-side effects
    if "status" in data:
        next_status = data["status"]
        # prevent reverting published → draft (business rule)
        if r.status == "published" and next_status == "draft":
            return {"error": "conflict", "detail": "Cannot revert a published review to draft"}, 409
        if next_status == "published" and not (data.get("body") or r.body):
            return {"error": "bad_request", "detail": "Body required when publishing."}, 400
        if next_status == "published" and not r.published_at:
            r.published_at = db.func.now()
        if next_status == "flagged" and not r.flagged_at:
            r.flagged_at = db.func.now()

    db.session.commit()
    return read_schema.dump(r), 200


# ========= DELETE REVIEW =========
# DELETE /films/<film_id>/reviews/<review_id>
@review_bp.delete("/<int:review_id>")
@jwt_required()
def delete_review(film_id: int, review_id: int):
    err = _ensure_film_or_404(film_id)
    if err:
        return err

    r = db.session.get(Review, review_id)
    if not r or r.film_id != film_id:
        return {"error": "not_found", "detail": "Review not found"}, 404

    ident = _current_user()
    if ident["id"] != r.user_id and not _is_admin(ident):
        return {"error": "forbidden", "detail": "Only the author or admin can delete"}, 403

    db.session.delete(r)
    db.session.commit()
    return "", 204


# ========= PUBLISH REVIEW =========
# POST /films/<film_id>/reviews/<review_id>/publish
@review_bp.post("/<int:review_id>/publish")
@jwt_required()
def publish_review(film_id: int, review_id: int):
    err = _ensure_film_or_404(film_id)
    if err:
        return err

    r = db.session.get(Review, review_id)
    if not r or r.film_id != film_id:
        return {"error": "not_found", "detail": "Review not found"}, 404

    ident = _current_user()
    if ident["id"] != r.user_id and not _is_admin(ident):
        return {"error": "forbidden", "detail": "Only the author or admin can publish"}, 403

    if not r.body:
        return {"error": "bad_request", "detail": "Body required when publishing."}, 400

    r.status = "published"
    if not r.published_at:
        r.published_at = db.func.now()
    db.session.commit()
    return read_schema.dump(r), 200


# ========= FLAG REVIEW =========
# POST /films/<film_id>/reviews/<review_id>/flag
@review_bp.post("/<int:review_id>/flag")
@jwt_required()
def flag_review(film_id: int, review_id: int):
    err = _ensure_film_or_404(film_id)
    if err:
        return err

    r = db.session.get(Review, review_id)
    if not r or r.film_id != film_id:
        return {"error": "not_found", "detail": "Review not found"}, 404

    # Anyone logged in can flag
    r.status = "flagged"
    if not r.flagged_at:
        r.flagged_at = db.func.now()
    db.session.commit()
    return read_schema.dump(r), 200
