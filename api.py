import yfinance as yf

def lookup(ticker: str):
    """Look up quote for ticker symbol."""

    try:
        ticker = ticker.strip().upper()
        stock = yf.Ticker(ticker)
        info = stock.info  # fetches metadata & price info

        # Some tickers (like ETFs) might not have "longName"
        name = info.get("longName") or info.get("shortName") or ticker

        # Get the latest close or regular market price
        price = info.get("regularMarketPrice") or info.get("previousClose")
        if price is None:
            raise ValueError("No price data found.")

        return {
            "name": name,
            "ticker": ticker,
            "price": round(float(price), 2),
        }

    except Exception as e:
        print(f"Lookup error for {ticker}: {e}")
        return None


if __name__ == "__main__":
    data = lookup("AAPL")
    if data:
        print(data)