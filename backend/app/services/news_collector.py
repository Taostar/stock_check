"""Service to collect financial news for stocks."""

import yfinance as yf
from datetime import datetime
from typing import Optional
from cachetools import TTLCache
import asyncio
from concurrent.futures import ThreadPoolExecutor

from ..config import get_settings
from ..models.analysis import NewsItem


class NewsCollector:
    """Collects financial news for holdings using yfinance."""

    def __init__(self):
        self.settings = get_settings()
        self._cache = TTLCache(
            maxsize=100,
            ttl=self.settings.news_cache_minutes * 60
        )
        self._executor = ThreadPoolExecutor(max_workers=5)

    async def get_news_for_symbols(
        self,
        symbols: list[str],
        max_per_symbol: int = 5
    ) -> list[NewsItem]:
        """
        Get news for given symbols.

        Args:
            symbols: List of stock symbols
            max_per_symbol: Maximum news items per symbol

        Returns:
            List of NewsItem sorted by date (newest first)
        """
        cache_key = f"{','.join(sorted(symbols))}:{max_per_symbol}"

        # Check cache
        if cache_key in self._cache:
            return self._cache[cache_key]

        # Fetch news concurrently
        loop = asyncio.get_event_loop()
        tasks = [
            loop.run_in_executor(
                self._executor,
                self._get_news_for_symbol,
                symbol,
                max_per_symbol
            )
            for symbol in symbols
        ]

        results = await asyncio.gather(*tasks)

        # Flatten and sort by date
        all_news = []
        for news_list in results:
            all_news.extend(news_list)

        # Sort by published date, newest first
        all_news.sort(
            key=lambda x: x.published_at if x.published_at else datetime.min,
            reverse=True
        )

        # Cache results
        self._cache[cache_key] = all_news

        return all_news

    def _get_news_for_symbol(
        self,
        symbol: str,
        max_items: int
    ) -> list[NewsItem]:
        """
        Get news for a single symbol using yfinance.

        This runs in a thread pool.
        """
        try:
            ticker = yf.Ticker(symbol)
            news = ticker.news

            if not news:
                return []

            news_items = []

            for item in news[:max_items]:
                # Parse publish time
                published_at = None
                publish_time = item.get("providerPublishTime")
                if publish_time:
                    try:
                        published_at = datetime.fromtimestamp(publish_time)
                    except (ValueError, OSError):
                        pass

                # Get thumbnail URL
                thumbnail_url = None
                thumbnail = item.get("thumbnail")
                if thumbnail and isinstance(thumbnail, dict):
                    resolutions = thumbnail.get("resolutions", [])
                    if resolutions:
                        thumbnail_url = resolutions[0].get("url")

                news_items.append(NewsItem(
                    symbol=symbol,
                    title=item.get("title", ""),
                    publisher=item.get("publisher", "Unknown"),
                    link=item.get("link", ""),
                    published_at=published_at,
                    summary=None,  # yfinance doesn't provide summary
                    thumbnail_url=thumbnail_url
                ))

            return news_items

        except Exception:
            return []

    async def get_news_for_high_fluctuation(
        self,
        symbols: list[str]
    ) -> list[NewsItem]:
        """
        Get news specifically for high-fluctuation stocks.

        This is the same as get_news_for_symbols but clearly named
        for the use case of fetching news for alerted stocks.
        """
        return await self.get_news_for_symbols(symbols, max_per_symbol=3)

    def clear_cache(self):
        """Clear the news cache."""
        self._cache.clear()
