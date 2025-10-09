from sqlite3 import IntegrityError
from flask import request, abort, jsonify

# Custom modules
from setup import get_db, close_db, create_blueprint, register_error_handlers
from api import load_cache, lookup

bp = create_blueprint("index")


# =====================================================
# Create Strategy
# =====================================================
@bp.route("/api/create-strategy", methods=["POST"])
def create_strategy():
    db = get_db()
    name = request.form.get("name", "").strip()
    cash = request.form.get("cash", "").strip()

    # Validate inputs
    if not name:
        abort(400, description="Missing strategy name.")
    if not cash:
        abort(400, description="Missing cash amount.")

    try:
        cash = float(cash)
        if cash <= 0:
            abort(400, description="Cash amount must be positive.")
    except ValueError:
        abort(400, description="Invalid cash amount. Must be numeric.")

    try:
        db.execute(
            "INSERT INTO strategy (name, starting_cash, current_cash, total_value) VALUES (?, ?, ?, ?)",
            (name, cash, cash, cash),
        )
        db.commit()
    except IntegrityError:
        abort(400, description="Strategy name must be unique.")
    finally:
        close_db()

    return jsonify({"status": "success", "name": name, "cash": cash}), 201


# =====================================================
# Get All Strategies
# =====================================================
@bp.route("/api/strategies", methods=["GET"])
def get_strategies():
    db = get_db()
    try:
        rows = db.execute(
            "SELECT id, name, current_cash, total_value FROM strategy ORDER BY id ASC"
        ).fetchall()
        strategies = [
            {
                "id": row["id"],
                "name": row["name"],
                "cash": round(row["current_cash"], 2),
                "total_value": round(row["total_value"], 2),
            }
            for row in rows
        ]
        return jsonify({"strategies": strategies, "exists": bool(rows)})
    finally:
        close_db()


# =====================================================
# Get Portfolio & Overview
# =====================================================
@bp.route("/api/portfolio/<int:id>", methods=["GET"])
def display_portfolio(id):
    db = get_db()

    # Defensive fetch: ensure strategy exists
    strategy = db.execute(
        "SELECT starting_cash, current_cash FROM strategy WHERE id = ?", (id,)
    ).fetchone()
    if not strategy:
        close_db()
        abort(404, description="Strategy not found.")

    starting_cash = float(strategy["starting_cash"])
    current_cash = float(strategy["current_cash"])

    # Portfolio metrics
    portfolio_data = get_portfolio_metrics(db, id)
    portfolio = portfolio_data["portfolio"]
    equity_value = portfolio_data["equity_value"]

    total_value = equity_value + current_cash
    overall_return = (
        (total_value - starting_cash) / starting_cash * 100 if starting_cash else 0
    )

    # Update cached total value
    db.execute("UPDATE strategy SET total_value = ? WHERE id = ?", (total_value, id))
    db.commit()
    close_db()

    return jsonify(
        {
            "portfolio": portfolio,
            "overview": {
                "starting_cash": round(starting_cash, 2),
                "current_cash": round(current_cash, 2),
                "total_value": round(total_value, 2),
                "overall_return": round(overall_return, 2),
            },
        }
    )


# =====================================================
# Helper: Portfolio Metrics
# =====================================================
def get_portfolio_metrics(db, id):
    portfolio = []
    equity_value = 0.0

    stocks = db.execute(
        "SELECT ticker, shares FROM portfolio WHERE strategy_id = ?", (id,)
    ).fetchall()

    if not stocks:
        return {"portfolio": [], "equity_value": 0.0}

    for stock in stocks:
        ticker = stock["ticker"].strip().upper()
        shares = float(stock["shares"])
        if shares <= 0:
            continue  # ignore invalid or stale entries

        CACHE = load_cache()
        quote = lookup(ticker, CACHE)
        if not quote or "price" not in quote:
            continue  # skip unavailable tickers instead of aborting entire portfolio

        price = float(quote["price"])
        share_value = round(shares * price, 2)
        equity_value += share_value

        # Weighted purchase price
        buys = db.execute(
            "SELECT price, shares FROM transactions WHERE strategy_id = ? AND ticker = ? AND type = 'buy'",
            (id, ticker),
        ).fetchall()
        sells = db.execute(
            "SELECT price, shares FROM transactions WHERE strategy_id = ? AND ticker = ? AND type = 'sell'",
            (id, ticker),
        ).fetchall()

        total_buys = sum(b["price"] * b["shares"] for b in buys)
        total_sells = sum(s["price"] * s["shares"] for s in sells)
        net_spent = total_buys - total_sells
        weighted_price = round(net_spent / shares, 2) if shares else 0

        stock_return = (
            round(((price - weighted_price) / weighted_price * 100), 2)
            if weighted_price
            else 0
        )

        portfolio.append(
            {
                "ticker": ticker,
                "shares": shares,
                "price": price,
                "share_value": share_value,
                "weighted_price": weighted_price,
                "stock_return": stock_return,
            }
        )

    return {"portfolio": portfolio, "equity_value": round(equity_value, 2)}


# =====================================================
# Rename Strategy
# =====================================================
@bp.route("/api/rename-strategy/<int:id>", methods=["PUT"])
def rename_strategy(id):
    data = request.get_json(silent=True)
    new_name = (data.get("new_name", "").strip() if data else "")
    if not new_name:
        abort(400, description="Missing or empty new name.")

    db = get_db()
    try:
        result = db.execute("UPDATE strategy SET name = ? WHERE id = ?", (new_name, id))
        db.commit()
        if result.rowcount == 0:
            abort(404, description="Strategy not found.")
        return jsonify({"status": "success"})
    except IntegrityError:
        abort(400, description="A strategy with that name already exists.")
    finally:
        close_db()


# =====================================================
# Delete Strategy
# =====================================================
@bp.route("/api/delete-strategy/<int:id>", methods=["DELETE"])
def delete_strategy(id):
    db = get_db()
    try:
        # Verify existence before deletion
        row = db.execute("SELECT id FROM strategy WHERE id = ?", (id,)).fetchone()
        if not row:
            abort(404, description="Strategy not found.")

        db.execute("DELETE FROM portfolio WHERE strategy_id = ?", (id,))
        db.execute("DELETE FROM transactions WHERE strategy_id = ?", (id,))
        db.execute("DELETE FROM strategy WHERE id = ?", (id,))
        db.commit()

        return jsonify({"status": "deleted"})
    finally:
        close_db()
