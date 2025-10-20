"""User model:

Represents a registered user in the CineCritic application.

Attributes:
- id (Integer): Primary key, unique identifier for each user.
- username (String): Unique username for the user, max length 50 characters.
- email (String): Unique email address of the user, max length 100 characters.
- password_hash (String): Hashed password for authentication, max length 255 characters.
- role (String): Role of the user, either 'user' or 'admin', default is 'user'.
- created_at (DateTime): Timestamp when the user was created, set automatically.

Constraints:
- username and email must be unique and not null.
- role has a default value 'user'.

Relationships:
- reviews: One-to-many relationship with Review model; a user can write multiple reviews.
- watchlist_entries: One-to-many relationship with Watchlist model; a user can have multiple watchlist entries.
"""

from extensions import db

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="user")  # user|admin
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    # ========== Relationships ==========
    reviews = db.relationship("Review", back_populates="user", cascade="all, delete-orphan")
    watchlist_entries = db.relationship("Watchlist", back_populates="user", cascade="all, delete-orphan")
