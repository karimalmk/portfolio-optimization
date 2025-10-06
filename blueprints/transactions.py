from datetime import datetime
from flask import Blueprint, request, session, abort, jsonify
from helpers import get_db, lookup

bp = Blueprint('transactions', __name__)

# ===============================
# Strategy Selection
# ===============================
@bp.route("/transactions/api/strategy", methods=["POST"])
def get_strategy():
    strategy_id = request.form.get("strategy_id")
    db = get_db()
    cash = db.execute("SELECT cash FROM strategy WHERE id = ?", (strategy_id,)).fetchone()[0]
    session["strategy_id"] = strategy_id
    session["cash"] = cash
    db.close()
    return jsonify({"status": "success"})


# ===============================
# Deposit Funds
# ===============================
@bp.route("/transactions/api/deposit", methods=["POST"])
def deposit():
    strategy_id = session.get("strategy_id")
    data = request.get_json()
    amount = data.get("amount")

    if not strategy_id or amount is None:
        return abort(400, "Missing data")

    try:
        amount = float(amount)
        if amount <= 0:
            return abort(400, "Invalid amount")
    except ValueError:
        return abort(400, "Invalid number")

    db = get_db()
    current_cash = db.execute("SELECT cash FROM strategy WHERE id = ?", (strategy_id,)).fetchone()[0]
    new_cash = current_cash + amount

    db.execute("UPDATE strategy SET cash = ? WHERE id = ?", (new_cash, strategy_id))
    db.execute(
        "INSERT INTO transactions (strategy_id, type, ticker, shares, price, date) VALUES (?, ?, ?, ?, ?, ?)",
        (strategy_id, "deposit", None, None, None, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
    )

    db.commit()
    db.close()
    session["cash"] = new_cash
    return jsonify({"status": "success"})


# ===============================
# Buy Stocks
# ===============================
@bp.route("/transactions/api/buy", methods=["POST"])
def buy():
    strategy_id = session.get("strategy_id")
    cash = session.get("cash")
    data = request.get_json()

    ticker = data.get("ticker")
    shares = data.get("shares")

    if not ticker or shares is None:
        return abort(400, "Missing data")

    try:
        shares = float(shares)
        if shares <= 0:
            return abort(400)
    except ValueError:
        return abort(400)

    quote = lookup(ticker)
    if not quote:
        return abort(502)

    price = float(quote["price"])
    cost = price * shares

    if cost > cash:
        return abort(400, "Insufficient cash")

    db = get_db()

    # Update portfolio
    row = db.execute(
        "SELECT shares FROM portfolio WHERE strategy_id = ? AND ticker = ?", (strategy_id, ticker)
    ).fetchone()
    if row:
        db.execute(
            "UPDATE portfolio SET shares = shares + ? WHERE strategy_id = ? AND ticker = ?",
            (shares, strategy_id, ticker),
        )
    else:
        db.execute(
            "INSERT INTO portfolio (strategy_id, ticker, shares) VALUES (?, ?, ?)",
            (strategy_id, ticker, shares),
        )

    # Record transaction & update cash
    db.execute(
        "INSERT INTO transactions (strategy_id, type, ticker, shares, price, date) VALUES (?, ?, ?, ?, ?, ?)",
        (strategy_id, "buy", ticker, shares, price, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
    )
    db.execute("UPDATE strategy SET cash = ? WHERE id = ?", (cash - cost, strategy_id))

    db.commit()
    db.close()
    session["cash"] = cash - cost
    return jsonify({"status": "success"})


# ===============================
# Sell Stocks
# ===============================
@bp.route("/transactions/api/sell", methods=["POST"])
def sell():
    strategy_id = session.get("strategy_id")
    cash = session.get("cash")
    data = request.get_json()

    ticker = data.get("ticker")
    shares = data.get("shares")

    if not ticker or shares is None:
        return abort(400, "Missing data")

    try:
        shares = float(shares)
        if shares <= 0:
            return abort(400)
    except ValueError:
        return abort(400)

    quote = lookup(ticker)
    if not quote:
        return abort(502)

    db = get_db()
    row = db.execute(
        "SELECT shares FROM portfolio WHERE strategy_id = ? AND ticker = ?", (strategy_id, ticker)
    ).fetchone()
    existing_shares = row[0] if row else 0

    if existing_shares < shares:
        db.close()
        return abort(400, "Not enough shares")

    price = float(quote["price"])
    revenue = price * shares

    # Update portfolio
    db.execute(
        "UPDATE portfolio SET shares = shares - ? WHERE strategy_id = ? AND ticker = ?",
        (shares, strategy_id, ticker),
    )

    # Remove entry if shares drop to zero or below
    db.execute(
        "DELETE FROM portfolio WHERE strategy_id = ? AND ticker = ? AND shares <= 0",
        (strategy_id, ticker),
    )

    # Record transaction & update cash
    db.execute(
        "INSERT INTO transactions (strategy_id, type, ticker, shares, price, date) VALUES (?, ?, ?, ?, ?, ?)",
        (strategy_id, "sell", ticker, shares, price, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
    )
    db.execute("UPDATE strategy SET cash = ? WHERE id = ?", (cash + revenue, strategy_id))

    db.commit()
    db.close()
    session["cash"] = cash + revenue
    return jsonify({"status": "success"})
