import os
from flask import Flask
from dotenv import load_dotenv
from extensions import db, migrate, jwt

def create_app():
    load_dotenv()  # loads .env into process env
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "dev-key")

    # wire extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # import models so Alembic can "see" them for migrations
    from models import User, Film  # noqa: F401

    # tiny health route so we can test
    @app.get("/healthz")
    def health():
        return {"ok": True}, 200

    return app

# for `flask run`
app = create_app()
