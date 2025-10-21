"""
Models package initialisation.

Ordering note:
- Some models depend on others being defined first.
- For example, Review requires User and Film to exist before it can be imported.
"""
from .users import User
from .film import Film
from .genre import Genre
from .review import Review
from .watchlist import Watchlist
from .film_genre import FilmGenre

__all__ = ["User", "Film", "Genre", "Review", "Watchlist", "FilmGenre"]
