"""
Controller for authentication and user session management.

Handles:
  - User registration (with hashed passwords)
  - User login (returns JWT access token)
  - Fetching the current user's profile

Note:
  - Passwords are securely hashed with Werkzeug.
  - JWT identity is the user ID (string). The user's role is added via additional JWT claims.
"""

# Installed imports
from flask import Blueprint, request
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt

# Local imports
from extensions import db
from models.users import User
from schemas.users_schema import UserRegisterSchema, LoginSchema

auth_bp = Blueprint("auth", __name__)  # url_prefix set in controllers/__init__.py

# Schemas
register_schema = UserRegisterSchema()
login_schema = LoginSchema()

# ========== Admin only Routes ==========

@auth_bp.get("/users")
@jwt_required()
def list_users():
    claims = get_jwt()
    if claims.get("role") != "admin":
        return {"error": "forbidden", "detail": "Admins only"}, 403
    users = db.session.scalars(db.select(User)).all()
    return [
        {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role
        }
        for user in users
    ], 200


@auth_bp.delete("/users/<int:user_id>")
@jwt_required()
def delete_user(user_id):
    claims = get_jwt()
    if claims.get("role") != "admin":
        return {"error": "forbidden", "detail": "Admins only"}, 403
    user = db.session.get(User, user_id)
    if not user:
        return {"error": "not_found", "detail": "User not found"}, 404
    db.session.delete(user)
    db.session.commit()
    return {"message": f"User {user.username} deleted"}, 200

# ========== User Routes ==========

@auth_bp.post("/register")
def register():
    data = register_schema.load(request.get_json() or {})

    # Uniqueness hints (DB unique constraints also backstop)
    if db.session.scalar(db.select(User).filter_by(email=data["email"])):
        return {"error": "conflict", "detail": "Email already registered"}, 409
    if db.session.scalar(db.select(User).filter_by(username=data["username"])):
        return {"error": "conflict", "detail": "Username already taken"}, 409

    user = User(
        username=data["username"],
        email=data["email"],
        password_hash=generate_password_hash(data["password"])
    )
    db.session.add(user)
    db.session.commit()
    return {
        "id": user.id, "username": user.username, "email": user.email, "role": user.role
    }, 201


@auth_bp.post("/login")
def login():
    creds = login_schema.load(request.get_json() or {})
    email = creds["email"].strip().lower()  # mirrors schema normalisation; safe if schema already does it
    user = db.session.scalar(db.select(User).filter_by(email=email))
    if not user or not check_password_hash(user.password_hash, creds["password"]):
        return {"error": "unauthorised", "detail": "Invalid email or password"}, 401

    # JWT identity shaped for admin checks elsewhere
    token = create_access_token(
        identity=str(user.id),                       # subject must be string/int
        additional_claims={"role": user.role}        # custom claim for role
    )
    return {"access_token": token}, 200


@auth_bp.get("/me")
@jwt_required()
def me():
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)
    if not user:
        return {"error": "not_found", "detail": "User not found"}, 404
    return {"id": user.id, "username": user.username, "email": user.email, "role": user.role}, 200
