from sqlite3 import IntegrityError
from flask import Blueprint, request, abort, jsonify
from helpers import get_db

bp = Blueprint("index", __name__)

# =====================================================
# CREATE STRATEGY
# =====================================================
@bp.route("/api/create-strategy", methods=["POST"])
def create_strategy():
    db = get_db()
    name = request.form.get("name")
    cash = request.form.get("cash")

    if not name or not cash:
        return abort(400, description="Missing name or cash")

    try:
        cash = float(cash)
        if cash <= 0:
            return abort(400, description="Invalid cash amount")
    except ValueError:
        return abort(400, description="Cash must be numeric")

    try:
        db.execute("INSERT INTO strategy (name, cash) VALUES (?, ?)", (name, cash))
    except IntegrityError:
        db.close()
        return abort(400, description="Strategy name must be unique")

    id = db.execute("SELECT last_insert_rowid()").fetchone()[0]
    db.commit()
    db.close()
    return jsonify({"id": id, "name": name})


# =====================================================
# CHECK IF STRATEGY LIST EXISTS
# =====================================================
@bp.route("/api/strategy-list-exists/", methods=["GET"])
def strategy_list_exists():
    db = get_db()
    strategy = db.execute("SELECT id FROM strategy LIMIT 1").fetchone()
    db.close()
    return jsonify({"exists": bool(strategy)})


# =====================================================
# GET STRATEGIES (for dropdown)
# =====================================================
@bp.route("/api/strategies", methods=["GET"])
def get_strategies():
    db = get_db()
    rows = db.execute("SELECT id, name FROM strategy ORDER BY id ASC").fetchall()
    db.close()
    strategies = [{"id": row["id"], "name": row["name"]} for row in rows]
    return jsonify({"strategies": strategies})


# =====================================================
# EDIT STRATEGIES (for rename/delete view)
# =====================================================
@bp.route("/api/edit-strategy", methods=["GET"])
def edit_strategy():
    db = get_db()
    rows = db.execute("SELECT id, name FROM strategy ORDER BY id ASC").fetchall()
    db.close()
    strategies = [{"id": row["id"], "name": row["name"]} for row in rows]
    return jsonify({"strategies": strategies})


# =====================================================
# LOAD PORTFOLIO FOR SELECTED STRATEGY
# =====================================================
@bp.route("/api/load-portfolio/<int:strategy_id>", methods=["GET"])
def load_portfolio(strategy_id):
    db = get_db()
    rows = db.execute(
        "SELECT symbol, shares FROM portfolio WHERE strategy = ?",
        (strategy_id,),
    ).fetchall()
    db.close()

    portfolio = [{"symbol": row["symbol"], "shares": row["shares"]} for row in rows]
    return jsonify({"portfolio": portfolio})


# =====================================================
# RENAME STRATEGY
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
        db.execute("UPDATE strategy SET name = ? WHERE id = ?", (new_name, strategy_id))
        db.commit()
    except IntegrityError:
        db.close()
        return abort(400, description="Name already exists")
    db.close()

    return jsonify({"status": "success", "new_name": new_name})


# =====================================================
# DELETE STRATEGY
# =====================================================
@bp.route("/api/delete-strategy/<int:strategy_id>", methods=["DELETE"])
def delete_strategy(strategy_id):
    db = get_db()
    db.execute("DELETE FROM strategy WHERE id = ?", (strategy_id,))
    db.commit()
    db.close()
    return jsonify({"status": "deleted"})