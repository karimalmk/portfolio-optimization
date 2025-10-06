import requests
import sqlite3
from flask import render_template
from werkzeug.exceptions import HTTPException

## ============================
## Defining error handlers
## ============================
def register_error_handlers(app):

    @app.errorhandler(400)
    def bad_request(e):
        return render_template("error.html", message="Bad request – user input error"), 400

    @app.errorhandler(404)
    def not_found(e):
        return render_template("error.html", message="Page not found"), 404
    
    @app.errorhandler(500)
    def internal_error(e):
        return render_template("error.html", message="Server error"), 500

    @app.errorhandler(502)
    def api_error(e):
        return render_template("error.html", message="API error – service unavailable"), 502

    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        return render_template("error.html", message=e.description), e.code

## ========================================
## Defining database connection function
## ========================================
def get_db():
    db = sqlite3.connect("portfolio.db")
    db.row_factory = sqlite3.Row
    return db

## =======================================
## Defining stock quote lookup function
## =======================================
def lookup(ticker):
    
    price = 50.00  # Mock price for testing
    return {"name": "Mock Company", "ticker": ticker.upper(), "price": price}

    '''
    """Look up quote for ticker."""
    url = f"https://finance.cs50.io/quote?ticker={ticker.upper()}"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for HTTP error responses
        quote_data = response.json()
        return {
            "name": quote_data["companyName"],
            "price": quote_data["latestPrice"],
            "ticker": ticker.upper()
        }
    except requests.RequestException as e:
        print(f"Request error: {e}")
    except (KeyError, ValueError) as e:
        print(f"Data parsing error: {e}")
    return None
    '''

## ========================================
## Defining currency formatting functions
## ========================================
def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"

def gbp(value):
    """Format value as GBP."""
    return f"£{value:,.2f}"

def eur(value):
    """Format value as EUR."""
    return f"€{value:,.2f}"