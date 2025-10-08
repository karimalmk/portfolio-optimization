from sqlite3 import IntegrityError
from flask import request, abort, jsonify

# Custom modules
from setup import get_db, close_db, create_blueprint, register_error_handlers
from api import lookup

# Blueprint setup
bp = create_blueprint("index")


# =====================================================
# Create Strategy
# =====================================================
@bp.route("/api/create-strategy", methods=["POST"])
def create_strategy():
    db = get_db()
    name = request.form.get("name")
    cash = request.form.get("cash")

    if not name or not cash:
        close_db()
        return abort(400, description="Missing name or cash")

    try:
        cash = float(cash)
        if cash <= 0:
            close_db()
            return abort(400, description="Invalid cash amount")
    except ValueError:
        close_db()
        return abort(400, description="Cash must be numeric")

    try:
        db.execute("INSERT INTO strategy (name, starting_cash, current_cash) VALUES (?, ?, ?)", (name, cash, cash))
        db.commit()
    except IntegrityError:
        close_db()
        return abort(400, description="Strategy name must be unique")

    strategy_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]
    close_db()
    return jsonify({"status": "success", "id": strategy_id, "name": name, "cash": cash}), 201


# =====================================================
# Get All Strategies
# =====================================================
@bp.route("/api/strategies", methods=["GET"])
def get_strategies():
    db = get_db()
    rows = db.execute("SELECT id, name, current_cash, total_value FROM strategy ORDER BY id ASC").fetchall()
    strategies = [
        {"id": row["id"], "name": row["name"], "cash": row["current_cash"], "total_value": row["total_value"]}
        for row in rows
    ]
    close_db()
    return jsonify({"strategies": strategies, "exists": bool(rows)}), 200


# =====================================================
# Get Portfolio & Overview
# =====================================================
@bp.route("/api/portfolio/<int:id>", methods=["GET"])
def display_portfolio(id):
    db = get_db()
    starting_cash = db.execute("SELECT starting_cash FROM strategy WHERE id = ?", (id,)).fetchone()[0]
    current_cash = db.execute("SELECT current_cash FROM strategy WHERE id = ?", (id,)).fetchone()[0]

    portfolio_analytics = get_portfolio_analytics(id, db, starting_cash, current_cash)
    total_value = portfolio_analytics["total_value"]
    overall_return = portfolio_analytics["overall_return"]
    portfolio = portfolio_analytics["portfolio"]

    # Update strategy total value in DB
    db.execute("UPDATE strategy SET total_value = ? WHERE id = ?", (total_value, id))

    overview = {
        "starting_cash": starting_cash,
        "current_cash": current_cash,
        "total_value": total_value,
        "overall_return": overall_return
    }

    db.commit()
    close_db()
    return jsonify({"portfolio": portfolio, "overview": overview}), 200


# Helper function to calculate portfolio analytics
def get_portfolio_analytics(id, db, starting_cash, current_cash):
    # Fetch all portfolio stocks
    portfolio_stocks = db.execute(
        "SELECT ticker, shares FROM portfolio WHERE strategy_id = ?", (id,)
    ).fetchall()

    portfolio = []
    total_value = current_cash  # Start with current cash
    for stock in portfolio_stocks:
        ticker = stock["ticker"]
        quote = lookup(ticker)
        if not quote or "price" not in quote:
            continue  # skip broken tickers instead of crashing
        share_price = quote["price"]
        shares = stock["shares"]
        total_share_value = shares * share_price
        
        # Adding each stock's contribution to total_value
        total_value += total_share_value
        
        purchase_list = db.execute(
            "SELECT price, shares FROM transactions WHERE strategy_id = ? AND ticker = ? AND type = 'buy'",
            (id, ticker)
        ).fetchall()

        sale_list = db.execute(
            "SELECT price, shares FROM transactions WHERE strategy_id = ? AND ticker = ? AND type = 'sell'",
            (id, ticker)
        ).fetchall()

        # Weighted average purchase price
        total_spend = sum(purchase["price"] * purchase["shares"] for purchase in purchase_list) - \
                      sum(sale["price"] * sale["shares"] for sale in sale_list)
        weighted_price = total_spend / shares if shares else 0

        # Calculate stock return
        stock_return = ((share_price - weighted_price) / weighted_price * 100) if weighted_price else 0
        stock_return = round(stock_return, 2)

        portfolio.append({
            "ticker": ticker,
            "shares": shares,
            "share_price": share_price,
            "total_share_value": total_share_value,
            "weighted_price": weighted_price,
            "stock_return": stock_return
        })

    total_value = round(total_value, 2)
    overall_return = ((total_value - starting_cash) / starting_cash * 100) if starting_cash else 0
    overall_return = round(overall_return, 2)

    return { "portfolio": (portfolio if portfolio else None), 
            "total_value": total_value, 
            "overall_return": overall_return }

# =====================================================
# Rename Strategy
# =====================================================
@bp.route("/api/rename-strategy/<int:strategy_id>", methods=["PUT"])
def rename_strategy(strategy_id):
    data = request.get_json()
    if not data or "new_name" not in data:
        return abort(400, description="Missing new name")

    new_name = data["new_name"].strip()
    if not new_name:
        return abort(400, description="Empty new name")

    db = get_db()
    try:
        result = db.execute("UPDATE strategy SET name = ? WHERE id = ?", (new_name, strategy_id))
        db.commit()
        if result.rowcount == 0:
            close_db()
            return abort(404, description="Strategy not found")
    except IntegrityError:
        close_db()
        return abort(400, description="Name already exists")

    close_db()
    return jsonify({"status": "success", "new_name": new_name}), 200


# =====================================================
# Delete Strategy
# =====================================================
@bp.route("/api/delete-strategy/<int:strategy_id>", methods=["DELETE"])
def delete_strategy(strategy_id):
    db = get_db()

    # Delete associated data if cascading is not enabled
    db.execute("DELETE FROM portfolio WHERE strategy_id = ?", (strategy_id,))
    db.execute("DELETE FROM transactions WHERE strategy_id = ?", (strategy_id,))
    db.execute("DELETE FROM strategy WHERE id = ?", (strategy_id,))
    db.commit()
    close_db()

    return jsonify({"status": "deleted", "strategy_id": strategy_id}), 200
