import os
from flask import Flask, redirect, render_template, request, session, abort
from flask_session import Session
from routes.error import register_error_handlers
from requests import get
from routes.helpers import lookup, get_db, usd, gbp, eur
from routes.api import create_strategy, select_strategy, delete_strategy, load-portfolio
from routes.transactions import buy, sell


# Configure application
app = Flask(__name__)

# Secret key (needed for sessions)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Register error handlers
register_error_handlers(app)

# Currency filters
app.jinja_env.filters["usd"] = usd
app.jinja_env.filters["gbp"] = gbp
app.jinja_env.filters["eur"] = eur

# Routes
@app.route("/")
def index():
        db = get_db()
        rows = db.execute("SELECT id, name FROM strategy").fetchall()
        strategies = [{"id": row["id"], "name": row["name"]} for row in rows]
        return render_template("index.html", strategies=strategies)

@app.route("/buy", methods=["GET", "POST"])
def buy_route():
    return buy()

@app.route("/sell", methods=["GET", "POST"])
def sell_route():
    return sell()
