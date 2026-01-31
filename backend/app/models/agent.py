"""Pydantic models for AI agent."""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class AgentSummary(BaseModel):
    """AI-generated analysis summary."""

    model_config = {"protected_namespaces": ()}

    summary: str = Field(..., description="AI-generated summary text")
    key_insights: list[str] = Field(default_factory=list, description="Bullet points of key insights")
    recommendations: list[str] = Field(default_factory=list, description="Action recommendations")
    risk_factors: list[str] = Field(default_factory=list, description="Identified risks")
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    model_used: str = Field(default="", description="LLM model that generated this")


class AnalyzeRequest(BaseModel):
    """Request to trigger analysis."""

    force_refresh: bool = Field(default=False, description="Force refresh cached data")
    include_news: bool = Field(default=True, description="Include news analysis")
    include_earnings: bool = Field(default=True, description="Include earnings data")


class AnalyzeResponse(BaseModel):
    """Response from analysis endpoint."""

    summary: Optional[AgentSummary] = None
    fluctuation_alerts: list = Field(default_factory=list)
    upcoming_earnings: list = Field(default_factory=list)
    news_items: list = Field(default_factory=list)
    holdings_count: int = 0
    analyzed_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = Field(default="success")
    error: Optional[str] = None


class SchedulerStatus(BaseModel):
    """Scheduler status information."""

    enabled: bool
    running: bool
    next_run: Optional[datetime] = None
    last_run: Optional[datetime] = None
    cron_expression: str
    job_count: int = 0
