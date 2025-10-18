"""
CineCritic — centralized JSON error handling.

Each handler returns JSON in the form:
    {"error": "code", "detail": "message", "meta": {...optional}}

- ValidationError → 400 with field-level messages in meta
- IntegrityError  → 409 for unique / FK / not-null / check violations
- DataError       → 400 for bad casts / malformed values from the DB driver
- 404/405         → not_found / method_not_allowed
- 500/Exception   → server_error (generic)
"""

# Installed imports
from flask import jsonify
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError, DataError
from psycopg2 import errorcodes
from psycopg2.errors import UniqueViolation

def register_error_handlers(app):
    """Register JSON error handlers with a consistent payload shape."""

    # ========== HELPER ==========
    def _json(error: str, detail: str, status: int, meta=None):
        payload = {"error": error, "detail": detail}
        if meta is not None:
            payload["meta"] = meta
        return jsonify(payload), status

    # ========== VALIDATION ERRORS ==========
    @app.errorhandler(ValidationError)
    def on_validation(err: ValidationError):
        # err.messages contains field-level errors from Marshmallow
        return _json("bad_request", "Invalid input data.", 400, meta=err.messages)

    # ========== DATABASE ERRORS ==========
    @app.errorhandler(IntegrityError)
    def on_integrity(err: IntegrityError):
        orig = getattr(err, "orig", None)
        code = getattr(orig, "pgcode", None)

        if code == errorcodes.NOT_NULL_VIOLATION:
            col = getattr(getattr(orig, "diag", None), "column_name", None)
            detail = f"Missing required field: {col}." if col else "Required field cannot be null."
            return _json("conflict", detail, 409)

        if code == errorcodes.UNIQUE_VIOLATION or code == getattr(UniqueViolation, "sqlstate", None):
            return _json("conflict", "Duplicate entry.", 409)

        if code == errorcodes.FOREIGN_KEY_VIOLATION:
            return _json("conflict", "Invalid reference. Check that related IDs exist.", 409)

        if code == errorcodes.CHECK_VIOLATION:
            diag_detail = getattr(getattr(orig, "diag", None), "message_detail", None)
            return _json("conflict", diag_detail or "Check constraint failed.", 409)

        return _json("conflict", "Database integrity error.", 409)

    @app.errorhandler(DataError)
    def on_data_error(err: DataError):
        primary = getattr(getattr(err, "orig", None), "diag", None)
        primary_msg = getattr(primary, "message_primary", None)
        return _json("bad_request", primary_msg or "Invalid data input.", 400)

    # ========== CLIENT ERRORS ==========
    @app.errorhandler(404)
    def on_404(_):
        return _json("not_found", "Resource not found.", 404)

    @app.errorhandler(405)
    def on_405(_):
        return _json("method_not_allowed", "Method not allowed for this endpoint.", 405)

    # ========== SERVER ERRORS ==========
    @app.errorhandler(500)
    def on_500(_):
        return _json("server_error", "Unexpected server error.", 500)

    # ========== FALLBACK ==========
    @app.errorhandler(Exception)
    def on_any_error(_):
        return _json("server_error", "Unexpected error.", 500)
