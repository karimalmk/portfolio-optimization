import requests
import sqlite3

db = sqlite3.connect("portfolio.db", check_same_thread=False)

###### TO DO: ADD A BACKTESTING PAGE #####

############ Defining stock quote lookup function #############
def lookup(symbol):
    """Look up quote for symbol."""
    url = f"https://finance.cs50.io/quote?symbol={symbol.upper()}"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for HTTP error responses
        quote_data = response.json()
        return {
            "name": quote_data["companyName"],
            "price": quote_data["latestPrice"],
            "symbol": symbol.upper()
        }
    except requests.RequestException as e:
        print(f"Request error: {e}")
    except (KeyError, ValueError) as e:
        print(f"Data parsing error: {e}")
    return None

############# Defining currency formatting functions #############
def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"

def gbp(value):
    """Format value as GBP."""
    return f"£{value:,.2f}"

def eur(value):
    """Format value as EUR."""
    return f"€{value:,.2f}"