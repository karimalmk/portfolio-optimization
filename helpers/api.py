import yfinance as yf
from datetime import datetime, timedelta
from pytz import timezone

CACHE = {}
CACHE_TTL = timedelta(days=1)

def load_cache():
    global CACHE
    # Remove stale entries
    now = datetime.now()
    to_delete = [k for k, v in CACHE.items() if now - datetime.combine(v["date"], v["time"]) > CACHE_TTL]
    for k in to_delete:
        del CACHE[k]
    return CACHE

def check_market_status():
    tz = timezone("US/Eastern")
    now = datetime.now(tz)
    open_t = datetime.strptime("09:30:00", "%H:%M:%S").time()
    close_t = datetime.strptime("16:00:00", "%H:%M:%S").time()
    return {
        "market_open": (open_t <= now.time() <= close_t) and now.weekday() < 5,
        "time_now": now.time(),
        "date_now": now.date(),
    }

def lookup(ticker: str, CACHE):
    status = check_market_status()
    ticker = (ticker or "").strip().upper()
    if not ticker:
        return None

    try:
        stock = yf.Ticker(ticker)
        info = getattr(stock, "fast_info", {}) or {}
        date_now, time_now = status["date_now"], status["time_now"]

        # Check cache first
        if ticker in CACHE:
            cached = CACHE[ticker]
            age = datetime.combine(date_now, time_now) - datetime.combine(cached["date"], cached["time"])
            if age < CACHE_TTL:
                return {"ticker": ticker, "price": cached["price"]}

        if not status["market_open"]:
            price = info.get("previous_close") or info.get("previousClose")
            if not price:
                hist = stock.history(period="2d")
                if not hist.empty and "Close" in hist:
                    price = float(hist["Close"].iloc[-1])
        else:
            price = info.get("last_price") or info.get("lastPrice")
            if not price:
                hist = stock.history(period="1d", interval="1m")
                if not hist.empty and "Close" in hist:
                    price = float(hist["Close"].iloc[-1])

        if price:
            price = round(float(price), 2)
            CACHE[ticker] = {"ticker": ticker, "price": price, "time": time_now, "date": date_now}
            return {"ticker": ticker, "price": price}
        else:
            return {"ticker": ticker, "price": None}

    except Exception as e:
        print(f"[lookup error] {ticker}: {e}")
        return {"ticker": ticker, "price": None, "error": str(e)}

if __name__ == "__main__":
    for symbol in ["AAPL", "MSFT", "GOOG", "INVALID"]:
        print(symbol, "→", lookup(symbol, CACHE))
    print("CACHE:", CACHE)
    print(lookup.__code__.co_varnames)