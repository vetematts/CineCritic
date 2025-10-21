"""
Schema imports for CineCritic.

- Defines import order so dependent schemas load correctly
- For example, ReviewSchema requires User and Film schemas
"""
from .films_schema import FilmCreateSchema, FilmSchema
from .reviews_schema import ReviewCreateSchema, ReviewSchema
from .genres_schema import GenreCreateSchema, GenreSchema
from .users_schema import UserRegisterSchema, LoginSchema
from .watchlist_schema import WatchlistEntrySchema
