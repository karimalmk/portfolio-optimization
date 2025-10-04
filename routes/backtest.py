from flask import Blueprint, render_template

bp = Blueprint('backtesting', __name__)

@bp.route("/backtest")
def backtest():
    return render_template("backtest.html")
    # TO DO: Implement backtesting logic