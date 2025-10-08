from datetime import datetime
from http.client import TOO_EARLY
from flask import request, session, abort, jsonify

# Custom modules
from setup import get_db, close_db, create_blueprint, register_error_handlers
from api import lookup

# Blueprint setup
bp = create_blueprint("transactions")


# =====================================================
# Strategy Selection
# =====================================================
@bp.route("/transactions/api/strategy", methods=["POST"])
def select_strategy():
    """Store selected strategy in session."""
    strategy_id = request.form.get("strategy_id")
    if not strategy_id:
        return abort(400, description="Missing strategy ID")

    db = get_db()
    row = db.execute("SELECT cash FROM strategy WHERE id = ?", (strategy_id,)).fetchone()
    if not row:
        close_db()
        return abort(404, description="Strategy not found")

    cash = row["cash"]
    session["strategy_id"] = int(strategy_id)
    session["cash"] = float(cash)
    close_db()

    return jsonify({"status": "success", "strategy_id": strategy_id, "cash": cash}), 200


# =====================================================
# Deposit Funds
# =====================================================
@bp.route("/transactions/api/deposit", methods=["POST"])
def deposit():
    """Deposit funds into the current strategy."""
    strategy_id = session.get("strategy_id")
    if not strategy_id:
        return abort(400, description="No active strategy")

    data = request.get_json(silent=True) or {}
    amount = data.get("amount")

    if amount is None:
        return abort(400, description="Missing deposit amount")

    try:
        amount = float(amount)
        if amount <= 0:
            return abort(400, description="Deposit must be positive")
    except ValueError:
        return abort(400, description="Invalid deposit amount")

    db = get_db()
    current_cash = db.execute(
        "SELECT cash FROM strategy WHERE id = ?", (strategy_id,)
    ).fetchone()["cash"]

    new_cash = current_cash + amount
    db.execute("UPDATE strategy SET cash = ? WHERE id = ?", (new_cash, strategy_id))
    db.execute(
        "INSERT INTO transactions (strategy_id, type, ticker, shares, price, date) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (strategy_id, "deposit", None, None, None, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
    )
    db.commit()
    close_db()

    session["cash"] = new_cash
    return jsonify({"status": "success", "new_cash": new_cash}), 200


# =====================================================
# Withdraw Funds
# =====================================================
@bp.route("/transactions/api/withdraw", methods=["POST"])
def withdraw():
    response = request.get_json()
    amount = response.get("amount")
    strategy_id = session.get("strategy_id")
    cash = session.get("cash")
    if not strategy_id or cash is None:
        return abort(400, description="No active strategy")
    if amount is None:
        return abort(400, description="Missing withdraw amount")
    try:
        amount = float(amount)
        if amount <= 0:
            return abort(400, description="Withdraw must be positive")
        if amount > cash:
            return abort(400, description="Insufficient cash balance")
    except ValueError:
        return abort(400, description="Invalid withdraw amount")
    
    new_cash = cash - amount
    db = get_db()
    db.execute("UPDATE strategy SET cash = ? WHERE id = ?", (new_cash, strategy_id))
    db.execute(
        "INSERT INTO transactions (strategy_id, type, ticker, shares, price, date) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (strategy_id, "withdraw", None, None, None, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
    )
    db.commit()
    close_db()

    session["cash"] = new_cash
    return jsonify({"status": "success", "new_cash": new_cash}), 200


# =====================================================
# Quotes API (buy/sell)
# =====================================================
@bp.route("/transactions/api/quote", methods=["POST"])
def get_quote():
    data = request.get_json()
    ticker = data.get("ticker", "").strip().upper()
    if not ticker:
        return abort(400, description="Missing ticker")
    shares = data.get("shares")
    if shares is None:
        return abort(400, description="Missing shares")
    try:
        shares = float(shares)
    except ValueError:
        return abort(400, description="Invalid shares value")
    
    quote = lookup(ticker)
    if not quote or "price" not in quote:
        return abort(502, description=f"Failed to fetch quote for {ticker}")

    price = round(quote["price"], 2)
    total = price * shares
    return jsonify({"ticker": ticker, "shares": shares, "price": price, "total": total})

