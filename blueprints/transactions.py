from datetime import datetime
from flask import request, session, abort, jsonify

# Custom modules
from helpers.setup import get_db, close_db, create_blueprint, register_error_handlers
from helpers.api import lookup, load_cache

bp = create_blueprint("transactions")


# =====================================================
# Strategy Selection
# =====================================================
@bp.route("/transactions/api/strategy", methods=["POST"])
def select_strategy():
    """Store selected strategy in session."""
    strategy_id = request.form.get("strategy_id", "").strip()
    if not strategy_id:
        abort(400, description="Missing strategy ID.")

    db = get_db()
    try:
        row = db.execute(
            "SELECT current_cash FROM strategy WHERE id = ?", (strategy_id,)
        ).fetchone()
        if not row:
            abort(404, description="Strategy not found.")

        current_cash = float(row["current_cash"])
        session["strategy_id"] = int(strategy_id)
        session["current_cash"] = current_cash

        return jsonify(
            {"status": "success", "strategy_id": int(strategy_id), "cash": current_cash}
        ), 200
    finally:
        close_db()


# =====================================================
# Deposit Funds
# =====================================================
@bp.route("/transactions/api/deposit", methods=["POST"])
def deposit():
    """Deposit funds into the current strategy."""
    strategy_id = session.get("strategy_id")
    if not strategy_id:
        abort(400, description="No active strategy.")

    data = request.get_json(silent=True) or {}
    amount = data.get("amount")

    try:
        amount = float(amount) # type: ignore
        if amount <= 0:
            abort(400, description="Deposit amount must be positive.")
    except (TypeError, ValueError):
        abort(400, description="Invalid deposit amount.")

    db = get_db()
    try:
        current_cash = session.get("current_cash", 0.0)
        new_cash = current_cash + amount

        db.execute(
            "UPDATE strategy SET current_cash = ? WHERE id = ?", (new_cash, strategy_id)
        )
        db.execute(
            """
            INSERT INTO transactions (strategy_id, type, ticker, shares, price, date)
            VALUES (?, ?, NULL, NULL, ?, ?)
            """,
            (
                strategy_id,
                "deposit",
                amount,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            ),
        )
        db.commit()
        session["current_cash"] = new_cash
        return jsonify({"status": "success", "new_cash": round(new_cash, 2)}), 200
    finally:
        close_db()


# =====================================================
# Withdraw Funds
# =====================================================
@bp.route("/transactions/api/withdraw", methods=["POST"])
def withdraw():
    """Withdraw funds from the current strategy."""
    strategy_id = session.get("strategy_id")
    current_cash = session.get("current_cash")
    if not strategy_id or current_cash is None:
        abort(400, description="No active strategy.")

    data = request.get_json(silent=True) or {}
    amount = data.get("amount")

    try:
        amount = float(amount) # type: ignore
        if amount <= 0:
            abort(400, description="Withdraw amount must be positive.")
        if amount > current_cash:
            abort(400, description="Insufficient cash balance.")
    except (TypeError, ValueError):
        abort(400, description="Invalid withdraw amount.")

    db = get_db()
    try:
        new_cash = current_cash - amount

        db.execute(
            "UPDATE strategy SET current_cash = ? WHERE id = ?", (new_cash, strategy_id)
        )
        db.execute(
            """
            INSERT INTO transactions (strategy_id, type, ticker, shares, price, date)
            VALUES (?, ?, NULL, NULL, ?, ?)
            """,
            (
                strategy_id,
                "withdraw",
                amount,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            ),
        )
        db.commit()
        session["current_cash"] = new_cash
        return jsonify({"status": "success", "new_cash": round(new_cash, 2)}), 200
    finally:
        close_db()


# =====================================================
# Quotes API (Buy/Sell)
# =====================================================
@bp.route("/transactions/api/quote", methods=["POST"])
def get_quote():
    """Return live or cached stock quote."""
    data = request.get_json(silent=True) or {}
    ticker = (data.get("ticker") or "").strip().upper()
    shares = data.get("shares")

    if not ticker:
        abort(400, description="Missing ticker symbol.")

    try:
        shares = float(shares) # type: ignore
        if shares <= 0:
            abort(400, description="Shares must be positive.")
    except (TypeError, ValueError):
        abort(400, description="Invalid number of shares.")

    CACHE = load_cache()
    quote = lookup(ticker, CACHE)
    if not quote or "price" not in quote or "time" not in quote or "date" not in quote or quote["price"] is None:
        abort(502, description=f"Failed to fetch quote for {ticker}.")

    price = round(float(quote["price"]), 2)
    total = round(price * shares, 2)
    time = quote["time"]
    date = quote["date"]

    return jsonify(
        {
            "status": "success",
            "ticker": ticker,
            "shares": shares,
            "price": price,
            "total": total,
            "time": time,
            "date": date,
        }
    ), 200


