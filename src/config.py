"""Application configuration management using Pydantic Settings."""

from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # App Environment
    APP_NAME: str = "RevBack"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    PORT: int = 8000
    HOST: str = "0.0.0.0"

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./revback.db"
    DATABASE_ECHO: bool = False

    # Razorpay Integration
    RAZORPAY_KEY_ID: str = Field(default="rzp_test_revback_mock", description="Razorpay Key ID")
    RAZORPAY_KEY_SECRET: str = Field(default="mock_key_secret_revback", description="Razorpay Key Secret")
    RAZORPAY_WEBHOOK_SECRET: str = Field(default="mock_webhook_secret_revback", description="Razorpay Webhook HMAC Secret")
    RAZORPAY_ACCOUNT_ID: str = "acc_merchant_revback"

    # LLM Settings & LiteLLM Routing
    MOCK_LLM_MODE: bool = Field(default=True, description="When true, uses high-fidelity deterministic responses for testing/offline runs")
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    
    # Model tiers (Configurable via .env)
    FAST_MODEL: str = Field(default="gemini/gemini-3.1-flash-lite", description="Model for extraction & classification")
    REASONING_MODEL: str = Field(default="gemini/gemini-3.1-flash-lite", description="Model for agent reasoning")
    LEGAL_MODEL: str = Field(default="gemini/gemini-3.1-flash-lite", description="Model for formal demand drafting")

    # Observability (Langfuse)
    LANGFUSE_PUBLIC_KEY: Optional[str] = None
    LANGFUSE_SECRET_KEY: Optional[str] = None
    LANGFUSE_HOST: str = "https://cloud.langfuse.com"

    # Recovery Policy Defaults
    MIN_GRACE_PERIOD_DAYS: int = 3
    MAX_INTERVENTIONS: int = 7
    DISCOUNT_APPROVAL_THRESHOLD_PAISE: int = 100_000_00  # ₹1 Lakh in paise
    LEGAL_ESCALATION_THRESHOLD_PAISE: int = 500_000_00   # ₹5 Lakh in paise
    CONFIDENCE_THRESHOLD_INTENT: float = 0.80
    CONFIDENCE_THRESHOLD_PROMISE: float = 0.85
    CONFIDENCE_THRESHOLD_AMOUNT: float = 0.90
    CONFIDENCE_THRESHOLD_DISPUTE: float = 0.75


settings = Settings()
