from sqlite3 import IntegrityError
from flask import Blueprint, request, abort, session, jsonify
from helpers import get_db, lookup

# Blueprint for API routes
api_bp = Blueprint("api", __name__)

# Create strategy
@api_bp.route("/api/create-strategy", methods=["POST"])
def create_strategy():
    db = get_db()
    name = request.form.get("name")
    cash = request.form.get("cash")
    if not name or not cash:
        return abort(400)
    try:
        cash = float(cash)
        if cash <= 0:
            return abort(400)
    except ValueError:
        return abort(400)
    try:
        db.execute("INSERT INTO strategy (name, cash) VALUES (?, ?)", (name, cash))
    except IntegrityError:
        db.close()
        return abort(400)  # Conflict: Strategy name already exists
    id = db.execute("SELECT last_insert_rowid()").fetchone()[0]
    db.commit()
    db.close()
    return jsonify({"id": id, "name": name})


# Select strategy
@api_bp.route("/api/select-strategy", methods=["GET"])
def select_strategy():
    db = get_db()
    rows = db.execute("SELECT id, name FROM strategy").fetchall()
    strategies = [{"id": row["id"], "name": row["name"]} for row in rows]
    session["strategy_id"] = strategies[0]["id"] if strategies else None
    db.commit()
    db.close()
    return jsonify({"strategies": strategies})


@api_bp.route("/api/portfolio/<int:strategy_id>", methods=["GET"])
def load_portfolio(strategy_id):
    db = get_db()
    
    rows = db.execute(
        "SELECT symbol, shares FROM portfolio WHERE strategy = ?", (strategy_id,)
    ).fetchall()
    
    portfolio = [{"symbol": row["symbol"], "shares": row["shares"]} for row in rows]
    
    db.close()
    return jsonify({"portfolio": portfolio})


# Delete strategy
@api_bp.route("/api/delete-strategy/<int:strategy_id>", methods=["DELETE"])
def delete_strategy(strategy_id):
    db = get_db()
    db.execute("DELETE FROM strategy WHERE id = ?", (strategy_id,))
    db.commit()
    db.close()
    return {"success": True}