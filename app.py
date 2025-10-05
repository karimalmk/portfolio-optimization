import os
from flask import Flask, render_template
from helpers import register_error_handlers, get_db, usd, gbp, eur

# Importing blueprints
from routes.transactions import bp as transactions_bp
from routes.backtest import bp as backtest_bp
from index import bp as api_bp

# Application set-up
app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Register error handlers
register_error_handlers(app)

# Currency filters
app.jinja_env.filters["usd"] = usd
app.jinja_env.filters["gbp"] = gbp
app.jinja_env.filters["eur"] = eur

# Register blueprints
app.register_blueprint(transactions_bp)
app.register_blueprint(backtest_bp)
app.register_blueprint(api_bp)

# Root route
@app.route("/")
def index():
    db = get_db()
    rows = db.execute("SELECT id, name FROM strategy").fetchall()
    strategies = [{"id": row["id"], "name": row["name"]} for row in rows]
    print("Returning strategies:", strategies)
    return render_template("index.html", strategies=strategies)


@app.route("/transactions")
def transactions():
    return render_template("transactions.html")

# Run the application
if __name__ == "__main__":
    app.run(debug=True)