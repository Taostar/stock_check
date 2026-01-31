"""Service to collect upcoming earnings data."""

import httpx
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from typing import Optional
from cachetools import TTLCache
import asyncio
from concurrent.futures import ThreadPoolExecutor
import yfinance as yf

from ..config import get_settings
from ..models.analysis import EarningsEvent


class EarningsCollector:
    """Collects upcoming earnings data for holdings."""

    def __init__(self):
        self.settings = get_settings()
        self._cache = TTLCache(
            maxsize=100,
            ttl=self.settings.earnings_cache_hours * 3600
        )
        self._executor = ThreadPoolExecutor(max_workers=5)

    async def get_earnings_for_symbols(
        self,
        symbols: list[str]
    ) -> list[EarningsEvent]:
        """
        Get upcoming earnings for given symbols.

        Uses yfinance calendar data as primary source.

        Args:
            symbols: List of stock symbols

        Returns:
            List of EarningsEvent for stocks with upcoming earnings
        """
        cache_key = ",".join(sorted(symbols))

        # Check cache
        if cache_key in self._cache:
            return self._cache[cache_key]

        # Fetch earnings concurrently
        loop = asyncio.get_event_loop()
        tasks = [
            loop.run_in_executor(
                self._executor,
                self._get_earnings_for_symbol,
                symbol
            )
            for symbol in symbols
        ]

        results = await asyncio.gather(*tasks)

        # Filter valid results and sort by date
        earnings = [e for e in results if e is not None]
        earnings.sort(key=lambda x: x.earnings_date)

        # Cache results
        self._cache[cache_key] = earnings

        return earnings

    def _get_earnings_for_symbol(self, symbol: str) -> Optional[EarningsEvent]:
        """
        Get earnings data for a single symbol using yfinance.

        This runs in a thread pool.
        """
        try:
            ticker = yf.Ticker(symbol)

            # Get earnings dates from calendar
            calendar = ticker.calendar

            if calendar is None or calendar.empty:
                return None

            # yfinance returns earnings date in various formats
            earnings_date = None

            if isinstance(calendar, dict):
                earnings_date = calendar.get("Earnings Date")
            elif hasattr(calendar, 'to_dict'):
                cal_dict = calendar.to_dict()
                if 'Earnings Date' in cal_dict:
                    earnings_date = cal_dict['Earnings Date']

            if earnings_date is None:
                # Try to get from info
                info = ticker.info
                earnings_timestamp = info.get("earningsTimestamp")
                if earnings_timestamp:
                    earnings_date = datetime.fromtimestamp(earnings_timestamp)

            if earnings_date is None:
                return None

            # Handle list of dates (sometimes yfinance returns range)
            if isinstance(earnings_date, list):
                earnings_date = earnings_date[0] if earnings_date else None

            if earnings_date is None:
                return None

            # Ensure it's a datetime
            if not isinstance(earnings_date, datetime):
                if hasattr(earnings_date, 'to_pydatetime'):
                    earnings_date = earnings_date.to_pydatetime()
                else:
                    return None

            # Only include upcoming earnings (within next 30 days)
            now = datetime.now()
            days_until = (earnings_date - now).days

            if days_until < 0 or days_until > 30:
                return None

            # Get additional info
            info = ticker.info
            name = info.get("shortName", symbol)

            # Try to get estimates
            eps_estimate = None
            revenue_estimate = None

            if isinstance(calendar, dict):
                eps_estimate = calendar.get("Earnings Average")
                revenue_estimate = calendar.get("Revenue Average")

            return EarningsEvent(
                symbol=symbol,
                name=name,
                earnings_date=earnings_date,
                time_of_day=None,  # yfinance doesn't reliably provide this
                eps_estimate=eps_estimate,
                revenue_estimate=revenue_estimate,
                days_until=days_until
            )

        except Exception as e:
            # Silently skip symbols with errors
            return None

    async def scrape_nasdaq_earnings(self, symbols: list[str]) -> list[EarningsEvent]:
        """
        Scrape NASDAQ earnings calendar as backup source.

        Note: This is a backup method - NASDAQ may block scraping.
        """
        try:
            url = "https://www.nasdaq.com/market-activity/earnings"
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            }

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()

                soup = BeautifulSoup(response.text, "lxml")

                earnings = []
                symbols_set = set(s.upper() for s in symbols)

                # Parse earnings table (structure may vary)
                table = soup.find("table", {"class": "earnings-table"})
                if not table:
                    return []

                rows = table.find_all("tr")[1:]  # Skip header

                for row in rows:
                    cols = row.find_all("td")
                    if len(cols) < 3:
                        continue

                    symbol = cols[0].get_text(strip=True).upper()

                    if symbol not in symbols_set:
                        continue

                    # Parse date
                    date_str = cols[1].get_text(strip=True)
                    try:
                        earnings_date = datetime.strptime(date_str, "%m/%d/%Y")
                    except ValueError:
                        continue

                    days_until = (earnings_date - datetime.now()).days

                    earnings.append(EarningsEvent(
                        symbol=symbol,
                        name=cols[2].get_text(strip=True) if len(cols) > 2 else symbol,
                        earnings_date=earnings_date,
                        days_until=days_until
                    ))

                return earnings

        except Exception:
            return []

    def clear_cache(self):
        """Clear the earnings cache."""
        self._cache.clear()