# =====================================================
# Buy Stocks
# =====================================================
@bp.route("/transactions/api/buy", methods=["POST"])
def buy():
    """Buy shares of a stock for the active strategy."""
    strategy_id = session.get("strategy_id")
    current_cash = session.get("current_cash")
    if not strategy_id or current_cash is None:
        abort(400, description="No active strategy.")

    data = request.get_json(silent=True) or {}
    ticker = (data.get("ticker") or "").strip().upper()
    shares = data.get("shares")
    price = data.get("price")

    try:
        shares = float(shares) # type: ignore
        price = float(price) # type: ignore
        if shares <= 0 or price <= 0:
            abort(400, description="Shares and price must be positive.")
    except (TypeError, ValueError):
        abort(400, description="Invalid trade parameters.")

    cost = price * shares
    if cost > current_cash:
        abort(400, description="Insufficient cash balance.")

    db = get_db()
    try:
        existing = db.execute(
            "SELECT shares FROM portfolio WHERE strategy_id = ? AND ticker = ?",
            (strategy_id, ticker),
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

        new_cash = current_cash - cost
        db.execute(
            """
            INSERT INTO transactions (strategy_id, type, ticker, shares, price, date)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                strategy_id,
                "buy",
                ticker,
                shares,
                price,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            ),
        )
        db.execute(
            "UPDATE strategy SET current_cash = ? WHERE id = ?", (new_cash, strategy_id)
        )
        db.commit()

        session["current_cash"] = new_cash
        return jsonify(
            {"status": "success", "ticker": ticker, "shares": shares, "cost": round(cost, 2)}
        ), 200
    finally:
        close_db()


# =====================================================
# Sell Stocks
# =====================================================
@bp.route("/transactions/api/sell", methods=["POST"])
def sell():
    """Sell shares of a stock for the active strategy."""
    strategy_id = session.get("strategy_id")
    current_cash = session.get("current_cash")
    if not strategy_id or current_cash is None:
        abort(400, description="No active strategy.")

    data = request.get_json(silent=True) or {}
    ticker = (data.get("ticker") or "").strip().upper()
    shares = data.get("shares")
    price = data.get("price")

    try:
        shares = float(shares) # type: ignore
        price = float(price) # type: ignore
        if shares <= 0 or price <= 0:
            abort(400, description="Shares and price must be positive.")
    except (TypeError, ValueError):
        abort(400, description="Invalid trade parameters.")

    db = get_db()
    try:
        row = db.execute(
            "SELECT shares FROM portfolio WHERE strategy_id = ? AND ticker = ?",
            (strategy_id, ticker),
        ).fetchone()
        existing_shares = float(row["shares"]) if row else 0.0

        if existing_shares < shares:
            abort(400, description="Insufficient shares to sell.")

        revenue = price * shares
        new_cash = current_cash + revenue

        if existing_shares == shares:
            db.execute(
                "DELETE FROM portfolio WHERE strategy_id = ? AND ticker = ?",
                (strategy_id, ticker),
            )
        else:
            db.execute(
                "UPDATE portfolio SET shares = shares - ? WHERE strategy_id = ? AND ticker = ?",
                (shares, strategy_id, ticker),
            )

        db.execute(
            """
            INSERT INTO transactions (strategy_id, type, ticker, shares, price, date)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                strategy_id,
                "sell",
                ticker,
                shares,
                price,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            ),
        )
        db.execute(
            "UPDATE strategy SET current_cash = ? WHERE id = ?", (new_cash, strategy_id)
        )
        db.commit()

        session["current_cash"] = new_cash
        return jsonify(
            {
                "status": "success",
                "ticker": ticker,
                "shares": shares,
                "revenue": round(revenue, 2),
            }
        ), 200
    finally:
        close_db()
