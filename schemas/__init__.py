"""
Schema imports for CineCritic.

- Defines import order so dependent schemas load correctly
- For example, ReviewSchema requires User and Film schemas
"""
from .film_schema import FilmCreateSchema, FilmSchema
from .review_schema import ReviewCreateSchema, ReviewSchema
from .genre_schema import GenreSchema
from .users_schema import UserRegisterSchema, LoginSchema
from .watchlist_schema import WatchlistEntrySchema
