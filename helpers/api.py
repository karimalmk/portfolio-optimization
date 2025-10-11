import yfinance as yf
from datetime import datetime, timedelta
from pytz import timezone

EXCHANGES = {
    # 🇺🇸 United States
    "NYSE":   {"currency": "USD", "timezone": "America/New_York", "open": "09:30", "close": "16:00"},
    "NASDAQ": {"currency": "USD", "timezone": "America/New_York", "open": "09:30", "close": "16:00"},
    "AMEX":   {"currency": "USD", "timezone": "America/New_York", "open": "09:30", "close": "16:00"},
    "BATS":   {"currency": "USD", "timezone": "America/New_York", "open": "09:30", "close": "16:00"},

    # 🇨🇦 Canada
    "TSX":    {"currency": "CAD", "timezone": "America/Toronto", "open": "09:30", "close": "16:00"},
    "TSXV":   {"currency": "CAD", "timezone": "America/Toronto", "open": "09:30", "close": "16:00"},

    # 🇬🇧 United Kingdom
    "LSE":    {"currency": "GBP", "timezone": "Europe/London", "open": "08:00", "close": "16:30"},

    # 🇪🇺 Europe
    "FRA":    {"currency": "EUR", "timezone": "Europe/Berlin", "open": "09:00", "close": "17:30"},  # Frankfurt
    "GER":    {"currency": "EUR", "timezone": "Europe/Berlin", "open": "09:00", "close": "17:30"},  # alias
    "ETR":    {"currency": "EUR", "timezone": "Europe/Berlin", "open": "09:00", "close": "17:30"},  # Deutsche Börse Xetra
    "PAR":    {"currency": "EUR", "timezone": "Europe/Paris", "open": "09:00", "close": "17:30"},   # Euronext Paris
    "AMS":    {"currency": "EUR", "timezone": "Europe/Amsterdam", "open": "09:00", "close": "17:30"},
    "BRU":    {"currency": "EUR", "timezone": "Europe/Brussels", "open": "09:00", "close": "17:30"},
    "MIL":    {"currency": "EUR", "timezone": "Europe/Rome", "open": "09:00", "close": "17:30"},
    "VIE":    {"currency": "EUR", "timezone": "Europe/Vienna", "open": "09:00", "close": "17:30"},
    "CPH":    {"currency": "DKK", "timezone": "Europe/Copenhagen", "open": "09:00", "close": "17:00"},
    "STO":    {"currency": "SEK", "timezone": "Europe/Stockholm", "open": "09:00", "close": "17:30"},
    "HEL":    {"currency": "EUR", "timezone": "Europe/Helsinki", "open": "10:00", "close": "18:30"},
    "OSL":    {"currency": "NOK", "timezone": "Europe/Oslo", "open": "09:00", "close": "16:30"},

    # 🇨🇭 Switzerland
    "SIX":    {"currency": "CHF", "timezone": "Europe/Zurich", "open": "09:00", "close": "17:30"},

    # 🇯🇵 Japan
    "TSE":    {"currency": "JPY", "timezone": "Asia/Tokyo", "open": "09:00", "close": "15:00"},
    "JPX":    {"currency": "JPY", "timezone": "Asia/Tokyo", "open": "09:00", "close": "15:00"},

    # 🇭🇰 Hong Kong
    "HKEX":   {"currency": "HKD", "timezone": "Asia/Hong_Kong", "open": "09:30", "close": "16:00"},

    # 🇨🇳 China
    "SSE":    {"currency": "CNY", "timezone": "Asia/Shanghai", "open": "09:30", "close": "15:00"},
    "SZSE":   {"currency": "CNY", "timezone": "Asia/Shanghai", "open": "09:30", "close": "15:00"},

    # 🇮🇳 India
    "NSE":    {"currency": "INR", "timezone": "Asia/Kolkata", "open": "09:15", "close": "15:30"},
    "BSE":    {"currency": "INR", "timezone": "Asia/Kolkata", "open": "09:15", "close": "15:30"},

    # 🇦🇺 Australia
    "ASX":    {"currency": "AUD", "timezone": "Australia/Sydney", "open": "10:00", "close": "16:00"},

    # 🇧🇷 Brazil
    "BVMF":   {"currency": "BRL", "timezone": "America/Sao_Paulo", "open": "10:00", "close": "17:00"},

    # 🇲🇽 Mexico
    "MX":     {"currency": "MXN", "timezone": "America/Mexico_City", "open": "08:30", "close": "15:00"},

    # 🇸🇬 Singapore
    "SGX":    {"currency": "SGD", "timezone": "Asia/Singapore", "open": "09:00", "close": "17:00"},

    # 🇰🇷 South Korea
    "KRX":    {"currency": "KRW", "timezone": "Asia/Seoul", "open": "09:00", "close": "15:30"},

    # 🇿🇦 South Africa
    "JSE":    {"currency": "ZAR", "timezone": "Africa/Johannesburg", "open": "09:00", "close": "17:00"},
}


