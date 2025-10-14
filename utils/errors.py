from flask import jsonify
from sqlalchemy.exc import IntegrityError
from marshmallow import ValidationError

def register_error_handlers(app):
    @app.errorhandler(IntegrityError)
    def handle_integrity(err):
        return jsonify(error="conflict", detail=str(err.orig)), 409

    @app.errorhandler(ValidationError)
    def handle_validation(err):
        return jsonify(error="bad_request", detail=err.messages), 400
