from crypt import methods
from datetime import datetime
from email.quoprimime import quote
from flask import Blueprint, request, session, redirect, abort, render_template
from helpers import get_db, lookup

bp = Blueprint('transactions', __name__)

@bp.route("/transactions/api/strategy", methods=["GET"])
def get_strategy():
    strategy = request.args.get("strategy")
    db = get_db()
    strategy_id = db.execute("SELECT id FROM strategy WHERE name = ?", (strategy,)).fetchone()[0]
    cash = db.execute("SELECT cash FROM strategy WHERE name = ?", (strategy,)).fetchone()[0]
    
    session["strategy"] = strategy
    session["strategy_id"] = strategy_id
    session["cash"] = cash
    
    db.close()
    return {"status": "success"}

@bp.route("/transactions/api/deposit", methods=["GET"])
def deposit():
    strategy = session.get("strategy")
    deposit = request.args.get("deposit")
    
    db = get_db()
    if deposit:
        old_amount = db.execute("SELECT cash FROM strategy WHERE name = ?", (strategy,)).fetchone()[0]
        db.execute("UPDATE strategy SET cash = ? WHERE name = ?", (old_amount + deposit, strategy))
        db.commit()
    return {"status": "success"}


@bp.route("/transactions/api/buy", methods=["GET"])
def buy():

    ticker = request.form.get("ticker")
    shares = request.form.get("shares")
    strategy = session.get("strategy")
    strategy_id = session.get("strategy_id")
    cash = session.get("cash")

    if not ticker or not shares:
        return abort(400)

    try:
        shares = int(shares)
        if shares <= 0:
            return abort(400)
    except ValueError:
        return abort(400)

    quote = lookup(ticker)
    if not quote:
        return abort(502)
    
    db = get_db()
    price = quote["price"]
    cost = price * shares
    
    if cost > cash:
        db.close()
        return abort(400)
    
    strategy_id = session.get("strategy_id")
    buy_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    db.execute("INSERT INTO transactions (type, ticker, shares, strategy, strategy_id, date) VALUES (?, ?, ?, ?, ?, ?)",
               ("buy", ticker, shares, strategy, strategy_id, buy_date))
    db.execute("UPDATE strategy SET cash = ? WHERE name = ?", (cash - cost, strategy))
    db.commit()
    db.close()
    return redirect("/transactions")

@bp.route("/transactions/api/sell", methods=["GET"])
def sell():

    ticker = request.form.get("ticker")
    shares = request.form.get("shares")
    strategy = session.get("strategy")
    strategy_id = session.get("strategy_id")
    cash = session.get("cash")

    if not ticker or not shares:
        return abort(400)

    try:
        shares = int(shares)
        if shares <= 0:
            return abort(400)
    except ValueError:
        return abort(400)

    quote = lookup(ticker)
    if not quote:
        return abort(502)

    price = quote["price"]
    if not price:
        return abort(502)
     
    db = get_db()
    existing_shares = db.execute("SELECT shares FROM portfolio WHERE symbol = ? AND strategy = ?", (ticker, strategy)).fetchone()[0]
    
    if existing_shares < shares:
        db.close()
        return abort(400)
    
    revenue = price * shares
    db = get_db()
    strategy_id = session.get("strategy_id")
    sell_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


    db.execute("INSERT INTO transactions (type, ticker, shares, strategy, strategy_id, date) VALUES (?, ?, ?, ?, ?, ?)",
               ("sell", ticker, shares, strategy, strategy_id, sell_date))
    db.execute("UPDATE strategy SET cash = ? WHERE name = ?", (cash + revenue, strategy))
    db.commit()
    db.close()
    return redirect("/transactions")