"""Service to fetch holdings from external endpoint."""

import httpx
from typing import Optional
from datetime import datetime

from ..config import get_settings
from ..models.holdings import Holding, HoldingsResponse


class HoldingsFetcher:
    """Fetches holdings data from configured ngrok endpoint."""

    def __init__(self):
        self.settings = get_settings()

    async def fetch_holdings(self) -> HoldingsResponse:
        """
        Fetch holdings from the configured endpoint.

        Returns:
            HoldingsResponse with list of holdings

        Raises:
            httpx.HTTPError: If the request fails
        """
        headers = {
            "ngrok-skip-browser-warning": "true",  # Skip ngrok interstitial page
            "User-Agent": "StockCheck/1.0",
        }
        if self.settings.holdings_auth_token:
            headers["Authorization"] = f"Bearer {self.settings.holdings_auth_token}"

        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.get(
                    self.settings.holdings_endpoint_url,
                    headers=headers
                )
                response.raise_for_status()
                data = response.json()

                # Parse holdings from response
                holdings = self._parse_holdings(data)

                # Calculate total value if prices are available
                total_value = sum(
                    h.market_value for h in holdings
                    if h.market_value is not None
                )

                return HoldingsResponse(
                    holdings=holdings,
                    total_value=total_value if total_value > 0 else None,
                    fetched_at=datetime.utcnow(),
                    source="ngrok"
                )
            except httpx.HTTPError as e:
                # Return empty holdings on error - let caller handle
                raise

    def _parse_holdings(self, data: dict | list) -> list[Holding]:
        """
        Parse holdings from various response formats.

        Supports formats:
        - List of holdings directly
        - Dict with 'holdings' key
        - Dict with 'data' key containing holdings
        """
        holdings_data = []

        if isinstance(data, list):
            holdings_data = data
        elif isinstance(data, dict):
            if "portfolio_holdings" in data:
                holdings_data = data["portfolio_holdings"]
            elif "holdings" in data:
                holdings_data = data["holdings"]
            elif "data" in data:
                holdings_data = data["data"]
            elif "positions" in data:
                holdings_data = data["positions"]
            else:
                # Try to use the dict as a single holding
                holdings_data = [data]

        holdings = []
        for item in holdings_data:
            holding = self._parse_single_holding(item)
            if holding:
                holdings.append(holding)

        return holdings

    def _parse_single_holding(self, item: dict) -> Optional[Holding]:
        """Parse a single holding from various key formats."""
        if not isinstance(item, dict):
            return None

        # Try various key names for symbol
        symbol = (
            item.get("symbol") or
            item.get("ticker") or
            item.get("Symbol") or
            item.get("Ticker")
        )

        if not symbol:
            return None

        # Parse other fields with fallbacks
        name = (
            item.get("name") or
            item.get("company") or
            item.get("Name") or
            item.get("companyName") or
            ""
        )

        shares = float(
            item.get("shares") or
            item.get("quantity") or
            item.get("open_quantity") or
            item.get("Shares") or
            item.get("Quantity") or
            0
        )

        average_cost = (
            item.get("average_cost") or
            item.get("averageCost") or
            item.get("average_entry_price") or
            item.get("cost_basis")
        )
        if average_cost:
            average_cost = float(average_cost)

        current_price = (
            item.get("current_price") or
            item.get("currentPrice") or
            item.get("price")
        )
        if current_price:
            current_price = float(current_price)

        market_value = (
            item.get("market_value") or
            item.get("marketValue") or
            item.get("current_market_value") or
            item.get("value")
        )
        if market_value:
            market_value = float(market_value)
        elif current_price and shares:
            market_value = current_price * shares

        sector = item.get("sector") or item.get("Sector")

        return Holding(
            symbol=symbol.upper(),
            name=name,
            shares=shares,
            average_cost=average_cost,
            current_price=current_price,
            market_value=market_value,
            sector=sector
        )

    def get_mock_holdings(self) -> HoldingsResponse:
        """Return mock holdings for testing when endpoint is unavailable."""
        mock_holdings = [
            Holding(symbol="AAPL", name="Apple Inc.", shares=100, average_cost=150.0),
            Holding(symbol="MSFT", name="Microsoft Corporation", shares=50, average_cost=350.0),
            Holding(symbol="GOOGL", name="Alphabet Inc.", shares=25, average_cost=140.0),
            Holding(symbol="TSLA", name="Tesla Inc.", shares=30, average_cost=200.0),
            Holding(symbol="NVDA", name="NVIDIA Corporation", shares=40, average_cost=500.0),
        ]

        return HoldingsResponse(
            holdings=mock_holdings,
            total_value=None,
            fetched_at=datetime.utcnow(),
            source="mock"
        )
