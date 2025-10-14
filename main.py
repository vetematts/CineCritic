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

    # ensure models are registered for migrations
    import models  # noqa: F401

    # register all blueprints
    from controllers import register_controllers
    register_controllers(app)

    from utils.error_handlers import register_error_handlers
    register_error_handlers(app)

    # tiny health route so we can test
    @app.get("/healthz")
    def health():
        return {"ok": True}, 200

    return app

# for `flask run`
app = create_app()
