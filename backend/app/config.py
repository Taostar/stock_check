"""Application configuration using pydantic-settings."""

from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Literal

# Get the directory where this config file lives (backend/app/)
# Then go up one level to backend/ where .env is located
ENV_FILE_PATH = Path(__file__).parent.parent / ".env"


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Holdings endpoint configuration
    holdings_endpoint_url: str = Field(
        default="https://your-ngrok-url.ngrok.io/api/holdings",
        description="URL to fetch holdings data from"
    )
    holdings_auth_token: str = Field(
        default="",
        description="Optional auth token for holdings endpoint"
    )

    # LLM Configuration
    llm_provider: Literal["openai", "anthropic", "local"] = Field(
        default="anthropic",
        description="LLM provider to use"
    )
    llm_model: str = Field(
        default="claude-3-sonnet-20240229",
        description="Model name/ID for the LLM"
    )
    openai_api_key: str = Field(
        default="",
        description="OpenAI API key"
    )
    anthropic_api_key: str = Field(
        default="",
        description="Anthropic API key"
    )
    local_llm_url: str = Field(
        default="http://localhost:11434",
        description="URL for local LLM (e.g., Ollama)"
    )

    # Scheduler Configuration
    scheduler_enabled: bool = Field(
        default=True,
        description="Enable/disable the scheduler"
    )
    scheduler_cron: str = Field(
        default="0 9,16 * * 1-5",
        description="Cron expression for scheduled runs (9AM and 4PM weekdays)"
    )

    # Analysis Thresholds
    fluctuation_threshold: float = Field(
        default=5.0,
        description="Percentage threshold for high-fluctuation alerts"
    )

    # Cache Settings
    earnings_cache_hours: int = Field(
        default=4,
        description="Hours to cache earnings data"
    )
    news_cache_minutes: int = Field(
        default=30,
        description="Minutes to cache news data"
    )

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE_PATH),
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
