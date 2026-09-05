"""RevBack — AI Revenue Recovery & Escalation Agent.

FastAPI application entrypoint providing REST endpoints, Razorpay webhook handlers,
LangGraph agent execution triggers, and real-time financial recovery analytics.
"""

from contextlib import asynccontextmanager
from datetime import datetime, timezone
import logging
from typing import Dict, Any

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response

from src.config import settings
from src.db.session import init_db
from src.api.webhooks import router as webhooks_router
from src.api.routes.invoices import router as invoices_router
from src.api.routes.approvals import router as approvals_router
from src.api.routes.metrics import router as metrics_router
from src.api.routes.simulation import router as simulation_router
from src.api.routes.auth import router as auth_router
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Configure Logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("revback")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager initializing database and checking services."""
    logger.info("Initializing RevBack AI Revenue Recovery Engine...")
    try:
        await init_db()
        logger.info("Database schema initialized successfully.")
    except Exception as e:
        logger.error(f"Database initialization warning: {e}")

    logger.info(
        f"LLM Mode: {'MOCK (Deterministic CI Mode)' if settings.MOCK_LLM_MODE else 'LIVE GEMINI API (' + settings.FAST_MODEL + ')'}"
    )
    logger.info(f"Razorpay Key ID: {settings.RAZORPAY_KEY_ID[:12]}...")

    yield

    logger.info("RevBack engine shutting down gracefully.")


# Create FastAPI App
app = FastAPI(
    title="RevBack — AI Revenue Recovery & Escalation Engine",
    description=(
        "Autonomous B2B revenue recovery agent: Detect, Recover, Verify, Escalate. "
        "Built for Razorpay Buildathon 2026."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Rate Limiter Setup
limiter = Limiter(key_func=get_remote_address, default_limits=["120/minute"])
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Root & Health Check Endpoints
@app.get("/", tags=["Health"])
async def root() -> Dict[str, Any]:
    return {
        "app": settings.APP_NAME,
        "event": "Razorpay Buildathon 2026",
        "tagline": "Find revenue that's slipping away and win it back.",
        "status": "online",
        "docs": "/docs",
        "health": "/health",
        "api_v1_prefix": "/api/v1",
    }


@app.get("/health", tags=["Health"], status_code=status.HTTP_200_OK)
async def health_check() -> Dict[str, Any]:
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "llm_engine": {
            "mode": "mock" if settings.MOCK_LLM_MODE else "live",
            "fast_model": settings.FAST_MODEL,
            "reasoning_model": settings.REASONING_MODEL,
            "legal_model": settings.LEGAL_MODEL,
        },
        "razorpay_status": {
            "key_configured": bool(settings.RAZORPAY_KEY_ID),
            "test_mode": settings.RAZORPAY_KEY_ID.startswith("rzp_test_"),
        },
    }


# Include Routers under API v1
api_v1_prefix = "/api/v1"
app.include_router(auth_router, prefix=api_v1_prefix)
app.include_router(invoices_router, prefix=api_v1_prefix)
app.include_router(approvals_router, prefix=api_v1_prefix)
app.include_router(metrics_router, prefix=api_v1_prefix)
app.include_router(simulation_router, prefix=api_v1_prefix)
app.include_router(webhooks_router, prefix=api_v1_prefix)


@app.get("/metrics", tags=["Observability"], response_class=Response)
async def prometheus_metrics() -> Response:
    """Prometheus exposition metrics endpoint for monitoring and alerts."""
    from src.observability.metrics import get_prometheus_metrics
    return Response(
        content=get_prometheus_metrics(),
        media_type="text/plain; version=0.0.4; charset=utf-8",
    )



if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
