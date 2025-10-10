import sqlite3
from flask import Blueprint, jsonify, g
from werkzeug.exceptions import HTTPException

# ============================
# Database Connection
# ============================
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect("portfolio.db")
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()

# ============================
# Error Handlers
# ============================
def register_error_handlers(app):
    """Register JSON error handlers for the Flask app."""
    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        response = jsonify({
            "status": "fail",
            "message": e.description,
            "code": e.code
        })
        response.status_code = e.code
        return response

# ============================
# Blueprint Factory
# ============================
def create_blueprint(name):
    return Blueprint(name, __name__)