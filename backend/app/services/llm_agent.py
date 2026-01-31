"""LangChain-based LLM agent for investment analysis."""

from typing import Optional
from datetime import datetime

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from ..config import get_settings
from ..models.agent import AgentSummary
from ..models.holdings import HoldingPerformance
from ..models.analysis import FluctuationAlert, EarningsEvent, NewsItem


class LLMAgent:
    """AI agent for generating investment analysis summaries."""

    def __init__(self):
        self.settings = get_settings()
        self._llm = None

    def _get_llm(self):
        """
        Get the configured LLM instance.

        Supports OpenAI, Anthropic, and local (Ollama) providers.
        """
        if self._llm is not None:
            return self._llm

        provider = self.settings.llm_provider.lower()
        model = self.settings.llm_model

        if provider == "openai":
            from langchain_openai import ChatOpenAI
            self._llm = ChatOpenAI(
                model=model,
                api_key=self.settings.openai_api_key,
                temperature=0.3
            )
        elif provider == "anthropic":
            from langchain_anthropic import ChatAnthropic
            self._llm = ChatAnthropic(
                model=model,
                api_key=self.settings.anthropic_api_key,
                temperature=0.3
            )
        elif provider == "local":
            from langchain_community.llms import Ollama
            self._llm = Ollama(
                model=model,
                base_url=self.settings.local_llm_url
            )
        else:
            raise ValueError(f"Unknown LLM provider: {provider}")

        return self._llm

    async def generate_summary(
        self,
        holdings: list[HoldingPerformance],
        fluctuations: list[FluctuationAlert],
        earnings: list[EarningsEvent],
        news: list[NewsItem]
    ) -> AgentSummary:
        """
        Generate an AI summary of the portfolio analysis.

        Args:
            holdings: List of holdings with performance data
            fluctuations: List of high-fluctuation alerts
            earnings: List of upcoming earnings events
            news: List of recent news items

        Returns:
            AgentSummary with AI-generated insights
        """
        # Build context from data
        context = self._build_context(holdings, fluctuations, earnings, news)

        # Create prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert investment analyst assistant. Analyze the provided
portfolio data and generate a concise, actionable summary. Focus on:
1. Overall portfolio health and performance
2. Significant movers (high fluctuation stocks) and potential reasons
3. Upcoming earnings that may impact positions
4. Relevant news that affects holdings

Be concise but insightful. Use bullet points for key insights and recommendations.
Do not give specific buy/sell advice - focus on analysis and awareness."""),
            ("user", """Please analyze this portfolio data:

{context}

Provide:
1. A brief summary paragraph (2-3 sentences)
2. 3-5 key insights as bullet points
3. 2-3 actionable recommendations
4. Any risk factors to be aware of""")
        ])

        try:
            llm = self._get_llm()
            chain = prompt | llm | StrOutputParser()

            response = await chain.ainvoke({"context": context})

            # Parse the response into structured format
            return self._parse_response(response)

        except Exception as e:
            # Return a basic summary on error
            return AgentSummary(
                summary=f"Unable to generate AI analysis: {str(e)}",
                key_insights=[
                    f"Portfolio contains {len(holdings)} holdings",
                    f"{len(fluctuations)} stocks show significant movement (>5%)",
                    f"{len(earnings)} upcoming earnings events",
                ],
                recommendations=["Review high-fluctuation stocks manually"],
                risk_factors=["AI analysis unavailable"],
                generated_at=datetime.utcnow(),
                model_used="error"
            )

    def _build_context(
        self,
        holdings: list[HoldingPerformance],
        fluctuations: list[FluctuationAlert],
        earnings: list[EarningsEvent],
        news: list[NewsItem]
    ) -> str:
        """Build context string from analysis data."""
        parts = []

        # Portfolio overview
        total_value = sum(h.market_value for h in holdings if h.market_value)
        positive_stocks = sum(1 for h in holdings if h.change_percent and h.change_percent > 0)
        negative_stocks = sum(1 for h in holdings if h.change_percent and h.change_percent < 0)

        parts.append(f"""## Portfolio Overview
- Total Holdings: {len(holdings)}
- Estimated Value: ${total_value:,.2f}
- Gainers Today: {positive_stocks}
- Losers Today: {negative_stocks}
""")

        # High fluctuation stocks
        if fluctuations:
            parts.append("## High Fluctuation Stocks (>5% change)")
            for f in fluctuations[:5]:
                direction = "+" if f.direction == "up" else ""
                parts.append(f"- {f.symbol} ({f.name}): {direction}{f.change_percent:.2f}%")
            parts.append("")

        # Upcoming earnings
        if earnings:
            parts.append("## Upcoming Earnings")
            for e in earnings[:5]:
                parts.append(f"- {e.symbol}: {e.earnings_date.strftime('%b %d')} ({e.days_until} days)")
            parts.append("")

        # Recent news
        if news:
            parts.append("## Recent News")
            for n in news[:5]:
                date_str = n.published_at.strftime('%b %d') if n.published_at else "Unknown"
                parts.append(f"- [{n.symbol}] {n.title} ({n.publisher}, {date_str})")
            parts.append("")

        # Holdings detail
        parts.append("## Holdings Detail")
        for h in sorted(holdings, key=lambda x: x.market_value or 0, reverse=True)[:10]:
            change = f"{h.change_percent:+.2f}%" if h.change_percent else "N/A"
            value = f"${h.market_value:,.2f}" if h.market_value else "N/A"
            parts.append(f"- {h.symbol}: {value} ({change})")

        return "\n".join(parts)

    def _parse_response(self, response: str) -> AgentSummary:
        """Parse LLM response into structured AgentSummary."""
        lines = response.strip().split("\n")

        summary = ""
        key_insights = []
        recommendations = []
        risk_factors = []

        current_section = "summary"

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Detect section headers
            line_lower = line.lower()
            if "key insight" in line_lower or "insight" in line_lower:
                current_section = "insights"
                continue
            elif "recommendation" in line_lower or "action" in line_lower:
                current_section = "recommendations"
                continue
            elif "risk" in line_lower or "caution" in line_lower or "warning" in line_lower:
                current_section = "risks"
                continue
            elif "summary" in line_lower:
                current_section = "summary"
                continue

            # Parse content based on section
            if line.startswith(("-", "*", "•")):
                content = line.lstrip("-*• ").strip()
                if current_section == "insights":
                    key_insights.append(content)
                elif current_section == "recommendations":
                    recommendations.append(content)
                elif current_section == "risks":
                    risk_factors.append(content)
            elif current_section == "summary" and not summary:
                summary = line
            elif current_section == "summary":
                summary += " " + line

        # Ensure we have at least basic content
        if not summary:
            summary = response[:500] if response else "Analysis complete."

        return AgentSummary(
            summary=summary,
            key_insights=key_insights or ["Analysis complete - review details below"],
            recommendations=recommendations or ["Monitor high-fluctuation positions"],
            risk_factors=risk_factors or [],
            generated_at=datetime.utcnow(),
            model_used=f"{self.settings.llm_provider}/{self.settings.llm_model}"
        )

    def is_configured(self) -> bool:
        """Check if the LLM is properly configured."""
        provider = self.settings.llm_provider.lower()

        if provider == "openai":
            return bool(self.settings.openai_api_key)
        elif provider == "anthropic":
            return bool(self.settings.anthropic_api_key)
        elif provider == "local":
            return bool(self.settings.local_llm_url)

        return False
