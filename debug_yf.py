import yfinance as yf
try:
    data = yf.download("AAPL BTC-USD", period="5d", auto_adjust=True)
    print("Data type:", type(data))
    print("Data columns:", data.columns)
    print("Data head:\n", data.head())
    print("Close head:\n", data['Close'].head())
except Exception as e:
    print("Error:", e)
