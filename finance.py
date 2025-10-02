import yfinance as yf
import numpy as np

msft = yf.Ticker("MSFT")

hist = msft.history(period="5d")

# Round and collect closing prices
priceList = [round(price) for price in hist["Close"]]

print(priceList)

# Average price
averagePrice = np.mean(priceList)
print(averagePrice)

# Convert to NumPy array
arrayFormat = np.array(priceList)
arrayShape = arrayFormat.shape

print(arrayFormat)
print(arrayShape)