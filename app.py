import os
import sqlite3
from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from datetime import datetime
from helpers import lookup, usd, gbp, eur

# Configure application
app = Flask(__name__)

# Secret key (needed for sessions)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret")

# Custom filter
app.jinja_env.filters["usd"] = usd
app.jinja_env.filters["gbp"] = gbp
app.jinja_env.filters["eur"] = eur

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure database
db = sqlite3.connect("portfolio.db", check_same_thread=False)

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Defining error-handlers
@app.errorhandler(404)
def not_found(e):
    return render_template("error.html", message="Page not found"), 404

@app.errorhandler(500)
def internal_error(e):
    return render_template("error.html", message="Server error"), 500

# Creating index route
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("index.html")
    
    strategy = session["strategy"]
    if strategy not in db.execute("SELECT DISTINCT strategy FROM portfolio").fetchall():
        db.execute("INSERT INTO portfolio (strategy) VALUES (?)", (strategy,))
    db.commit()

    portfolio_rows = db.execute("SELECT symbol, shares FROM portfolio WHERE strategy = ?", (strategy,))

    portfolio = []
    for row in portfolio_rows:
        symbol = row["symbol"]
        shares = row["shares"]

        quote = lookup(symbol)
        if not quote:
            return internal_error(500)

        price = quote["price"]
        total = price * shares

        portfolio.append({
            "symbol": symbol,
            "shares": shares,
            "price": price,
            "total": total
        })

    cash = db.execute("SELECT cash FROM strategy WHERE name = ?", (strategy,))[0]["cash"]
    grand_total = sum(stock["total"] for stock in portfolio) + cash

    return render_template("index.html", portfolio=portfolio, cash=cash, grand_total=grand_total)


@app.route("/buy", methods=["GET", "POST"])
def buy():
    if request.method == "GET":
        return render_template("buy.html")

    symbol = request.form.get("symbol", "").strip().upper()
    shares = request.form.get("shares")

    if not symbol or not shares:
        return internal_error(500)

    try:
        shares = int(shares)
        if shares <= 0:
            return internal_error(500)
    except ValueError:
        return internal_error(500)

    quote = lookup(symbol)
    if not quote:
        return internal_error(500)

    strategy = session["strategy"]
    cash = db.execute("SELECT cash FROM strategy WHERE name = ?", (strategy,))[0]["cash"]
    price = quote["price"]
    cost = price * shares
    
    if cost > cash:
        return internal_error(500)
    buy_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Record purchase
    db.execute("INSERT INTO buy (symbol, price, shares, buy_date, strategy) VALUES (?, ?, ?, ?, ?)",
               (symbol, price, shares, buy_date, strategy))

    # Update portfolio
    db.execute("""
               INSERT INTO portfolio (symbol, shares, strategy)
               VALUES (?, ?, ?), (symbol, shares, strategy)
               ON CONFLICT(strategy, symbol) DO UPDATE SET shares = shares + excluded.shares, 
               (strategy, symbol, shares))
               """, (symbol, shares, strategy))

    # Update cash
    db.execute("UPDATE strategy SET cash = ? WHERE name = ?", (cash - cost, strategy))

    return redirect("/")


@app.route("/sell", methods=["GET", "POST"])
def sell():
    if request.method == "GET":
        return render_template("sell.html")

    symbol = request.form.get("symbol", "").strip().upper()
    shares = request.form.get("shares")

    if not symbol or not shares:
        return internal_error(500)

    try:
        shares = int(shares)
        if shares <= 0:
            return internal_error(500)
    except ValueError:
        return internal_error(500)

    quote = lookup(symbol)
    if not quote:
        return internal_error(500)

    strategy = session["strategy"]

    # Check holdings
    portfolio_rows = db.execute(
        "SELECT shares FROM portfolio WHERE strategy = ? AND symbol = ?", (strategy, symbol))
    if not portfolio_rows:
        return internal_error(500)
    
    existing_shares = portfolio_rows[0]["shares"]
    if shares > existing_shares:
        return internal_error(500)
    
    price = quote["price"]
    sell_value = price * shares

    sell_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Record sale and update balances
    db.execute("INSERT INTO sell (symbol, price, shares, sell_date, strategy) VALUES (?, ?, ?, ?, ?)",
               (symbol, price, shares, sell_date, strategy))

    remaining = existing_shares - shares
    if remaining > 0:
        db.execute("UPDATE portfolio SET shares = ? WHERE strategy = ? AND symbol = ?",
                   (remaining, strategy, symbol))
    
    db.execute("DELETE FROM portfolio WHERE strategy = ? AND symbol = ?", strategy, symbol)

    cash = db.execute("SELECT cash FROM strategy WHERE name = ?", strategy)[0]["cash"]
    db.execute("UPDATE strategy SET cash = ? WHERE name = ?", (cash + sell_value, strategy))

    return redirect("/")


#### RETURN TO THIS LATER ####
"""
@app.route("/quote", methods=["GET", "POST"])
def quote():
    if request.method == "POST":
        symbol = request.form.get("symbol", "").strip().upper()
        if not symbol or not (1 <= len(symbol) <= 5) or not symbol.isalpha():
            return internal_error(500)
        quote = lookup(symbol)
        if not quote:
            return internal_error(500)
        return render_template("quoted.html", quote=quote)

    return render_template("quote.html")

@app.route("/history")
def history():
    transactions = db.execute(
        "SELECT symbol, shares, price, purchase_date FROM purchases WHERE user_id = ? ORDER BY purchase_date DESC",
        session["user_id"]
    )
    return render_template("history.html", transactions=transactions)
    """