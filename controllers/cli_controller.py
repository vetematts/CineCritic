"""
Database CLI commands for CineCritic.

Custom commands:
  flask ops drop    – drop all tables
  flask ops create  – create all tables
  flask ops seed    – populate tables with sample data

Migrations (via Flask-Migrate):
  flask db init     – set up migrations folder
  flask db migrate  – generate migration scripts from model changes
  flask db upgrade  – apply migrations to the database

Notes:
  - Seeds run in dependency order: Users → Films/Genres → FilmGenre → Reviews → Watchlist
  - Passwords are hashed; never store plain text.
"""
# Installed imports
from flask import Blueprint
from werkzeug.security import generate_password_hash

# Local imports
from extensions import db
from models import User, Film, Genre, Review, Watchlist, FilmGenre

ops_commands = Blueprint("ops", __name__)

# ======== CLI COMMANDS ========

@ops_commands.cli.command("create")
def create_tables():
    """Create all database tables."""
    db.create_all()
    print("Tables created.")

@ops_commands.cli.command("drop")
def drop_tables():
    """Drop all database tables."""
    db.drop_all()
    print("Tables dropped.")

@ops_commands.cli.command("seed")
def seed_tables():
    """Seed the database with sample CineCritic data."""
    # Safety check: don’t reseed if a user already exists
    if db.session.scalar(db.select(User).limit(1)):
        print("Seed skipped: data already present.")
        return

    # ========== Seed Users ==========
    u1 = User(
        username="matty",
        email="matty@example.com",
        password_hash=generate_password_hash("secret123")  # adjust to your column name if different
    )
    u2 = User(
        username="sol",
        email="sol@example.com",
        password_hash=generate_password_hash("secret123")
    )
    admin = User(
        username="admin",
        email="admin@example.com",
        password_hash=generate_password_hash("admin123"),
        role="admin"
    )
    db.session.add_all([u1, u2, admin])
    db.session.commit()

    # ========== Seed Films ==========
    f1 = Film(title="Inception",     release_year=2010, director="Christopher Nolan")
    f2 = Film(title="Parasite",      release_year=2019, director="Bong Joon-ho")
    f3 = Film(title="Spirited Away", release_year=2001, director="Hayao Miyazaki")
    db.session.add_all([f1, f2, f3])
    db.session.commit()

    # ========== Seed Genres ==========
    g1 = Genre(name="Sci-Fi")
    g2 = Genre(name="Drama")
    g3 = Genre(name="Animation")
    db.session.add_all([g1, g2, g3])
    db.session.commit()

    # ========== Seed Film↔Genre (junction) ==========
    db.session.add_all([
        FilmGenre(film_id=f1.id, genre_id=g1.id),  # Inception → Sci-Fi
        FilmGenre(film_id=f2.id, genre_id=g2.id),  # Parasite  → Drama
        FilmGenre(film_id=f3.id, genre_id=g3.id),  # Spirited Away → Animation
    ])
    db.session.commit()

    # ========== Seed Reviews ==========
    r1 = Review(film_id=f1.id, user_id=u1.id, rating=5.0, body="A mind-bender.", status="published", published_at=db.func.now())
    r2 = Review(film_id=f2.id, user_id=u2.id, rating=4.5, body="Tense and brilliant.", status="draft")
    r3 = Review(film_id=f1.id, user_id=u2.id, rating=4.0, body="Flag me please", status="flagged", flagged_at=db.func.now())
    db.session.add_all([r1, r2, r3])
    db.session.commit()

    # ========== Seed Watchlist ==========
    w1 = Watchlist(user_id=u2.id, film_id=f2.id)
    w2 = Watchlist(user_id=u1.id, film_id=f3.id)
    db.session.add_all([w1, w2])
    db.session.commit()

    print("✅ CineCritic Tables seeded.")
