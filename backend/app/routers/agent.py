"""AI Agent endpoints for portfolio analysis."""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import Optional
from datetime import datetime
import httpx

from ..services.holdings_fetcher import HoldingsFetcher
from ..services.performance_analyzer import PerformanceAnalyzer
from ..services.earnings_collector import EarningsCollector
from ..services.news_collector import NewsCollector
from ..services.llm_agent import LLMAgent
from ..models.agent import AnalyzeRequest, AnalyzeResponse, AgentSummary
from ..models.holdings import PerformanceResponse

router = APIRouter(prefix="/api/agent", tags=["agent"])

# Store for latest analysis results (in production, use Redis or similar)
_latest_analysis: Optional[AnalyzeResponse] = None
_analysis_in_progress: bool = False


def get_holdings_fetcher() -> HoldingsFetcher:
    return HoldingsFetcher()


def get_performance_analyzer() -> PerformanceAnalyzer:
    return PerformanceAnalyzer()


def get_earnings_collector() -> EarningsCollector:
    return EarningsCollector()


def get_news_collector() -> NewsCollector:
    return NewsCollector()


def get_llm_agent() -> LLMAgent:
    return LLMAgent()


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_portfolio(
    request: AnalyzeRequest = AnalyzeRequest(),
    fetcher: HoldingsFetcher = Depends(get_holdings_fetcher),
    analyzer: PerformanceAnalyzer = Depends(get_performance_analyzer),
    earnings_collector: EarningsCollector = Depends(get_earnings_collector),
    news_collector: NewsCollector = Depends(get_news_collector),
    llm_agent: LLMAgent = Depends(get_llm_agent)
):
    """
    Trigger a full portfolio analysis.

    This endpoint:
    1. Fetches holdings from ngrok endpoint
    2. Analyzes performance and identifies high-fluctuation stocks
    3. Collects upcoming earnings for holdings
    4. Fetches news for high-fluctuation stocks
    5. Generates AI summary using LLM
    """
    global _latest_analysis, _analysis_in_progress

    if _analysis_in_progress:
        raise HTTPException(
            status_code=409,
            detail="Analysis already in progress"
        )

    _analysis_in_progress = True

    try:
        # Clear caches if force refresh
        if request.force_refresh:
            earnings_collector.clear_cache()
            news_collector.clear_cache()

        # 1. Fetch holdings
        try:
            holdings_response = await fetcher.fetch_holdings()
        except httpx.HTTPError:
            holdings_response = fetcher.get_mock_holdings()

        # 2. Analyze performance
        performance = await analyzer.analyze_holdings(holdings_response.holdings)
        fluctuations = analyzer.get_fluctuation_alerts(performance.holdings)

        # 3. Get symbols for further analysis
        all_symbols = [h.symbol for h in holdings_response.holdings]
        fluctuation_symbols = [f.symbol for f in fluctuations]

        # 4. Collect earnings (optional)
        earnings = []
        if request.include_earnings:
            earnings = await earnings_collector.get_earnings_for_symbols(all_symbols)

        # 5. Collect news for high-fluctuation stocks (optional)
        news = []
        if request.include_news and fluctuation_symbols:
            news = await news_collector.get_news_for_high_fluctuation(fluctuation_symbols)

        # 6. Generate AI summary
        summary = None
        if llm_agent.is_configured():
            summary = await llm_agent.generate_summary(
                holdings=performance.holdings,
                fluctuations=fluctuations,
                earnings=earnings,
                news=news
            )
        else:
            # Generate basic summary without LLM
            summary = AgentSummary(
                summary=f"Portfolio analysis complete. {len(holdings_response.holdings)} holdings analyzed, "
                       f"{len(fluctuations)} showing significant movement.",
                key_insights=[
                    f"Total holdings: {len(holdings_response.holdings)}",
                    f"High fluctuation stocks: {len(fluctuations)}",
                    f"Upcoming earnings: {len(earnings)}",
                ],
                recommendations=["Configure LLM API key for detailed AI analysis"],
                risk_factors=[],
                generated_at=datetime.utcnow(),
                model_used="none"
            )

        # Build response
        response = AnalyzeResponse(
            summary=summary,
            fluctuation_alerts=[f.model_dump() for f in fluctuations],
            upcoming_earnings=[e.model_dump() for e in earnings],
            news_items=[n.model_dump() for n in news],
            holdings_count=len(holdings_response.holdings),
            analyzed_at=datetime.utcnow(),
            status="success"
        )

        _latest_analysis = response
        return response

    except Exception as e:
        return AnalyzeResponse(
            summary=None,
            fluctuation_alerts=[],
            upcoming_earnings=[],
            news_items=[],
            holdings_count=0,
            analyzed_at=datetime.utcnow(),
            status="error",
            error=str(e)
        )
    finally:
        _analysis_in_progress = False


@router.get("/summary", response_model=Optional[AgentSummary])
async def get_latest_summary():
    """Get the latest AI-generated summary."""
    if _latest_analysis and _latest_analysis.summary:
        return _latest_analysis.summary
    return None


@router.get("/fluctuations")
async def get_fluctuations():
    """Get the latest fluctuation alerts from the most recent analysis."""
    if _latest_analysis:
        return {
            "fluctuations": _latest_analysis.fluctuation_alerts,
            "count": len(_latest_analysis.fluctuation_alerts)
        }
    return {"fluctuations": [], "count": 0}


@router.get("/earnings")
async def get_earnings():
    """Get the upcoming earnings from the most recent analysis."""
    if _latest_analysis:
        return {
            "earnings": _latest_analysis.upcoming_earnings,
            "count": len(_latest_analysis.upcoming_earnings)
        }
    return {"earnings": [], "count": 0}


@router.get("/news")
async def get_news():
    """Get the news items from the most recent analysis."""
    if _latest_analysis:
        return {
            "news": _latest_analysis.news_items,
            "count": len(_latest_analysis.news_items)
        }
    return {"news": [], "count": 0}


@router.get("/status")
async def get_analysis_status():
    """Get the current analysis status."""
    return {
        "in_progress": _analysis_in_progress,
        "has_analysis": _latest_analysis is not None,
        "last_analyzed": _latest_analysis.analyzed_at if _latest_analysis else None,
        "holdings_count": _latest_analysis.holdings_count if _latest_analysis else 0
    }
