import yfinance as yf
from datetime import date, datetime, timedelta
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
    eastern_time = timezone("US/Eastern")
    now = datetime.now(eastern_time)
    time_now = now.time()
    date_now = now.date()
    weekday = now.weekday() < 5

    open_time = datetime.strptime("09:30:00", "%H:%M:%S").time()
    close_time = datetime.strptime("16:00:00", "%H:%M:%S").time()
    return {
        "market_open": (open_time <= time_now <= close_time) and weekday,
        "time_now": time_now,
        "date_now": date_now,
    }

def lookup(ticker: str, CACHE):
    status = check_market_status()
    ticker = (ticker or "").strip().upper()
    if not ticker:
        return None

    try:
        stock = yf.Ticker(ticker)
        info = stock.fast_info or {}
        date_now, time_now = status["date_now"], status["time_now"]
        if info is None: return {"ticker": ticker, "price": None, "time": time_now, "date": date_now, "error": "Info not found"}

        # Check cache first
        if ticker in CACHE:
            cached = CACHE[ticker]
            age = datetime.combine(date_now, time_now) - datetime.combine(cached["date"], cached["time"])
            if age < CACHE_TTL:
                return {"ticker": ticker, "price": cached["price"], "time": str(cached["time"])[:8], "date": str(cached["date"])}

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
            return {"ticker": ticker, "price": price, "time": str(time_now)[:8], "date": str(date_now)}
        else:
            return {"ticker": ticker, "price": None, "time": str(time_now)[:8], "date": str(date_now), "error": "Price not found"}

    except Exception as e:
        print(f"[lookup error] {ticker}: {e}")
        return {"ticker": ticker, "price": None, "time": str(time_now)[8:], "date": str(date_now), "error": str(e)}

if __name__ == "__main__":
    for symbol in ["AAPL", "MSFT", "GOOG", "INVALID"]:
        print(symbol, "→", lookup(symbol, CACHE))
    print("CACHE:", CACHE)
    print(lookup.__code__.co_varnames)