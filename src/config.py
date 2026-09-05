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
    
    # Security & CORS
    FRONTEND_URL: str = "http://localhost:3001"
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://localhost:8000",
    ]

    # Model tiers (Configurable via .env)
    FAST_MODEL: str = Field(default="gemini/gemini-2.0-flash", description="Model for extraction & classification")
    REASONING_MODEL: str = Field(default="gemini/gemini-2.0-flash", description="Model for agent reasoning")
    LEGAL_MODEL: str = Field(default="gemini/gemini-2.0-flash", description="Model for formal demand drafting")

    # Redis & Background Workers
    REDIS_URL: str = Field(default="redis://localhost:6379/0", description="Redis connection URL for caching and state")
    CELERY_BROKER_URL: str = Field(default="redis://localhost:6379/1", description="Celery message broker URL")
    CELERY_RESULT_BACKEND: str = Field(default="redis://localhost:6379/2", description="Celery result backend URL")

    # Authentication & Security
    JWT_SECRET: str = Field(default="revback_production_jwt_secret_key_2026_buildathon_secure", description="Secret key for signing JWTs")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    API_KEY_HEADER: str = "X-API-Key"

    # Transactional Communication (Resend / Twilio)
    RESEND_API_KEY: Optional[str] = None
    EMAIL_FROM_ADDRESS: str = "recoveries@revback.ai"
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    TWILIO_FROM_NUMBER: Optional[str] = None

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

