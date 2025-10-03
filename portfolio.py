def update_portfolio(user_id):
    symbols = db.execute("SELECT DISTINCT symbol FROM purchases WHERE user_id = ?", user_id)

    for row in symbols:
        symbol = row["symbol"]

        balance = db.execute(
            "SELECT COALESCE(SUM(shares), 0) AS total FROM purchases WHERE user_id = ? AND symbol = ?",
            user_id, symbol
        )[0]["total"]

        if balance > 0:
            db.execute(
                "INSERT INTO portfolio (user_id, symbol, shares) VALUES (?, ?, ?) "
                "ON CONFLICT(user_id, symbol) DO UPDATE SET shares = ?",
                user_id, symbol, balance, balance
            )
        else:
            db.execute("DELETE FROM portfolio WHERE user_id = ? AND symbol = ?", user_id, symbol)
