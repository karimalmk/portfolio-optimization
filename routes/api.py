# Create strategy
@app.route("/api/create-strategy", methods=["POST"])
def create_strategy():
    db = get_db()
    name = request.form.get("name")
    cash = request.form.get("cash")

    if not name or not cash:
        return abort(400)

    db.execute("INSERT INTO strategy (name, cash) VALUES (?, ?)", (name, cash))
    id = db.execute("SELECT last_insert_rowid()").fetchone()[0]
    db.close()
    return {"id": id, "name": name}

# Select strategy
@app.route("/api/select-strategy", methods=["GET"])
def select_strategy():
    db = get_db()
    rows = db.execute("SELECT id, name FROM strategy").fetchall()
    strategies = [{"id": row["id"], "name": row["name"]} for row in rows]
    db.close()
    return {"strategies": strategies} # flask automatically converts to JSON

# Load portfolio for a strategy
@app.route("/api/load-portfolio/<int:strategy_id>")
def get_portfolio(strategy_id):
    db = get_db()
    rows = db.execute(
        "SELECT symbol, shares FROM portfolio WHERE strategy = ?", (strategy_id,)
    ).fetchall()

    portfolio = []
    for row in rows:
        quote = lookup(row["symbol"])
        portfolio.append({
            "symbol": row["symbol"],
            "shares": row["shares"],
            "price": quote["price"],
            "total": quote["price"] * row["shares"]
        })

    cash_row = db.execute(
        "SELECT cash FROM strategy WHERE id = ?", (strategy_id,)
    ).fetchone()
    cash = cash_row["cash"] if cash_row else 0
    grand_total = sum(item["total"] for item in portfolio) + cash

    return {
        "cash": cash,
        "grand_total": grand_total,
        "portfolio": portfolio
    }


# Delete strategy
@app.route("/strategies/<int:strategy_id>", methods=["DELETE"])
def delete_strategy(strategy_id):
    db = get_db()
    db.execute("DELETE FROM strategy WHERE id = ?", (strategy_id,))
    db.commit()
    return {"success": True}