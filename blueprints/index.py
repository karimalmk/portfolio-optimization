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
        db.execute("INSERT INTO strategy (name, cash) VALUES (?, ?)", (name, cash))
        db.commit()
    except IntegrityError:
        close_db()
        return abort(400, description="Strategy name must be unique")

    strategy_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]
    close_db()
    return jsonify({"id": strategy_id, "name": name, "cash": cash}), 201


# =====================================================
# Get All Strategies
# =====================================================
@bp.route("/api/strategies", methods=["GET"])
def get_strategies():
    db = get_db()
    rows = db.execute("SELECT id, name, cash, total_value FROM strategy ORDER BY id ASC").fetchall()
    strategies = [
        {"id": row["id"], "name": row["name"], "cash": row["cash"], "total_value": row["total_value"]}
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
    update_portfolio(db, id)

    # Fetch strategy overview data
    overview_row = db.execute(
        "SELECT cash, total_value FROM strategy WHERE id = ?", (id,)
    ).fetchone()
    overview = {"cash": overview_row["cash"], "total_value": overview_row["total_value"]} if overview_row else None
    
    # Fetch all holdings
    rows = db.execute(
        "SELECT ticker, shares FROM portfolio WHERE strategy_id = ?", (id,)
    ).fetchall()

    if not rows:
        close_db()
        return jsonify({"portfolio": [], "overview": overview}), 200

    portfolio = []
    for row in rows:
        quote = lookup(row["ticker"])
        if not quote or "price" not in quote:
            continue
        share_price = quote["price"]
        total_share_value = row["shares"] * share_price
        portfolio.append({
            "ticker": row["ticker"],
            "shares": row["shares"],
            "share_price": share_price,
            "total_share_value": total_share_value
        })

    close_db()
    return jsonify({"portfolio": portfolio, "overview": overview}), 200



def update_portfolio(db, strategy_id):
    """Recalculate and update total portfolio value for a strategy."""
    rows = db.execute("SELECT ticker, shares FROM portfolio WHERE strategy_id = ?", (strategy_id,)).fetchall()
    total_value = 0

    for row in rows:
        quote = lookup(row["ticker"])
        if not quote or "price" not in quote:
            continue  # skip broken tickers instead of crashing
        total_value += row["shares"] * quote["price"]

    cash_row = db.execute("SELECT cash FROM strategy WHERE id = ?", (strategy_id,)).fetchone()
    cash = cash_row["cash"] if cash_row else 0
    db.execute("UPDATE strategy SET total_value = ? WHERE id = ?", (total_value + cash, strategy_id))
    db.commit()


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
