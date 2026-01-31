"""Stock data endpoints - refactored from original main.py."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import yfinance as yf
import pandas as pd
from typing import List

router = APIRouter(prefix="/api", tags=["stocks"])


@router.get("/stock/{ticker}")
def get_stock_info(ticker: str):
    """Get detailed stock information for a single ticker."""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        data = {
            "symbol": info.get("symbol", ticker),
            "shortName": info.get("shortName", ""),
            "longName": info.get("longName", ""),
            "currency": info.get("currency", "USD"),
            "currentPrice": info.get("currentPrice") or info.get("regularMarketPrice"),
            "marketCap": info.get("marketCap"),
            "dayHigh": info.get("dayHigh"),
            "dayLow": info.get("dayLow"),
            "previousClose": info.get("previousClose"),
            "fiftyTwoWeekHigh": info.get("fiftyTwoWeekHigh"),
            "fiftyTwoWeekLow": info.get("fiftyTwoWeekLow"),
            "sector": info.get("sector", "N/A"),
            "description": info.get("longBusinessSummary", "N/A")
        }

        return data
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching data for {ticker}: {str(e)}"
        )


@router.get("/history/{ticker}")
def get_stock_history(ticker: str, period: str = "1mo"):
    """
    Fetch historical data for a stock.

    Valid periods: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
    """
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period)

        if hist.empty:
            raise HTTPException(status_code=404, detail="No historical data found")

        hist = hist.reset_index()

        data = []
        for index, row in hist.iterrows():
            date_str = row['Date'].strftime('%Y-%m-%d')
            data.append({
                "date": date_str,
                "open": row['Open'],
                "high": row['High'],
                "low": row['Low'],
                "close": row['Close'],
                "volume": row['Volume']
            })

        return data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching history for {ticker}: {str(e)}"
        )


class CompareRequest(BaseModel):
    """Request model for comparing multiple stocks."""
    tickers: List[str]
    period: str = "1mo"


@router.post("/compare")
def compare_stocks(request: CompareRequest):
    """
    Fetch history for multiple tickers.

    Returns a unified list of dates with prices for each ticker.
    """
    try:
        if not request.tickers:
            raise HTTPException(status_code=400, detail="No tickers provided")

        tickers_str = " ".join(request.tickers)
        data = yf.download(tickers_str, period=request.period, auto_adjust=True)['Close']

        if data.empty:
            raise HTTPException(status_code=404, detail="No data found")

        if isinstance(data, pd.Series):
            data = data.to_frame(name=request.tickers[0])

        data = data.reset_index()

        result = []
        for index, row in data.iterrows():
            item = {"date": row['Date'].strftime('%Y-%m-%d')}
            for ticker in request.tickers:
                val = row.get(ticker)
                if val is None and ticker.upper() in row:
                    val = row[ticker.upper()]

                if pd.notna(val):
                    item[ticker] = val
                else:
                    item[ticker] = None
            result.append(item)

        return result

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in compare: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error comparing stocks: {str(e)}"
        )
