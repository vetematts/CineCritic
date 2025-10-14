from .auth_controller import auth_bp
from .film_controller import film_bp
from .genre_controller import genre_bp
from .review_controller import review_bp
from .watchlist_controller import watchlist_bp
from .cli_controller import db_commands

def register_controllers(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(film_bp)
    app.register_blueprint(genre_bp)
    app.register_blueprint(review_bp)
    app.register_blueprint(watchlist_bp)
    app.register_blueprint(db_commands)
