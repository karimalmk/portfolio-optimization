from sqlite3 import IntegrityError
from flask import Blueprint, request, abort, session, jsonify
from helpers import get_db, lookup

bp = Blueprint("api", __name__)

# -------------------------------
# CREATE STRATEGY
# -------------------------------
@bp.route("/api/create-strategy", methods=["POST"])
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
        return abort(400)

    id = db.execute("SELECT last_insert_rowid()").fetchone()[0]
    db.commit()
    db.close()
    return jsonify({"id": id, "name": name})


# -------------------------------
# GET STRATEGIES
# -------------------------------
@bp.route("/api/edit-strategy", methods=["GET"])
def edit_strategy():
    db = get_db()
    rows = db.execute("SELECT id, name FROM strategy").fetchall()
    db.close()
    strategies = [{"id": row["id"], "name": row["name"]} for row in rows]
    return jsonify({"strategies": strategies})


# -------------------------------
# LOAD PORTFOLIO
# -------------------------------
@bp.route("/api/portfolio/<int:strategy_id>", methods=["GET"])
def load_portfolio(strategy_id):
    db = get_db()
    rows = db.execute(
        "SELECT symbol, shares FROM portfolio WHERE strategy = ?", (strategy_id,)
    ).fetchall()
    portfolio = [{"symbol": row["symbol"], "shares": row["shares"]} for row in rows]
    db.close()
    return jsonify({"portfolio": portfolio})


# -------------------------------
# RENAME STRATEGY
# -------------------------------
@bp.route("/api/rename-strategy/<int:strategy_id>", methods=["PUT"])
def rename_strategy(strategy_id):
    data = request.get_json()
    new_name = data.get("new_name")
    if not new_name:
        return abort(400)

    db = get_db()
    db.execute("UPDATE strategy SET name = ? WHERE id = ?", (new_name, strategy_id))
    db.commit()
    db.close()
    return jsonify({"status": "success"})


# -------------------------------
# DELETE STRATEGY
# -------------------------------
@bp.route("/api/delete-strategy/<int:strategy_id>", methods=["DELETE"])
def delete_strategy(strategy_id):
    db = get_db()
    db.execute("DELETE FROM strategy WHERE id = ?", (strategy_id,))
    db.commit()
    db.close()
    return jsonify({"status": "deleted"})
