from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager

db = SQLAlchemy()     # ORM (models <-> Postgres)
migrate = Migrate()   # Alembic migrations
jwt = JWTManager()    # JWT auth 
