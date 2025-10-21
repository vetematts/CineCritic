# Built-in imports
import os

# Installed imports
from flask import Flask
from dotenv import load_dotenv

# Local imports
from extensions import db, migrate, jwt
from controllers import register_controllers
from utils.error_handlers import register_error_handlers

load_dotenv()

def create_app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
    # disable object change tracking to save memory
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "dev-key")
    # To keep the order of keys in JSON response
    app.json.sort_keys = False

    # wire extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # Ensure models are registered for Alembic migrations
    import models  # noqa: F401

    # register all blueprints
    register_controllers(app)

    register_error_handlers(app)

    @app.get("/healthz")
    def health():
        return {"ok": True}, 200

    return app

# for `flask run`
app = create_app()
