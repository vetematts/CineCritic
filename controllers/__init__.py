"""
Controller blueprints for CineCritic.

Defines the registration order of controllers.
Review routes depend on films and users, so they are registered afterwards.
"""

from .auth_controller import auth_bp
from .films_controller import film_bp
from .genres_controller import genre_bp
from .reviews_controller import review_bp
from .watchlist_controller import watchlist_bp
from .cli_controller import ops_commands

def register_controllers(app):
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(film_bp, url_prefix="/films")
    app.register_blueprint(genre_bp, url_prefix="/genres")
    app.register_blueprint(review_bp, url_prefix="/films/<int:film_id>/reviews")
    app.register_blueprint(watchlist_bp, url_prefix="/users/me/watchlist")
    app.register_blueprint(ops_commands)
