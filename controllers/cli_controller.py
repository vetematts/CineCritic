# controllers/cli_controller.py
from flask import Blueprint
from extensions import db
from models import User, Film, Genre, Review, Watchlist

db_commands = Blueprint("db", __name__)

@db_commands.cli.command("seed")
def seed_tables():
    """Seed the database with demo CineCritic data."""
    # drop and recreate tables (for demo/dev only)
    db.drop_all()
    db.create_all()

    # demo users
    users = [
        User(username="matty", email="matty@example.com", password="hashed_pw"),
        User(username="sol", email="sol@example.com", password="hashed_pw")
    ]

    # demo films
    films = [
        Film(title="Inception", release_year=2010, director="Christopher Nolan"),
        Film(title="Parasite", release_year=2019, director="Bong Joon-ho"),
        Film(title="Spirited Away", release_year=2001, director="Hayao Miyazaki")
    ]

    # demo genres
    genres = [
        Genre(name="Sci-Fi"),
        Genre(name="Drama"),
        Genre(name="Animation")
    ]

    # commit users, films, genres
    db.session.add_all(users + films + genres)
    db.session.commit()

    # demo review
    review = Review(
        rating=5,
        comment="A mind-bending masterpiece!",
        status="published",
        user_id=1,  # Matty
        film_id=1   # Inception
    )
    db.session.add(review)

    # demo watchlist entry
    watchlist = Watchlist(user_id=2, film_id=2)  # Sol has Parasite on watchlist
    db.session.add(watchlist)

    db.session.commit()

    print("✅ Demo CineCritic data seeded.")
