"""Holdings endpoints for fetching and analyzing portfolio holdings."""

from fastapi import APIRouter, HTTPException, Depends
import httpx

from ..services.holdings_fetcher import HoldingsFetcher
from ..services.performance_analyzer import PerformanceAnalyzer
from ..models.holdings import HoldingsResponse, PerformanceResponse

router = APIRouter(prefix="/api/holdings", tags=["holdings"])


def get_holdings_fetcher() -> HoldingsFetcher:
    """Dependency to get holdings fetcher instance."""
    return HoldingsFetcher()


def get_performance_analyzer() -> PerformanceAnalyzer:
    """Dependency to get performance analyzer instance."""
    return PerformanceAnalyzer()


@router.get("", response_model=HoldingsResponse)
async def get_holdings(
    use_mock: bool = False,
    fetcher: HoldingsFetcher = Depends(get_holdings_fetcher)
):
    """
    Fetch holdings from the configured ngrok endpoint.

    Args:
        use_mock: If true, return mock data instead of fetching from endpoint
    """
    if use_mock:
        return fetcher.get_mock_holdings()

    try:
        return await fetcher.fetch_holdings()
    except httpx.HTTPError as e:
        # Fall back to mock data on connection error
        if "connect" in str(e).lower() or "timeout" in str(e).lower():
            return fetcher.get_mock_holdings()
        raise HTTPException(
            status_code=502,
            detail=f"Failed to fetch holdings: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching holdings: {str(e)}"
        )


@router.get("/performance", response_model=PerformanceResponse)
async def get_holdings_performance(
    use_mock: bool = False,
    fetcher: HoldingsFetcher = Depends(get_holdings_fetcher),
    analyzer: PerformanceAnalyzer = Depends(get_performance_analyzer)
):
    """
    Fetch holdings and analyze their performance.

    Returns holdings with current prices, change percentages, and fluctuation flags.
    """
    try:
        # Get holdings
        if use_mock:
            holdings_response = fetcher.get_mock_holdings()
        else:
            try:
                holdings_response = await fetcher.fetch_holdings()
            except httpx.HTTPError:
                holdings_response = fetcher.get_mock_holdings()

        # Analyze performance
        performance = await analyzer.analyze_holdings(holdings_response.holdings)

        return performance

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing holdings: {str(e)}"
        )


@router.get("/fluctuations")
async def get_fluctuations(
    use_mock: bool = False,
    fetcher: HoldingsFetcher = Depends(get_holdings_fetcher),
    analyzer: PerformanceAnalyzer = Depends(get_performance_analyzer)
):
    """
    Get only the high-fluctuation stocks from holdings.

    Returns stocks with price change >= configured threshold (default 5%).
    """
    try:
        # Get holdings
        if use_mock:
            holdings_response = fetcher.get_mock_holdings()
        else:
            try:
                holdings_response = await fetcher.fetch_holdings()
            except httpx.HTTPError:
                holdings_response = fetcher.get_mock_holdings()

        # Analyze and extract fluctuations
        performance = await analyzer.analyze_holdings(holdings_response.holdings)
        alerts = analyzer.get_fluctuation_alerts(performance.holdings)

        return {
            "fluctuations": [alert.model_dump() for alert in alerts],
            "count": len(alerts),
            "threshold": analyzer.settings.fluctuation_threshold
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting fluctuations: {str(e)}"
        )
