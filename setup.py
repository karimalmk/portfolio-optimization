import sqlite3
from flask import Blueprint, render_template, g
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
    @app.errorhandler(HTTPException) # This decorator handles all HTTP exceptions
    def handle_http_exception(e): # e is an instance of HTTPException
        messages = {
            400: "Bad request – user input error",
            404: "Page not found",
            500: "Server error",
            502: "API error – service unavailable"
        }
        message = messages.get(e.code, e.description)
        return render_template("error.html", message=message), e.code

# ============================
# Blueprint Factory
# ============================
def create_blueprint(name):
    return Blueprint(name, __name__)

# ============================
# Currency Formatters
# ============================
def format_currency(value, symbol="$"):
    return f"{symbol}{value:,.2f}"

usd = lambda v: format_currency(v, "$")
gbp = lambda v: format_currency(v, "£")
eur = lambda v: format_currency(v, "€")