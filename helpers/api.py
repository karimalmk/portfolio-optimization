import yfinance as yf
from datetime import datetime, timedelta
from pytz import timezone

EXCHANGES = {
    # 🇺🇸 United States
    "NYSE":   {"currency": "USD", "timezone": "America/New_York"},
    "NASDAQ": {"currency": "USD", "timezone": "America/New_York"},
    "AMEX":   {"currency": "USD", "timezone": "America/New_York"},
    "BATS":   {"currency": "USD", "timezone": "America/New_York"},

    # 🇨🇦 Canada
    "TSX":    {"currency": "CAD", "timezone": "America/Toronto"},
    "TSXV":   {"currency": "CAD", "timezone": "America/Toronto"},

    # 🇬🇧 United Kingdom
    "LSE":    {"currency": "GBP", "timezone": "Europe/London"},

    # 🇪🇺 Europe
    "FRA":    {"currency": "EUR", "timezone": "Europe/Berlin"},  # Frankfurt
    "GER":    {"currency": "EUR", "timezone": "Europe/Berlin"},  # alias
    "ETR":    {"currency": "EUR", "timezone": "Europe/Berlin"},  # Deutsche Börse Xetra
    "PAR":    {"currency": "EUR", "timezone": "Europe/Paris"},   # Euronext Paris
    "AMS":    {"currency": "EUR", "timezone": "Europe/Amsterdam"},
    "BRU":    {"currency": "EUR", "timezone": "Europe/Brussels"},
    "MIL":    {"currency": "EUR", "timezone": "Europe/Rome"},
    "VIE":    {"currency": "EUR", "timezone": "Europe/Vienna"},
    "CPH":    {"currency": "DKK", "timezone": "Europe/Copenhagen"},
    "STO":    {"currency": "SEK", "timezone": "Europe/Stockholm"},
    "HEL":    {"currency": "EUR", "timezone": "Europe/Helsinki"},
    "OSL":    {"currency": "NOK", "timezone": "Europe/Oslo"},

    # 🇨🇭 Switzerland
    "SIX":    {"currency": "CHF", "timezone": "Europe/Zurich"},

    # 🇯🇵 Japan
    "TSE":    {"currency": "JPY", "timezone": "Asia/Tokyo"},
    "JPX":    {"currency": "JPY", "timezone": "Asia/Tokyo"},

    # 🇭🇰 Hong Kong
    "HKEX":   {"currency": "HKD", "timezone": "Asia/Hong_Kong"},

    # 🇨🇳 China
    "SSE":    {"currency": "CNY", "timezone": "Asia/Shanghai"},
    "SZSE":   {"currency": "CNY", "timezone": "Asia/Shanghai"},

    # 🇮🇳 India
    "NSE":    {"currency": "INR", "timezone": "Asia/Kolkata"},
    "BSE":    {"currency": "INR", "timezone": "Asia/Kolkata"},

    # 🇦🇺 Australia
    "ASX":    {"currency": "AUD", "timezone": "Australia/Sydney"},

    # 🇧🇷 Brazil
    "BVMF":   {"currency": "BRL", "timezone": "America/Sao_Paulo"},

    # 🇲🇽 Mexico
    "MX":     {"currency": "MXN", "timezone": "America/Mexico_City"},

    # 🇸🇬 Singapore
    "SGX":    {"currency": "SGD", "timezone": "Asia/Singapore"},

    # 🇰🇷 South Korea
    "KRX":    {"currency": "KRW", "timezone": "Asia/Seoul"},

    # 🇿🇦 South Africa
    "JSE":    {"currency": "ZAR", "timezone": "Africa/Johannesburg"},
}


EXCHANGE_ALIASES = {
    # United States
    "NMS": "NASDAQ",
    "NGM": "NASDAQ",
    "NAS": "NASDAQ",
    "NYQ": "NYSE",
    "PCX": "NYSE",   # NYSE Arca
    "ASE": "AMEX",
    "BATS": "BATS",

    # Canada
    "TOR": "TSX",
    "VAN": "TSXV",
    "TSX": "TSX",
    "CNQ": "TSX",  # Canadian Securities Exchange

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
CACHE_UPDATE = timedelta(hours=1)

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

    pair = f"{currency}USD=X"
    try:
        data = yf.Ticker(pair).info
        rate = data.get("regularMarketPrice") or data.get("previousClose")
        return float(rate) if rate else None
    except Exception:
        return None


# =====================================================
# Market Status
# =====================================================
def check_market_status(tz_name: str):
    tz = timezone(tz_name)
    now = datetime.now(tz)
    open_t = datetime.strptime("09:30:00", "%H:%M:%S").time()
    close_t = datetime.strptime("16:00:00", "%H:%M:%S").time()
    weekday = now.weekday() < 5

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

        tz_name = EXCHANGES[exchange]["timezone"]
        status = check_market_status(tz_name)
        rate = get_exchange_rate(exchange)

        if status["market_open"]:
            CACHE.pop(ticker, None)
            price = info.get("regularMarketPrice")
        else:
            # Cached price
            if ticker in CACHE and datetime.now() - CACHE[ticker]["time"] < CACHE_UPDATE:
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
