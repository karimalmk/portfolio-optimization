import os
from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from datetime import datetime
from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Secret key (needed for sessions)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret")

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    user_id = session["user_id"]

    # Get portfolio
    portfolio_rows = db.execute("SELECT symbol, shares FROM portfolio WHERE user_id = ?", user_id)

    portfolio = []
    for row in portfolio_rows:
        symbol = row["symbol"]
        shares = row["shares"]

        quote = lookup(symbol)
        if not quote:
            return apology(f"Missing quote for {symbol}")

        price = quote["price"]
        total = price * shares

        portfolio.append({
            "symbol": symbol,
            "shares": shares,
            "price": price,
            "total": total
        })

    # Get cash and grand total
    cash = db.execute("SELECT cash FROM users WHERE id = ?", user_id)[0]["cash"]
    grand_total = sum(stock["total"] for stock in portfolio) + cash

    return render_template("index.html", portfolio=portfolio, cash=cash, grand_total=grand_total)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    if request.method == "GET":
        return render_template("buy.html")

    symbol = request.form.get("symbol", "").strip().upper()
    shares = request.form.get("shares")

    if not symbol or not shares:
        return apology("Missing symbol or shares")

    try:
        shares = int(shares)
        if shares <= 0:
            return apology("Shares must be positive")
    except ValueError:
        return apology("Invalid input")

    quote = lookup(symbol)
    if not quote:
        return apology("Invalid symbol")

    price = quote["price"]
    user_id = session["user_id"]
    cash = db.execute("SELECT cash FROM users WHERE id = ?", user_id)[0]["cash"]

    total_cost = price * shares
    if total_cost > cash:
        return apology("Insufficient funds")

    purchase_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Record purchase
    db.execute("INSERT INTO purchases (symbol, price, shares, purchase_date, user_id) VALUES (?, ?, ?, ?, ?)",
               symbol, price, shares, purchase_date, user_id)

    # Update portfolio with UPSERT (SQLite >= 3.24)
    db.execute("""
        INSERT INTO portfolio (user_id, symbol, shares)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id, symbol) DO UPDATE SET shares = shares + excluded.shares
    """, user_id, symbol, shares)

    # Update cash
    db.execute("UPDATE users SET cash = ? WHERE id = ?", cash - total_cost, user_id)

    return redirect("/")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    if request.method == "GET":
        return render_template("sell.html")

    symbol = request.form.get("symbol", "").strip().upper()
    shares = request.form.get("shares")

    if not symbol or not shares:
        return apology("Missing symbol or shares")

    try:
        shares = int(shares)
        if shares <= 0:
            return apology("Shares must be positive")
    except ValueError:
        return apology("Invalid input")

    quote = lookup(symbol)
    if not quote:
        return apology("Invalid symbol")

    price = quote["price"]
    sale_value = price * shares
    user_id = session["user_id"]

    # Check holdings
    rows = db.execute(
        "SELECT shares FROM portfolio WHERE user_id = ? AND symbol = ?", user_id, symbol)
    if not rows:
        return apology("You don’t own this stock")

    existing_shares = rows[0]["shares"]
    if shares > existing_shares:
        return apology("Insufficient shares")

    sale_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Record sale (negative shares in purchases table)
    db.execute("INSERT INTO purchases (symbol, price, shares, purchase_date, user_id) VALUES (?, ?, ?, ?, ?)",
               symbol, price, -shares, sale_date, user_id)

    # Update portfolio
    remaining = existing_shares - shares
    if remaining > 0:
        db.execute("UPDATE portfolio SET shares = ? WHERE user_id = ? AND symbol = ?",
                   remaining, user_id, symbol)
    else:
        db.execute("DELETE FROM portfolio WHERE user_id = ? AND symbol = ?", user_id, symbol)

    # Update cash
    cash = db.execute("SELECT cash FROM users WHERE id = ?", user_id)[0]["cash"]
    db.execute("UPDATE users SET cash = ? WHERE id = ?", cash + sale_value, user_id)

    return redirect("/")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    transactions = db.execute(
        "SELECT symbol, shares, price, purchase_date FROM purchases WHERE user_id = ? ORDER BY purchase_date DESC",
        session["user_id"]
    )
    return render_template("history.html", transactions=transactions)


@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()

    if request.method == "POST":
        if not request.form.get("username"):
            return apology("must provide username", 403)
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        session["user_id"] = rows[0]["id"]
        return redirect("/")

    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    if request.method == "POST":
        symbol = request.form.get("symbol", "").strip().upper()
        if not symbol or not (1 <= len(symbol) <= 5) or not symbol.isalpha():
            return apology("Invalid symbol")
        quote = lookup(symbol)
        if not quote:
            return apology("Invalid symbol")
        return render_template("quoted.html", quote=quote)

    return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    username = request.form.get("username")
    password = request.form.get("password")
    confirmation = request.form.get("confirmation")

    if not username or not password or not confirmation:
        return apology("Missing fields")

    if password != confirmation:
        return apology("Password and confirmation don't match")

    hash_pw = generate_password_hash(password)
    try:
        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, hash_pw)
    except IntegrityError:
        return apology("User already exists")
    except Exception as e:
        if "UNIQUE constraint failed" in str(e):
            return apology("User already exists")
        raise

    # Auto-login newly registered user
    user = db.execute("SELECT id FROM users WHERE username = ?", username)[0]
    session["user_id"] = user["id"]

    return redirect("/")
