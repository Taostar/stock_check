"""APScheduler jobs for periodic analysis."""

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from typing import Optional
from datetime import datetime
import asyncio
import httpx

from ..config import get_settings
from ..models.agent import SchedulerStatus
from ..services.holdings_fetcher import HoldingsFetcher
from ..services.performance_analyzer import PerformanceAnalyzer
from ..services.earnings_collector import EarningsCollector
from ..services.news_collector import NewsCollector
from ..services.llm_agent import LLMAgent


# Global scheduler instance
_scheduler: Optional["AnalysisScheduler"] = None


def get_scheduler() -> "AnalysisScheduler":
    """Get or create the global scheduler instance."""
    global _scheduler
    if _scheduler is None:
        _scheduler = AnalysisScheduler()
    return _scheduler


class AnalysisScheduler:
    """Manages scheduled portfolio analysis jobs."""

    def __init__(self):
        self.settings = get_settings()
        self._scheduler = AsyncIOScheduler()
        self._last_run: Optional[datetime] = None
        self._job_id = "portfolio_analysis"

    def start(self):
        """Start the scheduler with configured cron expression."""
        if self._scheduler.running:
            return

        # Parse cron expression
        cron_parts = self.settings.scheduler_cron.split()

        # APScheduler expects: minute, hour, day, month, day_of_week
        if len(cron_parts) >= 5:
            trigger = CronTrigger(
                minute=cron_parts[0],
                hour=cron_parts[1],
                day=cron_parts[2],
                month=cron_parts[3],
                day_of_week=cron_parts[4]
            )
        else:
            # Default: 9 AM and 4 PM on weekdays
            trigger = CronTrigger(
                minute="0",
                hour="9,16",
                day_of_week="mon-fri"
            )

        # Add the job
        self._scheduler.add_job(
            self._run_analysis,
            trigger=trigger,
            id=self._job_id,
            name="Portfolio Analysis",
            replace_existing=True
        )

        self._scheduler.start()

    def stop(self):
        """Stop the scheduler."""
        if self._scheduler.running:
            self._scheduler.shutdown(wait=False)

    def is_running(self) -> bool:
        """Check if scheduler is running."""
        return self._scheduler.running

    def get_next_run_time(self) -> Optional[datetime]:
        """Get the next scheduled run time."""
        job = self._scheduler.get_job(self._job_id)
        if job:
            return job.next_run_time
        return None

    def get_status(self) -> SchedulerStatus:
        """Get current scheduler status."""
        return SchedulerStatus(
            enabled=self.settings.scheduler_enabled,
            running=self._scheduler.running,
            next_run=self.get_next_run_time(),
            last_run=self._last_run,
            cron_expression=self.settings.scheduler_cron,
            job_count=len(self._scheduler.get_jobs()) if self._scheduler.running else 0
        )

    def update_schedule(self, cron_expression: str):
        """Update the cron schedule."""
        cron_parts = cron_expression.split()
        if len(cron_parts) < 5:
            raise ValueError("Cron expression must have at least 5 parts")

        # Validate by trying to create trigger
        try:
            trigger = CronTrigger(
                minute=cron_parts[0],
                hour=cron_parts[1],
                day=cron_parts[2],
                month=cron_parts[3],
                day_of_week=cron_parts[4]
            )
        except Exception as e:
            raise ValueError(f"Invalid cron expression: {e}")

        # Reschedule the job
        if self._scheduler.running:
            self._scheduler.reschedule_job(
                self._job_id,
                trigger=trigger
            )

    async def run_analysis_now(self):
        """Trigger an immediate analysis run."""
        await self._run_analysis()

    async def _run_analysis(self):
        """Execute the portfolio analysis."""
        print(f"[Scheduler] Starting analysis at {datetime.utcnow()}")

        try:
            # Initialize services
            fetcher = HoldingsFetcher()
            analyzer = PerformanceAnalyzer()
            earnings_collector = EarningsCollector()
            news_collector = NewsCollector()
            llm_agent = LLMAgent()

            # 1. Fetch holdings
            try:
                holdings_response = await fetcher.fetch_holdings()
            except httpx.HTTPError:
                holdings_response = fetcher.get_mock_holdings()

            # 2. Analyze performance
            performance = await analyzer.analyze_holdings(holdings_response.holdings)
            fluctuations = analyzer.get_fluctuation_alerts(performance.holdings)

            # 3. Get symbols
            all_symbols = [h.symbol for h in holdings_response.holdings]
            fluctuation_symbols = [f.symbol for f in fluctuations]

            # 4. Collect data
            earnings = await earnings_collector.get_earnings_for_symbols(all_symbols)
            news = []
            if fluctuation_symbols:
                news = await news_collector.get_news_for_high_fluctuation(fluctuation_symbols)

            # 5. Generate summary
            if llm_agent.is_configured():
                summary = await llm_agent.generate_summary(
                    holdings=performance.holdings,
                    fluctuations=fluctuations,
                    earnings=earnings,
                    news=news
                )
                print(f"[Scheduler] AI Summary generated: {summary.summary[:100]}...")

            self._last_run = datetime.utcnow()
            print(f"[Scheduler] Analysis complete. {len(holdings_response.holdings)} holdings, "
                  f"{len(fluctuations)} fluctuations, {len(earnings)} earnings events")

            # Update the global latest analysis in the agent router
            from ..routers.agent import _latest_analysis
            from ..models.agent import AnalyzeResponse

            # Store result (importing here to avoid circular imports)
            import sys
            agent_module = sys.modules.get('backend.app.routers.agent')
            if agent_module:
                agent_module._latest_analysis = AnalyzeResponse(
                    summary=summary if llm_agent.is_configured() else None,
                    fluctuation_alerts=[f.model_dump() for f in fluctuations],
                    upcoming_earnings=[e.model_dump() for e in earnings],
                    news_items=[n.model_dump() for n in news],
                    holdings_count=len(holdings_response.holdings),
                    analyzed_at=datetime.utcnow(),
                    status="success"
                )

        except Exception as e:
            print(f"[Scheduler] Analysis failed: {e}")
            self._last_run = datetime.utcnow()
