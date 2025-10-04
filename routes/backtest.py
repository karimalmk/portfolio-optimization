from flask import Blueprint, render_template

backtest_bp = Blueprint('backtesting', __name__)

@backtest_bp.route("/backtest")
def backtest():
    return render_template("backtest.html")
    # TO DO: Implement backtesting logic