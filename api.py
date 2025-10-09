import yfinance as yf
from datetime import datetime
from pytz import timezone

def check_market_status():
    time_zone = timezone("US/Eastern")
    fulle_date = datetime.now(time_zone)
    time_now = fulle_date.time()
    date_now = fulle_date.date()
    
    # US. stock market market open/close times (Eastern Time)
    opening_time = datetime.strptime("09:30:00", "%H:%M:%S").time()
    closing_time = datetime.strptime("16:00:00", "%H:%M:%S").time()

    if time_now < opening_time or time_now > closing_time or date_now.weekday() >= 5:
        return {"market_open": False, "time_now": time_now, "date_now": date_now}
    return {"market_open": True, "time_now": time_now, "date_now": date_now}

def lookup(db, ticker: str):
    # Market status
    market_status = check_market_status()
    market_open = market_status["market_open"]
    time_now = market_status["time_now"]
    date_now = market_status["date_now"] 
    
    # Meta data
    ticker = ticker.strip().upper()
    stock = yf.Ticker(ticker)
    info = stock.fast_info
    
    # Setting default values
    name = None
    price = None # default value
    cached_quote = None # default value

    if not name:
        name = info.get("shortName", None)
    
     # Use cached quote outside trading hours
    if not market_open:    
        if cached_quote:
            price = db.execute("SELECT quote FROM queries WHERE ticker = ?", (ticker,))
            return {
                "name": name,
                "ticker": ticker,
                "price": ticker,
                "price": price,
                "time": time_now,
                "date": date_now,
                }
        pass

    # Make API request during trading hours
    try:
        price = stock.fast_info.get("lastPrice", None)
        if price is None or name is None:
            raise ValueError("Missing data.")
        price = round(price, 2)

        return {
            "name": name,
            "ticker": ticker,
            "price": ticker,
            "price": price,
            "time": time_now,
            "date": date_now,
        }

    except Exception as e:
        print(f"Lookup error for {ticker}: {e}")
        return None
    
if __name__ == "__main__":
    result = lookup(None, "AAPL")
    print(result["time"])