@bp.route("/transactions/api/buy", methods=["POST"])
def buy():
    """Buy shares of a given ticker."""
    strategy_id = session.get("strategy_id")
    cash = session.get("cash")
    if not strategy_id or cash is None:
        return abort(400, description="No active strategy")

    # Parsing data from request
    data = request.get_json()
    ticker = data.get("ticker")
    shares = data.get("shares")
    price = data.get("price")

    if not ticker or shares is None or price is None:
        return abort(400, description="Missing ticker, shares, or price")

    try:
        shares = float(shares)
        if shares <= 0:
            return abort(400, description="Shares must be positive")
    except ValueError:
        return abort(400, description="Invalid shares value")

    # Comparing cost to cash balance
    cost = price * shares
    if cost > cash:
        return abort(400, description="Insufficient cash balance")

    db = get_db()

    # Update or insert portfolio position
    existing = db.execute(
        "SELECT shares FROM portfolio WHERE strategy_id = ? AND ticker = ?", (strategy_id, ticker)
    ).fetchone()

    if existing:
        db.execute(
            "UPDATE portfolio SET shares = shares + ? WHERE strategy_id = ? AND ticker = ?",
            (shares, strategy_id, ticker),
        )
    else:
        db.execute(
            "INSERT INTO portfolio (strategy_id, ticker, shares) VALUES (?, ?, ?)",
            (strategy_id, ticker, shares),
        )

    # Record transaction and deduct cash
    db.execute(
        "INSERT INTO transactions (strategy_id, type, ticker, shares, price, date) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (strategy_id, "buy", ticker, shares, price, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
    )
    new_cash = cash - cost
    db.execute("UPDATE strategy SET cash = ? WHERE id = ?", (new_cash, strategy_id))
    db.commit()
    close_db()

    session["cash"] = new_cash
    return jsonify({"status": "success", "ticker": ticker, "shares": shares, "cost": cost}), 200


# =====================================================
# Sell Stocks
# =====================================================
@bp.route("/transactions/api/sell", methods=["POST"])
def sell():
    """Sell shares from a given ticker."""
    strategy_id = session.get("strategy_id")
    cash = session.get("cash")
    if not strategy_id or cash is None:
        return abort(400, description="No active strategy")

    # Parsing data from request
    data = request.get_json()
    ticker = data.get("ticker")
    shares = data.get("shares")
    price = data.get("price")

    if not ticker or shares is None or not price:
        return abort(400, description="Missing ticker, shares, or price")

    try:
        shares = float(shares)
        if shares <= 0:
            return abort(400, description="Shares must be positive")
    except ValueError:
        return abort(400, description="Invalid shares value")

    db = get_db()
    row = db.execute(
        "SELECT shares FROM portfolio WHERE strategy_id = ? AND ticker = ?", (strategy_id, ticker)
    ).fetchone()
    existing_shares = float(row["shares"]) if row else 0.0

    if existing_shares < shares:
        close_db()
        return abort(400, description="Not enough shares to sell")

    revenue = price * shares

    # Reduce or remove position
    db.execute(
        "UPDATE portfolio SET shares = shares - ? WHERE strategy_id = ? AND ticker = ?",
        (shares, strategy_id, ticker),
    )
    db.execute(
        "DELETE FROM portfolio WHERE strategy_id = ? AND ticker = ? AND shares <= 0",
        (strategy_id, ticker),
    )

    # Record transaction and add cash
    new_cash = cash + revenue
    db.execute(
        "INSERT INTO transactions (strategy_id, type, ticker, shares, price, date) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (strategy_id, "sell", ticker, shares, price, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
    )
    db.execute("UPDATE strategy SET cash = ? WHERE id = ?", (new_cash, strategy_id))
    db.commit()
    close_db()

    session["cash"] = new_cash
    return jsonify({"status": "success", "ticker": ticker, "shares": shares, "revenue": revenue}), 200
