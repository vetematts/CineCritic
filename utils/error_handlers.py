from flask import jsonify
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError, DataError
from psycopg2.errors import UniqueViolation

def register_error_handlers(app):
    @app.errorhandler(ValidationError)
    def handle_validation_error(err):
        response = {
            "error": "Bad Request",
            "message": "Invalid input data.",
            "details": err.messages
        }
        return jsonify(response), 400

    @app.errorhandler(IntegrityError)
    def handle_integrity_error(err):
        # Check if it's a unique violation from psycopg2
        if isinstance(getattr(err.orig, 'pgcode', None), str) and err.orig.pgcode == UniqueViolation.sqlstate:
            message = "Resource conflict: duplicate entry."
        else:
            message = "Database integrity error."
        response = {
            "error": "Conflict",
            "message": message,
            "details": str(err.orig)
        }
        return jsonify(response), 409

    @app.errorhandler(DataError)
    def handle_data_error(err):
        response = {
            "error": "Bad Request",
            "message": "Invalid data input.",
            "details": str(err.orig)
        }
        return jsonify(response), 400

    @app.errorhandler(404)
    def handle_not_found(err):
        response = {
            "error": "Not Found",
            "message": "The requested resource was not found."
        }
        return jsonify(response), 404

    @app.errorhandler(500)
    def handle_internal_error(err):
        response = {
            "error": "Internal Server Error",
            "message": "An unexpected error occurred. Please try again later."
        }
        return jsonify(response), 500
