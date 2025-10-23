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

    # Import models after db is setup so Alembic sees them
    import models  # noqa: F401

    # register all blueprints
    register_controllers(app)

    register_error_handlers(app)

    @app.get("/")
    def welcome():
        """Provide a quick status message for anyone hitting the root URL."""
        return {
            "message": "Welcome to CineCritic.",
            "status": "online",
            "try": {
                "films": {"method": "GET", "path": "/films"},
                "login": {"method": "POST", "path": "/auth/login"},
                "watchlist": {"method": "GET", "path": "/users/me/watchlist"},
            },
            "docs": "See the project README for full usage details.",
        }, 200

    @app.get("/healthz")
    def health():
        return {"ok": True}, 200

    return app

# for `flask run`
app = create_app()
