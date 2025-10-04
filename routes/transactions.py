from datetime import datetime
from flask import request, session, redirect, abort, render_template
from helpers import get_db, lookup

def buy():
    db = get_db()
    if request.method == "GET":
        db.close()
        return render_template("buy.html")

    symbol = request.form.get("symbol", "").strip().upper()
    shares = request.form.get("shares")

    if not symbol or not shares:
        db.close()
        return abort(400)

    try:
        shares = int(shares)
        if shares <= 0:
            db.close()
            return abort(400)
    except ValueError:
        db.close()
        return abort(400)

    quote = lookup(symbol)
    if not quote:
        db.close()
        return abort(502)

    strategy = session.get("strategy")
    if not strategy:
        db.close()
        return redirect("/")
    cash = db.execute("SELECT cash FROM strategy WHERE name = ?", (strategy,)).fetchone()[0]
    price = quote["price"]
    cost = price * shares
    
    if cost > cash:
        db.close()
        return abort(400)
    buy_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Record purchase
    db.execute("INSERT INTO buy (symbol, price, shares, buy_date, strategy) VALUES (?, ?, ?, ?, ?)",
               (symbol, price, shares, buy_date, strategy))

    # Update portfolio
    db.execute("""
        INSERT INTO portfolio (symbol, shares, strategy)
        VALUES (?, ?, ?)
        ON CONFLICT(strategy, symbol) DO UPDATE
        SET shares = shares + excluded.shares
    """, (symbol, shares, strategy))

    # Update cash
    db.execute("UPDATE strategy SET cash = ? WHERE name = ?", (cash - cost, strategy))
    db.commit()

    db.close()
    return redirect("/")

# Sell route
def sell():
    db = get_db()
    if request.method == "GET":
        db.close()
        return render_template("sell.html")

    symbol = request.form.get("symbol", "").strip().upper()
    shares = request.form.get("shares")

    if not symbol or not shares:
        db.close()
        return abort(400)

    try:
        shares = int(shares)
        if shares <= 0:
            db.close()
            return abort(400)
    except ValueError:
        db.close()
        return abort(400)

    quote = lookup(symbol)
    if not quote:
        db.close()
        return abort(502)

    strategy = session.get("strategy")
    if not strategy:
        db.close()
        return redirect("/")

    # Check holdings
    portfolio_rows = db.execute(
        "SELECT shares FROM portfolio WHERE strategy = ? AND symbol = ?", (strategy, symbol)).fetchone()[0]
    if not portfolio_rows:
        db.close()
        return abort(400)

    holdings = portfolio_rows[0]["shares"]
    if shares > holdings:
        db.close()
        return abort(400)

    price = quote["price"]
    sell_value = price * shares

    sell_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Record sale and update balances
    db.execute("INSERT INTO sell (symbol, price, shares, sell_date, strategy) VALUES (?, ?, ?, ?, ?)",
               (symbol, price, shares, sell_date, strategy))

    remaining = holdings - shares
    
    if remaining > 0:
        db.execute("UPDATE portfolio SET shares = ? WHERE strategy = ? AND symbol = ?",
                   (remaining, strategy, symbol))
    else:
        db.execute("DELETE FROM portfolio WHERE strategy = ? AND symbol = ?", (strategy, symbol))

    cash = db.execute("SELECT cash FROM strategy WHERE name = ?", (strategy,)).fetchone()[0]
    db.execute("UPDATE strategy SET cash = ? WHERE name = ?", (cash + sell_value, strategy))
    db.commit()

    db.close()
    return redirect("/")