EXCHANGE_ALIASES = {
    # United States
    "NMS": "NASDAQ",
    "NGM": "NASDAQ",
    "NAS": "NASDAQ",
    "NYQ": "NYSE",
    "PCX": "NYSE",
    "ASE": "AMEX",
    "BATS": "BATS",

    # Canada
    "TOR": "TSX",
    "VAN": "TSXV",
    "TSX": "TSX",
    "CNQ": "TSX",

    # UK & Europe
    "LSE": "LSE",
    "LON": "LSE",
    "FRA": "FRA",
    "GER": "FRA",
    "ETR": "FRA",
    "PAH": "PAR",
    "PAR": "PAR",
    "AMS": "AMS",
    "BRU": "BRU",
    "MIL": "MIL",
    "VIE": "VIE",
    "CPH": "CPH",
    "STO": "STO",
    "HEL": "HEL",
    "OSL": "OSL",

    # Switzerland
    "SWX": "SIX",

    # Asia
    "HKG": "HKEX",
    "HKEX": "HKEX",
    "TSE": "TSE",
    "TYO": "TSE",
    "JPX": "TSE",
    "SHE": "SZSE",
    "SHG": "SSE",
    "NSE": "NSE",
    "BSE": "BSE",
    "ASX": "ASX",
    "SGX": "SGX",
    "KOE": "KRX",
    "KRX": "KRX",

    # Americas
    "SAO": "BVMF",
    "BVMF": "BVMF",
    "MEX": "MX",
    "MEXI": "MX",

    # Africa
    "JSE": "JSE",
}


CACHE = {}  # {"ticker": {"price": float, "time": datetime}}

# =====================================================
# Exchange Rate
# =====================================================
def get_exchange_rate(exchange: str):
    info = EXCHANGES.get(exchange)
    if not info:
        return None

    currency = info["currency"]
    if currency == "USD":
        return 1.0

    pair = f"USD{currency}=X"
    try:
        data = yf.Ticker(pair).info
        rate = data.get("regularMarketPrice") or data.get("previousClose")
        rate = float(rate) if rate else None
        return 1/rate if rate else None
    except Exception:
        return None


# =====================================================
# Market Status
# =====================================================
def check_market_status(exchange: str):
    tz_name = EXCHANGES[exchange]["timezone"]
    tz = timezone(tz_name)
    now = datetime.now(tz)
    country_open = EXCHANGES[exchange]["open"]
    country_close = EXCHANGES[exchange]["close"]
    open_t = datetime.strptime(country_open, "%H:%M").time()
    close_t = datetime.strptime(country_close, "%H:%M").time()
    weekday = now.weekday() < 5 # Applies for most exchanges; holidays not considered

    return {
        "market_open": (open_t <= now.time() <= close_t) and weekday,
        "time_now": now,
        "date_now": now.date(),
    }


# =====================================================
# Lookup Stock
# =====================================================
def lookup(ticker: str):
    ticker = (ticker or "").strip().upper()
    if not ticker:
        return {"ticker": ticker, "price": None, "error": "Invalid ticker"}

    try:
        info = yf.Ticker(ticker).info or {}
        exchange_code = info.get("exchange") or info.get("Exchange") or "N/A"
        exchange = EXCHANGE_ALIASES.get(exchange_code, exchange_code)

        if exchange not in EXCHANGES:
            return {"ticker": ticker, "price": None, "error": f"Unknown exchange '{exchange_code}'"}

        status = check_market_status(exchange)
        rate = get_exchange_rate(exchange)

        if status["market_open"]:
            price = info.get("regularMarketPrice")
        else:
            # Cached price
            if ticker in CACHE:
                price = CACHE[ticker]["price"]
            else:
                price = info.get("previousClose")
                if price:
                    CACHE[ticker] = {"price": price, "time": datetime.now()}

        if not price:
            return {"ticker": ticker, "price": None, "error": "Price not found"}

        price = round(float(price) * (rate or 1.0), 2)
        return {
            "ticker": ticker,
            "price": price,
            "date": str(status["date_now"]),
            "time": str(status["time_now"].time())[:8],
        }

    except Exception as e:
        print(f"[lookup error] {ticker}: {e}")
        return {"ticker": ticker, "price": None, "error": str(e)}


# =====================================================
# Test
# =====================================================
if __name__ == "__main__":
    for symbol in ["AAPL", "MSFT", "MC.PA", "INVALID"]:
        print(symbol, "→", lookup(symbol))
    print("\nCACHE:", CACHE)
