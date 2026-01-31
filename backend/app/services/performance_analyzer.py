"""Service to analyze stock performance and identify high-fluctuation stocks."""

import yfinance as yf
from typing import Optional
from datetime import datetime
import asyncio
from concurrent.futures import ThreadPoolExecutor

from ..config import get_settings
from ..models.holdings import Holding, HoldingPerformance, PerformanceResponse
from ..models.analysis import FluctuationAlert


class PerformanceAnalyzer:
    """Analyzes stock performance and identifies high-fluctuation stocks."""

    def __init__(self):
        self.settings = get_settings()
        self._executor = ThreadPoolExecutor(max_workers=10)

    async def analyze_holdings(
        self,
        holdings: list[Holding]
    ) -> PerformanceResponse:
        """
        Analyze performance for all holdings.

        Args:
            holdings: List of holdings to analyze

        Returns:
            PerformanceResponse with performance data for each holding
        """
        # Fetch performance data for all symbols concurrently
        loop = asyncio.get_event_loop()
        tasks = [
            loop.run_in_executor(
                self._executor,
                self._get_stock_performance,
                holding
            )
            for holding in holdings
        ]

        performances = await asyncio.gather(*tasks)

        # Filter out None results and count high fluctuations
        valid_performances = [p for p in performances if p is not None]
        high_fluctuation_count = sum(
            1 for p in valid_performances if p.is_high_fluctuation
        )

        # Calculate total market value
        total_value = sum(
            p.market_value for p in valid_performances
            if p.market_value is not None
        )

        return PerformanceResponse(
            holdings=valid_performances,
            high_fluctuation_count=high_fluctuation_count,
            total_value=total_value if total_value > 0 else None,
            analyzed_at=datetime.utcnow()
        )

    def _get_stock_performance(self, holding: Holding) -> Optional[HoldingPerformance]:
        """
        Get performance data for a single stock.

        This runs in a thread pool since yfinance is synchronous.
        """
        try:
            ticker = yf.Ticker(holding.symbol)
            info = ticker.info

            current_price = info.get("currentPrice") or info.get("regularMarketPrice")
            previous_close = info.get("previousClose") or info.get("regularMarketPreviousClose")

            # Calculate change
            change_amount = None
            change_percent = None
            is_high_fluctuation = False

            if current_price and previous_close:
                change_amount = current_price - previous_close
                change_percent = (change_amount / previous_close) * 100
                is_high_fluctuation = abs(change_percent) >= self.settings.fluctuation_threshold

            # Calculate market value
            market_value = None
            if current_price and holding.shares:
                market_value = current_price * holding.shares

            return HoldingPerformance(
                symbol=holding.symbol,
                name=holding.name or info.get("shortName", ""),
                shares=holding.shares,
                current_price=current_price,
                previous_close=previous_close,
                change_amount=change_amount,
                change_percent=change_percent,
                day_high=info.get("dayHigh"),
                day_low=info.get("dayLow"),
                volume=info.get("volume"),
                market_value=market_value,
                is_high_fluctuation=is_high_fluctuation
            )
        except Exception as e:
            # Return basic info on error
            return HoldingPerformance(
                symbol=holding.symbol,
                name=holding.name,
                shares=holding.shares,
                current_price=None,
                previous_close=None,
                is_high_fluctuation=False
            )

    def get_fluctuation_alerts(
        self,
        performances: list[HoldingPerformance]
    ) -> list[FluctuationAlert]:
        """
        Extract fluctuation alerts from performance data.

        Args:
            performances: List of holding performances

        Returns:
            List of FluctuationAlert for stocks meeting threshold
        """
        alerts = []

        for p in performances:
            if p.is_high_fluctuation and p.change_percent is not None:
                alerts.append(FluctuationAlert(
                    symbol=p.symbol,
                    name=p.name,
                    change_percent=p.change_percent,
                    change_amount=p.change_amount,
                    current_price=p.current_price,
                    previous_close=p.previous_close,
                    direction="up" if p.change_percent > 0 else "down",
                    volume=p.volume
                ))

        # Sort by absolute change, highest first
        alerts.sort(key=lambda x: abs(x.change_percent), reverse=True)

        return alerts

    async def get_quick_quote(self, symbol: str) -> Optional[dict]:
        """Get a quick quote for a single symbol."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self._executor,
            self._fetch_quote,
            symbol
        )

    def _fetch_quote(self, symbol: str) -> Optional[dict]:
        """Fetch quote data synchronously."""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            current_price = info.get("currentPrice") or info.get("regularMarketPrice")
            previous_close = info.get("previousClose")

            change_percent = None
            if current_price and previous_close:
                change_percent = ((current_price - previous_close) / previous_close) * 100

            return {
                "symbol": symbol,
                "name": info.get("shortName", ""),
                "price": current_price,
                "previous_close": previous_close,
                "change_percent": change_percent,
                "day_high": info.get("dayHigh"),
                "day_low": info.get("dayLow"),
                "volume": info.get("volume"),
            }
        except Exception:
            return None
