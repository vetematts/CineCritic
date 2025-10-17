# Installed imports
from flask import Blueprint, request
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

# Local imports
from extensions import db
from models.users import User
from schemas.users_schema import UserRegisterSchema, LoginSchema

auth_bp = Blueprint("auth", __name__)  # url_prefix set in controllers/__init__.py

# Schemas
register_schema = UserRegisterSchema()
login_schema = LoginSchema()

# --- routes ----------------------------------------------------

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
    token = create_access_token(identity={"id": user.id, "role": user.role})
    return {"access_token": token}, 200


@auth_bp.get("/me")
@jwt_required()
def me():
    ident = get_jwt_identity()  # {"id":..., "role":...}
    user = db.session.get(User, ident["id"])
    if not user:
        return {"error": "not_found", "detail": "User not found"}, 404
    return {
        "id": user.id, "username": user.username, "email": user.email, "role": user.role
    }, 200
